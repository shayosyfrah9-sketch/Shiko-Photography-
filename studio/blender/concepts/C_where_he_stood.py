# SHIKO WORLD 2.0 — Concept C "WHERE HE STOOD", round 1 (Rendered, Blender 5.3 Cycles CPU).
# A sunset tidal flat where time is held: a frozen breaking wave with its spray curtain, a festival tapestry with
# confetti + water spray hanging beneath it, Maccabi-yellow ticker tape in floodlight beams over a turf patch,
# a pine-grove edge with backlit dust and a lifted linen sheet; footprints in the wet sand where Shay stood.
# Every suspended thing is a physical object with a real material (water spheres IOR 1.333, paper with translucency,
# linen, turf); nothing emits except the floodlights.
#
# Run:  /tmp/claude-0/bpyenv/bin/python C_where_he_stood.py -- SHOT OUT.png [W H SPP]
#   SHOT = overview | surf     (key frame 1 / key frame 2 of the visualisation plan in studio/concepts/CONCEPTS.md)
# Assets (Poly Haven, CC0): industrial_sunset_02_puresky (HDRI), damp_beach_sand, rough_linen (textures),
#   pine_tree_01, flood_lights, football (models). Cache dir: $PH (default below).
import bpy, bmesh, sys, math, os, random, json
from mathutils import Vector, Matrix, noise

a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["overview", "/tmp/c.png"]
SHOT = a[0]; OUT = a[1]
W = int(a[2]) if len(a) > 2 else 854; H = int(a[3]) if len(a) > 3 else 480; SPP = int(a[4]) if len(a) > 4 else 24
PH = os.environ.get("PH", "/tmp/claude-0/-home-user/2c38ec15-b058-5d59-86c9-28307ce7ab10/scratchpad/ph/")
NOTREES = os.environ.get("NOTREES") == "1"
OVER = SHOT == "overview"
random.seed(11)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = "CYCLES"; cy = sc.cycles
cy.device = "CPU"; cy.samples = SPP; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02
cy.use_denoising = True
try: cy.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
cy.max_bounces = 16; cy.diffuse_bounces = 3; cy.glossy_bounces = 4; cy.transmission_bounces = 14; cy.volume_bounces = 1
cy.transparent_max_bounces = 16
cy.sample_clamp_indirect = 10; cy.blur_glossy = 1.0; cy.caustics_reflective = False; cy.caustics_refractive = False
cy.volume_step_rate = float(os.environ.get("VSTEP", "4.0")); cy.volume_max_steps = 96
sc.render.resolution_x = W; sc.render.resolution_y = H; sc.render.filepath = OUT
sc.render.threads_mode = "FIXED"; sc.render.threads = int(os.environ.get("THREADS", "4"))
sc.view_settings.view_transform = "AgX"
try: sc.view_settings.look = os.environ.get("LOOK", "AgX - Punchy")
except Exception: pass
sc.view_settings.exposure = float(os.environ.get("EXPO", "-0.6"))

# ------------------------------------------------------------------ helpers
def node_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes["Principled BSDF"], m.node_tree.nodes["Material Output"]

def img(path, nc=False):
    i = bpy.data.images.load(PH + path, check_existing=True)
    if nc: i.colorspace_settings.name = "Non-Color"
    return i

def shadow_transparent(m):
    """Fake caustics: shadow rays pass through thin water (puddles, drops) instead of being blocked by glass."""
    N = m.node_tree.nodes; L = m.node_tree.links; out = N["Material Output"]
    src = out.inputs["Surface"].links[0].from_socket
    lp = N.new("ShaderNodeLightPath"); tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader")
    L.new(lp.outputs["Is Shadow Ray"], mx.inputs[0]); L.new(src, mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], out.inputs["Surface"])

def link(o):
    sc.collection.objects.link(o); return o

def mesh_obj(name, verts, faces, mat=None, smooth=False):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    o = link(bpy.data.objects.new(name, me))
    if mat: me.materials.append(mat)
    return o

def points_obj(name, pts, radii, mat):
    """Point cloud of real spheres (Cycles renders points natively): mesh verts -> Mesh to Points (GN)."""
    me = bpy.data.meshes.new(name); me.vertices.add(len(pts))
    me.vertices.foreach_set("co", [c for p in pts for c in p]); me.update()
    at = me.attributes.new("rad", "FLOAT", "POINT"); at.data.foreach_set("value", radii)
    o = link(bpy.data.objects.new(name, me))
    ng = bpy.data.node_groups.new(name + "_gn", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes; L = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    mp = N.new("GeometryNodeMeshToPoints"); na = N.new("GeometryNodeInputNamedAttribute"); na.data_type = "FLOAT"; na.inputs["Name"].default_value = "rad"
    sm = N.new("GeometryNodeSetMaterial"); sm.inputs["Material"].default_value = mat
    L.new(gi.outputs[0], mp.inputs["Mesh"]); L.new(na.outputs["Attribute"], mp.inputs["Radius"])
    L.new(mp.outputs["Points"], sm.inputs["Geometry"]); L.new(sm.outputs["Geometry"], go.inputs[0])
    md = o.modifiers.new("pts", "NODES"); md.node_group = ng
    return o

def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t)

def look_at(obj, target):
    d = Vector(target) - obj.location; obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

# ------------------------------------------------------------------ layout (metres; +z up; azimuth from +x toward +y)
SUN_EL, SUN_AZ = 2.24, 70.0             # sun of the HDRI (measured: elevation 2.24 deg) rotated to azimuth 70
sund = Vector((math.cos(math.radians(SUN_EL)) * math.cos(math.radians(SUN_AZ)),
               math.cos(math.radians(SUN_EL)) * math.sin(math.radians(SUN_AZ)), math.sin(math.radians(SUN_EL))))
W0 = Vector((21.0, 58.0, 0)); TS = Vector((-0.3, 0.954, 0)).normalized()   # shoreline point + direction
NL = Vector((-TS.y, TS.x, 0)) * -1                                           # unit normal pointing to land
if NL.dot(Vector((-1, 0, 0))) < 0: NL = -NL
def seaward(x, y): return -((Vector((x, y, 0)) - W0).dot(NL))               # >0 = sea side
WH = 4.0                                   # wave crest height (m)
C = W0 - NL * 7.0                          # crest line centre (in the sea, 7 m out)
D0 = 120.0                                 # surf vantage distance (200 mm lens)
T = C + NL * (0.75 * WH) + Vector((0, 0, WH + 1.5))      # aim point of the surf vantage (just above the lip)
AZV = SUN_AZ + 2.86                        # view azimuth: sun sits 2.86 deg right of centre (right third)
fwd_h = Vector((math.cos(math.radians(AZV)), math.sin(math.radians(AZV)), 0))
V = T - fwd_h * D0; V.z = 0.0              # where he stood
CAMV = V + Vector((0, 0, 1.2))
O = Vector((T.x, T.y, 0)) - Vector((math.cos(math.radians(80)), math.sin(math.radians(80)), 0)) * 95.0 + Vector((0, 0, 14.0))  # overview cam: wave 12 deg right of centre
YAW_O = 92.0
def at_az(az, dist, z=0.0): return Vector((O.x + dist * math.cos(math.radians(az)), O.y + dist * math.sin(math.radians(az)), z))
CANOPY = at_az(YAW_O + 12.0, 64)
TICK = at_az(YAW_O + 4.5, 150)
PINES = at_az(YAW_O + 22.0, 165)
TRAIL0 = at_az(YAW_O + 27.0, 33)
PAIRC = at_az(YAW_O + 11.0, 50)      # festival vantage: footprints facing the tapestry
print("layout V", V, "O", O, "canopy", CANOPY, "tick", TICK, "pines", PINES, "sea(tick)", seaward(TICK.x, TICK.y))

# surf-vantage camera frame (also used to carve the surfer-shaped absence)
cf = (T - CAMV).normalized(); cr = cf.cross(Vector((0, 0, 1))).normalized(); cu = cr.cross(cf)
PHOTO_W, PHOTO_H = 1500 / 132.0, 1238 / 132.0       # surf0001 at subject scale (board ~1.75 m = 232 px)
CREST_U = (C + Vector((0, 0, WH)) - CAMV).dot(cu) * D0 / (C + Vector((0, 0, WH)) - CAMV).dot(cf)
RECT = dict(left=-2.6 - PHOTO_W * 0.55, top=CREST_U + 0.62 * PHOTO_H)   # photo y=0.62 (its crest) on the 3D crest
RECT["w"] = PHOTO_W; RECT["h"] = PHOTO_H
SIL = [  # surfer + board silhouette traced from surf0001 (photo fractions x right, y down)
    [(0.625, .235), (.64, .222), (.66, .235), (.69, .27), (.70, .31), (.70, .37), (.695, .42), (.68, .445), (.645, .44), (.60, .40), (.575, .37), (.58, .345), (.60, .335), (.62, .31), (.615, .27)],
    [(.535, .28), (.545, .285), (.60, .30), (.66, .29), (.665, .315), (.60, .32), (.545, .297)],
    [(.575, .35), (.59, .37), (.545, .44), (.535, .465), (.515, .47), (.52, .445)],
    [(.555, .35), (.585, .42), (.575, .47), (.545, .51), (.50, .525), (.47, .505), (.47, .45), (.49, .39), (.52, .355)]]
def ph2plane(px, py): return (RECT["left"] + px * RECT["w"], RECT["top"] - py * RECT["h"])
SILP = [[ph2plane(*p) for p in poly] for poly in SIL]
def in_poly(x, y, poly):
    c = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1: c = not c
    return c
def proj(p):
    d = Vector(p) - CAMV; dep = d.dot(cf)
    return (d.dot(cr) * D0 / dep, d.dot(cu) * D0 / dep, dep)
