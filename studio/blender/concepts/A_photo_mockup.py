# SHIKO WORLD 2.0 · Concept A SUNLINE · photo-viewing frame (MOCK-UP, composited with PIL)
# Background: the Rendered key frame 2 (18:30, golden hour), paused, dimmed to 35 % and softly blurred.
# Foreground: Shay's REAL photo (Shira room, 2w2a0443, photo 8 of 42), uncropped, true 3:2 aspect, thin ivory mount.
# Interface (hairline sun-arc, counter, gallery, WhatsApp / booking dock) is drawn on top: it is a mock-up, not rendered.
# Run: python A_photo_mockup.py BACKGROUND.png PHOTO.jpg OUT.jpg
import sys, math
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
BG, PHOTO, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
LOGO = "/home/user/shiko-world2/assets/logo-lens.png"
W, H = 1600, 900
IVORY = (241, 236, 226); INK = (236, 230, 218)
FONT = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"; FONT_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
def f(sz, m=False):
    try: return ImageFont.truetype(FONT_M if m else FONT, sz)
    except Exception: return ImageFont.load_default()

bg = Image.open(BG).convert("RGB").resize((W, H), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(9))
bg = ImageEnhance.Brightness(bg).enhance(0.35)
img = bg.copy()

# --- the photograph: never cropped, scaled as a whole to 68 % of the viewport width, exact aspect
ph = Image.open(PHOTO).convert("RGB")
pw0, phh0 = ph.size
from math import gcd
g = gcd(pw0, phh0); uw, uh = pw0 // g, phh0 // g      # exact aspect unit (3:2 here)
k = int(W * 0.62) // uw; pw, phh = k * uw, k * uh    # whole multiples, so the ratio is exact
ph = ph.resize((pw, phh), Image.LANCZOS)
M = 12                                           # thin ivory mount
x0 = (W - pw) // 2; y0 = (H - phh) // 2 + 14
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
sd.rectangle((x0 - M + 10, y0 - M + 18, x0 + pw + M + 10, y0 + phh + M + 22), fill=(0, 0, 0, 120))
sh = sh.filter(ImageFilter.GaussianBlur(22))
img.paste(sh, (0, 0), sh)
d = ImageDraw.Draw(img)
d.rectangle((x0 - M, y0 - M, x0 + pw + M - 1, y0 + phh + M - 1), fill=IVORY)
img.paste(ph, (x0, y0))

# --- hairline sun-arc across the top, with five hour marks and the paused minute
cx, R = W // 2, 2241; cy = 40 + R
arc_top = cy - R
def arc_pt(t):   # t: 0 (dawn, left) .. 1 (midnight, right)
    a = math.radians(270 - 12.1 + t * 24.2)   # shallow slice of a big circle
    return (cx + R * math.cos(a), cy + R * math.sin(a))
pts = [arc_pt(i / 200) for i in range(201)]
d.line(pts, fill=(236, 230, 218), width=1)
marks = [(0.0, "06:10"), (0.22, "11:00"), (0.52, "18:30"), (0.62, "20:15"), (1.0, "00:00")]
icons = ["surf", "fest", "portrait", "sport", "video"]
for (t, lab), ic in zip(marks, icons):
    x, y = arc_pt(t)
    d.ellipse((x - 3, y - 3, x + 3, y + 3), outline=INK, width=1)
now_t = 0.52 + 0.012
x, y = arc_pt(now_t)
d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(233, 162, 90))
d.ellipse((x - 11, y - 11, x + 11, y + 11), outline=(233, 162, 90), width=1)
tw = d.textlength("18:42", font=f(15, True)); d.text((x - tw / 2, y + 14), "18:42", font=f(15, True), fill=INK)
for (t, lab) in marks:
    if abs(t - now_t) < 0.03: continue   # the live marker carries the time here
    xx, yy = arc_pt(t)
    tw = d.textlength(lab, font=f(11))
    d.text((xx - tw / 2, yy - 22), lab, font=f(11), fill=(200, 194, 182))

# --- Home: the Shiko camera mark, top-left (icon only)
try:
    lg = Image.open(LOGO).convert("RGBA").crop((130, 60, 900, 570))
    lg = lg.resize((44, int(44 * lg.height / lg.width)), Image.LANCZOS)
    img.paste(lg, (36, 30), lg)
except Exception as e:
    print("logo skipped", e)

# --- room line, counter, gallery link under the photo
yb = y0 + phh + M + 18
d.text((x0 - M, yb), "PORTRAITS  ·  SHIRA", font=f(13, True), fill=INK)
cnt = "‹    8 / 42    ›"
tw = d.textlength(cnt, font=f(15, True)); d.text(((W - tw) / 2, yb - 2), cnt, font=f(15, True), fill=INK)
gl = "Gallery  ↗"
tw = d.textlength(gl, font=f(13, True)); d.text((x0 + pw + M - tw, yb), gl, font=f(13, True), fill=INK)

# --- dock: WhatsApp-style chat bubble + booking (calendar), bottom-right, always one tap (generic glyphs)
bx, by = W - 132, H - 70
d.ellipse((bx, by, bx + 44, by + 44), outline=INK, width=1)
d.ellipse((bx + 12, by + 12, bx + 32, by + 30), outline=INK, width=2); d.polygon([(bx + 14, by + 27), (bx + 11, by + 34), (bx + 19, by + 30)], fill=INK)
bx2 = bx + 58
d.ellipse((bx2, by, bx2 + 44, by + 44), outline=INK, width=1)
d.rectangle((bx2 + 13, by + 14, bx2 + 31, by + 31), outline=INK, width=2); d.line((bx2 + 13, by + 19, bx2 + 31, by + 19), fill=INK, width=2)
d.line((bx2 + 17, by + 11, bx2 + 17, by + 16), fill=INK, width=2); d.line((bx2 + 27, by + 11, bx2 + 27, by + 16), fill=INK, width=2)

# --- honest label
lab = "MOCK-UP  ·  background: Rendered key frame 2 (Blender Cycles), dimmed 35 % + blurred  ·  photo: Shay's real photo 2w2a0443, uncropped 3:2  ·  UI drawn in PIL"
d.text((24, H - 24), lab, font=f(11), fill=(170, 165, 155))
img.save(OUT, quality=94)
print("saved", OUT, "photo box", pw, phh, "ratio", pw / phh, "source", pw0 / phh0)
