# Burn an honest label into a Rendered frame (corner tag), no other change to the pixels.
# Run: python3 C_label.py IN.png OUT.png "TITLE" "subline"
import sys
from PIL import Image, ImageDraw, ImageFont
src, out, title, sub = sys.argv[1:5]
im = Image.open(src).convert("RGB"); W, H = im.size
d = ImageDraw.Draw(im, "RGBA")
f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max(12, W // 95))
fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", max(10, W // 145))
bw = int(max(d.textlength(title, font=f), d.textlength(sub, font=fs))) + 24; bh = f.size + fs.size + 22
ox, oy = W - bw - 14, H - bh - 14
d.rounded_rectangle((ox, oy, ox + bw, oy + bh), 8, fill=(15, 14, 13, 170))
d.text((ox + 12, oy + 7), title, font=f, fill=(245, 240, 230, 255))
d.text((ox + 12, oy + 13 + f.size), sub, font=fs, fill=(220, 214, 204, 255))
im.save(out)
