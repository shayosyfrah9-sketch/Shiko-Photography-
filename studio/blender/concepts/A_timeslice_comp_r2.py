# SHIKO WORLD 2.0 · Concept A SUNLINE · ROUND 2 time-slice compositor (Rendered passes -> one image)
# Round-1 critique: slices must follow the coast like a real time-slice photograph.
#  * each pixel of land/sea takes its hour from the along-shore coordinate s = 0.45 x + 0.89 y (from pass_data.png),
#    so every seam is a straight line perpendicular to the shoreline;
#  * the seams are hard in the world and feathered only in the image (Gaussian sigma ~ 10 px -> ~40 px feather);
#  * the sky is ONE continuous sky (the blue-hour pass), never sliced;
#  * NO grading of any pass: every hour is only sun position, sky and exposure of the same camera.
# Run: bpyenv/bin/python A_timeslice_comp_r2.py PASSDIR OUT.jpg [label]
import sys, math, os, numpy as np
from PIL import Image, ImageDraw, ImageFont
import bpy
PD, OUT = sys.argv[1], sys.argv[2]
LABEL = sys.argv[3] if len(sys.argv) > 3 else None
ORDER = ["dawn", "noon", "golden", "blue", "night"]
P = [np.asarray(Image.open(f"{PD}/pass_{n}.png").convert("RGB"), dtype=np.float32) / 255.0 for n in ORDER]
_im = bpy.data.images.load(f"{PD}/pass_data.png"); _im.colorspace_settings.name = "Non-Color"
_w, _h = _im.size; D = np.array(_im.pixels[:], dtype=np.float32).reshape(_h, _w, 4)[::-1]
H, W = D.shape[:2]
s = -2000.0 + D[..., 0] * 10000.0
geo = (D[..., 2] > 0.5).astype(np.float32)
dsh = -1000.0 + D[..., 1] * 1000.0          # distance from the waterline, clamped to [-1000, 0]
# open sea far offshore is not sliced: it carries the same hour as the sky, so no stripe runs out to the horizon
OFF = float(os.environ.get("OFF", "-450"))
offshore = ((dsh < OFF) & (geo > 0.5))

def shore_x(y):   # same curve as A_coast_r2.py (without its +-18 m noise)
    return -520.0 + 0.30 * (y + 900.0) + 170.0 * math.sin((y + 900.0) / 760.0)
def s_at(y): return 0.45 * shore_x(y) + 0.89 * y
# zone borders on the shore (world y): surf | festival | kurkar cliff | stadium | city
YB = [float(v) for v in os.environ.get("YB", "-185,160,690,950").split(",")]
SB = [s_at(y) for y in YB]
idx = np.digitize(s, SB).astype(np.int32)          # 0..4 = dawn..night

def gblur(a, sig):
    r = int(sig * 3); k = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2); k /= k.sum()
    p = np.pad(a, ((r, r), (r, r)), mode="edge")
    p = np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 1, p)
    return np.apply_along_axis(lambda v: np.convolve(v, k, "valid"), 0, p)
SIG = float(os.environ.get("SIG", "10")) * W / 1600.0
out = np.zeros_like(P[0]); wsum = np.zeros((H, W, 1), np.float32)
SKY = ORDER.index(os.environ.get("SKYPASS", "blue"))
for i, im in enumerate(P):
    m = ((idx == i) & (geo > 0.5) & ~offshore).astype(np.float32)
    if i == SKY: m = np.maximum(m, np.maximum(1.0 - geo, offshore.astype(np.float32)))      # the one continuous sky (+ open sea)
    w = gblur(m, SIG)[..., None]
    out += im * w; wsum += w
out = out / np.maximum(wsum, 1e-6)
img = Image.fromarray(np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))
if LABEL:
    dr = ImageDraw.Draw(img)
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", max(11, W // 115))
    dr.text((W * 0.012 + 1, H - H * 0.032 + 1), LABEL, font=f, fill=(0, 0, 0))
    dr.text((W * 0.012, H - H * 0.032), LABEL, font=f, fill=(236, 230, 218))
img.save(OUT, quality=93)
# debug: slice map
Image.fromarray((np.where(geo > 0.5, idx * 60 + 15, 0)).astype(np.uint8)).save(OUT.rsplit(".", 1)[0] + "_slices.png")
# greyscale check sheet of the 5 passes (critique: hours must be tellable apart in greyscale)
th = [Image.fromarray((p * 255).astype(np.uint8)).convert("L").resize((W // 5, H // 5)) for p in P]
g = Image.new("L", (W, H // 5)); [g.paste(t, (i * (W // 5), 0)) for i, t in enumerate(th)]; g.save(OUT.rsplit(".", 1)[0] + "_grey.png")
print("saved", OUT, W, H, "seams s=", [round(v) for v in SB])
