# Concept B round 2 — focus states as a LAYERED COMPOSITE, the same method the web shader would use.
# Input: the all-sharp Cycles plate (PNG, AgX display) + its uncompressed multilayer EXR with per-object layer AOVs
#   m1 = (sea/sky ∞, sport, festival), m2 = (portrait set, pine).
# Per focus state every layer gets a disc ("bokeh") blur whose diameter grows with its distance from the focused
# detent on the ring (u: pine -0.75, portrait 0, festival 1, sport 2, sea 3). Behind the focus: 26 px per detent,
# in front: 32 px per detent (desktop, 1600 px wide), cap 64 px; unfocused layers -0.3 EV. Occluded parts of each
# layer are filled by push-pull inpainting before blurring (what a 6-layer RGBA bake would contain).
# Run: python3 B2_layer_composite.py PLATE.png PLATE.exr OUTDIR PREFIX SCALE  (SCALE = blur scale, 1.0 desktop, ~0.5 phone)
import sys, os, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from B2_exr import read_exr

PNG, EXR, OUTD, PREFIX = sys.argv[1:5]; SCALE = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
U = np.array([3.0, 2.0, 1.0, 0.0, -0.75])                 # layer order: 0 sea, 1 sport, 2 festival, 3 portrait, 4 pine
NAMES = ["surf", "sport", "festival", "portrait", "pine"]
BEHIND, FRONT, CAP, EV = 26.0, 32.0, 64.0, -0.3

disp = np.asarray(Image.open(PNG).convert("RGB"), np.float32) / 255.0
Hh, Ww = disp.shape[:2]
d = read_exr(EXR)
g = lambda n, c: d["ViewLayer.%s.%s" % (n, c)]
L = np.stack([g("m1", "R"), g("m1", "G"), g("m1", "B"), g("m2", "R"), g("m2", "G")], 0).clip(0, 1)

def box(a, r=1):
    p = np.pad(a, ((r, r), (r, r)), mode="edge"); out = np.zeros_like(a)
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1): out += p[r + dy:r + dy + a.shape[0], r + dx:r + dx + a.shape[1]]
    return out / (2 * r + 1) ** 2
# masks: volume scattering makes the AOV stochastic in the haze -> normalise, send leftovers to the sky/sea layer, de-speckle
tot = L.sum(0); w = np.clip((tot - 0.05) / 0.25, 0, 1)
Ln = L / np.maximum(tot, 1e-4)[None] * w[None]; Ln[0] += 1 - w
Ln = np.stack([box(box(x)) for x in Ln]); Ln /= Ln.sum(0)[None]

lin = disp ** 2.2
lum = disp @ np.array([0.2126, 0.7152, 0.0722], np.float32)
hl = np.clip((lum - 0.72) / 0.26, 0, 1) ** 2
lin_b = lin * (1 + 7.0 * hl)[..., None]                    # recover highlight energy clipped by the display transform so bulbs bloom into discs

def down(a):
    if a.shape[0] % 2: a = np.concatenate([a, a[-1:]], 0)
    if a.shape[1] % 2: a = np.concatenate([a, a[:, -1:]], 1)
    return 0.25 * (a[0::2, 0::2] + a[1::2, 0::2] + a[0::2, 1::2] + a[1::2, 1::2])
def up(a, shape):
    """bilinear 2x upsample (sample positions of the finer grid mapped into the coarse grid)"""
    def axis(n_out, n_in):
        x = (np.arange(n_out) + 0.5) / 2 - 0.5; x0 = np.clip(np.floor(x).astype(int), 0, n_in - 1); x1 = np.clip(x0 + 1, 0, n_in - 1)
        return x0, x1, np.clip(x - x0, 0, 1).astype(np.float32)
    y0, y1, fy = axis(shape[0], a.shape[0]); x0, x1, fx = axis(shape[1], a.shape[1])
    fx = fx[None, :, None] if a.ndim == 3 else fx[None, :]; fy = fy[:, None, None] if a.ndim == 3 else fy[:, None]
    r0 = a[y0][:, x0] * (1 - fx) + a[y0][:, x1] * fx; r1 = a[y1][:, x0] * (1 - fx) + a[y1][:, x1] * fx
    return r0 * (1 - fy) + r1 * fy
