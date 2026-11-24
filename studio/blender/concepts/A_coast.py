# SHIKO WORLD 2.0 · Concept A SUNLINE · Key frame 1 "Home time-slice" (Rendered + composite)
# One Mediterranean coast, rendered from one camera at several hours. A_timeslice_comp.py blends the passes
# along the coast (south = dawn ... north = midnight), the real photographic time-slice technique.
# Run: bpyenv/bin/python A_coast.py -- OUTDIR W H SPP pass1,pass2,...   (passes: data dawn noon golden blue night clay)
import bpy, bmesh, sys, math, os, random
from mathutils import Vector, noise
a = sys.argv[sys.argv.index("--") + 1:]
OUTDIR = a[0]; W = int(a[1]); H = int(a[2]); SPP = int(a[3]); PASSES = a[4].split(",")
PH = os.environ.get("PH", "/tmp/claude-0/-home-user/2c38ec15-b058-5d59-86c9-28307ce7ab10/scratchpad/ph/")
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
    return sstep(420, 620, y) * (1 - sstep(1250, 1420, y)) + 0.8 * sstep(4300, 4700, y)

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
    # inland plain: dry summer fields + orchards (patchwork) beyond 600 m
    fields = B.n("ShaderNodeTexVoronoi"); fields.distance = "CHEBYCHEV"; fields.inputs["Scale"].default_value = 1.0; fields.inputs["Randomness"].default_value = 0.85
    fmp = B.n("ShaderNodeMapping"); fmp.inputs["Rotation"].default_value = (0, 0, 0.33); fmp.inputs["Scale"].default_value = (0.011, 0.018, 0.01); B.l(pos, fmp.inputs["Vector"]); B.l(fmp.outputs[0], fields.inputs["Vector"])
    sepf = B.n("ShaderNodeSeparateColor"); B.l(fields.outputs["Color"], sepf.inputs[0])
    ramp = B.n("ShaderNodeValToRGB"); B.l(sepf.outputs[0], ramp.inputs[0]); el = ramp.color_ramp.elements
    el[0].position = 0.0; el[0].color = (0.40, 0.35, 0.24, 1); el[1].position = 1.0; el[1].color = (0.33, 0.31, 0.20, 1)
    for pos_, c_ in ((0.3, (0.46, 0.40, 0.28, 1)), (0.55, (0.22, 0.23, 0.13, 1)), (0.75, (0.42, 0.37, 0.26, 1))):
        e = el.new(pos_); e.color = c_
    ramp.color_ramp.interpolation = "CONSTANT"
    fcol = B.mix(1.0, ramp.outputs[0], B.mix(B.noise(0.05, 5).outputs[0], (0.8, 0.8, 0.8), (1.15, 1.12, 1.08)), "MULTIPLY")
    col = B.mix(B.math("MULTIPLY", B.ss(d, 500.0, 900.0), 0.85), col, fcol)
    # rock on steep faces (kurkar: ochre calcareous sandstone)
    geo = B.n("ShaderNodeNewGeometry")
    sep = B.n("ShaderNodeSeparateXYZ"); B.l(geo.outputs["Normal"], sep.inputs[0])
    steep = B.math("SUBTRACT", 1.0, B.ss(sep.outputs["Z"], 0.55, 0.8))
    rock = B.mix(1.0, rockD.outputs[0], (1.25, 0.95, 0.66), "MULTIPLY")
    col = B.mix(steep, col, rock)
    # coastal road (thin asphalt band) at ~ d = 430
    road = B.math("MULTIPLY", B.ss(d, 424.0, 425.5), B.math("SUBTRACT", 1.0, B.ss(d, 432.0, 433.5)))
    col = B.mix(road, col, (0.11, 0.10, 0.09))
    B.l(col, b.inputs["Base Color"])
    rg = B.mix(wetf, sandR.outputs[0], (0.25, 0.25, 0.25)); rg = B.mix(road, rg, (0.75, 0.75, 0.75)); B.l(rg, b.inputs["Roughness"])
    nm = B.n("ShaderNodeNormalMap"); B.l(rockN.outputs[0], nm.inputs["Color"]); nm.inputs["Strength"].default_value = 0.8
    bump = B.n("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25; bump.inputs["Distance"].default_value = 0.6
    B.l(B.noise(0.6, 6).outputs[0], bump.inputs["Height"])
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
    brk = B.math("MAXIMUM", line(115.0, 7.0, 0.5), line(58.0, 5.0, 0.42))
    trail = B.math("MULTIPLY", B.ss(streak.outputs[0], 0.5, 0.68), B.math("MULTIPLY", B.ss(d, -110.0, -60.0), B.math("SUBTRACT", 1.0, B.ss(d, -12.0, -2.0))))
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

# ---------------------------------------------------------------- stone pines (umbrella pines), instanced
def pine_proto(name, h, r):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.35 * h / 12, radius2=0.18 * h / 12, depth=h * 0.8, matrix=__import__("mathutils").Matrix.Translation((0, 0, h * 0.4)))
    me = bpy.data.meshes.new(name + "_t"); bm.to_mesh(me); bm.free()
    trunk = me
    bm = bmesh.new()
    for k in range(7):
        ang = k * 2 * math.pi / 7 + random.random()
        rr = r * (0.35 + 0.35 * random.random())
        c = Vector((math.cos(ang) * rr * (0 if k == 0 else 1), math.sin(ang) * rr * (0 if k == 0 else 1), h * (0.86 + 0.08 * random.random())))
        res = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r * (0.55 if k else 0.7))
        for v in res["verts"]:
            v.co.z *= 0.42; v.co += c
            v.co += v.normal * 0.0
    for v in bm.verts:
        v.co += Vector((0, 0, 1)) * 0.6 * noise.noise(v.co * 0.6) + v.co.normalized() * 0.0
        v.co.x += 0.5 * noise.noise(v.co * 0.9 + Vector((3, 0, 0))); v.co.y += 0.5 * noise.noise(v.co * 0.9 + Vector((0, 3, 0)))
    me2 = bpy.data.meshes.new(name + "_c"); bm.to_mesh(me2); bm.free(); me2.shade_smooth()
    return trunk, me2

