# SHIKO WORLD 2.0 · Concept A SUNLINE · ROUND 2 · Key frame 1 "Home time-slice" (Rendered + composite)
# Round 2 (critique A-round-1): camera 165 m / 35 mm / pitch -12 deg + lens shift (horizon at ~31 %), real hour light only,
# tufted stone pines in 3 shapes, 20x30 m stretch tents, Bloomfield-like stadium, 64 towers with windows, 4 surf rows.
# One Mediterranean coast, rendered from one camera at several hours. A_timeslice_comp.py blends the passes
# along the coast (south = dawn ... north = midnight), the real photographic time-slice technique.
# Run: bpyenv/bin/python A_coast.py -- OUTDIR W H SPP pass1,pass2,...   (passes: data dawn noon golden blue night clay)
import bpy, bmesh, sys, math, os, random
from mathutils import Vector, noise
a = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = a[0]; W = int(a[1]); H = int(a[2]); SPP = int(a[3]); PASSES = a[4].split(",")
PH = os.environ.get("PH", "/tmp/claude-0/-home-user/2c38ec15-b058-5d59-86c9-28307ce7ab10/scratchpad/A/ph/")
os.makedirs(OUTDIR, exist_ok=True)
random.seed(11)

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
cy.device = "CPU"; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02
cy.max_bounces = 6; cy.diffuse_bounces = 3; cy.glossy_bounces = 3; cy.transmission_bounces = 4; cy.volume_bounces = 1
cy.sample_clamp_indirect = 8; cy.blur_glossy = 1.0
sc.render.resolution_x = W; sc.render.resolution_y = H
sc.render.use_persistent_data = True

# ---------------------------------------------------------------- coast geometry
def shore_x(y):
    """x of the waterline at north-coordinate y (sea is x < shore_x). A long S-curve running NNE."""
    return -520.0 + 0.30 * (y + 900.0) + 170.0 * math.sin((y + 900.0) / 760.0) + 18.0 * noise.noise(Vector((y * 0.004, 1.3, 0)))

def sstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t)

def cliff_amt(y):   # golden kurkar cliff stretch, plus a headland far north
    return sstep(150, 250, y) * (1 - sstep(580, 680, y)) + 0.8 * sstep(4300, 4700, y)

def beach_w(y):
    return 55.0 + 25.0 * noise.noise(Vector((y * 0.003, 4.1, 0))) - 25.0 * cliff_amt(y)

def land_z(d, y):
    if d < 0:   # sea floor
        return -min(18.0, 0.025 * (-d)) + 0.6 * math.exp(-((d + 70) / 25) ** 2)
    wb = beach_w(y)
    z = 0.035 * min(d, wb)
    # dunes and the coastal plain
    dn = noise.fractal(Vector((d * 0.012, y * 0.006, 2.0)), 1.0, 2.0, 4)
    z += (9.0 + 5.0 * dn) * sstep(wb, wb + 140, d)
    z += 3.0 * noise.fractal(Vector((d * 0.04, y * 0.03, 7.0)), 1.0, 2.0, 3) * sstep(wb, wb + 60, d)
    z += 18.0 * sstep(300, 1400, d) * (0.6 + 0.4 * noise.fractal(Vector((d * 0.002, y * 0.002, 9.0)), 1.0, 2.0, 4))
    # far ridge (a Carmel-like line of hills inland and in the north)
    z += 240.0 * sstep(2200, 4200, d + 0.3 * max(0.0, y - 2500)) * (0.65 + 0.35 * noise.fractal(Vector((d * 0.0015, y * 0.0012, 5.0)), 1.0, 2.0, 5))
    z += 30.0 * sstep(1800, 3000, d) * noise.ridged_multi_fractal(Vector((d * 0.004, y * 0.004, 3.0)), 1.0, 2.0, 5, 0.0, 2.0)
    # kurkar cliff: a sharp sandstone step at the back of a narrow beach, jagged edge, notches
    c = cliff_amt(y)
    if c > 0:
        edge = wb + 6 + 9 * noise.noise(Vector((y * 0.02, 0.5, 0))) + 4 * noise.noise(Vector((y * 0.09, 2.5, 0)))
        step = sstep(edge, edge + 7, d)
        z += c * (24.0 + 6.0 * noise.noise(Vector((y * 0.01, 8.0, 0)))) * step
        z += c * 1.5 * noise.ridged_multi_fractal(Vector((d * 0.2, y * 0.2, 1.0)), 1.0, 2.0, 3, 0.0, 2.0) * step * (1 - step) * 4
    return z

def axis(segs):
    out = []
    for a0, a1, st in segs:
        n = max(1, int(round((a1 - a0) / st)))
        out += [a0 + (a1 - a0) * i / n for i in range(n)]
    out.append(segs[-1][1]); return out

D_LAND = axis([(-60, 0, 3), (0, 220, 2.0), (220, 700, 5), (700, 1600, 14), (1600, 5200, 40)])
YS = axis([(-1900, 1800, 3.5), (1800, 3200, 6), (3200, 9000, 22)])

def make_grid(name, ds, ys, zf, attrs=True):
    verts = []; dl = []; yl = []
    for y in ys:
        sx = shore_x(y)
        for d in ds:
            verts.append((sx + d, y, zf(d, y))); dl.append(d); yl.append(y)
    nd = len(ds); faces = []
    for j in range(len(ys) - 1):
        for i in range(nd - 1):
            k = j * nd + i; faces.append((k, k + 1, k + nd + 1, k + nd))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    me.shade_smooth()
    if attrs:
        at = me.attributes.new("d", "FLOAT", "POINT"); at.data.foreach_set("value", dl)
        at = me.attributes.new("yy", "FLOAT", "POINT"); at.data.foreach_set("value", yl)
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); return o

