# SHIKO WORLD 2.0 — Concept B "DEPTH OF FIELD", round 1 visualisation.
# One fixed camera on a kurkar pine ridge looking west over: portrait set (1.5 m), festival meadow (12 m),
# stadium + hall (~250-300 m), coast/surf/sea (∞). Real camera DOF proves focus-as-navigation.
# Run: /tmp/claude-0/bpyenv/bin/python B_depth_of_field.py -- MODE OUT.png [W H SPP]
#   MODE = hyper (f/16 hyperfocal home) | fest (f/1.4 @ 12 m) | portrait (f/1.4 @ 1.6 m) | bokeh (f/1.2 @ 0.3 m)
# Assets (CC0, Poly Haven) cached in PH below: pine_sapling_small, coast_land_rocks_03, grass_medium_01 (models);
# rough_linen, coast_sand_rocks_02, sparse_grass, concrete_wall_008, aerial_sand, quatrefoil_jacquard_fabric (textures).
import bpy, bmesh, sys, math, os, random, time
from mathutils import Vector, noise, Matrix

a = sys.argv[sys.argv.index("--") + 1:]
MODE = a[0]; OUT = a[1]
W = int(a[2]) if len(a) > 2 else 854; H = int(a[3]) if len(a) > 3 else 480; SPP = int(a[4]) if len(a) > 4 else 32
PH = os.environ.get("PH", "/tmp/claude-0/-home-user/2c38ec15-b058-5d59-86c9-28307ce7ab10/scratchpad/ph/")
T0 = time.time()
random.seed(11)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; cy = sc.cycles
cy.device = "CPU"; cy.samples = SPP; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02
cy.use_denoising = True
try: cy.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
cy.max_bounces = 6; cy.diffuse_bounces = 3; cy.glossy_bounces = 3; cy.transmission_bounces = 4; cy.transparent_max_bounces = 8
cy.volume_bounces = 0; cy.sample_clamp_indirect = 10; cy.blur_glossy = 1.0
sc.render.resolution_x = W; sc.render.resolution_y = H; sc.render.filepath = OUT
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.view_settings.exposure = float(os.environ.get("EXPO", "1.0"))

# ------------------------------------------------------------------ helpers
def img(path, nc=False):
    i = bpy.data.images.load(path, check_existing=True)
    if nc: i.colorspace_settings.name = "Non-Color"
    return i

def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; return m, m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes["Principled BSDF"]

def flat(name, col, rough=0.5, metal=0.0, emit=None, estr=0.0, trans=0.0):
    m, N, L, b = new_mat(name)
    b.inputs["Base Color"].default_value = tuple(col) + (1,); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    b.inputs["Transmission Weight"].default_value = trans
    if emit: b.inputs["Emission Color"].default_value = tuple(emit) + (1,); b.inputs["Emission Strength"].default_value = estr
    return m

def emitm(name, col, s):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    N.remove(N["Principled BSDF"]); e = N.new("ShaderNodeEmission"); e.inputs["Color"].default_value = tuple(col) + (1,); e.inputs["Strength"].default_value = s
    L.new(e.outputs[0], N["Material Output"].inputs["Surface"]); return m

def texset(N, L, vec, tex, scale):
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale,) * 3; L.new(vec, mp.inputs["Vector"])
    out = {}
    for k, nc in (("diff", False), ("rough", True), ("nor_gl", True)):
        n = N.new("ShaderNodeTexImage"); n.image = img(PH + "tex/%s_%s_2k.jpg" % (tex, k), nc); n.projection = "BOX"; n.projection_blend = 0.35
        L.new(mp.outputs["Vector"], n.inputs["Vector"]); out[k] = n.outputs["Color"]
    return out

def pbr(name, tex, scale, tint=(1, 1, 1), rough_add=0.0, nstr=1.0):
    m, N, L, b = new_mat(name); tc = N.new("ShaderNodeTexCoord")
    t = texset(N, L, tc.outputs["Object"], tex, scale)
    mx = N.new("ShaderNodeMixRGB"); mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1; mx.inputs[2].default_value = tuple(tint) + (1,)
    L.new(t["diff"], mx.inputs[1]); L.new(mx.outputs[0], b.inputs["Base Color"])
    ra = N.new("ShaderNodeMath"); ra.operation = "ADD"; ra.inputs[1].default_value = rough_add; L.new(t["rough"], ra.inputs[0]); L.new(ra.outputs[0], b.inputs["Roughness"])
    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = nstr; L.new(t["nor_gl"], nm.inputs["Color"]); L.new(nm.outputs[0], b.inputs["Normal"])
    return m

def link(o): sc.collection.objects.link(o); return o

def mesh_obj(name, bm, mat=None, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    o = link(bpy.data.objects.new(name, me))
    if mat: o.data.materials.append(mat)
    return o

def box(name, size, loc, mat, rot=(0, 0, 0), bevel=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    o = mesh_obj(name, bm, mat, smooth=False); o.location = loc; o.rotation_euler = rot
    if bevel > 0:
        md = o.modifiers.new("bv", "BEVEL"); md.width = bevel; md.segments = 2; md.limit_method = "ANGLE"
    return o

def cyl(name, p0, p1, r0, r1, mat, seg=12):
    p0 = Vector(p0); p1 = Vector(p1); d = p1 - p0
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r0, radius2=r1, depth=d.length)
    o = mesh_obj(name, bm, mat); o.location = (p0 + p1) / 2
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler(); return o

def import_gltf(path):
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=path)
    return [o for o in bpy.data.objects if o not in before]

# ------------------------------------------------------------------ world: blue-gold minute, sun 2° below the sea horizon
SUN_EL, SUN_AZ = float(os.environ.get("SUNEL", "-1.2")), 84.0          # azimuth from +x toward +y; camera looks along +y (= west)
wd = bpy.data.worlds.new("W"); sc.world = wd; wd.use_nodes = True; wn = wd.node_tree
sky = wn.nodes.new("ShaderNodeTexSky"); sky.sky_type = "MULTIPLE_SCATTERING"
sky.sun_elevation = math.radians(SUN_EL); sky.sun_rotation = math.radians(SUN_AZ - 90); sky.sun_disc = False
sky.air_density = 1.0; sky.aerosol_density = float(os.environ.get("AERO", "4.0")); sky.ozone_density = 1.5; sky.altitude = 40
bg = wn.nodes["Background"]; wn.links.new(sky.outputs["Color"], bg.inputs["Color"])
bg.inputs["Strength"].default_value = float(os.environ.get("SKY", "1.0"))

# coastal haze: bounded volume (world volume would swallow the sky), denser low over the plain
hz, N, L, _ = new_mat("haze"); N.remove(N["Principled BSDF"])
vol = N.new("ShaderNodeVolumePrincipled"); vol.inputs["Density"].default_value = float(os.environ.get("HAZE", "0.0013"))
vol.inputs["Color"].default_value = (0.78, 0.8, 0.9, 1); vol.inputs["Anisotropy"].default_value = 0.65
L.new(vol.outputs["Volume"], N["Material Output"].inputs["Volume"])
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(4000, 1700, 40), verts=bm.verts)
hb = mesh_obj("hazebox_low", bm, hz, smooth=False); hb.location = (0, 880, -35)   # y 30..1730, z -55..-15 (dense coastal haze over the plain)
hb.visible_shadow = False
hz2 = hz.copy(); hz2.node_tree.nodes["Principled Volume"].inputs["Density"].default_value = float(os.environ.get("HAZE2", "0.00035"))
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(4000, 1700, 60), verts=bm.verts)
hb2 = mesh_obj("hazebox_high", bm, hz2, smooth=False); hb2.location = (0, 880, 16); hb2.visible_shadow = False
cy.volume_step_rate = 4.0; cy.volume_max_steps = 64