PINE_C = NB("pinecrown"); pb = PINE_C.bsdf
oi = PINE_C.n("ShaderNodeObjectInfo")
pc = PINE_C.mix(oi.outputs["Random"], (0.030, 0.050, 0.022), (0.055, 0.070, 0.030))
PINE_C.l(pc, pb.inputs["Base Color"]); pb.inputs["Roughness"].default_value = 0.85
bp = PINE_C.n("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6; PINE_C.l(PINE_C.noise(3.0, 4).outputs[0], bp.inputs["Height"]); PINE_C.l(bp.outputs[0], pb.inputs["Normal"])
BARK = flat("bark", (0.09, 0.06, 0.045), 0.8)
PROTOS = [pine_proto("pine%d" % i, 11 + 4 * i, 5.5 + 1.5 * i) for i in range(3)]

def place_pine(p, s=1.0):
    t, c = random.choice(PROTOS)
    for me, mat in ((t, BARK), (c, PINE_C.m)):
        o = bpy.data.objects.new("pine", me); o.location = p; o.scale = (s, s, s); o.rotation_euler.z = random.random() * 6.28
        if not me.materials: me.materials.append(mat)
        sc.collection.objects.link(o)

def groves():
    n = 0
    for _ in range(26000):
        y = random.uniform(-1500, 4800); d = random.uniform(60, 1500)
        dens = noise.fractal(Vector((d * 0.004, y * 0.004, 12.0)), 1.0, 2.0, 3)
        thr = 0.15
        if 420 < y < 1420: thr = -0.05          # pine edge on top of the golden kurkar cliff
        if d < beach_w(y) + 40: continue
        if -480 < y < 320 and 90 < d < 420: continue   # the festival meadow stays open
        if 1450 < y < 1980 and 220 < d < 560: continue  # stadium precinct
        if dens > thr:
            place_pine(on_land(d, y), random.uniform(0.7, 1.2)); n += 1
            if n > 2600: break
    return n
NP = groves()

# low Mediterranean scrub (lentisk, retama) as one merged mesh of small blobs: the texture of the dunes from the air
def scrub():
    tb = bmesh.new(); bmesh.ops.create_icosphere(tb, subdivisions=1, radius=1.0)
    TV = [v.co.copy() for v in tb.verts]; TF = [[v.index for v in f.verts] for f in tb.faces]; tb.free()
    verts, faces, cols = [], [], []; n = 0
    pal = ((0.16, 0.17, 0.08), (0.12, 0.14, 0.06), (0.22, 0.2, 0.11), (0.09, 0.11, 0.05))
    for _ in range(140000):
        y = random.uniform(-1900, 3000); d = random.uniform(20, 900)
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

# ---------------------------------------------------------------- festival meadow: seven canopies (11:00 -> 19:40)
FAB = [(0.62, 0.16, 0.06), (0.75, 0.48, 0.08), (0.55, 0.06, 0.25), (0.05, 0.34, 0.36), (0.10, 0.12, 0.40), (0.78, 0.72, 0.62), (0.70, 0.10, 0.06)]
def fabric(col, i):
    B = NB("fab%d" % i); b = B.bsdf
    stripes = B.n("ShaderNodeTexWave"); stripes.inputs["Scale"].default_value = 0.35; stripes.inputs["Distortion"].default_value = 0.0
    c2 = tuple(min(0.8, x * 1.35 + 0.05) for x in col)
    c = B.mix(B.ss(stripes.outputs["Fac"], 0.45, 0.55), col, c2)
    B.l(c, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.8
    tr = B.n("ShaderNodeBsdfTranslucent"); B.l(c, tr.inputs["Color"])
    mx = B.n("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.3
    B.l(b.outputs[0], mx.inputs[1]); B.l(tr.outputs[0], mx.inputs[2]); B.l(mx.outputs[0], B.out.inputs["Surface"])
    return B.m
POLE = flat("pole", (0.25, 0.2, 0.15), 0.6)
PEOPLE = [flat("ppl%d" % i, c, 0.7) for i, c in enumerate(((0.05, 0.05, 0.05), (0.5, 0.45, 0.4), (0.6, 0.15, 0.1), (0.1, 0.2, 0.4), (0.7, 0.68, 0.62)))]
pm = bpy.data.meshes.new("person"); bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.25, radius2=0.2, depth=1.7, matrix=__import__("mathutils").Matrix.Translation((0, 0, 0.85))); bm.to_mesh(pm); bm.free()
def canopy(center, size, i, rot):
    n = 24; bm = bmesh.new(); vs = []
    for j in range(n + 1):
        for k in range(n + 1):
            u = j / n * 2 - 1; v = k / n * 2 - 1
            z = 0.22 * size * (u * v) + 0.06 * size * (1 - u * u) * (1 - v * v) * -1   # saddle + slight sag
            vs.append(bm.verts.new((u * size / 2, v * size / 2, z)))
    for j in range(n):
        for k in range(n):
            a_ = j * (n + 1) + k; bm.faces.new((vs[a_], vs[a_ + 1], vs[a_ + n + 2], vs[a_ + n + 1]))
    me = bpy.data.meshes.new("canopy%d" % i); bm.to_mesh(me); bm.free(); me.shade_smooth()
    o = bpy.data.objects.new("canopy%d" % i, me); o.location = center + Vector((0, 0, 0.32 * size)); o.rotation_euler.z = rot
    md = o.modifiers.new("s", "SOLIDIFY"); md.thickness = 0.08
    me.materials.append(fabric(FAB[i], i)); sc.collection.objects.link(o)
    for su in (-1, 1):
        for sv in (-1, 1):
            hgt = 0.32 * size + 0.22 * size * su * sv
            p = Vector((su * size / 2, sv * size / 2, 0)); p.rotate(o.rotation_euler); p += center
            prim("cyl", p + Vector((0, 0, hgt / 2 - 0.5)), (0.18, 0.18, hgt), POLE)
    # dancers under and around the canopy
    for _ in range(int(size * 9)):
        r = size * 0.55 * math.sqrt(random.random()); t = random.random() * 6.28
        y = center.y + r * math.sin(t); dd = center.x + r * math.cos(t) - shore_x(y)
        p = on_land(dd, y)
        o2 = bpy.data.objects.new("p", pm); o2.location = p; sc.collection.objects.link(o2)
    return o
pm.materials.append(PEOPLE[0])
for i in range(7):
    y = -380 + i * 95 + random.uniform(-20, 20); d = 170 + 110 * math.sin(i * 1.3) + random.uniform(-15, 15)
    canopy(on_land(d, y), 26 + 10 * random.random(), i, random.random() * 3)

# ---------------------------------------------------------------- stadium (blue hour) + basketball hall
def stadium(c, A=78, Bb=58, rot=0.35):
    prof = [(1.0, 0.0), (1.06, 1.5), (1.5, 26.0), (1.58, 31.0), (1.6, 0.0)]
    n = 128; bm = bmesh.new(); rings = []
    for (s, z) in prof:
        ring = []
        for k in range(n):
            t = k / n * 2 * math.pi; ring.append(bm.verts.new((A * s * math.cos(t), Bb * s * math.sin(t), z)))
        rings.append(ring)
    for r0, r1 in zip(rings[:-1], rings[1:]):
        for k in range(n): bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
    me = bpy.data.meshes.new("bowl"); bm.to_mesh(me); bm.free()
    bowl = bpy.data.objects.new("bowl", me); bowl.location = c; bowl.rotation_euler.z = rot; sc.collection.objects.link(bowl)
    SEAT = NB("seats"); sb = SEAT.bsdf
    rows = SEAT.n("ShaderNodeTexWave", wave_type="RINGS"); rows.inputs["Scale"].default_value = 0.06
    SEAT.l(SEAT.mix(SEAT.ss(rows.outputs["Fac"], 0.4, 0.6), (0.62, 0.48, 0.05), (0.08, 0.08, 0.09)), sb.inputs["Base Color"]); sb.inputs["Roughness"].default_value = 0.5
    me.materials.append(SEAT.m)
    # roof ring with the light crown underneath
    bm = bmesh.new(); r_in, r_out = [], []
    for k in range(n):
        t = k / n * 2 * math.pi
        r_in.append(bm.verts.new((A * 1.22 * math.cos(t), Bb * 1.22 * math.sin(t), 36.0)))
        r_out.append(bm.verts.new((A * 1.64 * math.cos(t), Bb * 1.64 * math.sin(t), 33.0)))
    for k in range(n): bm.faces.new((r_in[k], r_in[(k + 1) % n], r_out[(k + 1) % n], r_out[k]))
    me = bpy.data.meshes.new("roof"); bm.to_mesh(me); bm.free()
    roof = bpy.data.objects.new("roof", me); roof.location = c; roof.rotation_euler.z = rot; sc.collection.objects.link(roof)
    md = roof.modifiers.new("s", "SOLIDIFY"); md.thickness = 1.2
    me.materials.append(flat("roofm", (0.72, 0.72, 0.70), 0.4, metal=0.0))
    bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=64, radius=1.0)
    me = bpy.data.meshes.new("pitch"); bm.to_mesh(me); bm.free()
    pitch = bpy.data.objects.new("pitch", me); pitch.location = c + Vector((0, 0, 0.3)); pitch.scale = (A * 1.02, Bb * 1.02, 1); pitch.rotation_euler.z = rot; sc.collection.objects.link(pitch)
    PM = NB("pitchm"); w = PM.n("ShaderNodeTexWave"); w.inputs["Scale"].default_value = 0.6; w.bands_direction = "X"
    PM.l(PM.mix(PM.ss(w.outputs["Fac"], 0.45, 0.55), (0.05, 0.16, 0.03), (0.07, 0.21, 0.04)), PM.bsdf.inputs["Base Color"])
    me.materials.append(PM.m)
    # crown of floodlights under the roof edge (emission strength switched per pass)
    bm = bmesh.new(); vs = []
    for k in range(n):
        t = k / n * 2 * math.pi
        vs.append((bm.verts.new((A * 1.24 * math.cos(t), Bb * 1.24 * math.sin(t), 35.0)), bm.verts.new((A * 1.24 * math.cos(t), Bb * 1.24 * math.sin(t), 34.0))))
    for k in range(n): bm.faces.new((vs[k][0], vs[(k + 1) % n][0], vs[(k + 1) % n][1], vs[k][1]))
    me = bpy.data.meshes.new("crown"); bm.to_mesh(me); bm.free()
    cr = bpy.data.objects.new("crown", me); cr.location = c; cr.rotation_euler.z = rot; sc.collection.objects.link(cr)
    me.materials.append(flat("crownm", (0.8, 0.8, 0.8), 0.3, (1.0, 0.95, 0.85), 0.0))
    lights = []
    for k in range(8):
        t = k / 8 * 2 * math.pi
        ld = bpy.data.lights.new("flood%d" % k, "SPOT"); ld.energy = 0.0; ld.spot_size = math.radians(75); ld.color = (1.0, 0.96, 0.9); ld.shadow_soft_size = 2
        lo = bpy.data.objects.new("flood%d" % k, ld); p = Vector((A * 1.2 * math.cos(t), Bb * 1.2 * math.sin(t), 34.0)); p.rotate(roof.rotation_euler)
        lo.location = c + p; dv = (c - lo.location); lo.rotation_euler = dv.to_track_quat("-Z", "Y").to_euler(); sc.collection.objects.link(lo); lights.append(ld)
    return cr.data.materials[0], lights
ST_C = on_land(380, 1700)
CROWN, FLOODS = stadium(ST_C)
HALL = flat("hall", (0.62, 0.60, 0.56), 0.5)
hall_glow = flat("hallglow", (0.6, 0.6, 0.6), 0.4, (1.0, 0.78, 0.45), 0.0)
hp = on_land(480, 1900)
prim("cube", hp + Vector((0, 0, 8)), (70, 48, 16), HALL, (0, 0, 0.35))
prim("cube", hp + Vector((0, 0, 14.5)), (71, 49, 2.2), hall_glow, (0, 0, 0.35))

# ---------------------------------------------------------------- the town in the north (white blocks by day, lights at night)
WHITE = NB("blocks"); wb_ = WHITE.bsdf
oi2 = WHITE.n("ShaderNodeObjectInfo")
WHITE.l(WHITE.mix(oi2.outputs["Random"], (0.62, 0.60, 0.56), (0.74, 0.70, 0.62)), wb_.inputs["Base Color"]); wb_.inputs["Roughness"].default_value = 0.7
# windows: emission from a fine brick pattern, strength driven by a value node switched per pass
win = WHITE.n("ShaderNodeTexBrick"); win.inputs["Scale"].default_value = 0.35; win.inputs["Mortar Size"].default_value = 0.35
tcw = WHITE.n("ShaderNodeTexCoord"); WHITE.l(tcw.outputs["Object"], win.inputs["Vector"])
rnd = WHITE.n("ShaderNodeTexWhiteNoise"); WHITE.l(win.outputs["Color"], rnd.inputs["Vector"])
lit = WHITE.math("MULTIPLY", WHITE.ss(rnd.outputs["Value"], 0.55, 0.56), win.outputs["Fac"])
lit = WHITE.math("SUBTRACT", 1.0, lit)
WIN_V = WHITE.n("ShaderNodeValue"); WIN_V.outputs[0].default_value = 0.0
WHITE.l(WHITE.math("MULTIPLY", WHITE.math("SUBTRACT", 1.0, win.outputs["Fac"]), WIN_V.outputs[0]), wb_.inputs["Emission Strength"])
wb_.inputs["Emission Color"].default_value = (1.0, 0.72, 0.42, 1)
TOWN_LAMPS = []
for _ in range(900):
    y = random.uniform(2150, 7500); d = random.uniform(140, 1300) * (0.5 + 0.5 * random.random())
    if d < beach_w(y) + 70: continue
    if noise.fractal(Vector((d * 0.003, y * 0.003, 20.0)), 1.0, 2.0, 3) < -0.1: continue
    p = on_land(d, y); h = random.choice((9, 12, 15, 18, 24, 30, 45, 70)) if y > 2700 else random.choice((6, 9, 12))
    prim("cube", p + Vector((0, 0, h / 2 - 1)), (random.uniform(14, 30), random.uniform(12, 24), h), WHITE.m, (0, 0, 0.35 + random.uniform(-0.1, 0.1)))
# street lights: a string of warm points along the coast road and town grid (instanced spheres, emission switched)
LAMP = flat("lamp", (0.8, 0.8, 0.8), 0.5, (1.0, 0.62, 0.28), 0.0)
lm = bpy.data.meshes.new("lampm"); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.2); bm.to_mesh(lm); bm.free(); lm.materials.append(LAMP)
for y in range(1300, 7600, 38):
    o = bpy.data.objects.new("l", lm); o.location = on_land(428, y) + Vector((0, 0, 8)); sc.collection.objects.link(o)