# ---------------------------------------------------------------- materials
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
        for k, v in kw.items():
            if k.startswith("i_"):
                key = k[2:].replace("_", " ")
                x.inputs[key].default_value = v
            else: setattr(x, k, v)
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
    def attr(s, name):
        return s.n("ShaderNodeAttribute", attribute_name=name).outputs["Fac"]
    def ss(s, x, e0, e1):   # smoothstep via map range
        m = s.n("ShaderNodeMapRange", interpolation_type="SMOOTHSTEP"); m.inputs[1].default_value = e0; m.inputs[2].default_value = e1
        s.l(x, m.inputs[0]); return m.outputs[0]
    def tex(s, name, scale, nc=False, vec=None):
        t = s.n("ShaderNodeTexImage"); t.image = img(name, nc); t.projection = "BOX"; t.projection_blend = 0.25
        if vec is None:
            tc = s.n("ShaderNodeTexCoord"); mp = s.n("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale,) * 3
            s.l(tc.outputs["Object"], mp.inputs["Vector"]); vec = mp.outputs[0]
        s.l(vec, t.inputs["Vector"]); return t
    def noise(s, scale, detail=4, rough=0.55, vec=None):
        t = s.n("ShaderNodeTexNoise"); t.inputs["Scale"].default_value = scale; t.inputs["Detail"].default_value = detail; t.inputs["Roughness"].default_value = rough
        if vec is not None: s.l(vec, t.inputs["Vector"])
        else:
            tc = s.n("ShaderNodeTexCoord"); s.l(tc.outputs["Object"], t.inputs["Vector"])
        return t

def flat(name, col, rough=0.6, emit=None, estr=0.0, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = col + (1,); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit: b.inputs["Emission Color"].default_value = emit + (1,); b.inputs["Emission Strength"].default_value = estr
    return m

# --- terrain: wet sand -> dry sand -> dune scrub -> plain, kurkar rock on steep faces
def terrain_mat():
    B = NB("terrain"); b = B.bsdf
    d = B.attr("d")
    tc = B.n("ShaderNodeTexCoord"); pos = tc.outputs["Object"]
    sandD = B.tex("coast_sand_01_diff_2k.jpg", 0.12); sandR = B.tex("coast_sand_01_rough_2k.jpg", 0.12, True)
    aerD = B.tex("aerial_beach_01_diff_2k.jpg", 0.006)
    rockD = B.tex("sandstone_cracks_diff_2k.jpg", 0.05); rockN = B.tex("sandstone_cracks_nor_gl_2k.jpg", 0.05, True)
    grsD = B.tex("sparse_grass_diff_2k.jpg", 0.03)
    # sand colour: pale warm Mediterranean sand, broken up by the aerial beach scan at large scale
    sand = B.mix(0.55, sandD.outputs[0], aerD.outputs[0], "MIX")
    sand = B.mix(1.0, sand, (1.18, 1.05, 0.86), "MULTIPLY")
    wet = B.mix(1.0, sand, (0.42, 0.40, 0.36), "MULTIPLY")
    wetf = B.math("SUBTRACT", 1.0, B.ss(d, 2.0, 16.0))
    col = B.mix(wetf, sand, wet)
    # scrub & low pine-green patches on dunes and plain (large-scale noise, no tiling)
    n1 = B.noise(0.012, 6, 0.6); n2 = B.noise(0.07, 4, 0.6)
    veg = B.math("MULTIPLY", B.ss(n1.outputs[0], 0.52, 0.66), B.ss(d, 70.0, 180.0))
    veg = B.math("ADD", veg, B.math("MULTIPLY", B.ss(n2.outputs[0], 0.5, 0.7), B.ss(d, 110.0, 160.0)), clamp=True)
    scrub = B.mix(1.0, grsD.outputs[0], (0.62, 0.56, 0.34), "MULTIPLY")
    dark = B.mix(B.ss(B.noise(0.03, 3).outputs[0], 0.4, 0.65), (0.21, 0.19, 0.11), (0.085, 0.095, 0.045))
    dark = B.mix(0.25, dark, scrub, "OVERLAY")
    col = B.mix(veg, col, dark)
    # inland: the same dune sand and scrub continue (no field patchwork); slightly greyer, more vegetated
    col = B.mix(B.math("MULTIPLY", B.ss(d, 500.0, 1200.0), 0.5), col, B.mix(0.5, col, (0.16, 0.16, 0.10)))
    # rock on steep faces (kurkar: ochre calcareous sandstone)
    geo = B.n("ShaderNodeNewGeometry")
    sep = B.n("ShaderNodeSeparateXYZ"); B.l(geo.outputs["Normal"], sep.inputs[0])
    steep = B.math("SUBTRACT", 1.0, B.ss(sep.outputs["Z"], 0.55, 0.8))
    rock = B.mix(1.0, rockD.outputs[0], (0.98, 0.82, 0.64), "MULTIPLY")
    col = B.mix(steep, col, rock)
    # coastal road (thin asphalt band) at ~ d = 430
    road = B.math("MULTIPLY", B.ss(d, 424.0, 425.5), B.math("SUBTRACT", 1.0, B.ss(d, 432.0, 433.5)))
    col = B.mix(road, col, (0.11, 0.10, 0.09))
    B.l(col, b.inputs["Base Color"])
    rg = B.mix(wetf, sandR.outputs[0], (0.25, 0.25, 0.25)); rg = B.mix(road, rg, (0.75, 0.75, 0.75)); B.l(rg, b.inputs["Roughness"])
    nm = B.n("ShaderNodeNormalMap"); B.l(rockN.outputs[0], nm.inputs["Color"]); nm.inputs["Strength"].default_value = 0.8
    bump = B.n("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25; bump.inputs["Distance"].default_value = 0.6
    B.l(B.noise(0.6, 6).outputs[0], bump.inputs["Height"])
    sN = B.tex("coast_sand_01_nor_gl_2k.jpg", 0.25, True); snm = B.n("ShaderNodeNormalMap"); B.l(sN.outputs[0], snm.inputs["Color"]); B.l(snm.outputs[0], bump.inputs["Normal"])
    nmix = B.n("ShaderNodeMix", data_type="VECTOR"); B.l(steep, nmix.inputs[0]); B.l(bump.outputs[0], nmix.inputs[4]); B.l(nm.outputs[0], nmix.inputs[5])
    B.l(nmix.outputs[1], b.inputs["Normal"])
    return B.m

# --- sea: deep blue -> turquoise shallows -> breaking lines of foam -> swash
def sea_mat():
    B = NB("sea"); b = B.bsdf
    d = B.attr("d")
    tc = B.n("ShaderNodeTexCoord"); pos = tc.outputs["Object"]
    deep = (0.006, 0.03, 0.052); mid = (0.01, 0.075, 0.10); shal = (0.04, 0.20, 0.19)
    c = B.mix(B.ss(d, -700.0, -150.0), deep, mid)
    c = B.mix(B.ss(d, -160.0, -20.0), c, shal)
    # foam: two broken breaker lines over sandbars, white-water streaks behind them, swash at the waterline
    nz = B.noise(0.018, 5, 0.6); nz2 = B.noise(0.12, 5, 0.65)
    warp = B.math("MULTIPLY", B.math("SUBTRACT", nz.outputs[0], 0.5), 40.0)
    sepp = B.n("ShaderNodeSeparateXYZ"); B.l(pos, sepp.inputs[0])
    sv = B.n("ShaderNodeCombineXYZ"); B.l(B.math("MULTIPLY", d, 0.09), sv.inputs[0]); B.l(B.math("MULTIPLY", sepp.outputs["Y"], 0.004), sv.inputs[1])
    streak = B.noise(1.0, 6, 0.62, sv.outputs[0])
    patch = B.noise(0.006, 4, 0.5)
    def line(off, w, thr):
        x = B.math("ABSOLUTE", B.math("ADD", B.math("ADD", d, off), warp))
        ln = B.math("SUBTRACT", 1.0, B.ss(x, w * 0.3, w))
        return B.math("MULTIPLY", ln, B.ss(patch.outputs[0], thr, thr + 0.12))
    brk = B.math("MAXIMUM", B.math("MAXIMUM", line(150.0, 7.0, 0.52), line(112.0, 6.0, 0.46)), B.math("MAXIMUM", line(76.0, 5.5, 0.4), line(42.0, 5.0, 0.36)))   # 4 white-water rows
    trail = B.math("MULTIPLY", B.ss(streak.outputs[0], 0.5, 0.68), B.math("MULTIPLY", B.ss(d, -150.0, -60.0), B.math("SUBTRACT", 1.0, B.ss(d, -12.0, -2.0))))
    trail = B.math("MULTIPLY", trail, 0.55)
    swash = B.math("MULTIPLY", B.ss(d, -12.0, -3.0), B.ss(nz2.outputs[0], 0.32, 0.5))
    foam = B.math("MAXIMUM", B.math("MAXIMUM", brk, trail), swash)
    lace = B.ss(B.noise(0.5, 6, 0.7).outputs[0], 0.38, 0.6)
    foam = B.math("MULTIPLY", foam, B.math("ADD", 0.45, B.math("MULTIPLY", lace, 0.55)), clamp=True)
    col = B.mix(foam, c, (0.78, 0.80, 0.80))
    B.l(col, b.inputs["Base Color"])
    rough = B.math("ADD", 0.035, B.math("MULTIPLY", foam, 0.75)); B.l(rough, b.inputs["Roughness"])
    b.inputs["IOR"].default_value = 1.33; b.inputs["Specular IOR Level"].default_value = 0.5
    # wave normals: swell parallel to the shore + wind chop
    sw = B.math("SINE", B.math("MULTIPLY", B.math("DIVIDE", B.math("ADD", d, B.math("MULTIPLY", nz.outputs[0], 90.0)), 23.0), 6.2832))
    chop = B.noise(0.25, 6, 0.6); chop2 = B.noise(2.2, 4, 0.6)
    h = B.math("ADD", B.math("MULTIPLY", sw, 0.25), B.math("ADD", B.math("MULTIPLY", chop.outputs[0], 0.9), B.math("MULTIPLY", chop2.outputs[0], 0.12)))
    bump = B.n("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.35; bump.inputs["Distance"].default_value = 1.0
    B.l(h, bump.inputs["Height"]); B.l(bump.outputs[0], b.inputs["Normal"])
    return B.m

TER = terrain_mat(); SEA = sea_mat()
ter = make_grid("terrain", [-400, -200, -100] + D_LAND, YS, land_z); ter.data.materials.append(TER)
D_SEA = [-6000, -3000, -1600, -900, -500, -300, -200, -150, -100, -70, -45, -25, -12, -6, -2, 0, 4]
sea = make_grid("sea", D_SEA, axis([(-1900, 2200, 10), (2200, 9000, 30)]), lambda d, y: 0.0); sea.data.materials.append(SEA)
# open sea to the horizon (outside the shore-aligned grid)
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=4000000); me = bpy.data.meshes.new("ocean"); bm.to_mesh(me); bm.free()
oc = bpy.data.objects.new("ocean", me); oc.location = (0, 0, -0.4); sc.collection.objects.link(oc)
at = me.attributes.new("d", "FLOAT", "POINT"); at.data.foreach_set("value", [-9000.0] * len(me.vertices)); oc.data.materials.append(SEA)

def on_land(d, y): return Vector((shore_x(y) + d, y, land_z(d, y)))

# ---------------------------------------------------------------- round 2 layout along the coast (y = north)
# camera ~ y -700 over the water; dawn surf y -330..-150, noon festival y -110..170, golden kurkar cliff y 260..680,
# blue-hour stadium y ~900, night city y 1150+.
Y_SURF, Y_FEST, Y_CLIFF, Y_STAD, Y_CITY = (-360, -200), (-170, 110), (210, 600), 790, 1060

def on_land(d, y): return Vector((shore_x(y) + d, y, land_z(d, y)))
def shore_rot(y):   # heading of the coast at y (radians, for aligning buildings)
    return math.atan2(1.0, (shore_x(y + 5) - shore_x(y - 5)) / 10.0) * -1 + math.pi / 2

# ---------------------------------------------------------------- stone pines: 3 tufted prototypes with different crowns
from mathutils import Matrix
NEEDLE = NB("needles"); nb_ = NEEDLE.bsdf
oi = NEEDLE.n("ShaderNodeObjectInfo")
NEEDLE.l(NEEDLE.mix(oi.outputs["Random"], (0.035, 0.052, 0.020), (0.065, 0.075, 0.030)), nb_.inputs["Base Color"]); nb_.inputs["Roughness"].default_value = 0.75
trn = NEEDLE.n("ShaderNodeBsdfTranslucent"); trn.inputs["Color"].default_value = (0.20, 0.26, 0.05, 1)
mxs = NEEDLE.n("ShaderNodeMixShader"); mxs.inputs[0].default_value = 0.3
NEEDLE.l(nb_.outputs[0], mxs.inputs[1]); NEEDLE.l(trn.outputs[0], mxs.inputs[2]); NEEDLE.l(mxs.outputs[0], NEEDLE.out.inputs["Surface"])
bpn = NEEDLE.n("ShaderNodeBump"); bpn.inputs["Strength"].default_value = 0.8; NEEDLE.l(NEEDLE.noise(6.0, 3).outputs[0], bpn.inputs["Height"]); NEEDLE.l(bpn.outputs[0], nb_.inputs["Normal"])
BARK = NB("bark"); BARK.l(BARK.mix(1.0, BARK.tex("pine_bark_diff_2k.jpg", 0.6).outputs[0], (0.55, 0.42, 0.36), "MULTIPLY"), BARK.bsdf.inputs["Base Color"])
BARK.bsdf.inputs["Roughness"].default_value = 0.85

def _branch(bm, p0, p1, r0, r1, seg=6):
    dv = p1 - p0; L = dv.length
    mat = Matrix.Translation((p0 + p1) / 2) @ dv.to_track_quat("Z", "Y").to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=seg, radius1=r0, radius2=r1, depth=L, matrix=mat)

def pine_mesh(name, h, r, seed, flat_=0.45, lobes=5):
    rnd = random.Random(seed); bm = bmesh.new()
    lean = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), 0)) * 0.1 * h
    top = Vector((0, 0, h * 0.6)) + lean
    _branch(bm, Vector((0, 0, -0.5)), top, 0.36 * h / 14, 0.24 * h / 14, 8)
    for k in range(lobes):
        ang = k * 2 * math.pi / lobes + rnd.uniform(-0.4, 0.4)
        tip = top + Vector((math.cos(ang) * r * rnd.uniform(0.4, 0.75), math.sin(ang) * r * rnd.uniform(0.4, 0.75), h * rnd.uniform(0.17, 0.28)))
        _branch(bm, top, tip, 0.18 * h / 14, 0.06, 5)
    nwood = len(bm.faces)
    tb = bmesh.new(); bmesh.ops.create_icosphere(tb, subdivisions=1, radius=1.0)
    TV = [v.co.copy() for v in tb.verts]; TF = [[v.index for v in f.verts] for f in tb.faces]; tb.free()
    cz = top.z + h * 0.26
    # crown made of tufts on an umbrella dome; 'lobes' sub-domes make each prototype's outline different
    centers = [Vector((top.x + math.cos(k * 2 * math.pi / lobes) * r * 0.45, top.y + math.sin(k * 2 * math.pi / lobes) * r * 0.45, cz)) for k in range(lobes)] + [Vector((top.x, top.y, cz + 0.6))]
    n = int(170 * (r / 7.0) ** 2)
    for i in range(n):
        c = rnd.choice(centers); rr = r * 0.62 * math.sqrt(rnd.random()); t = rnd.random() * 6.283
        dome = 1 - (rr / (r * 0.62)) ** 2
        p = Vector((c.x + rr * math.cos(t), c.y + rr * math.sin(t), c.z + h * 0.12 * flat_ * 2 * dome + rnd.uniform(-0.4, 0.5)))
        s = rnd.uniform(0.9, 1.5)
        vs = [bm.verts.new((p.x + v.x * s, p.y + v.y * s, p.z + v.z * s * 0.55)) for v in TV]
        for f in TF: bm.faces.new([vs[j] for j in f])
    bm.faces.ensure_lookup_table()
    for i, f in enumerate(bm.faces): f.material_index = 0 if i < nwood else 1; f.smooth = True
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(BARK.m); me.materials.append(NEEDLE.m)
    return me
