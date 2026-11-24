# Critique: Concept B "DEPTH OF FIELD", round 1
Independent art critic, 2026-11-24. Read-only review; this file is the only thing written.
Scorecard: `.claude/skills/shiko-visual-critique` (10 points) + Shay's five criteria (BRIEF.md).

## What was judged (labels as stated on the images)
| File | Label | Notes |
|---|---|---|
| round-1/B_r1_01_hyperfocal_home_RENDERED(_clean).png | Rendered (Cycles CPU, 35 mm f/16, focus 3.0 m, 1600×900, 64 spp + OIDN) | Key frame 1 |
| round-1/B_r1_02_focus_festival_RENDERED(_clean).png | Rendered (35 mm **f/0.9**, focus 14.3 m) | Key frame 2 |
| round-1/B_r1_00_focus_pull_pair_RENDERED.png | Rendered, side-by-side of 01 and 02 | |
| round-1/B_r1_03_backplate_focus0.3m_RENDERED_clean.png | Rendered, 640×360 | Viewer backplate |
| round-1/B_r1_03_photo_view_MOCKUP.png | Mock-up (backplate upscaled + 8 px blur, real photo 2w2a1130) | Desktop viewer |
| B/ui-phone.png, ui-phone-rooms.png, ui-phone-viewer.png | Mock-up (HTML), world = **placeholder photo goa0413**, not the render | Phone UI |

**Method.** Full view of every image, 2×2-style crops of the home frame (festival/people block, portrait set block), a stadium crop of frame 01 stacked over frame 02 to see what the focus pull actually changes, and a 25% squint. No previous round of B exists, so no round-to-round comparison.
**Verified:** everything said below about what is visible in the pixels. **Assumed:** the pixel-size estimates (people height, blur disc size) are my arithmetic from the stated lens data, not measurements in Blender.

**Not delivered in round 1:** the sport (120 m), surf (∞), portrait (1.5 m) and video focus states; the vertical phone composition; any frame of the 6-layer shader approach. So the concept's central claim, that the five fields can be told apart by focus alone, is not shown. Only 2 of 5 focus states exist.

---

## Scorecard (1–10)
| # | Criterion | Score | Evidence (one line) |
|---|---|---|---|
| 1 | Silhouette & idea | 5 | The idea is strong, but at 25% the black shape is "round stadium + tent peaks + side table": it reads as a theme-park plan, not a single iconic photograph. |
| 2 | Composition | 5 | Pine trunk (~110 px) and glowing curtain (~300 px) eat ~25% of the width; the stadium sits dead centre; the brightest large area is the curtain at the right edge, which pulls the eye away from all four fields. |
| 3 | Light | 4 | Sun is meant to be 2° below the horizon, yet the side table throws a hard, dark shadow toward camera. Four floodlights light nothing (no pool on the pitch, no spill on the masts). The sky is flat lavender-pink: no indigo top, no apricot band. No key direction. |
| 4 | Materials | 4 | The magenta canopy is an untextured, glossy, airbag-like vinyl blob; the patterned canopies show a stretched procedural cell pattern; the stadium is matte grey plastic with an emissive LED ring; town = white clay boxes; people = pink untextured mannequins. Ground rock and the wood table are the only convincing materials. |
| 5 | Atmosphere & scale | 4 | Haze does separate the town from the meadow (good), but scale contradicts itself: the figures by the left canopy are ~40 px tall; a 1.7 m person at ~20 m on 35 mm / 1600 px should be ~130 px. Either the canopies are giant or the people are toys. Result: diorama. |
| 6 | Realism defects | 4 | Sphere "trees" and box houses behind the meadow; light bulb hanging out of the sky on a wire from the frame edge; curtain hem rolls onto the ground in a wavy, clipping edge (bottom right); the 0.3 m backplate has blotchy OIDN mottling across the stadium band at 640×360. |
| 7 | Originality | 6 | The concept (focus = navigation, each field at its shooting distance) is genuinely new for a photographer site. The images do not carry it: what we see is a stadium + festival tents + beach, i.e. a "photographer's world" map. |
| 8 | Brand fit | 5 | Photos are the stars in the viewer (good: true ratio, ivory mount, nothing tinted). The world itself is candy pink/magenta pastel: the "colour takeover" Shay dislikes, and nothing like his real colour (Maccabi yellow, turquoise surf, warm skin). |
| 9 | Usability (UI) | 6 | Dock with עבודות / הזמנת צילום / WhatsApp is visible at 0 s and passes the 3-second test. But the focus labels are tested over a placeholder photo, not the world, so the core gesture is unproven; the labels with check-box squares read as game waypoints. |
| 10 | Performance plausibility | 8 | Fixed camera, 6 layers, ~12 draw calls, ~1 MB phone: the most plausible of the three on paper. Not measured on a device; the round-1 frames were made with in-camera DOF, not the layered shader, so the cheap path is not yet shown to look like this. |
| | **Average** | **5.1** | Target is every score ≥ 7 and average ≥ 8. **Not reached.** |