def in_sil(p, pad=0.0):
    x, y, dep = proj(p)
    if abs(dep - D0) > 14: return False
    return any(in_poly(x, y, poly) for poly in SILP)
json.dump(dict(rect=RECT, frame_w=2 * D0 * 18 / 200.0, frame_h=2 * D0 * 10.125 / 200.0, note="plane coords (m) at D0, x right, y up, origin = frame centre"),
          open(os.path.splitext(OUT)[0] + "_register.json", "w"))

# ------------------------------------------------------------------ world: CC0 HDRI sky + matching sun lamp
wd = bpy.data.worlds.new("W"); sc.world = wd; wd.use_nodes = True; wn = wd.node_tree
env = wn.nodes.new("ShaderNodeTexEnvironment"); env.image = img("industrial_sunset_02_puresky_4k.hdr")
mpn = wn.nodes.new("ShaderNodeMapping"); tc = wn.nodes.new("ShaderNodeTexCoord")
wn.links.new(tc.outputs["Generated"], mpn.inputs["Vector"]); wn.links.new(mpn.outputs["Vector"], env.inputs["Vector"])
# Cycles equirect: u = 0.5 - atan2(y,x)/2pi. Sun at u=0.600 -> texture azimuth -36 deg; rotate so it lands at SUN_AZ
mpn.inputs["Rotation"].default_value[2] = math.radians(-36.0 - SUN_AZ)
bg = wn.nodes["Background"]
# grade the CC0 sky toward the concept's apricot (#f0b27a): +saturation, warm multiply (documented art-direction, not a new sky)
hsv = wn.nodes.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = float(os.environ.get("SKYSAT", "2.0")); hsv.inputs["Hue"].default_value = 0.515
wn.links.new(env.outputs["Color"], hsv.inputs["Color"])
wm_ = wn.nodes.new("ShaderNodeMixRGB"); wm_.blend_type = "MULTIPLY"; wm_.inputs[0].default_value = 1.0; wm_.inputs[2].default_value = (1.0, 0.8, 0.6, 1)
wn.links.new(hsv.outputs["Color"], wm_.inputs[1])
# sunset sky anisotropy: the sky away from the sun is dimmer than this low-contrast capture suggests (graded, documented)
dsun = wn.nodes.new("ShaderNodeVectorMath"); dsun.operation = "DOT_PRODUCT"; dsun.inputs[1].default_value = sund.to_tuple()
wn.links.new(tc.outputs["Generated"], dsun.inputs[0])
mrs = wn.nodes.new("ShaderNodeMapRange"); mrs.inputs["From Min"].default_value = -1.0; mrs.inputs["From Max"].default_value = 1.0
mrs.inputs["To Min"].default_value = float(os.environ.get("ANTI", "0.28")); mrs.inputs["To Max"].default_value = 1.15; wn.links.new(dsun.outputs["Value"], mrs.inputs["Value"])
pw_ = wn.nodes.new("ShaderNodeMath"); pw_.operation = "POWER"; pw_.inputs[1].default_value = 1.6; wn.links.new(mrs.outputs["Result"], pw_.inputs[0])
# warm toward the sun, cool (earth-shadow blue-violet) away from it: warm key / cool fill
tf = wn.nodes.new("ShaderNodeMapRange"); tf.inputs["From Min"].default_value = -0.3; tf.inputs["From Max"].default_value = 0.85; wn.links.new(dsun.outputs["Value"], tf.inputs["Value"])
tm = wn.nodes.new("ShaderNodeMixRGB"); tm.inputs[1].default_value = (0.62, 0.72, 1.0, 1); tm.inputs[2].default_value = (1.0, 1.0, 1.0, 1); wn.links.new(tf.outputs["Result"], tm.inputs[0])
wm2 = wn.nodes.new("ShaderNodeMixRGB"); wm2.blend_type = "MULTIPLY"; wm2.inputs[0].default_value = 1.0; wn.links.new(pw_.outputs[0], wm2.inputs[1]); wn.links.new(tm.outputs[0], wm2.inputs[2])
pw_ = wm2
gm = wn.nodes.new("ShaderNodeMixRGB"); gm.blend_type = "MULTIPLY"; gm.inputs[0].default_value = 1.0
wn.links.new(wm_.outputs[0], gm.inputs[1]); wn.links.new(pw_.outputs[0], gm.inputs[2]); wn.links.new(gm.outputs[0], bg.inputs["Color"]); bg.inputs["Strength"].default_value = float(os.environ.get("SKY", "0.6"))
sun_d = bpy.data.lights.new("sun", "SUN"); sun_d.energy = float(os.environ.get("SUNE", "8.0")); sun_d.angle = math.radians(0.55)
sun_d.color = (1.0, 0.56, 0.30)
sun = link(bpy.data.objects.new("sun", sun_d)); sun.rotation_euler = (-sund).to_track_quat("-Z", "Y").to_euler()

# ------------------------------------------------------------------ ground: wet tidal flat (height field) + one water plane
def fbm(x, y, s, oc=4, seed=0.0): return noise.fractal(Vector((x / s, y / s, seed)), 1.0, 2.0, oc)
TRAIL = []   # filled below; list of (pos, heading_deg, side, depth)
def trail_pts():
    pts = []; p0 = TRAIL0; p1 = PAIRC.copy(); d = (p1 - p0); L_ = d.length; d.normalize(); side = Vector((-d.y, d.x, 0))
    n = int(L_ / 0.74)
    for i in range(n):
        t = i / n; c = p0 + d * (L_ * t) + side * (0.035 * math.sin(i * 0.7))   # slight wander
        sgn = 1 if i % 2 == 0 else -1
        hd = math.degrees(math.atan2(d.y, d.x)) + random.uniform(-6, 6) + sgn * 4
        pts.append((c + side * (0.11 * sgn), hd, sgn, 0.022))
    for (Pp, hdv) in ((V, AZV), (PAIRC, math.degrees(math.atan2(CANOPY.y - PAIRC.y, CANOPY.x - PAIRC.x)))):
        sidev = Vector((-math.sin(math.radians(hdv)), math.cos(math.radians(hdv)), 0))
        pts.append((Pp + sidev * 0.15, hdv - 8, 1, 0.032)); pts.append((Pp - sidev * 0.15, hdv + 6, -1, 0.032))  # standing pair
    return pts
TRAIL = trail_pts()
def dist_to_trail(x, y):
    p = Vector((x, y, 0)); a_, b_ = TRAIL0, PAIRC
    ab = b_ - a_; t = max(0, min(1, (p - a_).dot(ab) / ab.length_squared)); return (a_ + ab * t - p).length

def height(x, y):
    s = seaward(x, y)
    h = 0.004 + 0.016 * fbm(x, y, 22.0, 4, 1.3) + 0.006 * fbm(x, y, 5.0, 3, 7.1)
    h -= 0.0006 * max(0.0, s + 60.0)               # flat tilts gently toward the sea
    if s > 0: h -= min(3.0, 0.3 * s)             # shelf under the sea
    # low dry dune under the pines, dry pads under the held moments
    dp = (Vector((x, y, 0)) - PINES).length; h += 0.25 * (1 - smoothstep(12, 40, dp))
    if dist_to_trail(x, y) < 1.6: h = max(h, 0.013)
    for c_, r_ in ((TICK, 13.0), (CANOPY, 7.0)):
        dd = (Vector((x, y, 0)) - c_).length
        if dd < r_ + 4: h = max(h, 0.012 * (1 - smoothstep(r_, r_ + 4, dd)) + h * smoothstep(r_, r_ + 4, dd))
    return h

def warp(u, k):   # dense near the centre, coarse far away
    return u * (1 + k * u * u)
def sand_mesh(cx, cy, n, half, k):
    verts = []; faces = []
    for j in range(n + 1):
        v = -1 + 2 * j / n
        for i in range(n + 1):
            u = -1 + 2 * i / n
            x = cx + warp(u, k) * half / (1 + k); y = cy + warp(v, k) * half / (1 + k)
            verts.append((x, y, height(x, y)))
    for j in range(n):
        for i in range(n):
            q = j * (n + 1) + i; faces.append((q, q + 1, q + n + 2, q + n + 1))
    return verts, faces

# sand material: Poly Haven damp_beach_sand + macro variation + ripples + wet/dry + depth tint under water
ms, N, L, bs, mo = node_mat("wet_sand")
tco = N.new("ShaderNodeTexCoord"); geo = N.new("ShaderNodeNewGeometry")
mp1 = N.new("ShaderNodeMapping"); mp1.inputs["Scale"].default_value = (0.55, 0.55, 0.55); L.new(tco.outputs["Object"], mp1.inputs["Vector"])
def tex(fn, nc, vec):
    t = N.new("ShaderNodeTexImage"); t.image = img(fn, nc); L.new(vec, t.inputs["Vector"]); return t
