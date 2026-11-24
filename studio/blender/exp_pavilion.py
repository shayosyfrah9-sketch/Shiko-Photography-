# SHIKO STUDIO readiness experiment: "Aperture Pavilion" — a futuristic pavilion on a cliff above a valley lake.
# Run: bpyenv/bin/python exp_pavilion.py -- ROUND OUT.png [W H SAMPLES] [FRAME_OF_N]
import bpy, bmesh, sys, math, os
from mathutils import Vector, noise
a = sys.argv[sys.argv.index("--")+1:]
RND = int(a[0]); OUT = a[1]; W = int(a[2]) if len(a)>2 else 1280; H = int(a[3]) if len(a)>3 else 720; SPP = int(a[4]) if len(a)>4 else 32
ANIM = a[5] if len(a)>5 else None   # "i/n" -> camera along the dolly path
PH = "/tmp/claude-0/-home-user/4c46e3af-0746-5d7c-a57c-71aa0650b7b7/scratchpad/ph/exp/"
R2, R3, R4 = RND >= 2, RND >= 3, RND >= 4

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; cy = sc.cycles
cy.device = "CPU"; cy.samples = SPP; cy.use_adaptive_sampling = True; cy.use_denoising = True
try: cy.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
cy.max_bounces = 6; cy.diffuse_bounces = 3; cy.glossy_bounces = 3; cy.transmission_bounces = 6; cy.sample_clamp_indirect = 8; cy.blur_glossy = 1.0
sc.render.resolution_x = W; sc.render.resolution_y = H; sc.render.filepath = OUT
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = "AgX - Medium High Contrast" if R2 else "None"
except Exception: pass
sc.view_settings.exposure = 0.0 if not R2 else -0.15

def img(n, nc=False):
    i = bpy.data.images.load(PH + n, check_existing=True)
    if nc: i.colorspace_settings.name = "Non-Color"
    return i

def pbr(name, tex, scale=1.0, tint=None, rough_mul=1.0, triplanar_box=True):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    bs = N["Principled BSDF"]
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale, scale, scale)
    L.new(tc.outputs["Object"], mp.inputs["Vector"])
    def t(fn, nc):
        n = N.new("ShaderNodeTexImage"); n.image = img(fn, nc); n.projection = "BOX"; n.projection_blend = 0.3; L.new(mp.outputs["Vector"], n.inputs["Vector"]); return n
    d = t(tex + "_diff_2k.jpg", False); r = t(tex + "_rough_2k.jpg", True); nm = t(tex + "_nor_gl_2k.jpg", True)
    col = d.outputs["Color"]
    if tint:
        mx = N.new("ShaderNodeMixRGB"); mx.blend_type = "MULTIPLY"; mx.inputs[0].default_value = 1; mx.inputs[2].default_value = tint + (1,)
        L.new(col, mx.inputs[1]); col = mx.outputs[0]
    L.new(col, bs.inputs["Base Color"])
    rm = N.new("ShaderNodeMath"); rm.operation = "MULTIPLY"; rm.inputs[1].default_value = rough_mul; L.new(r.outputs["Color"], rm.inputs[0]); L.new(rm.outputs[0], bs.inputs["Roughness"])
    nn = N.new("ShaderNodeNormalMap"); L.new(nm.outputs["Color"], nn.inputs["Color"]); L.new(nn.outputs["Normal"], bs.inputs["Normal"])
    return m