for _ in range(1400):
    y = random.uniform(2150, 7500); d = random.uniform(150, 1400)
    o = bpy.data.objects.new("l", lm); o.location = on_land(d, y) + Vector((0, 0, 6)); sc.collection.objects.link(o)
for y in range(1400, 2200, 45):   # stadium approach
    o = bpy.data.objects.new("l", lm); o.location = on_land(260, y) + Vector((0, 0, 7)); sc.collection.objects.link(o)

# ---------------------------------------------------------------- dawn surf: a lifeguard hut + a few surfers in the water
HUT = flat("hut", (0.72, 0.70, 0.66), 0.6)
for y in (-1250, -800, -560):
    p = on_land(beach_w(y) * 0.5, y)
    prim("cube", p + Vector((0, 0, 4.5)), (4, 4, 3), HUT)
    for sx in (-1, 1):
        for sy in (-1, 1):
            prim("cyl", p + Vector((sx * 1.7, sy * 1.7, 1.5)), (0.12, 0.12, 3), HUT)
SURF = flat("surfer", (0.03, 0.03, 0.03), 0.4)
for _ in range(14):
    y = random.uniform(-1500, -600); d = random.uniform(-150, -40)
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

# ---------------------------------------------------------------- camera
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
CAM_P = Vector(tuple(float(v) for v in os.environ.get("CAMP", "-420,-1900,640").split(",")))
CAM_T = Vector(tuple(float(v) for v in os.environ.get("CAMT", "820,1100,-420").split(",")))
cam.location = CAM_P; cam.rotation_euler = (CAM_T - CAM_P).to_track_quat("-Z", "Y").to_euler()
cam_d.lens = float(os.environ.get("LENS", "24")); cam_d.clip_end = 3000000; cam_d.clip_start = 2.0