PROTOS = [pine_mesh("pineA", 13, 7.0, 1, 0.45, 5), pine_mesh("pineB", 16, 8.5, 2, 0.35, 6), pine_mesh("pineC", 10, 5.0, 3, 0.55, 4)]
def place_pine(p, s=1.0):
    o = bpy.data.objects.new("pine", random.choice(PROTOS)); o.location = p; o.scale = (s, s, s * random.uniform(0.9, 1.1)); o.rotation_euler.z = random.random() * 6.28
    sc.collection.objects.link(o)

def groves():
    n = 0
    for _ in range(30000):
        y = random.uniform(-900, 3600); d = random.uniform(40, 1400)
        dens = noise.fractal(Vector((d * 0.004, y * 0.004, 12.0)), 1.0, 2.0, 3)
        thr = 0.18
        if Y_CLIFF[0] - 40 < y < Y_CLIFF[1] + 60 and d < 260: thr = -0.1          # the pine edge on top of the kurkar cliff
        if d < beach_w(y) + 25: continue
        if Y_FEST[0] - 60 < y < Y_FEST[1] + 40 and 70 < d < 300: continue        # festival meadow stays open
        if Y_STAD - 220 < y < Y_STAD + 260 and 120 < d < 560: continue          # stadium precinct
        if y > Y_CITY - 60 and d > 90: continue                                  # city
        if dens > thr:
            place_pine(on_land(d, y), random.uniform(0.7, 1.3)); n += 1
            if n > 2200: break
    return n
