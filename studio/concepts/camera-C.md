# Camera plan C: WHERE HE STOOD (the held moment)
Cinematic director, 2026-11-24, branch `world2-dev`. Text only: nothing was rendered or prototyped for this file (Blender not run). All frames are **plans** for Rendered key frames, an Interactive prototype (real-time three.js) and Mock-ups.

The conventions (units, lens→FOV table, easing, comfort limits, skip and return rules) are in `camera-A.md` §0 and apply here.

C is the only concept with a real-time camera that travels, so it carries the most motion-sickness risk. Every move below is **choose-and-glide**: the visitor picks a destination and the camera flies a pre-authored path. The visitor never steers.

## 0. Layout assumptions the camera depends on
- The sun is at 2.5° altitude, azimuth 270° (west). The overview camera faces about 20° off the sun.
- The four held moments stand on the flat, 70–160 m from the overview camera:

  | Moment | Position (x, y) | Radius of its vantage arc |
  |---|---|---|
  | Surf lip | (55, 70) | 70 m (long lens) |
  | Festival canopy | (−45, 80) | 14 m |
  | Sport ticker-tape and hall | (5, 150) | 18 m |
  | Portrait grove | (−70, 20) | 6 m |

- **[change] Vantages sit on an arc, not a ring.** CONCEPTS.md puts the 7 festival vantages in a ring around the canopy. A full ring puts half of them **front-lit**, which breaks the "every drop is a rim-lit gold bead" art rule. A ring also forces 51° steps, more than double the skill's ≤ 25° orbit limit. All of a field's vantages therefore sit on an arc **on the shadow side (facing the sun), within ±75° of the anti-sun axis**:
  - Festivals: 7 vantages at 25° spacing (150° arc).
  - Portraits: 6 vantages at 25° spacing (125° arc).
  - Sport: Football on the turf vantage, then Basketball and the Reservists League on the hall vantage, 25° apart.
  - Surfing: 1 vantage.
  - Video: 1 vantage at the centre of the flat.
  - Booking: 1 "your moment" vantage, plus the dock.

## 1. First-visit intro (6.0 s, skippable)
The concept text opens on "one shutter click", but **audio is locked until the first gesture**, so a first visit cannot open on sound. **[change]** The click becomes visual: a two-blade shutter iris opens. The sound plays later, on the first "click" arrival, when audio is allowed.

| # | t (s) | Shot | Camera | Lens | Move / easing | Learns |
|---|---|---|---|---|---|---|
| 1 | 0.0–0.6 | Black, the ivory camera mark. | — | — | outCubic fade 400 ms | Brand |
| 2 | 0.6–1.1 | A **shutter iris** (2 blades, dark slate, no white) opens on frame 1 of shot 3. | (−18, −40, 0.6) | 35 mm | Iris 500 ms, inOutCubic | "A photograph is being taken." |
| 3 | 1.1–4.0 | **Low glide** across the mirror sand toward the festival canopy. Hanging water drops pass the lens out of focus. At 2.4 s the camera passes *through a gap* in a spray curtain (it never passes through geometry). | (−18, −40, 0.6) → (−12, −33, 0.7), 2.5 m/s, heading 20° | 35 mm | **Truck + gentle dolly**, yaw change ≤ 6°. inOutCubic. | "Nothing moves. Time stopped." |
| 4 | 2.6–4.0 | A one-line caption, low-centre, 300 ms fade in and out: "הזמן עצר. מצאו איפה הוא עמד." / "Time stopped. Find where he stood." | — | — | outCubic / inCubic | The premise (see risk 2) |
| 5 | 4.0–5.4 | **Crane-up reveal** to the overview. The four moments and their reflections come into view. Footprints form a leading line from bottom-left. | → (0, −60, 14), pitch −3° → −12° | 35 mm | **Crane up + pull back**, 9.6 m/s peak, pitch rate ≤ 12°/s. inOutCubic. | The world |
| 6 | 5.4–6.0 | Four field icons at the bottom and the dock to 100%. Each moment's footprint pair glints once in turn (raking-light glint 200 ms). Input live from 5.4 s. | static | 35 mm | outCubic | "These are the destinations." |

- **Phone (mid and high tier, real time).** The same shots. The overview camera is at (0, −52, 18) with pitch −16°, 35 mm rotated (vFOV 54.4°), so all four moments stack vertically.
- **Phone (low tier).** The intro is **not** a video, because a 6 s, 720×1280 clip of about 1.5 MB would eat the 2.5 MB first-view budget. It is the overview poster (≤ 150 KB) with a 2-layer parallax push of 3% over 3.0 s, then the UI. Total 4.0 s.

