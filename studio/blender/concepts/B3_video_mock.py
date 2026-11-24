# Concept B round 3 — the VIDEO state: focus ring turned past infinity. Every layer goes soft (far field least),
# the frame narrows to 2.39:1 with soft bars, and a thin play ring + Hebrew RTL title appear. MOCK-UP UI over the
# Rendered plate + layered composite "video" state.
# Run: python3 B3_video_mock.py VIDEO_STATE.png OUT.png
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
SRC, OUT = sys.argv[1:3]
FD = os.environ.get("RUBIK", "/tmp/claude-0/-home-user/2c38ec15-b058-5d59-86c9-28307ce7ab10/scratchpad/B/fonts/")
im = Image.open(SRC).convert("RGBA"); W, H = im.size; S = 2
IV = (243, 239, 230); INK = (11, 10, 9); RTL = dict(direction="rtl", language="he")
sc = Image.new("L", (W, H), 0); ImageDraw.Draw(sc).ellipse((W // 2 - 330, H // 2 - 120, W // 2 + 330, H // 2 + 170), fill=105)
im.paste(INK + (255,), (0, 0, W, H), sc.filter(ImageFilter.GaussianBlur(70)))   # soft scrim behind the title (<= 40% ink)
ui = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(ui)
bar = int((H - W / 2.39) / 2) * S
d.rectangle((0, 0, W * S, bar), fill=INK + (225,)); d.rectangle((0, H * S - bar, W * S, H * S), fill=INK + (225,))
cx, cy, r = W * S // 2, H * S // 2, 44 * S
d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=IV + (235,), width=2 * S)
d.polygon([(cx - 13 * S, cy - 20 * S), (cx - 13 * S, cy + 20 * S), (cx + 22 * S, cy)], fill=IV + (235,))
f1 = ImageFont.truetype(FD + "Rubik-500.ttf", 22 * S); f2 = ImageFont.truetype(FD + "Rubik-400.ttf", 15 * S)
d.text((cx, cy + r + 22 * S), "וידאו", font=f1, fill=IV + (245,), anchor="ma", **RTL)
d.text((cx, cy + r + 56 * S), "הפוקוס עבר את האינסוף · השואוריל מתחיל", font=f2, fill=IV + (200,), anchor="ma", **RTL)
# lens scale strip (RTL) in the lower bar, video mark lit
y = H * S - bar // 2; x0, x1 = 300 * S, (W - 300) * S
d.line((x0, y - 10 * S, x1, y - 10 * S), fill=IV + (110,), width=S)
marks = ["פורטרטים", "פסטיבלים", "ספורט", "גלישה", "וידאו"]
for i, m in enumerate(marks):
    x = x1 - i * (x1 - x0) / 4; on = m == "וידאו"
    d.line((x, y - (18 if on else 14) * S, x, y - 10 * S), fill=IV + (250 if on else 150,), width=S * (2 if on else 1))
    d.text((x, y - 2 * S), m, font=ImageFont.truetype(FD + ("Rubik-500.ttf" if on else "Rubik-400.ttf"), 14 * S), fill=IV + (250 if on else 170,), anchor="ma", **RTL)
d.text((24 * S, 14 * S), "MOCK-UP UI over Rendered plate (Cycles) + layered composite, focus ring past infinity (all layers soft)", font=ImageFont.truetype(FD + "Rubik-400.ttf", 10 * S), fill=IV + (150,))
ui = ui.resize((W, H), Image.LANCZOS); im.alpha_composite(ui); im.convert("RGB").save(OUT); print("saved", OUT)
