# Burn a small honest label into a review image (bottom-left, ivory, ~55% opacity) and save as the deliverable.
# Run: python3 B_label.py IN.png OUT.png "LABEL TEXT"
import sys
from PIL import Image, ImageDraw, ImageFont
IN, OUT, TEXT = sys.argv[1:4]
im = Image.open(IN).convert("RGBA"); W, H = im.size; S = 2
ui = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(ui)
f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", 11 * S)
x, y = 24 * S, H * S - 34 * S
tw = d.textlength(TEXT, font=f)
d.rounded_rectangle((x - 8 * S, y - 6 * S, x + tw + 8 * S, y + 18 * S), radius=3 * S, fill=(11, 10, 9, 120))
d.text((x, y), TEXT, font=f, fill=(243, 239, 230, 215))
im.alpha_composite(ui.resize((W, H), Image.LANCZOS)); im.convert("RGB").save(OUT)
print("saved", OUT)
