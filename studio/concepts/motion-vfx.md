# SHIKO WORLD 2.0: motion & VFX for the three concepts
Motion & VFX designer, 2026-11-24, branch `world2-dev`. Concept phase, text only. Nothing here is built or rendered, so no image labels apply yet. When any of this is shown, it will be labelled **Rendered** (Cycles backplates and clips), **Interactive prototype** (live shader or sprites in the browser) or **Mock-up**.

Sources: `studio/concepts/CONCEPTS.md` (A SUNLINE, B DEPTH OF FIELD, C WHERE HE STOOD), `BRIEF.md`, `research/world2-research.md`, `DESIGN_LANGUAGE.md` (motion line), skills `shiko-cinematic-motion`, `shiko-realtime-webgl`, `shiko-asset-performance`.

---

## 0. Rules that apply to all three

**Test for every effect.** An effect stays only if it passes all three questions:
1. Does it exist in his photographs or at his shoots (backlit dust, spray, haze, floodlights, surf)?
2. Does it help orientation, depth or the concept's metaphor (light, focus, vantage)?
3. Would a visitor miss it if it were gone, without having noticed it while it was there?

If any answer is no, the effect is cut. Section "Rejected" in each concept lists what failed.

**Amplitude and rhythm**
- At most **3 ambient layers move at the same time** in any view.
- Displacement amplitude is at most 3 px at 1080p (2 px on phone). Camera idle drift is at most ±0.15°.
- Ambient periods are 5–11 s and use non-integer ratios (for example 6.3 s and 8.9 s), so no loop is visible.
- Motion never runs at a constant linear speed toward a stop. All authored moves are cubic in-out, 0.9–1.6 s (DESIGN_LANGUAGE).

**The photo-stillness rule (enforceable, not a guideline)**
- When a photo is opened, every ambient uniform eases to zero over 400 ms. Then the canvas **stops rendering** (render-on-demand; the RAF loop is cancelled) and shows its last frame dimmed and blurred behind the mount.
- Stopping the loop makes "nothing moves near a viewed photo" true by construction. It also saves battery and is the skill rule "pause rendering when a full-screen photo covers the canvas".
- Gyro parallax, cursor light and look-around are disabled while a photo is open. Swiping between photos moves only the HTML print; the world does not react.
- After the photo closes, ambient motion returns over 600 ms, never instantly.

**Particle accounting**
- The caps (2,000 desktop / 600 phone) count every sprite or instance that is **updated or animated per frame**, summed over the whole view.
- Matter that never moves (held spray in C) is not a particle. It is static merged geometry and counts against the triangle and draw-call budgets instead. This distinction matters in Concept C (see C.4).
- Particles are additive only for light (dust in beams, bokeh of lamps). There are no confetti or sparkle particle systems.

**Reduced motion (`prefers-reduced-motion: reduce`)**
- No camera travel, drift, parallax, gyro, flow maps or particles. The world is a still image.
- Every transition becomes an opacity cross-fade of 300–400 ms.
- Video never autoplays: a poster with a play icon.
- The same rule is offered as an in-site toggle (in the settings or mute area) for visitors who do not set it at OS level.

**Runtime governor** (from `shiko-realtime-webgl`). When fps stays below 45 for 2 s, effects drop in this order: particles halve → flow-map shaders off → idle drift off → resolution. The world must still look finished at the last step. Everything that follows is designed to degrade to a still frame without looking broken.

**One clock.** All ambient motion reads one `uTime` that stops when the tab is hidden, when a photo is open and during reduced motion.

---

## A. SUNLINE: one day of light

### A.1 Ambient motion (what, how, why)
At rest, the world sits at a room's minute: a paused frame of the scrubbed Cycles footage plus the low-poly proxy. A paused video looks dead, so the rest state must breathe without time advancing. **Rule for A: at rest, time stands still, but air and water move.** The sun never moves unless the visitor moves it.