# ------------------------------------------------------------------ terrain: ridge (z 0) -> kurkar step -> meadow (-4.5..-6) -> escarpment -> coastal plain (-46)
Z_PLAIN = -52.0
def edge1(x): return 5.2 + 0.9 * math.sin(x * 0.21) + 0.6 * noise.noise(Vector((x * 0.3, 1.0, 0.0)))
def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def height(x, y):
    e = edge1(x)
    ridge = 0.12 * noise.fractal(Vector((x * 0.4, y * 0.4, 0.2)), 1.0, 2.0, 4)
    meadow = -7.0 - max(0.0, y - e - 3) * 0.03 + 0.25 * noise.fractal(Vector((x * 0.05, y * 0.05, 4.0)), 1.0, 2.0, 3)
    z = ridge + (meadow - ridge) * smooth((y - e) / 2.6)
    z += 0.5 * noise.ridged_multi_fractal(Vector((x * 0.6, y * 0.6, 3.0)), 1.0, 2.0, 3, 0.0, 2.0) * smooth((y - e) / 1.3) * (1 - smooth((y - e - 1.4) / 1.4))
    esc = 46.0 + 3.0 * noise.noise(Vector((x * 0.03, 7.0, 0)))
    z = z + (Z_PLAIN - z) * smooth((y - esc) / 26.0)
    z += 0.35 * math.exp(-((x - 0.9) ** 2 + (y - 3.3) ** 2) / 2.0) * (1 - smooth((y - e) / 1.0))   # low kurkar shelf under the portrait set
    return z

bm = bmesh.new()
NX, NY = 260, 250; X0, X1, Y0, Y1 = -70.0, 70.0, -6.0, 95.0
vs = []
for j in range(NY + 1):
    # denser rows near the camera
    tj = j / NY; y = Y0 + (Y1 - Y0) * (tj ** 1.6)
    row = []
    for i in range(NX + 1):
        x = X0 + (X1 - X0) * i / NX
        row.append(bm.verts.new((x, y, height(x, y))))
    vs.append(row)
for j in range(NY):
    for i in range(NX):
        bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))

# slope-based terrain material: kurkar/sandstone on steep, dry sparse grass on flat
tm, N, L, b = new_mat("terrain"); tc = N.new("ShaderNodeTexCoord")
rk = texset(N, L, tc.outputs["Object"], "coast_sand_rocks_02", 0.35)
gr = texset(N, L, tc.outputs["Object"], "sparse_grass", 0.45)
geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sep.inputs[0])
nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.6; L.new(tc.outputs["Object"], nz.inputs["Vector"])
add = N.new("ShaderNodeMath"); add.operation = "ADD"; L.new(sep.outputs[2], add.inputs[0]); L.new(nz.outputs["Fac"], add.inputs[1])
mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 1.15; mr.inputs["From Max"].default_value = 1.35; L.new(add.outputs[0], mr.inputs["Value"])
# the ridge top itself is bare kurkar (rock) with only patchy grass; the meadow below is grass
sp_p = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Position"], sp_p.inputs[0])
lowz = N.new("ShaderNodeMapRange"); lowz.inputs["From Min"].default_value = -1.2; lowz.inputs["From Max"].default_value = -2.2; L.new(sp_p.outputs[2], lowz.inputs["Value"])
patch = N.new("ShaderNodeTexNoise"); patch.inputs["Scale"].default_value = 0.9; L.new(tc.outputs["Object"], patch.inputs["Vector"])
pmr = N.new("ShaderNodeMapRange"); pmr.inputs["From Min"].default_value = 0.55; pmr.inputs["From Max"].default_value = 0.62; pmr.inputs["To Max"].default_value = 0.8; L.new(patch.outputs["Fac"], pmr.inputs["Value"])
mxz = N.new("ShaderNodeMath"); mxz.operation = "MAXIMUM"; L.new(lowz.outputs[0], mxz.inputs[0]); L.new(pmr.outputs[0], mxz.inputs[1])
fac = N.new("ShaderNodeMath"); fac.operation = "MULTIPLY"; L.new(mr.outputs[0], fac.inputs[0]); L.new(mxz.outputs[0], fac.inputs[1])
def mix(a_, b_, nc=False):
    m_ = N.new("ShaderNodeMixRGB"); L.new(fac.outputs[0], m_.inputs[0]); L.new(a_, m_.inputs[1]); L.new(b_, m_.inputs[2]); return m_.outputs[0]
tint_r = N.new("ShaderNodeMixRGB"); tint_r.blend_type = "MULTIPLY"; tint_r.inputs[0].default_value = 1; tint_r.inputs[2].default_value = (1.0, 0.86, 0.68, 1); L.new(rk["diff"], tint_r.inputs[1])
tint_g = N.new("ShaderNodeMixRGB"); tint_g.blend_type = "MULTIPLY"; tint_g.inputs[0].default_value = 1; tint_g.inputs[2].default_value = (0.85, 0.8, 0.6, 1); L.new(gr["diff"], tint_g.inputs[1])
L.new(mix(tint_r.outputs[0], tint_g.outputs[0]), b.inputs["Base Color"])
L.new(mix(rk["rough"], gr["rough"]), b.inputs["Roughness"])
nmn = N.new("ShaderNodeNormalMap"); L.new(mix(rk["nor_gl"], gr["nor_gl"]), nmn.inputs["Color"]); L.new(nmn.outputs[0], b.inputs["Normal"])
terrain = mesh_obj("terrain", bm, tm)

# ------------------------------------------------------------------ the ledge: kurkar rock lip (CC0 coast_land_rocks_03) + grass tufts
for o in import_gltf(PH + "coast_land_rocks_03/coast_land_rocks_03.gltf"):
    if o.type == "MESH":
        o.location = (-1.6, 6.4, -1.45); o.rotation_euler = (0, 0, math.radians(8)); o.scale = (1.15, 1.0, 1.05)
        for ms in o.material_slots:
            bb = ms.material.node_tree.nodes.get("Principled BSDF")
            if bb:  # warm the grey rock toward kurkar ochre
                src = bb.inputs["Base Color"].links[0].from_socket if bb.inputs["Base Color"].is_linked else None
                if src:
                    nt = ms.material.node_tree; mx = nt.nodes.new("ShaderNodeMixRGB"); mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1
                    mx.inputs[2].default_value = (1.0, 0.78, 0.55, 1); nt.links.new(src, mx.inputs[1]); nt.links.new(mx.outputs[0], bb.inputs["Base Color"])
grass_src = [o for o in import_gltf(PH + "grass_medium_01/grass_medium_01.gltf") if o.type == "MESH" and ("large" in o.name or "mid" in o.name or "tall" in o.name)]
for o in grass_src: o.hide_render = True; o.location = (0, -50, 0)
for k in range(140):
    x = random.uniform(-4, 5); y = random.uniform(3.8, 7.5)
    if abs(x - 1.3) < 1.2 and y < 3.0: continue
    s = random.choice(grass_src); g = link(bpy.data.objects.new("grass", s.data))
    z = height(x, y)
    if y < edge1(x) + 0.4: z = max(z, 0.05)
    g.location = (x, y, z - 0.02); g.rotation_euler = (0, 0, random.uniform(0, 6.28)); sc_ = random.uniform(0.9, 1.5); g.scale = (sc_, sc_, sc_ * random.uniform(1.0, 1.4))

