# Technical feasibility: the three WORLD 2.0 concepts
**Role:** WebGL & Three.js Engineer (`.claude/agents/webgl-engineer.md`). **Date:** 2026-11-24. **Branch:** `world2-dev`, concept phase only.

Nothing was built. No site code, Blender run or commit was made. No images were made, so no Rendered, Interactive prototype or Mock-up label applies.

The micro-benchmarks below ran in `/tmp/claude-0/bench`, outside the repo, with `devtools/` (sharp 0.35.5, ktx2-encoder 0.6.0, three 0.181.0) and ffmpeg (libx264 and libx265).

**Legend:**
- **[M]** measured in this session.
- **[A]** assumed or estimated (my judgement).
- **[C]** a figure claimed in CONCEPTS.md that I have not checked.

---

## 0. Measurements that change the concepts

### 0.1 Video weight (6 s clips, ffmpeg, CRF 23 for H.264 and CRF 26 for HEVC) [M]
I used three source clips because no Cycles footage of the concepts exists yet:
- **render-like:** the existing `studio/renders/experiment/pavilion_move.mp4`, a soft, low-detail 960×540 Cycles render upscaled. It is the **optimistic** case.
- **sea:** a slow push-in on `a3/bg-surf.jpg`. It is the **realistic coastal** case.
- **photo-detailed:** a push-in on `a3/hero-fest.jpg`, a dense festival crowd. It is the **pessimistic** case.

| Clip (6 s) | GOP 6 H.264 (scrub-friendly) | GOP 12 H.264 | GOP 60 H.264 (normal playback) | GOP 6 HEVC |
|---|---|---|---|---|
| 1600×900, render-like | 2.14 MB (2.85 Mbps) | 1.83 MB (2.44 Mbps) | — | — |
| 1600×900, sea | 4.40 MB (5.87 Mbps); CRF 26: 3.14 MB | 2.67 MB (3.56 Mbps) | 1.25 MB (1.66 Mbps) | 2.93 MB (3.90 Mbps) |
| 1920×1080, render-like | 2.91 MB (3.88 Mbps) | — | 1.85 MB (2.47 Mbps) | 1.23 MB (1.65 Mbps) |
| 1920×1080, photo-detailed | 19.7 MB (26.3 Mbps) | — | 6.70 MB (8.93 Mbps) | 15.2 MB (20.3 Mbps) |
| 1280×720, render-like | 1.44 MB (1.92 Mbps) | — | 0.84 MB (1.12 Mbps) | 0.69 MB (0.91 Mbps) |
| 1280×720, photo-detailed | 10.6 MB (14.2 Mbps) | — | 3.93 MB (5.24 Mbps) | 8.26 MB (11.0 Mbps) |
| 720×1280 portrait, render-like | 1.37 MB (1.83 Mbps) | 1.20 MB (1.60 Mbps) | 0.89 MB (1.18 Mbps) | 0.64 MB (0.86 Mbps) |
| 720×1280 portrait, sea | 3.15 MB (4.19 Mbps); CRF 26: 2.28 MB | 1.94 MB (2.59 Mbps) | 0.86 MB (1.15 Mbps) | 2.12 MB (2.83 Mbps) |
| 720×1280 portrait, photo-detailed | 8.52 MB (11.4 Mbps) | — | 2.82 MB (3.76 Mbps) | 6.71 MB (8.94 Mbps) |

What this means:
- **Scrub-friendly video costs 1.7–3.6× more than normal playback video.** The cost comes from the short GOP.
- Concept A's figures of **"~1.8 MB per desktop segment / ~0.9 MB per phone segment" hold only for the optimistic case at GOP 12**, and only for segments of about 6 s.
- A realistic coastline is **2.7–4.4 MB per desktop segment and 1.9–3.2 MB per phone segment**.
- Fine detail (crowds, pine needles, sparkle on the sea) is the cost driver. A time-lapse also changes every pixel in every frame (sky, shadows), so the real numbers will sit nearer the sea row than the render-like row [A].

### 0.2 Textures: KTX2 against JPEG and AVIF [M]
Two sources were resized square:
- `a3/cabin-lm.jpg`, a real baked lightmap from v153.
- `a3/bg-surf.jpg`, a backdrop.