## 2. Return visit (1.2 s)
| t (s) | What happens |
|---|---|
| 0.0–0.5 | Overview poster, iris opens (400 ms). |
| 0.4–0.6 | The real-time scene replaces the poster invisibly, because the poster is the exact first frame. |
| 0.5–0.9 | UI fades in. |
| 0.7 | Input live. No glide, no caption. |

## 3. Camera language per state
| State | Position / height | Lens | Move type | Easing | Duration |
|---|---|---|---|---|---|
| **Home** (overview) | (0, −60, 14), pitch −12° | 35 mm (phone 35 mm rotated) | Static. Look-around by drag: ±25° yaw, ±10° pitch, spring back after 2 s idle. Idle breathing 0.2 m vertical over 8 s. | snap | idle |
| **Moving to a field** (tap the moment, its icon, or ↑↓) | → the field's **first** vantage, at Shay's eye height of 1.6 m (surf: 1.2 m) | 35 mm during the flight; lens change only **after** landing, see the next row | **Look-then-go glide:** the target swings to the destination in the first 40% of the time while the position follows on a Bezier that **stays at ≥ 6 m altitude until 65%**, then descends (so low-altitude ground flow is brief). Peak yaw rate ≤ 45°/s. No passing through matter; paths are authored with a 1.5 m clearance. | inOutCubic | t = clamp(0.9 + d/120, 0.9, 1.6) s, where d is the path length in metres (≈1.2 s typical) |
| **Lens change / "the click"** | Fixed at the vantage | 35 → field lens: Portraits 85 mm, Festivals 50 mm, Sport 135 mm, Surf 200 mm, Video 35 mm | A pure **zoom-in at rest**. No dolly, so there is no dolly-zoom. Then a 90 ms dark two-blade shutter wipe, and the cover photo fades in registered in the frame line (400 ms). Shutter sound + a 1.0 s ambience burst, if audio is on. | inOutCubic (zoom), outCubic (photo) | 0.5 s zoom + 0.09 s + 0.4 s |
| **Entering a room** (next vantage in a field: ← →) | Same height | Field lens kept | **Orbit 25°** around the moment's pivot on its arc. For telephoto fields the orbit is done at **35 mm**: zoom out 0.3 s, orbit 1.0 s, zoom in 0.3 s. At 200 mm, a 25° orbit would sweep the frame by about 3.6 frame-widths and is disorienting. Portraits (85 mm, 6 m radius) orbit directly. | inOutCubic | 1.0 s (85 mm and wider), 1.6 s (135/200 mm) |
| **Photo opens** (tap the registered cover) | static | — | The cover flattens to a front-parallel print on the ivory mount, 70% of width (landscape) / 88% (phone). The world dims to 35% and blurs. The matter's gentle idle shimmer stops. | outCubic | 450 ms |
| **Photo → photo** | static | — | Slide 6% + cross-fade. The world does not move. | outCubic / inCubic, 60 ms overlap | 280 ms |
| **Back of the print** | static | — | The print turns 180° on the Y axis at 0.6 m depth (perspective 1200 px). It is a flip of a flat object, not a camera move. | inOutCubic | 500 ms |
| **Video** (Video vantage, press) | (0, 10, 1.6) | 35 mm | Static camera. Time resumes for 5 s (matter animates), then a 1.0 s cross-dissolve into the showreel. | linear time inside the sim; dissolve inOutCubic | 5 + 1 s (skippable: tap = straight to the reel) |
| **Home in one tap** | → overview | Field lens → 35 mm **first, while still standing** (0.25 s) | **Crane up** 0.35 s to 8 m, then **pull back on a straight line** to the overview, 0.6 s. Yaw ≤ 45°/s. | inOutCubic, one continuous curve | 0.25 + 0.95 = 1.2 s (Comfort: 0.6 s cross-fade) |

- **Look-around while in a vantage** is scaled to the lens: max yaw = 25° × (35 / f). That is ±10.3° at 85 mm and ±4.4° at 200 mm. The image never whips at telephoto.

