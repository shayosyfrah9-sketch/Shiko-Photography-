# SHIKO WORLD 2.0 - Concept C "WHERE HE STOOD", risk test (C3). Blender 5.3 Cycles CPU, headless.
# One script, four modes (all procedural, no downloaded assets):
#   spray     landscape water-spray frame, sea behind, wet sand in front, no wave lip      (deliverable 1)
#   hole      same scene + a surfer/board-shaped absence carved in the drops, registered to the photo rect (deliverable 2 base)
#   edge      only: photo + ivory mount as 3D emissive planes at the focus plane + ~30 rendered drops at the photo edge (deliverable 2 overlay)
#   portrait  same scene, portrait camera + taller plume (deliverable 3 backdrop)
# Run: python C3_spray.py -- MODE W H SPP OUT.png
import bpy, bmesh, sys, os, math, json, time
import numpy as np
from mathutils import Vector
from PIL import Image, ImageDraw

MODE, W, H, SPP, OUT = sys.argv[sys.argv.index("--") + 1:][:5]
W, H, SPP = int(W), int(H), int(SPP)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PHOTO = os.path.join(ROOT, "media", "photos", "surf0001.jpg")
PW, PH = 1500, 1238
PORTRAIT = MODE == "portrait"
rng = np.random.default_rng(31)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ---------------------------------------------------------------- helpers
def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear(); return m, nt
def N(nt, t, **kw):
    n = nt.nodes.new(t)
    for k, v in kw.items(): setattr(n, k, v)
    return n
def L(nt, a, b): nt.links.new(a, b)
def mesh_from(name, V, F, mat, smooth=True):
    me = bpy.data.meshes.new(name); me.from_pydata(V.tolist() if len(V) < 2000000 else V, [], F.tolist() if False else F)
    me.update(); ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob)
    if smooth:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    ob.data.materials.append(mat); return ob

# ---------------------------------------------------------------- camera
SENS = 36.0
cam_d = bpy.data.cameras.new("cam"); cam_d.lens = 70; cam_d.sensor_width = SENS; cam_d.sensor_fit = "HORIZONTAL"
cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 8.0
cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
if PORTRAIT:
    cam.location = (0.05, 0.55, 1.0); pitch = 9.0; cam_d.dof.focus_distance = 4.0
else:
    cam.location = (0.0, 0.0, 0.5); pitch = 1.5; cam_d.dof.focus_distance = 4.5
cam.rotation_euler = (math.radians(90 - pitch), 0, 0)
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = W, H, 100
bpy.context.view_layer.update()
MI = np.array(cam.matrix_world.inverted())
FPX = W / SENS * cam_d.lens                                   # focal length in pixels

def project(P):                                               # world (n,3) -> px, py, optical depth
    Ph = np.c_[P, np.ones(len(P))] @ MI.T
    z = -Ph[:, 2]
    return W / 2 + Ph[:, 0] / z * FPX, H / 2 - Ph[:, 1] / z * FPX, z

# ---------------------------------------------------------------- photo registration (deliverable 2)
TW = 0.47 * W; TH = TW * PH / PW
X0 = 0.52 * W - 0.583 * TW; Y0 = 0.42 * H - 0.355 * TH
REG = dict(frame_w=W, frame_h=H, x0=X0, y0=Y0, w=TW, h=TH)

# hand-traced union silhouette of surfer + board in photo pixel coords (1500x1238)
_C = [  # traced on a 2x crop of the photo (origin 650,250); board, then body+arm+leg
 [(300,372),(380,372),(440,395),(472,470),(470,560),(432,642),(362,722),(322,776),(230,792),(165,762),(125,702),(120,600),(150,500),(215,410)],
 [(305,210),(360,216),(440,258),(505,250),(508,125),(540,75),(600,62),(655,75),(668,120),(665,180),(720,200),(780,260),(802,380),(792,480),(776,562),(740,592),(700,616),
  (620,612),(540,562),(500,546),(480,592),(440,642),(402,682),(330,682),(260,676),(238,645),(300,612),(360,545),(412,470),(440,400),(446,375),(420,300),(330,238)],
]
SIL = [[(650 + x / 2, 250 + y / 2) for x, y in poly] for poly in _C]
def sil_mask():
    im = Image.new("L", (PW, PH), 0); d = ImageDraw.Draw(im)
    for p in SIL: d.polygon(p, fill=255)
    return im