# ---------------------------------------------------------------- hours
def sun_dir(el, az):
    e, z = math.radians(el), math.radians(az)
    return Vector((math.cos(e) * math.cos(z), math.cos(e) * math.sin(z), math.sin(e)))

# az measured from +x (east) toward +y (north): north=90, west=180, south=270
HOURS = {
    # name: sun el, az, sun energy, sun colour, sky strength, haze density, haze colour, exposure, night, lights
    "dawn":   dict(el=3.0,  az=28,  E=2.6, C=(1.0, 0.62, 0.40), S=0.32, hd=0.00030, hc=(0.85, 0.80, 0.86), exp=0.35, night=0.0, L=0.0),
    "morning":dict(el=15.0, az=60,  E=4.0, C=(1.0, 0.86, 0.72), S=0.26, hd=0.00022, hc=(0.90, 0.92, 0.96), exp=0.0, night=0.0, L=0.0),
    "noon":   dict(el=62.0, az=250, E=5.0, C=(1.0, 0.97, 0.93), S=0.22, hd=0.00020, hc=(0.92, 0.95, 1.0), exp=-0.35, night=0.0, L=0.0),
    "golden": dict(el=5.0,  az=150, E=4.2, C=(1.0, 0.58, 0.30), S=0.30, hd=0.00032, hc=(1.0, 0.86, 0.72), exp=0.15, night=0.0, L=0.0),
    "blue":   dict(el=-3.5, az=152, E=0.0, C=(1.0, 0.6, 0.4), S=0.9, hd=0.00030, hc=(0.80, 0.85, 1.0), exp=1.5, night=0.25, L=1.0),
    "night":  dict(el=-14., az=170, E=0.0, C=(1.0, 0.6, 0.4), S=0.6, hd=0.00028, hc=(0.80, 0.85, 1.0), exp=1.6, night=1.0, L=1.0),
}