NP = groves()

# low Mediterranean scrub (lentisk, retama) as one merged mesh of small blobs: the texture of the dunes from the air
def scrub():
    tb = bmesh.new(); bmesh.ops.create_icosphere(tb, subdivisions=1, radius=1.0)
    TV = [v.co.copy() for v in tb.verts]; TF = [[v.index for v in f.verts] for f in tb.faces]; tb.free()
    verts, faces, cols = [], [], []; n = 0
    pal = ((0.16, 0.17, 0.08), (0.12, 0.14, 0.06), (0.22, 0.2, 0.11), (0.09, 0.11, 0.05))
    for _ in range(140000):
        y = random.uniform(-900, 2600); d = random.uniform(20, 900)
        if y > Y_CITY and d > 90: continue
        if Y_FEST[0] - 40 < y < Y_FEST[1] + 30 and 80 < d < 260: continue
        if d < beach_w(y) + 12: continue
        dens = noise.fractal(Vector((d * 0.01, y * 0.01, 31.0)), 1.0, 2.0, 4) + 0.35 * noise.noise(Vector((d * 0.06, y * 0.06, 2.0)))
        if dens < 0.05: continue
        p = on_land(d, y); r = random.uniform(0.9, 2.6) * (1.3 if d > 300 else 1.0)
        base = len(verts)
        verts += [(p.x + v.x * r, p.y + v.y * r, p.z + v.z * r * 0.55) for v in TV]
        faces += [[base + i for i in f] for f in TF]
        cols.append(random.choice(pal))
        n += 1
        if n >= 42000: break
    me = bpy.data.meshes.new("scrub"); me.from_pydata(verts, [], faces); me.update()
    nf = len(TF); fc = []
    for c in cols: fc += list(c) * 0 + [c] * nf
    at = me.attributes.new("tint", "FLOAT_COLOR", "FACE")
    flat_ = []
    for c in fc: flat_ += [c[0], c[1], c[2], 1.0]
    at.data.foreach_set("color", flat_)
    o = bpy.data.objects.new("scrub", me); sc.collection.objects.link(o)
    B = NB("scrubm"); B.l(B.mix(B.ss(B.noise(0.9, 2).outputs[0], 0.35, 0.65), (0.07, 0.085, 0.035), (0.17, 0.16, 0.08)), B.bsdf.inputs["Base Color"]); B.bsdf.inputs["Roughness"].default_value = 0.85
    me.materials.append(B.m); return n
NS = scrub()

