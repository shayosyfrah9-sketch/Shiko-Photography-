# SHIKO WORLD 2.0 — Concept B "DEPTH OF FIELD", ROUND 3 scene (fixes from studio/critique/B-round-2.md).
# R3: backlit silhouette crowd, real stadium (2 raked tiers, cantilever roof, open end, lined pitch), surf subject + glint path,
#     portrait set at ~5.5 m in the right third lit by a 3200 K softbox, plateau ground on the portrait layer, phone camera 35 mm.
# One fixed 50 mm camera on a kurkar pine ridge looking west at the blue-gold minute (sun 2° below the sea).
# Distance layers (each object is tagged, written to AOVs m1/m2 so a layered blur composite can be built exactly
# like the web shader would): 0 sea/surf (∞) · 1 sport (stadium ~690 m) · 2 festival (meadow 26-46 m) · 3 portrait set (~9 m) · 4 pine (~3.6 m)
# Run: /tmp/claude-0/bpyenv/bin/python B2_depth_of_field.py -- VIEW OUTBASE [W H SPP]
#   VIEW = desk (50 mm, pitch -5°, 16:9) | phone (35 mm on the vertical sensor, pitch -9°)
#   writes OUTBASE.png (AgX display, all sharp = hyperfocal) and OUTBASE.exr (uncompressed multilayer: Combined + AOV m1, m2)
# CC0 Poly Haven assets: pine_sapling_small, coast_land_rocks_03, grass_medium_01, bar_chair_round_01 (models);
#   rough_linen, coast_sand_rocks_02, sparse_grass, concrete_wall_008, aerial_sand, pine_bark (textures).
import bpy, bmesh, sys, math, os, random, time
from mathutils import Vector, noise, Matrix
a = sys.argv[sys.argv.index("--") + 1:]
VIEW = a[0]; OUTB = a[1]
W = int(a[2]) if len(a) > 2 else 800; H = int(a[3]) if len(a) > 3 else 450; SPP = int(a[4]) if len(a) > 4 else 16
PH = os.environ.get("PH", "/tmp/claude-0/-home-user/2c38ec15-b058-5d59-86c9-28307ce7ab10/scratchpad/ph/")
E = lambda k, d: float(os.environ.get(k, d))
T0 = time.time(); random.seed(21)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; cy = sc.cycles
cy.device = "CPU"; cy.samples = SPP; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02; cy.use_denoising = True
try: cy.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
cy.max_bounces = 6; cy.diffuse_bounces = 3; cy.glossy_bounces = 3; cy.transmission_bounces = 4; cy.transparent_max_bounces = 10
cy.volume_bounces = 0; cy.sample_clamp_indirect = 10; cy.blur_glossy = 1.0
sc.render.resolution_x = W; sc.render.resolution_y = H
if os.environ.get("CROP"):   # test renders: x0,x1,y0,y1 as fractions (y from the bottom)
    c_ = [float(v) for v in os.environ["CROP"].split(",")]; sc.render.use_border = True; sc.render.use_crop_to_border = True
    sc.render.border_min_x, sc.render.border_max_x, sc.render.border_min_y, sc.render.border_max_y = c_
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
sc.view_settings.exposure = E("EXPO", "1.5")

LAYER = [2]
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

def link(o):
    sc.collection.objects.link(o); o["lay"] = LAYER[0]; return o

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
    new = [o for o in bpy.data.objects if o not in before]
    for o in new: o["lay"] = LAYER[0]
    return new