def flat(name, col, rough=0.5, metal=0.0, trans=0.0, ior=1.45, emit=None, estr=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = col + (1,); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    b.inputs["Transmission Weight"].default_value = trans; b.inputs["IOR"].default_value = ior
    if emit: b.inputs["Emission Color"].default_value = emit + (1,); b.inputs["Emission Strength"].default_value = estr
    return m

def box(name, size, loc, mat, bevel=0.0, rot=(0,0,0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.object; o.name = name
    o.scale = size; bpy.ops.object.transform_apply(scale=True)
    if bevel > 0:
        md = o.modifiers.new("bv", "BEVEL"); md.width = bevel; md.segments = 2; md.limit_method = "ANGLE"
    o.data.materials.append(mat); return o

# ---------------- world / light ----------------
wd = bpy.data.worlds.new("W"); sc.world = wd; wd.use_nodes = True; wn = wd.node_tree
env = wn.nodes.new("ShaderNodeTexEnvironment"); env.image = img("qwantani_dusk_2_puresky_2k.hdr" if R2 else "kloofendal_48d_partly_cloudy_puresky_2k.hdr")
mp = wn.nodes.new("ShaderNodeMapping"); tc = wn.nodes.new("ShaderNodeTexCoord"); wn.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); wn.links.new(mp.outputs["Vector"], env.inputs["Vector"])
mp.inputs["Rotation"].default_value[2] = math.radians(200 if R2 else 0)
bg = wn.nodes["Background"]; wn.links.new(env.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.9 if R2 else 1.0
SUN_EL, SUN_AZ = (6.0 if R4 else 9.0), 205.0   # degrees; azimuth measured from +x toward +y
if R3:
    sky = wn.nodes.new("ShaderNodeTexSky"); sky.sky_type = "MULTIPLE_SCATTERING"; sky.sun_elevation = math.radians(SUN_EL); sky.sun_rotation = math.radians(SUN_AZ - 90)
    sky.sun_disc = True; sky.sun_size = math.radians(1.2); sky.air_density = 1.0; sky.aerosol_density = 2.2; sky.altitude = 300
    wn.links.new(sky.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.25
sun_d = bpy.data.lights.new("sun", "SUN")
sun_d.energy = 4.5 if R2 else 3.0; sun_d.angle = math.radians(1.2 if R2 else 3)
sun_d.color = (1.0, 0.72, 0.48) if R2 else (1, 0.95, 0.9)
sun = bpy.data.objects.new("sun", sun_d); sc.collection.objects.link(sun)
# R1: high afternoon sun. R2+: low golden sun behind-left of the building so glass and edges catch a rim
sun.rotation_euler = (math.radians(82 if R2 else 40), 0, math.radians(-128 if R2 else 30))
if R3:
    dvec = Vector((math.cos(math.radians(SUN_EL))*math.cos(math.radians(SUN_AZ)), math.cos(math.radians(SUN_EL))*math.sin(math.radians(SUN_AZ)), math.sin(math.radians(SUN_EL))))
    sun.rotation_euler = (-dvec).to_track_quat("-Z", "Y").to_euler(); sun_d.energy = 5.0; sun_d.angle = math.radians(0.6)
if R2:
    # aerial haze in a bounded volume box (a world volume would also swallow the sky at infinite distance)
    hz = bpy.data.materials.new("haze"); hz.use_nodes = True; hn = hz.node_tree; hn.nodes.remove(hn.nodes["Principled BSDF"])
    vol = hn.nodes.new("ShaderNodeVolumePrincipled"); vol.inputs["Density"].default_value = (0.0012 if R4 else 0.0019) if R3 else 0.0008
    vol.inputs["Color"].default_value = (0.95, 0.85, 0.75, 1); vol.inputs["Anisotropy"].default_value = 0.6
    hn.links.new(vol.outputs["Volume"], hn.nodes["Material Output"].inputs["Volume"])
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 60, 40)); hb = bpy.context.object; hb.name = "haze"; hb.scale = (700, 700, 110)
    hb.data.materials.append(hz); hb.visible_shadow = False
    cy.volume_step_rate = 6.0; cy.volume_max_steps = 128

# ---------------- terrain ----------------
def terrain():
    bm = bmesh.new(); S = 600.0; n = 240 if R2 else 120
    bmesh.ops.create_grid(bm, x_segments=n, y_segments=n, size=S/2)
    for v in bm.verts:
        x, y = v.co.x, v.co.y
        # plateau (cliff top) for y < 0, valley floor + lake beyond the cliff edge (y > 0)
        edge = 8.0 * math.sin(x * 0.02) + (4.0 * noise.noise(Vector((x*0.05, 0, 0))) + (3.0 * noise.noise(Vector((x*0.21, 3, 0))) if R4 else 0) if R2 else 0)
        dy = y - edge
        top = 34.0 + (1.2 if R2 else 3.0) * noise.fractal(Vector((x*0.01, y*0.01, 1)), 1.0, 2.0, 4)
        floor = (-9.0 if R2 else -2.0) + 6.0 * max(0, noise.fractal(Vector((x*0.006, y*0.006, 3)), 1.0, 2.0, 4))
        k = 1.0 / (1.0 + math.exp(dy * (0.9 if R2 else 0.35)))      # sharper cliff from round 2
        z = floor + (top - floor) * k
        if R2: z += 2.2 * noise.ridged_multi_fractal(Vector((x*0.04, y*0.04, 5)), 1.0, 2.0, 4, 0.0, 2.0) * k * (1-k) * 4   # rock strata on the cliff face
        # far mountains
        far = max(0.0, (y - 150) / 150.0) if not R3 else 0.62 * max(0.0, (math.hypot(x, y - 40) - 240) / 120.0)
        z += far * (90 + 60 * noise.fractal(Vector((x*0.008, 9, 0)), 1.0, 2.0, 5) + (25 * noise.ridged_multi_fractal(Vector((x*0.02, y*0.02, 2)), 1.0, 2.1, 6, 0.0, 2.0) if R2 else 0))
        if R4 and far > 0: z += far * 14 * noise.fractal(Vector((x*0.05, y*0.05, 7)), 1.0, 2.0, 4)
        v.co.z = z
    me = bpy.data.meshes.new("terrain"); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("terrain", me); sc.collection.objects.link(o)
    for p in me.polygons: p.use_smooth = True
    if R2:
        # slope-based material: rock on steep faces, ground on flat
        m = bpy.data.materials.new("terrainMix"); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; Lk = nt.links
        rock = pbr("rk", "rock_face_03", 0.08, (0.75, 0.68, 0.6)); grd = pbr("gr", "forest_ground_04", 0.12, (0.8, 0.85, 0.7))
        # merge by copying node groups is verbose: use two material slots by face slope instead
        o.data.materials.append(grd); o.data.materials.append(rock)
        for p in me.polygons: p.material_index = 1 if p.normal.z < 0.72 else 0
    else:
        o.data.materials.append(flat("ground", (0.25, 0.3, 0.18), 0.9))
    return o
terrain()
lake = bpy.data.objects.new("lake", bpy.data.meshes.new("lake")); sc.collection.objects.link(lake)
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=300); bm.to_mesh(lake.data); bm.free()
lake.location = (0, 150, 0.6)
WT = flat("water", (0.02, 0.05, 0.06), 0.03 if R2 else 0.1, 0, 0.0, 1.33)
if R2:
    wn_ = WT.node_tree; nz = wn_.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.5 if R3 else 0.35; bp = wn_.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.12
    tcw = wn_.nodes.new("ShaderNodeTexCoord"); wn_.links.new(tcw.outputs["Object"], nz.inputs["Vector"]); wn_.links.new(nz.outputs["Fac"], bp.inputs["Height"]); wn_.links.new(bp.outputs["Normal"], wn_.nodes["Principled BSDF"].inputs["Normal"])
lake.data.materials.append(WT)

# ---------------- the pavilion ----------------
CON = pbr("concrete", "concrete_wall_008", 0.6 if R4 else 0.25, (0.86, 0.83, 0.78) if R2 else (1, 1, 1)) if R2 else flat("concrete", (0.7, 0.7, 0.7), 0.6)
GLS = flat("glass", (0.9, 0.95, 1.0), 0.02, 0, 1.0, 1.45) if R2 else flat("glass", (0.6, 0.8, 0.9), 0.1, 0, 0.7)
MET = flat("bronze", (0.42, 0.3, 0.2), 0.32, 1.0)
if R3:
    mn = MET.node_tree; nzb = mn.nodes.new("ShaderNodeTexNoise"); nzb.inputs["Scale"].default_value = 3.0; mr = mn.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 0.22; mr.inputs["To Max"].default_value = 0.42; mn.links.new(nzb.outputs["Fac"], mr.inputs["Value"]); mn.links.new(mr.outputs["Result"], mn.nodes["Principled BSDF"].inputs["Roughness"])
WARM = flat("interior", (0.05, 0.04, 0.03), 0.6, 0, 0, 1.45, (1.0, 0.62, 0.32), 6.0 if R3 else 3.0)
GZ = 34.0  # cliff top height
L_, Wd, Hh = 34.0, 9.0, 5.2
y0 = -14.0  # building runs along +y and cantilevers past the cliff edge (y~0) by ~14 m
cx = 6.0
if not R2:
    box("slab", (Wd, L_, 0.6), (cx, y0 + L_/2, GZ + 0.3), CON)
    box("roof", (Wd, L_, 0.6), (cx, y0 + L_/2, GZ + Hh), CON)
    box("glassbox", (Wd - 0.4, L_ - 0.4, Hh - 0.6), (cx, y0 + L_/2, GZ + Hh/2 + 0.3), GLS)
else:
    # floor and roof plates taper to a knife edge at the cantilever tip (reads lighter, more "future")
    for nm_, z, th in (("slab", GZ + 0.35, 0.7), ("roof", GZ + Hh + 0.35, 0.55)):
        o = box(nm_, (Wd + 1.6, L_, th), (cx, y0 + L_/2, z), CON, 0.04)
    box("plinth", (Wd + 1.0, 11.0, 6.0), (cx, y0 + 5.0, GZ - 2.7), CON, 0.03)   # foundation sunk into the plateau
    box("core", (3.2, 8.0, Hh), (cx - 2.4, y0 + 4.5, GZ + Hh/2 + 0.35), CON, 0.03)   # stone service core anchors the cantilever into the rock
    box("glass", (Wd - 0.5, L_ - 1.2, Hh - 0.6), (cx, y0 + L_/2 + 0.2, GZ + Hh/2 + 0.35), GLS)
    SP = 3.2 if R3 else 1.6
    for i in range(int(L_ // SP)):
        y = y0 + 1.0 + i * SP
        for sx in (-1, 1):
            box("mull", (0.08, 0.08, Hh - 0.5), (cx + sx * (Wd/2 - 0.25), y, GZ + Hh/2 + 0.35), MET)
    box("glow", (Wd - 1.6, L_ - 4.0, 0.05), (cx, y0 + L_/2, GZ + Hh + 0.05), WARM)   # warm interior ceiling light
    # the "aperture": a bronze ring framing the valley at the cantilever tip
    if R4:
        MET.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.26, 0.105, 0.025, 1)
    bpy.ops.mesh.primitive_torus_add(major_radius=(3.6 if R4 else 2.3), minor_radius=(0.24 if R4 else 0.12), major_segments=96, location=(cx, y0 + L_ + 0.1, GZ + Hh/2 + 0.35), rotation=(math.radians(90), 0, 0))
    bpy.context.object.data.materials.append(MET)
    if R3 and not R4:
        # aperture blades inside the ring (6 thin bronze leaves) = brand signature
        for k in range(6):
            ang = k * math.pi / 3
            o = box("blade", (2.2, 0.03, 0.55), (cx + math.cos(ang) * 1.35, y0 + L_ + 0.12, GZ + Hh/2 + 0.35 + math.sin(ang) * 1.35), MET, 0.0, (0, ang + math.radians(60), 0))
            o.rotation_euler = (0, -(ang + math.radians(60)), 0)
        # still reflecting pool on the plateau + people for scale
        pass
    if R3 and not R4:
        box("pool", (14, 6, 0.1), (cx - 12, y0 + 6, GZ + 0.05), flat("poolwater", (0.01, 0.02, 0.025), 0.02, 0, 0, 1.33))
        for px, py in ((cx - 9, y0 + 2.0), (cx - 7.8, y0 + 2.4), (cx + 1.2, y0 + L_ - 3.0)):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=1.75, location=(px, py, GZ + 0.88)); bpy.context.object.data.materials.append(flat("person", (0.05, 0.05, 0.05), 0.7))

if R4:
    # one person at the glass tip for scale (body + head), dark silhouette against the light
    PM = flat("person", (0.04, 0.035, 0.03), 0.7)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=1.5, location=(cx + 1.0, y0 + L_ - 2.2, GZ + 0.7 + 0.75)); bpy.context.object.data.materials.append(PM)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(cx + 1.0, y0 + L_ - 2.2, GZ + 0.7 + 1.62)); bpy.context.object.data.materials.append(PM)