## 4. Input mapping
| Action | Desktop | Phone |
|---|---|---|
| Go to a field | Click its moment or footprints, a bottom field icon, ↑ / ↓ (previous/next field), or keys 1–4 | Tap the moment or a field icon |
| Next / previous vantage (room) | ← → (in RTL ← = next, following the arc dots visually) | Tap the ‹ › chevrons beside the vantage dots. A horizontal swipe also works, but **only while the photo viewer is closed** (see risk 3). |
| Look around | Drag ±25° (lens-scaled), spring back | Gyro (opt-in tap) or a one-finger drag. Spring back after 2 s. |
| Open the photo | Click the registered cover, or Enter | Tap the cover |
| Next / previous photo | ← → while the viewer is open | Horizontal swipe while the viewer is open |
| Back of the print | Click the "turn" icon (↻), or F | Tap the ↻ icon. **[change]** not a swipe up, which collides with the iOS home gesture. |
| Close viewer / leave room | Esc closes the viewer. A second Esc goes to the overview. | Swipe down or ✕ |
| Home | Camera icon, H | Camera icon |
| Wheel | **[change]** CONCEPTS.md has "wheel dollies to overview". Instead, the wheel does **nothing in a vantage** unless 3+ notches arrive within 600 ms. That prevents an accidental exit from a trackpad graze. In the viewer, the wheel = next/previous photo. | — |

## 5. Motion sickness and reduced motion
| Variant | Trigger | What changes |
|---|---|---|
| **Default** | — | §0 limits: yaw ≤ 45°/s, glides ≤ 1.6 s, ≥ 6 m altitude for the first 65% of a glide, no dolly-zoom, zoom only at rest, roll 0. The intro glide is at 0.6 m height but only 2.5 m/s (walking pace). |
| **Comfort** | ⚙ toggle | Every glide becomes a **cut-dissolve**: 250 ms fade to 40% luminance, cut, 350 ms fade up. Orbits become dissolves. Look-around is ±8° max, gyro off. The intro skips shot 3 (no low glide): the iris opens directly on the overview. |
| **Reduced motion** | `prefers-reduced-motion` | Comfort, plus no zooms (the lens is already set at the cut), no matter shimmer, no ambience bursts, and no animated "time resumes": Video goes straight to the reel poster with a play button. Print flip = 200 ms cross-fade from front to back. Intro = overview poster with a 400 ms fade, 0.8 s total. |
| **Low device tier** (any motion mode) | GPU tier detection | Glides are pre-rendered **1.2 s clips** (≤ 0.4 MB each) over backplates, as in CONCEPTS.md. Orbits are clips too. Look-around is a 2D offset of the plate, ±1.5°. |

## 6. Camera keyframe JSON sketch
```json
{
  "schema": "shiko-cam/1",
  "concept": "C-where-he-stood",
  "units": "m", "up": "Z", "fps": 24, "sensor_mm": [36, 24],
  "sun": { "alt_deg": 2.5, "az_deg": 270 },
  "limits": { "yaw_deg_s": 45, "roll": 0, "glide_min_alt_until": 0.65, "glide_min_alt_m": 6, "clearance_m": 1.5 },
  "vantages": [
    { "id": "fest_freeearth", "field": "festivals", "order": 1, "pivot": [-45, 80, 3], "arc_deg": -75, "radius": 14, "eye_m": 1.6, "focal_mm": 50 },
    { "id": "fest_ozora",     "field": "festivals", "order": 2, "pivot": [-45, 80, 3], "arc_deg": -50, "radius": 14, "eye_m": 1.6, "focal_mm": 50 },
    { "id": "surf",           "field": "surfing",   "order": 1, "pivot": [55, 70, 2],  "arc_deg": 0,   "radius": 70, "eye_m": 1.2, "focal_mm": 200 },
    { "id": "portrait_mayu",  "field": "portraits", "order": 1, "pivot": [-70, 20, 1.6], "arc_deg": -62, "radius": 6, "eye_m": 1.6, "focal_mm": 85 }
  ],
  "shots": [
    { "id": "intro", "duration": 6.0, "ease": "inOutCubic",
      "keys": [
        { "t": 0.6, "pos": [-18, -40, 0.6], "target": [-45, 80, 3],  "focal_mm": 35, "iris": 0 },
        { "t": 1.1, "pos": [-18, -40, 0.6], "target": [-45, 80, 3],  "focal_mm": 35, "iris": 1 },
        { "t": 4.0, "pos": [-12, -33, 0.7], "target": [-40, 85, 3],  "focal_mm": 35 },
        { "t": 5.4, "pos": [0, -60, 14],    "target": [0, 60, 0],    "focal_mm": 35 }
      ],
      "events": [ { "t": 2.6, "caption": "intro_line", "out": 4.0 }, { "t": 5.4, "ui": "in", "input": "live" } ] },
    { "id": "overview_to_fest_freeearth", "duration": "auto", "ease": "inOutCubic",
      "keys": [
        { "u": 0.0,  "pos": [0, -60, 14],   "target": [0, 60, 0] },
        { "u": 0.4,  "pos": [-10, -38, 11], "target": [-45, 80, 3] },
        { "u": 0.65, "pos": [-28, 0, 6.0],  "target": [-45, 80, 3] },
        { "u": 1.0,  "pos": "vantage:fest_freeearth", "target": "pivot", "focal_mm": 35 }
      ],
      "then": { "id": "click", "zoom_to_mm": 50, "zoom_s": 0.5, "shutter_s": 0.09, "cover_fade_s": 0.4 } },
    { "id": "orbit_fest_1_to_2", "duration": 1.0, "ease": "inOutCubic", "type": "orbit",
      "pivot": [-45, 80, 3], "from_deg": -75, "to_deg": -50, "radius": 14, "eye_m": 1.6, "focal_mm": 50 },
    { "id": "home", "duration": 1.2, "ease": "inOutCubic",
      "keys": [
        { "t": 0.0,  "pos": "current", "focal_mm": "current" },
        { "t": 0.25, "pos": "current", "focal_mm": 35 },
        { "t": 0.6,  "pos": "current+z8" },
        { "t": 1.2,  "pos": [0, -60, 14], "target": [0, 60, 0], "focal_mm": 35 }
      ] }
  ]
}
```
- **Vantage position** = pivot + radius·(cos θ, sin θ), with θ = anti-sun azimuth + `arc_deg`, and z = `eye_m`. That makes "backlit" a property of the data, not of manual placement.
- **three.js:** `CatmullRomCurve3` through the position keys, with `u` re-timed by inOutCubic. The target is slerped separately so the "look-then-go" timing holds. `fov = 2*atan(12/focal_mm)` on desktop, `2*atan(18/focal_mm)` on phone.
- **Blender:** the same keys drive key frame renders and the low-tier clips.
- **The registration of each cover photo** (exact vantage, focal length and roll = 0) is a per-room art-direction job. The values above are placeholders.

