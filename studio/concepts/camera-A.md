# Camera plan A: SUNLINE (one day of light)
Cinematic director, 2026-11-24, branch `world2-dev`. Text only: no image, render or animatic exists yet. Every frame described here is a **plan** for a Rendered (Blender/Cycles) clip or still. Nothing was rendered for this file (Blender not run).

Source of truth for the concept: `studio/concepts/CONCEPTS.md` §A. Where this plan departs from it, the change is marked **[change]** with the reason.

## 0. Conventions used in all three camera files
- **Units:** metres, Blender Z-up. three.js converts with (x, y, z)_three = (x, z, −y).
- **Lens to FOV:** full-frame sensor 36 × 24 mm. Desktop (landscape) uses vertical FOV = 2·atan(12/f). Phone (portrait) uses a **rotated sensor**, vertical FOV = 2·atan(18/f), so the focal length keeps its meaning on both.

  | f (mm) | 24 | 28 | 35 | 50 | 85 | 135 | 200 |
  |---|---|---|---|---|---|---|---|
  | desktop vFOV | 53.1° | 46.4° | 37.8° | 27.0° | 16.1° | 10.2° | 6.9° |
  | phone vFOV | 73.7° ✗ | 65.5° | 54.4° | 39.6° | 23.9° | 15.2° | 10.3° |

  24 mm is not allowed on the phone, because it breaks the skill's 70° vertical-FOV ceiling.
- **Easing names:** `inOutCubic` = cubic-bezier(0.65, 0, 0.35, 1), used for every camera move. `outCubic` = cubic-bezier(0.33, 1, 0.68, 1), used for UI in. `inCubic` = cubic-bezier(0.32, 0, 0.67, 0), used for UI out. `snap` is a critically damped spring with ω = 12 rad/s, which settles to 1% in about 0.4 s. There are no linear starts or stops.
- **Comfort limits (all concepts):**
  - Roll 0° always, horizon level.
  - Peak yaw rate 45°/s (Comfort mode 25°/s).
  - Never change FOV against the dolly direction, so there is no dolly-zoom vertigo.
  - No white flashes. Luminance may change by at most 3 EV in 250 ms.
- **Skip (all concepts):**
  - The first `pointerdown`, `keydown`, `wheel` or `touchstart` during the intro jumps to its end state with a 300 ms `outCubic` cross-fade. Esc does the same.
  - **That first input is consumed.** It never also scrubs, focuses or navigates.
  - A 44 × 44 px skip icon (⏭) is visible from 0.5 s, bottom corner (bottom-left in RTL).
  - The WhatsApp and booking dock is present and clickable from t = 0 at 60% opacity and reaches 100% at the end of the intro.
- **Return visit:** `localStorage['shiko.w2.seen']` holds the date. If it is less than 60 days old, play the short version. Every read and write is wrapped in try/catch, and a failure falls back to the full intro.

---

## 1. First-visit intro (6.0 s, skippable)
**[change]** CONCEPTS.md has the camera "drift along the waterline" and then has to reach the high Home view. A flight from a 30 m rail to a 420 m vantage in about 2 s is a fast crane that causes motion sickness, and it also needs one extra rendered clip. Instead, the camera **stays at (or near) the Home vantage the whole time**, and the *light* does the travelling. A south-to-north time wipe turns the single-hour still into the time-slice Home. This also teaches the map ("each place = an hour") before the visitor touches anything.

| # | t (s) | Shot | Camera | Lens | Move / easing | What the visitor learns |
|---|---|---|---|---|---|---|
| 1 | 0.0–0.5 | Black. The ivory camera mark fades in, small and low-centre (outCubic, 400 ms). | — | — | — | Brand. |
| 2 | 0.5–1.6 | The coast **at the real Israel hour**, the whole coast lit by that one hour. A pre-rendered still from the nearest of 6 baked hours, AVIF 220 KB. | (−380, −860, 405), pitch −21°, heading 0° (north) | 28 mm | Push-in 1.5% scale (2D, on the overscanned still), inOutCubic over 6.0 s total, continuing under shots 3–4 | "This is a real place, right now." |
| 3 | 1.6–3.8 | **Time-lapse of the light** (the 2.2 s clip, scrubbed by wall-clock): shadows swing, haze thickens. A **time-slice wipe** runs along the shoreline from the south (dawn) to the north (midnight), with a soft 120 px mask feather. | same as #2 | 28 mm | Camera static. The wipe front advances along the S-curve, inOutCubic. | "Each stretch of coast is a different hour." |
| 4 | 3.0–3.8 | The sun-arc hairline draws left to right (right to left in RTL). Its marker **travels with the wipe front**, and each of the 5 icons pops in (scale 0.8→1, outCubic, 180 ms) as the wipe crosses its stretch. | — | — | UI only | "The arc is the map." |
| 5 | 3.8–5.4 | Home time-slice. A 1.2 s breathing glint (opacity 0→0.6→0) on each of the 5 tap zones in turn, 240 ms each, from the south. | (−400, −900, 420), pitch −22° (end of push-in) | 28 mm | Push-in completes | "These are tappable." |
| 6 | 5.4–6.0 | Header icons and the dock come to 100% (outCubic, 300 ms). Input is live from 5.4 s. | static | 28 mm | — | — |