# ---------------------------------------------------------------- festival (14:00): seven 20 x 30 m stretch tents in a dune meadow
FAB = [(0.62, 0.30, 0.16), (0.72, 0.56, 0.24), (0.76, 0.73, 0.66), (0.22, 0.38, 0.37), (0.58, 0.22, 0.14), (0.70, 0.64, 0.52), (0.48, 0.36, 0.22)]
def fabric(col, i):
    B = NB("fab%d" % i); b = B.bsdf
    B.l(B.mix(B.ss(B.noise(0.3, 3).outputs[0], 0.3, 0.7), col, tuple(c * 0.85 for c in col)), b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.75
    b.inputs["Sheen Weight"].default_value = 0.3
    tr = B.n("ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value = col + (1,)
    mx = B.n("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.25
    B.l(b.outputs[0], mx.inputs[1]); B.l(tr.outputs[0], mx.inputs[2]); B.l(mx.outputs[0], B.out.inputs["Surface"])
    return B.m
POLE = flat("pole", (0.35, 0.32, 0.28), 0.5)
pm = bpy.data.meshes.new("person"); bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.24, radius2=0.18, depth=1.7, matrix=Matrix.Translation((0, 0, 0.85))); bm.to_mesh(pm); bm.free()
PPL = [flat("ppl%d" % i, c, 0.7) for i, c in enumerate(((0.05, 0.05, 0.05), (0.55, 0.5, 0.45), (0.5, 0.15, 0.1), (0.12, 0.2, 0.35), (0.7, 0.68, 0.62)))]
def stretch_tent(c, rot, i, Wt=22.0, Lt=32.0):
    rnd = random.Random(40 + i)
    poles = [(rnd.uniform(-2, 2), -Lt * 0.22, rnd.uniform(6.5, 8.0)), (rnd.uniform(-2, 2), Lt * 0.2, rnd.uniform(5.5, 7.0))]
    if rnd.random() < 0.5: poles.append((rnd.uniform(-4, 4), 0.0, rnd.uniform(4.5, 5.5)))
    anchors = [(-Wt / 2, -Lt / 2), (Wt / 2, -Lt / 2), (-Wt / 2, Lt / 2), (Wt / 2, Lt / 2), (-Wt / 2, 0), (Wt / 2, 0), (0, -Lt / 2), (0, Lt / 2)]
    nu, nv = 30, 44; bm = bmesh.new(); vs = []
    for j in range(nu + 1):
        for k in range(nv + 1):
            x = (j / nu - 0.5) * Wt; y = (k / nv - 0.5) * Lt
            pk = max(ph * math.exp(-((x - px) ** 2 + (y - py) ** 2) / (2 * 4.2 ** 2)) for px, py, ph in poles)
            e = min(Wt / 2 - abs(x), Lt / 2 - abs(y)); ef = sstep(0.0, 5.0, e)
            af = max(math.exp(-((x - ax) ** 2 + (y - ay) ** 2) / (2 * 2.2 ** 2)) for ax, ay in anchors)
            z = (2.6 + pk) * (0.45 + 0.55 * ef) * (1 - 0.88 * af) + 0.25
            vs.append(bm.verts.new((x, y, z)))
    for j in range(nu):
        for k in range(nv):
            a_ = j * (nv + 1) + k; bm.faces.new((vs[a_], vs[a_ + 1], vs[a_ + nv + 2], vs[a_ + nv + 1]))
    me = bpy.data.meshes.new("tent%d" % i); bm.to_mesh(me); bm.free(); me.shade_smooth(); me.materials.append(fabric(FAB[i % len(FAB)], i))
    o = bpy.data.objects.new("tent%d" % i, me); o.location = c; o.rotation_euler.z = rot; sc.collection.objects.link(o)
    o.modifiers.new("s", "SOLIDIFY").thickness = 0.05
    for px, py, ph in poles:
        p = Vector((px, py, 0)); p.rotate(o.rotation_euler); prim("cyl", c + p + Vector((0, 0, (ph + 2.6) / 2)), (0.12, 0.12, ph + 2.6), POLE)
    for _ in range(int(Wt * Lt * 0.18)):   # dancers in the shade and around
        x = rnd.uniform(-Wt * 0.6, Wt * 0.6); y = rnd.uniform(-Lt * 0.6, Lt * 0.6); p = Vector((x, y, 0)); p.rotate(o.rotation_euler); p += c
        q = on_land(p.x - shore_x(p.y), p.y)
        prim("cyl", q + Vector((0, 0, 0.85)), (0.22, 0.22, 1.7), rnd.choice(PPL), verts=6)
for i in range(7):
    y = Y_FEST[0] + i * (Y_FEST[1] - Y_FEST[0]) / 6.0 + random.uniform(-12, 12); d = 120 + 55 * math.sin(i * 1.7) + random.uniform(-10, 10)
    stretch_tent(on_land(d, y), shore_rot(y) + random.uniform(-0.5, 0.5), i)
# a stage at the north end of the meadow: dark truss box facing the tents
STG = flat("stage", (0.06, 0.06, 0.065), 0.5)
sp_ = on_land(215, Y_FEST[1] + 35); prim("cube", sp_ + Vector((0, 0, 5)), (16, 10, 10), STG, (0, 0, shore_rot(Y_FEST[1])))

# ---------------------------------------------------------------- stadium (20:15): Bloomfield-like rectangular bowl, two tiers, roofs
def wedge(bm, x0, x1, y0, y1, z0f, z0b, z1f, z1b):
    """box whose top slopes from front (y0) to back (y1): stand tier"""
    v = [bm.verts.new(p) for p in ((x0, y0, z0f), (x1, y0, z0f), (x1, y1, z0b), (x0, y1, z0b), (x0, y0, z1f), (x1, y0, z1f), (x1, y1, z1b), (x0, y1, z1b))]
    for f in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)): bm.faces.new([v[i] for i in f])