Settings: ETC1S at quality 128 with mips; UASTC with RDO and Zstd; JPEG q82 mozjpeg; AVIF q55.

| Texture | JPEG q82 | AVIF q55 | KTX2 ETC1S | KTX2 UASTC+Zstd | GPU if RGBA8+mips | GPU as ETC1S→ETC1/BC1 | GPU as UASTC→ASTC/BC7 |
|---|---|---|---|---|---|---|---|
| Lightmap 2048² | 710 KB | 371 KB | **549 KB** | 3.31 MB | 22.4 MB | **2.8 MB** | 5.6 MB |
| Lightmap 1024² | 217 KB | 121 KB | **149 KB** | 874 KB | 5.6 MB | **0.7 MB** | 1.4 MB |
| Backdrop 2048² | 304 KB | 149 KB | 488 KB | 3.36 MB | 22.4 MB | 2.8 MB | 5.6 MB |
| Backdrop 1024² | 104 KB | 58 KB | 143 KB | 978 KB | 5.6 MB | 0.7 MB | 1.4 MB |

- Gzip on top of the .ktx2 files saves under 0.2% [M], so the wire size equals the file size.
- Encode time on 4 CPU cores: ETC1S 1024² takes 3.7 s and UASTC 1024² takes 26 s [M].
- **Conclusion:** ETC1S is **bigger on the wire than AVIF** (1.5–3.3×) but **8× smaller in GPU memory**.
  - Use ETC1S where GPU memory matters: concept C's lightmaps.
  - Do not use UASTC for anything streamed to phones: it is 3.3 MB for one 2048² texture.
  - Do not use ETC1S or UASTC for Shay's photographs (research §2.3).

### 0.3 Alpha depth layers for concept B [M]
Each layer is a photographic plate with an alpha mask covering 35% of the frame, a feathered band.