- **Phone version:** the same timing on a separately composed vertical still. Camera (−260, −720, 540), pitch −30°, heading 8°, 28 mm on the rotated sensor (vFOV 65.5°). The coast S-curve runs bottom to top, so the wipe also runs bottom to top. Assets: 110 KB AVIF still plus a 1.1 s, 720×1280 light time-lapse of about 0.5 MB, streamed. If the time-lapse is not there by 1.6 s, the wipe runs over the still alone.

## 2. Return visit (1.2 s)
| t (s) | What happens |
|---|---|
| 0.0–0.6 | The Home time-slice still fades from black, scale 1.02→1.00, outCubic. |
| 0.4–0.9 | Arc, icons and dock fade in, outCubic. The arc marker sits on the hour of the visitor's last room, but the **camera is always Home** (Shay's rule). |
| 0.6 | Input live. Total 1.2 s; the last 0.3 s is a static hold. |

## 3. Camera language per state
The world is pre-rendered footage. "Camera" here means the Blender camera of each clip, plus a live ±1.5° look-around done as a 2D offset of the plate. **Render every plate with 4% overscan** so the offset never shows an edge.

| State | Position / height | Lens | Move type | Easing | Duration |
|---|---|---|---|---|---|
| **Home** (time-slice) | (−400, −900, 420), 420 m up, pitch −22° | 28 mm (phone 28 mm rotated) | Static still. Look-around ±1.5° yaw / ±0.8° pitch via a 2D offset, following the mouse or gyro with a 0.25 s low-pass. | snap | idle |
| **Home → field** (tap a stretch or arc icon) | Ends at the field's **first room**, at eye height | 28 → room lens, changing only in the last 35% of the move, in the same direction as the dolly | One pre-rendered **descending dolly along the line of sight** (mostly forward expansion, little sideways flow). Heading change ≤ 20°. Pitch −22° → −3°. | inOutCubic | 1.6 s (clip, 39 frames at 24 fps) |
| **Field → field** (scrub) | The **rail**: 30 m up, 60 m inland, parallel to the shore | 35 mm | Truck along the rail, played back by the scrub position (time-lapse sky). Rise from the room to the rail and descent at the end are part of each segment. | follows input; snap at the end | about 1.0 s of footage per room-stop at a calm scrub |
| **Entering a room** (next room in the same field) | Eye height 1.6 m (portraits 1.5 m, surf 1.8 m on a dune) | Room lens, below | **Orbit ≤ 20°** around the field's pivot, plus a time advance. Rooms of one field are laid out on an arc, not a line, so there is no fast truck at eye height. | inOutCubic | 1.0 s |
| **Photo opens** (tap the room or Enter) | Camera static | — | The plate dims to 35% and blurs (12 px at 1080p). The print rises 4% from below and scales 0.96→1.00 on the ivory mount, 70% of viewport width (landscape) or 88% (portrait). | outCubic | 450 ms |
| **Photo → photo** | static | — | The outgoing print slides 6% and fades. The incoming print slides in from 6% on the opposite side. The world does **not** move; time stays paused at the room's minute. | outCubic in / inCubic out, with a 60 ms overlap | 280 ms |
| **Home in one tap** | → Home | → 28 mm | **No rendered reverse clip** (H.264 reverse seeking is unreliable). A two-layer pull-back: the current frame scales 1.00→0.94 and fades out, while the Home still scales 1.06→1.00 and fades in. | inOutCubic | 0.7 s |

Room lenses and minutes. The room order is kept, and the minutes are **re-timed** (see risk 1):