td = tex("damp_beach_sand_diff_2k.jpg", False, mp1.outputs["Vector"]); trr = tex("damp_beach_sand_rough_2k.jpg", True, mp1.outputs["Vector"])
tn = tex("damp_beach_sand_nor_gl_2k.jpg", True, mp1.outputs["Vector"])
macro = N.new("ShaderNodeTexNoise"); macro.inputs["Scale"].default_value = 0.025; macro.inputs["Detail"].default_value = 6; L.new(tco.outputs["Object"], macro.inputs["Vector"])
mrm = N.new("ShaderNodeMapRange"); mrm.inputs["To Min"].default_value = 0.55; mrm.inputs["To Max"].default_value = 1.25; L.new(macro.outputs["Fac"], mrm.inputs["Value"])
sepz = N.new("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Position"], sepz.inputs["Vector"])
wet = N.new("ShaderNodeMapRange"); wet.inputs["From Min"].default_value = 0.05; wet.inputs["From Max"].default_value = 0.18; L.new(sepz.outputs["Z"], wet.inputs["Value"])   # 0 wet .. 1 dry
dep = N.new("ShaderNodeMapRange"); dep.inputs["From Min"].default_value = 0.0; dep.inputs["From Max"].default_value = -0.6; L.new(sepz.outputs["Z"], dep.inputs["Value"])   # 0 at surface .. 1 deep
c1 = N.new("ShaderNodeMixRGB"); c1.blend_type = "MULTIPLY"; c1.inputs[0].default_value = 1.0; L.new(td.outputs["Color"], c1.inputs[1])
cm = N.new("ShaderNodeCombineXYZ"); L.new(mrm.outputs["Result"], cm.inputs[0]); L.new(mrm.outputs["Result"], cm.inputs[1]); L.new(mrm.outputs["Result"], cm.inputs[2]); L.new(cm.outputs[0], c1.inputs[2])
wetcol = N.new("ShaderNodeMixRGB"); wetcol.blend_type = "MULTIPLY"; wetcol.inputs[0].default_value = 1.0; wetcol.inputs[2].default_value = (0.5, 0.47, 0.45, 1); L.new(c1.outputs[0], wetcol.inputs[1])
drywet = N.new("ShaderNodeMixRGB"); L.new(wet.outputs["Result"], drywet.inputs[0]); L.new(wetcol.outputs[0], drywet.inputs[1]); L.new(c1.outputs[0], drywet.inputs[2])
deep = N.new("ShaderNodeMixRGB"); L.new(dep.outputs["Result"], deep.inputs[0]); L.new(drywet.outputs[0], deep.inputs[1]); deep.inputs[2].default_value = (0.012, 0.05, 0.055, 1)
L.new(deep.outputs[0], bs.inputs["Base Color"])
rgh = N.new("ShaderNodeMapRange"); rgh.inputs["To Min"].default_value = 0.22; rgh.inputs["To Max"].default_value = 0.9; L.new(wet.outputs["Result"], rgh.inputs["Value"])
rmul = N.new("ShaderNodeMath"); rmul.operation = "MULTIPLY"; L.new(rgh.outputs["Result"], rmul.inputs[0]); L.new(trr.outputs["Color"], rmul.inputs[1])
rmul2 = N.new("ShaderNodeMath"); rmul2.operation = "MULTIPLY"; rmul2.inputs[1].default_value = 1.4; L.new(rmul.outputs[0], rmul2.inputs[0]); L.new(rmul2.outputs[0], bs.inputs["Roughness"])
# sand ripples (tidal ripple marks ~9 cm), distorted
wv = N.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 11.0; wv.inputs["Distortion"].default_value = 9.0; wv.inputs["Detail"].default_value = 3
wv.inputs["Detail Scale"].default_value = 0.6; L.new(tco.outputs["Object"], wv.inputs["Vector"])
nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.8; L.new(tn.outputs["Color"], nm.inputs["Color"])
bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25; bp.inputs["Distance"].default_value = 0.01
L.new(wv.outputs["Fac"], bp.inputs["Height"]); L.new(nm.outputs["Normal"], bp.inputs["Normal"]); L.new(bp.outputs["Normal"], bs.inputs["Normal"])
SAND = ms

sc_c = (O + Vector((0, 70, 0))) if OVER else (V + fwd_h * 70)
v_, f_ = sand_mesh(sc_c.x, sc_c.y, 800, 3500.0, 20.0)
sand = mesh_obj("sand", v_, f_, SAND, smooth=True)

# water plane: one surface over everything (shallow film on the flat, open sea beyond the shoreline)
mw, N, L, bw, mo = node_mat("water")
bw.inputs["Base Color"].default_value = (1, 1, 1, 1); bw.inputs["Transmission Weight"].default_value = 1.0; bw.inputs["IOR"].default_value = 1.333
bw.inputs["Roughness"].default_value = 0.012
at = N.new("ShaderNodeAttribute"); at.attribute_name = "sea"
tcw = N.new("ShaderNodeTexCoord")
n1 = N.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = 0.35; n1.inputs["Detail"].default_value = 8; n1.inputs["Roughness"].default_value = 0.62
mpw = N.new("ShaderNodeMapping"); mpw.inputs["Scale"].default_value = (1.0, 3.2, 1.0); mpw.inputs["Rotation"].default_value[2] = math.radians(SUN_AZ - 90 + 107)
L.new(tcw.outputs["Object"], mpw.inputs["Vector"]); L.new(mpw.outputs["Vector"], n1.inputs["Vector"])
n2 = N.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 4.0; n2.inputs["Detail"].default_value = 4; L.new(tcw.outputs["Object"], n2.inputs["Vector"])
st = N.new("ShaderNodeMapRange"); st.inputs["To Min"].default_value = 0.015; st.inputs["To Max"].default_value = 0.6; L.new(at.outputs["Fac"], st.inputs["Value"])
bpw = N.new("ShaderNodeBump"); bpw.inputs["Distance"].default_value = 0.6; L.new(st.outputs["Result"], bpw.inputs["Strength"]); L.new(n1.outputs["Fac"], bpw.inputs["Height"])
st2 = N.new("ShaderNodeMapRange"); st2.inputs["To Min"].default_value = 0.03; st2.inputs["To Max"].default_value = 0.3; L.new(at.outputs["Fac"], st2.inputs["Value"])
bpw2 = N.new("ShaderNodeBump"); L.new(st2.outputs["Result"], bpw2.inputs["Strength"]); bpw2.inputs["Distance"].default_value = 0.08; L.new(n2.outputs["Fac"], bpw2.inputs["Height"]); L.new(bpw2.outputs["Normal"], bpw.inputs["Normal"])
L.new(bpw.outputs["Normal"], bw.inputs["Normal"])
shadow_transparent(mw); WATER = mw

def water_grid(cx, cy, half, n):
    verts = []; faces = []; sea = []
    for j in range(n + 1):
        for i in range(n + 1):
            x = cx - half + 2 * half * i / n; y = cy - half + 2 * half * j / n
            verts.append((x, y, 0.0)); sea.append(smoothstep(-3, 10, seaward(x, y)))
    for j in range(n):
        for i in range(n):
            q = j * (n + 1) + i; faces.append((q, q + 1, q + n + 2, q + n + 1))
    o = mesh_obj("water", verts, faces, WATER)
    atr = o.data.attributes.new("sea", "FLOAT", "POINT"); atr.data.foreach_set("value", sea)
    return o
WCX, WCY, WHALF = O.x, O.y + 600, 1500.0
water_grid(WCX, WCY, WHALF, 300)
# far ring out to the horizon (open sea, sea=1)
R = 40000.0
ring_v = [(WCX - WHALF, WCY - WHALF, 0), (WCX + WHALF, WCY - WHALF, 0), (WCX + WHALF, WCY + WHALF, 0), (WCX - WHALF, WCY + WHALF, 0),
          (WCX - R, WCY - R, 0), (WCX + R, WCY - R, 0), (WCX + R, WCY + R, 0), (WCX - R, WCY + R, 0)]