def smooth(t): t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)
def lin(hexs):  # sRGB hex -> linear tuple
    c = [int(hexs[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c)

# ================================================================== SKY: blue-gold minute, sun 2° below the sea horizon
# Indigo #1d2433 overhead -> dusty rose -> apricot #e9a25a band hugging the horizon (2-4% of frame height), warmer toward the sun (west, slightly north).
wd = bpy.data.worlds.new("W"); sc.world = wd; wd.use_nodes = True; wn = wd.node_tree; N = wn.nodes; L = wn.links
tc = N.new("ShaderNodeTexCoord"); nrm = N.new("ShaderNodeVectorMath"); nrm.operation = "NORMALIZE"; L.new(tc.outputs["Generated"], nrm.inputs[0])
sp = N.new("ShaderNodeSeparateXYZ"); L.new(nrm.outputs[0], sp.inputs[0])
mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -0.02; mr.inputs["From Max"].default_value = 0.6; mr.clamp = True; L.new(sp.outputs[2], mr.inputs["Value"])
cr = N.new("ShaderNodeValToRGB"); el = cr.color_ramp.elements
def stop(pos_z, col, first=False):
    t = (pos_z + 0.02) / 0.62
    e = el[0] if first else el.new(t)
    e.position = t; e.color = col + (1,)
stop(-0.02, (0.06, 0.04, 0.035), True)
el[1].position = (0.0 + 0.02) / 0.62; el[1].color = (0.62, 0.27, 0.08, 1)    # apricot at the horizon
stop(0.010, (0.52, 0.22, 0.075))
stop(0.028, (0.3, 0.14, 0.1))      # peach-rose
stop(0.06, (0.12, 0.09, 0.12))        # dusty mauve
stop(0.11, (0.04, 0.045, 0.085))       # deep blue
stop(0.20, lin("#1d2433"))           # indigo
stop(0.6, (0.006, 0.008, 0.02))
cr.color_ramp.interpolation = "B_SPLINE"
L.new(mr.outputs[0], cr.inputs[0])
# azimuth: brighter toward the sun (+y, slightly +x), dimmer behind (east)
sund = Vector((E("SUNX", "0.14"), 1.0, 0.0)).normalized()
dp = N.new("ShaderNodeVectorMath"); dp.operation = "DOT_PRODUCT"; dp.inputs[1].default_value = sund; L.new(nrm.outputs[0], dp.inputs[0])
az = N.new("ShaderNodeMapRange"); az.inputs["From Min"].default_value = -1.0; az.inputs["From Max"].default_value = 1.0; az.inputs["To Min"].default_value = 0.25; az.inputs["To Max"].default_value = 1.0; L.new(dp.outputs["Value"], az.inputs["Value"])
pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = 2.0; L.new(az.outputs[0], pw.inputs[0])
mul = N.new("ShaderNodeVectorMath"); mul.operation = "SCALE"; L.new(cr.outputs[0], mul.inputs[0]); L.new(pw.outputs[0], mul.inputs["Scale"])
dp2 = N.new("ShaderNodeVectorMath"); dp2.operation = "DOT_PRODUCT"; dp2.inputs[1].default_value = Vector((sund.x, sund.y, 0.02)).normalized(); L.new(nrm.outputs[0], dp2.inputs[0])
lob = N.new("ShaderNodeMath"); lob.operation = "POWER"; lob.inputs[1].default_value = E("LOBK", "500"); L.new(dp2.outputs["Value"], lob.inputs[0])
lob2 = N.new("ShaderNodeMath"); lob2.operation = "MULTIPLY"; lob2.inputs[1].default_value = E("LOBS", "0.7"); L.new(lob.outputs[0], lob2.inputs[0])
# afterglow core: a thin bright patch ON the horizon line where the sun went down (az +-2°, hugging the horizon, no disc)
lobn = N.new("ShaderNodeMath"); lobn.operation = "POWER"; lobn.inputs[1].default_value = E("LOBK2", "2500"); L.new(dp2.outputs["Value"], lobn.inputs[0])
elv = N.new("ShaderNodeMapRange"); elv.inputs["From Min"].default_value = E("LOBE", "0.012"); elv.inputs["From Max"].default_value = 0.0; L.new(sp.outputs[2], elv.inputs["Value"])
elv2 = N.new("ShaderNodeMath"); elv2.operation = "POWER"; elv2.inputs[1].default_value = 2.0; L.new(elv.outputs[0], elv2.inputs[0])
lobm = N.new("ShaderNodeMath"); lobm.operation = "MULTIPLY"; L.new(lobn.outputs[0], lobm.inputs[0]); L.new(elv2.outputs[0], lobm.inputs[1])
lobn2 = N.new("ShaderNodeMath"); lobn2.operation = "MULTIPLY"; lobn2.inputs[1].default_value = E("LOBS2", "11.0"); L.new(lobm.outputs[0], lobn2.inputs[0])
lobsum = N.new("ShaderNodeMath"); lobsum.operation = "ADD"; L.new(lob2.outputs[0], lobsum.inputs[0]); L.new(lobn2.outputs[0], lobsum.inputs[1])
lobc = N.new("ShaderNodeVectorMath"); lobc.operation = "SCALE"; lobc.inputs[0].default_value = (1.0, 0.5, 0.18); L.new(lobsum.outputs[0], lobc.inputs["Scale"])
mul2 = N.new("ShaderNodeVectorMath"); mul2.operation = "ADD"; L.new(mul.outputs[0], mul2.inputs[0]); L.new(lobc.outputs[0], mul2.inputs[1]); mul = mul2
bg = N["Background"]; L.new(mul.outputs[0], bg.inputs["Color"]); bg.inputs["Strength"].default_value = E("SKY", "1.0")
# illumination-only lift (non-camera rays): the open eastern twilight sky behind the camera is brighter than the
# indigo zenith seen in frame; keeps the visible sky exactly as designed
amb = N.new("ShaderNodeVectorMath"); amb.operation = "ADD"; amb.inputs[1].default_value = (0.03 * E("AMB", "1.0"), 0.036 * E("AMB", "1.0"), 0.06 * E("AMB", "1.0")); L.new(mul.outputs[0], amb.inputs[0])
bgf = N.new("ShaderNodeBackground"); L.new(amb.outputs[0], bgf.inputs["Color"]); bgf.inputs["Strength"].default_value = E("SKY", "1.0")
lp = N.new("ShaderNodeLightPath"); msw = N.new("ShaderNodeMixShader"); L.new(lp.outputs["Is Camera Ray"], msw.inputs[0])
L.new(bgf.outputs[0], msw.inputs[1]); L.new(bg.outputs[0], msw.inputs[2]); L.new(msw.outputs[0], N["World Output"].inputs["Surface"])

# coastal haze: two bounded volumes (low dense over the plain, thin above). Volume colour leans to the sky.
def haze_box(name, dens, size, loc, col):
    m, Nn, Ll, _ = new_mat(name); Nn.remove(Nn["Principled BSDF"])
    v = Nn.new("ShaderNodeVolumePrincipled"); v.inputs["Density"].default_value = dens; v.inputs["Color"].default_value = col + (1,); v.inputs["Anisotropy"].default_value = 0.6
    Ll.new(v.outputs["Volume"], Nn["Material Output"].inputs["Volume"])
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    o = mesh_obj(name, bm, m, smooth=False); o.location = loc; o.visible_shadow = False; o["lay"] = -1; return o
LAYER[0] = 1
haze_box("haze_low", E("HAZE", "0.0011"), (5000, 2600, 40), (0, 1340, -36), (0.85, 0.8, 0.85))
haze_box("haze_high", E("HAZE2", "0.0003"), (5000, 2600, 70), (0, 1340, 19), (0.85, 0.8, 0.85))
cy.volume_step_rate = 4.0; cy.volume_max_steps = 64

# ================================================================== TERRAIN
Z_PLAIN = -52.0; Z_MEADOW = E("ZMEAD", "-6.6")
def ridge_edge(x): return 5.6 + 2.0 * smooth((x - 0.8) / 2.2) * 3.0 + 0.5 * noise.noise(Vector((x * 0.25, 1.0, 0.0)))   # lip at ~5.6 m, plateau runs on to ~11 m on the right (portrait set)
def height(x, y):
    e = ridge_edge(x)
    z = 0.10 * noise.fractal(Vector((x * 0.5, y * 0.5, 0.2)), 1.0, 2.0, 4)
    meadow = Z_MEADOW - 0.25 * max(0.0, y - 30) / 20 + 0.3 * noise.fractal(Vector((x * 0.06, y * 0.06, 4.0)), 1.0, 2.0, 3)
    t = smooth((y - e) / 6.0)
    z = z + (meadow - z) * t
    z += 0.35 * noise.ridged_multi_fractal(Vector((x * 0.5, y * 0.5, 3.0)), 1.0, 2.0, 3, 0.0, 2.0) * t * (1 - t) * 4   # kurkar steps on the slope
    esc = 50.0 + 4.0 * noise.noise(Vector((x * 0.04, 7.0, 0)))
    z = z + (Z_PLAIN - z) * smooth((y - esc) / 22.0)
    return z
LAYER[0] = 2
bm = bmesh.new(); NX, NY = 280, 240; X0, X1, Y0, Y1 = -45.0, 45.0, 2.0, 90.0; vs = []
for j in range(NY + 1):
    y = Y0 + (Y1 - Y0) * ((j / NY) ** 1.35); row = []
    for i in range(NX + 1):
        x = (X0 + (X1 - X0) * i / NX) * (0.4 + 0.6 * y / Y1)
        row.append(bm.verts.new((x, y, height(x, y))))
    vs.append(row)
for j in range(NY):
    for i in range(NX): bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
tm, N, L, b = new_mat("terrain"); tc = N.new("ShaderNodeTexCoord")
rk = texset(N, L, tc.outputs["Object"], "coast_sand_rocks_02", 0.32); gr = texset(N, L, tc.outputs["Object"], "sparse_grass", 0.4)
geo = N.new("ShaderNodeNewGeometry"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sep.inputs[0])
nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.5; L.new(tc.outputs["Object"], nz.inputs["Vector"])
add = N.new("ShaderNodeMath"); add.operation = "ADD"; L.new(sep.outputs[2], add.inputs[0]); L.new(nz.outputs["Fac"], add.inputs[1])
fac = N.new("ShaderNodeMapRange"); fac.inputs["From Min"].default_value = 1.2; fac.inputs["From Max"].default_value = 1.38; L.new(add.outputs[0], fac.inputs["Value"])
def mix(a_, b_):
    m_ = N.new("ShaderNodeMixRGB"); L.new(fac.outputs[0], m_.inputs[0]); L.new(a_, m_.inputs[1]); L.new(b_, m_.inputs[2]); return m_.outputs[0]
tr_ = N.new("ShaderNodeMixRGB"); tr_.blend_type = "MULTIPLY"; tr_.inputs[0].default_value = 1; tr_.inputs[2].default_value = (1.0, 0.84, 0.64, 1); L.new(rk["diff"], tr_.inputs[1])
tg_ = N.new("ShaderNodeMixRGB"); tg_.blend_type = "MULTIPLY"; tg_.inputs[0].default_value = 1; tg_.inputs[2].default_value = (0.8, 0.74, 0.55, 1); L.new(gr["diff"], tg_.inputs[1])
L.new(mix(tr_.outputs[0], tg_.outputs[0]), b.inputs["Base Color"]); L.new(mix(rk["rough"], gr["rough"]), b.inputs["Roughness"])
nmn = N.new("ShaderNodeNormalMap"); L.new(mix(rk["nor_gl"], gr["nor_gl"]), nmn.inputs["Color"]); L.new(nmn.outputs[0], b.inputs["Normal"])
tmesh = mesh_obj("terrain", bm, tm)
bm = bmesh.new(); bm.from_mesh(tmesh.data)
near = [f for f in bm.faces if f.calc_center_median().y < ridge_edge(f.calc_center_median().x) + 1.2]
bm2 = bm.copy(); bmesh.ops.delete(bm, geom=near, context="FACES"); bm.to_mesh(tmesh.data); bm.free()
far_ = [f for f in bm2.faces if not (f.calc_center_median().y < ridge_edge(f.calc_center_median().x) + 1.2)]
bmesh.ops.delete(bm2, geom=far_, context="FACES"); LAYER[0] = 3; plat = mesh_obj("plateau", bm2, tm); LAYER[0] = 2
for p_ in plat.data.polygons: p_.use_smooth = True
# kurkar outcrops on the ridge slope + grass tufts (sharp, readable at the bottom edge in the festival state)
for (x, y, s_, rz) in ((-3.6, 6.4, 0.42, 20), (-7.5, 8.8, 0.5, -40)):
    LAYER[0] = 3 if y < ridge_edge(x) + 1.2 else 2
    for o in import_gltf(PH + "coast_land_rocks_03/coast_land_rocks_03.gltf"):
        if o.type == "MESH":
            o.location = (x, y, -0.55 * s_); o.scale = (s_, s_, s_ * 1.2); o.rotation_euler = (0, 0, math.radians(rz))
LAYER[0] = 2
grass_src = [o for o in import_gltf(PH + "grass_medium_01/grass_medium_01.gltf") if o.type == "MESH" and ("large" in o.name or "mid" in o.name or "tall" in o.name)]
for o in grass_src: o.hide_render = True; o.location = (0, -50, 0)
for k in range(900):
    y = random.uniform(4.6, 34.0); x = random.uniform(-0.42, 0.42) * y
    if 0.5 < x < 3.2 and 4.6 < y < 7.4: continue
    s = random.choice(grass_src); g = link(bpy.data.objects.new("grass", s.data)); g["lay"] = 3 if y < ridge_edge(x) + 1.2 else 2
    g.location = (x, y, height(x, y) - 0.02); g.rotation_euler = (0, 0, random.uniform(0, 6.28)); k_ = random.uniform(0.8, 1.6) * (0.6 + y / 26); g.scale = (k_, k_, k_ * random.uniform(0.9, 1.4))

# ================================================================== FESTIVAL (layer 2): 7 woven shade canopies (6-9.5 m span), string lights glowing through, 50 people
LIN_D = img(PH + "tex/rough_linen_diff_2k.jpg"); LIN_N = img(PH + "tex/rough_linen_nor_gl_2k.jpg", True)
CANCOL = [(0.42, 0.17, 0.08), (0.48, 0.33, 0.12), (0.12, 0.13, 0.22), (0.52, 0.43, 0.3), (0.42, 0.2, 0.2), (0.22, 0.24, 0.12), (0.36, 0.14, 0.07)]
def canopy_mat(i):
    # woven cotton canvas: colour x linen weave albedo, weave normal, back-lit translucency (string lights glow through)
    m, N, L, b = new_mat("canopy%d" % i); tc = N.new("ShaderNodeTexCoord")
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (7, 7, 7); L.new(tc.outputs["UV"], mp.inputs[0])
    t1 = N.new("ShaderNodeTexImage"); t1.image = LIN_D; L.new(mp.outputs[0], t1.inputs[0])
    t2 = N.new("ShaderNodeTexImage"); t2.image = LIN_N; L.new(mp.outputs[0], t2.inputs[0])
    base = CANCOL[i]
    col = N.new("ShaderNodeMixRGB"); col.blend_type = "MULTIPLY"; col.inputs[0].default_value = 1.0; col.inputs[1].default_value = tuple(min(1, c * 1.6) for c in base) + (1,); L.new(t1.outputs[0], col.inputs[2])
    out_col = col.outputs[0]
    if False:   # two block-printed cottons: faded border stripes, not neon
        sx = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["UV"], sx.inputs[0])
        wv = N.new("ShaderNodeTexWave"); wv.wave_type = "RINGS"; wv.rings_direction = "SPHERICAL"; wv.inputs["Scale"].default_value = 9.0; wv.inputs["Distortion"].default_value = 0.0
        mpc = N.new("ShaderNodeMapping"); mpc.inputs["Location"].default_value = (-0.5, -0.5, 0); L.new(tc.outputs["UV"], mpc.inputs[0]); L.new(mpc.outputs[0], wv.inputs[0])
        st = N.new("ShaderNodeMapRange"); st.inputs["From Min"].default_value = 0.7; st.inputs["From Max"].default_value = 0.85; L.new(wv.outputs["Fac"], st.inputs["Value"])
        m2 = N.new("ShaderNodeMixRGB"); m2.inputs[2].default_value = (0.62, 0.55, 0.42, 1); L.new(st.outputs[0], m2.inputs[0]); L.new(out_col, m2.inputs[1]); out_col = m2.outputs[0]
    L.new(out_col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.85; b.inputs["Sheen Weight"].default_value = 0.4
    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.6; L.new(t2.outputs[0], nm.inputs["Color"]); L.new(nm.outputs[0], b.inputs["Normal"])
    tl = N.new("ShaderNodeBsdfTranslucent"); L.new(out_col, tl.inputs["Color"])
    ms = N.new("ShaderNodeMixShader"); ms.inputs[0].default_value = 0.5
    L.new(b.outputs[0], ms.inputs[1]); L.new(tl.outputs[0], ms.inputs[2]); L.new(ms.outputs[0], N["Material Output"].inputs["Surface"])
    return m
WOOD = flat("pole_wood", (0.2, 0.14, 0.09), 0.7); ROPE = flat("rope", (0.45, 0.4, 0.33), 0.9); WIRE = flat("wire", (0.02, 0.02, 0.02), 0.5)
SBULB = emitm("stringbulb", (1.0, 0.52, 0.2), E("SBULB", "22"))
bulbs = bmesh.new()
def strand(p, q, sag, n):
    p = Vector(p); q = Vector(q); pts = [p.lerp(q, k / n) + Vector((0, 0, -4 * sag * (k / n) * (1 - k / n))) for k in range(n + 1)]
    cu = bpy.data.curves.new("strand", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.005
    s_ = cu.splines.new("POLY"); s_.points.add(len(pts) - 1)
    for k, pt in enumerate(pts): s_.points[k].co = (pt.x, pt.y, pt.z, 1)
    o = link(bpy.data.objects.new("strand", cu)); o.data.materials.append(WIRE)
    for pt in pts[1:-1]: bmesh.ops.create_icosphere(bulbs, subdivisions=1, radius=0.028, matrix=Matrix.Translation(pt - Vector((0, 0, 0.05))))
# (x, y, w, d, peak, yaw, peaks) — near ones right of centre (below the surf), far ones left-centre (over the stadium base)
# R3: tall canopies only left of centre (far); low shade sails right of centre (near) so the surf + glint stay visible above them
CAN = [(-8.0, 42.0, 7.5, 5.5, 4.6, 8, 1), (-3.4, 46.0, 9.5, 6.5, 4.8, -6, 2), (-0.6, 36.0, 6.5, 5.0, 4.2, 14, 1),
       (-5.4, 31.0, 6.0, 5.0, 4.0, 20, 1), (3.0, 29.0, 5.5, 4.5, 3.4, -18, 1), (6.4, 30.5, 5.5, 4.5, 3.3, 22, 1), (9.4, 33.0, 6.0, 5.0, 3.5, -10, 1)]
HE = 2.3; pole_tops = []
for i, (cx, cy_, w, d, pk, yaw, npk) in enumerate(CAN):
    gz = height(cx, cy_); rot = Matrix.Rotation(math.radians(yaw), 3, "Z")
    peaks = [(0.0, 0.0)] if npk == 1 else [(-0.24 * w, 0.0), (0.24 * w, 0.0)]
    bm = bmesh.new(); n = 56; uvl = bm.loops.layers.uv.new("UV"); vv = []
    for j in range(n + 1):
        row = []
        for k in range(n + 1):
            un = k / n - 0.5; vn = j / n - 0.5; x = un * w; y = vn * d; lift = 0.0
            for (px, py) in peaks:
                hw = (w / 2 - px) if x > px else (w / 2 + px); ax = abs(x - px) / hw; ay = abs(y - py) / (d / 2)
                rn = min(1.0, (ax ** 2.5 + ay ** 2.5) ** (1 / 2.5)); lift = max(lift, (pk - HE) * (1 - rn) ** 1.5)
            # gravity sag of the cloth between supports (~4% of span) + soft wrinkles
            sag = 0.04 * min(w, d) * math.sin(math.pi * (un + 0.5)) * math.sin(math.pi * (vn + 0.5)) * (1 - lift / (pk - HE))
            z = HE + lift - sag + 0.025 * noise.noise(Vector((un * 9, vn * 9, i)))
            sx = 1 - 0.1 * (1 - (2 * vn) ** 2) * abs(2 * un) ** 3; sy = 1 - 0.1 * (1 - (2 * un) ** 2) * abs(2 * vn) ** 3
            row.append(bm.verts.new(rot @ Vector((x * sx, y * sy, 0)) + Vector((cx, cy_, gz + z))))
        vv.append(row)
    for j in range(n):
        for k in range(n):
            f = bm.faces.new((vv[j][k], vv[j][k + 1], vv[j + 1][k + 1], vv[j + 1][k]))
            for lp, (jj, kk) in zip(f.loops, ((j, k), (j, k + 1), (j + 1, k + 1), (j + 1, k))): lp[uvl].uv = (kk / n, jj / n)
    o = mesh_obj("canopy%d" % i, bm, canopy_mat(i)); sd = o.modifiers.new("s", "SOLIDIFY"); sd.thickness = 0.01
    corners = [rot @ Vector((sx * w / 2, sy * d / 2, 0)) + Vector((cx, cy_, 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for c in corners:
        g = height(c.x, c.y); top = Vector((c.x, c.y, gz + HE + 0.06)); cyl("pole", Vector((c.x, c.y, g)), top, 0.045, 0.04, WOOD, 8)
        out = (c - Vector((cx, cy_, 0))).normalized() * 1.8; an = Vector((c.x + out.x, c.y + out.y, height(c.x + out.x, c.y + out.y)))
        cyl("guy", top, an, 0.007, 0.007, ROPE, 5); pole_tops.append(top)
    for (px, py) in peaks:
        pp = rot @ Vector((px, py, 0)) + Vector((cx, cy_, 0)); cyl("mast", Vector((pp.x, pp.y, gz)), Vector((pp.x, pp.y, gz + pk - 0.05)), 0.065, 0.055, WOOD, 10)
    ld = bpy.data.lights.new("canlight", "POINT"); ld.energy = E("CANW", "180"); ld.shadow_soft_size = 0.6; ld.color = (1.0, 0.55, 0.26)
    lo = link(bpy.data.objects.new("canlight", ld)); lo.location = (cx, cy_, gz + 1.6)
    # festoon strands *under* the cloth so the bulbs glow through it
    strand(corners[0] + Vector((0, 0, gz + 2.05)), corners[2] + Vector((0, 0, gz + 2.05)), 0.25, 22)
    strand(corners[1] + Vector((0, 0, gz + 2.05)), corners[3] + Vector((0, 0, gz + 2.05)), 0.25, 22)
order = sorted(range(len(pole_tops)), key=lambda k: pole_tops[k].x)
for k in range(0, len(order) - 3, 2):
    p, q = pole_tops[order[k]], pole_tops[order[k + 3]]
    if (p - q).length < 13: strand(p, q, 0.45, int((p - q).length * 2.4))
mo = mesh_obj("bulbs", bulbs, SBULB); mo.visible_shadow = False

# people (R3): BACKLIT SILHOUETTES — near-black matte bodies (albedo ~0.015) with a velvet sheen lobe so the warm
# string lights / canopy glow behind them draw a ~2700 K rim. Varied clothing outlines (dresses, loose shirts, shorts),
# hats / caps / buns / long hair, raised phones (lit screens), bottles. 60-100 figures in clusters; arms up <= 15%.
SIL, N, L, b = new_mat("silhouette")
b.inputs["Base Color"].default_value = (0.005, 0.0045, 0.004, 1); b.inputs["Roughness"].default_value = 0.6
b.inputs["Sheen Weight"].default_value = E("SHEEN", "0.6"); b.inputs["Sheen Roughness"].default_value = 0.2; b.inputs["Sheen Tint"].default_value = (1.0, 0.62, 0.34, 1)
b.inputs["Specular IOR Level"].default_value = 0.15
lw_ = N.new("ShaderNodeLayerWeight"); lw_.inputs["Blend"].default_value = E("RIMB", "0.12")
rimc = N.new("ShaderNodeMath"); rimc.operation = "POWER"; rimc.inputs[1].default_value = 3.0; L.new(lw_.outputs["Facing"], rimc.inputs[0])
rims = N.new("ShaderNodeMath"); rims.operation = "MULTIPLY"; rims.inputs[1].default_value = E("RIM", "0.0"); L.new(rimc.outputs[0], rims.inputs[0])
b.inputs["Emission Color"].default_value = (1.0, 0.56, 0.24, 1); L.new(rims.outputs[0], b.inputs["Emission Strength"])
SCREEN = emitm("phonescreen", (0.75, 0.85, 1.0), E("SCR", "6"))
POSES = {   # hand/elbow joints, metres, body faces +y (toward the stage, away from the camera)
    "up2":   dict(elL=(-0.32, 0.02, 1.68), haL=(-0.24, 0.06, 1.95), elR=(0.32, 0.0, 1.66), haR=(0.22, 0.05, 1.93)),
    "up1":   dict(elL=(-0.22, 0.04, 1.13), haL=(-0.23, 0.08, 0.88), elR=(0.33, 0.0, 1.68), haR=(0.27, 0.07, 1.97)),
    "down":  dict(elL=(-0.21, 0.03, 1.13), haL=(-0.22, 0.06, 0.88), elR=(0.21, 0.03, 1.13), haR=(0.22, 0.06, 0.88)),
    "phone": dict(elL=(-0.2, 0.18, 1.16), haL=(-0.05, 0.3, 1.44), elR=(0.2, 0.2, 1.18), haR=(0.06, 0.31, 1.45)),
    "drink": dict(elL=(-0.21, 0.03, 1.13), haL=(-0.22, 0.06, 0.88), elR=(0.24, 0.12, 1.12), haR=(0.1, 0.12, 1.5)),
    "hips":  dict(elL=(-0.33, -0.02, 1.14), haL=(-0.17, 0.0, 0.98), elR=(0.33, -0.02, 1.14), haR=(0.17, 0.0, 0.98)),
    "walk":  dict(elL=(-0.2, 0.1, 1.13), haL=(-0.2, 0.2, 0.9), elR=(0.2, -0.1, 1.13), haR=(0.2, -0.18, 0.9)),
    "talk":  dict(elL=(-0.21, 0.03, 1.13), haL=(-0.22, 0.06, 0.88), elR=(0.26, 0.15, 1.15), haR=(0.2, 0.38, 1.2)),
}
POSE_BAG = ["up2"] * 4 + ["up1"] * 7 + ["down"] * 30 + ["phone"] * 12 + ["drink"] * 10 + ["hips"] * 12 + ["walk"] * 12 + ["talk"] * 13
def ellip(name, c, r, sc_, parent):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=r); bmesh.ops.scale(bm, vec=sc_, verts=bm.verts)
    o = mesh_obj(name, bm, SIL); o.parent = parent; o.location = c; return o
def person(loc, yaw, h=1.75, pose="down"):
    s = h / 1.75; fem = random.random() < 0.5
    J = {"pel": (0, 0, 0.96), "spn": (0, 0.01, 1.18), "chs": (0, 0.0, 1.36), "nck": (0, 0, 1.5), "hd": (0, 0, 1.56),
         "shL": (-0.18 if not fem else -0.16, 0, 1.42), "shR": (0.18 if not fem else 0.16, 0, 1.42), "hpL": (-0.095, 0, 0.93), "hpR": (0.095, 0, 0.93)}
    st = 0.28 if pose == "walk" else 0.12
    stepL = random.uniform(-st, st); stepR = -stepL * random.uniform(0.3, 1.0); bend = random.uniform(0.0, 0.08)
    J.update(knL=(-0.1, 0.03 + stepL * 0.5, 0.5 + bend), knR=(0.1, 0.03 + stepR * 0.5, 0.5), ftL=(-0.12, stepL, 0.05), ftR=(0.12, stepR, 0.05))
    J.update(POSES[pose])
    loose = random.random() < 0.35
    R = {"pel": 0.14, "spn": 0.12 + 0.03 * loose, "chs": 0.15 + 0.035 * loose, "nck": 0.05, "hd": 0.05, "shL": 0.055, "shR": 0.055, "elL": 0.042, "elR": 0.042, "haL": 0.034, "haR": 0.034,
         "hpL": 0.08, "hpR": 0.08, "knL": 0.055, "knR": 0.055, "ftL": 0.045, "ftR": 0.045}
    Ed = [("pel", "spn"), ("spn", "chs"), ("chs", "nck"), ("nck", "hd"), ("chs", "shL"), ("chs", "shR"), ("shL", "elL"), ("elL", "haL"), ("shR", "elR"), ("elR", "haR"),
          ("pel", "hpL"), ("pel", "hpR"), ("hpL", "knL"), ("knL", "ftL"), ("hpR", "knR"), ("knR", "ftR")]
    keys = list(J.keys()); me = bpy.data.meshes.new("p"); sway = random.uniform(-0.05, 0.05)
    me.from_pydata([(Vector(J[k]) + Vector((sway * J[k][2], 0, 0))) * s for k in keys], [(keys.index(x), keys.index(y)) for x, y in Ed], [])
    o = link(bpy.data.objects.new("person", me)); sk_ = o.modifiers.new("skin", "SKIN"); sk_.use_smooth_shade = True
    for k, sv in zip(keys, me.skin_vertices[0].data):
        sv.radius = (R[k] * s * (1.12 if k in ("chs", "pel") else 1.0), R[k] * s * (0.72 if k in ("chs", "pel", "spn") else 1.0))
    me.skin_vertices[0].data[0].use_root = True
    sub = o.modifiers.new("sub", "SUBSURF"); sub.levels = 1; sub.render_levels = 1
    o.data.materials.append(SIL); o.location = loc; o.rotation_euler = (0, 0, yaw)
    hx = sway * 1.62 * s
    ellip("head", (hx, 0.0, 1.63 * s), 0.1 * s, (0.86, 1.0, 1.12), o)
    hair = random.choice(("short", "short", "long", "bun", "cap", "hat", "curly") if fem else ("short", "short", "short", "cap", "cap", "hat", "curly", "bald"))
    if hair == "long": ellip("hair", (hx, -0.06 * s, 1.47 * s), 0.1 * s, (1.2, 0.55, 2.0), o)
    if hair == "bun": ellip("hair", (hx, -0.07 * s, 1.75 * s), 0.055 * s, (1, 1, 1), o)
    if hair == "curly": ellip("hair", (hx, -0.01 * s, 1.68 * s), 0.125 * s, (1.05, 1.05, 0.9), o)
    if hair == "cap":
        ellip("hair", (hx, 0.0, 1.69 * s), 0.1 * s, (0.95, 1.05, 0.55), o); ellip("brim", (hx, 0.09 * s, 1.69 * s), 0.07 * s, (0.9, 1.1, 0.12), o)
    if hair == "hat": ellip("brim", (hx, 0.0, 1.7 * s), 0.2 * s, (1.0, 1.0, 0.06), o); ellip("crown", (hx, 0.0, 1.74 * s), 0.09 * s, (1, 1, 0.75), o)
    if fem and random.random() < 0.45:   # dress / skirt outline: flared cone from waist to knee
        bm = bmesh.new(); L_ = random.uniform(0.42, 0.6)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=14, radius1=random.uniform(0.25, 0.34) * s, radius2=0.15 * s, depth=L_ * s,
                              matrix=Matrix.Translation((0, 0, (1.02 - L_ / 2) * s)))
        dr = mesh_obj("dress", bm, SIL); dr.parent = o
    elif random.random() < 0.5:          # shorts: wider at the thigh
        for sx in (-1, 1):
            bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.1 * s, radius2=0.09 * s, depth=0.3 * s, matrix=Matrix.Translation((sx * 0.1 * s, 0, 0.78 * s)))
            sh_ = mesh_obj("shorts", bm, SIL); sh_.parent = o
    ha = Vector(J["haR"]) * s + Vector((hx * 0.9, 0, 0))
    if pose == "phone":
        ph_ = box("phone", (0.075 * s, 0.012, 0.15 * s), (0.0, 0.31 * s, 1.47 * s), SIL); ph_.parent = o
        sc_ = box("screen", (0.065 * s, 0.002, 0.135 * s), (0.0, 0.302 * s, 1.47 * s), SCREEN); sc_.parent = o; sc_.visible_shadow = False
    if pose in ("drink", "down") and random.random() < 0.4:
        bt = cyl("bottle", ha + Vector((0, 0.02, -0.12)), ha + Vector((0, 0.02, 0.1)), 0.035 * s, 0.03 * s, SIL, 8); bt.parent = o; bt.location = bt.location
    return o
# clusters (not a grid): groups around the canopies and an open dance floor toward the stage (far, centre-left)
DJ = Vector((-1.0, 52.0, 0)); NP = 0; placed = []
CLU = [(-7.0, 41.0, 2.2, 12), (-3.0, 44.5, 2.6, 16), (-0.8, 36.5, 2.0, 10), (-5.0, 31.5, 1.6, 7), (2.6, 33.0, 1.8, 8), (3.4, 29.5, 1.3, 5),
       (6.8, 31.0, 1.5, 7), (9.4, 34.0, 1.6, 6), (1.2, 40.5, 2.2, 10), (-9.6, 34.0, 1.4, 4), (5.0, 39.0, 1.6, 6)]
for (cx_, cy2, rad, n_) in CLU:
    k_ = 0
    for _ in range(400):
        if k_ >= n_: break
        x = random.gauss(cx_, rad * 0.6); y = random.gauss(cy2, rad * 0.6)
        if y < 28.6 or any((Vector((x, y)) - q).length < 0.5 for q in placed): continue
        placed.append(Vector((x, y))); k_ += 1; NP += 1
        pose = random.choice(POSE_BAG)
        yaw = math.atan2(-(DJ.x - x), DJ.y - y) + random.uniform(-0.8, 0.8) + (math.pi if random.random() < 0.15 else 0)
        h = min(1.95, max(1.55, random.gauss(1.73, 0.09)))
        person((x, y, height(x, y)), yaw, h, pose)
print("people", NP)
# a few Aleppo pines (CC0 sapling meshes scaled to 9-12 m) at the escarpment edge as natural framing
saps = [o for o in import_gltf(PH + "pine_sapling_small/pine_sapling_small.gltf") if o.type == "MESH"]
for o in saps: o.hide_render = True
for (x, y, s_, k) in ((-17.0, 52.0, 8.5, 0), (-13.0, 57.0, 7.0, 1), (16.5, 49.0, 7.5, 2)):
    g = link(bpy.data.objects.new("pine", saps[k].data)); g.location = (x, y, height(x, y) - 0.2); g.scale = (s_, s_, s_); g.rotation_euler = (0, 0, random.uniform(0, 6))

# ================================================================== SPORT (layer 1): coastal plain + a Bloomfield-like football ground
LAYER[0] = 1
def coast_x(y): return E("COAST0", "30.0") - 0.2 * (y - 400.0)   # land where x < coast_x(y); R3: surf zone ~400-500 m out, right of centre
PL, N, L, b = new_mat("plain"); tc = N.new("ShaderNodeTexCoord")
nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.012; nz.inputs["Detail"].default_value = 8; L.new(tc.outputs["Object"], nz.inputs["Vector"])
cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.035, 0.04, 0.03, 1); cr.color_ramp.elements[1].color = (0.13, 0.11, 0.08, 1)
L.new(nz.outputs["Fac"], cr.inputs[0]); L.new(cr.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.95
SAND = pbr("sand", "aerial_sand", 0.05, (1.0, 0.9, 0.76), 0.0, 0.5)
bm = bmesh.new(); vv = []; NXp, NYp = 160, 120
for j in range(NYp + 1):
    y = 50 + 1400 * (j / NYp) ** 1.3; row = []
    for i in range(NXp + 1):
        x = -1600 + 3200 * i / NXp; d = x - coast_x(y)      # d < 0: land
        z = Z_PLAIN + 0.8 * noise.fractal(Vector((x * 0.006, y * 0.006, 2)), 1.0, 2.0, 3) * smooth(-d / 60)
        z -= 1.6 * smooth((d + 45) / 45)                   # beach slopes into the sea
        row.append(bm.verts.new((x, y, z)))
    vv.append(row)
for j in range(NYp):
    for i in range(NXp): bm.faces.new((vv[j][i], vv[j][i + 1], vv[j + 1][i + 1], vv[j + 1][i]))
pl = mesh_obj("plain", bm, PL); pl.data.materials.append(SAND)
for p in pl.data.polygons:
    c = p.center; p.material_index = 1 if c.x - coast_x(c.y) > -45 else 0

# R3 STADIUM (Bloomfield-like, seen along its length): pitch 68 x 105 m with white lines, OPEN near end (low opaque wall + adboards),
# two raked tiers (~32°) on both long sides and the far end, a cantilever roof over the WEST long side only (cable-stayed),
# crowd speckle in the stands (1-2 px warm/cool dots), four lattice floodlight masts throwing pools on the grass.
STC = Vector((E("STX", "-118.0"), E("STY", "715.0"), Z_PLAIN))
CONC = pbr("stad_conc", "concrete_wall_008", 0.12, (0.3, 0.29, 0.28))
STEEL = flat("steel", (0.5, 0.51, 0.52), 0.4, 0.9)
ROOFM = flat("roofsheet", (0.2, 0.21, 0.22), 0.5, 0.4)
SEAT, N, L, b = new_mat("seats_crowd"); tc = N.new("ShaderNodeTexCoord")
vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = E("CROWDS", "1.6"); L.new(tc.outputs["Object"], vo.inputs["Vector"])
sepc = N.new("ShaderNodeSeparateColor"); L.new(vo.outputs["Color"], sepc.inputs[0])
occ_ = N.new("ShaderNodeMath"); occ_.operation = "LESS_THAN"; occ_.inputs[1].default_value = E("CROWDF", "0.62"); L.new(sepc.outputs[0], occ_.inputs[0])   # ~62% of seats taken
pal = N.new("ShaderNodeValToRGB"); pe = pal.color_ramp.elements; pal.color_ramp.interpolation = "CONSTANT"
pe[0].position = 0.0; pe[0].color = (0.3, 0.23, 0.04, 1); pe[1].position = 0.85; pe[1].color = (0.32, 0.31, 0.29, 1)
for pos_, c_ in ((0.18, (0.05, 0.08, 0.2)), (0.32, (0.02, 0.02, 0.02)), (0.45, (0.35, 0.18, 0.1)), (0.6, (0.12, 0.12, 0.13)), (0.72, (0.28, 0.21, 0.03))):
    e_ = pal.color_ramp.elements.new(pos_); e_.color = c_ + (1,)
L.new(sepc.outputs[1], pal.inputs[0])
mxs = N.new("ShaderNodeMixRGB"); mxs.inputs[1].default_value = (0.02, 0.03, 0.05, 1); L.new(occ_.outputs[0], mxs.inputs[0]); L.new(pal.outputs[0], mxs.inputs[2])
L.new(mxs.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.7
# a few phone screens / camera flashes in the crowd (tiny emissive dots)
fl = N.new("ShaderNodeMath"); fl.operation = "GREATER_THAN"; fl.inputs[1].default_value = E("FLASHT", "0.996"); L.new(sepc.outputs[2], fl.inputs[0])
fl2 = N.new("ShaderNodeMath"); fl2.operation = "MULTIPLY"; fl2.inputs[1].default_value = E("FLASH", "3"); L.new(fl.outputs[0], fl2.inputs[0])
b.inputs["Emission Color"].default_value = (0.8, 0.88, 1.0, 1); L.new(fl2.outputs[0], b.inputs["Emission Strength"])
PITCHM, N, L, b = new_mat("pitch"); tc = N.new("ShaderNodeTexCoord"); wv = N.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 0.05; wv.wave_profile = "SAW"; wv.bands_direction = "Y"
L.new(tc.outputs["Object"], wv.inputs[0]); cr = N.new("ShaderNodeValToRGB"); cr.color_ramp.interpolation = "CONSTANT"; cr.color_ramp.elements[0].color = (0.04, 0.15, 0.03, 1); cr.color_ramp.elements[1].color = (0.065, 0.22, 0.04, 1)
L.new(wv.outputs["Fac"], cr.inputs[0]); L.new(cr.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.85
LINEM = flat("pitchline", (0.75, 0.75, 0.72), 0.8)
def quad(bm_, a, b_, c, d_):
    bm_.faces.new([bm_.verts.new(STC + Vector(p)) for p in (a, b_, c, d_)])
def slab(name, x0, x1, y0, y1, z0, z1, mat, th=0.6, axis="y"):
    """sloped plate rising from edge (.., z0) to (.., z1); axis = direction of the rise"""
    bm = bmesh.new()
    if axis == "y": P_ = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z1), (x0, y1, z1)]
    else:           P_ = [(x0, y0, z0), (x0, y1, z0), (x1, y1, z1), (x1, y0, z1)]
    top = [bm.verts.new(STC + Vector(p)) for p in P_]; bot = [bm.verts.new(STC + Vector(p) - Vector((0, 0, th))) for p in P_]
    bm.faces.new(top); bm.faces.new(bot[::-1])
    for k in range(4): bm.faces.new((top[k], bot[k], bot[(k + 1) % 4], top[(k + 1) % 4]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return mesh_obj(name, bm, mat, smooth=False)
# pitch + apron
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0); bmesh.ops.scale(bm, vec=(42, 62, 1), verts=bm.verts)
pt = mesh_obj("pitch", bm, PITCHM, smooth=False); pt.location = STC + Vector((0, 0, 0.15))
# white lines (0.3 m: slightly wider than the real 0.12 m so they survive at ~700 m / 1600 px)
lb = bmesh.new(); LW_ = 0.3; Z_ = 0.2
def seg(p0, p1):
    p0 = Vector((p0[0], p0[1], Z_)); p1 = Vector((p1[0], p1[1], Z_)); d_ = (p1 - p0).normalized(); n_ = Vector((-d_.y, d_.x, 0)) * LW_ / 2
    quad(lb, p0 - n_, p1 - n_, p1 + n_, p0 + n_)
HX, HY = 34.0, 52.5
for (a_, b2) in (((-HX, -HY), (HX, -HY)), ((HX, -HY), (HX, HY)), ((HX, HY), (-HX, HY)), ((-HX, HY), (-HX, -HY)), ((-HX, 0), (HX, 0))): seg(a_, b2)
for sy in (-1, 1):
    for (a_, b2) in (((-20.16, sy * HY), (-20.16, sy * (HY - 16.5))), ((-20.16, sy * (HY - 16.5)), (20.16, sy * (HY - 16.5))), ((20.16, sy * (HY - 16.5)), (20.16, sy * HY)),
                     ((-9.16, sy * HY), (-9.16, sy * (HY - 5.5))), ((-9.16, sy * (HY - 5.5)), (9.16, sy * (HY - 5.5))), ((9.16, sy * (HY - 5.5)), (9.16, sy * HY))): seg(a_, b2)
for k in range(48):
    a0 = k / 48 * 6.283; a1 = (k + 1) / 48 * 6.283; seg((9.15 * math.cos(a0), 9.15 * math.sin(a0)), (9.15 * math.cos(a1), 9.15 * math.sin(a1)))
mesh_obj("lines", lb, LINEM, smooth=False)
for sy in (-1, 1):   # goals
    for sx in (-1, 1): cyl("post", STC + Vector((sx * 3.66, sy * HY, 0)), STC + Vector((sx * 3.66, sy * HY, 2.44)), 0.07, 0.07, LINEM, 6)
    cyl("bar", STC + Vector((-3.66, sy * HY, 2.44)), STC + Vector((3.66, sy * HY, 2.44)), 0.07, 0.07, LINEM, 6)
# LONG SIDES: lower tier (x 39->53, z 1->10, ~33°), concourse, upper tier (x 56->70, z 13->22), opaque concrete back wall
for sx in (-1, 1):
    slab("lower_tier", sx * 39, sx * 53, -56, 56, 1.0, 10.0, SEAT, 1.2, axis="x")
    slab("concourse", sx * 53, sx * 56, -56, 56, 10.0, 10.6, CONC, 1.6, axis="x")
    slab("upper_tier", sx * 56, sx * 70, -56, 56, 12.5, 22.0, SEAT, 1.2, axis="x")
    box("back_wall", (1.2, 114, 23.0), STC + Vector((sx * 71, 0, 11.5)), CONC)
    box("concourse_glow", (0.2, 110, 1.6), STC + Vector((sx * 71.65, 0, 10.6)), emitm("glaze", (1.0, 0.72, 0.42), E("GLAZE", "2.5")))
    for y in range(-54, 55, 6): box("fin", (1.0, 0.6, 23.0), STC + Vector((sx * 72.0, y, 11.5)), CONC)
    for y in (-55.0, -40.0, -25.0):     # raker columns under the tiers (seen through the open end)
        for xx, zz in ((47, 6.5), (63, 18.5)): cyl("raker", STC + Vector((sx * xx, y, 0)), STC + Vector((sx * xx, y, zz)), 0.5, 0.5, CONC, 8)
    box("front_wall", (0.5, 112, 1.3), STC + Vector((sx * 38.6, 0, 0.65)), CONC)
    box("side_wall", (33, 1.2, 23.0), STC + Vector((sx * 55, 56.6, 11.5)), CONC)   # far corner closed; near end open (tier profile visible)
# FAR END: two tiers rising away (+y); NEAR END: open, only a low opaque wall with adboards
slab("end_lower", -38, 38, 58, 70, 1.0, 9.0, SEAT, 1.2)
slab("end_upper", -38, 38, 73, 84, 11.5, 19.0, SEAT, 1.2)
box("end_back", (78, 1.2, 21), STC + Vector((0, 85, 10.5)), CONC)
box("near_wall", (78, 0.6, 1.4), STC + Vector((0, -58.5, 0.7)), CONC)
box("adboard", (64, 0.15, 0.9), STC + Vector((0, -57.6, 0.6)), emitm("adboard", (0.85, 0.72, 0.35), E("ADB", "1.5")))
# CANTILEVER ROOF over the WEST long side, hung from masts behind the back wall by tie rods (cable-stayed); underside lit
roof = slab("roof_w", -73, -36, -58, 58, 29.0, 26.0, ROOFM, 0.9, axis="x")
truss = bmesh.new()
def bar(p0, p1, r):
    p0 = STC + Vector(p0); p1 = STC + Vector(p1); d_ = p1 - p0
    bmesh.ops.create_cone(truss, cap_ends=True, segments=6, radius1=r, radius2=r, depth=d_.length,
                          matrix=Matrix.Translation((p0 + p1) / 2) @ d_.to_track_quat("Z", "Y").to_matrix().to_4x4())
for k in range(8):
    y = -52 + k * 14.86
    bar((-76, y, 0), (-76, y, 44), 0.55); bar((-76, y, 43), (-36.5, y, 26.2), 0.12); bar((-76, y, 43), (-55, y, 28.0), 0.1); bar((-76, y, 38), (-90, y, 0), 0.12)
for z_ in (26.0, 24.4): bar((-36.4, -58, z_), (-36.4, 58, z_), 0.22)
for k in range(29): y = -58 + k * 4.0; bar((-36.4, y, 26.0), (-36.4, y + 2, 24.4), 0.07); bar((-36.4, y + 2, 24.4), (-36.4, y + 4, 26.0), 0.07)
mesh_obj("truss", truss, STEEL, smooth=False)
# east side: lighter roof on columns (lower), far end open to the sky
slab("roof_e", 74, 50, -58, 58, 25.5, 24.0, ROOFM, 0.5, axis="x")
for y in range(-56, 57, 14): cyl("ecol", STC + Vector((72, y, 0)), STC + Vector((72, y, 25.5)), 0.4, 0.4, STEEL, 8)
# FLOODLIGHT MASTS (lattice, 58 m) at the four corners; spots aimed at the four quarters -> pools on the grass
LAMP = emitm("floodlamp", (0.86, 0.92, 1.0), E("FLOOD", "120"))
latt = bmesh.new()
def lbar(p0, p1, r):
    d_ = p1 - p0; bmesh.ops.create_cone(latt, cap_ends=True, segments=5, radius1=r, radius2=r, depth=d_.length, matrix=Matrix.Translation((p0 + p1) / 2) @ d_.to_track_quat("Z", "Y").to_matrix().to_4x4())
for (mx, my) in ((-62, -66), (62, -66), (-62, 72), (62, 72)):
    base = STC + Vector((mx, my, 0)); Hm = 58.0
    legs = [Vector((sx, sy, 0)) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    def at(lg, z): w_ = 2.4 - 1.5 * z / Hm; return base + Vector((lg.x * w_, lg.y * w_, z))
    for lg in legs: lbar(at(lg, 0), at(lg, Hm), 0.22)
    for z in range(0, int(Hm), 5):
        for k in range(4):
            lbar(at(legs[k], z), at(legs[(k + 1) % 4], z + 5), 0.08); lbar(at(legs[k], z + 5), at(legs[(k + 1) % 4], z + 5), 0.07)
    toc = (STC - base); yaw = math.atan2(toc.y, toc.x); head_c = base + Vector((0, 0, Hm + 3.5))
    hd = box("mhead", (1.0, 11.0, 6.0), head_c, STEEL, rot=(0, math.radians(-28), yaw))
    for r_ in range(4):
        for c_ in range(7):
            off = Vector((0.55, -4.6 + c_ * 1.53, -2.1 + r_ * 1.4)); off.rotate(Matrix.Rotation(math.radians(-28), 3, "Y")); off.rotate(Matrix.Rotation(yaw, 3, "Z"))
            bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, segments=10, radius=0.5)
            o = mesh_obj("lamp", bm, LAMP, smooth=False); o.location = head_c + off; o.rotation_euler = (0, math.radians(90 - 28), yaw); o.visible_shadow = False
    for (qx, qy) in ((0.35, 0.3), (0.1, -0.15)):   # two spot groups per mast: a near-quarter pool + a centre pool
        sl = bpy.data.lights.new("flood", "SPOT"); sl.energy = E("FLOODW", "5.0e5"); sl.color = (0.85, 0.91, 1.0); sl.spot_size = math.radians(30); sl.spot_blend = 0.5; sl.shadow_soft_size = 3.0
        so = link(bpy.data.objects.new("flood", sl)); so.location = head_c + Vector((math.cos(yaw), math.sin(yaw), 0)) * 1.5
        tgt = STC + Vector((mx * qx, my * qy, 0)); so.rotation_euler = (tgt - so.location).to_track_quat("-Z", "Y").to_euler()
mesh_obj("masts", latt, STEEL, smooth=False)

# ================================================================== SEA (layer 0, R3): glossy sea with wind ripples stretched across the view
# (crests run left-right) so the apricot glow near the horizon smears into a vertical GLINT PATH; 4 rows of white water
# (opaque core, broken edges, 10-14 m deep so each row is >= 3 px tall at ~450 m); 2 riders on a wave shoulder + 2 in the line-up.
LAYER[0] = 0
SEA, N, L, b = new_mat("sea"); b.inputs["Base Color"].default_value = (0.006, 0.02, 0.028, 1); b.inputs["Roughness"].default_value = E("SEAR", "0.09"); b.inputs["IOR"].default_value = 1.33
tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.03, E("SEAY", "0.9"), 0.1); L.new(tc.outputs["Object"], mp.inputs[0])
nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 10; L.new(mp.outputs[0], nz.inputs["Vector"])
bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = E("SEAB", "0.3"); L.new(nz.outputs["Fac"], bp.inputs["Height"]); L.new(bp.outputs[0], b.inputs["Normal"])
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=4, y_segments=4, size=1.0)
for v in bm.verts: v.co = Vector((v.co.x * 30000, 15000 + v.co.y * 15000, Z_PLAIN - 1.25))
mesh_obj("sea", bm, SEA, smooth=False)
FOAM, N, L, b = new_mat("foam"); b.inputs["Base Color"].default_value = (0.92, 0.92, 0.93, 1); b.inputs["Roughness"].default_value = 0.6
b.inputs["Emission Color"].default_value = (0.85, 0.8, 0.82, 1); b.inputs["Emission Strength"].default_value = E("FOAMEM", "0.1")   # sky-lit foam (open sky dome above it)
tc = N.new("ShaderNodeTexCoord"); nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.12; nz.inputs["Detail"].default_value = 12; nz.inputs["Roughness"].default_value = 0.65
L.new(tc.outputs["Object"], nz.inputs[0])
uvs = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["UV"], uvs.inputs[0])
edge = N.new("ShaderNodeMath"); edge.operation = "PINGPONG"; edge.inputs[1].default_value = 0.5; L.new(uvs.outputs[1], edge.inputs[0])
eg = N.new("ShaderNodeMapRange"); eg.inputs["From Min"].default_value = 0.0; eg.inputs["From Max"].default_value = 0.5; L.new(edge.outputs[0], eg.inputs["Value"])
ends = N.new("ShaderNodeMath"); ends.operation = "PINGPONG"; ends.inputs[1].default_value = 0.5; L.new(uvs.outputs[0], ends.inputs[0])
endf = N.new("ShaderNodeMapRange"); endf.inputs["From Min"].default_value = 0.0; endf.inputs["From Max"].default_value = 0.2; L.new(ends.outputs[0], endf.inputs["Value"])
eg3 = N.new("ShaderNodeMath"); eg3.operation = "MULTIPLY"; eg3.inputs[1].default_value = 0.65; L.new(eg.outputs[0], eg3.inputs[0]); eg = eg3
eg2 = N.new("ShaderNodeMath"); eg2.operation = "MULTIPLY"; L.new(eg.outputs[0], eg2.inputs[0]); L.new(endf.outputs[0], eg2.inputs[1])
nzw = N.new("ShaderNodeMath"); nzw.operation = "MULTIPLY"; nzw.inputs[1].default_value = 1.5; L.new(nz.outputs["Fac"], nzw.inputs[0])
ad = N.new("ShaderNodeMath"); ad.operation = "ADD"; L.new(eg2.outputs[0], ad.inputs[0]); L.new(nzw.outputs[0], ad.inputs[1])
mr = N.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.98; mr.inputs["From Max"].default_value = 1.12; L.new(ad.outputs[0], mr.inputs["Value"])
trb = N.new("ShaderNodeBsdfTransparent"); ms = N.new("ShaderNodeMixShader"); L.new(mr.outputs[0], ms.inputs[0]); L.new(trb.outputs[0], ms.inputs[1]); L.new(b.outputs[0], ms.inputs[2])
L.new(ms.outputs[0], N["Material Output"].inputs["Surface"])
cdir = Vector((-0.2, 1.0, 0)).normalized(); seaward = Vector((cdir.y, -cdir.x, 0))
if seaward.x < 0: seaward = -seaward
ROWS = ((10, 9), (27, 10), (47, 8), (70, 7))
for k, (off, wdt) in enumerate(ROWS):
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UV"); rows = []
    for j in range(5):
        row = []
        for i in range(81):
            yy = 365 + i * 3.5; wob = 2.5 * math.sin(yy * 0.017 + k * 1.7) + 1.2 * math.sin(yy * 0.05 + k)
            base = Vector((coast_x(yy), yy, 0)) + seaward * (off + wob + wdt * (j / 4))
            lip = 0.9 * math.exp(-((j - 1) / 1.0) ** 2) * (1.0 + 0.4 * (k == 1))      # breaking lip near the seaward edge
            row.append(bm.verts.new((base.x, base.y, Z_PLAIN - 1.2 + lip)))
        rows.append(row)
    for j in range(4):
        for i in range(80):
            f = bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
            for lp, (jj, ii) in zip(f.loops, ((j, i), (j, i + 1), (j + 1, i + 1), (j + 1, i))): lp[uvl].uv = (ii / 80, jj / 4)
    mesh_obj("whitewater%d" % k, bm, FOAM)
WETS = flat("wetsuit", (0.012, 0.012, 0.014), 0.35); BOARD = flat("board", (0.8, 0.78, 0.72), 0.3)
def surfer(p, mode, yaw):
    s = 1.0
    o = box("board", (2.1, 0.55, 0.08), p + Vector((0, 0, 0.05)), BOARD, rot=(0, 0, yaw))
    fw = Vector((math.cos(yaw), math.sin(yaw), 0)); sd = Vector((-fw.y, fw.x, 0))
    if mode == "ride":    # crouched rider, arms out
        cyl("sbody", p + Vector((0, 0, 0.1)), p + Vector((0, 0, 0.75)) + fw * 0.1, 0.13, 0.13, WETS, 8)
        cyl("sleg", p + fw * 0.35 + Vector((0, 0, 0.08)), p + Vector((0, 0, 0.8)), 0.08, 0.08, WETS, 6); cyl("sleg", p - fw * 0.35 + Vector((0, 0, 0.08)), p + Vector((0, 0, 0.8)), 0.08, 0.08, WETS, 6)
        cyl("storso", p + Vector((0, 0, 0.8)), p + Vector((0, 0, 1.45)) + fw * 0.15, 0.17, 0.15, WETS, 8)
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.12); hh = mesh_obj("shead", bm, WETS); hh.location = p + Vector((0, 0, 1.62)) + fw * 0.18
        cyl("sarm", p + Vector((0, 0, 1.35)), p + Vector((0, 0, 1.25)) + fw * 0.85 + sd * 0.2, 0.05, 0.05, WETS, 6); cyl("sarm", p + Vector((0, 0, 1.35)), p + Vector((0, 0, 1.2)) - fw * 0.8 - sd * 0.2, 0.05, 0.05, WETS, 6)
    else:                 # sitting in the line-up
        cyl("sbody", p + Vector((0, 0, 0.1)), p + Vector((0, 0, 0.95)), 0.17, 0.15, WETS, 8); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=6, radius=0.12)
        hh = mesh_obj("shead", bm, WETS); hh.location = p + Vector((0, 0, 1.12))