| What moves | Where / when | How | Why it earns its place | Amplitude |
|---|---|---|---|---|
| Sea surface shimmer | every hour with visible water | Flow-map shader on the paused backplate. A baked water mask and flow texture (from Blender) push UVs; no extra video. | Water that does not move tells you it is a picture. His surf work begins here. | ≤ 2 px, period ~7 s |
| Sun glint on the water | surf 06:10, golden 18:30 | Live specular on the proxy water plane, driven by the exported sun direction and the ±1.5° look-around (already in the concept). | The glint is the only view-dependent light in a pre-rendered world. It proves the world is not a video. | follows the camera only |
| Sea haze drift | every hour; thicker toward evening | Two large soft noise cards between proxy depth bands, scrolled at different speeds (0.2 and 0.35% of the width per second). | Haze carries the time of day and separates the layers of the coast. | opacity ±4% |
| Dust motes in backlight | 18:30 portraits only | Additive sprites in the sunbeam volume through the pines, slow Brownian drift. Desktop **400**, phone **120**. | Backlit dust is his own signature (Shira, Maya). Only at golden hour, so it marks the hour instead of decorating every place. | 0.5–2 px sprites, ≤ 3 cm/s scene speed |
| Canopy flutter | festival hours 11:00–19:40 | A small masked cinemagraph loop of the canopy region (2 s, H.264, ≤ 150 KB), composited over the paused backplate. It decodes only while the main segment is paused, so one decoder at a time still holds. | Wind in canvas is the cheapest proof of a festival in daylight without showing people. | baked cloth motion |
| Gulls | 06:10 surf only | 3–5 flipbook sprites (8-frame atlas) on baked curve paths, one pass every ~25 s. | Gulls are in the dawn soundscape. Seeing the source of a sound makes the ambience believable. | 3–5 sprites |
| Floodlight haze | 20:15 sport | Beam cards with slowly scrolling noise inside the volumetric shafts. No flicker. | Haze in floodlights is what a night stadium looks like in his Maccabi shots. | opacity ±3% |

**Simultaneous particle count, A:** maximum **≈ 405 desktop / 125 phone** (dust + gulls at different hours, never together). Well under the caps.