ring = mesh_obj("sea_far", ring_v, [(0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], WATER)
ra = ring.data.attributes.new("sea", "FLOAT", "POINT"); ra.data.foreach_set("value", [1.0] * 8)
# far sea floor under the ring so the water reads deep teal, not the HDRI ground
mesh_obj("seafloor_far", [(v[0], v[1], -3.0) for v in ring_v], [(0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], SAND)

# ------------------------------------------------------------------ the held wave
prof_plunge = [(-5, -.15), (-3, .12), (-1.6, .4), (-.8, .68), (-.3, .88), (.05, .98), (.3, 1.0), (.55, .95), (.72, .82), (.74, .74),
               (.64, .76), (.48, .83), (.33, .8), (.2, .66), (.12, .45), (.12, .25), (.2, .08), (.45, -.15)]
prof_spill = [(-5, -.15), (-3, .12), (-1.6, .4), (-.8, .68), (-.3, .88), (.05, .98), (.25, .97), (.4, .88), (.5, .74), (.56, .6),
              (.6, .5), (.63, .42), (.66, .33), (.7, .24), (.76, .15), (.85, .07), (.95, 0.0), (.75, -.15)]
LIP_IDX = 9; CREST_IDX = 5
WL = 190.0; NR = 380
wave_v = []; wave_f = []; foam = []; lipline = []; crestline = []
for k in range(NR + 1):
    w = -WL / 2 + WL * k / NR
    e = math.exp(-(w / 9.0) ** 2) if w < 0 else math.exp(-(w / 22.0) ** 2)    # peak, longer shoulder peeling right
    e *= 1 + 0.06 * noise.noise(Vector((w * 0.08, 0.5, 2.0)))
    broken = smoothstep(-5.0, -14.0, w)                     # left of the peak the wave has already broken: low whitewater
    env = (0.72 + 0.28 * e) if w >= 0 else max(e, 0.4 * (1 - smoothstep(-22.0, -40.0, w)))   # a long wall with a peak, not a dome
    env *= 1 - smoothstep(40.0, 75.0, w)                    # the shoulder fades into the sea, no hard ends
    hsc = WH * env + 0.03
    c = math.exp(-((w + 2.0) / (5.0 if w < -2 else 9.0)) ** 2) * (0.85 + 0.15 * noise.noise(Vector((w * 0.3, 1.1, 0)))) * float(os.environ.get("CURL", "0.5"))   # the lip throws hardest at one point
    base = C + TS * w
    ring_pts = []
    for idx, (pp, ps) in enumerate(zip(prof_plunge, prof_spill)):
        u = ps[0] + (pp[0] - ps[0]) * c; v = ps[1] + (pp[1] - ps[1]) * c
        jitter = (0.025 if idx < 8 else 0.012) * noise.noise(Vector((w * 0.25, idx * 0.37, 5.0)))
        P = base + NL * (u * hsc) + Vector((0, 0, v * hsc + jitter * hsc))
        if v < 0: P.z = v * 2.0      # sink the base below the water plane
        wave_v.append(P.to_tuple())
        fm = 0.0
        if idx in (8, 9): fm = 0.45 * c
        if v < 0.16 and idx > 13: fm = 1.0
        if v > -0.05: fm = max(fm, broken * 1.2)
        foam.append(fm)
    lipline.append((Vector(wave_v[-len(prof_plunge) + LIP_IDX]), e, w))
    crestline.append((Vector(wave_v[-len(prof_plunge) + CREST_IDX]), e, w))
NP = len(prof_plunge)
for k in range(NR):
    for i in range(NP):
        a0 = k * NP + i; a1 = k * NP + (i + 1) % NP; b0 = a0 + NP; b1 = a1 + NP
        wave_f.append((a0, a1, b1, b0))
wave_f.append(tuple(range(NP))[::-1]); wave_f.append(tuple(range(NR * NP, NR * NP + NP)))
mwv, N, L, bwv, mo = node_mat("wave_water")
bwv.inputs["Base Color"].default_value = (0.85, 1.0, 0.95, 1); bwv.inputs["Transmission Weight"].default_value = 1.0; bwv.inputs["IOR"].default_value = 1.333
bwv.inputs["Roughness"].default_value = 0.05
vab = N.new("ShaderNodeVolumeAbsorption"); vab.inputs["Color"].default_value = (0.04, 0.55, 0.42, 1); vab.inputs["Density"].default_value = float(os.environ.get("ABS", "6.0"))
vsc = N.new("ShaderNodeVolumeScatter"); vsc.inputs["Color"].default_value = (0.35, 0.9, 0.7, 1); vsc.inputs["Density"].default_value = 0.25; vsc.inputs["Anisotropy"].default_value = 0.75
adv = N.new("ShaderNodeAddShader"); L.new(vab.outputs[0], adv.inputs[0]); L.new(vsc.outputs[0], adv.inputs[1])
L.new(vab.outputs[0], mo.inputs["Volume"])   # absorption only: scatter inside a closed glass body gets no direct sun (no caustics) and went olive
# whitewater: rough, translucent, ivory (never pure white); mask from per-vertex foam + noise
fa = N.new("ShaderNodeAttribute"); fa.attribute_name = "foam"
fn_ = N.new("ShaderNodeTexNoise"); fn_.inputs["Scale"].default_value = 1.6; fn_.inputs["Detail"].default_value = 10; fn_.inputs["Roughness"].default_value = 0.7
fm_ = N.new("ShaderNodeMath"); fm_.operation = "MULTIPLY"; L.new(fa.outputs["Fac"], fm_.inputs[0]); L.new(fn_.outputs["Fac"], fm_.inputs[1])
fr = N.new("ShaderNodeMapRange"); fr.inputs["From Min"].default_value = 0.2; fr.inputs["From Max"].default_value = 0.34; L.new(fm_.outputs[0], fr.inputs["Value"])
foamb = N.new("ShaderNodeBsdfPrincipled"); foamb.inputs["Base Color"].default_value = (0.78, 0.78, 0.74, 1); foamb.inputs["Roughness"].default_value = 0.5
trl = N.new("ShaderNodeBsdfTranslucent"); trl.inputs["Color"].default_value = (0.75, 0.8, 0.75, 1)
fmix = N.new("ShaderNodeMixShader"); fmix.inputs[0].default_value = 0.45; L.new(foamb.outputs[0], fmix.inputs[1]); L.new(trl.outputs[0], fmix.inputs[2])
smix = N.new("ShaderNodeMixShader"); L.new(fr.outputs["Result"], smix.inputs[0]); L.new(bwv.outputs[0], smix.inputs[1]); L.new(fmix.outputs[0], smix.inputs[2])
L.new(smix.outputs[0], mo.inputs["Surface"])
if os.environ.get("DBG") == "nofoam": L.new(bwv.outputs[0], mo.inputs["Surface"])
if os.environ.get("DBG") == "novol": N.remove(adv)
# water-face detail: vertical streaks (water drawn up the face) + wind chop; breaks the sky reflection like real water
tcv = N.new("ShaderNodeTexCoord")
mpv = N.new("ShaderNodeMapping"); mpv.inputs["Scale"].default_value = (1.6, 1.6, 0.22); L.new(tcv.outputs["Object"], mpv.inputs["Vector"])
nzw = N.new("ShaderNodeTexNoise"); nzw.inputs["Scale"].default_value = 1.0; nzw.inputs["Detail"].default_value = 8; nzw.inputs["Roughness"].default_value = 0.6
L.new(mpv.outputs["Vector"], nzw.inputs["Vector"])
nzc = N.new("ShaderNodeTexNoise"); nzc.inputs["Scale"].default_value = 6.0; nzc.inputs["Detail"].default_value = 6; nzc.inputs["Roughness"].default_value = 0.6; L.new(tcv.outputs["Object"], nzc.inputs["Vector"])
wbp = N.new("ShaderNodeBump"); wbp.inputs["Strength"].default_value = 0.1; wbp.inputs["Distance"].default_value = 0.12; L.new(nzw.outputs["Fac"], wbp.inputs["Height"])
wbc = N.new("ShaderNodeBump"); wbc.inputs["Strength"].default_value = 0.2; wbc.inputs["Distance"].default_value = 0.03; L.new(nzc.outputs["Fac"], wbc.inputs["Height"]); L.new(wbc.outputs["Normal"], wbp.inputs["Normal"])
L.new(wbp.outputs["Normal"], bwv.inputs["Normal"])
shadow_transparent(mwv)   # sunlight reaches through the water body (attenuated by its absorption volume): the thin lip and foam glow like real backlit water
if os.environ.get("DBG") == "wavegrey":
    mwv = node_mat("dbg")[0]
wave = mesh_obj("wave", wave_v, wave_f, mwv, smooth=True)
fat = wave.data.attributes.new("foam", "FLOAT", "POINT"); fat.data.foreach_set("value", foam)
sd = wave.modifiers.new("sub", "SUBSURF"); sd.levels = 1; sd.render_levels = 2

for (off, hh, ln, sh) in ():   # background swells removed (read as piers from the low vantage); sea chop does the job
    sv = []; sf = []; nr = 120; prof = [(-6, -.15), (-3, .3), (-1, .8), (0, 1.0), (1.2, .7), (2.5, .2), (3.5, -.15)]
    for k in range(nr + 1):
        w = -ln / 2 + ln * k / nr; hk = hh * (0.55 + 0.45 * math.cos(w / ln * math.pi) ** 2) * (1 + 0.15 * noise.noise(Vector((w * 0.03, off, 1))))
        for (u, v) in prof:
            P = C + TS * (w + sh) + NL * (off + u * hk * 2.2) + Vector((0, 0, v * hk if v > 0 else v))
            sv.append(P.to_tuple())
    for k in range(nr):
        for i in range(len(prof) - 1):
            a0 = k * len(prof) + i; sf.append((a0, a0 + 1, a0 + 1 + len(prof), a0 + len(prof)))
    sw = mesh_obj("swell", sv, sf, mwv, smooth=True)
    swa = sw.data.attributes.new("foam", "FLOAT", "POINT"); swa.data.foreach_set("value", [0.0] * len(sv))

# whitewater soup spreading over the water in front of the broken section (thin foam sheet, holes from noise)
mfo, N, L, bfo, mo = node_mat("soup")
bfo.inputs["Base Color"].default_value = (0.76, 0.76, 0.72, 1); bfo.inputs["Roughness"].default_value = 0.55
tcf = N.new("ShaderNodeTexCoord"); mpf = N.new("ShaderNodeMapping"); mpf.inputs["Scale"].default_value = (0.35, 1.2, 1.0); mpf.inputs["Rotation"].default_value[2] = math.atan2(TS.y, TS.x)
L.new(tcf.outputs["Object"], mpf.inputs["Vector"])
nf = N.new("ShaderNodeTexNoise"); nf.inputs["Scale"].default_value = 1.1; nf.inputs["Detail"].default_value = 10; nf.inputs["Roughness"].default_value = 0.7; nf.inputs["Distortion"].default_value = 0.6
L.new(mpf.outputs["Vector"], nf.inputs["Vector"])
fade = N.new("ShaderNodeAttribute"); fade.attribute_name = "fade"
mul_ = N.new("ShaderNodeMath"); mul_.operation = "MULTIPLY"; L.new(nf.outputs["Fac"], mul_.inputs[0]); L.new(fade.outputs["Fac"], mul_.inputs[1])
thr = N.new("ShaderNodeMapRange"); thr.inputs["From Min"].default_value = 0.36; thr.inputs["From Max"].default_value = 0.46; L.new(mul_.outputs[0], thr.inputs["Value"])
trn = N.new("ShaderNodeBsdfTransparent"); mxs = N.new("ShaderNodeMixShader"); L.new(thr.outputs["Result"], mxs.inputs[0]); L.new(trn.outputs[0], mxs.inputs[1]); L.new(bfo.outputs[0], mxs.inputs[2])
L.new(mxs.outputs[0], mo.inputs["Surface"])
sv_ = []; sf_ = []; fd = []; nw, nu = 90, 30
for k in range(nw + 1):
    w = -42 + 50 * k / nw
    for i in range(nu + 1):
        u = 0.2 * WH + 16.0 * i / nu
        P = C + TS * w + NL * u; sv_.append((P.x, P.y, 0.012))
        fd.append(smoothstep(-42, -30, w) * (1 - smoothstep(-2, 8, w)) * (1 - smoothstep(4, 16, u - 0.2 * WH)) * 1.25)
for k in range(nw):
    for i in range(nu):
        q = k * (nu + 1) + i; sf_.append((q, q + 1, q + nu + 2, q + nu + 1))
so_ = mesh_obj("soup", sv_, sf_, mfo, smooth=True)
fa_ = so_.data.attributes.new("fade", "FLOAT", "POINT"); fa_.data.foreach_set("value", fd)

# ------------------------------------------------------------------ spray: real water drops (points) + fine mist (bounded volume)
mdrop, N, L, bd, mo = node_mat("drop")
bd.inputs["Base Color"].default_value = (1, 1, 1, 1); bd.inputs["Transmission Weight"].default_value = 1.0; bd.inputs["IOR"].default_value = 1.333; bd.inputs["Roughness"].default_value = 0.0
shadow_transparent(mdrop)
if os.environ.get("DBG") == "dropred":
    em = mdrop.node_tree.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (1, 0, 0, 1); em.inputs["Strength"].default_value = 50
    mdrop.node_tree.links.new(em.outputs[0], mdrop.node_tree.nodes["Material Output"].inputs["Surface"])

def lognorm(mu, sig, lo, hi): return max(lo, min(hi, mu * math.exp(random.gauss(0, sig))))
import numpy as np
rng = np.random.default_rng(3)
def np_in_sil(P):
    d = P - np.array(CAMV); dep = d @ np.array(cf)
    x = (d @ np.array(cr)) * D0 / dep; y = (d @ np.array(cu)) * D0 / dep
    inside = np.zeros(len(P), bool)
    for poly in SILP:
        c = np.zeros(len(P), bool); n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
            cond = ((y1 > y) != (y2 > y)) & (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1)
            c ^= cond
        inside |= c
    return inside & (np.abs(dep - D0) < 14)
LIPA = np.array([l[0].to_tuple() for l in lipline]); CRA = np.array([c_[0].to_tuple() for c_ in crestline]); EA = np.array([l[1] for l in lipline]); WA = np.array([l[2] for l in lipline])
NLa, TSa = np.array(NL.to_tuple()), np.array(TS.to_tuple())
def spray_curtain(n):
    M = n * 4
    p = EA ** 2.4; p /= p.sum(); k = rng.choice(len(EA), M, p=p)
    e = EA[k]; w = WA[k]
    hgt = WH * e * np.minimum(1.6, rng.exponential(0.34, M))
    # feathered plumes: the offshore wind tears the crest into fingers
    ph1, ph2, ph3 = rng.uniform(0, 6.28, 3)
    plume = 0.5 + 0.25 * np.sin(w * 0.85 + ph1 + hgt * 0.3) + 0.25 * np.sin(w * 2.3 + ph2 - hgt * 0.8) * np.sin(w * 0.31 + ph3)
    keep = rng.random(M) < np.clip(plume, 0, 1) ** 1.6
    r = rng.random(M)[:, None] * 0.8
    base = CRA[k] + (LIPA[k] - CRA[k]) * r
    P = base + np.outer(hgt * 0.9, [0, 0, 1]) - np.outer(hgt * 0.6 + rng.normal(0, 0.3, M), NLa) + np.outer(rng.normal(0, 0.25, M), TSa)
    P += rng.normal(0, 0.1, (M, 3)) * (1 + hgt[:, None] * 0.15)
    keep &= ~np_in_sil(P)
    P = P[keep][:n]; hk = hgt[keep][:n]
    rad = np.clip(0.0055 * np.exp(rng.normal(0, 0.65, len(P))) * (1.25 - 0.1 * np.minimum(hk, 4)), 0.001, 0.03)
    return P, rad
def surfer_fan(n):
    cxp, cyp = ph2plane(0.58, 0.42)
    M = n * 3
    cxp, cyp = ph2plane(0.6, 0.37)          # silhouette centre
    tail = rng.random(M) < 0.4                # 40 %: the sheet thrown off the board toward lower right
    x = np.where(tail, cxp + 1.3 + rng.normal(0, 1.4, M), cxp + rng.normal(0, 0.95, M))
    y = np.where(tail, cyp - 0.9 + rng.normal(0, 0.8, M), cyp + rng.normal(-0.1, 0.95, M))
    dep_ = D0 + rng.normal(0, 1.2, M)
    P = np.array(CAMV) + np.outer(dep_, cf) + np.outer(x * dep_ / D0, cr) + np.outer(y * dep_ / D0, cu)
    keep = (y > CREST_U - 0.6) & ~np_in_sil(P)
    P = P[keep][:n]
    return P, np.clip(0.007 * np.exp(rng.normal(0, 0.6, len(P))), 0.0015, 0.035)
if os.environ.get("DBGFAN"):
    fpp, _ = surfer_fan(2000); d_ = fpp - np.array(CAMV); dep_ = d_ @ np.array(cf)
    xx = (d_ @ np.array(cr)) * D0 / dep_; yy = (d_ @ np.array(cu)) * D0 / dep_
    print("FAN n", len(fpp), "x", xx.min(), xx.max(), "y", yy.min(), yy.max(), "dep", dep_.min(), dep_.max())
    allp = [p_ for poly in SILP for p_ in poly]; print("SIL x", min(p_[0] for p_ in allp), max(p_[0] for p_ in allp), "y", min(p_[1] for p_ in allp), max(p_[1] for p_ in allp), "CREST_U", CREST_U, "RECT", RECT)
    import sys as _s; _s.exit(0)
sp, sr = spray_curtain(int(os.environ.get("NSPRAY", 60000 if OVER else 160000)))
fp, fr2 = surfer_fan(int(os.environ.get("NFAN", 15000 if OVER else 40000)))
points_obj("spray", np.vstack([sp, fp]).tolist(), np.concatenate([sr, fr2]).tolist(), mdrop)

def points_mist(name, P, radius, voxel, dens, aniso, color):
    me = bpy.data.meshes.new(name); me.vertices.add(len(P)); me.vertices.foreach_set("co", np.asarray(P, dtype=np.float32).ravel()); me.update()
    o = link(bpy.data.objects.new(name, me))
    m, N, L, b, mo = node_mat(name + "_mat"); N.remove(b)
    pv = N.new("ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = color + (1,); pv.inputs["Anisotropy"].default_value = aniso
    at_ = N.new("ShaderNodeAttribute"); at_.attribute_name = "density"
    mul = N.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = dens; L.new(at_.outputs["Fac"], mul.inputs[0]); L.new(mul.outputs[0], pv.inputs["Density"])
    L.new(pv.outputs[0], mo.inputs["Volume"])
    ng = bpy.data.node_groups.new(name + "_gn", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry"); ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    Ng = ng.nodes; Lg = ng.links; gi = Ng.new("NodeGroupInput"); go = Ng.new("NodeGroupOutput")
    mp = Ng.new("GeometryNodeMeshToPoints"); pv2 = Ng.new("GeometryNodePointsToVolume")
    try: pv2.resolution_mode = "VOXEL_SIZE"
    except Exception: pass
    for k_, v_ in (("Voxel Size", voxel), ("Radius", radius), ("Density", 1.0)):
        if k_ in pv2.inputs: pv2.inputs[k_].default_value = v_
    sm = Ng.new("GeometryNodeSetMaterial"); sm.inputs["Material"].default_value = m
    Lg.new(gi.outputs[0], mp.inputs["Mesh"]); Lg.new(mp.outputs["Points"], pv2.inputs["Points"]); Lg.new(pv2.outputs["Volume"], sm.inputs["Geometry"]); Lg.new(sm.outputs["Geometry"], go.inputs[0])
    md = o.modifiers.new("vol", "NODES"); md.node_group = ng; o.visible_shadow = False
    print("points_mist inputs", [i.name for i in pv2.inputs])
    return o

def mist_volume(name, centre, size, rot_z, dens, aniso, color, gen_falloff=True, noise_scale=3.0):
    m, N, L, b, mo = node_mat(name); N.remove(b)
    pv = N.new("ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = color + (1,); pv.inputs["Anisotropy"].default_value = aniso
    tc_ = N.new("ShaderNodeTexCoord"); sx = N.new("ShaderNodeSeparateXYZ"); L.new(tc_.outputs["Generated"], sx.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = noise_scale; nz.inputs["Detail"].default_value = 5; L.new(tc_.outputs["Generated"], nz.inputs["Vector"])
    nzr = N.new("ShaderNodeMapRange"); nzr.inputs["From Min"].default_value = 0.4; nzr.inputs["From Max"].default_value = 0.75; L.new(nz.outputs["Fac"], nzr.inputs["Value"])
    # falloff: strongest at the bottom (z=0 of box), fades up; fades at the long ends (x)
    fz = N.new("ShaderNodeMath"); fz.operation = "SUBTRACT"; fz.inputs[0].default_value = 1.0; L.new(sx.outputs["Z"], fz.inputs[1])
    fz2 = N.new("ShaderNodeMath"); fz2.operation = "POWER"; fz2.inputs[1].default_value = 1.8; L.new(fz.outputs[0], fz2.inputs[0])
    ex = N.new("ShaderNodeMath"); ex.operation = "PINGPONG"; ex.inputs[1].default_value = 0.5; L.new(sx.outputs["X"], ex.inputs[0])
    ex2 = N.new("ShaderNodeMath"); ex2.operation = "MULTIPLY"; ex2.inputs[1].default_value = 2.0; L.new(ex.outputs[0], ex2.inputs[0])
    m1 = N.new("ShaderNodeMath"); m1.operation = "MULTIPLY"; L.new(fz2.outputs[0], m1.inputs[0]); L.new(ex2.outputs[0], m1.inputs[1])
    m2 = N.new("ShaderNodeMath"); m2.operation = "MULTIPLY"; L.new(m1.outputs[0], m2.inputs[0]); L.new(nzr.outputs["Result"], m2.inputs[1])
    m3 = N.new("ShaderNodeMath"); m3.operation = "MULTIPLY"; m3.inputs[1].default_value = dens; L.new(m2.outputs[0], m3.inputs[0])
    L.new(m3.outputs[0], pv.inputs["Density"]); L.new(pv.outputs[0], mo.inputs["Volume"])
    bpy.ops.mesh.primitive_cube_add(size=1, location=centre); o = bpy.context.object; o.name = name
    o.scale = size; o.rotation_euler = (0, 0, rot_z); o.data.materials.append(m); o.visible_shadow = False
    return o

# mist over the crest (fine spray too small to model as spheres): box along the wave, base at the crest
mz = math.atan2(TS.y, TS.x)
if os.environ.get("NOMIST") != "1":
    mp_, _ = spray_curtain(int(os.environ.get("NMIST", 120000)))
    mf_, _ = surfer_fan(int(os.environ.get("NMISTF", 60000)))
    points_mist("spray_mist", mp_, 0.22, 0.07, float(os.environ.get("MISTD", "0.35")), 0.85, (0.97, 0.98, 1.0))
    points_mist("fan_mist", mf_, 0.07, 0.03, float(os.environ.get("MISTF", "1.2")), 0.8, (0.97, 0.98, 1.0))   # the board's spray, dense around the absence
if False: mist_volume("crest_mist", C - NL * 1.5 + Vector((0, 0, WH * 0.75 + WH * 0.8)), (WL * 0.75, WH * 1.3, WH * 1.6), mz, 0.15, 0.82, (0.95, 0.97, 1.0), noise_scale=4.0)

# ------------------------------------------------------------------ festival: stretched tapestry + confetti + water spray beneath
def tapestry_mat():
    m, N, L, b, mo = node_mat("tapestry")
    tc_ = N.new("ShaderNodeTexCoord")
    mp_ = N.new("ShaderNodeMapping"); mp_.inputs["Scale"].default_value = (3.0, 3.0, 3.0); L.new(tc_.outputs["UV"], mp_.inputs["Vector"])
    # procedural block-print pattern: bands + diamonds in saffron / magenta / teal on ivory (colours from his festival photos)
    # mandala print: rings modulated by petals (polar coords from the sail centre)
    sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc_.outputs["UV"], sep.inputs["Vector"])
    dx = N.new("ShaderNodeMath"); dx.operation = "SUBTRACT"; dx.inputs[1].default_value = 0.5; L.new(sep.outputs["X"], dx.inputs[0])
    dy = N.new("ShaderNodeMath"); dy.operation = "SUBTRACT"; dy.inputs[1].default_value = 0.5; L.new(sep.outputs["Y"], dy.inputs[0])
    ang = N.new("ShaderNodeMath"); ang.operation = "ARCTAN2"; L.new(dy.outputs[0], ang.inputs[0]); L.new(dx.outputs[0], ang.inputs[1])
    cmb_ = N.new("ShaderNodeCombineXYZ"); L.new(dx.outputs[0], cmb_.inputs[0]); L.new(dy.outputs[0], cmb_.inputs[1])
    ln_ = N.new("ShaderNodeVectorMath"); ln_.operation = "LENGTH"; L.new(cmb_.outputs[0], ln_.inputs[0])
    pet = N.new("ShaderNodeMath"); pet.operation = "MULTIPLY"; pet.inputs[1].default_value = 12.0; L.new(ang.outputs[0], pet.inputs[0])
    pts_ = N.new("ShaderNodeMath"); pts_.operation = "SINE"; L.new(pet.outputs[0], pts_.inputs[0])
    pa = N.new("ShaderNodeMath"); pa.operation = "MULTIPLY_ADD"; pa.inputs[1].default_value = 0.035; L.new(pts_.outputs[0], pa.inputs[0]); L.new(ln_.outputs["Value"], pa.inputs[2])
    rs = N.new("ShaderNodeMath"); rs.operation = "MULTIPLY"; rs.inputs[1].default_value = 5.0; L.new(pa.outputs[0], rs.inputs[0])
    fr_ = N.new("ShaderNodeMath"); fr_.operation = "FRACT"; L.new(rs.outputs[0], fr_.inputs[0])
    ramp = N.new("ShaderNodeValToRGB"); cr_ = ramp.color_ramp; cr_.interpolation = "CONSTANT"
    cr_.elements[0].position = 0.0; cr_.elements[0].color = (0.7, 0.36, 0.03, 1)
    cr_.elements[1].position = 0.78; cr_.elements[1].color = (0.06, 0.34, 0.34, 1)
    e2 = cr_.elements.new(0.3); e2.color = (0.58, 0.05, 0.24, 1)
    e3 = cr_.elements.new(0.52); e3.color = (0.74, 0.62, 0.42, 1)
    L.new(fr_.outputs[0], ramp.inputs["Fac"])
    mix = ramp
    lt = N.new("ShaderNodeTexImage"); lt.image = img("rough_linen_diff_2k.jpg"); mpl = N.new("ShaderNodeMapping"); mpl.inputs["Scale"].default_value = (14, 14, 14)
    L.new(tc_.outputs["UV"], mpl.inputs["Vector"]); L.new(mpl.outputs["Vector"], lt.inputs["Vector"])
    ov = N.new("ShaderNodeMixRGB"); ov.blend_type = "MULTIPLY"; ov.inputs[0].default_value = 0.5; L.new(mix.outputs["Color"], ov.inputs[1]); L.new(lt.outputs["Color"], ov.inputs[2])
    L.new(ov.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.85; b.inputs["Sheen Weight"].default_value = 0.4
    ln = N.new("ShaderNodeTexImage"); ln.image = img("rough_linen_nor_gl_2k.jpg", True); L.new(mpl.outputs["Vector"], ln.inputs["Vector"])
    nmp = N.new("ShaderNodeNormalMap"); L.new(ln.outputs["Color"], nmp.inputs["Color"]); L.new(nmp.outputs["Normal"], b.inputs["Normal"])
    tr = N.new("ShaderNodeBsdfTranslucent"); L.new(ov.outputs[0], tr.inputs["Color"])
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.6; L.new(b.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], mo.inputs["Surface"])
    return m

def paper_mat(name, attr=True, col=(0.7, 0.6, 0.5)):
    m, N, L, b, mo = node_mat(name)
    if attr:
        ca = N.new("ShaderNodeAttribute"); ca.attribute_name = "col"; src = ca.outputs["Color"]
    else:
        rgb = N.new("ShaderNodeRGB"); rgb.outputs[0].default_value = col + (1,); src = rgb.outputs[0]
    L.new(src, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.55
    tr = N.new("ShaderNodeBsdfTranslucent"); L.new(src, tr.inputs["Color"])
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.4; L.new(b.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], mo.inputs["Surface"])
    return m

def metal_mat(name, col, rough):
    m, N, L, b, mo = node_mat(name); b.inputs["Base Color"].default_value = col + (1,); b.inputs["Metallic"].default_value = 1.0; b.inputs["Roughness"].default_value = rough
    return m

ALU = metal_mat("alu", (0.62, 0.6, 0.57), 0.35)
ROPE = node_mat("rope")[0]; ROPE.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.45, 0.38, 0.28, 1); ROPE.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9

def cyl(p0, p1, r, mat, verts=12):
    p0 = Vector(p0); p1 = Vector(p1); d = p1 - p0
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, vertices=verts, location=(p0 + p1) / 2)
    o = bpy.context.object; o.rotation_euler = d.to_track_quat("Z", "Y").to_euler(); o.data.materials.append(mat)
    bv = o.modifiers.new("bv", "BEVEL"); bv.width = min(0.01, r * 0.3); bv.segments = 2
    return o

def build_canopy():
    cx_ = CANOPY
    # a 9 x 6 m tapestry stretched between 4 poles, tilted ~50 deg so its top faces the sun: the camera sees it backlit
    nU, nV = 36, 24; Wt, Ht = 9.0, 6.0
    cam_az = math.degrees(math.atan2(O.y - cx_.y, O.x - cx_.x))
    rz = math.radians(cam_az - 270 + 35)
    Wt, Ht = 11.0, 9.0; nU, nV = 44, 36
    hc = (2.3, 7.2, 2.8, 6.6)      # twisted shade sail (hypar): two high corners, two low
    Mx = Matrix.Translation(cx_) @ Matrix.Rotation(rz, 4, "Z")
    verts = []; uvs = []; faces = []
    for j in range(nV + 1):
        for i in range(nU + 1):
            u = i / nU; v = j / nV
            x = (u - 0.5) * Wt * (1 - 0.15 * math.sin(math.pi * v)); y = (v - 0.5) * Ht * (1 - 0.15 * math.sin(math.pi * u))
            z = hc[0] * (1 - u) * (1 - v) + hc[1] * u * (1 - v) + hc[2] * u * v + hc[3] * (1 - u) * v
            z += -0.35 * math.sin(math.pi * u) * math.sin(math.pi * v) + 0.05 * noise.noise(Vector((x * 0.7, y * 0.7, 3.3)))
            verts.append((Mx @ Vector((x, y, z))).to_tuple()); uvs.append((u, v))
    for j in range(nV):
        for i in range(nU):
            q = j * (nU + 1) + i; faces.append((q, q + 1, q + nU + 2, q + nU + 1))
    o = mesh_obj("tapestry", verts, faces, tapestry_mat(), smooth=True)
    uvl = o.data.uv_layers.new(name="UV")
    for poly in o.data.polygons:
        for li in poly.loop_indices: uvl.data[li].uv = uvs[o.data.loops[li].vertex_index]
    sol = o.modifiers.new("sol", "SOLIDIFY"); sol.thickness = 0.004
    corners = [Mx @ Vector(((u - 0.5) * Wt, (v - 0.5) * Ht, hh)) for (u, v), hh in zip(((0, 0), (1, 0), (1, 1), (0, 1)), hc)]
    for c_ in corners:
        foot = Vector((c_.x, c_.y, height(c_.x, c_.y) - 0.3))
        cyl(foot, c_ + Vector((0, 0, 0.15)), 0.04, ALU)
        # guy rope from pole top outward to a stake
        out = (Vector((c_.x, c_.y, 0)) - Vector((cx_.x, cx_.y, 0))).normalized() * 3.0
        cyl(c_ + Vector((0, 0, 0.1)), Vector((c_.x + out.x, c_.y + out.y, height(c_.x + out.x, c_.y + out.y))), 0.007, ROPE, 6)
    # confetti (paper 3.5 x 2.5 cm) + festival water spray hanging under and in front of the tapestry
    cols = [(0.78, 0.46, 0.04), (0.62, 0.05, 0.3), (0.05, 0.42, 0.42), (0.78, 0.74, 0.62), (0.75, 0.6, 0.05)]
    cv = []; cfc = []; ccol = []
    nconf = 22000
    for k in range(nconf):
        P = cx_ + Vector((random.gauss(0, 2.8), random.gauss(0, 2.2), 0.3 + abs(random.gauss(0, 1.2)) + random.random() * 3.0))
        q = Vector((random.random() - .5, random.random() - .5, random.random() - .5)).normalized()
        rot = Matrix.Rotation(random.uniform(0, 6.28), 3, q)
        sx_, sy_ = 0.0175, 0.0125
        b0 = len(cv); curl = random.uniform(-0.004, 0.004)
        for (x, y) in ((-sx_, -sy_), (sx_, -sy_), (sx_, sy_), (-sx_, sy_)):
            cv.append((P + rot @ Vector((x, y, curl * (x / sx_) ** 2))).to_tuple())
        cfc.append((b0, b0 + 1, b0 + 2, b0 + 3)); ccol.append(random.choice(cols))
    o = mesh_obj("confetti", cv, cfc, paper_mat("confetti_paper"))
    ca = o.data.color_attributes.new("col", "FLOAT_COLOR", "CORNER")
    for poly in o.data.polygons:
        c3 = ccol[poly.index]
        for li in poly.loop_indices: ca.data[li].color = c3 + (1,)
    # water spray (festival hose / water cannon), a falling arc held still
    pts = []; rad = []
    a0 = cx_ + Vector((-3.5, -2.0, 0.0))
    for k in range(30000 if OVER else 8000):
        t = random.random(); arc = a0 + Vector((7.0 * t, 4.0 * t, 0)) + Vector((0, 0, 0.6 + 5.4 * 4 * t * (1 - t)))
        arc += Vector((random.gauss(0, 0.25 + 0.6 * t), random.gauss(0, 0.25 + 0.6 * t), random.gauss(0, 0.2 + 0.4 * t)))
        pts.append(arc.to_tuple()); rad.append(lognorm(0.003, 0.5, 0.0008, 0.012))
    points_obj("festival_spray", pts, rad, mdrop)
    mist_volume("festival_mist", cx_ + Vector((0, 0, 1.6)), (8, 7, 3.5), 0.0, 0.08, 0.75, (0.95, 0.9, 0.85), noise_scale=2.0)

# ------------------------------------------------------------------ sport: ticker tape in floodlight beams over turf, ball held mid-air
def build_ticker():
    c_ = TICK
    rz = math.atan2(TS.y, TS.x)
    # turf patch on a thin base, white touchline
    m, N, L, b, mo = node_mat("turf")
    tc_ = N.new("ShaderNodeTexCoord"); wv_ = N.new("ShaderNodeTexWave"); wv_.wave_type = "BANDS"; wv_.inputs["Scale"].default_value = 3.0; wv_.inputs["Distortion"].default_value = 0.4
    L.new(tc_.outputs["Generated"], wv_.inputs["Vector"])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 60; L.new(tc_.outputs["Object"], nz.inputs["Vector"])
    r_ = N.new("ShaderNodeMapRange"); r_.inputs["To Min"].default_value = 0.75; r_.inputs["To Max"].default_value = 1.0; L.new(wv_.outputs["Fac"], r_.inputs["Value"])
    mul = N.new("ShaderNodeMixRGB"); mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1.0; mul.inputs[1].default_value = (0.06, 0.16, 0.03, 1)
    cmb = N.new("ShaderNodeCombineXYZ"); L.new(r_.outputs["Result"], cmb.inputs[0]); L.new(r_.outputs["Result"], cmb.inputs[1]); L.new(r_.outputs["Result"], cmb.inputs[2]); L.new(cmb.outputs[0], mul.inputs[2])
    L.new(mul.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.8; b.inputs["Sheen Weight"].default_value = 0.6
    bpn = N.new("ShaderNodeBump"); bpn.inputs["Strength"].default_value = 0.6; L.new(nz.outputs["Fac"], bpn.inputs["Height"]); L.new(bpn.outputs["Normal"], b.inputs["Normal"])
    bpy.ops.mesh.primitive_cube_add(size=1, location=(c_.x, c_.y, 0.03)); o = bpy.context.object; o.scale = (20, 13, 0.06); o.rotation_euler = (0, 0, rz)
    o.data.materials.append(m); bv = o.modifiers.new("bv", "BEVEL"); bv.width = 0.02
    lineM = node_mat("chalk")[0]; lineM.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.75, 0.75, 0.72, 1)
    for off in (-6.2, 6.2):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(c_ + Vector((math.cos(rz + math.pi / 2), math.sin(rz + math.pi / 2), 0)) * off + Vector((0, 0, 0.062))))
        l_ = bpy.context.object; l_.scale = (19.6, 0.12, 0.002); l_.rotation_euler = (0, 0, rz); l_.data.materials.append(lineM)
    # two floodlight masts (galvanised steel) with Poly Haven flood_lights heads; real spot lights 5600 K-ish
    steel = metal_mat("galv", (0.55, 0.56, 0.57), 0.45)
    head = None
    try:
        bpy.ops.import_scene.gltf(filepath=PH + "flood_lights/flood_lights_1k.gltf")
        imp = list(bpy.context.selected_objects)
        meshes = [o_ for o_ in imp if o_.type == "MESH"]
        for o_ in meshes:
            mw_ = o_.matrix_world.copy(); o_.parent = None; o_.matrix_world = mw_
        for o_ in imp:
            if o_.type != "MESH": bpy.data.objects.remove(o_, do_unlink=True)
        bpy.ops.object.select_all(action="DESELECT")
        for o_ in meshes: o_.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]; bpy.ops.object.join(); head = bpy.context.view_layer.objects.active
    except Exception as ex:
        print("flood_lights import failed", ex)
    masts = []
    for side in (-1, 1):
        pv_ = Vector((math.cos(math.radians(YAW_O - 90)), math.sin(math.radians(YAW_O - 90)), 0)); fv_ = Vector((math.cos(math.radians(YAW_O)), math.sin(math.radians(YAW_O)), 0))
        base = c_ + pv_ * (side * 13.0) + fv_ * 7.0
        top = base + Vector((0, 0, 19.0))
        cyl(Vector((base.x, base.y, -0.5)), top, 0.22, steel, 16)
        cyl(top + Vector((-1.4, 0, 0)), top + Vector((1.4, 0, 0)), 0.06, steel)
        masts.append(top)
    if head:
        for i, top in enumerate(masts):
            inst = head if i == 0 else head.copy()
            if i: link(inst)
            d = (c_ + Vector((0, 0, 5)) - top)
            inst.location = top + Vector((0, 0, 0.05)); inst.scale = (1.4, 1.4, 1.4); inst.rotation_euler = (0, 0, math.atan2(d.y, d.x) - math.pi / 2)
    for top in masts:
        sl = bpy.data.lights.new("flood", "SPOT"); sl.energy = 50000; sl.spot_size = math.radians(34); sl.spot_blend = 0.35
        sl.color = (0.86, 0.92, 1.0); sl.shadow_soft_size = 0.4
        so = link(bpy.data.objects.new("flood", sl)); so.location = top + Vector((0, 0, 0.8)); look_at(so, c_ + Vector((0, 0, 4.5)))
    # beam haze (stadium-like air around the lights), bounded box
    m, N, L, b, mo = node_mat("beam_haze"); N.remove(b)
    sv = N.new("ShaderNodeVolumeScatter"); sv.inputs["Anisotropy"].default_value = 0.55
    tcb = N.new("ShaderNodeTexCoord"); vs_ = N.new("ShaderNodeVectorMath"); vs_.operation = "SUBTRACT"; vs_.inputs[1].default_value = (0.5, 0.5, 0.5)
    L.new(tcb.outputs["Generated"], vs_.inputs[0]); vl = N.new("ShaderNodeVectorMath"); vl.operation = "LENGTH"; L.new(vs_.outputs[0], vl.inputs[0])
    fo = N.new("ShaderNodeMapRange"); fo.inputs["From Min"].default_value = 0.5; fo.inputs["From Max"].default_value = 0.15; fo.inputs["To Max"].default_value = 0.012
    L.new(vl.outputs["Value"], fo.inputs["Value"]); L.new(fo.outputs["Result"], sv.inputs["Density"])
    L.new(sv.outputs[0], mo.inputs["Volume"])
    bpy.ops.mesh.primitive_cube_add(size=1, location=(c_.x, c_.y, 11)); o = bpy.context.object; o.scale = (44, 44, 24); o.rotation_euler = (0, 0, rz)
    o.data.materials.append(m); o.visible_shadow = False
    # ticker tape: 1.8 cm paper strips, 40-110 cm, curled and twisted; Maccabi yellow (albedo capped at 0.8)
    yel = paper_mat("ticker_paper", attr=False, col=(0.78, 0.52, 0.0))
    tv = []; tf = []
    for k in range(14000 if OVER else 600):
        Pc = c_ + Vector((random.gauss(0, 4.2), random.gauss(0, 3.4), 1.0 + abs(random.gauss(4.0, 2.3))))
        Lg = random.uniform(0.4, 1.1); nseg = 12
        ax = Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1))).normalized()
        bx = ax.cross(Vector((0.3, 0.2, 1))).normalized(); cx2 = ax.cross(bx)
        kk = random.uniform(2, 9); tw = random.uniform(-3, 3); amp = random.uniform(0.03, 0.15)
        b0 = len(tv)
        for s in range(nseg + 1):
            t = s / nseg; arc = (t - 0.5) * Lg
            p = Pc + ax * arc + bx * (amp * math.sin(kk * arc)) + cx2 * (amp * (1 - math.cos(kk * arc)))
            wdir = (bx * math.cos(tw * t) + cx2 * math.sin(tw * t)) * 0.02
            tv.append((p - wdir).to_tuple()); tv.append((p + wdir).to_tuple())
        for s in range(nseg):
            q = b0 + 2 * s; tf.append((q, q + 1, q + 3, q + 2))
    mesh_obj("ticker_tape", tv, tf, yel, smooth=True)
    try:
        bpy.ops.import_scene.gltf(filepath=PH + "football/football_1k.gltf")
        for o_ in bpy.context.selected_objects:
            if "deflated" in o_.name: bpy.data.objects.remove(o_, do_unlink=True)
            else: o_.location = c_ + Vector((1.2, -0.5, 4.2)); o_.rotation_euler = (0.4, 0.2, 1.1)
    except Exception as ex:
        print("football import failed", ex)

