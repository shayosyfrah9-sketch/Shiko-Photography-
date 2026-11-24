---
name: shiko-asset-performance
description: 3D asset optimization and mobile performance budgets (glTF/meshopt, textures, lazy loading, LOD, measured load times) for SHIKO WORLD 2.0. Use before shipping any model, texture, audio or page change.
---
# Asset & Performance (covers: 3D asset optimization, mobile performance optimization)

## Budgets (first visit, regular 4G 9 Mbps / 85 ms)
| Metric | Desktop | Phone |
| Logo/first paint | ≤ 1.2 s | ≤ 1.5 s |
| World interactive | ≤ 4.5 s | ≤ 4.5 s |
| Bytes before interactive | ≤ 3 MB | ≤ 1 MB |
| Background after interactive (first 60 s) | ≤ 25 MB | ≤ 12 MB |
| Frame time in world | ≤ 16.7 ms (60 fps) | ≤ 33 ms (30 fps) |
| Draw calls | ≤ 250 | ≤ 120 |
| Triangles in view | ≤ 1.5 M | ≤ 400 k |
| GPU texture memory | ≤ 600 MB | ≤ 200 MB |

## Pipeline
- Geometry: `scratchpad/gp/node_modules/.bin/gltfpack -i in.gltf -o out.gltf -cc -kn -km -vtf` (+ `-si 0.5` only after visual check). Then embed buffers base64 if it must go to the artifact preview (binary .glb is refused there).
- Phone variants: half-size textures, simplified meshes, fewer instances; loader picks `-m` vs `-g` by device, old files as fallback when MeshoptDecoder is unsupported.
- Textures: JPEG q82 for colour, PNG only for alpha; power-of-two; 1K phone / 2K desktop. KTX2/Basis would cut GPU memory ~4–6×: requires toktx/basisu install (needs approval).
- Audio: 96 kbps MP3/AAC, stream with `preload=none`, start only after a gesture.
- Loading order: logo → world shell → current area → neighbours on idle → never the rest.

## Measure, don't guess
- `scratchpad/gzsrv.js` (GitHub-Pages-like gzip server) + `perf6.js page d|m wifi|4g|slow4g` → bytes and timings.
- Compare against the previous version every time and write numbers in `studio/LESSONS.md`.
- Swiftshader frame times are NOT real-device numbers: say so in reports.

## Mistakes
Measuring without gzip (overstated 31 MB vs real 21 MB); duplicate downloads with cache disabled; preloading all rooms; 4K textures on phones; claiming fps without a device.