| Layer | Full-frame AVIF (q55) | 35% layer, WebP (alpha, hidden RGB zeroed) | GPU RGBA8+mips |
|---|---|---|---|
| Desktop 2560×1440, low-detail (sea) | 138 KB | 87 KB | 19.7 MB |
| Desktop 2560×1440, high-detail (crowd) | 467 KB | 223 KB | 19.7 MB |
| Phone 1170×2532 (concept's figure) | 109–327 KB | 59–190 KB | 15.8 MB |
| Phone 900×1950 (my recommendation) | 80–243 KB | 42–137 KB | 9.4 MB |

- My AVIF-with-alpha test kept the hidden RGB, so it came out the same size as the full frame. Real Cycles layers would be premultiplied with black under alpha 0, so AVIF would end up smaller than the WebP figures [A].
- PNG would cost 3–9 MB per layer [M]. Never use it.

### 0.4 Engine bytes (gzip -9) [M]
| File | gzip |
|---|---|
| three r181 `three.module.min.js` + `three.core.min.js` (WebGLRenderer) | 86 + 100 = **186 KB** |
| three r181 `three.webgpu.min.js` | 170 KB, plus core |
| live r128 `vendor/three.min.js` | 149 KB |
| GLTFLoader.js (not minified) | 25 KB |
| KTX2Loader.js | 9 KB |
| meshopt decoder | 6.5 KB |
| basis transcoder (wasm + js) | 245 + 15 = **260 KB** |
| live `index.html` (v153) | 206 KB |

---

## A. SUNLINE: real-time architecture

**Split:**
| Layer | What it is |
|---|---|
| Video | The world: 9 day segments plus field approach clips, pre-rendered in Cycles. |
| Still | Home time-slice, AVIF. |
| DOM | Photos, viewer, dock, arc, booking. |
| WebGL | Only a transparent overlay: sun glint, haze sprites, ±1.5° fake look-around. |

**Recommended build:**
- **Video stack:** two `<video muted playsinline>` elements, ping-ponged so the next segment preloads while one plays. The time scrubber:
  - Chromium, and Safari 16.4+ [A]: a **WebCodecs `VideoDecoder`** decodes into a small ring buffer of `VideoFrame`s around the playhead (about ±12 frames). This gives smooth reverse scrubbing that `currentTime` seeks cannot.
  - Fallback: `currentTime` seeks on GOP-6 files.
- **Camera sync:** `requestVideoFrameCallback` drives the overlay camera from the exported Blender camera track (one JSON per segment, about 5–15 KB gz [A]).
- **Overlay:** three r181 WebGLRenderer with `alpha:true`, loaded **after** first interaction. Alternatively a 10 KB raw-WebGL2 overlay, because A needs no scene graph.
- **Photos:** stay in the **DOM** (`<img>` with `srcset` AVIF/JPEG). Colour is exact, with no tone mapping question, and the View Transitions API can be used. They are never textures.
- **Look-around:** ±1.5° look-around on pre-rendered video is only a 2D pan. The video must be rendered with about 4% overscan and cropped with a CSS or shader offset. It is not true parallax.

**three.js features:** WebGLRenderer (alpha), Sprite/Points for glint and haze, CameraHelper-free camera animation from JSON. No lights, shadows or post-processing.

**Shaders:** an additive glint sprite (sun direction from the camera track) and an optional haze gradient. Both are trivial.

**Quality tiers and FPS governor:**
| Tier | Video | Overlay | Scrubbing |
|---|---|---|---|
| T0 (reduced motion / save-data) | Stills only | — | 400 ms cross-fades |
| T1 phone | 720×1280 HEVC (Safari) or H.264 | Glint only | — |
| T2 desktop | 1600×900 | Glint + haze | WebCodecs scrubbing |

The governor watches dropped video frames (`getVideoPlaybackQuality`) and rAF time. If more than 10% of frames drop for 2 s, it falls back to snapping between minute stills instead of continuous scrubbing.

**Loading order:**
1. Shell, logo, and the Home time-slice AVIF for the current Israel hour.
2. Dock icons. The page is interactive at this point.
3. On idle: the approach clips of the 2 fields nearest the current hour.
4. On hover or approach: that field's scrub segment.
5. Never preload all 9 segments.

**Risks and unknowns:**
1. **Scrub latency on iOS Safari** (seek and decode of H.264/HEVC GOP 6 at 720×1280) is unknown without a device. It is the make-or-break test.
2. Weight is 2–3× the concept's figure (§0.1).
3. Render cost: about 65 h CPU [C] **per composition**, and A needs two compositions (16:9 and 9:16), so about 130 h. Any art change means re-rendering.
4. Re-encoding the time-slice consistently with the segments.
5. Autoplay and scrubbing policies differ in Low Power Mode on iOS [A].

**Effort [A]:**
- 4–6 engineer-weeks: player, streaming, sync, viewer, RTL, reduced motion.
- 130 h+ CPU of renders per art iteration.
- Engineering risk is medium; render risk is high.

---

## B. DEPTH OF FIELD: real-time architecture

**Split:**
| Layer | What it is |
|---|---|
| Baked | 6 premultiplied RGBA depth layers rendered in Cycles, plus one low-res depth map (R8, about 1/4 resolution) per layer. |
| Highlight list | A JSON of 1–2k light points with position, colour and layer, for disc bokeh. |
| WebGL | A compositor: layers + blur + bokeh sprites + grain. |
| Video | Only "past ∞": a 6 s loop with a static camera. |
| DOM | Photos, distance scale, dock. |

**Recommended build:**
- **Renderer:** three r181 WebGLRenderer with an orthographic camera and 6 full-screen planes. Alternatively raw WebGL2, which saves 186 KB, but the team knows three.
- **Blur pyramid:** at load, each layer's mip chain is **regenerated with a Gaussian/dual-Kawase pass** (render-to-mip-level). It is not the box-filter `generateMipmap`, which looks blocky when magnified.
  - Per pixel: CoC = f(layer depth map, focus distance, aperture). The shader blends 2 pyramid levels.
  - The blur runs in **premultiplied alpha**, so blurred foreground edges spread without dark halos.
- **Disc bokeh:** a Gaussian blur of floodlights and string lights does **not** give the disc bokeh the concept sells. One `InstancedBufferGeometry` draw of soft disc sprites (aperture texture) is sized by CoC, with additive blending. This is the key shader.
- **Focus peaking:** a Sobel edge on the layer under the cursor, × (1 − CoC), in ivory.
- **Tap-to-focus:** read the layer alpha and depth at the tap position from CPU-side copies at 1/8 resolution, with no `readPixels`.
- **Gyro parallax (±1.5%):** layer offsets ∝ 1/depth. iOS needs a `DeviceOrientationEvent.requestPermission()` tap, so it is opt-in.
- **Breathing and drift:** a uniform scale and offset.
- **Photo palette tint:** 5 uniforms, as in research idea 3.
- **Video past ∞:** a cross-fade from the layers into a `<video>` behind the canvas, or a VideoTexture on the back plane.

**three.js features:** WebGLRenderer, `WebGLRenderTarget` with mip levels, ShaderMaterial/RawShaderMaterial, InstancedBufferGeometry, VideoTexture (optional).

**Shaders:** layer composite with CoC (2 texture taps + depth tap per layer), Kawase downsample, disc bokeh sprite, peaking edge, film grain. All of them are small.

**Quality tiers and FPS governor:**
| Tier | Layers | Bokeh | Effects |
|---|---|---|---|
| T0 | 5 pre-composed focus stills, cross-fade (reduced motion / no WebGL2) | — | — |
| T1 phone | 900×1950 | 500 sprites | No peaking, DPR 1.5 |
| T2 desktop | 2560×1440 | 2k sprites | Peaking + grain, DPR 2 |

The governor steps down in this order when frames stay over 22 ms (phone) or 17 ms (desktop) for 2 s: grain → peaking → bokeh count ÷2 → DPR 1.0.

**Loading order:**
1. A 40 KB blurred frame [C] as `<img>`. This is the intro.
2. Far layers (sea, then stadium).
3. Festival and near layers. Focus animates as each layer arrives, so the intro *is* the progress bar.
4. Highlight JSON.
5. On idle: room cover thumbnails.
6. On demand: the video loop past ∞.

**Risks and unknowns:**
1. **Bokeh quality:** layered 2.5D with a CoC blur can look like cardboard cut-outs at f/1.2. The disc sprites and in-layer depth maps are mandatory, not optional.
2. **Occluded areas:** each layer must be rendered with the hidden regions filled in (Cycles: render each depth band with the nearer bands hidden, plus a shadow catcher). That is an art-pipeline task.
3. **Phone portrait composition** is a second full set of renders.
4. Hit areas for 18 rooms in one frame. The UX risk is crowding.

**Effort [A]:**
- 3–4 engineer-weeks.
- Renders: 6 layers × 2 compositions + a DOF reference + a 144-frame video plate. This is the fewest CPU hours of the three.
- Engineering risk is **low**.

---

## C. WHERE HE STOOD: real-time architecture

**Split:**
| Part | What it is |
|---|---|
| 3D | Tidal flat, 5 held moments, instanced suspended matter, camera rail between 18 vantages. |
| Baked | KTX2 ETC1S lightmaps, LDR sky dome, small HDR for reflections. |
| Video | Phone fallback flight clips, "time resumes" 5 s clips. |
| DOM | Photo viewer, back of the print, dock. |

**Recommended build:**
- **Engine:** three r181 WebGLRenderer, GLTFLoader + MeshoptDecoder + KTX2Loader.
- **Scenery:** MeshBasicMaterial × lightMap for the flat and the scenery.
- **Wet-sand mirror:** `onBeforeCompile` adds a Fresnel term, a procedural ripple normal (0 bytes, instead of a measured 0.9 MB UASTC normal map) and the reflection. The reflection is a **reflected instanced draw** (matter drawn a second time with a Y-flipped matrix), not a planar reflection render target. Phone tiers use baked reflections in the backplate.
- **Suspended matter:** `InstancedBufferGeometry`, one draw per matter type (drops, spray, confetti, ticker-tape, dust, linen shreds).
  - Positions are procedural from a seed, plus authored hero clusters exported from Blender as points (16-bit quantised, about 8 B per instance).
  - **No per-frame depth sort:** drops use alphaTest/alpha-to-coverage, and glowing spray is additive (order-independent).
  - Gold rim light: a Henyey-Greenstein forward-scatter term in the sprite shader, using the fixed sun direction.
- **Camera:** spline rails between vantages with GSAP-style easing. Look-around is clamped to ±25° yaw and ±10° pitch.
- **"The click":** the photo plane is a **DOM overlay** registered to a projected 3D rectangle (CSS `matrix3d`), so colour stays exact. A WebGL plane would need `toneMapped:false` and sRGB.
- **Post-processing:** ACES/AgX, bloom on emissive only (desktop only), vignette, grain.

**three.js features:** InstancedMesh/InstancedBufferGeometry, KTX2Loader, GLTFLoader + meshopt, lightMap, PMREMGenerator (256² HDR), EffectComposer + UnrealBloomPass (T2 only), CSS3D-style overlay, AnimationMixer for the 5 s "time resumes" clips (or video).

**Shaders:** wet sand (Fresnel + ripple + reflected matter), drop sprite (HG phase + fake refraction from the env map), spray soft particle (depth-fade), floodlight beam cones (additive, depth-fade), and a footprint decal revealed by raking light.

**Quality tiers and FPS governor:**
| Tier | Approach | Matter | Reflections | DPR |
|---|---|---|---|---|
| T0 (phone low/mid, reduced motion, no WebGL2) | Cycles backplate per vantage + 1.2 s flight clips + DOM photo | — | Baked | — |
| T1 (phone high / laptop iGPU) | Real time | 15k | Reflected draw off | 1.5 |
| T2 (desktop dGPU) | Real time | 80k + bloom | On | 2 |

- The governor steps down in this order when over budget for 2 s: bloom → reflected matter → matter ÷2 → DPR −0.25 → drop to T0 (backplates).
- The tier is chosen from the WebGL renderer string, `hardwareConcurrency`, `deviceMemory` and a 1 s warm-up frame-time probe.

**Loading order:**
1. Poster (150 KB) [C].
2. Engine JS (186 KB three + 40 KB loaders).
3. Basis transcoder (260 KB). **It is loaded only if the tier is T1 or T2**, so T0 phones never pay for it.
4. Flat + sky + overview LODs of the 4 moments.
5. Nearest field, full detail.
6. Neighbours on idle.
7. "Time resumes" clips only on demand.

**Risks and unknowns:**
1. **Fill rate:** soft spray sprites seen through a 200 mm lens become huge screen-filling quads. This is the #1 phone risk and needs device tests.
2. **Two products:** real time plus the T0 backplate/clip path. Both must be maintained.
3. **18 hand-registered vantages:** each needs a camera-to-photo match.
4. Shader compile and first-frame hitch with three r181 (research §2.1 found 5–10× slower first frames with WebGPU; WebGL is fine but still needs a warm-up compile behind the poster).
5. "Particles look" art risk.
6. The iOS memory ceiling is unknown.

**Effort [A]:**
- 8–12 engineer-weeks: the scene, the matter system, the wet sand, the rails, 18 registrations and the T0 fallback.
- Renders: lightmap bakes, 18 backplates × 2 orientations, 18 × 1.2 s clips (about 520 frames), and 5 × 5 s clips.
- This is the highest risk of the three.

---

## Summary
| | A SUNLINE | B DEPTH OF FIELD | C WHERE HE STOOD |
|---|---|---|---|
| Core tech | Scrubbed Cycles video + DOM + thin overlay | Six baked layers + WebGL CoC/bokeh compositor | Real-time three r181 + baked lightmaps + video fallback |
| Make-or-break unknown | iOS scrub latency | Bokeh believability (cut-out look) | Phone fill rate, two code paths |
| Engineering effort [A] | 4–6 weeks | 3–4 weeks | 8–12 weeks |
| Render (CPU) cost [A] | Highest (about 130 h per iteration) | Lowest | Medium-high |
| Engineering risk | Medium | **Low** | **High** |

**Verified [M]:**
- Every number in §0.
- Engine file sizes.
- The existence of the render-like source clip.

**Assumed [A]:**
- All effort figures.
- WebCodecs support on Safari.
- That Cycles layer and footage compression falls between my sources.
- Every runtime frame figure. **No frame time was measured: swiftshader is not a device, and no device was used.**