for (yy, off, mode) in ((430, 24, "ride"), (452, 30, "ride"), (470, 84, "sit"), (440, 88, "sit")):
    p = Vector((coast_x(yy), yy, Z_PLAIN - 1.2 + (0.6 if mode == "ride" else 0.0))) + seaward * off
    surfer(p, mode, math.atan2(cdir.y, cdir.x) + (0.35 if mode == "ride" else 1.4))

# ================================================================== PORTRAIT SET (layer 3, R3): 2.0 x 2.4 m natural linen backdrop on two stands at ~6 m, stool at ~5.7 m (right third),
# lit by one 3200 K softbox just outside the frame (right) so it is the warmest near element; plateau ground is on the same layer
LAYER[0] = 3
METAL = flat("stand_metal", (0.035, 0.035, 0.037), 0.35, 1.0)
LIN = pbr("linen", "rough_linen", 1.4, (E("LINT", "0.5"), E("LINT", "0.5") * 0.9, E("LINT", "0.5") * 0.78), 0.1, 0.8)
SETC = Vector((2.38, 6.23, 0)); SDIR = Vector((-0.66, 0.75, 0)).normalized()
P_NEAR = SETC - SDIR; P_FAR = SETC + SDIR; BW = (P_FAR - P_NEAR).length; DIR = (P_FAR - P_NEAR).normalized()
NRM = Vector((-DIR.y, DIR.x, 0))
if NRM.dot(-(P_NEAR + P_FAR) / 2) < 0: NRM = -NRM
def gz(p): return height(p.x, p.y)
def setp(u, z): p = P_NEAR + DIR * u; return Vector((p.x, p.y, gz(p) + z))
BH = 2.4
for u in (0.0, BW):
    base = setp(u, 0)
    cyl("pole", base + Vector((0, 0, 0.55)), base + Vector((0, 0, BH + 0.12)), 0.017, 0.014, METAL)
    for k in range(3):
        ang = k * 2.094 + 0.4; cyl("leg", base + Vector((0, 0, 0.62)), base + Vector((math.cos(ang) * 0.5, math.sin(ang) * 0.5, 0.0)), 0.011, 0.011, METAL, 8)