SEAT = NB("seats"); sb = SEAT.bsdf
rows = SEAT.n("ShaderNodeTexWave"); rows.bands_direction = "Z"; rows.inputs["Scale"].default_value = 1.4
tcs_ = SEAT.n("ShaderNodeTexCoord"); SEAT.l(tcs_.outputs["Object"], rows.inputs["Vector"])
blk = SEAT.n("ShaderNodeTexWave"); blk.bands_direction = "X"; blk.inputs["Scale"].default_value = 0.09; SEAT.l(tcs_.outputs["Object"], blk.inputs["Vector"])
seatc = SEAT.mix(SEAT.ss(blk.outputs["Fac"], 0.1, 0.12), (0.62, 0.50, 0.05), (0.06, 0.12, 0.32))
SEAT.l(SEAT.mix(SEAT.ss(rows.outputs["Fac"], 0.25, 0.35), (0.05, 0.05, 0.05), seatc), sb.inputs["Base Color"]); sb.inputs["Roughness"].default_value = 0.5
CONC = flat("concrete", (0.55, 0.53, 0.50), 0.8); ROOF = flat("roof", (0.70, 0.70, 0.68), 0.35, metal=0.3)
CROWN = flat("crownm", (0.8, 0.8, 0.8), 0.3, (1.0, 0.96, 0.88), 0.0)
PITCH = NB("pitchm"); w_ = PITCH.n("ShaderNodeTexWave"); w_.inputs["Scale"].default_value = 0.05; w_.bands_direction = "Y"
tcp = PITCH.n("ShaderNodeTexCoord"); PITCH.l(tcp.outputs["Object"], w_.inputs["Vector"])
PITCH.l(PITCH.mix(PITCH.ss(w_.outputs["Fac"], 0.45, 0.55), (0.045, 0.15, 0.03), (0.07, 0.21, 0.045)), PITCH.bsdf.inputs["Base Color"])
def stadium(c, rot):
    PW, PL = 72.0, 112.0                     # pitch + margin (x = short side)
    bm = bmesh.new()
    # 4 stands (sides 1,3 = long stands along the touchlines; 0,2 = end stands), lower + upper tier + back wall
    for side in range(4):
        long_ = side % 2 == 1
        half_run = (PL / 2 + 6) if long_ else (PW / 2 + 6)
        off = (PW / 2 + 3) if long_ else (PL / 2 + 3)
        parts = [(-half_run, half_run, off, off + 24, 0.5, 0.5, 1.5, 13.0), (-half_run, half_run, off + 24, off + 26, 0.5, 0.5, 13.0, 15.0),
                 (-half_run, half_run, off + 26, off + 46, 0.5, 0.5, 15.5, 28.0), (-half_run - 6, half_run + 6, off + 46, off + 49, 0.0, 0.0, 30.0, 30.0)]
        R = Matrix.Rotation(side * math.pi / 2, 3, "Z")
        for (x0, x1, y0, y1, z0f, z0b, z1f, z1b) in parts:
            n0 = len(bm.verts); wedge(bm, x0, x1, y0, y1, z0f, z0b, z1f, z1b); bm.verts.ensure_lookup_table()
            for v in bm.verts[n0:]: v.co = R @ v.co
    me = bpy.data.meshes.new("stands"); bm.to_mesh(me); bm.free(); me.materials.append(SEAT.m)
    o = bpy.data.objects.new("stands", me); o.location = c; o.rotation_euler.z = rot; sc.collection.objects.link(o)
    # roofs over each stand + light strip under the front edge
    for side in range(4):
        long_ = side % 2 == 1
        half_run = (PL / 2 + 8) if long_ else (PW / 2 + 8)
        off = (PW / 2 + 3) if long_ else (PL / 2 + 3)
        bm = bmesh.new(); wedge(bm, -half_run, half_run, off + 8, off + 50, 34.0, 32.0, 35.2, 33.2)
        R = Matrix.Rotation(side * math.pi / 2, 3, "Z")
        for v in bm.verts: v.co = R @ v.co
        me = bpy.data.meshes.new("roof"); bm.to_mesh(me); bm.free(); me.materials.append(ROOF)
        r_ = bpy.data.objects.new("roof", me); r_.location = c; r_.rotation_euler.z = rot; sc.collection.objects.link(r_)
        bm = bmesh.new(); wedge(bm, -half_run + 4, half_run - 4, off + 8.5, off + 10.5, 33.2, 33.2, 33.9, 33.9)
        for v in bm.verts: v.co = R @ v.co
        me = bpy.data.meshes.new("crown"); bm.to_mesh(me); bm.free(); me.materials.append(CROWN)
        cr = bpy.data.objects.new("crown", me); cr.location = c; cr.rotation_euler.z = rot; sc.collection.objects.link(cr)
    # corner blocks + concourse plinth
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = Vector((sx * (PW / 2 + 30), sy * (PL / 2 + 30), 0)); p.rotate(Matrix.Rotation(rot, 3, "Z"))
            prim("cube", c + p + Vector((0, 0, 9)), (44, 44, 18), CONC, (0, 0, rot))
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    me = bpy.data.meshes.new("pitch"); bm.to_mesh(me); bm.free(); me.materials.append(PITCH.m)
    pt = bpy.data.objects.new("pitch", me); pt.location = c + Vector((0, 0, 0.6)); pt.scale = (PW + 6, PL + 6, 1); pt.rotation_euler.z = rot; sc.collection.objects.link(pt)
    lights = []
    for k in range(6):
        ld = bpy.data.lights.new("flood%d" % k, "AREA"); ld.size = 30; ld.spread = math.radians(40); ld.energy = 0.0; ld.color = (1.0, 0.97, 0.92)
        lo = bpy.data.objects.new("flood%d" % k, ld); p = Vector(((k % 2 - 0.5) * PW * 0.9, (k // 2 - 1) * PL * 0.4, 33)); p.rotate(Matrix.Rotation(rot, 3, "Z"))
        lo.location = c + p; sc.collection.objects.link(lo); lights.append(ld)
    return lights
ST_C = on_land(260, Y_STAD); ST_C.z = land_z(260, Y_STAD) * 0 + 6.0
FLOODS = stadium(ST_C, shore_rot(Y_STAD))
HALL = flat("hall", (0.62, 0.60, 0.56), 0.5)
hall_glow = flat("hallglow", (0.6, 0.6, 0.6), 0.4, (1.0, 0.78, 0.45), 0.0)
hp = on_land(430, Y_STAD + 210)
prim("cube", hp + Vector((0, 0, 8)), (70, 48, 16), HALL, (0, 0, shore_rot(Y_STAD)))
prim("cube", hp + Vector((0, 0, 14.5)), (71, 49, 2.2), hall_glow, (0, 0, shore_rot(Y_STAD)))

# ---------------------------------------------------------------- the city (night): 60 towers 30-180 m + low-rise, lit windows
FAC = NB("facade"); fb = FAC.bsdf
geo_ = FAC.n("ShaderNodeNewGeometry"); sep_ = FAC.n("ShaderNodeSeparateXYZ"); FAC.l(geo_.outputs["Position"], sep_.inputs[0])
uvw = FAC.n("ShaderNodeCombineXYZ"); FAC.l(FAC.math("ADD", sep_.outputs["X"], sep_.outputs["Y"]), uvw.inputs[0]); FAC.l(sep_.outputs["Z"], uvw.inputs[1])
win = FAC.n("ShaderNodeTexBrick"); win.inputs["Scale"].default_value = 1.0; win.inputs["Mortar Size"].default_value = 0.85; win.inputs["Brick Width"].default_value = 2.9; win.inputs["Row Height"].default_value = 3.4; win.inputs["Color1"].default_value = (0, 0, 0, 1); win.inputs["Color2"].default_value = (1, 1, 1, 1)
win.offset = 0.0; FAC.l(uvw.outputs[0], win.inputs["Vector"])
oi3 = FAC.n("ShaderNodeObjectInfo")
wn_ = FAC.n("ShaderNodeTexWhiteNoise"); FAC.l(win.outputs["Color"], wn_.inputs["Vector"])
glassf = FAC.ss(FAC.noise(0.002, 1).outputs[0], 0.3, 0.7)
base_c = FAC.mix(oi3.outputs["Random"], (0.50, 0.48, 0.45), (0.24, 0.27, 0.30))
FAC.l(FAC.mix(win.outputs["Fac"], (0.05, 0.06, 0.07), base_c), fb.inputs["Base Color"])
FAC.l(FAC.mix(win.outputs["Fac"], (0.12, 0.12, 0.12), (0.7, 0.7, 0.7)), fb.inputs["Roughness"])
clus = FAC.ss(FAC.noise(0.07, 2, 0.5, vec=geo_.outputs["Position"]).outputs[0], 0.50, 0.56)   # lit floors come in clusters (offices/flats), not an even glow
litw = FAC.math("MULTIPLY", FAC.math("MULTIPLY", FAC.math("SUBTRACT", 1.0, win.outputs["Fac"]), FAC.math("LESS_THAN", wn_.outputs["Value"], 0.45)), clus)
WIN_V = FAC.n("ShaderNodeValue"); WIN_V.outputs[0].default_value = 0.0
FAC.l(FAC.math("MULTIPLY", litw, WIN_V.outputs[0]), fb.inputs["Emission Strength"])
FAC.l(FAC.mix(wn_.outputs["Value"], (1.0, 0.78, 0.52), (0.85, 0.9, 1.0)), fb.inputs["Emission Color"])
WHITE = FAC
rc = random.Random(21); NT = 0
while NT < 64:
    y = rc.uniform(Y_CITY + 60, Y_CITY + 2200); d = rc.uniform(110, 950) * (0.5 + 0.5 * rc.random())
    if d < beach_w(y) + 70: continue
    h = rc.choice((32, 45, 60, 75, 90, 110, 130, 150, 180)); fp = rc.uniform(24, 42)
    prim("cube", on_land(d, y) + Vector((0, 0, h / 2 - 1)), (fp, fp * rc.uniform(0.7, 1.2), h), FAC.m, (0, 0, shore_rot(y) + rc.choice((0, 0.1, -0.1, 0.785))))
    NT += 1
for _ in range(420):
    y = rc.uniform(Y_CITY - 80, Y_CITY + 3200); d = rc.uniform(90, 1300)
    if d < beach_w(y) + 45: continue
    h = rc.choice((7, 10, 13, 16, 20, 24))
    prim("cube", on_land(d, y) + Vector((0, 0, h / 2 - 1)), (rc.uniform(14, 28), rc.uniform(12, 22), h), FAC.m, (0, 0, shore_rot(y) + rc.uniform(-0.1, 0.1)))
# promenade lamps along the beach road (only), small and warm
LAMP = flat("lamp", (0.8, 0.8, 0.8), 0.5, (1.0, 0.64, 0.30), 0.0)
lm = bpy.data.meshes.new("lampm"); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.6); bm.to_mesh(lm); bm.free(); lm.materials.append(LAMP)
for y in range(int(Y_STAD - 250), 5200, 28):
    o = bpy.data.objects.new("l", lm); o.location = on_land(beach_w(y) + 18, y) + Vector((0, 0, 6)); sc.collection.objects.link(o)

# ---------------------------------------------------------------- dawn surf: lifeguard huts + surfers
HUT = flat("hut", (0.72, 0.70, 0.66), 0.6)
for y in (Y_SURF[0] + 30, Y_SURF[1] - 10):
    p = on_land(beach_w(y) * 0.5, y)
    prim("cube", p + Vector((0, 0, 4.5)), (4, 4, 3), HUT)
    for sx in (-1, 1):
        for sy in (-1, 1): prim("cyl", p + Vector((sx * 1.7, sy * 1.7, 1.5)), (0.12, 0.12, 3), HUT)
SURF = flat("surfer", (0.03, 0.03, 0.03), 0.4)
for _ in range(12):
    y = random.uniform(Y_SURF[0] - 100, Y_SURF[1] + 50); d = random.uniform(-170, -45)
    prim("cube", (shore_x(y) + d, y, 0.1), (0.6, 2.2, 0.25), SURF, (0, 0, random.random()))

# ---------------------------------------------------------------- sky, sun, haze
wd = bpy.data.worlds.new("W"); sc.world = wd; wd.use_nodes = True; wn = wd.node_tree; WN = wn.nodes; WL = wn.links
bg = WN["Background"]
sky = WN.new("ShaderNodeTexSky"); sky.sky_type = "MULTIPLE_SCATTERING"; sky.sun_disc = False; sky.altitude = 50; sky.air_density = 1.0; sky.aerosol_density = 1.6
# night component: deep blue gradient + stars, added to the physical sky
tcs = WN.new("ShaderNodeTexCoord"); sepw = WN.new("ShaderNodeSeparateXYZ"); WL.new(tcs.outputs["Generated"], sepw.inputs[0])
grad = WN.new("ShaderNodeMapRange"); grad.inputs[1].default_value = 0.0; grad.inputs[2].default_value = 0.5; WL.new(sepw.outputs["Z"], grad.inputs[0])
ncol = WN.new("ShaderNodeMix"); ncol.data_type = "RGBA"; WL.new(grad.outputs[0], ncol.inputs[0])
ncol.inputs[6].default_value = (0.010, 0.016, 0.034, 1); ncol.inputs[7].default_value = (0.002, 0.003, 0.010, 1)
vor = WN.new("ShaderNodeTexVoronoi"); vor.inputs["Scale"].default_value = 420; WL.new(tcs.outputs["Generated"], vor.inputs["Vector"])
star = WN.new("ShaderNodeMapRange"); star.inputs[1].default_value = 0.035; star.inputs[2].default_value = 0.0; WL.new(vor.outputs["Distance"], star.inputs[0])
starp = WN.new("ShaderNodeMath"); starp.operation = "POWER"; starp.inputs[1].default_value = 6.0; WL.new(star.outputs[0], starp.inputs[0])
stars_w = WN.new("ShaderNodeMath"); stars_w.operation = "MULTIPLY"; WL.new(starp.outputs[0], stars_w.inputs[0]); stars_w.inputs[1].default_value = 0.0
add1 = WN.new("ShaderNodeMix"); add1.data_type = "RGBA"; add1.blend_type = "ADD"; add1.inputs[0].default_value = 1.0
WL.new(ncol.outputs[2], add1.inputs[6]); WL.new(stars_w.outputs[0], add1.inputs[7])
night_w = WN.new("ShaderNodeMix"); night_w.data_type = "RGBA"; night_w.blend_type = "ADD"
WL.new(sky.outputs["Color"], night_w.inputs[6]); WL.new(add1.outputs[2], night_w.inputs[7])
WL.new(night_w.outputs[2], bg.inputs["Color"])

sun_d = bpy.data.lights.new("sun", "SUN"); sun_d.angle = math.radians(0.6)
sun = bpy.data.objects.new("sun", sun_d); sc.collection.objects.link(sun)
moon_d = bpy.data.lights.new("moon", "SUN"); moon_d.angle = math.radians(0.6); moon_d.color = (0.62, 0.72, 1.0)
moon = bpy.data.objects.new("moon", moon_d); sc.collection.objects.link(moon)

hz = bpy.data.materials.new("haze"); hz.use_nodes = True; hn = hz.node_tree; hn.nodes.remove(hn.nodes["Principled BSDF"])
vol = hn.nodes.new("ShaderNodeVolumePrincipled"); vol.inputs["Anisotropy"].default_value = 0.55
# homogeneous haze slab (sea-breeze inversion layer, 0-380 m): constant density means no ray-marching and no step banding
HAZE_D = hn.nodes.new("ShaderNodeValue"); HAZE_D.outputs[0].default_value = 0.0003
hn.links.new(HAZE_D.outputs[0], vol.inputs["Density"]); hn.links.new(vol.outputs["Volume"], hn.nodes["Material Output"].inputs["Volume"])
hb = bpy.data.objects.new("haze", bpy.data.meshes.new("hz")); _b = bmesh.new(); bmesh.ops.create_cube(_b, size=1.0); _b.to_mesh(hb.data); _b.free(); sc.collection.objects.link(hb)
hb.location = (0, 0, 185); hb.scale = (6000000, 6000000, 390)
hb.data.materials.append(hz); hb.visible_shadow = False
cy.volume_step_rate = 8.0; cy.volume_max_steps = 96

# ---------------------------------------------------------------- camera: 165 m, 35 mm, pitch -12 deg, vertical lens shift puts the horizon at ~31 %
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
CY0 = float(os.environ.get("CAMY", "-700")); CAM_P = Vector((shore_x(CY0) - float(os.environ.get("CAMOFF", "70")), CY0, float(os.environ.get("CAMZ", "165"))))
HEAD = math.radians(float(os.environ.get("CAMHEAD", "66")))        # heading from +x towards +y
PITCH = math.radians(float(os.environ.get("CAMPITCH", "-12")))
fwd = Vector((math.cos(PITCH) * math.cos(HEAD), math.cos(PITCH) * math.sin(HEAD), math.sin(PITCH)))
cam.location = CAM_P; cam.rotation_euler = fwd.to_track_quat("-Z", "Y").to_euler()
cam_d.lens = float(os.environ.get("LENS", "35")); cam_d.shift_y = float(os.environ.get("SHIFTY", "0.10")); cam_d.clip_end = 3000000; cam_d.clip_start = 2.0

# ---------------------------------------------------------------- hours
def sun_dir(el, az):
    e, z = math.radians(el), math.radians(az)
    return Vector((math.cos(e) * math.cos(z), math.cos(e) * math.sin(z), math.sin(e)))

# az measured from +x (east) toward +y (north): north=90, west=180, south=270
# Round 2: no per-hour grade. Hours differ only by sun position / sky; day passes share one exposure.
# dawn sun from the land (ENE, behind-right), golden from the sea (W, front-left): shadows point ~180 deg apart.
HOURS = {
    "dawn":   dict(el=4.0,  az=12,  E=3.2, C=(1.0, 0.78, 0.60), S=0.30, hd=0.00030, hc=(0.88, 0.88, 0.92), exp=0.2, night=0.0, L=0.0),
    "noon":   dict(el=72.0, az=230, E=4.6, C=(1.0, 0.97, 0.94), S=0.22, hd=0.00022, hc=(0.92, 0.95, 1.0), exp=0.2, night=0.0, L=0.0),
    "golden": dict(el=5.0,  az=172, E=3.6, C=(1.0, 0.76, 0.54), S=0.30, hd=0.00030, hc=(0.95, 0.90, 0.85), exp=0.2, night=0.0, L=0.0),
    "blue":   dict(el=-4.0, az=175, E=0.0, C=(1.0, 0.6, 0.4), S=0.9, hd=0.00028, hc=(0.85, 0.88, 1.0), exp=1.4, night=0.25, L=1.0),
    "night":  dict(el=-14., az=190, E=0.0, C=(1.0, 0.6, 0.4), S=0.6, hd=0.00026, hc=(0.85, 0.88, 1.0), exp=1.4, night=1.0, L=1.0),
}

def set_hour(h):
    p = HOURS[h]
    sky.sun_elevation = math.radians(max(p["el"], -12.0)); sky.sun_rotation = math.radians(p["az"] - 90)
    bg.inputs["Strength"].default_value = p["S"]
    sun.rotation_euler = (-sun_dir(p["el"], p["az"])).to_track_quat("-Z", "Y").to_euler()
    sun_d.energy = p["E"]; sun_d.color = p["C"]; sun.hide_render = p["E"] <= 0
    moon_d.energy = 0.035 * p["night"]; moon.rotation_euler = (-sun_dir(35, 300)).to_track_quat("-Z", "Y").to_euler(); moon.hide_render = p["night"] <= 0
    night_w.inputs[0].default_value = p["night"]
    stars_w.inputs[1].default_value = 0.10 * p["night"]
    HAZE_D.outputs[0].default_value = p["hd"] * float(os.environ.get("HAZEK", "0.4")); vol.inputs["Color"].default_value = p["hc"] + (1,)
    sc.view_settings.exposure = p["exp"]
    L = p["L"]
    CROWN.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 30.0 * L
    for f in FLOODS: f.energy = 8e5 * L * float(os.environ.get("FLOODK", "1"))
    hall_glow.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 6.0 * L
    LAMP.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 40.0 * L
    WIN_V.outputs[0].default_value = 0.45 * L * float(os.environ.get("WINK", "1"))

def setup_beauty():
    sc.view_settings.view_transform = "AgX"
    try: sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception: pass
    cy.samples = SPP; cy.use_denoising = True
    try: cy.denoiser = "OPENIMAGEDENOISE"
    except Exception: pass
    sc.view_layers[0].material_override = None; hb.hide_render = False

def setup_data():
    # world-Y (red) and camera distance (green) as unlit colour, read by the compositor script
    m = bpy.data.materials.new("datapass"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes
    N.remove(N["Principled BSDF"]); em = N.new("ShaderNodeEmission")
    geo = N.new("ShaderNodeNewGeometry"); sp = N.new("ShaderNodeSeparateXYZ"); nt.links.new(geo.outputs["Position"], sp.inputs[0])
    dp = N.new("ShaderNodeVectorMath"); dp.operation = "DOT_PRODUCT"; dp.inputs[1].default_value = (0.45, 0.89, 0.0); nt.links.new(geo.outputs["Position"], dp.inputs[0])
    r = N.new("ShaderNodeMapRange"); r.inputs[1].default_value = -2000; r.inputs[2].default_value = 8000; nt.links.new(dp.outputs["Value"], r.inputs[0])
    cb = N.new("ShaderNodeCombineColor"); nt.links.new(r.outputs[0], cb.inputs[0])
    cb.inputs[2].default_value = 1.0
    dist = N.new("ShaderNodeVectorMath"); dist.operation = "DISTANCE"; dist.inputs[1].default_value = CAM_P; nt.links.new(geo.outputs["Position"], dist.inputs[0])
    at_d = N.new("ShaderNodeAttribute"); at_d.attribute_name = "d"   # distance from the waterline (negative = offshore)
    g = N.new("ShaderNodeMapRange"); g.inputs[1].default_value = -1000; g.inputs[2].default_value = 0; nt.links.new(at_d.outputs["Fac"], g.inputs[0]); nt.links.new(g.outputs[0], cb.inputs[1])
    nt.links.new(cb.outputs[0], em.inputs["Color"]); nt.links.new(em.outputs[0], N["Material Output"].inputs["Surface"])
    sc.view_layers[0].material_override = m; hb.hide_render = True
    bg.inputs["Strength"].default_value = 0.0
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"; sc.view_settings.exposure = 0.0
    try: sc.view_settings.view_transform = "Raw"
    except Exception: pass
    cy.samples = 4; cy.use_denoising = False
    sc.render.image_settings.color_depth = "16"

import time
for ps in PASSES:
    t0 = time.time()
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16"
    if ps == "data": setup_data()
    else:
        setup_beauty(); set_hour(ps)
    sc.render.filepath = os.path.join(OUTDIR, "pass_%s.png" % ps)
    bpy.ops.render.render(write_still=True)
    print("PASS", ps, "%.1fs" % (time.time() - t0), flush=True)
print("DONE pines=%d scrub=%d" % (NP, NS))
