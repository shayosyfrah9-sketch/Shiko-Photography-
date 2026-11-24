# Concept B round 3 — focus states as a LAYERED COMPOSITE, the same method the web shader would use.
# R3 changes: (1) every layer is blurred with a real lens kernel — a disc with a brighter rim (onion-ring-free, like a
# fast 50 mm wide open) that turns into a cat's eye toward the frame edges (mechanical vignetting), via 3x3 zone kernels
# blended bilinearly; (2) grown masks: each layer's alpha is dilated 3 px under the nearer layers and everything is blurred
# premultiplied, so no halo/gap at layer edges; (3) near-layer blur capped at 40 px in the sport state (no tilt-shift
# stripe); (4) a "video" state = focus ring past infinity (everything soft, the far field least).
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
U = np.array([3.0, 2.0, 1.0, 0.0, -0.6])                 # layer order: 0 sea, 1 sport, 2 festival, 3 portrait, 4 pine
NAMES = ["surf", "sport", "festival", "portrait", "pine"]
BEHIND, FRONT, CAP, EV = 26.0, 32.0, 64.0, -0.3
GROW = int(os.environ.get("GROW", "3"))

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
def boxblur_axis(a, r, ax):
    c = np.cumsum(np.pad(a, [(r + 1, r) if i == ax else (0, 0) for i in range(a.ndim)], mode="edge"), axis=ax)
    return (np.take(c, range(2 * r + 1, c.shape[ax]), axis=ax) - np.take(c, range(0, c.shape[ax] - 2 * r - 1), axis=ax)) / (2 * r + 1)
loc = boxblur_axis(boxblur_axis(lum, 12, 0), 12, 1)
# only small, locally bright sources (bulbs, lamps, phone screens, glints) get their clipped energy back -> discs;
# broad bright areas (the afterglow on the horizon, the linen) are left alone
hl = np.clip((lum - 0.72) / 0.26, 0, 1) ** 2 * np.clip((lum - loc - 0.12) / 0.2, 0, 1)
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
    if k > 0 and GROW > 0:   # grown mask: extend this layer GROW px under whatever covers it (hidden there, but no gap after blur)
        g_ = a2.copy(); pa_ = np.pad(a2, GROW, mode="edge")
        for dy in range(-GROW, GROW + 1):
            for dx in range(-GROW, GROW + 1):
                if dx * dx + dy * dy <= GROW * GROW: g_ = np.maximum(g_, pa_[GROW + dy:GROW + dy + a2.shape[0], GROW + dx:GROW + dx + a2.shape[1]])
        a2 = np.where(occ > 0.05, np.maximum(a2, g_ * np.clip(occ * 3, 0, 1)), a2)
    known = pure[..., None]
    c2 = known * c + (1 - known) * cf
    return c2 * a2[..., None], a2

LAYERS = [layer_rgba(k) for k in range(5)]

def lens_kernel(diam, vx=0.0, vy=0.0):
    """disc with a brighter rim; (vx, vy) = position in the frame (-1..1): the disc is clipped by a second, offset disc
    (the rear lens barrel) into a cat's eye toward the edges"""
    r = diam / 2; R = int(np.ceil(r)) + 2
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1].astype(np.float32)
    rho = np.hypot(xx, yy); ker = np.clip(r + 0.5 - rho, 0, 1) * (0.62 + 0.38 * np.clip(rho / max(r, 1e-3), 0, 1) ** 4)
    e = 0.42 * np.hypot(vx, vy)
    if e > 1e-3:
        ox, oy = vx / np.hypot(vx, vy) * e * r * 1.6, vy / np.hypot(vx, vy) * e * r * 1.6
        ker *= np.clip(r * 1.05 + 0.5 - np.hypot(xx - ox, yy - oy), 0, 1)
    return ker / ker.sum()
ZX = (-1.0, 0.0, 1.0); ZY = (-1.0, 0.0, 1.0)
def tent(n, c):   # bilinear weights of 3 zone centres along an axis of n pixels
    x = np.linspace(-1, 1, n); return np.clip(1 - np.abs(x - c), 0, 1).astype(np.float32)
def disc_blur(img, diam):
    if diam < 1.2: return img
    R = int(np.ceil(diam / 2)) + 3; Hh_, Ww_ = img.shape[:2]
    sh = (Hh_ + 2 * R, Ww_ + 2 * R)
    F = [np.fft.rfft2(np.pad(img[..., ch], R, mode="edge"), s=sh) for ch in range(img.shape[2])]
    out = np.zeros_like(img)
    for zy in ZY:
        wy = tent(Hh_, zy)
        for zx in ZX:
            wx = tent(Ww_, zx); wgt = wy[:, None] * wx[None, :]
            ker = lens_kernel(diam, zx * 0.9, -zy * 0.9 * Hh_ / Ww_ * 1.6)
            kp = np.zeros(sh, np.float32); kh = ker.shape[0] // 2
            kp[:ker.shape[0], :ker.shape[1]] = ker; kp = np.roll(np.roll(kp, -kh, 0), -kh, 1)
            K = np.fft.rfft2(kp)
            for ch in range(img.shape[2]):
                o = np.fft.irfft2(F[ch] * K, s=sh)[R:R + Hh_, R:R + Ww_]
                out[..., ch] += o * wgt
    return out

def to_disp(x):
    x = np.maximum(x, 0) ** (1 / 2.2)
    knee = 0.85; y = np.where(x < knee, x, knee + (1 - knee) * (1 - np.exp(-(x - knee) / (1 - knee))))
    return (np.clip(y, 0, 1) * 255 + 0.5).astype(np.uint8)

def render_state(u_focus, name, diam_override=None, ev=EV, cap_front=CAP):
    out = np.zeros((Hh, Ww, 3), np.float32); report = []
    for k in range(5):
        du = (U[k] - u_focus) if u_focus is not None else 1.0
        diam = (BEHIND if du > 0 else FRONT) * abs(du)
        diam = min(diam, CAP if du > 0 else cap_front) * SCALE if diam_override is None else diam_override[k] * SCALE
        P, A = LAYERS[k]
        PA = disc_blur(np.concatenate([P, A[..., None]], 2), diam)
        Pb, Ab = PA[..., :3], np.clip(PA[..., 3], 0, 1)
        if abs(du) > 0.25 or diam_override is not None: Pb = Pb * 2 ** ev
        out = Pb + out * (1 - Ab[..., None])
        report.append("%s %.0f px" % (NAMES[k], diam))
    Image.fromarray(to_disp(out)).save(os.path.join(OUTD, PREFIX + name + ".png"))
    print(name, " | ".join(report))

STATES = os.environ.get("STATES", "portrait,festival,sport,surf,video,bokeh").split(",")
for st in STATES:
    if st == "bokeh": render_state(None, "bokeh", diam_override=[96, 96, 92, 88, 80], ev=-0.5)
    elif st == "video": render_state(4.0, "video")                        # ring turned past infinity
    elif st == "sport": render_state(U[NAMES.index(st)], st, cap_front=40.0)
    else: render_state(U[NAMES.index(st)], st)
