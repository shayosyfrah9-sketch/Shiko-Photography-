# Performance budgets: the three WORLD 2.0 concepts
**Role:** Performance Engineer (`.claude/agents/performance-engineer.md`). **Date:** 2026-11-24. **Branch:** `world2-dev`, concept phase only.

Nothing was built and nothing ran on a device. No images were made, so no Rendered, Interactive prototype or Mock-up label applies.

**Legend:**
- **[M]** measured in this session (micro-benchmarks in `/tmp/claude-0/bench`; see `tech-feasibility.md` §0).
- **[P]** measured by the previous thread.
- **[A]** estimated: built from [M] parts plus assumptions.
- **[C]** a figure claimed in CONCEPTS.md.

> **Important:** **no frame rate, frame time or GPU figure in this file is a device number.**
> - No prototype exists.
> - Swiftshader (the CPU WebGL in this container) frame times are **not** device numbers either, and none were used here.
> - Every fps, draw-call, triangle and GPU-memory value below is a **budget or a design estimate**. It must be confirmed on Shay's real phone and computer (Remote Control) before anyone claims it.

## Method
- **Bytes** are gzip transfer sizes. Images and video do not shrink under gzip; ktx2 shrinks by less than 0.2% [M].
- **Time to interactive (TTI) on 4G** (9 Mbps, 85 ms, the skill's profile) is estimated as:
  4 round trips (0.34 s) + bytes before interactive × 8 / 9 Mbps + decode and compile time [A].
  - Decode and compile: phone 0.3–1.5 s by concept, desktop about 0.3–0.6 s.
- **Live v153 comparison:**
  - After entering, the phone loads **≈ 21 MB gzip** [P].
  - Live first-view bytes were **not re-measured in this session**: the throttled browser run was not permitted. The fixed floor before any image or model is `index.html` 206 KB + three r128 149 KB = **0.36 MB** [M].
  - Single live models (gzip) [M]:
    - `a3/bloomfield.json`: 4.26 MB
    - `tree3-oak.json`: 3.57 MB
    - `cabin.json`: 2.22 MB
    - `bloomfield-m.json`: 1.00 MB
  - Live draw calls, triangles and fps were not measured here.
- **Skill budgets** (`shiko-asset-performance`):
  - Bytes before interactive: phone ≤ 1 MB, desktop ≤ 3 MB.
  - Background bytes in the first 60 s: phone ≤ 12 MB, desktop ≤ 25 MB.
  - Draw calls: phone ≤ 120, desktop ≤ 250.
  - Triangles: phone ≤ 400 k, desktop ≤ 1.5 M.
  - GPU textures: phone ≤ 200 MB, desktop ≤ 600 MB.
  - Frame rate: phone 30 fps, desktop 60 fps.
  - The research doc is stricter on phones: ≤ 80 draw calls, ≤ 300 k triangles, ≤ 150 MB GPU.

---

## A. SUNLINE (scrubbed Cycles video)
| Metric | Desktop | Phone | Basis |
|---|---|---|---|
| First view (interactive on the Home still) | **0.30–0.40 MB** | **0.20–0.30 MB** | Shell ~0.1 MB [A] + Home AVIF (desktop 150–250 KB, phone 80–150 KB) [M-scaled] |
| TTI, 4G | ~1.0 s | ~1.0–1.2 s | Formula |
| Total after entering one field | **3.3–4.2 MB** | **2.0–2.7 MB** | + overlay three 186 KB [M] + 1.6 s approach clip (0.23–0.33 MB) [M-scaled] + one 6 s GOP-12 scrub segment (desktop 1.83–2.67 MB, phone 1.20–1.94 MB) [M] + 3 photos [A] |
| Whole day (9 segments) | 16–24 MB + photos | 11–17 MB + photos | 9 × segment [M] |
| Concept's claim [C] | 1.8 MB per segment | 0.9 MB per segment | **0.6–0.75× of my GOP-12 numbers; 0.4× of the GOP-6 sea numbers** |
| Video bitrate cap | ≤ 3.6 Mbps (1600×900, H.264 GOP 12) | ≤ 2.6 Mbps (720×1280, H.264 GOP 12; HEVC on Safari) | [M] |
| Draw calls | ≤ 10 | ≤ 10 | Overlay only [A] |
| Triangles | < 10 k | < 10 k | [A] |
| GPU / decoded memory | ~100–150 MB | ~60–90 MB | Video surfaces + canvas + ≤ 8 decoded photos [A] |
| Target fps | Video 24–30 native; UI 60 | Video 24–30; UI ≥ 30 | Budget |

**Against the skill budgets:**
- First-view bytes and TTI are the best of the three, and about the same as the live floor.
- Background bytes stay within 12 MB on a phone only if prefetch is limited to 2 segments (2.4–3.9 MB).
- The risk is not GPU. It is **network and decoder**:
  - A visitor who scrubs the whole day downloads 11–17 MB on a phone. That approaches live v153's 21 MB.
  - **Scrub latency on iOS is unknown.**

---

## B. DEPTH OF FIELD (6 baked layers + WebGL compositor)
| Metric | Desktop | Phone | Basis |
|---|---|---|---|
| First paint | 40 KB blurred frame [C] | 40 KB | — |
| First view (all 6 layers, focus works) | **1.4–1.8 MB** | **0.85–1.0 MB** | 6 layers (desktop 2560×1440 ≈ 0.95–1.3 MB; phone 900×1950 ≈ 0.5–0.6 MB) [M-scaled] + depth maps 0.09–0.15 MB + three 186 KB [M] + shell [A] |
| TTI, 4G | ~2.0–2.3 s (first paint ~0.5 s) | ~1.6–2.0 s | Formula + 6 AVIF decodes + pyramid build [A] |
| Total after entering one field | **~2.2 MB** | **~1.3 MB** | Focus needs no new world bytes; + 3 photos [A] |
| + Video past ∞ (6 s loop, static camera) | +0.9–1.3 MB | +0.9–1.3 MB | GOP-60 720p/portrait measured with a *moving* camera: 0.84–1.25 MB [M]. A static camera will be smaller [A]. Claim 1.5 MB [C]: OK. |
| Draw calls | 10–14 | 10–14 | 6 layers + bokeh + post [A] |
| Triangles | < 5 k | < 5 k | Plus 500–2k bokeh quads |
| GPU texture memory | ~220 MB | ~120 MB | Layers 6 × 19.7 MB / 6 × 9.4 MB [M] + render targets + ≤ 8 / ≤ 6 photos [A] |
| Target fps | 60 | 60 (floor 30) | Budget; fill is ~7× overdraw at DPR 1.5 [A] |

**Against the skill budgets:**
- It meets every budget.
- Phone first view (0.85–1.0 MB) sits **on** the 1 MB line. To keep margin:
  - Use 900×1950 layers, not the concept's 1170×2532, which would add 0.3 MB and +38 MB GPU [M].
  - Load the 2 nearest layers last, behind the intro.
- It has the lowest GPU, draw-call and network risk of the three.

---

## C. WHERE HE STOOD (real-time three r181 + T0 video fallback)
| Metric | Desktop (T2) | Phone T1 (real time) | Phone T0 (backplates) | Basis |
|---|---|---|---|---|
| First paint | Poster 150 KB [C] | 100 KB | 100 KB | — |
| First view, bytes | **~2.9 MB** | **~2.1 MB** | **~0.4 MB** | Engine: three 186 + loaders ~40 + basis 260 KB [M]; flat lightmap ETC1S 549 KB (2048) / 149 KB (1024) [M]; sky/HDR ~0.15 MB, overview LODs ~0.4 MB, nearest field 0.6–1.0 MB [A] |
| TTI, 4G | ~3.5 s | **~3.0–3.8 s** | ~1.0 s | Formula + wasm init, transcode and shader compile [A] |
| Total after entering one field | **~4.5 MB** | **~2.8 MB** | **~1.1–1.4 MB** | + rest of field, 3 photos; T0: backplate + 1.2 s clip 0.18–0.56 MB [M-scaled] |
| All fields | ~6 MB [C] + photos | ~5 MB + photos [A] | 18 × (0.12 + 0.25) ≈ 6.7 MB [A] | — |
| Video bitrate | 5 s "time resumes" clip ≤ 2.5 Mbps | Flight clip ≤ 1.2–1.6 Mbps (720×1280 GOP 60/12) [M] | Same | — |
| Draw calls | 60–90 | ≤ 60 | ≤ 10 | 4 fields × ~6 + matter 6 (×2 reflected) + post [A] |
| Triangles | 0.6–0.9 M | 0.2–0.25 M | < 10 k | 80k / 15k impostors × 2 tris (×2 reflected) + scenery [A] |
| GPU texture memory | 200–250 MB | 90–130 MB | ~60 MB | ETC1S lightmaps 2.8 / 0.7 MB each [M] + HDR render targets + photos [A] |
| Target fps | 60 | 30 | UI 60 | Budget |

**Against the skill budgets:**
- **The phone T1 first view (~2.1 MB) fails the 1 MB budget.** It passes the research's 2.5 MB line.
- Plan to close the gap:
  - Make the poster + DOM dock interactive at about 0.4 MB, so Home, WhatsApp and booking work immediately.
  - Stream the 3D upgrade in the background.
  - Send phones to T0 unless a warm-up probe passes.
  - Load basis only for T1/T2.
- Desktop passes (2.9 MB ≤ 3 MB, just).
- **Fill rate from soft spray sprites at 200 mm** is unmeasurable without a device and is the largest risk.
- It also needs two code paths.

---

## Comparison
| | Live v153 | A SUNLINE | B DEPTH OF FIELD | C WHERE HE STOOD |
|---|---|---|---|---|
| Phone first view | ≥ 0.36 MB floor [M] (full value not re-measured) | 0.2–0.3 MB | 0.85–1.0 MB | T1 ~2.1 MB / T0 ~0.4 MB |
| Phone after entering a field | **≈ 21 MB [P]** | 2.0–2.7 MB | ~1.3 MB | T1 ~2.8 / T0 ~1.1–1.4 MB |
| Desktop first view | not measured | 0.3–0.4 MB | 1.4–1.8 MB | ~2.9 MB |
| Desktop after a field | not measured | 3.3–4.2 MB | ~2.2 MB | ~4.5 MB |
| TTI 4G, phone [A] | not measured | ~1.1 s | ~1.8 s | T1 ~3.4 s / T0 ~1.0 s |
| Draw calls, phone | not measured | ≤ 10 | 10–14 | ≤ 60 |
| Triangles, phone | not measured | < 10 k | < 5 k | 0.2–0.25 M |
| GPU memory, phone | not measured | 60–90 MB | ~120 MB | 90–130 MB |
| Video | none | ≤ 2.6 Mbps scrub (core of the site) | 1 lazy loop | Fallback clips |
| Target fps (phone) | — | 30 (UI) | 60 | 30 |

**Mid-range phone verdict (to be confirmed on a device):**
- **Safest: B. DEPTH OF FIELD.**
  - Fixed, tiny geometry, about 12 draw calls, and about 1 MB total.
  - Its cost does not grow as the visitor explores: every field after the first is free except for photos.
- **Middle: A. SUNLINE.**
  - GPU is trivial and the first view is the fastest.
  - The bytes grow with exploration (11–17 MB for the whole day).
  - It depends entirely on iOS seek and decode behaviour for 720×1280 short-GOP video. That is unmeasured and binary: it is either smooth or not.
- **Riskiest: C. WHERE HE STOOD.**
  - It is the only concept that fails the 1 MB phone first-view budget in real-time mode.
  - It is fill-rate bound on soft sprites.
  - It needs a second (T0) product to be safe on phones.

All three are an order of magnitude below live v153's ≈ 21 MB phone-after-entering figure [P].

**Verified [M]:** video bitrates, texture and layer sizes, and engine sizes in `tech-feasibility.md` §0, plus the live index and model gzip sizes. **Assumed [A]:** every total that combines them, every TTI, draw-call, triangle, GPU and fps figure. **Not measured:** live v153 first view (the browser run was denied in this session) and every device frame time.