# ---------------------------------------------------------------- world: photo-matched blue sky + sun
SUN_EL, SUN_AZ = 32.0, 14.0                                   # elevation, azimuth left of +Y (backlit, behind the spray)
s = Vector((-math.sin(math.radians(SUN_AZ)) * math.cos(math.radians(SUN_EL)), math.cos(math.radians(SUN_AZ)) * math.cos(math.radians(SUN_EL)), math.sin(math.radians(SUN_EL))))
w = bpy.data.worlds.new("w"); w.use_nodes = True; sc.world = w; nt = w.node_tree; nt.nodes.clear()
tc = N(nt, "ShaderNodeTexCoord"); sep = N(nt, "ShaderNodeSeparateXYZ"); L(nt, tc.outputs["Generated"], sep.inputs[0])
# generated coords in the world shader are the view direction; z = elevation
ab = N(nt, "ShaderNodeMath", operation="ABSOLUTE"); L(nt, sep.outputs["Z"], ab.inputs[0])
pw_ = N(nt, "ShaderNodeMath", operation="POWER"); pw_.inputs[1].default_value = 0.55; L(nt, ab.outputs[0], pw_.inputs[0])
ramp = N(nt, "ShaderNodeValToRGB"); L(nt, pw_.outputs[0], ramp.inputs[0])
ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = (0.12, 0.30, 0.80, 1)   # horizon (photo ~ sRGB 112,145,215 -> a touch lower)
ramp.color_ramp.elements[1].position = 0.85; ramp.color_ramp.elements[1].color = (0.020, 0.080, 0.50, 1)  # zenith (photo ~ 75,105,190)
dot = N(nt, "ShaderNodeVectorMath", operation="DOT_PRODUCT"); dot.inputs[1].default_value = s; L(nt, tc.outputs["Generated"], dot.inputs[0])
cl = N(nt, "ShaderNodeMath", operation="MAXIMUM"); cl.inputs[1].default_value = 0.0; L(nt, dot.outputs["Value"], cl.inputs[0])
gl = N(nt, "ShaderNodeMath", operation="POWER"); gl.inputs[1].default_value = 18.0; L(nt, cl.outputs[0], gl.inputs[0])
gm = N(nt, "ShaderNodeMath", operation="MULTIPLY"); gm.inputs[1].default_value = 1.4; L(nt, gl.outputs[0], gm.inputs[0])
glc = N(nt, "ShaderNodeMix", data_type="RGBA", blend_type="ADD"); glc.inputs[0].default_value = 1.0
L(nt, ramp.outputs[0], glc.inputs[6]); glc.inputs[7].default_value = (1, 0.95, 0.85, 1)
mulg = N(nt, "ShaderNodeVectorMath", operation="SCALE"); L(nt, gm.outputs[0], mulg.inputs["Scale"]); mulg.inputs[0].default_value = (1, 0.95, 0.85)
L(nt, mulg.outputs[0], glc.inputs[7])
bg = N(nt, "ShaderNodeBackground"); bg.inputs["Strength"].default_value = 0.9; L(nt, glc.outputs[2], bg.inputs["Color"])
wo = N(nt, "ShaderNodeOutputWorld"); L(nt, bg.outputs[0], wo.inputs[0])

sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 4.2; sun.angle = math.radians(1.2); sun.color = (1.0, 0.96, 0.9)
so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so); so.rotation_euler = (-s).to_track_quat("-Z", "Y").to_euler()

