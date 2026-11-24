# Concept B round 3 — six focus states on one sheet (hyperfocal, portrait, festival, sport, surf, video past infinity).
# Run: python3 B3_sheet.py OUT.png "img|Hebrew name|English caption|blur line" x6
import sys, os
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1]; items = [a.split("|") for a in sys.argv[2:]]
FD = os.environ.get("RUBIK", "/tmp/claude-0/-home-user/2c38ec15-b058-5d59-86c9-28307ce7ab10/scratchpad/B/fonts/")
TW, TH, G, CAP = 800, 450, 16, 62
W = 3 * TW + 4 * G; H = 2 * (TH + CAP) + 3 * G + 50
sh = Image.new("RGB", (W, H), (14, 13, 12)); d = ImageDraw.Draw(sh)
fh = ImageFont.truetype(FD + "Rubik-500.ttf", 20); fe = ImageFont.truetype(FD + "Rubik-400.ttf", 15); fs = ImageFont.truetype(FD + "Rubik-300.ttf", 13)
d.text((G, 14), "Concept B round 3 · one fixed 50 mm view, six focus states · Rendered plate (Blender Cycles) + layered lens-kernel composite (offline, web-shader method)", font=fe, fill=(230, 226, 218))
for i, (img, he, en, bl) in enumerate(items):
    x = G + (i % 3) * (TW + G); y = 50 + G + (i // 3) * (TH + CAP + G)
    sh.paste(Image.open(img).convert("RGB").resize((TW, TH), Image.LANCZOS), (x, y))
    d.text((x + TW, y + TH + 8), he, font=fh, fill=(243, 239, 230), anchor="ra", direction="rtl", language="he")
    d.text((x, y + TH + 10), en, font=fe, fill=(230, 226, 218)); d.text((x, y + TH + 34), bl, font=fs, fill=(170, 166, 158))
sh.save(OUT); print("saved", OUT, sh.size)
