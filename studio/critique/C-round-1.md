# Critique: Concept C "WHERE HE STOOD", round 1
Independent art critic, 2026-11-24. Read-only review; this file is the only thing written to the repo (crops for inspection were made in the scratchpad only).
Scorecard: `.claude/skills/shiko-visual-critique` (10 points) + Shay's five criteria (BRIEF.md). Images judged, not intentions.

## What was judged (labels as stated on the images)
| File | Label | Notes |
|---|---|---|
| round-1/C_r1_keyframe1_overview_RENDERED.png | **Rendered** (Cycles CPU, 1600×900, 28 spp + OIDN, AgX Punchy, 12m49s) | Key frame 1, Home overview |
| round-1/C_r1_keyframe2_surf_vantage_RENDERED.png | **Rendered** (200 mm f/4, 40 spp + OIDN, 12m12s) | Key frame 2, surf vantage before the click |
| round-1/C_r1_photo_click_and_viewer_MOCKUP.jpg | **Mock-up** (key frame 2 + real photo surf0001.jpg composited in PIL; viewer UI drawn in PIL) | The click + viewer |
| C/ui-phone.png, ui-phone-rooms.png, ui-phone-viewer.png | **Mock-up** (HTML, 390×844 @2x). World = **placeholder photo sol0177** (lit floating stones), not the render | Phone UI |
| round-1/render_settings.txt, keyframe2_register.json, LICENSES.txt | text | Read for context only |

**Method.** Full view of every image; 2×2 quadrant crops of key frame 1 at 2× (grove/floodlights, sun/wave, canopy/flat); a 3× crop of the ticker-tape cloud; a 3× crop of the "surfer-shaped absence" and of the bottom strip of key frame 2; a 25% squint of key frame 1. No previous round of C exists, so no side-by-side.
**Verified:** everything said about what is visible in the pixels; file labels; render settings as printed on the frames. **Assumed:** pixel-per-metre estimates (my arithmetic from the stated lens/distances); performance figures are the team's own estimates in performance-budgets.md, nothing was measured on a device.