def pushpull(val, wt):
    """fill val (H,W,C) where wt (H,W) ~ 0 from surrounding pixels where wt ~ 1"""
    wv = val * wt[..., None]; pyr = [(wv, wt)]
    while min(pyr[-1][1].shape) > 2: pyr.append((down(pyr[-1][0]), down(pyr[-1][1])))
    est = pyr[-1][0] / np.maximum(pyr[-1][1], 1e-6)[..., None]
    for wv_l, w_l in reversed(pyr[:-1]):
        upv = up(est, w_l.shape); est = wv_l + (1 - np.clip(w_l, 0, 1))[..., None] * upv
        est = np.where(w_l[..., None] > 1e-6, est, upv) if False else est
    return est

def layer_rgba(k):
    occ = Ln[k + 1:].sum(0) if k < 4 else np.zeros((Hh, Ww), np.float32)   # covered by nearer layers
    a = Ln[k]; trust = np.clip(1 - occ, 0, 1)
    pure = np.clip((a - 0.9) / 0.08, 0, 1)                 # only pixels that belong (almost) wholly to this layer give colour
    col_w = trust * pure
    c = lin_b; cf = pushpull(c, col_w)
    af = pushpull(a[..., None], trust)[..., 0] if k > 0 else np.ones_like(a)
    af = np.clip((af - 0.1) / 0.35, 0, 1)                    # bias hidden alpha toward opaque: a far plane continues behind what covers it (no see-through rims)
    # un-occluded share of this layer (a mixed edge pixel festival+sport means sport continues behind the festival edge)
    vis = np.clip(1 - occ, 0, 1); t = np.clip((vis - 0.05) / 0.2, 0, 1)
    a2 = (t * np.clip(a / np.maximum(vis, 1e-3), 0, 1) + (1 - t) * af) if k > 0 else np.ones_like(a)
    known = pure[..., None]
    c2 = known * c + (1 - known) * cf
    return c2 * a2[..., None], a2

LAYERS = [layer_rgba(k) for k in range(5)]

def disc_blur(img, diam):
    if diam < 1.2: return img
    r = diam / 2; R = int(np.ceil(r)) + 1
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]; ker = np.clip(r + 0.5 - np.hypot(xx, yy), 0, 1); ker /= ker.sum()
    sh = (img.shape[0] + 2 * R, img.shape[1] + 2 * R)
    K = np.fft.rfft2(ker, s=sh)
    out = np.empty_like(img)
    for ch in range(img.shape[2]):
        p = np.pad(img[..., ch], R, mode="edge")
        o = np.fft.irfft2(np.fft.rfft2(p, s=sh) * K, s=sh)
        out[..., ch] = o[2 * R:2 * R + img.shape[0], 2 * R:2 * R + img.shape[1]]
    return out

def to_disp(x):
    x = np.maximum(x, 0) ** (1 / 2.2)
    knee = 0.85; y = np.where(x < knee, x, knee + (1 - knee) * (1 - np.exp(-(x - knee) / (1 - knee))))
    return (np.clip(y, 0, 1) * 255 + 0.5).astype(np.uint8)

def render_state(u_focus, name, diam_override=None, ev=EV):
    out = np.zeros((Hh, Ww, 3), np.float32); report = []
    for k in range(5):
        du = (U[k] - u_focus) if u_focus is not None else 1.0
        diam = (BEHIND if du > 0 else FRONT) * abs(du)
        diam = min(diam, CAP) * SCALE if diam_override is None else diam_override[k] * SCALE
        P, A = LAYERS[k]
        PA = disc_blur(np.concatenate([P, A[..., None]], 2), diam)
        Pb, Ab = PA[..., :3], np.clip(PA[..., 3], 0, 1)
        if abs(du) > 0.25 or diam_override is not None: Pb = Pb * 2 ** ev
        out = Pb + out * (1 - Ab[..., None])
        report.append("%s %.0f px" % (NAMES[k], diam))
    Image.fromarray(to_disp(out)).save(os.path.join(OUTD, PREFIX + name + ".png"))
    print(name, " | ".join(report))

STATES = os.environ.get("STATES", "portrait,festival,sport,surf,bokeh").split(",")
for st in STATES:
    if st == "bokeh": render_state(None, "bokeh", diam_override=[96, 96, 92, 88, 80], ev=-0.5)
    else: render_state(U[NAMES.index(st)], st)