---

## Shay's five criteria
### Originality: 6 / 10
- **Evidence.** The mechanism is original: a site navigated by a focus ring, Home = hyperfocal, video = past ∞, the world becomes the bokeh of the photo. I have not seen this as an Awwwards/FWA site. The pair image (00) makes the idea legible in one glance: the same view, a different subject sharp.
- **Weaknesses.** The *content* of the view is the cliché: a round stadium with four masts, a row of festival tents with string lights, and the sea, all crammed into one vista, is a "photographer's theme park" map: each field as a literal icon-building. That is the same idea as the live site's cabins, with blur. The tents and stadium look like a city-builder game set, not a place on the Israeli coast (no kurkar cliff visible, no palms, no Tel Aviv skyline, no Bloomfield).
- **Tilt-shift: yes.** Frame 02 is the textbook tilt-shift miniature: high vantage, a horizontal sharp band through the middle, blur top (pine) and bottom (ground), saturated toy colours, tiny figures. A viewer will read "fake miniature photo" before "festival". This is the most dangerous cliché in the set, because tilt-shift is exactly the photographic effect the concept is built on.

### Visual quality: 4 / 10
- **Evidence.** Clean render, low noise at 1600×900, believable rock ground and haze layering between town and sea. The desktop viewer mock-up is the best image of the round: the photo, mount and counter are calm and premium.
- **Weaknesses.** Placeholder-grade assets in the hero frame: sphere trees, box houses, mannequin people, untextured magenta canopy, LED-ring "UFO" stadium and a grey dome for the basketball hall. Light is physically wrong for the stated time (hard shadow at sun −2°; floodlights that light nothing). The sea is a flat lavender plane with no glint and **no visible surf line**, so the surfing field has nothing to focus on. The viewer backplate is only 640×360 with three bokeh discs and mottled denoiser artefacts; "the world becomes the bokeh of the photo" currently looks like a muddy brown blur, and the palette tint toward the photo is not shown.

### User experience: 5 / 10
- **Evidence.** The phone dock (WhatsApp, gold booking, works) is visible from the first frame; the rooms sheet groups all 18 rooms by distance with photo counts; the phone viewer has large ←/→ buttons, 01/11, full-gallery link and a visible ✕. Keyboard and screen-reader plan in ui-B.md is thorough.
- **Weaknesses.** The signature interaction is unproven: the phone home mock shows labels ("∞ גלישה", "120 m ספורט") floating over a festival gate, so the label/plane mapping is meaningless in the picture. On the render itself, focusing on festivals does not visibly change the stadium or the sea (crop of 01 vs 02: the stadium is near-identical), so "sport vs surf" cannot be told apart, which is the camera plan's own art-critic gate (risk 2). One fixed view for 18 rooms risks "where is the world?" after the second room. Phone viewer photo is 74% of width, spec says 88%.
- **Game-like:** the checkbox-style labels pinned in the scene are quest markers. The rooms sheet chip grid is a generic template, acceptable as a fallback only.

### Brand fit: 5 / 10
- **Evidence.** Photography-first in the viewer; ivory mount; restrained header icons; nothing tints the photo. Dock in Hebrew RTL, Rubik-like round type.
- **Weaknesses.** The world fails Shay's own rules: "real, not game-like" (the town, figures and stadium are game assets); "no colour takeovers" (magenta/pink dominates ~20% of the frame); "each room's environment matches its photos" (his festival photos are daylight dust, water spray and fabric, not neon tents at dusk). Mixed language on the rooms sheet ("שואוריל soon"). Booking on desktop is an unlabelled calendar icon.

