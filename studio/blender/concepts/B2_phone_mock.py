# Concept B round 2 — vertical phone frame (390x844 CSS px), MOCK-UP UI over a Rendered + layered-composite plate.
# Focus labels sit ON the real planes: a thin ivory tick down to the plane + field name + distance, 44 px tall, no boxes.
# Run: python3 B2_phone_mock.py PLATE@2x.png OUT_390.png OUT_2x.png FOCUSED "Name|dist|x|y" ...   (x,y in plate pixels)
import sys
from PIL import Image, ImageDraw, ImageFont
PLATE, OUT1, OUT2, FOCUSED = sys.argv[1:5]; ANCH = [s.split("|") for s in sys.argv[5:]]
im = Image.open(PLATE).convert("RGBA"); W, H = im.size; k = W / 390.0          # px per CSS px (2.0 for a 780 plate)
IV = (243, 239, 230); GOLD = (243, 220, 176)
ui = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ui)
F = lambda sz, w="Light": ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-%s.otf" % w, int(sz * k))
def tracked(x, y, t, f, fill, tr=0.16):
    for ch in t:
        d.text((x, y), ch, font=f, fill=fill); x += d.textlength(ch, font=f) + f.size * tr
    return x
# soft scrims top and bottom (<= 30% ink) so UI holds contrast over the sky and the dark ridge
sc = Image.new("L", (1, 256))
for i in range(256): sc.putpixel((0, i), int(80 * (1 - i / 255) ** 1.6))
top = sc.resize((W, int(130 * k))); ui.paste((11, 10, 9, 255), (0, 0, W, top.size[1]), top)
bot = sc.resize((W, int(190 * k))).transpose(Image.FLIP_TOP_BOTTOM); ui.paste((11, 10, 9, 255), (0, H - bot.size[1], W, H), bot)
ui2 = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ui2)
lw = max(1, int(1 * k)); iv = IV + (235,)
# header: camera mark (home) left, booking (gold) + WhatsApp right
X, Y = 20 * k, 22 * k
d.rounded_rectangle((X, Y + 4 * k, X + 24 * k, Y + 20 * k), radius=3 * k, outline=iv, width=lw + 1)
d.rectangle((X + 7 * k, Y + 1 * k, X + 15 * k, Y + 4 * k), outline=iv, width=lw); d.ellipse((X + 7 * k, Y + 7 * k, X + 17 * k, Y + 17 * k), outline=iv, width=lw + 1)
X = W - 20 * k - 22 * k
d.ellipse((X, Y, X + 22 * k, Y + 22 * k), outline=iv, width=lw + 1); d.polygon([(X + 2 * k, Y + 17 * k), (X, Y + 24 * k), (X + 7 * k, Y + 20 * k)], fill=iv)
d.arc((X + 6 * k, Y + 6 * k, X + 16 * k, Y + 17 * k), 100, 260, fill=iv, width=lw + 1)
X2 = X - 40 * k
d.rounded_rectangle((X2, Y + 2 * k, X2 + 22 * k, Y + 23 * k), radius=2 * k, outline=GOLD + (240,), width=lw + 1)
d.line((X2, Y + 8 * k, X2 + 22 * k, Y + 8 * k), fill=GOLD + (240,), width=lw)
# focus labels on the planes: tick (from label down to the plane) + name + distance; focused one brighter with a dot
for name, dist, x, y in ANCH:
    x = float(x); y = float(y); on = (name == FOCUSED); a = 245 if on else 170
    ty = y - 44 * k                                       # 44 px tall label: text block + tick
    d.line((x, ty + 22 * k, x, y - 3 * k), fill=IV + (a,), width=lw)
    if on: d.ellipse((x - 3 * k, y - 3 * k, x + 3 * k, y + 3 * k), fill=IV + (a,))
    else: d.ellipse((x - 2 * k, y - 2 * k, x + 2 * k, y + 2 * k), outline=IV + (a,), width=lw)
    f1 = F(12, "Regular" if on else "Light"); f2 = F(10, "Light")
    tw = d.textlength(name.upper(), font=f1) + f1.size * 0.16 * len(name)
    x0 = min(max(x - tw / 2, 12 * k), W - tw - 12 * k)
    tracked(x0, ty - 2 * k, name.upper(), f1, IV + (a,)); d.text((x0, ty + 13 * k), dist, font=f2, fill=IV + (a - 30,))
# bottom: lens distance scale (the ring), focused mark highlighted, + dock
sy = H - 78 * k; d.line((24 * k, sy, W - 24 * k, sy), fill=IV + (90,), width=lw)
marks = [("9 m", "Portrait"), ("30 m", "Festival"), ("700 m", "Sport"), ("∞", "Surf"), ("▶", "Video")]
for i, (m, nm) in enumerate(marks):
    x = 24 * k + i * (W - 48 * k) / 4; on = (nm == FOCUSED)
    d.line((x, sy - (8 if on else 5) * k, x, sy), fill=IV + (240 if on else 140,), width=lw + (1 if on else 0))
    fm = F(11, "Regular" if on else "Light"); tw = d.textlength(m, font=fm)
    d.text((min(max(x - tw / 2, 16 * k), W - tw - 16 * k), sy + 6 * k), m, font=fm, fill=IV + (240 if on else 150,))
f = F(13, "Regular")
d.text((24 * k, H - 38 * k), "Works", font=f, fill=iv)
tw = d.textlength("Book a shoot", font=f); d.text((W / 2 - tw / 2, H - 38 * k), "Book a shoot", font=f, fill=GOLD + (245,))
tw = d.textlength("WhatsApp", font=f); d.text((W - 24 * k - tw, H - 38 * k), "WhatsApp", font=f, fill=iv)
d.text((12 * k, 60 * k), "MOCK-UP UI over Rendered plate (Cycles) + layered focus composite", font=F(7.5), fill=IV + (150,))
im.alpha_composite(ui); im.alpha_composite(ui2)
im.convert("RGB").save(OUT2); im.convert("RGB").resize((390, int(round(H / k))), Image.LANCZOS).save(OUT1)
print("saved", OUT1, OUT2)