cyl("crossbar", setp(-0.06, BH + 0.06), setp(BW + 0.06, BH + 0.06), 0.015, 0.015, METAL)
bm = bmesh.new(); NU, NV = 50, 70; grid = []
for j in range(NV + 1):
    v = j / NV; row = []
    for i in range(NU + 1):
        u = 0.03 + i / NU * (BW - 0.06); z = BH - v * (BH + 0.35)
        fold = (0.03 * math.sin(u * 10.0 + 0.7) + 0.015 * math.sin(u * 23.0 + 2)) * (0.3 + v)
        sweep = 0.0
        if z < 0.03: sweep = -z; z = 0.03 + 0.04 * math.exp(-sweep * 10)
        row.append(bm.verts.new(setp(u, z) + NRM * (fold + sweep)))
    grid.append(row)
for j in range(NV):
    for i in range(NU): bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
sheet = mesh_obj("linen", bm, LIN); sheet.modifiers.new("s", "SOLIDIFY").thickness = 0.004
for o in import_gltf(PH + "bar_chair_round_01/bar_chair_round_01.gltf"):
    if o.type == "MESH" and o.parent is None:
        sp_ = setp(BW * 0.5, 0) + NRM * 1.1; o.location = Vector((sp_.x, sp_.y, gz(sp_))); o.rotation_euler = (0, 0, math.radians(-30)); STOOL = o
