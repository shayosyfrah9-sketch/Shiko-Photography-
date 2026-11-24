---
name: shiko-realtime-webgl
description: Three.js/WebGL (and WebGPU where justified), GLSL shaders, PBR, post-processing and responsive immersive layouts for SHIKO WORLD 2.0. Use when building or changing anything rendered in the browser.
---
# Real-time WebGL (covers: advanced Three.js, WebGL & WebGPU engineering, GLSL shaders, real-time rendering, responsive immersive experiences)

## Stack decision
- Production site today: three.js r128 UMD, self-hosted (vendor/three.min.js), GLTFLoader + MeshoptDecoder. Any upgrade (e.g. r16x ES modules, WebGPURenderer) is a decision logged in `studio/DECISIONS.md` with a fallback plan; WebGPU only behind feature detection with a WebGL2 path.
- CDN only from cdnjs/jsdelivr/unpkg pinned versions in previews; self-host for the live domain.

## Rendering recipe for "Unreal-like" in a browser
1. Baked lighting (Blender) for static architecture → MeshBasic/Lambert × lightmap: cinema quality at mobile cost.
2. HDRI/PMREM environment for reflections; real-time sun only for moving things.
3. Far scenery = pre-rendered panorama/backplates; mid = impostors; near = real geometry.
4. Post: ACES/AgX tone mapping, subtle bloom on emissive only, vignette, film grain 2–3%, depth-of-field only for far layers (desktop only).
5. Custom shaders via onBeforeCompile; keep `customProgramCacheKey` unique per variant.

## Responsiveness
- Quality tiers by device: tier from `navigator.hardwareConcurrency`, devicePixelRatio cap (desktop 2, phone 1.5), and a runtime FPS governor (drop shadows → DOF → particles → resolution) when fps < 45 for 2 s.
- Phone portrait has its own camera framings; never just a scaled desktop.
- Pause rendering when the tab is hidden or a full-screen photo covers the canvas.

## Photos in 3D
Never stretch: plane size from the real aspect ratio (`ASP` map). Textures sRGB, anisotropy max, `toneMapped=false` so photo colours stay exact. Load the full-res only for the focused photo.

## Common mistakes
Shadow maps on everything; unbounded pixel ratio; transparent sorting fights (use alphaTest); recompiling shaders per frame; forgetting to dispose textures on room exit; errors swallowed by try/catch (this project lost trees and the service worker that way: always log in dev builds).

## Test
Playwright with `--use-gl=swiftshader` for functional/screenshot checks (`shiko-qa-guardian`); frame time on real devices before claiming performance.