# loose kurkar stones on the ledge
RKM = pbr("stones", "coast_sand_rocks_02", 1.2, (1.0, 0.85, 0.66))
for k in range(30):
    x = random.uniform(-3.0, 3.2); y = random.uniform(3.3, 5.6); r = random.uniform(0.04, 0.14)
    if abs(x - 1.6) < 0.8 and y < 4.6: continue
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=3, radius=r); st = mesh_obj("stone", bm, RKM)
    st.location = (x, y, height(x, y) + r * 0.1); st.scale = (1, random.uniform(0.6, 1.3), random.uniform(0.25, 0.45)); st.rotation_euler = (0, 0, random.uniform(0, 6))
    d_ = st.modifiers.new("d", "DISPLACE"); tx = bpy.data.textures.new("st%d" % k, "VORONOI"); tx.noise_scale = r * 0.8; d_.texture = tx; d_.strength = r * 0.35

# ------------------------------------------------------------------ ~3 m: empty portrait set (linen backdrop on stands, bar stool, bare bulb) and a pine
METAL = flat("stand_metal", (0.035, 0.035, 0.037), 0.35, 1.0)
LIN = pbr("linen", "rough_linen", 1.6, (0.6, 0.5, 0.38), 0.1, 0.8)
nt = LIN.node_tree; bb = nt.nodes["Principled BSDF"]; bb.inputs["Subsurface Weight"].default_value = 0.08; bb.inputs["Subsurface Radius"].default_value = (0.02, 0.018, 0.015)
# backdrop recedes from near-right to far-left; its face turns toward the camera and the stool
P_NEAR = Vector((2.05, 2.75, 0)); P_FAR = Vector((1.45, 4.55, 0)); BW = (P_FAR - P_NEAR).length; DIR = (P_FAR - P_NEAR).normalized()
NRM = Vector((-DIR.y, DIR.x, 0))
if NRM.dot(Vector((0, 0, 0)) - (P_NEAR + P_FAR) / 2) < 0: NRM = -NRM     # front normal, toward camera
def gz(p): return max(0.0, height(p.x, p.y))
def setp(u, z):
    p = P_NEAR + DIR * u; return Vector((p.x, p.y, gz(p) + z))
BH = 2.4
for u in (0.0, BW):
    base = setp(u, 0)
    cyl("pole", base + Vector((0, 0, 0.55)), base + Vector((0, 0, BH + 0.1)), 0.016, 0.013, METAL)
    cyl("clamp", base + Vector((0, 0, 0.5)), base + Vector((0, 0, 0.62)), 0.024, 0.024, METAL)
    for k in range(3):
        ang = k * 2.094 + 0.4; foot = base + Vector((math.cos(ang) * 0.45, math.sin(ang) * 0.45, 0.0))
        cyl("leg", base + Vector((0, 0, 0.6)), foot, 0.01, 0.01, METAL, 8)
cyl("crossbar", setp(-0.08, BH + 0.05), setp(BW + 0.08, BH + 0.05), 0.014, 0.014, METAL)
bm = bmesh.new(); NU, NV = 70, 80; grid = []
for j in range(NV + 1):
    v = j / NV; row = []
    for i in range(NU + 1):
        u = i / NU * (BW - 0.04) + 0.02
        z = BH - v * (BH + 0.75)
        fold = 0.03 * math.sin(u * 11.0 + 0.7) + 0.018 * math.sin(u * 27.0 + 2) + 0.012 * noise.noise(Vector((u * 3, v * 3, 0.5)))
        fold *= (0.35 + v)
        sweep = 0.0
        if z < 0.02:
            sweep = -z; z = 0.02 + 0.025 * noise.noise(Vector((u * 4, sweep * 4, 1))) + 0.04 * math.exp(-sweep * 12)
        p = setp(u, z) + NRM * (fold + sweep)
        row.append(bm.verts.new(p))
    grid.append(row)
for j in range(NV):
    for i in range(NU):
        bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
sheet = mesh_obj("linen", bm, LIN); sd = sheet.modifiers.new("s", "SOLIDIFY"); sd.thickness = 0.004
# bar stool (CC0 bar_chair_round_01, 0.75 m) on the sweep, turned three-quarters: the empty seat waiting for the sitter
STOOL_P = setp(BW * 0.45, 0) + NRM * 0.95
for o in import_gltf(PH + "bar_chair_round_01/bar_chair_round_01.gltf"):
    if o.type == "MESH" and o.parent is None: o.location = STOOL_P; o.rotation_euler = (0, 0, math.radians(35))
# bare tungsten bulb hanging from the bar: the motivated warm light of the set
BULB = emitm("bulb", (1.0, 0.58, 0.26), 80.0)
bp = setp(BW * 0.82, BH - 0.75) + NRM * 0.7; cyl("cord", bp, bp + Vector((0, 0, 1.2)), 0.0025, 0.0025, METAL, 6)
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.03); o = mesh_obj("bulb", bm, BULB); o.location = bp - Vector((0, 0, 0.03)); o.visible_shadow = False
ld = bpy.data.lights.new("setbulb", "POINT"); ld.energy = float(os.environ.get("SETW", "30")); ld.color = (1.0, 0.6, 0.3); ld.shadow_soft_size = 0.03
lo = link(bpy.data.objects.new("setbulb", ld)); lo.location = bp - Vector((0, 0, 0.03))

# pine: trunk at the left edge + CC0 sapling clusters as drooping boughs into the upper-left corner
BARK, N, L, b = new_mat("bark"); tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (2.0, 2.0, 0.7); L.new(tc.outputs["Object"], mp.inputs["Vector"])
for k, sock, nc in (("diff", "Base Color", False), ("rough", "Roughness", True)):
    n = N.new("ShaderNodeTexImage"); n.image = img(PH + "pine_bark_%s_2k.jpg" % k, nc); n.projection = "BOX"; L.new(mp.outputs[0], n.inputs[0]); L.new(n.outputs[0], b.inputs[sock])
n = N.new("ShaderNodeTexImage"); n.image = img(PH + "pine_bark_nor_gl_2k.jpg", True); n.projection = "BOX"; L.new(mp.outputs[0], n.inputs[0])
nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 1.5; L.new(n.outputs[0], nm.inputs["Color"]); L.new(nm.outputs[0], b.inputs["Normal"])
tr = cyl("trunk", (-1.72, 3.1, -0.3), (-1.45, 3.35, 7.0), 0.26, 0.17, BARK, 24)
d_ = tr.modifiers.new("d", "DISPLACE"); tx = bpy.data.textures.new("trn", "CLOUDS"); tx.noise_scale = 0.15; d_.texture = tx; d_.strength = 0.04
saps = [o for o in import_gltf(PH + "pine_sapling_small/pine_sapling_small.gltf") if o.type == "MESH"]
for o in saps: o.hide_render = True
def bough(src, root, rot, s):
    g = link(bpy.data.objects.new("bough", src.data)); g.location = root; g.rotation_euler = rot; g.scale = (s, s, s)
    m_ = Matrix.Rotation(rot[2], 3, "Z") @ Matrix.Rotation(rot[1], 3, "Y") @ Matrix.Rotation(rot[0], 3, "X")
    cyl("limb", root, root + m_ @ Vector((0, 0, 0.75 * s)), 0.05, 0.015, BARK, 8)
bough(saps[0], Vector((-1.55, 3.2, 2.3)), (math.radians(-8), math.radians(106), math.radians(-30)), 1.35)
bough(saps[1], Vector((-1.5, 3.25, 2.75)), (math.radians(6), math.radians(98), math.radians(-5)), 1.4)
bough(saps[2], Vector((-1.6, 3.0, 2.5)), (math.radians(-20), math.radians(115), math.radians(-60)), 1.2)

