# SHIKO WORLD 2.0 — Concept C "WHERE HE STOOD", round 1: photo-viewing MOCK-UP (PIL composite, not a render).
# Panel 1 "the click": Shay's real photo surf0001.jpg (uncropped, true 1500x1238 aspect, thin ivory mount) snapped into the
#   surfer-shaped absence of the Rendered key frame 2. Its position/scale come from the _register.json written by
#   C_where_he_stood.py (the absence in the 3D spray was carved from a silhouette traced off this same photo).
# Panel 2 "the viewer": the photo flattened front-parallel on an ivory mount, world dimmed, 1/7 + arrows + dock icons.
# Run: python3 C_mockup_click.py RENDER.png REGISTER.json PHOTO.jpg OUT.png
import sys, json
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

rpath, jpath, ppath, out = sys.argv[1:5]
R = Image.open(rpath).convert("RGB"); W, H = R.size
reg = json.load(open(jpath)); rect = reg["rect"]; fw, fh = reg["frame_w"], reg["frame_h"]
P = Image.open(ppath).convert("RGB"); pw, ph = P.size
IVORY = (241, 236, 224); INK = (34, 32, 30)
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(sz, b=False): return ImageFont.truetype(FB if b else F, sz)

def plane2px(x, y): return (W / 2 + x / fw * W, H / 2 - y / fh * H)