**Not delivered in round 1:** footprints (the concept's core navigation mark: **not visible anywhere** in key frame 1), the basketball hall doorway and the orange ball, the held football (not visible in the ticker cloud), festival confetti (not legible), the Video vantage, the booking "your moment" vantage, the back of the print, and any phone-portrait frame of the actual world. The phone UI is judged over an unrelated placeholder photo.

---

## Scorecard (1–10)
| # | Criterion | Score | Evidence (one line) |
|---|---|---|---|
| 1 | Silhouette & idea | 4 | At 25% the right half reads as a **crashed aircraft wing / open book** lying on the flat, not a wave; the four "held moments" read as sail + two lamp posts + tree island, none as an *instant*. |
| 2 | Composition | 5 | Thirds are planned (canopy left, wave right, sun upper-right third) but the centre is dead haze, the bottom ~40% is an empty dark mirror with vector-edged sand patches, and the ticker cloud (~250 px wide) is the smallest moment while being the farthest. KF2: slab in the bottom third, a soft blob floating in flat pink, nothing in crisp focus. |
| 3 | Light | 5 | Sun position and warm haze are believable and the mist glows. But the matter is **not rim-lit**: in KF2 the spray flecks are *darker* than the sky behind (grey ash on pink), the wave face is flat grey-blue with no light transmitted through the lip, and the bright plume under the sun reads as rocket exhaust / geyser. The concept's own rule ("every drop a rim-lit gold bead") is not met. |
| 4 | Materials | 3 | Wave = glossy grey plastic slab; wet sand shows no texture at overview scale, only flat colour with clean vector-like dry-patch edges; "turf" is a grey rectangle; floodlight heads are stick glyphs; ticker-tape and spray are noise, not paper or water. Only the CC0 pines and the canopy weave are convincing. |
| 5 | Atmosphere & scale | 5 | Aerial perspective is the best thing in frame 1 (haze separates planes). Scale is unreadable: no human-scale object, the wave length cannot be judged (it could be 5 m or 500 m), the canopy and poles have no reference. |
| 6 | Realism defects | 3 | Floodlight head clusters **float above and left of the pole caps**, disconnected; KF2 bottom strip has hard rectangular slab steps (step at x≈335, y≈800); the wave has no breaking lip at all; the "surfer absence" is two soft-edged lobes with a halo (reads as an alpha cut-out / a peanut, not a board path); the linen sheet is a stray white shard at the grove edge (~x150, y370); no ball visible. |
| 7 | Originality | 6 | The idea (the people are missing; his photo puts them back) is genuinely new for a photographer site. The pixels do not carry it: what we see is a **surreal desert-sculpture vista** in the Dalí / *Journey* register the concept itself listed as a risk; the ticker cloud is a **generic particle field**. |
| 8 | Brand fit | 4 | Apricot takeover over everything: no Maccabi yellow, no festival saffron/magenta/teal, no turquoise sea. The mock-up proves the clash: his surf photo is a **blue midday sky**, pasted into a 2.5° sunset world. Empty and eerie, the opposite of parties and crowds. The viewer itself (ivory mount, true ratio, uncropped) is right. |
| 9 | Usability (UI) | 5 | Dock (עבודות / הזמנת צילום / WhatsApp) visible at 0 s, and the all-rooms sheet is clean and complete (18 rooms, counts, order). But Home shows **no photograph**, footprints are invisible in the render, the phone fix is six boxed labels zig-zagged over the scene, and the UI was tested over a placeholder, not the world. "swipe up · the back of the print" in the viewer mock contradicts camera-C.md (swipe up dropped for the iOS home gesture). |
| 10 | Performance plausibility | 4 | The heaviest of the three: phone T1 first view ~2.1 MB (fails the 1 MB skill budget), TTI ~3.0–3.8 s on 4G, soft-sprite fill rate at 200 mm unmeasured, two code paths (T1 + T0 backplates). The round-1 look depends on volumetric haze and 60k mist flecks (NMISTF=60000), none of which has a real-time equivalent shown. No prototype. |
| | **Average** | **4.4** | Target is every score ≥ 7 and average ≥ 8. **Not reached.** Lowest of the C criteria: materials and realism defects (3). |

---

## Shay's five criteria

### Originality: 6 / 10
- **Evidence for:** the concept is the most original of anything this studio has proposed: a photograph as the *missing piece* of a world, and navigation as "find the vantage". Nobody on Awwwards does a portfolio where absence is the interface.
- **Evidence against:** the images look like a generic "surreal golden-hour dreamscape": mirror flat, lone sail, tree island, sun haze. Ticker cloud = WebGL particle field. Frozen spray with a hole = stock "frozen time" VFX.
- **Weakness:** originality lives in the text, not the render. A juror shown frame 1 without the caption would not guess "time stopped" or "people missing".

### Visual quality: 4 / 10
- **Evidence for:** atmosphere, haze gradient and the pine reflections in frame 1 are pleasant; the sun disc is soft and believable; OIDN output is clean (no fireflies).
- **Evidence against:** the hero object (the wave) is not a wave; the matter is dust, not drops or paper; material work is placeholder-grade (grey slab, grey turf rectangle, floating lamp glyphs, rectangular slab steps in KF2); KF2 has nothing sharp in it.
- **Weakness:** nothing in either render reaches "photograph-grade", which is the minimum for a photographer whose work will sit next to it.

### User experience: 5 / 10
- **Evidence for:** HTML dock at 0 s; rooms sheet groups 18 rooms by held moment, with counts, in correct order; viewer has big 44 px arrows, 01 / 07, honest "כל 7 ברשת" note instead of a dead link; camera plan is choose-and-glide with sane comfort limits.
- **Evidence against:** the first 3 seconds contain no photograph; footprints (the navigation) are not visible at 1600 px, let alone 390 px; the phone fix (six dark boxes with footprint glyphs, zig-zag down the screen) is a **level-select map**; one finger does three things (orbit / next photo / flip).
- **Weakness:** the UI is designed against a placeholder background, so its contrast and clutter over the real (very bright, apricot) render are unproven.

### Brand fit: 4 / 10
- **Evidence for:** photos are shown front-parallel, uncropped, on the ivory mount; the world is dimmed in the viewer; no tint on the photo.
- **Evidence against:** colour takeover (the whole world is one apricot hue, which Shay said he dislikes); the photo-to-world clash in the click mock-up (blue noon photo in an orange dusk); no sign of his real colours; a cold, peopleless world for a festival/sport brand.
- **Weakness:** the concept's art direction (2.5° sun, everything backlit) is incompatible with most of his actual photos, which are daylight. The "spray continues the 3D spray" promise **fails visibly** in the mock: the 3D spray stops at the photo edge, the photo covers the absence entirely (photo rect ≈ x140–990 vs absence ≈ x540–730), and the colours do not meet.

### Performance: 4 / 10
- **Evidence for:** the team is honest: T0 backplate path (~0.4 MB first view), poster-first, DOM dock independent of WebGL, static merged matter instead of 80k impostors (motion-vfx C.4).
- **Evidence against:** real-time T1 fails the 1 MB phone budget (~2.1 MB); TTI 3–3.8 s; two products to build and keep visually identical; fill-rate risk unmeasured; the round-1 look relies on volumetrics that the real-time path will not have, so the prototype will look worse than these renders, not better.
- **Weakness:** on most phones the user will actually get T0 (pre-rendered plates + clips), i.e. a slideshow that is functionally Concept A with more bytes.

---

## Explicit flags
- **Game-like: YES.** (1) Phone home: six boxed labels with footprint icons scattered over the scene = a level-select / waypoint HUD. (2) Pine grove on a round sand island, a grey turf tile between two lamp posts, a sail on a disc: discrete "stations" on a flat plane read as a strategy-game map / diorama. (3) The floating dark glyph clusters on the floodlights look like little stick figures, a game-asset artefact.
- **Template-like: partly.** The viewer is a standard lightbox (acceptable, shared on purpose). The click mock's corner brackets are the stock "viewfinder frame" motif.
- **Bullet-time cliché: not in the images.** Good: no 360° orbit, no frozen person. The frozen-spray-with-hole in KF2 is adjacent to the stock "frozen time" VFX look and must stay physical to avoid it.
- **Generic particle field: YES.** The ticker-tape cloud between the floodlights is a fuzzy yellow noise blob; no strip of paper is readable at 3× crop. The KF2 spray is ash-grey flecks, not water. This is exactly the risk the concept named ("must read as physical, never as particles").

---

## Top 3 weaknesses and round-2 fixes

### 1. The held matter reads as dust/particles, not water and paper, and is not backlit
- **Problem:** KF2 flecks are darker than the sky; ticker tape is noise; nothing glitters. The concept's whole visual claim is lost.
- **Fixes (numbers):**
  - Replace the 60k mist flecks (`NMISTF=60000`) in KF2 with **3,000–5,000 discrete drops**, radius 2–8 mm, glass/water BSDF IOR 1.33, roughness 0, plus ~300 elongated droplets (aspect 1:3) aligned to the spray direction.
  - Drop sky/background exposure behind the spray by **1.5 stops** (`EXPO -0.6 → -2.1`, compensate the foreground with a 0.8 m-wide bounce card or +1 stop on the sand only) so each drop's rim is **brighter** than the sky behind it. Put the sun **0.5–1.5° behind the spray centre** in frame (now ≈ 3.9° to the right at 200 mm), so the drops form a lit halo.
  - Ticker tape: at 150 m on 35 mm one pixel is ≈ 9.6 cm, so real 10 cm strips are invisible. Move the sport moment to **≤ 70 m**, use **1,500–2,500 strips 3 × 25 cm**, Maccabi yellow (≈ #FFD200), translucency 0.3, each strip bent 10–30°, and make the two floodlight beams real volumetric cones crossing **inside** the cloud. Model the lamp heads onto the poles (no gap) and give the turf a green, 5 cm grass shader.
  - Add **one foreground held element 8–15 m from camera** in the overview (drops or confetti, out of focus, 10–20% of the frame) to sell both scale and "time stopped".

### 2. The wave is not a wave, and the surfer absence is not a surfer
- **Problem:** the hero reads as a crashed wing / grey pillow; there is no sea; the absence is two soft lobes.
- **Fixes (numbers):**
  - Rebuild as a real breaking lip: face **2.5–3 m**, lip thrown forward **1.2–1.5 m**, a hollow below it, white water at the base; extend **open sea to the horizon** behind it (now there is only haze).
  - Water shader: transmission 0.9–1.0, volume absorption teal (≈ #1f7f80, density ~0.4/m) so the backlit lip **glows green-teal** where it is thin (< 0.3 m).
  - Absence: a **sharp-edged cut** following the board path (≈ 1.9 × 0.5 m board slot + carved arc ~4 m long) with drops displaced outward along its rim, no soft halo; it must match the spray fan in surf0001 within ≤ 2 px at 1080p, or it is not "registration".
  - Remove the rectangular slab steps in KF2's bottom strip (x≈335, y≈800); the foreground should be wet sand with a 0.5–1 cm ripple normal, not boxes.

### 3. World palette vs. his photographs, and no photo on Home
- **Problem:** a 2.5° apricot sunset hosts blue-sky daylight photos; the click mock shows the clash and the spray does not continue into the photo; Home shows none of his work.
- **Fixes (numbers):**
  - Raise the sun to **8–12°** and halve sky saturation (`SKYSAT 2.0 → 1.0`) so the sky reads pale gold-to-blue, not a one-hue takeover; keep the top of the sky ≥ 30% bluer than the horizon.
  - Per-vantage registration rule: the cover photo occupies **40–55% of frame width**, and **20–40 held 3D drops sit in front of the photo edge** (overlap 20–60 px), colour-matched to the photo's highlights, so the spray visibly continues. Choose covers whose light direction is within ±30° of the vantage's sun azimuth; if none exists for a field, that field does not get the click.
  - Put **one real photograph on Home**: e.g. the last-registered cover held as a small print standing on the flat (≈ 6–8% of frame), or the footprints of the nearest vantage with its cover already visible. And show footprints at all: 28 cm prints, 2–3 cm deep, raking specular, at ≥ 12 px tall in the overview; render a phone-portrait (720×1560) overview with the real UI over the real render, labels reduced from six boxes to four field icons in the dock + one first-visit caption.

## Other issues to fix (lower priority)
- Floodlight heads floating off the pole tops (frame 1).
- The bright plume under the sun reads as exhaust / geyser: cut its intensity by ~60% or break it into the wave's spray.
- Linen sheet at the grove is a 20 px white shard: make it 2.5 × 1.8 m, lifted at 30–40°, backlit so it glows.
- Viewer mock says "swipe up" (contradicts camera-C.md §4 ↻ icon); dock icons (house / wave / chat / window) in the PIL mock vs text dock in the HTML mock: pick one.
- Bottom 40% of frame 1 is empty: lower the horizon to ~30% from the top or tilt pitch −12° → −8°.

## Verdict: **NOT YET**
The concept is the most original of the three on paper, but round 1 shows none of its three promises (time stopped, people missing, photo completes the moment) in a way a visitor would read without the text. Average 4.4 / 10, with materials and realism defects at 3. It is also the heaviest and riskiest on phones. Do not show to Shay as a finished concept; round 2 must fix weaknesses 1 and 2 before the click (weakness 3) can even be judged.
