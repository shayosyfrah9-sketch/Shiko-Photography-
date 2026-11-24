# Concept B round 3 — vertical phone frame (390x844 CSS px), Hebrew RTL MOCK-UP UI over a Rendered + layered-composite plate.
# Labels: field name (Rubik Medium 15 px) + metres as a small second line (Rubik 13 px), on a 60% ink pill (>= 4.5:1 contrast
# is measured and printed), a hairline leader + dot down to the real plane. Distance scale = field names, RTL (near on the right).
# Booking uses the same calendar icon (ring tabs) as the desktop viewer.
# Run: python3 B3_phone_mock.py PLATE@2x.png OUT_390.png OUT_2x.png FOCUSED "name|metres|x|y" ...   (x,y in plate pixels)
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
PLATE, OUT1, OUT2, FOCUSED = sys.argv[1:5]; ANCH = [s.split("|") for s in sys.argv[5:]]
FD = os.environ.get("RUBIK", "/tmp/claude-0/-home-user/2c38ec15-b058-5d59-86c9-28307ce7ab10/scratchpad/B/fonts/")
im = Image.open(PLATE).convert("RGBA"); W, H = im.size; k = W / 390.0
IV = (243, 239, 230); GOLD = (243, 220, 176); INK = (11, 10, 9)
F = lambda sz, w=400: ImageFont.truetype(FD + "Rubik-%d.ttf" % w, int(round(sz * k)))
RTL = dict(direction="rtl", language="he")
def lumi(c):
    c = np.asarray(c, np.float64) / 255; c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4); return c @ [0.2126, 0.7152, 0.0722]
def contrast(a, b): la, lb = sorted((lumi(a), lumi(b)), reverse=True); return (la + 0.05) / (lb + 0.05)
base = np.asarray(im.convert("RGB"), np.float32)
ui = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ui)
# soft scrims top and bottom (<= 35% ink)
sc = Image.new("L", (1, 256))
for i in range(256): sc.putpixel((0, i), int(90 * (1 - i / 255) ** 1.6))
top = sc.resize((W, int(120 * k))); ui.paste(INK + (255,), (0, 0, W, top.size[1]), top)
bot = sc.resize((W, int(210 * k))).transpose(Image.FLIP_TOP_BOTTOM); ui.paste(INK + (255,), (0, H - bot.size[1], W, H), bot)
lw = max(1, int(round(1 * k))); iv = IV + (240,)
def calendar(X, Y, s, col):   # same icon as the desktop viewer: body, header line, two ring tabs
    d.rounded_rectangle((X, Y + 3 * s, X + 22 * s, Y + 23 * s), radius=2 * s, outline=col, width=lw + 1)
    d.line((X, Y + 9 * s, X + 22 * s, Y + 9 * s), fill=col, width=lw)
    for xx in (X + 6 * s, X + 16 * s): d.line((xx, Y, xx, Y + 6 * s), fill=col, width=lw + 1)
def whatsapp(X, Y, s, col):
    d.ellipse((X, Y, X + 22 * s, Y + 22 * s), outline=col, width=lw + 1); d.polygon([(X + 2 * s, Y + 17 * s), (X, Y + 24 * s), (X + 7 * s, Y + 20 * s)], fill=col)
    d.arc((X + 6 * s, Y + 6 * s, X + 16 * s, Y + 17 * s), 100, 260, fill=col, width=lw + 1)