# ---------------------------------------------------------------- drop material (real water: IOR 1.33)
def drop_mat(rimk=2.4):
    m, nt = new_mat("water_drop")
    g = N(nt, "ShaderNodeBsdfGlass"); g.inputs["IOR"].default_value = 1.33; g.inputs["Roughness"].default_value = 0.0
    g.inputs["Color"].default_value = (0.80, 0.98, 0.96, 1)                 # slight teal where the path through water is long
    lw = N(nt, "ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.55
    em = N(nt, "ShaderNodeEmission"); em.inputs["Color"].default_value = (0.92, 0.97, 1.0, 1)
    mk = N(nt, "ShaderNodeMath", operation="MULTIPLY"); mk.inputs[1].default_value = rimk; L(nt, lw.outputs["Fresnel"], mk.inputs[0])   # rim = grazing facing
    L(nt, mk.outputs[0], em.inputs["Strength"])
    ad = N(nt, "ShaderNodeAddShader"); L(nt, g.outputs[0], ad.inputs[0]); L(nt, em.outputs[0], ad.inputs[1])
    tr = N(nt, "ShaderNodeBsdfTransparent"); lp = N(nt, "ShaderNodeLightPath")
    mx = N(nt, "ShaderNodeMixShader"); L(nt, lp.outputs["Is Shadow Ray"], mx.inputs[0]); L(nt, ad.outputs[0], mx.inputs[1]); L(nt, tr.outputs[0], mx.inputs[2])
    o = N(nt, "ShaderNodeOutputMaterial"); L(nt, mx.outputs[0], o.inputs[0]); return m
def mist_mat():
    m, nt = new_mat("mist")
    em = N(nt, "ShaderNodeEmission"); em.inputs["Color"].default_value = (0.9, 0.96, 1.0, 1); em.inputs["Strength"].default_value = 1.7
    tr = N(nt, "ShaderNodeBsdfTransparent"); mx = N(nt, "ShaderNodeMixShader"); mx.inputs[0].default_value = 0.72
    L(nt, tr.outputs[0], mx.inputs[1]); L(nt, em.outputs[0], mx.inputs[2])
    o = N(nt, "ShaderNodeOutputMaterial"); L(nt, mx.outputs[0], o.inputs[0]); return m

# icosphere templates
def ico(sub):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    V = np.array([v.co[:] for v in bm.verts]); F = np.array([[v.index for v in f.verts] for f in bm.faces]); bm.free(); return V, F
T1, TF1 = ico(1); T0, TF0 = ico(1)

def build_drops(name, P, R, ax, el, mat):
    """P centres (n,3), R radii (n,), ax unit stretch axis (n,3), el elongation (n,)"""
    n = len(P); V = T1[None] * R[:, None, None]                      # (n,v,3)
    A = np.eye(3)[None] + (el - 1)[:, None, None] * ax[:, :, None] * ax[:, None, :]
    V = np.einsum("nij,nvj->nvi", A, V) + P[:, None, :]
    F = (TF1[None] + (np.arange(n) * len(T1))[:, None, None]).reshape(-1, 3)
    me = bpy.data.meshes.new(name); me.vertices.add(n * len(T1)); me.vertices.foreach_set("co", V.reshape(-1).astype(np.float32))
    me.loops.add(len(F) * 3); me.polygons.add(len(F))
    me.loops.foreach_set("vertex_index", F.reshape(-1)); me.polygons.foreach_set("loop_start", np.arange(len(F)) * 3); me.polygons.foreach_set("loop_total", np.full(len(F), 3))
    me.polygons.foreach_set("use_smooth", np.ones(len(F), bool)); me.update(); me.validate()
    ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob); me.materials.append(mat); return ob

# ---------------------------------------------------------------- spray (same seed -> same scene for every mode)
def gen_spray():
    hs = 1.7 if PORTRAIT else 1.0
    CX, CY, ARCH = 0.05, 4.5, 1.0 * hs
    P = []; R = []; AX = []; EL = []
    def diam(n): return np.clip(np.exp(rng.normal(np.log(3.3), 0.45, n)), 2.0, 8.0)       # mm diameter
    # (a) arch / curtain of spray, rising from the sea edge and falling back
    n = 2600; u = rng.random(n); x = CX - 1.05 + 2.1 * u + rng.normal(0, 0.07, n)
    za = ARCH * (1 - (2 * u - 1) ** 2) ** 0.85
    z = za * np.where(rng.random(n) < 0.3, 1.0, rng.random(n) ** 0.5) + rng.normal(0, 0.035, n) * hs
    y = CY + rng.normal(0, 0.16, n)
    tx = np.c_[np.full(n, 2.1), np.zeros(n), -ARCH * 2 * (2 * u - 1) * 2 * 0.85 * 1.0]; tx /= np.linalg.norm(tx, axis=1)[:, None]
    P.append(np.c_[x, y, z]); AX.append(tx); d = diam(n); R.append(d / 2000.0)
    EL.append(np.where(rng.random(n) < 0.18, rng.uniform(1.8, 3.6, n), 1.0))
    # (b) central plume
    n = 2000; z = np.clip(rng.exponential(0.30 * hs, n), 0, 1.25 * hs); x = CX + 0.05 + rng.normal(0, 1, n) * (0.35 + 0.5 * z / hs)
    y = CY + rng.normal(0, 0.2, n); P.append(np.c_[x, y, z]); d = diam(n); R.append(d / 2000.0)
    v = np.c_[rng.normal(0, 0.3, n), rng.normal(0, 0.1, n), np.ones(n)]; v /= np.linalg.norm(v, axis=1)[:, None]; AX.append(v)
    EL.append(np.where(rng.random(n) < 0.15, rng.uniform(1.6, 3.0, n), 1.0))
    # (c) a few larger flung drops, 6-8 mm
    n = 260; x = CX + rng.normal(0, 1.0, n); z = rng.uniform(0.05, 1.35 * hs, n); y = CY + rng.normal(0, 0.3, n)
    P.append(np.c_[x, y, z]); R.append(rng.uniform(2.6, 4.0, n) / 1000.0)
    v = np.c_[rng.normal(0, 0.5, n), rng.normal(0, 0.2, n), rng.normal(0.5, 0.5, n)]; v /= np.linalg.norm(v, axis=1)[:, None]; AX.append(v); EL.append(np.where(rng.random(n) < 0.3, 2.2, 1.0))
    P = np.vstack(P); R = np.concatenate(R); AX = np.vstack(AX); EL = np.concatenate(EL)
    # near-camera out-of-focus drops (bokeh), a handful
    n = 22; pb = np.c_[rng.uniform(-0.45, 0.45, n), rng.uniform(1.9, 3.1, n), rng.uniform(0.35, 1.0, n) + (0.5 if PORTRAIT else 0)]
    return P, R, AX, EL, pb