# ------------------------------------------------------------------ portraits: pine grove edge, backlit dust, a lifted linen sheet
def build_pines():
    if NOTREES: return
    try:
        bpy.ops.import_scene.gltf(filepath=PH + "pine_tree_01/pine_tree_01_1k.gltf")
    except Exception as ex:
        print("pine import failed", ex); return
    objs = list(bpy.context.selected_objects)
    keep = sorted([o_ for o_ in objs if o_.type == "MESH"], key=lambda o_: len(o_.data.polygons))
    gone = set(o_.name for o_ in keep[1:])
    objs = [o_ for o_ in objs if o_.name not in gone]
    for o_ in keep[1:]: bpy.data.objects.remove(o_, do_unlink=True)
    keep = keep[:1]; print("pine faces", len(keep[0].data.polygons))
    random.seed(5)
    spots = []
    for i in range(13):
        spots.append(PINES + Vector((random.uniform(-32, 22), random.uniform(-10, 34), 0)))
    for i, p in enumerate(spots):
        src = keep[i % len(keep)]
        o_ = src if i < len(keep) else src.copy()
        if i >= len(keep): link(o_)
        if o_.parent: mw_ = o_.matrix_world.copy(); o_.parent = None; o_.matrix_world = mw_
        o_.location = (p.x, p.y, height(p.x, p.y) - 0.1); o_.rotation_euler = (0, 0, random.uniform(0, 6.28))
        s = random.uniform(0.85, 1.15); o_.scale = (s, s, s)
    for o_ in objs:
        if o_.type != "MESH": bpy.data.objects.remove(o_, do_unlink=True)
    # dust in the low sun at the grove edge
    mist_volume("grove_dust", PINES + Vector((-4, -2, 3.5)), (40, 22, 7), math.radians(20), 0.035, 0.7, (0.95, 0.82, 0.62), noise_scale=2.5)
    # linen sheet lifted by the wind, held in the air
    nU, nV = 30, 20; verts = []; faces = []; uvs = []
    base = PINES + Vector((6, -16, 0)); base.z = height(base.x, base.y) + 1.6
    Mx = Matrix.Translation(base) @ Matrix.Rotation(math.radians(SUN_AZ + 200), 4, "Z") @ Matrix.Rotation(math.radians(70), 4, "X")
    for j in range(nV + 1):
        for i in range(nU + 1):
            u = i / nU; v = j / nV; x = (u - .5) * 3.0; y = (v - .5) * 2.0
            z = 0.45 * math.sin(math.pi * u * 1.3 + v) * v + 0.25 * math.sin(3 * v + 2 * u) * v
            verts.append((Mx @ Vector((x, y, z))).to_tuple()); uvs.append((u, v))
    for j in range(nV):
        for i in range(nU):
            q = j * (nU + 1) + i; faces.append((q, q + 1, q + nU + 2, q + nU + 1))
    m, N, L, b, mo = node_mat("linen")
    t_ = N.new("ShaderNodeTexImage"); t_.image = img("rough_linen_diff_2k.jpg"); tc_ = N.new("ShaderNodeTexCoord"); mpp = N.new("ShaderNodeMapping"); mpp.inputs["Scale"].default_value = (6, 6, 6)
    L.new(tc_.outputs["UV"], mpp.inputs["Vector"]); L.new(mpp.outputs["Vector"], t_.inputs["Vector"])
    br = N.new("ShaderNodeBrightContrast"); br.inputs["Bright"].default_value = 0.15; L.new(t_.outputs["Color"], br.inputs["Color"])
    L.new(br.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = 0.9
    tr = N.new("ShaderNodeBsdfTranslucent"); L.new(br.outputs[0], tr.inputs["Color"])
    mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.45; L.new(b.outputs[0], mx.inputs[1]); L.new(tr.outputs[0], mx.inputs[2]); L.new(mx.outputs[0], mo.inputs["Surface"])
    o = mesh_obj("linen_sheet", verts, faces, m, smooth=True)
    uvl = o.data.uv_layers.new(name="UV")
    for poly in o.data.polygons:
        for li in poly.loop_indices: uvl.data[li].uv = uvs[o.data.loops[li].vertex_index]

# ------------------------------------------------------------------ footprints (where he stood): real dents in the wet sand that hold water
def footprint(c, hd, side, depth):
    nx, ny = 30, 16; Lx, Ly = 0.44, 0.24
    rot = Matrix.Rotation(math.radians(hd), 3, "Z")
    verts = []; faces = []
    ells = [(-0.085, 0.0, 0.048, 0.037), (0.045, 0.006 * side, 0.072, 0.047), (0.118, 0.012 * side, 0.03, 0.045)]
    base = height(c.x, c.y) + 0.002
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = -Lx / 2 + Lx * i / nx; y = -Ly / 2 + Ly * j / ny
            mval = max(1 - ((x - ex_) / rx) ** 2 - ((y - ey) / ry) ** 2 for ex_, ey, rx, ry in ells)
            d = -depth * smoothstep(-0.05, 0.45, mval)
            if mval < 0: d += 0.005 * math.exp(-((mval + 0.25) / 0.18) ** 2)
            edge = min(i, nx - i, j, ny - j)
            if edge == 0: d = -0.002
            P = c + rot @ Vector((x, y, 0)); verts.append((P.x, P.y, base + d))
    for j in range(ny):
        for i in range(nx):
            q = j * (nx + 1) + i; faces.append((q, q + 1, q + nx + 2, q + nx + 1))
    return verts, faces
fv = []; ff = []
for (c, hd, side, depth) in TRAIL:
    v_, f_ = footprint(c, hd, side, depth); b0 = len(fv); fv += v_; ff += [tuple(b0 + i for i in f) for f in f_]
mesh_obj("footprints", fv, ff, SAND, smooth=True)

# ------------------------------------------------------------------ aerial haze (bounded box; a world volume would black out the sky)
hz, N, L, b, mo = node_mat("haze"); N.remove(b)
vol = N.new("ShaderNodeVolumePrincipled"); vol.inputs["Density"].default_value = float(os.environ.get("HAZE", "0.0004"))
vol.inputs["Color"].default_value = (0.98, 0.86, 0.74, 1); vol.inputs["Anisotropy"].default_value = 0.7
L.new(vol.outputs["Volume"], mo.inputs["Volume"])
bpy.ops.mesh.primitive_cube_add(size=1, location=(O.x, O.y + 300, 30)); hb = bpy.context.object; hb.name = "haze"; hb.scale = (1000, 1000, 62)
hb.data.materials.append(hz); hb.visible_shadow = False

if OVER:
    build_canopy(); build_ticker(); build_pines()

# ------------------------------------------------------------------ cameras
cam_d = bpy.data.cameras.new("cam"); cam = link(bpy.data.objects.new("cam", cam_d)); sc.camera = cam
cam_d.sensor_width = 36.0; cam_d.sensor_fit = "HORIZONTAL"; cam_d.clip_start = 0.05; cam_d.clip_end = 60000
if OVER:
    cam.location = O; cam_d.lens = 35
    pitch = math.radians(float(os.environ.get("PITCH", "-8")))
    tgt = O + Vector((math.cos(math.radians(YAW_O)) * math.cos(pitch), math.sin(math.radians(YAW_O)) * math.cos(pitch), math.sin(pitch)))
    look_at(cam, tgt)
    cam_d.dof.use_dof = True; cam_d.dof.focus_distance = 120; cam_d.dof.aperture_fstop = 11
else:
    cam.location = CAMV; cam_d.lens = 200; look_at(cam, T)
    cam_d.dof.use_dof = True; cam_d.dof.focus_distance = D0; cam_d.dof.aperture_fstop = 4.0
if os.environ.get("CAMDBG"):
    tg = {"tick": TICK + Vector((0, 0, 5)), "canopy": CANOPY + Vector((0, 0, 3)), "pines": PINES + Vector((0, 0, 8))}[os.environ["CAMDBG"]]
    cam.location = tg + (O - tg).normalized() * 30 + Vector((0, 0, 2)); cam_d.lens = 35; look_at(cam, tg); cam_d.dof.use_dof = False
print("cam", cam.location, "V", V, "T", T)
dg = bpy.context.evaluated_depsgraph_get()
for nm_ in ("spray", "festival_spray"):
    if nm_ in bpy.data.objects:
        ev = bpy.data.objects[nm_].evaluated_get(dg); print("EVAL", nm_, ev.type, [(k.name, len(k.points) if hasattr(k, "points") else None) for k in [ev.data]] if ev.data else None)
bpy.ops.render.render(write_still=True)
print("DONE", OUT)
