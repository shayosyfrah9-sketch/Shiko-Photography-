# Critique: Concept A "SUNLINE", round 1
Independent art critic, 2026-11-24. Read-only review; this file is the only thing written. Images judged, not intentions.
Read first: STUDIO.md, GUARDRAILS.md, BRIEF.md, CONCEPTS.md §A, ui-A.md, camera-A.md, motion-vfx.md §A, performance-budgets.md §A.

## What was judged (labels as stated on the images)
| File | Label |
|---|---|
| round-1/A_r1_kf1_home-timeslice_RENDERED-composite.jpg | Rendered (Cycles), composite of 5 hour passes of one camera, "light per-hour grade", 1600×900 |
| round-1/A_r1_kf1_hour-passes_RENDERED.jpg | Rendered: the 5 un-composited passes (dawn, noon, golden, blue, night) |
| round-1/A_r1_kf2_golden-portraits_RENDERED.jpg | Rendered: 18:30, 85 mm, sun 3.6° behind stone pines, Poly Haven HDRI sky |
| round-1/A_r1_photo-view_shira-0443_MOCKUP.jpg | Mock-up (PIL UI over kf2 dimmed and blurred; real photo 2w2a0443) |
| A/ui-phone.png, ui-phone-rooms.png, ui-phone-viewer.png | Mock-up (HTML), world = **placeholder photo maya8612**, not the render |

**Method.** Full view of every image; crops of the Home frame (north end with city, stadium and canopies; the inland noon band), crops of kf2 (cliff and pines; far coast); 25% squint of both key frames.
**Verified:** what is in the pixels. **Assumed:** object sizes worked back from the stated 420 m camera height and 28 mm lens.
**Not delivered:** no surf, festival, sport or video key frame at eye height; no phone render of the world; nothing that shows motion (the scrub, the terminator wipe), so the core experience (moving time) cannot be judged at all in round 1.

---

## Scorecard (1–10)
| # | Criterion | Score | Evidence (one line) |
|---|---|---|---|
| 1 | Silhouette & idea | 5 | kf2's pine-topped cliff is a strong black shape, but it is the stock "umbrella pines on a sunset headland" image. Home has no shape at all at 25%: a blue curve and coloured fog. |
| 2 | Composition | 5 | Home: the shoreline is a good leading line from bottom-left, but the horizon sits at 11% from the top, the right half is empty mottled terrain, and every field is tiny. kf2: horizon at 57% (on no third), the cliff fills the left 38%, the right 60% is empty haze. |
| 3 | Light | 4 | The concept *is* light, and light is the weakest part. From 420 m no hour has visible shadows or rim light; dawn and golden passes are near-identical pink haze, and the caption admits a "per-hour grade". kf2 has a clear backlit key but no rim on trunks or cliff edge, and the sun's reflection is a hard-edged rectangle. |
| 4 | Materials | 3 | Terrain is a low-res texture with pale polygon patches; trees are lollipops with blue shadows; the cliff is smooth extruded clay with no strata; the sea in kf2 is mirror-flat glass on a surf coast. |
| 5 | Atmosphere & scale | 4 | Good haze on kf2's far coast. Home scale breaks: canopies (~15–20 px) are bigger than the trees (~10 px), so ~40–60 m tents; the city is a glowing particle blob; the stadium is a beige ring ~70 px wide. |
| 6 | Realism defects | 3 | Time-slice masks are huge diagonal gradients that cross the sea and sky as well as the land (an orange stripe across the open sea); a hard horizontal band across the sky at y ≈ 100; rectangular sun reflection; the cliff meets the water on a clean hard line with no beach, notch or wet band; polygon patches in the sand. |
| 7 | Originality | 5 | The time-slice as a map is a real idea. The image reads as a **Google Earth day/night terminator** over a map, and the travel is a **scroll-scrubbed video**, the trope the concept itself names. Nothing in round 1 lifts it above that. |
| 8 | Brand fit | 5 | The viewer is the best of all three concepts (calm, the photo untinted, ivory mount, real counts). The world is a colour takeover and does not look like Israel (no Tel Aviv skyline, no Bloomfield, no kurkar strata). |
| 9 | Usability (UI) | 6 | Phone: a labelled sun-arc (Hebrew field names + times), a big hour readout, a dock from the first frame, rooms grouped by hour: clear. But on the real Home render the five fields are 15–70 px targets from 420 m; the desktop viewer arc has times only; the vertical swipe is a scroll hijack. |
| 10 | Performance plausibility | 6 | Best first view of the three (0.2–0.3 MB). But a full day costs 11–17 MB on a phone, iOS scrub latency is unknown and binary, the concept's per-segment sizes are 0.4–0.75× the measured ones, and ~65 h of CPU rendering is needed for the footage. |
| | **Average** | **4.6** | Target is every score ≥ 7 and average ≥ 8. **Not reached.** |

