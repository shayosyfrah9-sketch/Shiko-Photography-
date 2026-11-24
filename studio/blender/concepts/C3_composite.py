# SHIKO WORLD 2.0 - Concept C risk test (C3): labels + the click MOCK-UP composite (PIL).
# Run: python3 C3_composite.py TMPDIR OUTDIR     (TMPDIR holds f1_spray.png, f2_hole.png(+_register.json), f2_edge.png(+_register.json), f3_portrait.png)
import sys, os, json
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
T, O = sys.argv[1:3]
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PHOTO = Image.open(os.path.join(ROOT, "media", "photos", "surf0001.jpg")).convert("RGB"); PW, PH = PHOTO.size
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(s, b=False): return ImageFont.truetype(FB if b else F, s)
IVORY = (241, 236, 224)

def tag(img, text, sub=None, pos=(14, 14)):
    d = ImageDraw.Draw(img, "RGBA"); f = font(17, True); fs = font(13)
    tw = d.textlength(text, font=f); sw = d.textlength(sub, font=fs) if sub else 0
    bw = int(max(tw, sw)) + 24; bh = 36 + (20 if sub else 0)
    d.rounded_rectangle((pos[0], pos[1], pos[0] + bw, pos[1] + bh), 8, fill=(12, 12, 12, 190))
    d.text((pos[0] + 12, pos[1] + 8), text, font=f, fill=(250, 246, 236, 255))
    if sub: d.text((pos[0] + 12, pos[1] + 34), sub, font=fs, fill=(225, 220, 210, 255))

# ---------------- deliverable 1
r1 = json.load(open(os.path.join(T, "f1_spray_register.json")))
A = Image.open(os.path.join(T, "f1_spray.png")).convert("RGB")
tag(A, "RENDERED", f"Blender Cycles CPU · {A.width}×{A.height} · {r1['spp']} spp + OIDN · {r1['n_drops']} glass drops (IOR 1.33) + mist volume · {r1['seconds']:.0f} s")
A.save(os.path.join(O, "C_rt_1_spray_RENDERED.png"))

# ---------------- deliverable 2: the click
reg = json.load(open(os.path.join(T, "f2_hole_register.json"))); ereg = json.load(open(os.path.join(T, "f2_edge_register.json")))
B = Image.open(os.path.join(T, "f2_hole.png")).convert("RGB"); E = Image.open(os.path.join(T, "f2_edge.png")).convert("RGB")
W, H = B.size; X0, Y0, TW, TH = reg["x0"], reg["y0"], reg["w"], reg["h"]; mm = ereg["mount_px"]
x0, y0 = int(round(X0)), int(round(Y0)); tw, th = int(round(TW)), int(round(TH))
M = B.copy()
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((x0 - mm + 7, y0 - mm + 9, x0 + tw + mm + 7, y0 + th + mm + 9), fill=(0, 0, 0, 95))
M = Image.alpha_composite(M.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(11))).convert("RGB")
ImageDraw.Draw(M).rectangle((x0 - mm, y0 - mm, x0 + tw + mm - 1, y0 + th + mm - 1), fill=IVORY)
M.paste(PHOTO.resize((tw, th), Image.LANCZOS), (x0, y0))
# rendered drops over the print edge: take the Cycles EDGE pass only inside each drop's disc (soft edge)
mk = Image.new("L", (W * 4, H * 4), 0); dm = ImageDraw.Draw(mk)
for e in ereg["edge_drops"]:
    r = e["r_px"] * 4 + 3; dm.ellipse((e["px"] * 4 - r, e["py"] * 4 - r, e["px"] * 4 + r, e["py"] * 4 + r), fill=255)
mk = mk.resize((W, H), Image.LANCZOS)
M = Image.composite(E, M, mk)
tag(M, "MOCK-UP · the click", "Rendered world (Cycles) + Shay's real photo surf0001.jpg pasted in PIL, uncropped 1500×1238, ivory mount + 32 rendered edge drops (Cycles)")
# bottom strip
SH = 360; C = Image.new("RGB", (W, H + SH), (14, 13, 12)); C.paste(M, (0, 0))
# panel L: the absence before the click
pad = 40; crop = B.crop((x0 - pad, y0 - pad, x0 + tw + pad, y0 + th + pad)); ch = SH - 60
cw = int(crop.width * ch / crop.height); cp = crop.resize((cw, ch), Image.LANCZOS); sc_ = ch / crop.height
d = ImageDraw.Draw(cp)
src = open(os.path.join(HERE, "C3_spray.py")).read(); i = src.index("_C = ["); j = src.index("def sil_mask"); ns = {}; exec(src[i:j], ns)
for poly in ns["SIL"]:
    pts = [((x * TW / PW + pad) * sc_, (y * TH / PH + pad) * sc_) for x, y in poly]; d.line(pts + [pts[0]], fill=(250, 246, 236), width=1)
C.paste(cp, (20, H + 40)); tag(C, "RENDERED (crop)", "before the click: the surfer-shaped absence in the 3D spray", (20, H + 4))
# panel R: viewer front-on, world dimmed
vw_, vh_ = 700, SH - 20; V = ImageEnhance.Brightness(B.filter(ImageFilter.GaussianBlur(9))).enhance(0.38).resize((int(W * (SH - 20) / H * 1.0 + 1), SH - 20))
V = B.crop((W // 2 - 350, 0, W // 2 + 350, 300)).filter(ImageFilter.GaussianBlur(7)); V = ImageEnhance.Brightness(V).enhance(0.36).resize((vw_, vh_ - 0))
ph_h = vh_ - 70; ph_w = int(ph_h * PW / PH); vm = 7
dv = ImageDraw.Draw(V); px_ = (vw_ - ph_w) // 2 + 20; py_ = 12
dv.rectangle((px_ - vm, py_ - vm, px_ + ph_w + vm, py_ + ph_h + vm), fill=IVORY); V.paste(PHOTO.resize((ph_w, ph_h), Image.LANCZOS), (px_, py_))
dv.text((px_ + ph_w // 2 - 22, py_ + ph_h + vm + 8), "1 / 7", font=font(15), fill=(240, 234, 222))
ox = W - vw_ - 20; C.paste(V, (ox, H + 20)); tag(C, "MOCK-UP · viewer", "same photo front-on, ivory mount, world dimmed (PIL)", (ox + 10, H + 28))
d = ImageDraw.Draw(C); d.text((20 + cw + 24, H + 60), "The photo is a real file at its true\naspect. Everything around it, and the\n32 drops at its border, is Cycles.\nThe absence is hand-traced, about\n±3 px at 1600×900.", font=font(14), fill=(225, 220, 210))
C.convert("RGB").save(os.path.join(O, "C_rt_2_click_MOCKUP.jpg"), quality=93)
print("composites done")