### Performance: 7 / 10
- **Evidence.** Fixed camera, < 5 k triangles, 10–14 draw calls, ~0.85–1.0 MB phone first view, ~120 MB GPU, no cost growth per field (performance-budgets.md §B). Lowest risk of the three on paper.
- **Weaknesses.** Every figure is estimated [A], nothing measured on a phone. The phone first view sits on the 1 MB line. The round-1 look comes from in-camera DOF; the gain-3 shader composite that must produce visible far-field separation is untested and may expose cut-out edges (the concept's own "cardboard" risk). The phone needs its own vertical render set, which does not exist yet.

---

## Top 3 weaknesses and fixes for round 2
### 1. It reads as a tilt-shift miniature / city-builder diorama
- **Scale:** people near the canopies must be ~120–140 px tall at 1600 px width (35 mm, ~20 m), not ~40 px. Or shrink the canopies to a real 6–10 m span. Put 30–60 people in the meadow with real clothing shaders and motion poses, not pink mannequins.
- **Delete the box town and sphere trees.** Replace with kurkar cliff edge + 6–10 real palm/pine silhouettes from Poly Haven, or haze the zone out completely (volume density up until values behind the meadow sit within ±0.05 of the sky).
- **Stadium:** asymmetric stands with a real roof truss (Bloomfield-like), LED ring emission down to ≤ 25% of now, and four floodlights that actually light the pitch and cast a visible cone in the haze (light 5600 K, spot 30–40°).
- **Colour:** canopy saturation −30%, magenta canopy → woven fabric with 3–5% sag and back-lit translucency (string lights glowing *through* the cloth), so no single hue covers more than ~8% of the frame.
- **Break the tilt-shift band:** keep something sharp and readable at the bottom edge in the festival state (e.g. grass and rocks at 10–14 m filling the lower third via a lower pitch −3° instead of −6°), so the frame is "near blur + sharp plane + far blur", not "blur / sharp stripe / blur".

### 2. Focus does not separate the far fields, and two fields have no subject
- Render **all five** states (1.5 m, 12 m, 120 m, ∞, past ∞) plus hyperfocal, with the spec'd **50 mm f/1.4**, not 35 mm f/0.9 (a look no real lens gives).
- Use the layered composite with the camera plan's gain 3 behind and −0.3 EV on unfocused planes. Measure at 1600 px width: festival-focus → stadium disc ≥ 24 px, sea glints ≥ 32 px; sport-focus → canopies ≥ 30 px and sea ≥ 12 px; surf-focus → stadium ≥ 16 px. Downscale 120 m and ∞ frames to 390 px wide side by side: they must be tellable apart in 1 s.
- **Surfing needs a subject at ∞:** a visible break with 3–4 rows of white water (foam rows ≥ 3 px tall at 1600 px), 2–3 surfer silhouettes, and a sun glint path. **Portraits need a real set:** linen backdrop 2.0 × 2.4 m on two visible stands.

### 3. Light and framing are wrong for the stated minute
- Sun −2°: **no hard shadows.** Remove the direct sun or make the key a large sky/soft light so shadow penumbra under the table is > 20 cm; if you want a hard shadow, the source must be a visible practical (the bulb) and cast from it.
- Sky gradient as specified: indigo #1d2433 at the top third → apricot #e9a25a in a band 2–4% of frame height at the horizon; the sea reflects that band.
- Curtain: −1.5 EV and pull it into the scene so it covers ≤ 10% of width (it is ~19% now and the brightest surface). Pine trunk ≤ 4% of width. Move the stadium to the left third (centre x ≈ 530 px, not 540–860 straddling centre). Remove the floating bulb or hang it from a visible string line between two poles.
- Viewer backplate: render at ≥ 1600×900 (not 640×360) with 12–20 bokeh discs of mixed size (string lights 2700 K, floodlights 5600 K), then show the 10–15% palette tint toward the photo, side by side with the untinted plate.

Also for round 2: a vertical phone render (900×1950) with the real focus labels placed on the real planes, and labels redesigned without checkbox squares (a thin ivory tick + text, 44 px tall).

---

## Verdict: **NOT YET**
The idea is the most original mechanism of the round and the cheapest to run. The images do not yet sell it: the hero frames look like a tilt-shift photo of a toy city, with game-asset filler, and the focus pull that is supposed to *be* the navigation barely changes the far half of the frame. Do not show these frames to Shay as the concept's visual quality. The desktop viewer mock-up can be shown as UI direction only, labelled Mock-up.