# ------------------------------------------------------------------ 12 m: festival meadow, seven patterned canopies under string lights
SOLID = {0: (0.85, 0.36, 0.03), 3: (0.55, 0.03, 0.22), 4: (0.02, 0.28, 0.3), 6: (0.6, 0.16, 0.05)}
PRINT = {1: ((0.08, 0.06, 0.25), (0.85, 0.5, 0.06), (0.6, 0.05, 0.2), (0.9, 0.82, 0.6)),
         2: ((0.45, 0.04, 0.08), (0.95, 0.62, 0.12), (0.03, 0.22, 0.28), (0.85, 0.75, 0.55)),
         5: ((0.04, 0.18, 0.12), (0.8, 0.3, 0.45), (0.9, 0.6, 0.1), (0.15, 0.05, 0.3))}
def canopy_mat(i):
    # stretch-lycra shade canopies: solid saturated colours or UV-printed mandala tapestry; translucent so the warm light below glows through
    m, N, L, b = new_mat("canopy%d" % i); tc = N.new("ShaderNodeTexCoord")
    if i in SOLID:
        col_out = None; b.inputs["Base Color"].default_value = SOLID[i] + (1,)
        tl_col = SOLID[i]
    else:
        pal = PRINT[i]
        mp = N.new("ShaderNodeMapping"); mp.inputs["Location"].default_value = (-0.5, -0.5, 0); L.new(tc.outputs["UV"], mp.inputs[0])
        sp = N.new("ShaderNodeSeparateXYZ"); L.new(mp.outputs[0], sp.inputs[0])
        at = N.new("ShaderNodeMath"); at.operation = "ARCTAN2"; L.new(sp.outputs[1], at.inputs[0]); L.new(sp.outputs[0], at.inputs[1])
        ln = N.new("ShaderNodeVectorMath"); ln.operation = "LENGTH"; L.new(mp.outputs[0], ln.inputs[0])
        def op(o_, a_, b_):
            n_ = N.new("ShaderNodeMath"); n_.operation = o_
            for k_, x_ in enumerate((a_, b_)):
                if isinstance(x_, (int, float)): n_.inputs[k_].default_value = x_
                else: L.new(x_, n_.inputs[k_])
            return n_.outputs[0]
        petals = op("SINE", op("ADD", op("MULTIPLY", at.outputs["Value"], 24.0 + 8 * (i % 2)), op("MULTIPLY", op("SINE", op("MULTIPLY", ln.outputs["Value"], 90.0), 0), 1.2)), 0)
        rings = op("SINE", op("MULTIPLY", ln.outputs["Value"], 140.0 + 20 * i), 0)
        f = op("MULTIPLY", op("ADD", op("MULTIPLY", petals, rings), 1.0), 0.5)
        f = op("ADD", op("MULTIPLY", f, 0.75), op("MULTIPLY", op("GREATER_THAN", ln.outputs["Value"], 0.42), 0.25))
        cr = N.new("ShaderNodeValToRGB"); el = cr.color_ramp.elements
        el[0].position = 0.0; el[0].color = pal[0] + (1,); el[1].position = 0.38; el[1].color = pal[1] + (1,)
        e2 = el.new(0.62); e2.color = pal[2] + (1,); e3 = el.new(0.9); e3.color = pal[3] + (1,)
        L.new(f, cr.inputs[0]); col_out = cr.outputs[0]; L.new(col_out, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.55; b.inputs["Sheen Weight"].default_value = 0.5
    tl = N.new("ShaderNodeBsdfTranslucent")
    if col_out: L.new(col_out, tl.inputs["Color"])
    else: tl.inputs["Color"].default_value = tl_col + (1,)
    ms = N.new("ShaderNodeMixShader"); ms.inputs[0].default_value = 0.45
    L.new(b.outputs[0], ms.inputs[1]); L.new(tl.outputs[0], ms.inputs[2]); L.new(ms.outputs[0], N["Material Output"].inputs["Surface"])
    j = N.new("ShaderNodeTexImage"); j.image = img(PH + "tex/quatrefoil_jacquard_fabric_nor_gl_2k.jpg", True)
    mpj = N.new("ShaderNodeMapping"); mpj.inputs["Scale"].default_value = (10, 10, 10); L.new(tc.outputs["UV"], mpj.inputs[0]); L.new(mpj.outputs[0], j.inputs[0])
    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.25; L.new(j.outputs[0], nm.inputs["Color"]); L.new(nm.outputs[0], b.inputs["Normal"])
    return m

WOOD = flat("pole_wood", (0.22, 0.15, 0.09), 0.7)
ROPE = flat("rope", (0.5, 0.45, 0.38), 0.9)
WIRE = flat("wire", (0.02, 0.02, 0.02), 0.5)
SBULB = emitm("stringbulb", (1.0, 0.56, 0.24), float(os.environ.get("SBULB", "30")))
bulbs = bmesh.new()
def add_bulb(p, r=0.022):
    bmesh.ops.create_icosphere(bulbs, subdivisions=1, radius=r, matrix=Matrix.Translation(p))
def strand(p, q, sag, n):
    p = Vector(p); q = Vector(q); pts = []
    for k in range(n + 1):
        t = k / n; pts.append(p.lerp(q, t) + Vector((0, 0, -4 * sag * t * (1 - t))))
    cu = bpy.data.curves.new("strand", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.004
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for k, pt in enumerate(pts): sp.points[k].co = (pt.x, pt.y, pt.z, 1)
    o = link(bpy.data.objects.new("strand", cu)); o.data.materials.append(WIRE)
    for pt in pts[1:-1]: add_bulb(pt - Vector((0, 0, 0.05)))

# seven canopies, left -> right (room order). (x, y, width, depth, peak, yaw, peaks)
CAN = [(-8.2, 17.5, 7.0, 6.0, 5.2, 18, 1), (-6.4, 29.0, 9.0, 6.5, 5.6, -8, 2), (-2.6, 14.0, 7.2, 6.0, 5.4, 6, 1),
       (0.4, 24.0, 9.5, 6.5, 5.6, -14, 2), (2.9, 15.5, 6.5, 5.5, 5.0, 24, 1), (5.2, 33.0, 9.0, 6.5, 5.6, -4, 2), (7.6, 26.0, 7.5, 6.0, 5.3, 12, 1)]
HE = 2.3
pole_tops = []
for i, (cx, cy_, w, d, pk, yaw, npk) in enumerate(CAN):
    gz = height(cx, cy_); rot = Matrix.Rotation(math.radians(yaw), 3, "Z")
    peaks = [(0.0, 0.0)] if npk == 1 else [(-0.24 * w, 0.0), (0.24 * w, 0.0)]
    bm = bmesh.new(); n = 48; uvl = bm.loops.layers.uv.new("UV"); vv = []
    for j in range(n + 1):
        row = []
        for k in range(n + 1):
            un = k / n - 0.5; vn = j / n - 0.5
            x = un * w; y = vn * d
            lift = 0.0
            for (px, py) in peaks:
                hw = (w / 2 - px) if x > px else (w / 2 + px); hd = d / 2
                ax = abs(x - px) / hw; ay = abs(y - py) / hd
                rn = min(1.0, (ax ** 3 + ay ** 3) ** (1 / 3))
                lift = max(lift, (pk - HE) * (1 - rn) ** 1.7)
            z = HE + lift + 0.02 * noise.noise(Vector((un * 6, vn * 6, i)))
            # catenary-cut edges: pull the edge cables inward between corners
            sx = 1 - 0.11 * (1 - (2 * vn) ** 2) * abs(2 * un) ** 3; sy = 1 - 0.11 * (1 - (2 * un) ** 2) * abs(2 * vn) ** 3
            p = rot @ Vector((x * sx, y * sy, 0)) + Vector((cx, cy_, gz + z))
            row.append(bm.verts.new(p))
        vv.append(row)
    for j in range(n):
        for k in range(n):
            f = bm.faces.new((vv[j][k], vv[j][k + 1], vv[j + 1][k + 1], vv[j + 1][k]))
            for lp, (jj, kk) in zip(f.loops, ((j, k), (j, k + 1), (j + 1, k + 1), (j + 1, k))):
                lp[uvl].uv = (kk / n, jj / n)
    o = mesh_obj("canopy%d" % i, bm, canopy_mat(i)); sd = o.modifiers.new("s", "SOLIDIFY"); sd.thickness = 0.012
    corners = [rot @ Vector((sx * w / 2, sy * d / 2, 0)) + Vector((cx, cy_, 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for c in corners:
        g = height(c.x, c.y); top = Vector((c.x, c.y, gz + HE)); cyl("pole", Vector((c.x, c.y, g)), top + Vector((0, 0, 0.08)), 0.04, 0.035, WOOD, 8)
        out = (c - Vector((cx, cy_, 0))).normalized() * 1.8; anchor = Vector((c.x + out.x, c.y + out.y, height(c.x + out.x, c.y + out.y)))
        cyl("guy", top + Vector((0, 0, 0.06)), anchor, 0.006, 0.006, ROPE, 5)
        pole_tops.append(top + Vector((0, 0, 0.06)))
    for (px, py) in peaks:
        pp = rot @ Vector((px, py, 0)) + Vector((cx, cy_, 0))
        cyl("mast", Vector((pp.x, pp.y, gz)), Vector((pp.x, pp.y, gz + pk - 0.05)), 0.06, 0.05, WOOD, 10)
    ld = bpy.data.lights.new("canlight", "POINT"); ld.energy = float(os.environ.get("CANW", "260")); ld.shadow_soft_size = 0.4
    ld.color = (1.0, 0.55, 0.25) if i not in (1, 5) else ((0.95, 0.2, 0.55) if i == 1 else (0.2, 0.6, 0.9))
    lo = link(bpy.data.objects.new("canlight", ld)); lo.location = (cx, cy_, gz + 2.0)
    # string lights inside along the long edges
    strand(corners[0] + Vector((0, 0, height(corners[0].x, corners[0].y) + 1.95)), corners[2] + Vector((0, 0, height(corners[2].x, corners[2].y) + 1.95)), 0.35, 24)
# string lights between canopies (zig-zag across the meadow) and to tall poles
order = sorted(range(len(pole_tops)), key=lambda k: pole_tops[k].x)
for k in range(0, len(order) - 3, 2):
    p, q = pole_tops[order[k]], pole_tops[order[k + 3]]
    if (p - q).length < 14: strand(p, q, 0.5 + 0.2 * random.random(), int((p - q).length * 2.2))
for (x, y) in ((-4.6, 21.5), (1.6, 19.5), (4.0, 29.0), (-10.5, 24.0), (8.8, 20.0)):
    g = height(x, y); top = Vector((x, y, g + 5.0)); cyl("lpole", Vector((x, y, g)), top, 0.05, 0.04, WOOD, 8); pole_tops.append(top)
    for c in sorted(pole_tops[:-1], key=lambda t: (t - top).length)[:3]:
        strand(top, c, 0.45, int((top - c).length * 2.2))
mesh_obj("bulbs", bulbs, SBULB).visible_shadow = False

# festival-goers: organic mannequins from the Skin modifier (real proportions 1.55-1.9 m), varied poses
SKIN = [(0.42, 0.26, 0.17), (0.6, 0.4, 0.28), (0.3, 0.18, 0.12), (0.55, 0.36, 0.24)]
CLOTH = [(0.05, 0.05, 0.06), (0.35, 0.08, 0.1), (0.7, 0.62, 0.5), (0.08, 0.15, 0.25), (0.45, 0.32, 0.12), (0.12, 0.1, 0.08), (0.55, 0.2, 0.35)]
def person_mat(k):
    m, N, L, b = new_mat("person%d" % k); tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    cr = N.new("ShaderNodeValToRGB"); el = cr.color_ramp.elements; cr.color_ramp.interpolation = "CONSTANT"
    tw = random.choice(CLOTH); sh = random.choice(CLOTH); sk = random.choice(SKIN)
    el[0].color = tw + (1,); el[1].position = 0.50; el[1].color = sh + (1,); e3 = el.new(0.80); e3.color = sk + (1,)
    hm = N.new("ShaderNodeMath"); hm.operation = "DIVIDE"; hm.inputs[1].default_value = 1.75; L.new(sep.outputs[2], hm.inputs[0]); L.new(hm.outputs[0], cr.inputs[0])
    L.new(cr.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.6; b.inputs["Sheen Weight"].default_value = 0.4
    return m
PMATS = [person_mat(k) for k in range(10)]
HAIR = flat("hair", (0.03, 0.022, 0.018), 0.45)
def person(loc, yaw, h=1.75, pose=0):
    s = h / 1.75
    J = {"pel": (0, 0, 0.95), "spn": (0, 0.01, 1.2), "chs": (0, 0.0, 1.38), "nck": (0, 0, 1.52), "hd": (0, 0, 1.63),
         "shL": (-0.19, 0, 1.43), "shR": (0.19, 0, 1.43), "hpL": (-0.1, 0, 0.92), "hpR": (0.1, 0, 0.92),
         "knL": (-0.11, 0.02, 0.5), "knR": (0.11, -0.02, 0.5), "ftL": (-0.12, 0.0, 0.06), "ftR": (0.12, 0.0, 0.06)}
    sway = random.uniform(-0.08, 0.08)
    if pose == 0:   # both arms up (dancing)
        J.update(elL=(-0.3, 0.02, 1.7), haL=(-0.24, 0.05, 1.98), elR=(0.3, 0.0, 1.68), haR=(0.2, 0.04, 1.95))
    elif pose == 1: # one arm up
        J.update(elL=(-0.26, 0.05, 1.15), haL=(-0.22, 0.18, 0.98), elR=(0.32, 0.0, 1.7), haR=(0.26, 0.06, 1.98))
    elif pose == 2: # arms relaxed, slight bend
        J.update(elL=(-0.24, 0.03, 1.15), haL=(-0.25, 0.08, 0.9), elR=(0.24, 0.03, 1.15), haR=(0.25, 0.1, 0.9))
    else:           # mid-dance, arms bent forward
        J.update(elL=(-0.27, 0.12, 1.2), haL=(-0.15, 0.3, 1.32), elR=(0.27, 0.1, 1.22), haR=(0.17, 0.32, 1.36))
    R = {"pel": 0.15, "spn": 0.13, "chs": 0.16, "nck": 0.055, "hd": 0.055, "shL": 0.06, "shR": 0.06, "elL": 0.045, "elR": 0.045, "haL": 0.035, "haR": 0.035,
         "hpL": 0.085, "hpR": 0.085, "knL": 0.06, "knR": 0.06, "ftL": 0.045, "ftR": 0.045}
    E = [("pel", "spn"), ("spn", "chs"), ("chs", "nck"), ("nck", "hd"), ("chs", "shL"), ("chs", "shR"), ("shL", "elL"), ("elL", "haL"), ("shR", "elR"), ("elR", "haR"),
         ("pel", "hpL"), ("pel", "hpR"), ("hpL", "knL"), ("knL", "ftL"), ("hpR", "knR"), ("knR", "ftR")]
    keys = list(J.keys()); me = bpy.data.meshes.new("p")
    co = [Vector(J[k]) + Vector((sway * J[k][2] * 0.3, 0, 0)) for k in keys]
    me.from_pydata([c * s for c in co], [(keys.index(a_), keys.index(b_)) for a_, b_ in E], [])
    o = link(bpy.data.objects.new("person", me)); sk_ = o.modifiers.new("skin", "SKIN"); sk_.use_smooth_shade = True
    for k, sv in zip(keys, me.skin_vertices[0].data):
        sv.radius = (R[k] * s * (1.1 if k in ("chs", "pel") else 1.0), R[k] * s * (0.75 if k in ("chs", "pel", "spn") else 1.0))
    me.skin_vertices[0].data[0].use_root = True
    sub = o.modifiers.new("sub", "SUBSURF"); sub.levels = 1; sub.render_levels = 2
    o.data.materials.append(random.choice(PMATS)); o.location = loc; o.rotation_euler = (0, 0, yaw)
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.105 * s); bmesh.ops.scale(bm, vec=(0.9, 1.0, 1.12), verts=bm.verts)
    hd = mesh_obj("head", bm, random.choice(PMATS)); hd.parent = o; hd.location = (sway * 0.5 * s, 0, 1.67 * s)
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.11 * s); bmesh.ops.scale(bm, vec=(0.93, 1.03, 0.8), verts=bm.verts)
    hr = mesh_obj("hair", bm, HAIR); hr.parent = o; hr.location = (sway * 0.5 * s, 0.015 * s, 1.71 * s)
    return o
# crowd clusters under/between canopies, facing a small DJ booth at the far middle
DJ = Vector((-0.5, 38.0, 0)); DJ.z = height(DJ.x, DJ.y)
NPEOPLE = 0
for k in range(400):
    y = random.uniform(15.0, 42.0); x = random.uniform(-0.5, 0.33) * y
    inside = False
    for c in CAN:
        if (Vector((x - c[0], y - c[1], 0))).length < min(c[2], c[3]) * 0.42: inside = True
    if inside and random.random() < 0.85: continue
    if NPEOPLE >= 85: break
    NPEOPLE += 1
    yaw = math.atan2(DJ.x - x, -(DJ.y - y)) + math.pi + random.uniform(-0.6, 0.6)
    person((x, y, height(x, y)), yaw, random.uniform(1.58, 1.9), random.choice((0, 1, 2, 2, 3, 3)))
box("djbooth", (2.6, 1.0, 1.05), (DJ.x, DJ.y, DJ.z + 0.52), flat("booth", (0.05, 0.04, 0.035), 0.6), bevel=0.02)
box("djglow", (2.2, 0.05, 0.12), (DJ.x, DJ.y - 0.52, DJ.z + 0.98), emitm("djglow", (0.6, 0.2, 1.0), 25))

# ------------------------------------------------------------------ coastal plain, town, beach, sea (∞)
PL, N, L, b = new_mat("plain"); tc = N.new("ShaderNodeTexCoord")
nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.02; nz.inputs["Detail"].default_value = 6; L.new(tc.outputs["Object"], nz.inputs["Vector"])
cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.05, 0.06, 0.035, 1); cr.color_ramp.elements[1].color = (0.2, 0.16, 0.1, 1)
L.new(nz.outputs["Fac"], cr.inputs[0]); L.new(cr.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.9
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=120, y_segments=60, size=1.0)
for v in bm.verts:
    x = v.co.x * 1600; y = 275 + v.co.y * 215
    v.co = Vector((x, y, Z_PLAIN - 0.3 + 1.5 * noise.fractal(Vector((x * 0.004, y * 0.004, 2)), 1.0, 2.0, 3) * smooth((y - 120) / 100)))
mesh_obj("plain", bm, PL)   # y 60..660
SAND = pbr("sand", "aerial_sand", 0.05, (1.0, 0.92, 0.8), 0.0, 0.5)
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=60, y_segments=4, size=1.0)
for v in bm.verts:
    t = (v.co.y + 1) / 2; v.co = Vector((v.co.x * 2500, 478 + t * 62, Z_PLAIN + 0.4 - t * 1.8))
mesh_obj("beach", bm, SAND)
# sea: dark, low-roughness, wind-ripple normals; reflects the apricot band
SEA, N, L, b = new_mat("sea"); b.inputs["Base Color"].default_value = (0.008, 0.03, 0.04, 1); b.inputs["Roughness"].default_value = 0.06
b.inputs["IOR"].default_value = 1.33
tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.08, 0.25, 0.1); L.new(tc.outputs["Object"], mp.inputs[0])
nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 8; L.new(mp.outputs[0], nz.inputs["Vector"])
bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25; L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=4, y_segments=4, size=1.0)
for v in bm.verts: v.co = Vector((v.co.x * 30000, 530 + (v.co.y + 1) * 15000, Z_PLAIN - 1.0))
mesh_obj("sea", bm, SEA, smooth=False)
# surf: three breaking lines of foam (noise-masked), slightly raised lips
FOAM, N, L, b = new_mat("foam"); b.inputs["Base Color"].default_value = (0.85, 0.87, 0.88, 1); b.inputs["Roughness"].default_value = 0.5
tc = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.08; nz.inputs["Detail"].default_value = 10
mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.3, 3.0, 1.0); L.new(tc.outputs["Object"], mp.inputs[0]); L.new(mp.outputs[0], nz.inputs[0])
gy = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["UV"], gy.inputs[0])
mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.45; mr.inputs["From Max"].default_value = 0.62; L.new(nz.outputs["Fac"], mr.inputs["Value"])
tr_ = N.new("ShaderNodeBsdfTransparent"); ms = N.new("ShaderNodeMixShader"); L.new(mr.outputs[0], ms.inputs[0]); L.new(tr_.outputs[0], ms.inputs[1]); L.new(b.outputs[0], ms.inputs[2])
L.new(ms.outputs[0], N["Material Output"].inputs["Surface"])
for k, (yy, wdt) in enumerate(((538, 16), (572, 11), (612, 8))):
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=200, y_segments=2, size=1.0)
    for v in bm.verts:
        x = v.co.x * 2500; t = (v.co.y + 1) / 2
        v.co = Vector((x, yy + 6 * math.sin(x * 0.004 + k) + t * wdt, Z_PLAIN - 0.95 + 0.35 * math.sin(t * math.pi)))
    mesh_obj("surf%d" % k, bm, FOAM)