P, R, AX, EL, PB = gen_spray()
from mathutils import noise as mnoise
def clump(PP):   # keep probability from a 3D fractal: drops gather in fans and clots
    f = np.array([mnoise.fractal(Vector((p[0] * 2.2, p[1] * 2.2, p[2] * 3.0)), 1.0, 2.0, 4) for p in PP])
    return np.clip((f + 0.25) * 2.6, 0.04, 1.0)
kc = rng.random(len(P)) < clump(P); P, R, AX, EL = P[kc], R[kc], AX[kc], EL[kc]
mist_n = 1
MZ = np.clip(rng.exponential(0.32 * (1.7 if PORTRAIT else 1.0), mist_n), 0, 2.0); MX = 0.05 + rng.normal(0, 0.55 + 0.45 * MZ, mist_n)
MP = np.c_[MX, 4.5 + rng.normal(0, 0.35, mist_n), MZ]; MR = rng.uniform(0.8, 2.6, mist_n) / 1000.0

if MODE == "hole":
    mask = np.array(sil_mask()) > 0
    from PIL import ImageFilter
    mask = np.array(sil_mask().filter(ImageFilter.MaxFilter(5))) > 0        # +2 px dilation in photo px
    def keep(PP, RR):
        px, py, z = project(PP); sc_ = TW / PW
        ux = ((px - X0) / sc_).astype(int); uy = ((py - Y0) / sc_).astype(int)
        inside = (ux >= 0) & (ux < PW) & (uy >= 0) & (uy < PH)
        hit = np.zeros(len(PP), bool); hit[inside] = mask[uy[inside], ux[inside]]
        return ~hit
    k = keep(P, R); P, R, AX, EL = P[k], R[k], AX[k], EL[k]
    k = keep(MP, MR); MP, MR = MP[k], MR[k]
    k = keep(PB, np.zeros(len(PB))); PB = PB[k]
    REG["removed_note"] = "drops whose projected centre falls in the traced surfer+board silhouette (+2 photo px) are removed"
if MODE != "edge":
    drop_obj = build_drops("drops", P, R, AX, EL, drop_mat())
    zeros = np.tile([0, 0, 1.0], (len(MP), 1)); ones = np.ones(len(MP))
    build_drops("bokeh", PB, rng.uniform(3.0, 6.0, len(PB)) / 1000.0, np.tile([0, 0, 1.0], (len(PB), 1)), np.ones(len(PB)), drop_mat(3.5))
    REG["n_drops"] = int(len(P)); REG["n_mist"] = int(len(MP)); REG["n_bokeh"] = int(len(PB))