| Field | Rooms (order kept) | Minute(s) | Lens | Height | Framing note |
|---|---|---|---|---|---|
| Surfing | Surfing | 06:10 | 135 mm | 1.8 m on a dune | Wave line on the lower third, low sun from the land. |
| Festivals | FreeEarth, Ozora, Zoodana, Goaland, Bardak, Hippietipi, Sounds of Love | 10:00, 11:15, 12:30, 13:45, 15:00, 16:15, 17:30 | 35 mm | 1.6 m | Canopy on the left or right third. The next canopy is visible out of focus in the background as a leading element. |
| Portraits & Branding | Mayu, Maya, Amit, Shira, Eden, Noa | 18:00, 18:12, 18:24, 18:36, 18:48, 19:00 | 85 mm | 1.5 m | Backlit pine edge, sun 2–6° high and behind. |
| Sport | Football (Maccabi TA), Basketball (Maccabi Rishon), Reservists League | 20:15, 21:00, 21:30 | 50 mm (stadium from the stand at 8 m), 35 mm (hall) | 8 m / 1.6 m | Floodlight masts on the thirds. |
| Video | Showreel | 00:00 | 28 mm | rail, 30 m | Long-exposure still of the whole day. Tap plays the 12 s replay, then cuts to the reel. |

## 4. Input mapping
The scrub coordinate is **s = room-stop index 0…18** (surf = 0, video = 18). Each room-stop costs the same effort, so a field with 7 rooms is not 7 times harder to cross than its clock span suggests.

| Action | Desktop | Phone |
|---|---|---|
| Move time / travel | Wheel or trackpad: 120 px of deltaY = 0.25 stop. Horizontal drag: 240 px = 1 stop. Inertia with friction 0.92 per frame. After 180 ms with no input, `snap` to the nearest stop. | **Vertical swipe**: 0.6 × viewport height = 1 stop. A flick (> 0.8 px/ms) adds at most **one** extra stop, so a flick cannot fly over three fields. |
| Next / previous room | → / ← (in RTL the arrows follow the visual direction of the arc) | Tap the ‹ › chevrons, 44 px, beside the arc |
| Jump to a field | Click an arc icon, or keys 1–5 | Tap an arc icon |
| Open the room's photos | Click the room, or Enter | Tap the room |
| Next / previous photo | ← →, or the wheel (the wheel does **not** scrub time while the viewer is open) | Horizontal swipe |
| Close the viewer | Esc, or click outside the print | Swipe down, or the ✕ (44 px) |
| Home | Camera icon top-left (top-right in RTL), or H | Camera icon |
| Look-around | Mouse position, ±1.5° | Gyro ±1.5°, only after an explicit tap on "motion" (iOS permission). Otherwise off. |
| Speed cap | Visual travel ≤ 2 stops/s. Faster input queues and decelerates. | same |

Wheel down / swipe up always means **later in the day**, in both LTR and RTL. Only the visual direction of the arc flips.

## 5. Motion sickness and reduced motion
| Variant | Trigger | What changes |
|---|---|---|
| **Default** | — | The limits in §0. The time-lapse sky is rendered at ≤ 12° of cloud travel per second of footage. |
| **Comfort** (toggle in the ⚙ sheet, remembered) | The visitor chooses it | Scrub speed capped at 1 stop/s. Home→field becomes a 0.6 s plate cross-fade plus a 0.5 s still settle, with no flight. Look-around and gyro off. A 6% dark vignette during travel. |
| **Reduced motion** | `prefers-reduced-motion: reduce` (or Comfort+ in the sheet) | **No footage plays at all.** Every stop is a still. The scrub steps stop by stop with a 400 ms cross-fade. The intro is the Home still, fading in over 400 ms with the arc already drawn, 0.8 s total. Photo→photo is a 200 ms opacity cross-fade with no slide. The audio clock ambience is off unless the visitor turns it on. |