# 3200 K softbox (1.0 x 1.0 m) on a stand just outside the right frame edge, aimed at the stool / backdrop
sbl = bpy.data.lights.new("softbox", "AREA"); sbl.shape = "SQUARE"; sbl.size = 1.0; sbl.energy = E("SOFTW", "150"); sbl.color = (1.0, 0.71, 0.45)
sbo = link(bpy.data.objects.new("softbox", sbl)); sbo.location = (3.15, 4.35, gz(Vector((3.15, 4.35, 0))) + 1.9)
sbo.rotation_euler = (SETC + Vector((0, 0, 0.9)) - sbo.location).to_track_quat("-Z", "Y").to_euler()
sb_st = Vector((3.15, 4.35, gz(Vector((3.15, 4.35, 0))))); cyl("sb_pole", sb_st + Vector((0, 0, 0.5)), sb_st + Vector((0, 0, 1.85)), 0.017, 0.015, METAL)
for k in range(3):
    ang = k * 2.094; cyl("sb_leg", sb_st + Vector((0, 0, 0.58)), sb_st + Vector((math.cos(ang) * 0.45, math.sin(ang) * 0.45, 0)), 0.011, 0.011, METAL, 8)

# ================================================================== PINE (layer 4): trunk at the left edge (<= 4% of width) + drooping boughs top-left
LAYER[0] = 4
BARK, N, L, b = new_mat("bark"); tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (2.0, 2.0, 0.7); L.new(tc.outputs["Object"], mp.inputs["Vector"])
for k, sock, nc in (("diff", "Base Color", False), ("rough", "Roughness", True)):
    n_ = N.new("ShaderNodeTexImage"); n_.image = img(PH + "pine_bark_%s_2k.jpg" % k, nc); n_.projection = "BOX"; L.new(mp.outputs[0], n_.inputs[0]); L.new(n_.outputs[0], b.inputs[sock])
