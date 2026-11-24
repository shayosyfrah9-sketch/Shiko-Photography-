---
name: shiko-blender-worldbuilding
description: Headless Blender (bpy 5.x, Cycles CPU) for architecture, landscapes, materials, water, atmosphere and procedural worlds for SHIKO WORLD 2.0. Use for any render, bake, model or environment work.
---
# Blender Worldbuilding (covers: Blender workflow, architectural visualization, cinematic environments, procedural world building, photoreal materials, 3D modeling, natural landscapes, water & atmosphere)

## Environment facts (verified)
- Python module Blender 5.3: `scratchpad/bpyenv/bin/python script.py -- args`. No GUI, no GPU: **Cycles CPU only** (4 cores, 15 GB). EEVEE needs a GPU context: do not rely on it.
- Never run two heavy renders/bakes at once (OOM at ~15 GB killed a 6144² bake before).
- Assets: Poly Haven API (api.polyhaven.com, dl.polyhaven.org) is allowed: CC0 HDRIs, textures, models. Cache downloads in `scratchpad/ph/`. Local HDRIs in `scratchpad/hdri/`.

## Render budgets (CPU)
| Use | Res | Samples | Time |
| look-dev | 960×540 | 24 + OIDN denoise | 1–3 min |
| review still | 1600×900 | 64 + denoise | 4–10 min |
| hero still | 1920×1080 | 128 + denoise | 10–25 min |
| animatic frame | 960×540 | 16 + denoise | 20–60 s/frame |
Use adaptive sampling, light paths 4/4/8, clamp indirect 10, filter glossy 1.0 to kill fireflies. Persistent data on for animation.

## Architecture
- Start from massing and silhouette (blockout, judge as black shape), then proportion (golden/1:1.6, human scale figure 1.8 m in every scene), then detail.
- Real thickness: slabs 0.3–0.5 m, mullions 5–8 cm, bevel every hard edge (0.5–2 cm) so light catches it. No zero-thickness planes.
- Material honesty: concrete/stone mass, glass with real IOR 1.45 + thin dark frame, metal anisotropic. Avoid pure white (max albedo 0.8) and pure black (min 0.03).

## Landscape & nature
- Terrain: displace a subdivided grid with layered noise (fBm + ridged for cliffs), erosion feel via slope-based material mixing (rock on steep, grass on flat, scree at foot).
- Scale cues: trees 15–30 m, layered atmospheric perspective (volume scatter or mist pass), three depth planes (foreground frame, mid subject, far silhouettes).
- Water: Principled glass/transmission with low roughness + normal noise, or dark reflective plane with Fresnel; waterfalls = emissive-free white scatter sheets + mist volume at base.
- Atmosphere: world volume scatter density 0.002–0.02 (slow!) or fake with mist pass/compositing fog; god rays need a volume + a strong sun with small angle.

## Lighting
Golden hour: sun elevation 4–12°, warm 3200–4000 K key vs cool sky fill; Nishita sky or HDRI; one practical/accent light max per building. Exposure via Filmic/AgX, look "Medium High Contrast".

## Bridging to real time
Bake lighting (diffuse direct+indirect) to lightmaps, export glTF (`export_format='GLB'`), then gltfpack `-cc -vtf -kn -km` (see `shiko-asset-performance`). Pre-rendered panoramas/backplates for far scenery; real geometry only near camera.

## Gotchas learned on this project
- gltfpack without `-vtf` quantizes UVs → stretched textures.
- Quads in bakes must face the right way (CCW) or bake black.
- The artifact host refuses binary .glb: embed buffers as base64 glTF .json.

## Process
Blockout → silhouette check → lighting pass (clay) → materials → atmosphere → review still → critique (`shiko-visual-critique`) → 3 rounds → hero still.