# lifeguard tower on the beach (human-scale cue at distance)
TW = flat("tower", (0.55, 0.5, 0.42), 0.7)
for dx in (-1.2, 1.2):
    for dy in (-1.2, 1.2): cyl("stilt", (18 + dx, 500 + dy, Z_PLAIN), (18 + dx * 0.8, 500 + dy * 0.8, Z_PLAIN + 3.5), 0.12, 0.1, TW, 6)
box("hut", (3.0, 3.0, 2.4), (18, 500, Z_PLAIN + 4.7), TW); box("hutroof", (4.0, 3.8, 0.25), (18, 500, Z_PLAIN + 6.0), TW, rot=(0.15, 0, 0))
# town on the plain: low concrete blocks with lit windows, olive/pine trees, street lights
BLD, N, L, b = new_mat("building"); b.inputs["Base Color"].default_value = (0.16, 0.15, 0.14, 1); b.inputs["Roughness"].default_value = 0.8
tc = N.new("ShaderNodeTexCoord"); sp_ = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sp_.inputs[0])
def op(o_, a_, b_=None):
    n_ = N.new("ShaderNodeMath"); n_.operation = o_
    for k_, x_ in enumerate((a_, b_)):
        if x_ is None: continue
        if isinstance(x_, (int, float)): n_.inputs[k_].default_value = x_
        else: L.new(x_, n_.inputs[k_])
    return n_.outputs[0]