### A.2 Signature transitions
1. **The time-lapse is the travel.** Moving between fields is scrubbing the footage: shadows swing, the sky races, and the camera drops from the rail to eye height in ≤ 1.6 s. Scrub speed is eased with inertia and a magnetic snap to the room's minute. On arrival, playback rate eases from the scrub speed to 0 over 300 ms (no hard stop). Then the ambient layers fade in over 600 ms. Diegetic: you move by moving the sun.
2. **The terminator line (Home ↔ field).** Home is the time-slice still, where soft masks join six hours along the coast. When you tap a stretch, the mask edge between two hours **slides along the coast** like the day/night line on a globe, until your chosen hour fills the frame (1.2 s, a shader mix of the time-slice and the segment's first frame with a travelling gradient mask). Home reverses it. The seam that makes the map becomes the motion of entering it.
3. **Time pauses (photo open).** Ambient eases to zero (400 ms), the frame dims to 35% and softly blurs (pre-blurred mip mix, 500 ms), and the print rises 24 px into place with a fade (400 ms, cubic out). The render loop then stops.
4. **Midnight replay (Video).** The long-exposure still of the whole day is the first frame of a baked 12 s time-lapse clip. On touch, the clip plays and its last frame (black midnight sea) dissolves (600 ms) into the showreel's first frame on black. Match cut on darkness, not a wipe.

### A.3 Implementation and budgets
- Footage: Cycles segments scrubbed via `requestVideoFrameCallback`, with a 6-frame GOP (as in CONCEPTS.md). Ambient at rest uses **shader layers on a paused frame**, not more video, except the small canopy loop.
- Shaders: one flow-map water pass and one haze-card material, both ported-to-TSL-friendly (small, isolated, research §2.1).
- Sprites: dust in one instanced draw call, gulls in one. Two draw calls in total for all particles.
- Draw-call impact of motion: ≤ 6. Download impact: water and flow masks per hour ≈ 40 KB each (JPEG/PNG, 512²), canopy loop ≤ 150 KB, gull atlas ≈ 20 KB.

### A.4 What stays still near a viewed photo
Everything. Video paused, flow map frozen, haze frozen, dust faded out and stopped, gulls removed, look-around and the sun glint frozen, render loop stopped. The day's tint never touches the photo (the mount is neutral and `toneMapped=false`).

### A.5 Reduced motion
No scrubbing or flight. A cross-fade of 400 ms between the stills of each room's minute. The terminator line becomes a 400 ms cross-fade. No water, haze, dust, gulls or canopy loop. The midnight replay shows a play icon on the long-exposure still and plays only on request, with standard video controls.

### A.6 Rejected
- **God rays on every hour (post-process).** Light shafts belong only where the haze and the pines justify them (18:30, and the floodlights at 20:15). Rays everywhere make "bloom on everything" (skill mistake list).
- **Lens flare that follows the cursor.** A flare reacts to the sun, not to a mouse. It is a toy.
- **Clouds racing at rest.** Time-lapse sky only while time moves; at rest, clouds are still. Otherwise the pause loses its meaning.
- **Star-trail sky at midnight.** A long-exposure cliché. The midnight still is already a long exposure, of the day.
- **A spinning clock hand or animated numerals in the sun-arc.** The arc is a hairline; the current hour is shown by a mark that moves only while the visitor moves time.
- **Sparkle particles on the water.** The glint shader does this with zero particles.
- **UI tinted by the hour.** That is the colour takeover Shay dislikes. The interface stays ivory on dark in every hour.

---

## B. DEPTH OF FIELD: the focus ring is the map

### B.1 Ambient motion
The camera never travels, so the view must not look like a still photograph. Each moving element sits **in one focus plane**, so it sharpens and blurs with the ring: the ambient motion also teaches the mechanic.

| What moves | Plane | How | Why | Amplitude |
|---|---|---|---|---|
| Pine bough sway | 1.5 m (near) | Vertex displacement of a subdivided quad on the near RGBA layer, masked by a baked weight map (tips move, trunk does not). | The nearest thing in a real landscape is the one that moves. It also shows the near plane exists while it is blurred. | ≤ 3 px, period ~8.9 s |
| Linen backdrop breathing | 1.5 m | Same technique, its own mask, period ~6.3 s. | The empty portrait set waiting for someone: life without people. | ≤ 2 px |
| Canopy ripple | 12 m | Low-frequency displacement mask on the canopy fabric. | Festival fabric in the evening breeze. | ≤ 2 px |
| Haze between planes | between 12 m, 120 m and ∞ | Two soft noise layers inserted between the depth layers, scrolled at different speeds. | Haze is what makes the depth readable (CONCEPTS.md calls it essential). Movement in it gives the layers separation. | opacity ±4% |
| Sea and surf line | ∞ | Flow-map shimmer + a scrolling foam mask along the baked surf line. | Surfing lives at ∞; the surf has to roll. | ≤ 2 px |
| Lamp bokeh | all planes | **Live bokeh sprites** at the light positions exported from Blender (string bulbs, floodlights, sea glints). Disc radius = circle of confusion from the thin-lens formula for the current focus. Discs near the frame edges become slightly cat's-eye (mechanical vignetting of a real fast lens). Desktop **≈ 900** (350 bulbs + 48 flood lamps + ≤ 500 glints), phone **≈ 380** (350 bulbs merged into ~180 + 48 + 150). | A pre-blurred mip stack turns points of light into grey mush. His photos show real round discs. Bokeh is the visual identity of this concept, so it must be correct. | discs static in place; only radius changes with focus |
| Handheld drift | camera | Perlin noise on yaw/pitch, ±0.15° (CONCEPTS.md says ±0.3°; I halve it, see Rejected). | A fixed camera that is too fixed reads as a screenshot. | ±0.15° |
| One gull crossing (desktop only, optional) | ∞ | One flipbook sprite on a curved path, once every ~45 s. | A moving thing that turns sharp or soft with the ring. Cut it first if the critic disagrees. | 1 sprite |

Bulb brightness is **steady**: no twinkle. **Particles, B:** ≈ 900 desktop / ≈ 380 phone. Under caps.

### B.2 Signature transitions
1. **Rack focus (enter a field).** The ring moves; each layer's blur (mip level) follows the thin-lens CoC for the new distance, eased cubic over 700–900 ms. The image scales by about 2% (focus breathing), the bokeh discs grow or shrink, and the ambient sound mix follows the plane on the same curve. The camera never moves. This is the concept's only transition, and it is the photographer's real act.
2. **Defocus to f/1.2 (open a photo).** All layers go to maximum blur at once, the bokeh discs swell to their largest, and over 600 ms the disc colours lean 10–15% toward the photo's palette (the world takes its light from the photo; the photo is never tinted). The print comes forward from its small in-world position to the mount, front-parallel, 500 ms. The world becomes the bokeh of his photo. Then the render loop stops.
3. **Hyperfocal (Home).** All layers sharpen together, staggered far→near by 60 ms each, so the eye reads the depth once more. 900 ms.
4. **Past ∞ (Video).** The ring meets a soft detent at ∞ (wheel or swipe resistance). Pushing through it fades in a 6 s baked loop **whose first frame is the still**, so nothing jumps; the scene starts moving more fully (pines, canopies, surf, flood haze), then dissolves into the showreel (600 ms). Diegetic: real lenses do focus past infinity.
5. **Intro.** Pure bokeh (the 40 KB first paint) → focus roll ∞→near → settle at hyperfocal (2–4.5 s, as in CONCEPTS.md). The blur is the loading state, so it is never a fake delay; the roll waits for the layers and is skipped on any input.

### B.3 Implementation and budgets
- One fragment shader per layer mixes a pre-blurred mip stack by CoC (already the plan); displacement for bough, linen and canopy happens in the same layer shader through a mask channel. Six layers + two haze cards + one bokeh draw = **~10 draw calls**.
- Bokeh sprites: one instanced draw, an additive disc texture (with a faint edge, as on a real lens), size from a CoC uniform, position from a JSON export (≈ 15 KB).
- Hover "focus peaking": a **static** faint ivory edge on the plane that would focus (a precomputed edge mask per layer, 300 ms fade). It does not shimmer.
- Canvas2D fallback (no WebGL): five pre-composed focus states, cross-faded. No ambient motion.

### B.4 What stays still near a viewed photo
After the 600 ms palette lean, the bokeh and every layer freeze and the loop stops. No drift, no breathing, no haze, no bough, no gull, gyro off. The world behind the print is a still bokeh field.

### B.5 Reduced motion
A 300 ms cross-fade between the five pre-composed focus states (as in CONCEPTS.md). No breathing magnification, no drift, no displacement, no haze, no live bokeh growth (the discs are baked into each state). The palette lean is applied instantly with the fade. Past ∞ shows a poster + play icon.

### B.6 Rejected
- **Chromatic aberration fringes during the focus pull.** A post-process signature of "effects", not of his lenses (modern glass hides it).
- **Twinkling string lights.** Real bulbs do not twinkle; it is the cheapest "magic" cue on the web.
- **Tilt-shift miniature blur.** It makes the world look like a toy, which is the game look Shay rejected.
- **Animated, shimmering focus peaking.** In the concept text it shimmers; I keep it static. A shimmer on hover is UI candy.
- **±0.3° handheld drift.** On a 27" screen at 50 mm this reads as a wobble, and a fixed-view concept invites long looking. ±0.15° is enough to feel handheld.
- **Lens dirt, rain on the lens, dust on the sensor.** Fake imperfections; his frames are clean.
- **Dolly zoom (vertigo) on enter.** The camera must never move; that is the idea.
- **Fireflies.** They are not on a Mediterranean kurkar ridge, and they are particles for their own sake.

---

## C. WHERE HE STOOD: the held moment

### C.1 Ambient motion
The concept is a stopped instant. **The held matter must never drift, rotate or "float".** If the spray moves, the idea is gone. So in C, life comes only from what is still real in a frozen world: **light that depends on where you stand, and you.**

| What moves | How | Why | Amplitude |
|---|---|---|---|
| Glints in held drops | The near drops have a view-dependent specular (sun direction fixed, camera moving). As the camera glides or idles, highlights wander across the frozen drops. | Time is stopped, light is not. It is the strongest proof that the visitor is inside the moment. | zero cost when the camera is still |
| Mirror reflections on the wet flat | Planar reflection (desktop, half resolution) or a baked reflection probe with screen-space offset (phone). Moves only with the camera. | The doubled world is part of the overview's composition. | camera-driven only |
| Footprint reveal | Baked normal map; the wet edges of the footprints catch the sun as the camera approaches (a raking specular term with a distance falloff). No glow, no ring. | "Where he stood" must be findable without a game marker. | appears within ~15 m |
| Idle camera breath | At the overview only: ±0.15° slow drift, which also makes the glints shimmer. Off at vantages. | Without it the overview looks like a render. | ±0.15° |
| Sun-edge sky gradient | none | The sun is held too. Nothing in the sky moves. | — |

**Live particles, C:** only the nearest held drops and paper pieces, as soft depth-sorted sprites with refraction-style glints: desktop **≤ 1,500**, phone **≤ 450**. They do not move; they are sprites because they need per-frame view-dependent shading and sorting near the lens. Everything farther is static geometry (C.4).

### C.2 Signature transitions
1. **The glide to the vantage (enter a field).** 1.2 s, cubic in-out, one move (dolly + crane down to eye height), and the focal length eases to Shay's lens (85 mm portraits, 200 mm surf) during the last 40% so the compression arrives with the stop. The camera never passes through matter: the paths are authored in Blender and exported as camera JSON.
2. **The click (registration).** In the last 200 ms the held matter lines up with the frame. Then, in this order:
   - a viewfinder blackout of **80 ms that dips luminance to 85%** (the mirror slap of a DSLR, at the moment of the shutter sound; not a white flash);
   - a hairline ivory frame line draws in (200 ms);
   - the cover photo fades into the frame line (150 ms), exactly registered, at true ratio, uncropped;
   - the real ambience bursts in for 1 s and fades out.
   It is the concept's whole idea in one beat, so it must be **exact** (registration error ≤ 2 px at 1080p) or cut.
3. **Circling the held moment (between rooms of one field).** An orbit around the held moment's centre with the target locked. The skill limits one orbit move to ≤ 25°. Seven festival vantages on a full ring would be 51° per hop, so **I recommend the creative director place the 7 festival vantages on a ~150° arc (~25° apart)**, and the 6 portrait spots on ~125°. Each hop then becomes one calm 0.9 s move, with the click at each stop.
4. **Flatten the print (open the photo).** From the registered window in the world to the front-parallel ivory mount: 500 ms, world dims to 35%. The render loop stops.
5. **The back of the print.** Swipe up rotates the print 180° on its horizontal axis in 450 ms, cubic, no overshoot, no bounce. It is the physical act of turning a print over. Text is HTML on the back face.
6. **Time resumes (Video).** A 5 s **baked Cycles clip** from the Video vantage: drops fall on ballistic arcs, confetti flutters down, ticker-tape drifts. Frame 0 of the clip matches the real-time pose exactly. The falling ticker-tape match-cuts into the showreel. On return, the world is held again through a 400 ms cross-fade; the clip never rewinds on screen.
7. **Home.** Crane up from any vantage to the overview, 1.4 s.

### C.3 Implementation and budgets
- **Held matter (static):** one merged mesh per field (drops as low-poly quads or icospheres, paper as quads), baked lighting, one draw call each. Desktop ~20k pieces ≈ 40k triangles per field; phone ~5k pieces ≈ 10k triangles. This sits inside the triangle budgets (1.5M / 400k).
- **Near sprites (view-dependent):** one instanced draw, ≤ 1,500 desktop / ≤ 450 phone, sorted per frame only while the camera moves.
- **Reflections:** planar at half resolution on desktop; baked probe on phone.
- **Phone path** (as in CONCEPTS.md): pre-rendered backplates per vantage + flight clips ≤ 0.4 MB. On that path the glints are baked into the clip, and only the ≤ 450 near sprites are live, over the paused backplate.
- **Time resumes:** one 720p clip per field (≈ 1.5 MB, lazy). Only one video decodes at a time.
- **Click audio:** four 1 s bursts (crowd, surf, bass, breeze), 96 kbps, ≈ 12 KB each, loaded with the field.

### C.4 Conflict to resolve with the creative director
CONCEPTS.md specifies **"GPU-instanced impostors, 80k on desktop and 15k on phone"**. That is **40× the desktop cap and 25× the phone cap** of this role. My proposal, kept above:
- Matter that never moves is **static merged geometry**, not particles (budgeted as triangles: ~40k / ~10k per field).
- Only the nearest matter, which needs live view-dependent glints and sorting, is a sprite system: ≤ 1,500 / ≤ 450.
- The visual density of the concept stays; the particle cap is respected; and the "WebGL particle field" look the concept warns about becomes less likely, because static meshes take baked light like everything else.

The **festival ring geometry** (C.2.3) is the second item for the creative director.

### C.5 What stays still near a viewed photo
At the registered moment and after: the camera is locked (gyro off, no idle breath), so glints and reflections are frozen. The burst audio has ended. Once the print is flattened, the render loop stops. The swipe through the set moves only the HTML print.

### C.6 Reduced motion
- No glides, orbits or crane: a 400 ms cut-dissolve between vantages.
- No blackout, no audio burst; the photo appears with a 300 ms fade inside its frame line.
- The flip becomes a cross-fade between the front and the back.
- No idle breath, no gyro.
- Time resumes becomes a poster + play icon.

### C.7 Rejected
- **Bullet-time orbit around the held moment.** It is *The Matrix*, the exact trope the concept is closest to. Orbits are ≤ 25° and only from vantage to vantage, never a showy 360°.
- **Matter that slowly drifts or rotates ("almost frozen").** It is a screensaver, and it kills the idea of a held instant.
- **A white flash on the click.** That is the flash-reveal idea already killed, and it hides the photograph at its moment of arrival.
- **Ripple shader where you tap the wet sand.** The water is held too; a ripple would also be a toy.
- **Ghost silhouettes of the missing people.** The absence in the spray is enough. Ghosts would be horror and would compete with the real people in his photos.
- **A rewind effect when leaving the Video vantage.** A cheap VHS trope; a quiet cross-fade back to the held state is enough.
- **Glowing rings or pulsing markers on the footprints.** Raking light is the marker.
- **Shatter or explode transitions** of the held matter. Spectacle, not photography.

---

## Comparison: motion load per concept

| | A. SUNLINE | B. DEPTH OF FIELD | C. WHERE HE STOOD |
|---|---|---|---|
| What is alive at rest | water, haze, one hour-specific element | bough, linen, canopies, haze, sea, steady bokeh | only view-dependent light (glints, reflections) |
| Max live particles (desktop / phone) | ≈ 405 / 125 | ≈ 900 / 380 | ≤ 1,500 / ≤ 450 |
| Signature transition | time-lapse scrub + terminator line | rack focus | glide + the click |
| Baked video for motion | segments, canopy loop, midnight replay | past-∞ loop | flight clips (phone), time-resumes clips |
| Risk of motion sickness | medium (fast scrub; cap scrub speed) | very low (camera fixed) | medium (glides; ≤ 25° orbits, no roll) |

## Verified vs assumed
- **Verified (by reading the project files):** concept content, budgets and research claims as written in CONCEPTS.md, world2-research.md and the three skills; the 80k/15k impostor figure in Concept C that conflicts with the particle caps; the orbit limit of ≤ 25° per move against the 7-vantage ring.
- **Assumed (nothing built or measured):** all particle counts, file sizes, durations and amplitudes above are design targets. Frame-time impact needs real-device timing (iPhone 12 / Galaxy S20 class) before any performance claim. Whether 80 ms at 85% luminance reads as a mirror blackout or as a glitch must be judged on screen. The bokeh-sprite light counts depend on the final Blender scene.