# header (RTL): home camera mark on the RIGHT; WhatsApp + booking on the LEFT
Y = 24 * k; X = W - 20 * k - 24 * k
d.rounded_rectangle((X, Y + 4 * k, X + 24 * k, Y + 20 * k), radius=3 * k, outline=iv, width=lw + 1)
d.rectangle((X + 7 * k, Y + 1 * k, X + 15 * k, Y + 4 * k), outline=iv, width=lw); d.ellipse((X + 7 * k, Y + 7 * k, X + 17 * k, Y + 17 * k), outline=iv, width=lw + 1)
whatsapp(20 * k, Y, k, iv); calendar(60 * k, Y - 1 * k, k, GOLD + (245,))
# focus labels on the planes
rep = []
for name, dist, x, y in ANCH:
    x = float(x); y = float(y); on = (name == FOCUSED)
    f1 = F(15, 500); f2 = F(13, 400)
    t1 = d.textlength(name, font=f1, **RTL); t2 = d.textlength(dist, font=f2, **RTL)
    pw = max(t1, t2) + 22 * k; ph = 46 * k; gap = 30 * k
    x0 = min(max(x - pw / 2, 10 * k), W - pw - 10 * k); y0 = y - gap - ph
    box_ = (int(x0), int(y0), int(x0 + pw), int(y0 + ph))
    bg = base[box_[1]:box_[3], box_[0]:box_[2]].reshape(-1, 3).mean(0)
    pill = INK if not on else IV
    eff = tuple(0.6 * np.array(pill) + 0.4 * bg) if not on else tuple(0.92 * np.array(pill) + 0.08 * bg)
    tc = IV if not on else INK
    rep.append("%s contrast %.1f:1" % (name, contrast(tc, eff)))
    d.rounded_rectangle(box_, radius=10 * k, fill=pill + ((153,) if not on else (235,)))
    d.line((x, y0 + ph, x, y - 4 * k), fill=IV + (220,), width=lw)
    d.ellipse((x - 3.5 * k, y - 3.5 * k, x + 3.5 * k, y + 3.5 * k), fill=IV + (240,) if on else None, outline=IV + (240,), width=lw)
    xr = x0 + pw - 11 * k
    d.text((xr, y0 + 5 * k), name, font=f1, fill=tc + (255,), anchor="ra", **RTL)
    d.text((xr, y0 + 25 * k), dist, font=f2, fill=tc + (215,), anchor="ra", **RTL)
# lens distance scale = field names, RTL: near (portrait) on the right
sy = H - 104 * k; d.line((22 * k, sy, W - 22 * k, sy), fill=IV + (110,), width=lw)
marks = [("פורטרטים", "6 מ׳"), ("פסטיבלים", "40 מ׳"), ("ספורט", "700 מ׳"), ("גלישה", "∞"), ("וידאו", "▶")]
for i, (nm, m) in enumerate(marks):
    x = W - 40 * k - i * (W - 80 * k) / 4; on = (nm == FOCUSED)
    d.line((x, sy - (9 if on else 5) * k, x, sy), fill=IV + (250 if on else 150,), width=lw + (1 if on else 0))
    if on: d.ellipse((x - 3 * k, sy - 3 * k, x + 3 * k, sy + 3 * k), fill=GOLD + (250,))
    d.text((x, sy + 8 * k), nm, font=F(13, 500 if on else 400), fill=IV + (250 if on else 185,), anchor="ma", **RTL)
    d.text((x, sy + 26 * k), m, font=F(11, 400), fill=IV + (200 if on else 140,), anchor="ma", **RTL)
# dock (RTL): works on the right, booking centre (gold, calendar), WhatsApp left
f = F(15, 400); yb = H - 40 * k
d.text((W - 24 * k, yb), "עבודות", font=f, fill=iv, anchor="ra", **RTL)
tw = d.textlength("לקביעת צילום", font=f, **RTL); cxm = W / 2 + 13 * k
d.text((cxm + tw / 2, yb), "לקביעת צילום", font=f, fill=GOLD + (250,), anchor="ra", **RTL); calendar(cxm - tw / 2 - 30 * k, yb - 2 * k, 0.85 * k, GOLD + (250,))
d.text((24 * k, yb), "וואטסאפ", font=f, fill=iv, anchor="la", **RTL)
d.text((12 * k, 64 * k), "MOCK-UP UI (Hebrew RTL, Rubik) over Rendered plate (Cycles) + layered focus composite", font=ImageFont.truetype(FD + "Rubik-400.ttf", int(8 * k)), fill=IV + (150,))
im.alpha_composite(ui)
im.convert("RGB").save(OUT2); im.convert("RGB").resize((390, int(round(H / k))), Image.LANCZOS).save(OUT1)
print("saved", OUT1, OUT2, "|", "; ".join(rep))
