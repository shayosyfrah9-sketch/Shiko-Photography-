# Lessons (append, dated)
- 2026-11-24 Measure downloads with gzip like GitHub Pages; without it the phone looked like 31 MB, really 21 MB.
- 2026-11-24 Swallowed try/catch errors hid two bugs for weeks (trees not loading; service worker never registering). Log errors in dev builds.
- 2026-11-24 gltfpack needs -vtf or UVs get quantized (stretched textures).
- 2026-11-24 The artifact host refuses binary files named .json/.glb: embed glTF buffers as base64.
- 2026-11-24 Experiment (Aperture Pavilion): critic averages 3.0 → 4.6 → 5.4 → 5.3. Biggest gains came from the camera (3/4 low view, ring facing camera) and physical sky + low sun. Round 4 lost atmosphere when haze density was cut 40%: keep haze ≥ 0.0018 and add rim light. A world-volume in Cycles blacks out the sky; use a bounded volume box.
- 2026-11-24 Rendering one frame per process is ~10× slower for animation (scene rebuild each time); build once and loop frames inside Blender.
- 2026-11-24 Glass box on a cliff is a cliché (critic). Originality has to come from the concept itself, not from detailing.