# window grid: 3.2 m bays x 3 m floors on both facade directions; ~35% of windows lit (random per window cell)
hx = op("LESS_THAN", op("FRACT", op("DIVIDE", sp_.outputs[0], 3.2)), 0.5); hy = op("LESS_THAN", op("FRACT", op("DIVIDE", sp_.outputs[1], 3.2)), 0.5)
vz = op("LESS_THAN", op("FRACT", op("DIVIDE", sp_.outputs[2], 3.0)), 0.45)
cell = N.new("ShaderNodeCombineXYZ"); L.new(op("FLOOR", op("DIVIDE", sp_.outputs[0], 3.2)), cell.inputs[0]); L.new(op("FLOOR", op("DIVIDE", sp_.outputs[1], 3.2)), cell.inputs[1]); L.new(op("FLOOR", op("DIVIDE", sp_.outputs[2], 3.0)), cell.inputs[2])
wnz = N.new("ShaderNodeTexWhiteNoise"); wnz.noise_dimensions = "3D"; L.new(cell.outputs[0], wnz.inputs["Vector"])
lit = op("GREATER_THAN", wnz.outputs["Value"], 0.86)
win = op("MULTIPLY", op("MULTIPLY", op("MAXIMUM", hx, hy), vz), lit)
b.inputs["Emission Color"].default_value = (1.0, 0.66, 0.36, 1); L.new(op("MULTIPLY", win, 3.0), b.inputs["Emission Strength"])
TREE = flat("tree", (0.035, 0.05, 0.025), 0.85)
STADIUM_C = Vector((-62.0, 380.0, Z_PLAIN)); HALL_C = Vector((24.0, 235.0, Z_PLAIN))
def free(x, y):
    if ((x - STADIUM_C.x) / 100) ** 2 + ((y - STADIUM_C.y) / 82) ** 2 < 1: return False
    if ((x - HALL_C.x) / 50) ** 2 + ((y - HALL_C.y) / 38) ** 2 < 1: return False
    return True
