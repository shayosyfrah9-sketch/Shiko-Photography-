---
name: shiko-visual-critique
description: Independent critique loop for renders, screenshots and prototypes of SHIKO WORLD 2.0 (photorealism, originality, composition, lighting, materials, innovation). Use after every render or screenshot and before showing anything to Shay.
---
# Visual Critique (covers: independent visual critique, photorealism quality assessment, creative innovation review)

## Rule
Nothing important ships after a first attempt. Minimum 3 rounds: create → look at the actual image (Read the PNG/JPG, never judge from code) → critique → fix → compare side by side.

## Scorecard (1–10 each, write numbers + one-line evidence)
1. **Silhouette & idea** — is the form iconic and recognisable as a black shape?
2. **Composition** — thirds/symmetry, depth planes (fore/mid/back), leading lines, breathing room.
3. **Light** — clear key direction, contrast ratio, time-of-day believable, shadows soft/hard appropriately.
4. **Materials** — roughness variation, edge highlights, no plastic, no pure white/black, scale of texture correct.
5. **Atmosphere & scale** — aerial perspective, human-scale reference, size reads as intended.
6. **Realism defects** — floating objects, intersecting geometry, tiling repetition, noise/fireflies, stretched UVs.
7. **Originality** — would an Awwwards/FWA juror have seen this exact thing before? Name the cliché if yes.
8. **Brand fit** — premium, calm, photography-first; the photos remain the stars.
9. **Usability (for UI)** — 3-second test: can you find work, booking, WhatsApp?
10. **Performance plausibility** — can this run on a phone with the bridging recipe?

Target: every score ≥ 7, average ≥ 8 before showing Shay as "final". Report honestly when it is not reached.

## How to critique
- Look at the full image, then crops (2×2 grid) for defects.
- Squint test (downscale to 25%) for hierarchy and silhouette.
- Compare with the previous round in one side-by-side image (PIL) so changes are visible.
- Write: top 3 weaknesses, each with a concrete fix (e.g. "sun 35° is flat → 8°, rotate 40° so the glass catches a rim").

## Labels
Every image shown to Shay is labelled: **Rendered (Blender/Cycles)**, **Interactive prototype (browser, real time)** or **Mock-up**. Never present a render as real time.