n_ = N.new("ShaderNodeTexImage"); n_.image = img(PH + "pine_bark_nor_gl_2k.jpg", True); n_.projection = "BOX"; L.new(mp.outputs[0], n_.inputs[0])
nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 1.5; L.new(n_.outputs[0], nm.inputs["Color"]); L.new(nm.outputs[0], b.inputs["Normal"])
TRX = E("TRX", "-1.43")
tr = cyl("trunk", (TRX - 0.05, 3.6, -0.3), (TRX + 0.12, 3.75, 6.0), 0.19, 0.14, BARK, 24)
def bough(src, root, rot, s):
    g = link(bpy.data.objects.new("bough", src.data)); g.location = root; g.rotation_euler = rot; g.scale = (s, s, s)
    m_ = Matrix.Rotation(rot[2], 3, "Z") @ Matrix.Rotation(rot[1], 3, "Y") @ Matrix.Rotation(rot[0], 3, "X")
    cyl("limb", root, root + m_ @ Vector((0, 0, 0.7 * s)), 0.045, 0.014, BARK, 8)
bough(saps[0], Vector((TRX + 0.05, 3.7, 2.25)), (math.radians(-8), math.radians(108), math.radians(-25)), 1.3)
bough(saps[1], Vector((TRX + 0.07, 3.72, 2.7)), (math.radians(6), math.radians(102), math.radians(-5)), 1.4)
if VIEW == "phone":   # the phone frame sits right of the trunk: a second pine bough hangs into its top-left corner
    PBX = E("PBX", "-0.6"); PBY = E("PBY", "3.9"); PBZ = E("PBZ", "3.5")
    cyl("limb", Vector((PBX - 0.9, PBY - 0.2, PBZ + 0.2)), Vector((PBX, PBY, PBZ)), 0.06, 0.035, BARK, 8)
    bough(saps[0], Vector((PBX, PBY, PBZ)), (math.radians(-12), math.radians(112), math.radians(-35)), 1.6)
    bough(saps[1], Vector((PBX + 0.1, PBY + 0.3, PBZ + 0.25)), (math.radians(4), math.radians(98), math.radians(-10)), 1.5)

