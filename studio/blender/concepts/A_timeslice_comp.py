# SHIKO WORLD 2.0 · Concept A SUNLINE · Key frame 1 compositor: blends the hour passes from A_coast.py into one
# "time-slice" image. Every pixel picks its hour from where it is on the coast (world Y from pass_data.png):
# south/near = dawn, the festival meadow = noon, the kurkar cliff = golden hour, the stadium = blue hour, the far north = night.
# Sky pixels pick their hour from the screen x (dusk over the sea on the left -> night on the right).
# Run: bpyenv/bin/python A_timeslice_comp.py PASSDIR OUT.png [label]
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
PD, OUT = sys.argv[1], sys.argv[2]
LABEL = sys.argv[3] if len(sys.argv) > 3 else None
ORDER = ["dawn", "noon", "golden", "blue", "night"]
P = [np.asarray(Image.open(f"{PD}/pass_{n}.png").convert("RGB"), dtype=np.float32) / 255.0 for n in ORDER]
# light per-hour print grade (contrast / saturation / warmth), the way each hour would be developed on its own
GRADE = {"dawn": (1.10, 1.10, (1.00, 0.98, 1.02)), "noon": (1.18, 1.08, (1.0, 1.0, 1.0)), "golden": (1.15, 1.15, (1.03, 0.99, 0.92)),
         "blue": (1.05, 1.05, (1.0, 1.0, 1.0)), "night": (1.0, 1.0, (1.0, 1.0, 1.0))}
def grade(im, c, sat, wb):
    im = (im - 0.5) * c + 0.5
    g = im.mean(-1, keepdims=True); im = g + (im - g) * sat
    return np.clip(im * np.array(wb, dtype=np.float32), 0, 1)
P = [grade(p, *GRADE[n]) for p, n in zip(P, ORDER)]
import bpy   # PIL reads 16-bit RGBA PNGs as 8-bit: read the data pass through Blender's image loader instead
_im = bpy.data.images.load(f"{PD}/pass_data.png"); _im.colorspace_settings.name = "Non-Color"
_w, _h = _im.size; D = np.array(_im.pixels[:], dtype=np.float32).reshape(_h, _w, 4)[::-1]
H, W = D.shape[:2]
y = -1500.0 + D[..., 0] * 10000.0
geo = np.clip((D[..., 2] - 0.2) / 0.6, 0, 1)

def smooth_interp(x, xs, ts):
    """piecewise: flat on each hour stretch, smoothstep between them"""
    out = np.full_like(x, ts[0], dtype=np.float32)
    for i in range(len(xs) - 1):
        a, b = xs[i], xs[i + 1]; t0, t1 = ts[i], ts[i + 1]
        u = np.clip((x - a) / max(1e-6, b - a), 0, 1); u = u * u * (3 - 2 * u)
        m = (x >= a) & (x < b)
        out[m] = (t0 + (t1 - t0) * u)[m]
    out[x >= xs[-1]] = ts[-1]
    return out

# Hour field. The coast runs away from the camera, so a slice by world-Y crowds four hours into the top third.
# Instead the slice is a soft diagonal in the frame, bottom-left (dawn surf) -> top-right (night), which follows
# the leading line of the shore. Its stops are placed on the features: canopies = noon, kurkar cliff = golden,
# stadium = blue hour, the town and the sky to the right = night.
import os
yy = np.linspace(0, 1, H, dtype=np.float32)[:, None].repeat(W, 1)          # 0 top .. 1 bottom
xs = np.linspace(0, 1, W, dtype=np.float32)[None, :].repeat(H, 0)
KV, KU = float(os.environ.get("KV", "0.72")), float(os.environ.get("KU", "0.28"))
sfield = KV * (1 - yy) + KU * xs
SS = [float(v) for v in os.environ.get("SS", "0.0,0.30,0.44,0.48,0.56,0.60,0.655,0.69,0.80").split(",")]
TS = [0, 0, 1, 1, 2, 2, 3, 3, 4]
t = smooth_interp(sfield, SS, TS)
def gblur(a, sig):
    r = int(sig * 3); k = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2); k /= k.sum()
    p = np.pad(a, ((r, r), (r, r)), mode="edge")
    p = np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 1, p)
    return np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 0, p)
t = gblur(t, W * 0.012).astype(np.float32)
out = np.zeros_like(P[0])
for i, im in enumerate(P):
    w = np.clip(1.0 - np.abs(t - i), 0, 1)[..., None]
    out += im * w
img = Image.fromarray(np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))
if LABEL:
    dr = ImageDraw.Draw(img)
    try: f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", max(11, W // 110))
    except Exception: f = ImageFont.load_default()
    dr.text((W * 0.012 + 1, H - H * 0.035 + 1), LABEL, font=f, fill=(0, 0, 0))
    dr.text((W * 0.012, H - H * 0.035), LABEL, font=f, fill=(236, 230, 218))
img.save(OUT, quality=93)
# debug: hour map
Image.fromarray((np.clip(t / 4, 0, 1) * 255).astype(np.uint8)).save(OUT.rsplit(".", 1)[0] + "_hourmap.png")
print("saved", OUT, W, H)