tree_bm = bmesh.new(); bld_bm = bmesh.new()
for k in range(1600):
    x = random.uniform(-420, 420); y = random.uniform(90, 470)
    if y > 400 and random.random() < 0.75: continue   # keep the coast strip low and green
    if not free(x, y): continue
    if random.random() < 0.7:
        h = random.uniform(5, 11); r = h * random.uniform(0.28, 0.42)
        bmesh.ops.create_icosphere(tree_bm, subdivisions=2, radius=1.0, matrix=Matrix.Translation((x, y, Z_PLAIN + h * 0.55)) @ Matrix.Diagonal((r, r, h * 0.5, 1)))
    else:
        w = random.uniform(9, 22); d = random.uniform(9, 16); h = random.choice((4, 6, 6, 9, 9, 12))
        bmesh.ops.create_cube(bld_bm, size=1.0, matrix=Matrix.Translation((x, y, Z_PLAIN + h / 2)) @ Matrix.Rotation(random.uniform(-0.1, 0.1), 4, "Z") @ Matrix.Diagonal((w, d, h, 1)))
t_o = mesh_obj("trees", tree_bm, TREE)
d_ = t_o.modifiers.new("d", "DISPLACE"); tx = bpy.data.textures.new("tn", "CLOUDS"); tx.noise_scale = 1.5; d_.texture = tx; d_.strength = 1.2
mesh_obj("town", bld_bm, BLD, smooth=False)
SL = emitm("streetlight", (1.0, 0.62, 0.3), 120.0)
sl_bm = bmesh.new()
for x in range(-600, 601, 28):
    for y in (470.0,): bmesh.ops.create_icosphere(sl_bm, subdivisions=1, radius=0.35, matrix=Matrix.Translation((x, y, Z_PLAIN + 7)))
for y in range(120, 465, 30):
    for x in (-140.0, 25.0, 170.0): bmesh.ops.create_icosphere(sl_bm, subdivisions=1, radius=0.35, matrix=Matrix.Translation((x + 3 * math.sin(y), y, Z_PLAIN + 7)))
for x in range(-420, 421, 30):
    for y in (300.0, 180.0): bmesh.ops.create_icosphere(sl_bm, subdivisions=1, radius=0.35, matrix=Matrix.Translation((x, y + 2 * math.sin(x), Z_PLAIN + 7)))
mesh_obj("streetlights", sl_bm, SL)

