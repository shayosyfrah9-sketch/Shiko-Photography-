# Critique: Concept C "World Beyond the Lens", risk test
Independent art critic, 2026-11-24. Read-only; this file is the only thing written. Judged on pixels only; the maker's NOTES.md was NOT read before scoring.
Context seen once: C round-1 keyframe 1, C round-2 keyframe 2 and click mock-up, the real photo surf0001.jpg, B-round-2.md.

## Images and labels
| File | Label on image |
|---|---|
| C_rt_1_spray_RENDERED.png | Rendered (Cycles CPU, 1600x900, 96 spp + OIDN, 2744 glass drops, mist volume) |
| C_rt_2_click_MOCKUP.jpg | Mock-up: rendered world + the real photo pasted in PIL, ivory mount, 32 rendered edge drops; plus a viewer panel |
| C_rt_3_phone_MOCKUP.png | Mock-up: HTML UI over rendered backdrop (C_rt_3_phone_backdrop_RENDERED.png) |

Verified: everything visible in the pixels. Assumed: nothing from the maker's claims.

## Scores (1-10)
| # | Criterion | Score | Evidence (one line) |
|---|---|---|---|
| 1 | Spray / water believability | 4 | 2744 near-uniform confetti drops of one size fill the sky evenly, with no plume, no density core, no motion streaking; the sea is flat horizontal banding with a glitter patch and no wave at all. |
| 2 | Photo-world match / the click | 3 | World is a cool grey-lilac haze with soft light; the photo is hard midday, saturated cobalt and cyan with a high sun. Pasted as an ivory-mounted rectangle, it looks like a postcard on a wallpaper; the spray does not continue into it. |
| 3 | Phone frame | 5 | Clean RTL Hebrew UI, icon header and bottom bar are tidy; but the picture is 35% empty moire sand, labels float like map pins, and no photo or subject is shown. |
| 4 | Overall photorealism | 4 | Reads as a render at first glance: glassy oval drops, rubber-looking ripple sand with a regular moire, a wet-looking blur plane for sea. Beach, not world. |
| 5 | Originality shown in pixels | 5 | The idea (photo is a window and the spray spills out of it) is strong on paper; in pixels it is a framed picture over a spray backdrop, which is the common "gallery wall" pattern. |
| 6 | Brand fit | 5 | Calm and photo-first, Hebrew first, icons not text: good. But the world is dull and pale next to Shay's saturated, high-energy surf work; the photo outshines the world 10:1. |

