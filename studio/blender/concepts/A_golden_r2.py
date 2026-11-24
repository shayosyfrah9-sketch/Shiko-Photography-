# SHIKO WORLD 2.0 · Concept A SUNLINE · ROUND 2 key frame 2 "18:30 Portraits & Branding" (Rendered)
# Round-1 critique fixes: horizon on the lower third (y ~ 600 of 900); kurkar cliff with horizontal strata (benches),
# a wave-cut notch at the waterline, angular scree and a 0.3-0.5 m dark wet band; a sand beach in front of the cliff;
# 3 stone pines with different crowns; a 0.2-0.5 m geometric swell + wind chop so the low sun makes a vertical glitter
# path; backlit wind ripples in the foreground; a portrait set (reflector, light stand, apple box, tripod) on the
# right third at ~8 m; warm sun against a cool sea and sky (no grade: AgX only).
# Camera: 50 mm, 0.6 m above the sand (crouched photographer), pitch +3.9 deg.
# Run: bpyenv/bin/python A_golden_r2.py -- OUT.png W H SPP
import bpy, bmesh, sys, math, os, random
from mathutils import Vector, Matrix, noise
a = sys.argv[sys.argv.index("--") + 1:]
OUT = a[0]; W = int(a[1]); H = int(a[2]); SPP = int(a[3])
PH = os.environ.get("PH", "/tmp/claude-0/-home-user/2c38ec15-b058-5d59-86c9-28307ce7ab10/scratchpad/A/ph/")
random.seed(5)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---- fast primitives (data API, shared meshes: bpy.ops gets very slow with thousands of objects)
_PRIM = {}
def _prim(kind, verts=6):
    key = (kind, verts)
    if key in _PRIM: return _PRIM[key]
    bm = bmesh.new()
    if kind == "cube": bmesh.ops.create_cube(bm, size=1.0)
    elif kind == "cyl": bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=1.0, radius2=1.0, depth=1.0)
    elif kind == "sphere": bmesh.ops.create_uvsphere(bm, u_segments=verts, v_segments=max(4, verts // 2), radius=1.0)
    me = bpy.data.meshes.new(kind); bm.to_mesh(me); bm.free()
    if kind != "cube":
        for p in me.polygons: p.use_smooth = True
    _PRIM[key] = me; return me
def prim(kind, loc, scale, mat, rot=(0, 0, 0), verts=6):
    o = bpy.data.objects.new(kind, _prim(kind, verts)); o.location = loc; o.scale = scale; o.rotation_euler = rot
    sc.collection.objects.link(o)
    if mat is not None:
        # per-object material through an object-linked slot so shared meshes can carry different materials
        if len(o.data.materials) == 0: o.data.materials.append(None)
        o.material_slots[0].link = "OBJECT"; o.material_slots[0].material = mat
    return o
sc = bpy.context.scene; sc.render.engine = "CYCLES"; cy = sc.cycles
cy.device = "CPU"; cy.samples = SPP; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.015
cy.use_denoising = True
try: cy.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
cy.max_bounces = 6; cy.diffuse_bounces = 3; cy.glossy_bounces = 3; cy.transmission_bounces = 4; cy.volume_bounces = 1
cy.sample_clamp_indirect = 6; cy.blur_glossy = 1.0
sc.render.resolution_x = W; sc.render.resolution_y = H; sc.render.filepath = OUT
sc.render.image_settings.file_format = "PNG"
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = os.environ.get("LOOK", "AgX - Medium High Contrast")
except Exception: pass
sc.view_settings.exposure = float(os.environ.get("EXPO", "-0.35"))

def sstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t)

# ---------------------------------------------------------------- layout
# Camera frame: X = right, Y = forward (towards the sunset sea), Z = up. The camera stands on the sand of a bay.
# Left: a kurkar headland pushes out into the sea, stone pines on top, the sun 3 deg high behind them.
# Right: the bay's shore curves away to the north; 3-4 km up it the stadium crown is already on.
K_BAY = float(os.environ.get("KBAY", "0.008"))
def shore_main(X):          # waterline Y at lateral X (land is Y < shore)
    return 40.0 + K_BAY * max(0.0, X) ** 2 + 0.0006 * min(0.0, X) ** 2 + 4.0 * noise.noise(Vector((X * 0.02, 0.5, 0)))
# the headland is an arm that leaves the land far to the left and curls out to a tip just left of the frame centre
HEAD_TIP = Vector((float(os.environ.get("TIPX", "-24")), float(os.environ.get("TIPY", "172"))))
_B0, _B1 = Vector((-480.0, 20.0)), Vector((-230.0, 192.0))
HEAD_PTS = [(_B0 * (1 - t) ** 2 + _B1 * 2 * t * (1 - t) + HEAD_TIP * t * t) for t in [i / 60 for i in range(61)]]
def head_axis_x(Y):   # x of the arm's crest line nearest to this Y (only used to place pines)
    return min(HEAD_PTS, key=lambda p: abs(p.y - Y)).x
def tongue(X, Y):
    if X > 90 or Y < -20 or Y > 360: return -999.0
    q = Vector((X, Y)); best = 1e9; bt = 0.0
    for i, p in enumerate(HEAD_PTS):
        dd = (q - p).length_squared
        if dd < best: best, bt = dd, i / 60
    w = 20.0 + 24.0 * (1 - bt) + 7.0 * noise.noise(Vector((X * 0.02, Y * 0.02, 1.7))) + 5.0 * noise.noise(Vector((X * 0.07, Y * 0.07, 3.1))) + 2.0 * noise.noise(Vector((X * 0.2, Y * 0.2, 6.3))) + 2.0 * noise.ridged_multi_fractal(Vector((X * 0.25, Y * 0.25, 5.1)), 1.0, 2.0, 3, 0.0, 2.0)
    return w - math.sqrt(best)
BEACH = float(os.environ.get("BEACH", "16"))   # width of the sand beach at the foot of the cliff
def landval(X, Y): return max(shore_main(X) - Y, tongue(X, Y) + BEACH)

def land_z(X, Y):
    F = shore_main(X) - Y; T = tongue(X, Y); L = max(F, T + BEACH)
    if L < 0: return -min(8.0, 0.03 * -L) + 0.4 * math.exp(-((L + 45) / 15) ** 2)
    z = 0.03 * min(F, 60.0) if F > 0 else 0.0
    if T + BEACH > 0: z = max(z, 0.1 * min(T + BEACH, 20.0) + 0.15 * noise.noise(Vector((X * 0.05, Y * 0.05, 7))) * sstep(2, 8, T + BEACH))
    if F > 60: z += 5.0 * sstep(60, 160, F) * (0.6 + 0.4 * noise.fractal(Vector((X * 0.01, Y * 0.01, 1)), 1.0, 2.0, 3))
    if F > 120: z += 70.0 * sstep(600, 2500, F) * (0.7 + 0.3 * noise.fractal(Vector((X * 0.002, Y * 0.002, 5)), 1.0, 2.0, 4))
    if T > -2:
        st = sstep(0.0, 12.0, T)
        zt = st * (14.0 + 2.5 * noise.fractal(Vector((X * 0.03, Y * 0.03, 4)), 1.0, 2.0, 3) + 2.5 * sstep(6, 26, T) * (0.6 + 0.8 * noise.noise(Vector((X * 0.05, Y * 0.05, 9)))))
        zt += 1.0 * noise.ridged_multi_fractal(Vector((X * 0.12, Y * 0.12, 2)), 1.0, 2.0, 3, 0.0, 2.0) * st * (1 - st) * 4
        # horizontal strata: harder layers stand out as benches, softer ones are cut back (terraced profile)
        Hl = 1.7; q = zt / Hl; fq = q - math.floor(q); zt = (math.floor(q) + sstep(0.25, 0.75, fq) * 0.85 + fq * 0.15) * Hl if zt > 1.2 else zt
        # wave-cut notch: the face is undercut ~1-2 m above the beach (heightfield: reads as a dark recessed band)
        zt -= 0.9 * math.exp(-((zt - 2.6) / 0.6) ** 2) * (1 - sstep(3, 8, T))
        z = max(z, zt)
    return z

def make_polar(name, zf, ang=(-25.0, 22.0), da=0.035, r0=1.5, r1=9000.0, gr=0.016, keep=None):
    angs = []; a_ = ang[0]
    while a_ <= ang[1]: angs.append(math.radians(a_)); a_ += da
    rs = []; r = r0
    while r < r1:
        rs.append(r); r = r + (0.4 if 140 < r < 260 else 0.8) if (120 < r < 330 and gr < 0.018) else r * (1 + gr)
    verts = []; dl = []
    for r in rs:
        for t in angs:
            X = r * math.sin(t); Y = r * math.cos(t)
            verts.append((X, Y, zf(X, Y))); dl.append(landval(X, Y))
    na = len(angs); faces = []
    for j in range(len(rs) - 1):
        for i in range(na - 1):
            k = j * na + i; q = (k, k + 1, k + na + 1, k + na)
            if keep and not keep([dl[v] for v in q]): continue
            faces.append(q)
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update(); me.shade_smooth()
    at = me.attributes.new("d", "FLOAT", "POINT"); at.data.foreach_set("value", dl)
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); return o