# ------------------------------------------------------------------ ~300 m: football stadium (roof crown + four floodlight masts) and basketball hall
CONC = pbr("stad_conc", "concrete_wall_008", 0.12, (0.85, 0.82, 0.78))
ROOFM = flat("membrane", (0.42, 0.43, 0.44), 0.35, 0.6)
SEAT, N, L, b = new_mat("seats"); tc = N.new("ShaderNodeTexCoord"); wv = N.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 0.6; L.new(tc.outputs["Object"], wv.inputs[0])
wv.wave_profile = "SAW"
cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.05, 0.04, 0.02, 1); cr.color_ramp.elements[1].color = (0.72, 0.52, 0.03, 1); cr.color_ramp.elements[0].position = 0.3
L.new(wv.outputs["Fac"], cr.inputs[0]); L.new(cr.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.5
PITCH, N, L, b = new_mat("pitch"); tc = N.new("ShaderNodeTexCoord"); wv = N.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 0.05; wv.wave_profile = "SAW"
wv.bands_direction = "X"; L.new(tc.outputs["Object"], wv.inputs[0])
cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.interpolation = "CONSTANT"; cr.color_ramp.elements[0].color = (0.06, 0.2, 0.04, 1); cr.color_ramp.elements[1].color = (0.09, 0.27, 0.05, 1)
L.new(wv.outputs["Fac"], cr.inputs[0]); L.new(cr.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.85
def ellipse_ring(name, a0, b0, z0, a1, b1, z1, mat, seg=128, ctr=STADIUM_C):
    bm = bmesh.new(); r0 = []; r1 = []
    for k in range(seg):
        t = 2 * math.pi * k / seg
        r0.append(bm.verts.new((ctr.x + a0 * math.cos(t), ctr.y + b0 * math.sin(t), ctr.z + z0)))
        r1.append(bm.verts.new((ctr.x + a1 * math.cos(t), ctr.y + b1 * math.sin(t), ctr.z + z1)))
    for k in range(seg):
        bm.faces.new((r0[k], r0[(k + 1) % seg], r1[(k + 1) % seg], r1[k]))
    return mesh_obj(name, bm, mat)
A_O, B_O = 82.0, 64.0
ellipse_ring("stands", 58, 41, 0.5, 76, 58, 21, SEAT)
ellipse_ring("facade_out", A_O, B_O, 0, A_O, B_O, 26.8, CONC)
ellipse_ring("facade_in", 76, 58, 21, A_O, B_O, 26.8, CONC)
fin_bm = bmesh.new()
for k in range(96):
    t = 2 * math.pi * k / 96; p = STADIUM_C + Vector(((A_O + 0.8) * math.cos(t), (B_O + 0.8) * math.sin(t), 13.4)); ang = math.atan2(math.sin(t) / B_O, math.cos(t) / A_O)
    bmesh.ops.create_cube(fin_bm, size=1.0, matrix=Matrix.Translation(p) @ Matrix.Rotation(ang, 4, "Z") @ Matrix.Diagonal((1.6, 0.5, 26.8, 1)))
for k in range(72):  # radial roof trusses on top of the crown
    t = 2 * math.pi * k / 72; p0 = Vector(((A_O + 1) * math.cos(t), (B_O + 1) * math.sin(t), 28.6)); p1 = Vector((60 * math.cos(t), 43 * math.sin(t), 25.4))
    mid = STADIUM_C + (p0 + p1) / 2; dv = p1 - p0
    bmesh.ops.create_cube(fin_bm, size=1.0, matrix=Matrix.Translation(mid) @ dv.to_track_quat("X", "Z").to_matrix().to_4x4() @ Matrix.Diagonal((dv.length, 0.5, 0.9, 1)))
mesh_obj("fins", fin_bm, flat("fins", (0.5, 0.5, 0.5), 0.4, 0.7), smooth=False)
# concourse glow band on the facade
ellipse_ring("concourse", A_O + 0.05, B_O + 0.05, 9.0, A_O + 0.05, B_O + 0.05, 10.2, emitm("concourse", (1.0, 0.75, 0.45), 6.0))
# roof crown: ring canopy cantilevered inward, rising toward the pitch, white fascia
ellipse_ring("roof_top", A_O + 1, B_O + 1, 28.0, 60, 43, 25.0, ROOFM)
ellipse_ring("roof_bot", A_O + 1, B_O + 1, 26.8, 60, 43, 24.2, ROOFM)
ellipse_ring("fascia", A_O + 1, B_O + 1, 26.8, A_O + 1, B_O + 1, 28.0, ROOFM)
ellipse_ring("roof_lip", 60, 43, 24.2, 60, 43, 25.0, ROOFM)
ellipse_ring("roof_lights", 60.6, 43.6, 24.1, 61.6, 44.6, 24.25, emitm("rooflights", (0.85, 0.92, 1.0), 40.0))
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0); bmesh.ops.scale(bm, vec=(62, 44, 1), verts=bm.verts)
pt = mesh_obj("pitch", bm, PITCH, smooth=False); pt.location = STADIUM_C + Vector((0, 0, 0.3))
# four floodlight masts (lattice-like tapered pylons) with lamp banks aimed at the centre spot, cool 5600 K
LAMP = emitm("floodlamp", (0.82, 0.9, 1.0), float(os.environ.get("FLOOD", "260")))
FRAME = flat("maststeel", (0.3, 0.3, 0.3), 0.5, 1.0)
for k, ang in enumerate((40, 140, 220, 320)):
    t = math.radians(ang); base = STADIUM_C + Vector((96 * math.cos(t), 78 * math.sin(t), 0)); top = base + Vector((0, 0, 64))
    cyl("mast", base, top, 1.3, 0.55, FRAME, 10)
    to_c = (STADIUM_C - base); yaw = math.atan2(to_c.y, to_c.x)
    head = box("head", (1.2, 11.0, 6.5), top + Vector((0, 0, 3)), FRAME, rot=(0, math.radians(-25), yaw))
    for r_ in range(4):
        for c_ in range(7):
            off = Vector((0.65, -4.8 + c_ * 1.6, -2.4 + r_ * 1.6))
            off.rotate(Matrix.Rotation(math.radians(-25), 3, "Y")); off.rotate(Matrix.Rotation(yaw, 3, "Z"))
            bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=12, radius=0.55)
            o = mesh_obj("lamp", bm, LAMP, smooth=False); o.location = top + Vector((0, 0, 3)) + off
            o.rotation_euler = (0, math.radians(90 - 25), yaw)
    sd_ = bpy.data.lights.new("flood", "SPOT"); sd_.energy = float(os.environ.get("FLOODW", "7e5")); sd_.color = (0.85, 0.92, 1.0)
    sd_.spot_size = math.radians(55); sd_.spot_blend = 0.5; sd_.shadow_soft_size = 3.0
    so = link(bpy.data.objects.new("flood", sd_)); so.location = top + Vector((0, 0, 3)) + Vector((math.cos(yaw), math.sin(yaw), 0)) * 2
    so.rotation_euler = (STADIUM_C - so.location).to_track_quat("-Z", "Y").to_euler()
# basketball hall: low elliptic shell roof, glowing ribbed skylight (Maccabi Rishon), glazed base
HALLM = flat("hallroof", (0.12, 0.12, 0.13), 0.35, 0.8)
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=24, radius=1.0)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.01], context="VERTS")
bmesh.ops.scale(bm, vec=(34, 24, 14), verts=bm.verts)
hall = mesh_obj("hall", bm, HALLM); hall.location = HALL_C + Vector((0, 0, 7))
ellipse_ring("hallbase", 34, 24, 0, 34, 24, 7, emitm("hallglass", (1.0, 0.8, 0.55), 4.0), ctr=HALL_C)
ellipse_ring("hallsky", 13.2, 9.3, 7 + 12.85, 0.2, 0.2, 7 + 14.05, emitm("hallsky", (1.0, 0.86, 0.66), 9.0), ctr=HALL_C)   # glowing oculus skylight
ellipse_ring("hallband", 24.5, 17.3, 7 + 10.0, 23.5, 16.6, 7 + 10.6, emitm("hallband", (1.0, 0.8, 0.55), 5.0), ctr=HALL_C)
for k in range(0):  # (ribs removed: read as sci-fi pods)
    u = -0.8 + k * 0.2; bm = bmesh.new(); pts = []
    for j in range(25):
        t = -math.pi / 2 + math.pi * j / 24; x = u; yy = math.sqrt(max(0, 1 - x * x)) * math.sin(t); zz = math.sqrt(max(0, 1 - x * x - yy * yy))
        pts.append(Vector((x * 34.2, yy * 24.2, zz * 14.2)))
    cu = bpy.data.curves.new("rib", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.3
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for j, p in enumerate(pts): sp.points[j].co = (p.x, p.y, p.z, 1)
    ob = link(bpy.data.objects.new("rib", cu)); ob.location = hall.location; ob.data.materials.append(emitm("hallrib", (1.0, 0.8, 0.55), 6.0))

# ------------------------------------------------------------------ camera: fixed, 40 mm, eye height on the ridge
cam_d = bpy.data.cameras.new("cam"); cam = link(bpy.data.objects.new("cam", cam_d)); sc.camera = cam
cam_d.lens = float(os.environ.get("LENS", "35")); cam_d.sensor_width = 36; cam_d.sensor_fit = "HORIZONTAL"; cam_d.clip_start = 0.05; cam_d.clip_end = 40000
cam.location = (0, 0, 1.55)
PITCH_DEG = float(os.environ.get("PITCH", "-8"))
cam.rotation_euler = (math.radians(90 + PITCH_DEG), 0, 0)
dof = cam_d.dof; dof.use_dof = True; dof.aperture_blades = 0
FOCUS = {"hyper": (3.0, 16.0), "fest": (float(os.environ.get("FOCUSD", "14.3")), float(os.environ.get("FSTOP", "0.7"))), "portrait": (3.2, 0.7), "bokeh": (0.3, float(os.environ.get("FSTOP", "1.4")))}[MODE]
dof.focus_distance, dof.aperture_fstop = FOCUS
print("scene built in %.1fs" % (time.time() - T0), flush=True)
bpy.ops.render.render(write_still=True)
print("DONE", OUT, "%.1fs" % (time.time() - T0))