def label(img, text, sub=None, pos="tl"):
    d = ImageDraw.Draw(img, "RGBA"); f = font(max(12, W // 95), True); fs = font(max(10, W // 145))
    tw = d.textlength(text, font=f); sw = d.textlength(sub, font=fs) if sub else 0
    bw = int(max(tw, sw)) + 24; bh = (f.size + 16) + ((fs.size + 6) if sub else 0)
    ox, oy = (14, 14) if pos == "tl" else ((14, H - bh - 14) if pos == "bl" else (W - bw - 14, H - bh - 14))
    d.rounded_rectangle((ox, oy, ox + bw, oy + bh), 8, fill=(15, 14, 13, 175))
    d.text((ox + 12, oy + 7), text, font=f, fill=(245, 240, 230, 255))
    if sub: d.text((ox + 12, oy + 7 + f.size + 6), sub, font=fs, fill=(220, 214, 204, 255))

# ---------- panel 1: the click
A = R.copy()
x0, y0 = plane2px(rect["left"], rect["top"]); x1, y1 = plane2px(rect["left"] + rect["w"], rect["top"] - rect["h"])
x0, y0, x1, y1 = [int(round(v)) for v in (x0, y0, x1, y1)]
tw_, th_ = x1 - x0, y1 - y0
# keep the TRUE aspect: derive height from width (never crop, never stretch)
th_ = int(round(tw_ * ph / pw))
Pi = P.resize((tw_, th_), Image.LANCZOS)
m = max(3, W // 400)                                   # thin ivory mount
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
ds.rectangle((x0 - m + 6, y0 - m + 8, x0 + tw_ + m + 6, y0 + th_ + m + 8), fill=(0, 0, 0, 90))
sh = sh.filter(ImageFilter.GaussianBlur(10)); A = Image.alpha_composite(A.convert("RGBA"), sh).convert("RGB")
d = ImageDraw.Draw(A); d.rectangle((x0 - m, y0 - m, x0 + tw_ + m - 1, y0 + th_ + m - 1), fill=IVORY)
A.paste(Pi, (x0, y0))
# shutter tick marks (frame-line corners) where the camera settles
cl = W // 60; c = (245, 240, 230)
for (cx, cy, sx, sy) in ((x0 - 3 * m, y0 - 3 * m, 1, 1), (x0 + tw_ + 3 * m, y0 - 3 * m, -1, 1), (x0 - 3 * m, y0 + th_ + 3 * m, 1, -1), (x0 + tw_ + 3 * m, y0 + th_ + 3 * m, -1, -1)):
    d.line((cx, cy, cx + sx * cl, cy), fill=c, width=2); d.line((cx, cy, cx, cy + sy * cl), fill=c, width=2)
label(A, "MOCK-UP 1/2 · the click", "Rendered key frame 2 (Cycles) + Shay's real photo surf0001.jpg composited in PIL (uncropped 1500×1238, ivory mount)", "br")

# ---------- panel 2: the viewer (front-parallel, ivory mount, world dimmed)
B = R.filter(ImageFilter.GaussianBlur(W // 160)); B = ImageEnhance.Brightness(B).enhance(0.38); B = ImageEnhance.Color(B).enhance(0.7)
vh = int(H * 0.66); vw = int(vh * pw / ph); mm = max(10, W // 90)
vx = (W - vw) // 2; vy = int(H * 0.07)
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
ds.rectangle((vx - mm + 10, vy - mm + 16, vx + vw + mm + 10, vy + vh + mm + 16), fill=(0, 0, 0, 140))
sh = sh.filter(ImageFilter.GaussianBlur(18)); B = Image.alpha_composite(B.convert("RGBA"), sh).convert("RGB")
d = ImageDraw.Draw(B, "RGBA"); d.rectangle((vx - mm, vy - mm, vx + vw + mm - 1, vy + vh + mm - 1), fill=IVORY)
B.paste(P.resize((vw, vh), Image.LANCZOS), (vx, vy))
fy = vy + vh + mm + int(H * 0.025); fm = font(max(14, W // 75)); fsm = font(max(11, W // 110))
cap = "1 / 7"; d.text(((W - d.textlength(cap, font=fm)) / 2, fy), cap, font=fm, fill=(240, 234, 222, 255))
# arrows
ay = vy + vh // 2; r_ = W // 45
for sx, cx in ((-1, vx - mm - r_ * 2), (1, vx + vw + mm + r_ * 2)):
    d.ellipse((cx - r_, ay - r_, cx + r_, ay + r_), outline=(240, 234, 222, 200), width=2)
    d.line((cx - sx * r_ * 0.25, ay - r_ * 0.4, cx + sx * r_ * 0.2, ay, cx - sx * r_ * 0.25, ay + r_ * 0.4), fill=(240, 234, 222, 230), width=3)
hint = "swipe up · the back of the print"
d.text(((W - d.textlength(hint, font=fsm)) / 2, fy + fm.size + 8), hint, font=fsm, fill=(200, 194, 184, 220))
# dock: home · surf field · WhatsApp · booking (icons only, as Shay asked)
dk_y = H - int(H * 0.055); gap = W // 22; icons = 4; dx0 = W // 2 - gap * (icons - 1) / 2; rr = W // 75
d.rounded_rectangle((dx0 - gap * 0.8, dk_y - rr * 1.9, dx0 + gap * (icons - 1) + gap * 0.8, dk_y + rr * 1.9), 22, fill=(20, 19, 18, 150))
col = (240, 234, 222, 235)
for i in range(icons):
    cx = dx0 + i * gap; cy = dk_y
    if i == 0:   # home
        d.polygon([(cx - rr, cy), (cx, cy - rr), (cx + rr, cy)], outline=col, width=2); d.rectangle((cx - rr * 0.7, cy, cx + rr * 0.7, cy + rr * 0.9), outline=col, width=2)
    elif i == 1:  # wave (surf field)
        d.arc((cx - rr, cy - rr * 0.6, cx + rr * 0.2, cy + rr * 0.8), 180, 360, fill=col, width=2); d.arc((cx - rr * 0.2, cy - rr * 0.6, cx + rr, cy + rr * 0.8), 0, 180, fill=col, width=2)
    elif i == 2:  # chat bubble (WhatsApp)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=col, width=2); d.polygon([(cx - rr * 0.8, cy + rr * 0.5), (cx - rr * 1.15, cy + rr * 1.15), (cx - rr * 0.3, cy + rr * 0.9)], fill=col)
    else:         # calendar (booking)
        d.rectangle((cx - rr, cy - rr * 0.8, cx + rr, cy + rr), outline=col, width=2); d.line((cx - rr, cy - rr * 0.3, cx + rr, cy - rr * 0.3), fill=col, width=2)
label(B, "MOCK-UP 2/2 · the viewer", "same real photo front-parallel, true ratio; world dimmed; UI drawn in PIL", "bl")

# ---------- stack
gap_ = 12
O = Image.new("RGB", (W, H * 2 + gap_), (12, 12, 12)); O.paste(A, (0, 0)); O.paste(B, (0, H + gap_))
O.save(out, quality=92)
print("photo rect px", x0, y0, tw_, th_, "aspect", tw_ / th_, "photo aspect", pw / ph)