**Average of the first three (Shay's criteria): 4.0**
**Average of all six: 4.3**

## Shay's three criteria
### (a) Match between his real photo and the 3D world: FAIL
- **Light direction/colour.** The photo has a high hard sun, sapphire sky, turquoise sea, deep contrast. The world has an overcast-dusk lilac gradient, a faint left glitter patch, no visible sun, low contrast. They are two different days. The photo's own spray is bright white and sharp; the world's drops are pale grey-blue and smaller.
- **Spray continuing.** At the photo border about 32 drops overlap the mount, but they are the same confetti as everywhere else; there is no plume that leaves the frame, no bigger drops near the edge, and the photo's own spray (dense white mass right of the surfer) is cut straight at the frame edge. The eye reads "two objects", not "one splash".
- **Registration.** The hand-traced surfer-shaped absence (about +/-3 px, shown in the crop) is a pleasant technical idea but it is hidden by the photo itself in the final click image, so it proves nothing visually. The photo's horizon sits at about 55% of the frame while the world's horizon is at about 80%: the two horizons contradict.
- **The click works as a transition concept** (world, then photo, then viewer) and the viewer panel is fine, but the key promise, that the world is the continuation of the photograph, is not delivered.

### (b) Water and spray: FAIL (weak)
- Drops: glass-like ovals with bright rims at one scale; no log-normal size mix, no cluster/sheet structure, no fine mist near the source. Reads as snow or a confetti particle field.
- Water: horizontal colour bands, a glitter patch, a pale foam strip at the shore. No wave, no lip, no depth, no wet-sand reflection. Round 2's wave was blobby; this removes the wave and so removes the sport.
- The sand is a regular chevron ripple with visible repetition (moire), the worst-looking area in all three images.

### (c) Vertical phone: MEDIOCRE
- The layout is sound: header icons top, three pins, footprints marker "here Shay stood", CTA bar. Booking and WhatsApp are findable in under 3 s.
- Weak: about 35% of the height is empty sand; the spray is a thin speckle in the upper 45%; the pins (Festivals, Sport, Portraits, Surfing) hang on nothing, so it feels like a game map with markers; the footprint icon plus "drag the footprints" is a game-like affordance. The first frame has no photograph, so it does not show the photos as the art.

## Flags
- **Game-like: YES** (floating HUD pins over a world, footprint "you are here" marker, "drag to see what Shay saw").
- **Particle-field: YES** (uniform spray of identical drops across the whole sky).
- **Template-like: PARTLY** (framed print with ivory mount over a blurred backdrop is a standard gallery/lightbox layout; icons-in-dark-pills is a stock mobile pattern).
- **Bullet-time cliche: NO in these images** (the frozen-moment idea is present but not staged as a bullet-time orbit).

## Stop rule
Rule: average below 6.5, or a click that does not work, means Concept C stops.
- Average of the first three: 4.0. Average of all six: 4.3. Both are below 6.5.
- The click works mechanically, but fails the match test (a).
- **Stop rule triggers: YES.**

## Comparison with Concept B round 2 (avg 5.7 on the 10-point card)
| | B round 2 | C risk test |
|---|---|---|
| Best asset | Light and bokeh are photographic; six-state sheet proves the mechanism | The idea; clean phone UI |
| Worst asset | Mannequin crowd, box stadium, empty sea | Uniform spray, sand moire, light mismatch with the photo |
| Proof of the central idea | Yes (focus states work on screen) | No (the spray-into-photo continuity is not visible) |
| Game-like | Crowd and stadium | HUD pins, footprints, particle sky |
| Average | 5.7 | 4.0 (three criteria) / 4.3 (six) |
B is clearly ahead: it shows its core mechanism working and has real atmosphere. C is ahead only on being less cluttered and on a more honest phone layout.

## Top 3 concrete fixes IF someone continued
1. **Match the world to the photo's light, then make the spray continue it.** Sun elevation about 55-65 degrees, colour 5600 K, sky zenith about RGB (0.20, 0.35, 0.80), horizon band teal about (0.0, 0.5, 0.6); exposure about +1.5 EV over now; keep world contrast >= 100:1 between mist and shadow. Put the photo horizon and the world horizon at the same height (within 3% of frame height). Replace the ivory mount with a 30-60 px feathered edge, and put at least 150 drops, plus a white plume mass as dense as the photo's own spray, crossing the border, matched in size and density.
2. **Rebuild the spray as a distribution, not confetti.** Log-normal drop radius 0.3-6 px (not one size), density falling about 10x from the plume core to the edge, 30% of drops with motion-streak 2-6x length along the arc, a 15-25% white mist alpha at the core, and no glass rim on drops below 3 px (they should be white specks). Cut the count in the outer 50% of the frame by 70%.
3. **Give the water a wave and fix the ground and the phone.** Two-scale displacement (swell about 1.5 m wavelength x 0.3 m, chop 0.2 m) with a foam rim and a real specular sun path 60-100 px wide; scale the sand ripple 3x and break its regularity (noise-modulated phase) to kill the moire. In the phone frame, raise the horizon to about 40% from the top, sand to at most 20% of height, put the photo (or the plume) in the middle third, and delete the footprints marker.

## Verdict: **STOP C**
The stop rule is triggered by the numbers (4.0 / 4.3 against 6.5), and not by a close call: the three images do not demonstrate that a real photo and a 3D world can be made to look like one scene. The central promise of Concept C is exactly the thing the risk test failed to show. If Shay wants to keep any part, take the idea of the photo opening as a "window" and fold it into B, whose light and focus mechanism are already stronger. Do not spend more render time on C as it stands.