---

## Shay's five criteria
### Originality: 5 / 10
- **Evidence.** "You travel through hours, not rooms" and "the map is a time-slice photograph" are both real photographic ideas. Video as the long exposure of the whole day (Sugimoto) is the best single idea in the three concept documents.
- **Weaknesses.** The Home render does not look like a time-slice photograph (crisp, deliberate slices of one scene, each at its own hour). It looks like a weather map or the Google Earth day/night line: soft colour washes over a satellite view. The travel model (scrub the footage with the wheel or swipe) is the **scroll-scrubbed video trope** of Awwwards sites (the Apple product-page pattern). Round 1 shows no element that would make a juror see it as anything else.

### Visual quality: 3 / 10
- **Evidence.** kf2's mood (pastel backlight, haze, far-coast lights reflected as vertical streaks) is calm and has some beauty at thumbnail size.
- **Weaknesses.** The Home frame is placeholder-grade: procedural terrain with polygon patches, lollipop trees, paper-triangle canopies, a particle-blob city, a ring stadium. kf2 has a clay cliff, three identical umbrella pines, a glass sea, a rectangular sun reflection and smooth soap-like foreground rocks. Neither frame would pass as a photograph, which is the whole premise.

### User experience: 6 / 10
- **Evidence.** The phone UI is the most legible of the three concepts: the arc names the fields in Hebrew with times, "18:42 · שעת זהב · פורטרטים ומיתוג" says where you are, the dock is visible at 0 s, the hint teaches the gesture once, and the rooms sheet fits on one screen. The desktop viewer is clear: counter, Gallery, booking and WhatsApp icons.
- **Weaknesses.** It is tested over a placeholder photo, not the Home render, where the five fields are tiny and the time-slice bands do not line up with tappable places. The vertical swipe is the time scrub, so a visitor who scrolls flies through the day (ui-A.md risk 1). Portraits (18:30) sit inside the festival span (11:00–19:40), so the clock order and the data order collide. **Data error:** the Shira viewer shows "Gallery ↗", but Shira has no full-gallery link (ui-A.md §0). The desktop arc shows times only, no field names. Photo width is 63% of the viewport, spec says 70%.

### Brand fit: 4 / 10
- **Evidence.** The photo is never tinted, sits on a neutral mount and is the brightest thing on screen in the viewer. The interface stays ivory on dark.
- **Weaknesses.** **Colour takeover: yes**, on two levels. Home swings the whole frame orange → white → navy, with the bands washing over sky and sea as well as land. kf2 is a single pink-beige monochrome. These are exactly the "colour takeovers" Shay says he dislikes, and the caption's "per-hour grade" contradicts the concept's own rule ("no grading on top"). **Game-like: yes**: an aerial map with coloured pin-like tents, a glowing city and lollipop trees reads as Cities: Skylines or Civilization. **Template-like:** an aerial "story map" with a time scrubber is a known scrollytelling template. None of his real places is recognisable.

### Performance: 6 / 10
- **Evidence.** Interactive on one still: 0.20–0.30 MB phone, ~1 s TTI on 4G, ≤ 10 draw calls, no GPU dependency.
- **Weaknesses.** All of the experience after Home is video: 2.0–2.7 MB per field on a phone, 11–17 MB for the whole day, close to the live site's 21 MB. iOS seeking with short-GOP 720×1280 video is unmeasured and either works or does not. The concept's claimed segment sizes are 0.4–0.75× the measured figures. CPU-only Cycles footage is ~65 h before any revision round, and every lighting fix means re-rendering footage, not one still.

