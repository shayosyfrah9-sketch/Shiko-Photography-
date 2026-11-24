# SHIKO WORLD 2.0 — research for the concept phase
Innovation Researcher, 2026-11-24, branch `world2-dev`. Text only: no images were made, so no Rendered / Interactive prototype / Mock-up labels apply.

**Legend.** **[V]** means verified: I fetched and read the source on 2026-11-24. **[V-2nd]** means the claim comes from a secondary source (a news site or forum) and is not first-party. **[A]** means assumed: my judgement or prior knowledge, with no source checked today. Every phone budget I propose myself is marked [A].

---

## 1. References: what to learn from each, and which trap to avoid

### A. Award-level interactive web

**1. Igloo Inc (abeto), Awwwards Site of the Year 2024.** https://www.igloo.inc/ · case study https://awwwards.com/igloo-inc-case-study.html
- [V] SOTY 2024, made by abeto ([awwwards](https://www.awwwards.com/annual-awards-2024/site-of-the-year)). The 2026 Webby page credits the studio as "Bureaux" ([webby](https://winners.webbyawards.com/2026/websites-and-mobile-sites/features-design/best-visual-design-aesthetic/361001/igloo-inc)). I have not resolved this credit conflict.
- [V] The intro renders in real time with code and shaders instead of video, to keep file size down. Particles are driven by VDB volumes compressed "smaller than a typical website image". Shaders and textures compile in the background during the initial load. Text "scrambles" offset an SDF texture instead of changing the HTML.
- **Learn:** one material idea (ice) carries the whole brand, including transitions and type. For SHIKO, choose one physical material that belongs to photography (light, the film base, the darkroom) and let it carry everything.
- **Trap:** abstract spectacle with no content in it. On SHIKO the 3D must never compete with the photographs.

**2. Lusion v3 (lusion.co), Awwwards Site of the Month (May).** Case study https://awwwards.com/case-study-for-lusion-by-lusion-winner-of-site-of-the-month-may.html
- [V] Their stated rule: "You don't need to do everything real-time." Cloth was simulated in Houdini and blended at runtime from 4 drag directions. Normal, AO, thickness and diffuse lighting were baked into images. **One scene is an offline Redshift video with a low-poly glTF and the camera data on top. It adds a cursor-following light and about 1.72° of camera look-around, and weighs 150 KB.** The mobile build uses 1,024 vertices instead of 4,096 (animation data 246 KB vs 983 KB). The site is fully static.
- **Learn:** this is the strongest proof that a cinematic look on a phone comes from baking and video, not real-time GI. The mobile build is a lighter version of the same design, not a different site.
- **Trap:** a studio showreel aesthetic ("blow people's minds"). Shay's site has a job to do: get people to book.

**3. Immersive Garden × Cartier, Watches & Wonders 2025.** https://www.awwwards.com/watches-wonders-immersive-experience-for-cartier.html
- [V] Six 3D scenes, one per watch, built as a mirror of the physical pavilion's intimate alcoves. Hidden interactions reward exploring. Sound (Web Audio, by Mooders) is treated as a narrative layer. Stack: three.js, Blender, GSAP, Lenis.
- **Learn:** small, intimate chambers, each built around one hero, beat one big open map. This fits four domains with 18 rooms.
- **Trap:** a luxury product as the hero. Here the hero is a flat photograph, so the architecture has to frame it, not compete with it.

**4. Active Theory v5 (activetheory.net).** https://www.webbyawards.com/crafted-with-code/active-theory
- [V] They planned three environments and built eight. Going from one scene to several "really adds to the storytelling" and keeps repeat visits fresh. Built on their own Hydra framework.
- **Learn:** keep one ambience and change the place. Four domains in one visual language, not four art styles.
- **Trap:** environments used as wallpaper behind generic UI.

**5. Bruno Simon folio 2025.** https://www.awwwards.com/brunos-portfolio-case-study.html
- [V] You drive a car. There are weather and seasons, a leaderboard and unlockable skins. three.js TSL on WebGPU with a WebGL fallback, ETC1S/UASTC textures, and a mobile preset that turns off DOF and water blur and lowers shadow resolution.
- **Learn:** the tech pattern (TSL with a fallback, an automatic mobile preset, instancing and merged geometry).
- **Trap: this is exactly the "game" Shay rejected.** Driving, scores and achievements are the opposite of the brief.

**6. "Where Worlds Take Shape", Awwwards SOTD, 3 May 2026.** https://www.awwwards.com/sites/where-worlds-take-shape
- [V] A portfolio rebuilt as a "playable WebGL world". It scored **Usability 6.81, its lowest score**, against Creativity 7.74.
- **Trap, with evidence:** the jury itself marks playable portfolio worlds down on usability. Our navigation must be choose-and-glide, not steer-and-walk.

### B. Photographs in space: exhibitions, installations, titles

**7. Lina Bo Bardi's glass easels, MASP (1968; revived 2015).** https://www.dezeen.com/?p=790265
- [V] Each painting hangs on a glass pane set in a concrete cube. There are no walls and no fixed route, and **the label is on the back of the glass**.
- **Learn:** photos as free-standing objects in an open field, and walking around a photo to read its story. This answers "the world is the stage, the photo is the art" for PORTRAITS & BRANDING. The glass is structure here, not decoration, which is different from the rejected "Aperture Pavilion" cliché.
- **Trap:** glass and concrete minimalism that reads as a generic architecture render.

**8. The Family of Man, MoMA 1955 (installation by Paul Rudolph).** https://www.paulrudolph.institute/195404-family-of-man-exhibit
- [V] 503 images by 273 photographers. Prints ranged from 8×10 inches to 10×12 feet, arranged to create "drama as visitors moved through", as "an architectural as well as pictorial experience."
- **Learn:** **a change of scale is a camera move.** One decisive frame at monumental size (a goal at Bloomfield, a dust-lit crowd at Ozora) and the rest of the set at human size.
- **Trap:** nostalgic museum pastiche.

**9. Wolfgang Tillmans, *To look without fear*, MoMA 2022–23.** https://www.moma.org/calendar/exhibitions/5440 · https://www.sfmoma.org/read/the-voracious-eye-of-wolfgang-tillmans/
- [V] Unframed prints pinned or taped up, with no separate series. Four "industrially determined print sizes" make a "language matrix", in constellations from floor to ceiling.
- **Learn:** a **fixed size system** (for example 4 plane sizes driven by the `ASP` map) gives a 3D gallery rhythm without a grid that looks like a template.
- **Trap:** a collage that becomes noise on a 390 px wide phone.

**10. True Detective main titles (Patrick Clair / Elastic, 2014).** https://www.artofthetitle.com/title/true-detective
- [V] Built from still photographs. **Landscape photos were projected onto low-poly geometry, and slow virtual cameras moved through them.** Some footage was slowed to 10–20%.
- **Learn:** camera-projection mapping makes 2.5D spaces from real photographs. It is the cheapest way to put Shay's own images into the architecture (the festival field, the stadium tunnel) without modelling them.
- **Trap:** the double-exposure portrait has been copied to death.

**11. Charles & Ray Eames, *Glimpses of the USA*, Moscow 1959.** https://eamesfoundation.org/work/glimpses-of-the-u-s-a-film/
- [V] Seven screens of about 30 ft each and 2,200+ still and moving images in about 12 minutes, inside Fuller's dome.
- **Learn:** for VIDEO, show many screens at once, in sync, as architecture: a cinema whose walls are synchronised clips.
- **Trap:** overload. On phones, play one live video at a time.

**12. Hiroshi Sugimoto, *Theaters* (from 1976).** https://hyperallergic.com/323313/hiroshi-sugimotos-otherworldly-photographs-of-movie-theaters/
- [V] The premise: "What happens if you shoot a whole movie in a single frame?" (the screen burns to white).
- **Learn:** a photographer's way into the VIDEO domain. Time can be compressed into one image (see idea 2).
- **Trap:** too conceptual for clients who want to see the reel quickly.

**13. Apple iOS 26 "Spatial Scenes".** https://9to5mac.com/2025/06/10/psa-spatial-scenes-will-work-on-any-iphone-running-ios-26/
- [V-2nd] Depth is reconstructed from a single 2D photo on the device, and the photo shifts as you move the phone (iPhone 12 and later).
- **Learn:** visitors' phones are teaching them that photographs can have depth. Subtle gyro parallax will feel native, not gimmicky.
- **Trap:** stretched edges and the wobble of "3D Ken Burns". Keep amplitude under about 2% [A].

**14. World Labs Spark 2.0 (Gaussian splat worlds).** https://worldlabs.ai/blog/spark-2.0
- [V] A 40M-splat world is claimed to run "smoothly on smartphones" through LoD streaming. No frame rates are published.
- **Learn:** the technical ceiling for real-place capture (see §2.2).
- **Trap:** splats look like "a 3D scan". That is impressive, but it is a look, not an idea.

---

## 2. Rendering and tech feasibility, late 2026

### 2.1 WebGPU and three.js WebGPURenderer
- [V] WebGPU ships in **Safari 26 on iOS, iPadOS, macOS Tahoe and visionOS 26**, and in Chrome, Edge and Firefox ([web.dev, 25 Nov 2025](https://web.dev/blog/webgpu-supported-major-browsers)). [V-2nd] It has been "officially Baseline" since January 2026 ([vr.org](https://vr.org/articles/webgpu-baseline-2026-three-js-webxr-default)).
- [V] The three.js manual still calls WebGPURenderer **"experimental"**. Depending on the scene, you may get "better performance with `WebGLRenderer`", which "is still maintained and the recommended choice for pure WebGL 2 applications". Four limits matter for us ([threejs manual](https://threejs.org/manual/pages/webgpurenderer.html)):
  - **ShaderMaterial, RawShaderMaterial and `onBeforeCompile` are not supported.** Shaders must be ported to TSL.
  - EffectComposer is not supported; there is a new post-processing stack instead.
  - It falls back to WebGL 2 automatically.
  - Initialisation is async.
- [V-2nd] r183 forum benchmark (desktop, 4,000 meshes): WebGPURenderer had **about 2× the CPU cost per frame and a 5–10× slower first frame** than WebGLRenderer, on both backends ([forum](https://discourse.threejs.org/t/webgpurenderer-2x-slower-cpu-and-5-10x-slower-first-frame-than-webglrenderer-on-many-mesh-scenes-r183-same-on-both-backends/91904)).
- **Verdict [A]:** build v1 on **WebGLRenderer (WebGL2, three r181 already in devtools)**. A baked, video-backed world needs none of WebGPU's compute. Keep shader logic small and isolated so it can be ported to TSL later. This matches our skill rule: WebGPU only behind feature detection, with a WebGL2 path. Visitors on iOS 18–25 get WebGL2 either way.

### 2.2 Gaussian splats on phones
- [V] Spark (World Labs) is MIT-licensed and runs on WebGL2 ("98%+ WebGL2 support"). It mixes splats with three.js meshes and reads PLY, SPZ, SPLAT, KSPLAT and SOG ([README](https://raw.githubusercontent.com/sparkjsdev/spark/main/README.md)).
- [V] Spark 2.0 facts ([blog, Apr 2026](https://worldlabs.ai/blog/spark-2.0)):
  - LoD budget of **500K–2.5M splats per frame "depending on device type"**.
  - "Most consumer devices can only render 1–5M splats" interactively, and mobile browsers cap GPU memory.
  - **10M splats in .SPZ is 200–250 MB.** SPZ cannot load progressively, so they introduce the .RAD format.
  - A coarse 64K-splat version appears first.
- [V] WebSplatter (arXiv 2602.03207) claims 1.2–4.5× speedups over web viewers, but the abstract gives no phone figures.
- **Verdict [A]:** splats are feasible only as one hero element per domain, about 300–500K splats and 10–25 MB, streamed after first paint. They are not a ground layer. We also have no capture of real places and no GPU here to train splats. **Not recommended for v1.**

### 2.3 Textures: KTX2 / Basis
- [V] A decoded PNG or JPEG sits uncompressed in GPU memory: width × height × 4 × 1.333 bytes with mips. That is **about 22.4 MB for 2048²** and 90 MB for 4096². KTX2 cuts GPU memory **4–8×**. ETC1S is the default (small files, weak on normal maps); UASTC is higher quality, about BC7, and its files are 1–2× JPEG size ([Don McCurdy](https://www.donmccurdy.com/2024/02/11/web-texture-formats/)).
- **Rule for SHIKO [A]:**
  - **Architecture textures and lightmaps:** KTX2 (ETC1S for albedo and lightmaps, UASTC for normals).
  - **Photographs:** AVIF or JPEG, never ETC1S. Its block artefacts hurt photos, and colour accuracy matters for an artist.
  - **Photo sizes:** 1280–1600 px on the long edge inside 3D, with full resolution only in the HTML lightbox.
  - **Photo memory:** a 1600×1067 photo costs about 9 MB of GPU memory (same formula), so **keep at most about 8 photo textures resident on a phone**. Dispose them on room exit.

### 2.4 Geometry: meshopt
- [V] "Meshopt decoding is considerably faster than Draco decoding." It also compresses morph targets and animation, and it needs gzip or brotli on top to reach its full size reduction ([gltf-transform](https://gltf-transform.dev/modules/extensions/classes/EXTMeshoptCompression)).
- **Verdict [A]:** use meshopt with quantisation through `@gltf-transform` 4.5.1, which is already in devtools. Skip Draco.

### 2.5 Pre-rendered video backplate with a live 3D overlay
- [V] This is proven by Lusion (§1.2): an offline render, plus a low-poly proxy and the exported camera, a live light and a ±1.72° look-around, at 150 KB.
- [V] Lusion had to hack frame sync with `readPixels` because `video.currentTime` was unreliable. Today `requestVideoFrameCallback` handles it: **Safari and iOS 15.4+, Chrome 83+, Firefox 132+** ([caniuse](https://caniuse.com/mdn-api_htmlvideoelement_requestvideoframecallback)).
- **Fit:** Blender Cycles on this machine (CPU, 4 cores) can render the backplates. Domain flythroughs become 4–8 s clips, and photos, hotspots and light react live on top.
- **Phone budget [A]:**
  - 720×1280 portrait H.264/HEVC at about 1.5–3 Mbps, so a 6 s loop is about 1–2 MB.
  - Autoplay needs `muted playsinline`. This is standard behaviour I did not re-check today.
  - Only one decoding video at a time.
  - Use a poster JPEG as the first frame.

### 2.6 Baked lighting
- [V] Lusion baked AO and diffuse into images (§1.2), and our own skill recipe says the same. Blender bakes on CPU here.
- **Budget [A]:** each domain gets one or two 2048² lightmaps in KTX2 (ETC1S, about 2.8–5.6 MB of GPU memory each, by McCurdy's 4–8× figure). Materials are MeshBasic/Lambert × lightmap. No real-time shadows on phones.

### 2.7 View Transitions API
- [V] Same-document transitions became **Baseline on 14 Oct 2025** when Firefox 144 shipped ([web.dev](https://web.dev/blog/same-document-view-transitions-are-now-baseline-newly-available)).
- [V] Cross-document transitions work in **Chrome 126+ and Safari/iOS 18.2+**, with partial support in Firefox 144+. Global usage is 89.6% ([caniuse](https://caniuse.com/cross-document-view-transitions)).
- **Use [A]:** for the HTML layer (world → gallery grid → lightbox → booking) and for smooth handoffs such as photo thumbnail → full screen. It does not animate inside the WebGL canvas: snapshot the canvas or cross-fade there.

### 2.8 Concrete phone budgets
| Item | Value | Status |
|---|---|---|
| Draw calls | 100–200 is "a rough target for low end mobile" | [V] [PlayCanvas](https://developer.playcanvas.com/user-manual/optimization/guidelines/) |
| Draw calls, SHIKO target | ≤ 80 on phone (merge plus instancing) | [A] |
| Frame rate | >60 recommended, 45–60 acceptable, 5th percentile ≥ 30 | [V] [Viverse](https://docs.viverse.com/optimization/optimization-recommendations-and-requirements) |
| Memory | <800 MB recommended; a tab crash fails review | [V] Viverse |
| Loader visible | ≤ 3 s | [V] Viverse |
| Median test device | iPhone 12 / Galaxy S20; floor Galaxy A16 | [V] Viverse |
| iOS per-tab WebGL memory cap | **no official figure found**; crashes are reported in forums | Unverified ([Apple forum](https://developer.apple.com/forums/thread/741624)) |
| SHIKO first view | ≤ 2.5 MB transferred, interactive ≤ 4 s on 4G; triangles ≤ 300K; GPU textures ≤ 150 MB; DPR cap 1.5 | [A] |

---

## 3. Ideas nobody asked for

1. **"The back of the print"** (after Bo Bardi's labels on the back of the glass).
   - Every photo in the world can be turned over, by a swipe or by walking around it. The back holds the decisive moment in Shay's words: one line, the place, the time, the shutter speed from EXIF, and the frame shot 0.5 s before it, if the burst exists.
   - It makes "the decisive moment" visible as a mechanism. No other portfolio explains why this frame won.
   - It costs almost nothing: one extra quad per photo, with the text in HTML.

2. **"Whole film in one frame"**, a Sugimoto treatment for the VIDEO domain.
   - Each screen in the cinema at rest shows one still, made offline by averaging or max-blending all frames of the clip. The result is a ghostly long exposure of that event. Touch a screen and it plays.
   - It is a photographer's way to show video, and it is also a **performance device**: still images until the visitor asks, so only one video ever decodes.

3. **The world takes its light from the photograph.**
   - When a photo is focused, the fog, rim light and sky tint lerp about 10–15% toward that photo's precomputed palette. A Zoodana night shot cools the room; a surfing sunrise warms it.
   - The world stays subordinate to the image, so this is not a "colour takeover" (Shay's rule). Keep the amplitude low and the transition at about 600 ms.
   - It costs about 5 uniforms and a 6-colour palette per photo, computed at build time.

4. **Depth you can tilt.**
   - Precompute a depth map for each hero photo with **Depth Anything V2 Small, which is Apache-2.0**. The Base, Large and Giant models are **CC-BY-NC-4.0, so they cannot be used for a commercial site** ([README](https://raw.githubusercontent.com/DepthAnything/Depth-Anything-V2/main/README.md), [V]).
   - On a phone, gyro parallax of ≤ 2% moves the subject a little off the background, in the same gesture iOS 26 has taught people.
   - It costs one 256–512 px greyscale map per photo and runs offline. Nothing runs in the browser.
   - **The risk:** it can look like a gimmick, and it must never warp faces.

5. **Israel-time light** (extra).
   - Three baked lighting states (day, golden hour, night) chosen by the real time in Israel. At night the FESTIVALS domain is the one that glows, and SPORT turns on its floodlights.
   - Cost: three lightmap sets for each domain that uses this [A].

---

## 4. Licence notes
- three.js: MIT [A, well known]. Spark: MIT [V]. Depth Anything V2 Small: Apache-2.0; larger models are non-commercial [V].
- Poly Haven assets: CC0, and downloads work from this machine according to BRIEF.md [V via project docs].
- The references above are for learning only. Copy no assets, shaders or layouts from them.

## 5. Not verified, and why
- The Awwwards SOTY 2025 winner (the annual-awards page did not list it). The FWA SOTY winner (searches returned nothing relevant).
- Bruno Simon's live URL and award. The Codrops interviews (fetch failed).
- An official iOS WebGL memory cap.
- Splat or WebGPU frame rates on phones.
- The `muted playsinline` autoplay rules.
- The 2–4 Mbps video bitrates.
- Every SHIKO budget marked [A].

Real-device frame timing is required before any performance claim (skill rule).
