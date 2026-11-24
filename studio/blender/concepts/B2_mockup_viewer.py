# Concept B DEPTH OF FIELD round 2 — photo-viewing state, MOCK-UP (PIL composite over a Cycles-rendered backplate).
# Backplate: the same fixed view rendered with focus at 0.3 m (nothing in focus: the world becomes bokeh).
# Photo: Shay's real FreeEarth photo 2w2a1130 (1200x1800), never cropped, true aspect, thin ivory mount.
# The world leans ~12% toward the photo's own palette; the photo itself is never tinted.
# Run: python3 B_mockup_photo_view.py BACKPLATE.png PHOTO.jpg OUT.png
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat

BACK, PHOTO, OUT = sys.argv[1:4]
W, H = 1600, 900
S = 2                                   # supersample UI drawing
IVORY = (243, 239, 230)
FT = "/usr/share/fonts/opentype/inter/Inter-Light.otf"
FTT = "/usr/share/fonts/opentype/inter/Inter-Thin.otf"

bg = Image.open(BACK).convert("RGB").resize((W, H), Image.LANCZOS)
photo = Image.open(PHOTO).convert("RGB")
pw0, ph0 = photo.size

# 1) world takes its light from the photograph: tint the bokeh 12% toward the photo's mean colour (luminance-preserving)
mean = ImageStat.Stat(photo.resize((64, 96))).mean
lum = 0.2126 * mean[0] + 0.7152 * mean[1] + 0.0722 * mean[2]
tint = tuple(min(255, int(c / lum * 128)) for c in mean)
gray = bg.convert("L").convert("RGB")
tinted_gray = Image.merge("RGB", [ch.point(lambda v, k=k: min(255, int(v * tint[k] / 128))) for k, ch in enumerate(gray.split())])
tinted = Image.blend(bg, tinted_gray, 0.12)
# slight darkening so the print carries the frame (max 8% black, per art direction)
tinted = Image.blend(tinted, Image.new("RGB", (W, H), (0, 0, 0)), 0.08)

# 2) the print: 64% of the viewport height, true aspect, thin ivory mount (1% of the short side of the viewport)
ph = int(H * 0.64); pw = round(ph * pw0 / ph0)
m = max(2, round(min(W, H) * 0.01))
print_img = photo.resize((pw, ph), Image.LANCZOS)
cx, cy = W // 2, int(H * 0.47)
x0, y0 = cx - pw // 2 - m, cy - ph // 2 - m
canvas = tinted.copy()
# soft contact shadow (<= 8% black)
sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rectangle((x0 + 4, y0 + 10, x0 + pw + 2 * m + 4, y0 + ph + 2 * m + 14), fill=int(255 * 0.08))
sh = sh.filter(ImageFilter.GaussianBlur(18))
canvas = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), canvas, sh)
ImageDraw.Draw(canvas).rectangle((x0, y0, x0 + pw + 2 * m - 1, y0 + ph + 2 * m - 1), fill=IVORY)
canvas.paste(print_img, (x0 + m, y0 + m))

# 3) hairline UI (drawn 2x, downsampled)
ui = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(ui)
iv = IVORY + (235,); hl = IVORY + (64,)
def font(sz, thin=False): return ImageFont.truetype(FTT if thin else FT, sz * S)
def tracked(x, y, text, f, fill, track=0.28, anchor="l"):
    widths = [d.textlength(ch, font=f) for ch in text]; tw = sum(widths) + f.size * track * (len(text) - 1)
    if anchor == "c": x -= tw / 2
    if anchor == "r": x -= tw
    for ch, w_ in zip(text, widths):
        d.text((x, y), ch, font=f, fill=fill); x += w_ + f.size * track
    return tw
lw = 1 * S
# home = camera mark (top-left): body + lens ring
X, Y = 40 * S, 34 * S
d.rounded_rectangle((X, Y + 5 * S, X + 30 * S, Y + 25 * S), radius=3 * S, outline=iv, width=lw + 1)
d.rectangle((X + 9 * S, Y + 1 * S, X + 19 * S, Y + 5 * S), outline=iv, width=lw + 1)
d.ellipse((X + 9 * S, Y + 9 * S, X + 21 * S, Y + 21 * S), outline=iv, width=lw + 1)
# top-right: booking (calendar) and WhatsApp (bubble)
X = W * S - 40 * S - 26 * S
d.ellipse((X, Y + 1 * S, X + 26 * S, Y + 27 * S), outline=iv, width=lw + 1)
d.polygon([(X + 3 * S, Y + 21 * S), (X + 1 * S, Y + 29 * S), (X + 9 * S, Y + 25 * S)], fill=iv)
d.arc((X + 7 * S, Y + 7 * S, X + 19 * S, Y + 21 * S), 100, 260, fill=iv, width=lw + 1)
X2 = X - 52 * S
d.rounded_rectangle((X2, Y + 4 * S, X2 + 26 * S, Y + 28 * S), radius=2 * S, outline=(243, 220, 176, 240), width=lw + 1)
d.line((X2, Y + 11 * S, X2 + 26 * S, Y + 11 * S), fill=(243, 220, 176, 240), width=lw)
for xx in (X2 + 7 * S, X2 + 19 * S): d.line((xx, Y + 1 * S, xx, Y + 7 * S), fill=(243, 220, 176, 240), width=lw + 1)
# room title above the print, tracked thin caps (Latin only, so tracking is allowed)
tracked(cx * S, (y0 - 34) * S, "FREEEARTH", font(13), iv, 0.32, "c")
# bottom: ‹ 1 / 11 › with hairlines, gallery link
by = (y0 + ph + 2 * m + 30) * S
f = font(15, thin=False)
d.text((cx * S - 110 * S, by - 4 * S), "‹", font=font(24, True), fill=iv)
d.text((cx * S + 98 * S, by - 4 * S), "›", font=font(24, True), fill=iv)
tracked(cx * S, by + 2 * S, "1 / 11", font(13), iv, 0.18, "c")
d.line((cx * S - 80 * S, by + 12 * S, cx * S - 40 * S, by + 12 * S), fill=hl, width=lw)
d.line((cx * S + 40 * S, by + 12 * S, cx * S + 80 * S, by + 12 * S), fill=hl, width=lw)
tw = tracked(W * S - 40 * S, H * S - 50 * S, "OPEN GALLERY ↗", font(11), iv, 0.26, "r")
d.line((W * S - 40 * S - tw, H * S - 30 * S, W * S - 40 * S, H * S - 30 * S), fill=IVORY + (110,), width=lw)
# honest label
d.text((40 * S, H * S - 46 * S), "MOCK-UP  ·  backplate: Cycles plate 1600x900 + layered bokeh composite (every layer 80-96 px discs, the 0.3 m focus state), tinted 12% toward the photo  ·  photo: Shiko, FreeEarth 2w2a1130, uncropped",
       font=font(10), fill=IVORY + (150,))
ui = ui.resize((W, H), Image.LANCZOS)
canvas = canvas.convert("RGBA"); canvas.alpha_composite(ui); canvas.convert("RGB").save(OUT, quality=95)
print("saved", OUT, "print", pw, "x", ph, "mount", m, "tint", tint)