---

## Explicit flags
| Flag | Verdict | Where |
|---|---|---|
| Game-like | **Yes** | Home: aerial map, pin-like coloured triangles, particle-blob city, lollipop trees (city-builder look) |
| Toy-like | **Yes** | kf2: clay mesa with three identical umbrella pines (diorama/bonsai); Home tents bigger than trees |
| Template-like | **Partly** | Aerial story-map + scrubber; the viewer and rooms sheet are fine but generic |
| Scroll-scrubbed video trope | **Yes, not yet lifted** | The navigation model; round 1 shows nothing (no wipe, no clip) that answers it |
| Colour takeover | **Yes** | Home bands wash the whole frame; kf2 monochrome pink; "per-hour grade" |
| Tilt-shift | No | — |

---

## Top 3 weaknesses and fixes for round 2
### 1. The Home time-slice must read as a photograph made of slices, not a colour wash over a map
- **Masks:** slices follow the **coast**, with seams roughly perpendicular to the shoreline, feather **≤ 40 px** (now ~300–400 px). Slices apply to land and sea only; the sky is one continuous gradient (or slices with the same seams), never a diagonal stripe across open water.
- **Camera:** come down from 420 m to **150–180 m**, 35 mm, pitch **−12°**, horizon at **30–33% from the top** (now 11%). Target sizes at 1600 px: canopies ≥ 60 px, stadium ≥ 220 px wide, the surf break ≥ 4 visible white-water rows.
- **Light, not grade:** delete the per-hour grade. Each hour is sun position + sky only. Dawn and golden must differ by **shadow direction (≈ 180°)** and shadow length ≥ 8× object height; noon shadows ≤ 1× height. Check: the five passes side by side should be tellable apart in greyscale.

### 2. Replace the toy assets in both key frames
- **Terrain:** real dune and sand material (ripple normal 2–5 cm, Poly Haven), no polygon patches; scrub and pine clumps from 3D models at three sizes with random rotation and scale 0.7–1.3.
- **Places:** stretch-tent geometry (20 × 30 m) for the festival; a Bloomfield-like stadium (two tiers, roof, green pitch); a city made of 40–80 tower blocks 30–180 m tall with lit windows, not a particle blob.
- **kf2:** kurkar cliff with horizontal strata, an erosion notch at the waterline, scree and a **0.3–0.5 m wet dark band**; a sand beach in front; 3 stone pines with different crowns and a warm rim on trunks; sea with small swell (0.2–0.5 m) so the sun reflection becomes a **vertical glitter path 60–120 px wide**, not a rectangle; foreground sand ripples with backlit rim highlights.

### 3. Kill the colour takeover and give every hour a subject
- Keep a constant neutral anchor: sand and the ivory UI. Sky saturation ≤ 0.45, adjacent slices differ by ≤ 30° of hue. kf2 must not be one monochrome: add the cool blue of the sea shadow side against the warm sun (2 hues, not 1).
- kf2 is "18:30 Portraits" but has no portrait cue: put a set or a silhouetted figure on the right third at 6–10 m, and move the horizon to a third (y ≈ 300 or 600, not 515).
- Render eye-height frames for surf (06:10), one festival (14:00) and the stadium (20:15), plus one still of the terminator wipe mid-transition, so the travel can be judged.
- UI: field names on the desktop arc; Shira's viewer must show "all 42 in a grid", not "Gallery ↗"; photo at 70% width; place the phone mock-up over the real vertical render.

---

## Verdict: **NOT YET**
The interface layer is the strongest of the three concepts, and the idea (hours instead of rooms, video as the day's long exposure) is good. The images undercut it: the Home reads as a game map with a colour wash, kf2 as a clay diorama at sunset, and the light, which is the whole concept, is a grade rather than sunlight doing something. Do not show these renders to Shay as visual quality. The phone UI mock-ups and the desktop viewer may be shown as UI direction only, labelled Mock-up.