# ================================================================== CAMERA
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam_d.sensor_width = 36; cam_d.clip_start = 0.05; cam_d.clip_end = 40000; cam.location = (0, 0, 1.55)
if VIEW == "desk":
    cam_d.lens = E("LENS", "50"); cam_d.sensor_fit = "HORIZONTAL"; pitch = E("PITCH", "-5")
else:
    cam_d.lens = E("LENS", "32"); cam_d.sensor_fit = "VERTICAL"; cam_d.sensor_height = 36; pitch = E("PITCH", "-7.7"); cam.location = (E("CAMX", "1.2"), E("CAMY", "1.6"), E("CAMZ", "2.6"))   # photographer standing on a kurkar block
yaw = E("YAW", "0")
cam.rotation_euler = (math.radians(90 + pitch), 0, math.radians(yaw)); cam_d.dof.use_dof = False   # base plate is all-sharp; focus states are layered composites

# ================================================================== LAYER MASK AOVs (per-object one-hot -> m1 = layers 0,1,2 ; m2 = layers 3,4)
vl = sc.view_layers[0]
for nm_ in ("m1", "m2"):
    av = vl.aovs.add(); av.name = nm_; av.type = "COLOR"
for o in bpy.data.objects:
    l_ = o.get("lay", 2)
    if l_ < 0: continue
    oh = [1.0 if l_ == k else 0.0 for k in range(5)]
    o["m1"] = oh[0:3]; o["m2"] = oh[3:5] + [0.0]