## 7. Where a first-time visitor will get confused, and the fix
1. **"Where do I tap?" on an open plain (the biggest risk).** The diegetic footprints are subtle by design, the flat has 4 moments and 20 vantages, and there are no labels. A first-timer may glide around without understanding that each footprint pair is a gallery.
   **Fix:**
   - The always-visible **bottom bar of 4 field icons** (names on hover, and on the phone on the first visit).
   - On the overview, each moment gets a faint ivory name label for the first visit only, until the first arrival.
   - In a field, a **vantage-dots indicator** (•••○•••, 7 dots for festivals) with the room name ("Ozora · 2/7") and ‹ ›.
   - The footprints glint in raking light once every 6 s when idle.
2. **"The people are missing" reads as "the photos didn't load".** **Fix:** the single intro caption (shot 4), and a short first arrival: within 1.6 s of landing, the click puts the cover photo in, so the visitor sees the absence filled before they can doubt it.
3. **One gesture, two meanings on the phone.** A horizontal swipe arcs to the next vantage in the world, but it means next photo inside the viewer. **Fix:**
   - The viewer is a distinct modal (ivory mount, dimmed world, ✕) so the mode is visible.
   - In the world, the primary control is the ‹ › chevrons. The swipe is a secondary shortcut, and it is disabled for 400 ms after the viewer closes, so a "next photo" flick does not carry into an orbit.
4. **Orientation lost at telephoto.** Arriving and orbiting at 135/200 mm flattens the space. **Fix:** fly at 35 mm, zoom only at rest, orbit telephoto fields at 35 mm, and a tiny overview minimap is **not** added (it would read as a game HUD). Orientation comes from the always-visible sun direction instead: the sun is always in the frame's upper half, and the flight starts by looking at the destination.
5. **The wheel leaves the room by accident.** **Fix:** the 3-notches-in-600 ms threshold (§4).

## Verified vs assumed
- **Verified:**
  - The concept text, room list and order, and the skill rules (orbit ≤ 25°, ≤ 70° vFOV, sound only after a gesture).
  - The arithmetic: FOV table, lens-scaled look-around, 25° arc spacing for 7 vantages = 150°.
  - The 3.6 frame-width figure: a 25° orbit at 200 mm shifts a point 70 m away by about 30 m, which is about 3.6 × the 8.4 m frame width at that distance.
- **Assumed:** all positions and radii (the flat is not built), the 6 m / 65% glide rule and the duration formula, the comfort of the 2.5 m/s low glide, the tier split, and the clip sizes. A real-device test and an animatic are needed. No animatic has been made, because Blender was not to be run.