## 6. Camera keyframe JSON sketch (shared by Blender and three.js)
```json
{
  "schema": "shiko-cam/1",
  "concept": "A-sunline",
  "units": "m", "up": "Z", "fps": 24, "sensor_mm": [36, 24],
  "phone_sensor": "rotated",
  "shots": [
    { "id": "intro_desktop", "duration": 6.0, "ease": "inOutCubic", "plate": "intro_lapse_1600x900.mp4",
      "keys": [
        { "t": 0.5, "pos": [-380, -860, 405], "target": [180, 900, 0], "focal_mm": 28, "roll": 0 },
        { "t": 6.0, "pos": [-400, -900, 420], "target": [180, 900, 0], "focal_mm": 28, "roll": 0 }
      ],
      "tracks": { "wipe_front_s": [[1.6, 0.0], [3.8, 1.0]], "arc_marker": [[3.0, 0.0], [3.8, 1.0]] } },
    { "id": "home_to_festivals_01", "duration": 1.6, "ease": "inOutCubic", "plate": "seg_home_fest01.mp4",
      "keys": [
        { "t": 0.0,  "pos": [-400, -900, 420], "target": [180, 900, 0],   "focal_mm": 28 },
        { "t": 1.04, "pos": [-120, -260, 90],  "target": [60, 140, 2],   "focal_mm": 28 },
        { "t": 1.6,  "pos": [-30, -40, 1.6],   "target": [10, 25, 2.2],  "focal_mm": 35 }
      ],
      "clock": [[0.0, "home"], [1.6, "10:00"]] },
    { "id": "rail_fest07_to_portrait01", "duration": 1.0, "ease": "input", "plate": "seg_f07_p01.mp4",
      "keys": [
        { "t": 0.0, "pos": [240, 610, 1.6], "target": [255, 640, 2.4], "focal_mm": 35 },
        { "t": 0.3, "pos": [230, 600, 30],  "target": [300, 760, 4],   "focal_mm": 35 },
        { "t": 0.75,"pos": [290, 720, 30],  "target": [330, 820, 3],   "focal_mm": 35 },
        { "t": 1.0, "pos": [318, 790, 1.5], "target": [326, 812, 1.6], "focal_mm": 85 }
      ],
      "clock": [[0.0, "17:30"], [1.0, "18:00"]] },
    { "id": "return_home", "duration": 0.7, "ease": "inOutCubic", "type": "2d_pullback",
      "out_scale": [1.0, 0.94], "in_scale": [1.06, 1.0] }
  ]
}
```
- **three.js:** `camera.fov = 2*atan(12/focal_mm)` (phone: 18/focal_mm). Position and target are converted to Y-up. The proxy camera follows the plate frame through `requestVideoFrameCallback` (`metadata.mediaTime × fps` → key interpolation).
- **Blender:** the same keys drive the camera object, with Bezier handles set to the `inOutCubic` tangents. `focal_mm` → `cam.data.lens`, and `clock` → the sun-rig driver.
- The coordinates are placeholders on the planned 3 km S-curve. They will be fixed once the coast layout exists.

## 7. Where a first-time visitor will get confused, and the fix
1. **The clock order in CONCEPTS.md is not monotonic with the fields.** Festivals run 11:00 → 19:40 and portraits sit at 18:30, so scrubbing forward from Sounds of Love would go *back* to the portraits, or the portraits would sit in the middle of the festivals. **Fix:** re-time as in §3. Festivals 10:00–17:30 (75 min steps), portraits 18:00–19:00, sport 20:15–21:30, video 00:00. The time order then equals the field order equals the coast order.
2. **"Time is the map" is abstract (the biggest risk).** A first-timer does not know that 13:45 means Zoodana, so they scrub blind through 18 snaps. **Fix:**
   - The intro wipe and the arc marker teach the mapping (shots 3–4).
   - Every arc icon carries the field name, shown on hover, and always on the phone for the first visit, until the first tap.
   - While scrubbing, a 1-line chip under the arc shows "Festivals · Zoodana · 3/7" (room name first; the clock is secondary and smaller).
3. **Scroll and vertical swipe are repurposed.** Visitors expect scroll to move the page, and on a phone the vertical swipe is time but the horizontal swipe is photos. **Fix:**
   - The canvas has `touch-action: none` and `overscroll-behavior: none`, so there is no pull-to-refresh fight.
   - On the first visit, after 4 s idle on Home, a single 1.2 s hint animates the arc marker one stop forward and back, with a small ↕ glyph. It never shows again after the first scrub.
   - Inside the photo viewer, vertical swipe is **only** "close", never time.
4. **Inertia overshoot across 18 stops.** **Fix:** the flick cap (+1 stop max), the 2 stops/s speed cap and the 180 ms snap. Arrow keys and chevrons always move exactly one room.
5. **RTL.** The arc runs right to left, but "wheel down = later" stays fixed. The ← → keys follow the arc visually: in RTL, ← = later. This is tested as a QA item.

## Verified vs assumed
- **Verified, by reading the repo:** the concept text, room list and order, the skill's rules (≤ 6 s / ≤ 1.5 s, cubic in-out, 0.9–1.6 s, ≤ 70° vFOV), and the research facts (`requestVideoFrameCallback` support, the Lusion plate + proxy pattern). The FOV table is arithmetic.
- **Assumed, not measured:** every coordinate (the coast is not built yet), the scrub constants (120 px, 0.6 vh, friction 0.92), clip sizes, the 4% overscan sufficiency, and the claim that a descending line-of-sight dolly is comfortable at 1.6 s. All of these need an animatic and testing with real users on a phone. No animatic MP4 has been made, because Blender is not to be run now.