def img(n, nc=False):
    i = bpy.data.images.load(PH + n, check_existing=True)
    if nc: i.colorspace_settings.name = "Non-Color"
    return i

class NB:
    def __init__(s, name):
        s.m = bpy.data.materials.new(name); s.m.use_nodes = True; s.nt = s.m.node_tree; s.N = s.nt.nodes; s.L = s.nt.links
        s.out = s.N["Material Output"]; s.bsdf = s.N.get("Principled BSDF")
    def n(s, t, **kw):
        x = s.N.new(t)
        for k, v in kw.items(): setattr(x, k, v)
        return x
    def l(s, a, b): s.L.new(a, b)
    def math(s, op, a, b=None, clamp=False):
        m = s.n("ShaderNodeMath", operation=op, use_clamp=clamp)
        for idx, v in ((0, a), (1, b)):
            if v is None: continue
            if isinstance(v, (int, float)): m.inputs[idx].default_value = v
            else: s.l(v, m.inputs[idx])
        return m.outputs[0]
    def mix(s, fac, c1, c2, blend="MIX"):
        m = s.n("ShaderNodeMix", data_type="RGBA", blend_type=blend)
        for sock, v in ((0, fac), (6, c1), (7, c2)):
            if isinstance(v, (int, float)): m.inputs[sock].default_value = v
            elif isinstance(v, tuple): m.inputs[sock].default_value = v + (1,) if len(v) == 3 else v
            else: s.l(v, m.inputs[sock])
        return m.outputs[2]
    def attr(s, name): return s.n("ShaderNodeAttribute", attribute_name=name).outputs["Fac"]
    def ss(s, x, e0, e1):
        m = s.n("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP"); m.inputs[1].default_value = e0; m.inputs[2].default_value = e1
        s.l(x, m.inputs[0]); return m.outputs[0]
    def coord(s, scale):
        tc = s.n("ShaderNodeTexCoord"); mp = s.n("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale,) * 3
        s.l(tc.outputs["Object"], mp.inputs["Vector"]); return mp.outputs[0]
    def tex(s, name, scale, nc=False):
        t = s.n("ShaderNodeTexImage"); t.image = img(name, nc); t.projection = "BOX"; t.projection_blend = 0.25
        s.l(s.coord(scale), t.inputs["Vector"]); return t
    def noise(s, scale, detail=4, rough=0.55, vec=None):
        t = s.n("ShaderNodeTexNoise"); t.inputs["Scale"].default_value = scale; t.inputs["Detail"].default_value = detail; t.inputs["Roughness"].default_value = rough
        if vec is None: vec = s.n("ShaderNodeTexCoord").outputs["Object"]
        s.l(vec, t.inputs["Vector"]); return t

def flat(name, col, rough=0.6, emit=None, estr=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = col + (1,); b.inputs["Roughness"].default_value = rough
    if emit: b.inputs["Emission Color"].default_value = emit + (1,); b.inputs["Emission Strength"].default_value = estr
    return m

# ---------------------------------------------------------------- terrain material: wind-rippled sand, damp sand, kurkar
def terrain_mat():
    B = NB("terrain"); b = B.bsdf; d = B.attr("d")
    sD = B.tex("coast_sand_01_diff_2k.jpg", 0.35); sR = B.tex("coast_sand_01_rough_2k.jpg", 0.35, True)
    wD = B.tex("damp_beach_sand_diff_2k.jpg", 0.3)
    rD = B.tex("sandstone_cracks_diff_2k.jpg", 0.3); rN = B.tex("sandstone_cracks_nor_gl_2k.jpg", 0.3, True)
    gD = B.tex("sparse_grass_diff_2k.jpg", 0.1)
    sand = B.mix(1.0, sD.outputs[0], (1.15, 1.0, 0.82), "MULTIPLY")
    wet = B.mix(1.0, wD.outputs[0], (0.75, 0.70, 0.64), "MULTIPLY")
    wetf = B.math("SUBTRACT", 1.0, B.ss(d, 3.0, 14.0))
    col = B.mix(wetf, sand, wet)
    veg = B.math("MULTIPLY", B.ss(B.noise(0.05, 5).outputs[0], 0.45, 0.6), B.ss(d, 50.0, 70.0))
    col = B.mix(veg, col, B.mix(1.0, gD.outputs[0], (0.5, 0.5, 0.35), "MULTIPLY"))
    geo = B.n("ShaderNodeNewGeometry"); sep = B.n("ShaderNodeSeparateXYZ"); B.l(geo.outputs["Normal"], sep.inputs[0])
    steep = B.math("SUBTRACT", 1.0, B.ss(sep.outputs["Z"], 0.5, 0.78))
    rock = B.mix(1.0, rD.outputs[0], (0.55, 0.38, 0.25), "MULTIPLY")
    # kurkar strata: horizontal bands of harder / softer sandstone, and dark wet base
    sepz = B.n("ShaderNodeSeparateXYZ"); B.l(B.n("ShaderNodeTexCoord").outputs["Object"], sepz.inputs[0])
    strata = B.n("ShaderNodeTexWave"); strata.bands_direction = "Z"; strata.inputs["Scale"].default_value = 0.13; strata.inputs["Distortion"].default_value = 0.5; strata.inputs["Detail"].default_value = 2.0; strata.inputs["Detail Scale"].default_value = 1.0
    rock = B.mix(B.math("MULTIPLY", B.ss(strata.outputs["Fac"], 0.4, 0.6), 0.6), rock, (0.26, 0.18, 0.12))
    bed = B.n("ShaderNodeTexWave"); bed.bands_direction = "Z"; bed.inputs["Scale"].default_value = 0.185; bed.inputs["Distortion"].default_value = 0.3   # thin dark bedding planes
    rock = B.mix(B.math("MULTIPLY", B.ss(bed.outputs["Fac"], 0.93, 0.99), 0.85), rock, (0.05, 0.04, 0.03))
    wetb = B.math("SUBTRACT", 1.0, B.ss(sepz.outputs["Z"], 1.95, 2.1))   # wet dark band ~0.4 m above the cliff foot (beach berm top ~1.6 m)
    rock = B.mix(wetb, rock, (0.075, 0.06, 0.05))
    col = B.mix(steep, col, rock)
    B.l(col, b.inputs["Base Color"])
    B.l(B.mix(B.math("MAXIMUM", wetf, B.math("MULTIPLY", wetb, steep)), sR.outputs[0], (0.2, 0.2, 0.2)), b.inputs["Roughness"])
    # wind ripples: anisotropic wave bands warped by noise, only on dry sand
    tc = B.n("ShaderNodeTexCoord")
    wv = B.n("ShaderNodeTexWave"); wv.wave_profile = "SIN"; wv.inputs["Scale"].default_value = float(os.environ.get("RIPS", "1.8")); wv.inputs["Distortion"].default_value = 5.0
    wv.inputs["Detail"].default_value = 3.0; wv.inputs["Detail Scale"].default_value = 0.6
    mp = B.n("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = (0, 0, float(os.environ.get("RIPR", "0.8"))); mp.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    B.l(tc.outputs["Object"], mp.inputs["Vector"]); B.l(mp.outputs[0], wv.inputs["Vector"])
    rip = B.math("MULTIPLY", B.math("POWER", wv.outputs["Fac"], 1.8), B.math("SUBTRACT", 1.0, wetf))   # sine bands sharpened into crests (a saw profile only tilts the bump uniformly)
    rip = B.math("MULTIPLY", rip, B.math("SUBTRACT", 1.0, steep))
    h = B.math("ADD", rip, B.math("MULTIPLY", B.noise(1.5, 6).outputs[0], 0.25))
    bump = B.n("ShaderNodeBump"); bump.inputs["Strength"].default_value = 1.0; bump.inputs["Distance"].default_value = float(os.environ.get("RIPD", "0.06"))
    B.l(h, bump.inputs["Height"])
    nm = B.n("ShaderNodeNormalMap"); B.l(rN.outputs[0], nm.inputs["Color"])
    # cliff relief: pitted, fluted kurkar (multi-scale noise + the strata bands) on top of the scanned normal map
    rb2 = B.n("ShaderNodeBump"); rb2.inputs["Strength"].default_value = 0.85; rb2.inputs["Distance"].default_value = 0.8
    rel = B.math("ADD", B.noise(0.18, 8, 0.7).outputs[0], B.math("MULTIPLY", strata.outputs["Fac"], 0.6))
    flute = B.n("ShaderNodeMapping"); flute.inputs["Scale"].default_value = (0.25, 0.25, 1.6); B.l(B.n("ShaderNodeTexCoord").outputs["Object"], flute.inputs["Vector"])
    rel = B.math("ADD", rel, B.math("MULTIPLY", B.noise(1.0, 4, 0.6, flute.outputs[0]).outputs[0], 0.8))
    B.l(rel, rb2.inputs["Height"]); B.l(nm.outputs[0], rb2.inputs["Normal"])
    nmix = B.n("ShaderNodeMix", data_type="VECTOR"); B.l(steep, nmix.inputs[0]); B.l(bump.outputs[0], nmix.inputs[4]); B.l(rb2.outputs[0], nmix.inputs[5])
    B.l(nmix.outputs[1], b.inputs["Normal"])
    if os.environ.get("DEBUGRIP") == "1": B.l(h, b.inputs["Base Color"])
    if os.environ.get("DEBUGRIP") == "2": B.l(nmix.outputs[1], b.inputs["Base Color"])
    if os.environ.get("DEBUGRIP") == "3": B.l(bump.outputs[0], b.inputs["Base Color"])
    return B.m

def sea_mat():
    B = NB("sea"); b = B.bsdf; d = B.attr("d")
    deep = (0.01, 0.035, 0.05); shal = (0.05, 0.16, 0.15)
    col = B.mix(B.ss(d, -120.0, -10.0), deep, shal)
    nz = B.noise(0.03, 5, 0.6); nz2 = B.noise(0.25, 5, 0.65)
    ph = B.math("DIVIDE", B.math("ADD", d, B.math("MULTIPLY", nz.outputs[0], 30.0)), 22.0)
    band = B.ss(B.math("SINE", B.math("MULTIPLY", ph, 6.2832)), 0.86, 0.99)
    zone = B.math("MULTIPLY", B.ss(d, -90.0, -25.0), B.math("SUBTRACT", 1.0, B.ss(d, -6.0, -1.0)))
    foam = B.math("MULTIPLY", B.math("MULTIPLY", band, zone), B.ss(nz2.outputs[0], 0.35, 0.6))
    sw = B.math("MULTIPLY", B.ss(d, -9.0, -1.0), B.ss(nz2.outputs[0], 0.3, 0.55))
    foam = B.math("MAXIMUM", foam, sw)
    foam = B.math("MULTIPLY", foam, B.ss(B.noise(1.2, 6, 0.7).outputs[0], 0.35, 0.6))
    col = B.mix(foam, col, (0.8, 0.8, 0.78))
    B.l(col, b.inputs["Base Color"])
    cam_dist = B.n("ShaderNodeCameraData").outputs["View Distance"]
    B.l(B.math("ADD", B.math("ADD", 0.015, B.math("MULTIPLY", B.ss(cam_dist, 300.0, 4000.0), float(os.environ.get("WROUGH", "0.06")))), B.math("MULTIPLY", foam, 0.8)), b.inputs["Roughness"])
    b.inputs["IOR"].default_value = 1.33
    sw2 = B.math("SINE", B.math("MULTIPLY", B.math("DIVIDE", B.math("ADD", d, B.math("MULTIPLY", nz.outputs[0], 40.0)), 14.0), 6.2832))
    vec = B.n("ShaderNodeTexCoord").outputs["Object"]
    mp = B.n("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.5, 1.4, 1.0); B.l(vec, mp.inputs["Vector"])
    chop = B.noise(0.9, 6, 0.6, mp.outputs[0]); chop2 = B.noise(5.0, 4, 0.6, mp.outputs[0])
    h = B.math("ADD", B.math("MULTIPLY", sw2, 0.1), B.math("ADD", chop.outputs[0], B.math("MULTIPLY", chop2.outputs[0], 0.35)))
    bump = B.n("ShaderNodeBump"); bump.inputs["Strength"].default_value = float(os.environ.get("WBUMP", "0.5")); bump.inputs["Distance"].default_value = float(os.environ.get("WBD", "0.25"))
    B.l(h, bump.inputs["Height"]); B.l(bump.outputs[0], b.inputs["Normal"])
    return B.m

ter = make_polar("terrain", land_z, keep=lambda ds: max(ds) > -60); ter.data.materials.append(terrain_mat())
SEA = sea_mat()
SWA = float(os.environ.get("SWELL", "0.35"))   # swell height (crest-trough, m)
def sea_z(X, Y):
    r = math.hypot(X, Y); fade = 1.0 - sstep(500.0, 1400.0, r)
    z = 0.5 * SWA * (0.65 * math.sin(Y * 2 * math.pi / 34.0 + X * 0.03 + 4.0 * noise.noise(Vector((X * 0.004, Y * 0.004, 2))))
                     + 0.35 * math.sin((Y * 0.9 + X * 0.44) * 2 * math.pi / 19.0))
    return z * fade + 0.06 * noise.fractal(Vector((X * 0.15, Y * 0.15, 3)), 1.0, 2.0, 3) * (1 - sstep(100, 400, r))
sea = make_polar("sea", sea_z, da=0.03, gr=0.012, r0=3.0, keep=lambda ds: min(ds) < 3); sea.data.materials.append(SEA)
def ground(x, y):
    return Vector((x, y, land_z(x, y)))

# ---------------------------------------------------------------- stone pines (Pinus pinea) with tufted crowns so the sun can break through
NEEDLE = NB("needles"); nb = NEEDLE.bsdf
oi = NEEDLE.n("ShaderNodeObjectInfo")
nc = NEEDLE.mix(NEEDLE.ss(NEEDLE.noise(0.8, 3).outputs[0], 0.3, 0.7), (0.035, 0.055, 0.02), (0.07, 0.085, 0.03))
NEEDLE.l(nc, nb.inputs["Base Color"]); nb.inputs["Roughness"].default_value = 0.7
tr = NEEDLE.n("ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = (0.25, 0.32, 0.06, 1)
mxs = NEEDLE.n("ShaderNodeMixShader"); mxs.inputs[0].default_value = 0.35
NEEDLE.l(nb.outputs[0], mxs.inputs[1]); NEEDLE.l(tr.outputs[0], mxs.inputs[2]); NEEDLE.l(mxs.outputs[0], NEEDLE.out.inputs["Surface"])
bp = NEEDLE.n("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.8; NEEDLE.l(NEEDLE.noise(14.0, 3).outputs[0], bp.inputs["Height"]); NEEDLE.l(bp.outputs[0], nb.inputs["Normal"])
# leaf alpha: a spiky noise mask makes each tuft ragged (needle clusters), not a ball
amask = NEEDLE.ss(NEEDLE.noise(5.0, 6, 0.75).outputs[0], 0.42, 0.5)
tsp = NEEDLE.n("ShaderNodeBsdfTransparent"); mx2 = NEEDLE.n("ShaderNodeMixShader")
NEEDLE.l(amask, mx2.inputs[0]); NEEDLE.l(tsp.outputs[0], mx2.inputs[1]); NEEDLE.l(mxs.outputs[0], mx2.inputs[2]); NEEDLE.l(mx2.outputs[0], NEEDLE.out.inputs["Surface"])
BARK = NB("bark"); bk = BARK.bsdf
bD = BARK.tex("pine_bark_diff_2k.jpg", 0.6); BARK.l(BARK.mix(1.0, bD.outputs[0], (0.85, 0.62, 0.48), "MULTIPLY"), bk.inputs["Base Color"])
try:
    bk.inputs["Sheen Weight"].default_value = 0.6; bk.inputs["Sheen Tint"].default_value = (1.0, 0.75, 0.5, 1); bk.inputs["Sheen Roughness"].default_value = 0.35
except Exception: pass
bN = BARK.tex("pine_bark_nor_gl_2k.jpg", 0.6, True); nmb = BARK.n("ShaderNodeNormalMap"); BARK.l(bN.outputs[0], nmb.inputs["Color"]); BARK.l(nmb.outputs[0], bk.inputs["Normal"])

tuft_me = bpy.data.meshes.new("tuft"); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
for v in bm.verts:
    v.co.z *= 0.45; v.co *= 1.0 + 0.35 * noise.noise(v.co * 2.0)
bm.to_mesh(tuft_me); bm.free(); tuft_me.shade_smooth(); tuft_me.materials.append(NEEDLE.m)

def branch(bm, p0, p1, r0, r1, seg=6):
    dv = p1 - p0; L = dv.length
    mat = Matrix.Translation((p0 + p1) / 2) @ dv.to_track_quat("Z", "Y").to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=seg, radius1=r0, radius2=r1, depth=L, matrix=mat)

def stone_pine(base, h=14.0, r=7.0, seed=0, style="umbrella", lean_dir=None):
    """style: 'umbrella' = one wide flat dome on a long bare leaning trunk;
       'lobed' = forked trunk, crown broken into 3-4 separate cushions with sky between;
       'young' = shorter trunk, rounder, deeper crown that starts low."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    if lean_dir is None: lean_dir = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)).normalized()
    lean = lean_dir * {"umbrella": 0.22, "lobed": 0.1, "young": 0.05}[style] * h
    tf_ = {"umbrella": 0.66, "lobed": 0.5, "young": 0.4}[style]
    top = base + Vector((0, 0, h * tf_)) + lean
    mid = base + Vector((0, 0, h * tf_ * 0.5)) + lean * 0.35 + Vector((rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), 0))
    branch(bm, base + Vector((0, 0, -0.5)), mid, 0.4 * h / 14, 0.32 * h / 14, 10); branch(bm, mid, top, 0.32 * h / 14, 0.24 * h / 14, 10)
    forks = [top]
    if style == "lobed":
        forks = []
        for k in range(2):
            ang = rnd.uniform(0, 6.3) + k * math.pi
            f = top + Vector((math.cos(ang) * r * 0.35, math.sin(ang) * r * 0.35, h * 0.14)); branch(bm, top, f, 0.2 * h / 14, 0.15 * h / 14, 8); forks.append(f)
    tips = []
    for f in forks:
        for k in range(rnd.randint(4, 6) if style != "lobed" else 3):
            ang = k * 2 * math.pi / 5 + rnd.uniform(-0.5, 0.5)
            reach = r * (rnd.uniform(0.45, 0.85) if style != "lobed" else rnd.uniform(0.35, 0.6))
            tip = f + Vector((math.cos(ang) * reach, math.sin(ang) * reach, h * rnd.uniform(0.12, 0.26)))
            branch(bm, f, tip, 0.17 * h / 14, 0.05, 6); tips.append(tip)
    me = bpy.data.meshes.new("pinewood"); bm.to_mesh(me); bm.free(); me.materials.append(BARK.m)
    o = bpy.data.objects.new("pinewood", me); sc.collection.objects.link(o)
    def tuft(p, s):
        tf = bpy.data.objects.new("tuft", tuft_me); tf.location = p; tf.scale = (s, s, s * rnd.uniform(0.8, 1.2)); tf.rotation_euler = (rnd.uniform(-0.3, 0.3), rnd.uniform(-0.3, 0.3), rnd.random() * 6.3)
        sc.collection.objects.link(tf)
    if style == "lobed":   # separate cushions over each branch tip, gaps of sky between them
        for tp in tips:
            rl = r * rnd.uniform(0.32, 0.45)
            for i in range(int(70 * (rl / 3.0) ** 2)):
                u = rnd.random(); t = rnd.random() * 2 * math.pi; rr = rl * math.sqrt(u)
                dome = 1 - (rr / rl) ** 2
                tuft(tp + Vector((rr * math.cos(t), rr * math.sin(t), h * 0.07 * dome + rnd.uniform(-0.3, 0.6))), rnd.uniform(0.6, 1.15))
        return
    cz = top.z + h * (0.27 if style == "umbrella" else 0.2)
    depth = 0.14 if style == "umbrella" else 0.3
    n = int(260 * (r / 7.0) ** 2)
    for i in range(n):
        u = rnd.random(); t = rnd.random() * 2 * math.pi
        rr = r * math.sqrt(u) * rnd.uniform(0.85, 1.08)
        dome = (1 - (rr / (r * 1.08)) ** (2.2 if style == "umbrella" else 1.4))
        p = Vector((top.x + rr * math.cos(t), top.y + rr * math.sin(t), cz + h * depth * dome + rnd.uniform(-0.25, 0.55) * h * 0.12 - h * 0.06 * (1 - dome)))
        tuft(p, rnd.uniform(0.7, 1.35) * (1.0 + 0.3 * dome))

# ---------------------------------------------------------------- camera + sun
CAM = Vector((0.0, 0.0, land_z(0.0, 0.0) + float(os.environ.get("CAMH", "0.6"))))
SUN_EL = float(os.environ.get("SUNEL", "3.4"))
YAW = float(os.environ.get("YAW", "-2.0"))          # camera yaw to the right (deg)
SUN_OFF = float(os.environ.get("SUNOFF", "-2.5"))  # sun bearing (deg, negative = left)
PITCH = float(os.environ.get("PITCH", "3.9"))
def dvec(el, bearing):   # bearing from +Y towards +X
    e, b = math.radians(el), math.radians(bearing); return Vector((math.cos(e) * math.sin(b), math.cos(e) * math.cos(b), math.sin(e)))
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam.location = CAM; cam.rotation_euler = dvec(PITCH, YAW).to_track_quat("-Z", "Y").to_euler()
cam_d.lens = float(os.environ.get("LENS", "50")); cam_d.clip_start = 0.5; cam_d.clip_end = 30000
cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = float(os.environ.get("FSTOP", "8.0")); cam_d.dof.aperture_blades = 7
def ray_point(bearing, dist): return CAM + dvec(0, bearing) * dist
SUN_D = dvec(SUN_EL, SUN_OFF)
# stone pines along the headland; the biggest one sits on the sun's bearing so the sun breaks through its crown
rp = random.Random(3)
def crest_point(t, side=0.0):
    p_ = HEAD_PTS[int(t * 60)]; return Vector((p_.x + side, p_.y))
HERO = [(0.995, -3.0, 15.5, 8.0, "umbrella", Vector((0.8, 0.2, 0))),   # outermost: long leaning trunk, flat umbrella (sun just to its right)
        (0.95, 3.0, 12.5, 6.5, "lobed", None),                           # forked trunk, broken crown
        (0.905, -1.0, 9.0, 4.8, "young", None)]                           # young pine, rounder and lower
for i, (t, side, h, r, sty, ld) in enumerate(HERO):
    q = crest_point(t, side); g = ground(q.x, q.y)
    for _ in range(12):   # keep the trunk on the cliff top, not on the face
        if g.z > 10: break
        q = q + (Vector((HEAD_PTS[int(t * 60) - 3].x, HEAD_PTS[int(t * 60) - 3].y)) - q).normalized() * 1.5; g = ground(q.x, q.y)
    stone_pine(g, h, r, 40 + i, sty, ld)
for k in range(9):   # a few more, further back along the arm (smaller, partly hidden)
    t = rp.uniform(0.45, 0.75); q = crest_point(t, rp.uniform(-8, 8)); g = ground(q.x, q.y)
    if g.z < 10: continue
    stone_pine(g, rp.uniform(9, 14), rp.uniform(4.5, 7), 60 + k, rp.choice(("umbrella", "lobed", "young")))
for k in range(90):
    t = rp.uniform(0.5, 1.0); p_ = HEAD_PTS[int(t * 60)]; X = p_.x + rp.uniform(-14, 14); Y = p_.y + rp.uniform(-14, 8)
    g = ground(X, Y)
    if g.z < 12: continue
    tf = bpy.data.objects.new("bush", tuft_me); tf.location = g + Vector((0, 0, 0.2)); sc_ = rp.uniform(0.6, 1.6); tf.scale = (sc_, sc_, sc_ * 0.8); sc.collection.objects.link(tf)
# pines thinning away along the far shore of the bay (small silhouettes)
for k in range(40):
    X = rp.uniform(150, 1100); Y = shore_main(X) - rp.uniform(60, 220)
    if Y < 300: continue
    g = ground(X, Y); stone_pine(g, rp.uniform(10, 15), rp.uniform(5, 7.5), 100 + k)

# portrait set: a linen backdrop on a stand, waiting for the next session (backlit, glows)
LINEN = NB("linen"); lb = LINEN.bsdf; lb.inputs["Base Color"].default_value = (0.78, 0.74, 0.66, 1); lb.inputs["Roughness"].default_value = 0.9
lt = LINEN.n("ShaderNodeBsdfTranslucent"); lt.inputs["Color"].default_value = (0.95, 0.85, 0.7, 1)
lm = LINEN.n("ShaderNodeMixShader"); lm.inputs[0].default_value = 0.45; LINEN.l(lb.outputs[0], lm.inputs[1]); LINEN.l(lt.outputs[0], lm.inputs[2]); LINEN.l(lm.outputs[0], LINEN.out.inputs["Surface"])
ALU = flat("stand", (0.25, 0.24, 0.23), 0.35)
SET = ray_point(float(os.environ.get("SETB", "4.6")), float(os.environ.get("SETD", "9.5"))); SET = ground(SET.x, SET.y)
def backdrop(c, rot):
    w, hgt = 2.2, 2.0
    bm = bmesh.new(); n = 16; vs = []
    for j in range(n + 1):
        for k in range(n + 1):
            u = j / n; v = k / n
            x = (u - 0.5) * w; z = 0.35 + v * hgt; yy = 0.08 * math.sin(u * 9 + v * 3) * (1 - v) + 0.35 * (1 - v) ** 3 * (u - 0.5) * 0
            if v < 0.15: yy += (0.15 - v) * 3.0   # the cloth sweeps onto the sand
            vs.append(bm.verts.new((x, yy, z if v >= 0.15 else 0.35 * v / 0.15 + 0.02)))
    for j in range(n):
        for k in range(n):
            a_ = j * (n + 1) + k; bm.faces.new((vs[a_], vs[a_ + 1], vs[a_ + n + 2], vs[a_ + n + 1]))
    me = bpy.data.meshes.new("linen"); bm.to_mesh(me); bm.free(); me.shade_smooth(); me.materials.append(LINEN.m)
    o = bpy.data.objects.new("linen", me); o.location = c; o.rotation_euler.z = rot; sc.collection.objects.link(o)
    o.modifiers.new("s", "SOLIDIFY").thickness = 0.01
    for sx in (-1, 1):
        p = Vector((sx * (w / 2 + 0.05), 0, 0)); p.rotate(o.rotation_euler)
        prim("cyl", c + p + Vector((0, 0, 1.45)), (0.018, 0.018, 2.9), ALU, verts=8)
    p0 = Vector((-(w / 2 + 0.05), 0, 2.85)); p0.rotate(o.rotation_euler)
    prim("cyl", c + Vector((0, 0, 2.85)), (0.015, 0.015, w + 0.1), ALU, (0, math.radians(90), rot), verts=8)
if os.environ.get("BACKDROP"): backdrop(SET, math.radians(-25))
# the photographer's kit, waiting for the 18:30 session: an apple box where the sitter will be, a gold reflector on a
# stand catching the sun, a light stand with a small softbox, a tripod; a canvas bag on the sand
WOOD = flat("wood", (0.42, 0.30, 0.19), 0.65)
BLACK = flat("blackkit", (0.035, 0.035, 0.035), 0.45)
GOLD = bpy.data.materials.new("goldrefl"); GOLD.use_nodes = True; _gb = GOLD.node_tree.nodes["Principled BSDF"]
_gb.inputs["Base Color"].default_value = (0.8, 0.6, 0.3, 1); _gb.inputs["Metallic"].default_value = 0.9; _gb.inputs["Roughness"].default_value = 0.3
CANVAS = flat("canvas", (0.36, 0.33, 0.26), 0.9)
def leg(p0, p1, r, mat):
    dv = p1 - p0; o = prim("cyl", (p0 + p1) / 2, (r, r, dv.length), mat, verts=8); o.rotation_euler = dv.to_track_quat("Z", "Y").to_euler(); return o
def tripod_stand(c, hgt, spread=0.45, mat=None, rot=0.0):
    mat = mat or ALU; hub = c + Vector((0, 0, 0.75))
    for k in range(3):
        a = rot + k * 2.094; leg(hub, ground(c.x + spread * math.cos(a), c.y + spread * math.sin(a)), 0.012, mat)
    leg(hub, c + Vector((0, 0, hgt)), 0.011, mat); return c + Vector((0, 0, hgt))
fwd = (SET - CAM); fwd.z = 0; fwd.normalize(); rgt = Vector((fwd.y, -fwd.x, 0))
box_c = SET
prim("cube", box_c + Vector((0, 0, 0.2)), (0.5, 0.3, 0.2), WOOD, (0, 0, 0.3))                    # apple box (full: 20x12x8 in)
top_r = tripod_stand(SET + rgt * 0.7 - fwd * 0.45, 0.8, 0.38)                                         # low reflector stand right-front of the box
refl = prim("cyl", top_r, (0.4, 0.4, 0.01), GOLD, verts=40)
refl.rotation_euler = Vector((-0.75, 0.35, 0.55)).normalized().to_track_quat("Z", "Y").to_euler()    # gold face turned to the sun and the box
top_l = tripod_stand(SET + rgt * 0.95 + fwd * 0.55, 1.8, 0.5)                                         # light stand + white shoot-through umbrella
_um = bmesh.new(); bmesh.ops.create_cone(_um, cap_ends=False, segments=16, radius1=0.45, radius2=0.03, depth=0.25)
_ume = bpy.data.meshes.new("umb"); _um.to_mesh(_ume); _um.free(); _ume.materials.append(LINEN.m)
umb = bpy.data.objects.new("umb", _ume); umb.location = top_l + Vector((0, 0, 0.05)); sc.collection.objects.link(umb)
umb.rotation_euler = (-(SET - top_l + Vector((0, 0, 1.4)))).normalized().to_track_quat("Z", "Y").to_euler()
0 and prim("sphere", SET - rgt * 0.5 - fwd * 0.9 + Vector((0, 0, 0.08)), (0.35, 0.2, 0.16), CANVAS, (0, 0, 0.4), verts=16)

# foreground: a low kurkar outcrop in the sand (bottom-left), eroded and pitted
ROCK = NB("kurkar"); rb = ROCK.bsdf
rD = ROCK.tex("sandstone_cracks_diff_2k.jpg", 0.5); ROCK.l(ROCK.mix(1.0, rD.outputs[0], (0.85, 0.62, 0.42), "MULTIPLY"), rb.inputs["Base Color"])
rN = ROCK.tex("sandstone_cracks_nor_gl_2k.jpg", 0.5, True); nmr = ROCK.n("ShaderNodeNormalMap"); ROCK.l(rN.outputs[0], nmr.inputs["Color"]); ROCK.l(nmr.outputs[0], rb.inputs["Normal"])
rb.inputs["Roughness"].default_value = 0.85
for i, (off, dist, s) in enumerate(()):
    p = ray_point(off, dist); g = ground(p.x, p.y)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=5, radius=s)
    for v in bm.verts:
        q = v.co.copy(); v.co.z *= 0.42
        v.co += v.normal * s * (0.25 * noise.fractal(q * (1.4 / s) + Vector((i, 0, 0)), 1.0, 2.0, 5) + 0.12 * noise.ridged_multi_fractal(q * (3 / s), 1.0, 2.0, 4, 0.0, 2.0))
        if v.co.z > s * 0.25: v.co.z = s * 0.25 + (v.co.z - s * 0.25) * 0.3   # flat-topped like wave-cut kurkar
    me = bpy.data.meshes.new("rock"); bm.to_mesh(me); bm.free(); me.shade_smooth(); me.materials.append(ROCK.m)
    o = bpy.data.objects.new("rock", me); o.location = g + Vector((0, 0, -0.15 * s)); o.rotation_euler.z = random.random() * 6; sc.collection.objects.link(o)

# talus: fallen kurkar blocks along the foot of the headland, on the side facing us
rt = random.Random(9)
# scree: angular fallen kurkar slabs (flat-shaded, faceted) in a band along the cliff foot on the beach
for k in range(int(os.environ.get("SCREE", "260"))):
    p_ = HEAD_PTS[int(rt.uniform(0.6, 1.0) * 60)]
    q = Vector((p_.x, p_.y)); dv = (Vector((CAM.x, CAM.y)) - q).normalized()
    for st_ in range(160):
        q = q + dv * 0.5
        if land_z(q.x, q.y) < 2.0: break
    q = q + dv * abs(rt.gauss(0, 2.5)) + Vector((dv.y, -dv.x)) * rt.uniform(-10, 10)
    s_ = min(2.2, rt.paretovariate(2.2) * 0.25)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=s_)
    sx, sy, sz = rt.uniform(0.8, 1.5), rt.uniform(0.6, 1.1), rt.uniform(0.35, 0.7)
    for v in bm.verts:
        v.co.x *= sx; v.co.y *= sy; v.co.z *= sz; v.co += Vector((rt.uniform(-1, 1), rt.uniform(-1, 1), rt.uniform(-1, 1))) * s_ * 0.18
    me = bpy.data.meshes.new("talus"); bm.to_mesh(me); bm.free(); me.materials.append(ROCK.m)
    o = bpy.data.objects.new("talus", me); o.location = (q.x, q.y, max(-0.3, land_z(q.x, q.y)) - 0.1 * s_); o.rotation_euler = (rt.random(), rt.random(), rt.random() * 6); sc.collection.objects.link(o)

# stadium crown 3 km up the coast (just switching on) + a string of promenade lights
ST = ground(float(os.environ.get("STX", "1000")), shore_main(1000) - 300)
bm = bmesh.new(); n = 96
for (s, z) in ((1.0, 0), (1.55, 30), (1.62, 34), (1.64, 0)):
    pass
prof = [(1.0, 0.0), (1.5, 26.0), (1.58, 31.0), (1.6, 0.0)]; rings = []
for (s, z) in prof:
    rings.append([bm.verts.new((78 * s * math.cos(k / n * 6.283), 58 * s * math.sin(k / n * 6.283), z)) for k in range(n)])
for r0, r1 in zip(rings[:-1], rings[1:]):
    for k in range(n): bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
me = bpy.data.meshes.new("bowl"); bm.to_mesh(me); bm.free(); me.materials.append(flat("bowlm", (0.5, 0.48, 0.45), 0.6))
o = bpy.data.objects.new("bowl", me); o.location = ST; sc.collection.objects.link(o)
bm = bmesh.new(); vs = [(bm.verts.new((78 * 1.25 * math.cos(k / n * 6.283), 58 * 1.25 * math.sin(k / n * 6.283), 36)), bm.verts.new((78 * 1.25 * math.cos(k / n * 6.283), 58 * 1.25 * math.sin(k / n * 6.283), 33.5))) for k in range(n)]
for k in range(n): bm.faces.new((vs[k][0], vs[(k + 1) % n][0], vs[(k + 1) % n][1], vs[k][1]))
me = bpy.data.meshes.new("crown"); bm.to_mesh(me); bm.free(); me.materials.append(flat("crownm", (0.8, 0.8, 0.8), 0.3, (1.0, 0.93, 0.82), 4.0))
o = bpy.data.objects.new("crown", me); o.location = ST; sc.collection.objects.link(o)
MASTLAMP = flat("mastlamp", (0.8, 0.8, 0.8), 0.3, (1.0, 0.95, 0.86), 25.0)
BLK = flat("blk", (0.6, 0.55, 0.5), 0.7)
for k in range(4):   # four masts, Bloomfield-style, lamps on
    t = k * math.pi / 2 + 0.6; p = ST + Vector((78 * 1.75 * math.cos(t), 58 * 1.75 * math.sin(t), 0))
    prim("cyl", p + Vector((0, 0, 27.5)), (1.0, 1.0, 55), flat("mast", (0.4, 0.4, 0.4), 0.5))
    prim("cube", p + Vector((0, 0, 56)), (9, 2, 5), MASTLAMP, (0, 0, t + 1.57))
LAMP = flat("lamp", (0.8, 0.8, 0.8), 0.5, (1.0, 0.66, 0.32), 80.0)
for X in range(120, 1400, 25):
    g = ground(X, shore_main(X) - 120); prim("sphere", g + Vector((0, 0, 6)), (0.5, 0.5, 0.5), LAMP, verts=8)
# a few white blocks of the town by the stadium
for k in range(14):
    X = random.uniform(900, 1500); g = ground(X, shore_main(X) - random.uniform(300, 1200)); h = random.choice((8, 12, 16, 22))
    prim("cube", g + Vector((0, 0, h / 2)), (random.uniform(10, 22), 12, h), BLK)

# ---------------------------------------------------------------- sky, sun, haze
wd = bpy.data.worlds.new("W"); sc.world = wd; wd.use_nodes = True; wn = wd.node_tree; bg = wn.nodes["Background"]
sky = wn.nodes.new("ShaderNodeTexSky"); sky.sky_type = "MULTIPLE_SCATTERING"; sky.sun_disc = True; sky.sun_size = math.radians(0.8)
sky.sun_elevation = math.radians(SUN_EL); sky.sun_rotation = math.radians(SUN_OFF); sky.altitude = 20; sky.air_density = 1.0; sky.aerosol_density = float(os.environ.get("AER", "0.9"))
try: sky.sun_intensity = float(os.environ.get("SUNI", "0.25"))
except Exception: pass
if os.environ.get("HDRI", "1") == "1":
    # real photographed sunset sky (Poly Haven CC0 "Industrial Sunset 02 (Pure Sky)", sun at 2.2 deg, u=0.5996)
    # three rotations bring its sun exactly onto our sun bearing / elevation
    env = wn.nodes.new("ShaderNodeTexEnvironment"); env.image = img("industrial_sunset_02_puresky_4k.hdr")
    tcw = wn.nodes.new("ShaderNodeTexCoord"); prev = tcw.outputs["Generated"]
    HDR_EL, HDR_AZ = 2.2, -(0.5996 - 0.5) * 360.0   # Cycles equirect: u = -atan2(y, x) / 2pi + 0.5
    our_az = math.degrees(math.atan2(SUN_D.y, SUN_D.x))
    for rot in ((0, 0, math.radians(90 - our_az)), (math.radians(-(SUN_EL - HDR_EL)), 0, 0), (0, 0, math.radians(HDR_AZ - 90))):
        mpn = wn.nodes.new("ShaderNodeMapping"); mpn.vector_type = "VECTOR"; mpn.inputs["Rotation"].default_value = rot
        wn.links.new(prev, mpn.inputs["Vector"]); prev = mpn.outputs[0]
    wn.links.new(prev, env.inputs["Vector"]); wn.links.new(env.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = float(os.environ.get("HDRS", "0.35"))
else:
    wn.links.new(sky.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = float(os.environ.get("SKYS", "0.12"))
sun_d = bpy.data.lights.new("sun", "SUN"); sun_d.energy = float(os.environ.get("SUNE", "4.2")); sun_d.angle = math.radians(0.8); sun_d.color = (1.0, 0.55, 0.26)
sun = bpy.data.objects.new("sun", sun_d); sc.collection.objects.link(sun); sun.rotation_euler = (-SUN_D).to_track_quat("-Z", "Y").to_euler()

hz = bpy.data.materials.new("haze"); hz.use_nodes = True; hn = hz.node_tree; hn.nodes.remove(hn.nodes["Principled BSDF"])
vol = hn.nodes.new("ShaderNodeVolumePrincipled"); vol.inputs["Anisotropy"].default_value = float(os.environ.get("ANISO", "0.45")); vol.inputs["Color"].default_value = (1.0, 0.86, 0.72, 1)
geo = hn.nodes.new("ShaderNodeNewGeometry"); sp = hn.nodes.new("ShaderNodeSeparateXYZ"); hn.links.new(geo.outputs["Position"], sp.inputs[0])
fl = hn.nodes.new("ShaderNodeMath"); fl.operation = "MULTIPLY"; fl.inputs[1].default_value = -1 / 90.0; hn.links.new(sp.outputs["Z"], fl.inputs[0])
ex = hn.nodes.new("ShaderNodeMath"); ex.operation = "EXPONENT"; hn.links.new(fl.outputs[0], ex.inputs[0])
dn = hn.nodes.new("ShaderNodeMath"); dn.operation = "MULTIPLY"; dn.inputs[1].default_value = float(os.environ.get("HAZE", "0.00008")); hn.links.new(ex.outputs[0], dn.inputs[0])
hn.links.new(dn.outputs[0], vol.inputs["Density"]); hn.links.new(vol.outputs["Volume"], hn.nodes["Material Output"].inputs["Volume"])
hb = bpy.data.objects.new("haze", bpy.data.meshes.new("hz")); _b = bmesh.new(); bmesh.ops.create_cube(_b, size=1.0); _b.to_mesh(hb.data); _b.free(); sc.collection.objects.link(hb)
hb.location = (0, 4000, 150); hb.scale = (12000, 9000, 320); hb.data.materials.append(hz); hb.visible_shadow = False
cy.volume_step_rate = 4.0; cy.volume_max_steps = 128

cam_d.dof.focus_distance = (SET - CAM).length
print("set dist %.1f" % (SET - CAM).length)
if os.environ.get("BORDER"):
    bx = [float(v) for v in os.environ["BORDER"].split(",")]; sc.render.use_border = True; sc.render.use_crop_to_border = True
    sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = bx
import time; t0 = time.time()
bpy.ops.render.render(write_still=True)
print("RENDER %.1fs" % (time.time() - t0)); print("DONE", OUT)