# ---------------------------------------------------------------- sand + sea
if MODE != "edge":
    # wet sand
    xs = np.linspace(-9, 9, 360); ys = np.linspace(-1.5, 5.2, 300); gx, gy = np.meshgrid(xs, ys)
    gz = 0.04 - 0.05 * np.clip(gy - 3.0, 0, None) + 0.004 * np.sin(gx * 9 + gy * 3) * np.exp(-((gy - 3.4) / 1.0) ** 2)
    V = np.c_[gx.ravel(), gy.ravel(), gz.ravel()]
    idx = np.arange(len(xs) * len(ys)).reshape(len(ys), len(xs))
    F = np.c_[idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()]
    m, nt = new_mat("wet_sand")
    tcn = N(nt, "ShaderNodeTexCoord")
    mp = N(nt, "ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 1.0, 1.0); L(nt, tcn.outputs["Object"], mp.inputs[0])
    nz = N(nt, "ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.6; nz.inputs["Detail"].default_value = 6; L(nt, mp.outputs[0], nz.inputs[0])
    nz2 = N(nt, "ShaderNodeTexNoise"); nz2.inputs["Scale"].default_value = 70; nz2.inputs["Detail"].default_value = 8; L(nt, mp.outputs[0], nz2.inputs[0])
    mp2 = N(nt, "ShaderNodeMapping"); mp2.inputs["Scale"].default_value = (5.0, 1.0, 1.0); L(nt, tcn.outputs["Object"], mp2.inputs[0])
    wv = N(nt, "ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "Y"; wv.inputs["Scale"].default_value = 24; wv.inputs["Distortion"].default_value = 5.0; wv.inputs["Detail"].default_value = 3
    L(nt, mp2.outputs[0], wv.inputs[0])
    mixb = N(nt, "ShaderNodeMath", operation="ADD"); L(nt, wv.outputs[0], mixb.inputs[0]); L(nt, nz2.outputs[0], mixb.inputs[1])
    bump = N(nt, "ShaderNodeBump"); bump.inputs["Strength"].default_value = 1.0; bump.inputs["Distance"].default_value = 0.012; L(nt, mixb.outputs[0], bump.inputs["Height"])
    cr = N(nt, "ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.10, 0.065, 0.040, 1); cr.color_ramp.elements[1].color = (0.30, 0.20, 0.11, 1); L(nt, nz.outputs[0], cr.inputs[0])
    rr = N(nt, "ShaderNodeMapRange"); rr.inputs["To Min"].default_value = 0.32; rr.inputs["To Max"].default_value = 0.75; L(nt, nz.outputs[0], rr.inputs[0])
    pb = N(nt, "ShaderNodeBsdfPrincipled"); pb.inputs["Specular IOR Level"].default_value = 0.12
    L(nt, cr.outputs[0], pb.inputs["Base Color"]); L(nt, rr.outputs[0], pb.inputs["Roughness"]); L(nt, bump.outputs[0], pb.inputs["Normal"])
    o = N(nt, "ShaderNodeOutputMaterial"); L(nt, pb.outputs[0], o.inputs[0])
    mesh_from("sand", V, F, m, smooth=True)

    # sea: displaced grid, geometric spacing to the horizon
    nyy, nxx = 360, 420
    ys = 3.7 + 25000.0 * np.linspace(0, 1, nyy) ** 3.2
    u = np.linspace(-1, 1, nxx)
    gx = u[None, :] * (14 + 1.6 * ys[:, None]); gy = np.repeat(ys[:, None], nxx, 1)
    amp = np.exp(-gy / 90.0) * np.clip((gy - 3.7) / 1.5, 0, 1)
    gz = (0.10 * np.sin(0.95 * gy + 0.35 * gx) + 0.06 * np.sin(1.7 * gy - 0.5 * gx + 1.3) + 0.012 * np.sin(5.3 * gy + 3.1 * gx) + 0.009 * np.sin(7.9 * gx - 2.0 * gy)) * amp
    gz += 0.20 * np.exp(-((gy - 5.5) / 0.8) ** 2) * (0.7 + 0.3 * np.sin(gx * 1.7))      # low shore swell only, no breaking lip
    V = np.c_[gx.ravel(), gy.ravel(), gz.ravel()]
    idx = np.arange(nxx * nyy).reshape(nyy, nxx)
    F = np.c_[idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()]
    m, nt = new_mat("sea")
    tcn = N(nt, "ShaderNodeTexCoord")
    mpb = N(nt, "ShaderNodeMapping"); mpb.inputs["Scale"].default_value = (0.08, 0.35, 1.0); L(nt, tcn.outputs["Object"], mpb.inputs[0])     # long bands across the sea
    nzb = N(nt, "ShaderNodeTexNoise"); nzb.inputs["Scale"].default_value = 1.2; nzb.inputs["Detail"].default_value = 4; L(nt, mpb.outputs[0], nzb.inputs[0])
    crb = N(nt, "ShaderNodeValToRGB"); crb.color_ramp.interpolation = "EASE"
    crb.color_ramp.elements[0].position = 0.35; crb.color_ramp.elements[0].color = (0.0, 0.07, 0.30, 1)
    crb.color_ramp.elements[1].position = 0.62; crb.color_ramp.elements[1].color = (0.0, 0.42, 0.40, 1)
    e = crb.color_ramp.elements.new(0.85); e.color = (0.02, 0.50, 0.30, 1); L(nt, nzb.outputs[0], crb.inputs[0])
    sepo = N(nt, "ShaderNodeSeparateXYZ"); L(nt, tcn.outputs["Object"], sepo.inputs[0])
    far = N(nt, "ShaderNodeMapRange"); far.inputs["From Min"].default_value = 15; far.inputs["From Max"].default_value = 900; L(nt, sepo.outputs["Y"], far.inputs[0])
    hz = N(nt, "ShaderNodeMix", data_type="RGBA"); L(nt, far.outputs[0], hz.inputs[0]); L(nt, crb.outputs[0], hz.inputs[6]); hz.inputs[7].default_value = (0.03, 0.2, 0.42, 1)
    mpc = N(nt, "ShaderNodeMapping"); mpc.inputs["Scale"].default_value = (9.0, 9.0, 9.0); L(nt, tcn.outputs["Object"], mpc.inputs[0])
    nzc = N(nt, "ShaderNodeTexNoise"); nzc.inputs["Scale"].default_value = 1.0; nzc.inputs["Detail"].default_value = 10; L(nt, mpc.outputs[0], nzc.inputs[0])
    bump = N(nt, "ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.35; bump.inputs["Distance"].default_value = 0.05; L(nt, nzc.outputs[0], bump.inputs["Height"])
    pb = N(nt, "ShaderNodeBsdfPrincipled"); pb.inputs["Roughness"].default_value = 0.035; pb.inputs["IOR"].default_value = 1.33
    L(nt, hz.outputs[2], pb.inputs["Base Color"]); L(nt, bump.outputs[0], pb.inputs["Normal"])
    pb.inputs["Emission Color"].default_value = (0.0, 0.5, 0.45, 1); pb.inputs["Emission Strength"].default_value = 0.35
    L(nt, hz.outputs[2], pb.inputs["Emission Color"])
    # shore foam: lacy white band where the water meets the sand and on the low swell crest
    fy = N(nt, "ShaderNodeMapRange"); fy.inputs["From Min"].default_value = 3.6; fy.inputs["From Max"].default_value = 6.2; fy.inputs["To Min"].default_value = 1.0; fy.inputs["To Max"].default_value = 0.0
    L(nt, sepo.outputs["Y"], fy.inputs[0])
    mpf = N(nt, "ShaderNodeMapping"); mpf.inputs["Scale"].default_value = (7, 7, 7); L(nt, tcn.outputs["Object"], mpf.inputs[0])
    nzf = N(nt, "ShaderNodeTexNoise"); nzf.inputs["Scale"].default_value = 1.4; nzf.inputs["Detail"].default_value = 9; L(nt, mpf.outputs[0], nzf.inputs[0])
    fm = N(nt, "ShaderNodeMath", operation="MULTIPLY"); L(nt, fy.outputs[0], fm.inputs[0]); L(nt, nzf.outputs[0], fm.inputs[1])
    fr = N(nt, "ShaderNodeMapRange"); fr.inputs["From Min"].default_value = 0.36; fr.inputs["From Max"].default_value = 0.52; L(nt, fm.outputs[0], fr.inputs[0])
    fd = N(nt, "ShaderNodeBsdfDiffuse"); fd.inputs["Color"].default_value = (0.9, 0.95, 0.95, 1)
    fmx = N(nt, "ShaderNodeMixShader"); L(nt, fr.outputs[0], fmx.inputs[0]); L(nt, pb.outputs[0], fmx.inputs[1]); L(nt, fd.outputs[0], fmx.inputs[2])
    o = N(nt, "ShaderNodeOutputMaterial"); L(nt, fmx.outputs[0], o.inputs[0])
    mesh_from("sea", V, F, m, smooth=True)

# ---------------------------------------------------------------- mist volume (soft white mass behind/around the drops)
if MODE != "edge":
    hs = 1.7 if PORTRAIT else 1.0
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    me = bpy.data.meshes.new("mistvol"); bm.to_mesh(me); bm.free()
    vo = bpy.data.objects.new("mistvol", me); sc.collection.objects.link(vo)
    vo.location = (0.05, 4.55, 0.65 * hs); vo.scale = (3.6, 1.2, 1.5 * hs); vo.visible_shadow = False
    m, nt = new_mat("mist_vol")
    tcn = N(nt, "ShaderNodeTexCoord"); sp = N(nt, "ShaderNodeSeparateXYZ"); L(nt, tcn.outputs["Generated"], sp.inputs[0])
    mp = N(nt, "ShaderNodeMapping"); mp.inputs["Scale"].default_value = (4.0, 4.0, 5.0); L(nt, tcn.outputs["Generated"], mp.inputs[0])
    nz = N(nt, "ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.0; nz.inputs["Detail"].default_value = 8; nz.inputs["Roughness"].default_value = 0.62; L(nt, mp.outputs[0], nz.inputs[0])
    mr = N(nt, "ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0.36; mr.inputs["From Max"].default_value = 0.66; L(nt, nz.outputs["Fac"], mr.inputs[0])
    hm = N(nt, "ShaderNodeMath", operation="MULTIPLY"); hm.inputs[1].default_value = -2.6; L(nt, sp.outputs["Z"], hm.inputs[0])
    he = N(nt, "ShaderNodeMath", operation="EXPONENT"); L(nt, hm.outputs[0], he.inputs[0])
    lx = N(nt, "ShaderNodeMath", operation="SUBTRACT"); lx.inputs[1].default_value = 0.5; L(nt, sp.outputs["X"], lx.inputs[0])
    lq = N(nt, "ShaderNodeMath", operation="MULTIPLY"); lq.inputs[1].default_value = -9.0; L(nt, lx.outputs[0], lq.inputs[0]); L(nt, lx.outputs[0], lq.inputs[0])
    lq2 = N(nt, "ShaderNodeMath", operation="MULTIPLY"); L(nt, lx.outputs[0], lq2.inputs[0]); L(nt, lq.outputs[0], lq2.inputs[1])
    le = N(nt, "ShaderNodeMath", operation="EXPONENT"); L(nt, lq2.outputs[0], le.inputs[0])
    d1 = N(nt, "ShaderNodeMath", operation="MULTIPLY"); L(nt, he.outputs[0], d1.inputs[0]); L(nt, le.outputs[0], d1.inputs[1])
    d2 = N(nt, "ShaderNodeMath", operation="MULTIPLY"); L(nt, d1.outputs[0], d2.inputs[0]); L(nt, mr.outputs[0], d2.inputs[1])
    dsc = d2
    if MODE == "hole":                                     # carve the same surfer/board absence out of the mist (Window = screen space)
        mpath = os.path.splitext(OUT)[0] + "_mask.png"
        mk = sil_mask().filter(__import__("PIL.ImageFilter", fromlist=["x"]).MaxFilter(5)); mk.save(mpath)
        wn = N(nt, "ShaderNodeTexCoord"); sw = N(nt, "ShaderNodeSeparateXYZ"); L(nt, wn.outputs["Window"], sw.inputs[0])
        u = N(nt, "ShaderNodeMath", operation="MULTIPLY_ADD"); u.inputs[1].default_value = W / TW; u.inputs[2].default_value = -X0 / TW; L(nt, sw.outputs["X"], u.inputs[0])
        v = N(nt, "ShaderNodeMath", operation="MULTIPLY_ADD"); v.inputs[1].default_value = H / TH; v.inputs[2].default_value = 1 - (H - Y0) / TH; L(nt, sw.outputs["Y"], v.inputs[0])
        cv = N(nt, "ShaderNodeCombineXYZ"); L(nt, u.outputs[0], cv.inputs["X"]); L(nt, v.outputs[0], cv.inputs["Y"])
        it = N(nt, "ShaderNodeTexImage"); it.image = bpy.data.images.load(mpath); it.image.colorspace_settings.name = "Non-Color"; it.extension = "CLIP"; it.interpolation = "Closest"
        L(nt, cv.outputs[0], it.inputs[0])
        inv = N(nt, "ShaderNodeMath", operation="SUBTRACT"); inv.inputs[0].default_value = 1.0; L(nt, it.outputs["Color"], inv.inputs[1]) if False else None
        sepc = N(nt, "ShaderNodeSeparateColor"); L(nt, it.outputs["Color"], sepc.inputs[0]); L(nt, sepc.outputs["Red"], inv.inputs[1])
        d3 = N(nt, "ShaderNodeMath", operation="MULTIPLY"); L(nt, d2.outputs[0], d3.inputs[0]); L(nt, inv.outputs[0], d3.inputs[1]); dsc = d3
    dd = N(nt, "ShaderNodeMath", operation="MULTIPLY"); dd.inputs[1].default_value = 2.8; L(nt, dsc.outputs[0], dd.inputs[0])
    vs_ = N(nt, "ShaderNodeVolumeScatter"); vs_.inputs["Color"].default_value = (0.95, 0.98, 1.0, 1); vs_.inputs["Anisotropy"].default_value = 0.72; L(nt, dd.outputs[0], vs_.inputs["Density"])
    o = N(nt, "ShaderNodeOutputMaterial"); L(nt, vs_.outputs[0], o.inputs["Volume"]); me.materials.append(m)

# ---------------------------------------------------------------- edge pass: photo + mount in 3D, ~30 drops at the edge
if MODE == "edge":
    zf = 4.5; mpp = zf * SENS / cam_d.lens / W                    # metres per pixel at the focus plane
    def cam_to_world(xp, yp, d):                                  # pixel (xp,yp) at optical depth d -> world
        v = Vector(((xp - W / 2) / FPX * d, -(yp - H / 2) / FPX * d, -d)); return cam.matrix_world @ v
    def plane(name, xa, ya, wp, hp, mat, d):
        c = cam_to_world(xa + wp / 2, ya + hp / 2, d); me = bpy.data.meshes.new(name)
        wm, hm = wp * mpp * d / zf, hp * mpp * d / zf
        me.from_pydata([(-wm / 2, -hm / 2, 0), (wm / 2, -hm / 2, 0), (wm / 2, hm / 2, 0), (-wm / 2, hm / 2, 0)], [], [(0, 1, 2, 3)])
        uv = me.uv_layers.new(name="uv"); uv.data.foreach_set("uv", [0, 0, 1, 0, 1, 1, 0, 1]); me.update()
        ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob); ob.parent = cam
        ob.location = cam.matrix_world.inverted() @ c; me.materials.append(mat); return ob
    mm = max(3, W // 400)
    mi, nt = new_mat("mount"); em = N(nt, "ShaderNodeEmission"); em.inputs["Color"].default_value = (0.879, 0.842, 0.745, 1)   # ivory 241,236,224 (sRGB) ~ linear
    o = N(nt, "ShaderNodeOutputMaterial"); L(nt, em.outputs[0], o.inputs[0])
    pm, nt = new_mat("photo"); im = N(nt, "ShaderNodeTexImage"); im.image = bpy.data.images.load(PHOTO); im.image.colorspace_settings.name = "sRGB"; im.extension = "EXTEND"
    em = N(nt, "ShaderNodeEmission"); L(nt, im.outputs[0], em.inputs["Color"]); o = N(nt, "ShaderNodeOutputMaterial"); L(nt, em.outputs[0], o.inputs[0])
    plane("mount", X0 - mm, Y0 - mm, TW + 2 * mm, TH + 2 * mm, mi, zf + 0.0005)
    plane("photo", X0, Y0, TW, TH, pm, zf)
    # ~30 spheres in front of the print, centres in a band across its border (inside up to 36 px, outside up to 46 px)
    n = 32; E = []; Ps = []; Rs = []
    for i in range(n):
        t = rng.random(); side = rng.integers(4); off = rng.uniform(-36, 46)
        if side == 0: px, py = X0 + t * TW, Y0 - off
        elif side == 1: px, py = X0 + t * TW, Y0 + TH + off
        elif side == 2: px, py = X0 - off, Y0 + t * TH
        else: px, py = X0 + TW + off, Y0 + t * TH
        d = rng.uniform(4.0, 4.4); r = rng.uniform(2.2, 4.6) / 1000.0
        Ps.append(cam_to_world(px, py, d)[:]); Rs.append(r); E.append(dict(px=float(px), py=float(py), r_px=float(r * FPX / d), d=float(d)))
    build_drops("edge_drops", np.array(Ps), np.array(Rs), np.tile([0, 0, 1.0], (n, 1)), np.ones(n), drop_mat(1.4))
    REG["edge_drops"] = E; REG["mount_px"] = mm

# ---------------------------------------------------------------- render
cy = sc.cycles; sc.render.engine = "CYCLES"; cy.device = "CPU"; cy.samples = SPP; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02
cy.max_bounces = 10; cy.transmission_bounces = 8; cy.glossy_bounces = 4; cy.diffuse_bounces = 2; cy.transparent_max_bounces = 12; cy.volume_bounces = 0
cy.caustics_reflective = False; cy.caustics_refractive = False; cy.sample_clamp_indirect = 8
cy.use_denoising = MODE != "edge"; cy.denoiser = "OPENIMAGEDENOISE"
cy.use_auto_tile = True; sc.render.threads = 4
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "8"
sc.render.filepath = OUT
vs = sc.view_settings
if MODE == "edge":
    vs.view_transform = "Standard"
else:
    vs.view_transform = "AgX"
    for lk in ("AgX - Punchy", "Punchy"):
        try: vs.look = lk; break
        except Exception: pass
sc.render.film_transparent = False
t0 = time.time(); bpy.ops.render.render(write_still=True); dt = time.time() - t0
REG["mode"] = MODE; REG["spp"] = SPP; REG["seconds"] = round(dt, 1); REG["look"] = vs.look
json.dump(REG, open(os.path.splitext(OUT)[0] + "_register.json", "w"), indent=1)
print("RENDER_DONE", MODE, W, H, SPP, round(dt, 1), "s")