# scattered boulders on the plateau (R2+) for foreground depth
if R2:
    RK = pbr("boulder", "aerial_rocks_02", 0.35, (0.7, 0.65, 0.6))
    import random; random.seed(7)
    for i in range(14):
        x = random.uniform(-40, 30); y = random.uniform(-60, -18); s = random.uniform(0.8, 3.2)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=s, location=(x, y, GZ - s * 0.35))
        o = bpy.context.object; o.scale = (1, random.uniform(0.7, 1.3), random.uniform(0.5, 0.8))
        d = o.modifiers.new("d", "DISPLACE"); tx = bpy.data.textures.new("rt%d" % i, "CLOUDS"); tx.noise_scale = 0.9; d.texture = tx; d.strength = s * 0.35
        o.data.materials.append(RK); bpy.ops.object.shade_smooth()

# ---------------- camera ----------------
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam
if not R2:
    cam.location = (-40, -40, 60); tgt = Vector((cx, 0, GZ))
    cam_d.lens = 35
else:
    # low three-quarter view from the cliff top: building cuts the horizon, valley + far mountains behind, boulders in the foreground
    P0, P1 = Vector((-34, -46, GZ + 3.2)), Vector((-20, -30, GZ + 2.4))
    t = 0.0
    if ANIM: i, n = map(int, ANIM.split("/")); t = i / max(1, n - 1); t = t * t * (3 - 2 * t)
    P0, P1 = Vector((-58, 22, GZ + 6.0)), Vector((-44, 16, GZ + 3.5))
    cam.location = P0.lerp(P1, t) if ANIM else Vector((-52, 19, GZ + 4.5))
    tgt = Vector((cx, y0 + L_ * 0.55, GZ + Hh * 0.2))
    cam_d.lens = 32
    if R3:
        tip = Vector((cx, y0 + L_, GZ + Hh/2 + 0.35))
        Q0, Q1 = tip + Vector((-24, 31, -12)), tip + Vector((-17, 24, -6))
        cam.location = Q0.lerp(Q1, t) if ANIM else tip + Vector((-20, 27, -8))
        tgt = tip + Vector((-2.0, -9.0, 2.5)); cam_d.lens = 28
        if R4:
            cam.location = tip + (Q0.lerp(Q1, t) - tip if ANIM else Vector((-20, 27, -8))) * 1.25 + Vector((0, 0, -1.5))
            tgt = tip + Vector((1.5, -17.0, 1.8)); cam_d.lens = 35
        cam_d.dof.use_dof = True; cam_d.dof.focus_distance = (tgt - cam.location).length; cam_d.dof.aperture_fstop = 5.6 if R4 else 8.0
d = tgt - cam.location; cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
cam_d.clip_end = 2000
NALL = int(os.environ.get("ANIMALL", "0"))
if NALL and R4:
    # whole camera move in one process (scene built once): slow crane-down dolly toward the aperture
    tip = Vector((cx, y0 + L_, GZ + Hh/2 + 0.35)); cy.use_animated_seed = True
    for i in range(NALL):
        t = i / (NALL - 1); t = t * t * (3 - 2 * t)
        cam.location = tip + (Q0.lerp(Q1, t) - tip) * 1.25 + Vector((0, 0, -1.5))
        d = tgt - cam.location; cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler(); cam_d.dof.focus_distance = d.length
        sc.frame_set(i + 1); sc.render.filepath = OUT.replace("####", "%04d" % i); bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(write_still=True)
print("DONE", OUT)