for m in bpy.data.materials:
    if not m.use_nodes or m.name.startswith("haze"): continue
    nt = m.node_tree
    pb = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    asrc = pb.inputs["Alpha"].links[0].from_socket if (pb is not None and pb.inputs["Alpha"].is_linked) else None
    for nm_ in ("m1", "m2"):
        at_ = nt.nodes.new("ShaderNodeAttribute"); at_.attribute_type = "OBJECT"; at_.attribute_name = nm_
        ao = nt.nodes.new("ShaderNodeOutputAOV"); ao.aov_name = nm_; src = at_.outputs["Color"]
        if asrc is not None:   # alpha-cut leaves/grass: only the opaque part of the card belongs to the layer
            sv = nt.nodes.new("ShaderNodeVectorMath"); sv.operation = "SCALE"; nt.links.new(src, sv.inputs[0]); nt.links.new(asrc, sv.inputs["Scale"]); src = sv.outputs[0]
        nt.links.new(src, ao.inputs["Color"])

print("scene built in %.1fs" % (time.time() - T0), flush=True)
# 1) beauty (all sharp = hyperfocal), AgX display PNG
sc.render.image_settings.media_type = "IMAGE"; sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "8"
sc.render.filepath = OUTB + ".png"
if not os.environ.get("MASKONLY"): bpy.ops.render.render(write_still=True)
print("beauty %.1fs" % (time.time() - T0), flush=True)
# 2) clean layer-mask pass: haze hidden (volume scattering makes AOVs stochastic), few samples, uncompressed multilayer EXR
for o in bpy.data.objects:
    if o.name.startswith("haze"): o.hide_render = True
cy.samples = int(E("MASKSPP", "12")); cy.use_denoising = False; cy.use_adaptive_sampling = False; cy.max_bounces = 0
sc.render.image_settings.media_type = "MULTI_LAYER_IMAGE"; sc.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"; sc.render.image_settings.color_depth = "16"
sc.render.image_settings.exr_codec = "NONE"; sc.render.filepath = OUTB + ".exr"
bpy.ops.render.render(write_still=True)
print("DONE", OUTB, "%.1fs" % (time.time() - T0))