def set_hour(h):
    p = HOURS[h]
    sky.sun_elevation = math.radians(max(p["el"], -12.0)); sky.sun_rotation = math.radians(p["az"] - 90)
    bg.inputs["Strength"].default_value = p["S"]
    sun.rotation_euler = (-sun_dir(p["el"], p["az"])).to_track_quat("-Z", "Y").to_euler()
    sun_d.energy = p["E"]; sun_d.color = p["C"]; sun.hide_render = p["E"] <= 0
    moon_d.energy = 0.035 * p["night"]; moon.rotation_euler = (-sun_dir(35, 300)).to_track_quat("-Z", "Y").to_euler(); moon.hide_render = p["night"] <= 0
    night_w.inputs[0].default_value = p["night"]
    stars_w.inputs[1].default_value = 0.35 * p["night"]
    HAZE_D.outputs[0].default_value = p["hd"] * 0.75; vol.inputs["Color"].default_value = p["hc"] + (1,)
    sc.view_settings.exposure = p["exp"]
    L = p["L"]
    CROWN.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 18.0 * L
    for f in FLOODS: f.energy = 4.0e5 * L
    hall_glow.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 6.0 * L
    LAMP.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 60.0 * L
    WIN_V.outputs[0].default_value = 3.0 * L

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
    r = N.new("ShaderNodeMapRange"); r.inputs[1].default_value = -1500; r.inputs[2].default_value = 8500; nt.links.new(sp.outputs["Y"], r.inputs[0])
    cb = N.new("ShaderNodeCombineColor"); nt.links.new(r.outputs[0], cb.inputs[0])
    cb.inputs[2].default_value = 1.0
    dist = N.new("ShaderNodeVectorMath"); dist.operation = "DISTANCE"; dist.inputs[1].default_value = CAM_P; nt.links.new(geo.outputs["Position"], dist.inputs[0])
    g = N.new("ShaderNodeMapRange"); g.inputs[1].default_value = 0; g.inputs[2].default_value = 20000; nt.links.new(dist.outputs["Value"], g.inputs[0]); nt.links.new(g.outputs[0], cb.inputs[1])
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
