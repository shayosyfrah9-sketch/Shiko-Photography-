# Camera plan B: DEPTH OF FIELD (the focus ring is the map)
Cinematic director, 2026-11-24, branch `world2-dev`. Text only: nothing was rendered or prototyped for this file (Blender not run). All frames are **plans** for Rendered layers and Mock-ups.

The conventions (units, lens→FOV table, easing names, comfort limits, skip and return rules) are in `camera-A.md` §0 and apply here unchanged.

## 0. What "camera" means in B
The camera **never translates**. Every move is a lens behaviour: **focus distance, aperture, breathing, drift and parallax.** The shot list is therefore mostly a focus-pull list.

- **Fixed camera.**
  - Desktop: (0, 0, 1.55), heading 270° (west, downhill), pitch −6°, 50 mm, so vFOV 27.0°.
  - Phone: a separate vertical composition from the same spot. Pitch −9°, 35 mm on the rotated sensor, vFOV 54.4°. The wider lens is needed so the ledge, the meadow, the stadium and the sea all stack vertically.
- **The ring.** Ring position `u` runs from 0 to 4, with detents at:

  | u | Distance | Diopters | Field |
  |---|---|---|---|
  | 0 | 1.5 m | 0.667 D | Portraits & Branding |
  | 1 | 12 m | 0.083 D | Festivals |
  | 2 | 120 m | 0.0083 D | Sport |
  | 3 | ∞ (3000 m) | 0 D | Surfing |
  | 4 | "past ∞" | — | Video |

  Distance = 10^(piecewise-linear log10) between detents, so each detent costs the same effort. A real ring is roughly logarithmic too.
- **Blur per layer.** Diameter in px = K · |1/d_layer − 1/d_focus| · g.
  - Physical K at 50 mm f/1.4 is about 127 px per dioptre at 2560 px width. On the phone it is about 58 px per dioptre at 1170 px with 35 mm.
  - g is an **artistic gain**: 1.0 for layers in front of the focus and 3.0 for layers behind it. Diameter is capped at 96 px (the top of the mip stack).
  - The gain matters because physics alone is too weak for far planes. Focused at 12 m, the stadium would only get about 9.5 px of blur. Focused at 120 m, the meadow would only get about 9.5 px. Without the gain, the far fields barely separate (see risk 2).
- **Breathing.** Magnification 1.000 at ∞, 1.020 at 1.5 m, linear in dioptres. Scaled around the frame centre.
- **Drift.** ±0.3° handheld drift: two summed sines at 0.11 Hz and 0.17 Hz on yaw and pitch. Off in reduced motion.
- **Parallax.** ±1.5% from the mouse or gyro, applied per layer in proportion to (1/d_layer). The ledge moves the most and the sea does not move.

## 1. First-visit intro (6.0 s, skippable)
| # | t (s) | Shot | Ring / aperture | Easing | Learns |
|---|---|---|---|---|---|
| 1 | 0.0–0.8 | Black → **pure bokeh frame**: a 40 KB pre-blurred plate, focus at 0.3 m, f/1.2. Floodlight, string-light and sea-glint discs. The ivory camera mark sits low-centre. | focus 0.3 m | outCubic fade, 600 ms | Mood; this is also the loader. |
| 2 | 0.8–2.0 | Hold the bokeh. The discs breathe in scale 1.00→1.015, and the sharp layers stream behind. | — | inOutCubic | — |
| 3 | 2.0–2.6 | Focus pulls to **∞**: the sea and the surf line snap sharp. The scale mark "∞" with the surf icon fades in at its position on the bottom scale. | u 3.0, f/1.4 look | inOutCubic, 0.4 s pull + 0.2 s dwell | ∞ = surf |
| 4 | 2.6–3.2 | → **120 m**: the stadium crown, with the sport icon mark. | u 2 | same | 120 m = sport |
| 5 | 3.2–3.8 | → **12 m**: the canopies, with the festival icon mark. | u 1 | same | 12 m = festivals |
| 6 | 3.8–4.5 | → **1.5 m**: the portrait set on the ledge, with the portrait icon mark. The meadow and the sea melt. | u 0 | same, 0.45 s pull | 1.5 m = portraits |
| 7 | 4.5–5.4 | **Hyperfocal Home**: everything sharp. The full distance scale (1.5 · 12 · 120 · ∞ · ▶) is complete, and the ▶ "past ∞" video mark draws last with a small play glyph. | all sharp (cross-fade of blur → 0) | inOutCubic, 0.7 s | Home = all sharp |
| 8 | 5.4–6.0 | Header icons and dock to 100%. One **focus-peaking shimmer** sweeps each plane, near to far, 120 ms each. Input is live from 5.4 s. | — | outCubic | "These planes are choosable." |

- **Network rule.** The intro clock starts when the 40 KB bokeh frame paints. If the sharp layers are not decoded by 2.0 s, shot 2 holds for up to **+1.5 s** and then continues with whatever layers exist. Missing layers stay blurred, which is honest because they are out of focus. The intro is never longer than 7.5 s from first paint, and the skip works from the start.
- **Phone.** The same shot list on the vertical composition. Audio stays silent (browser policy), so the focus-driven ambience starts only after the first gesture.

## 2. Return visit (1.0 s)
| t (s) | What happens |
|---|---|
| 0.0–0.3 | The bokeh frame (from cache). |
| 0.3–0.8 | A single focus pull to hyperfocal, with no stops at the planes. inOutCubic. |
| 0.5–0.9 | Scale and dock fade in. |
| 0.6 | Input live. |

## 3. Camera (lens) language per state
| State | Ring / aperture | Image behaviour | Easing | Duration |
|---|---|---|---|---|
| **Home** (hyperfocal) | All layers blur 0. Breathing 1.000. | Drift and parallax on. A faint peaking shimmer on hover, desktop only. | — | idle |
| **Moving to a field** (focus a plane) | Ring to the detent. Look of f/1.4: blur by the formula in §0. The unfocused planes also drop **−0.3 EV**, so the chosen field reads even where physics blurs it weakly. | Breathing follows the ring. The field's **room prints** (true-ratio cards, 28–60 px tall) rise 6 px and fade in, in their stored order. In RTL the order is mirrored. | inOutCubic on `u` (not on distance) | 0.9 s for one detent. +0.25 s per extra detent, max 1.4 s (1.5 m → ∞). |
| **Entering a room** (tap a print) | Focus goes to **0.3 m, f/1.2**: nothing in the world is sharp. Bokeh discs tint 10–15% toward the photo's palette over 600 ms. | The print flies forward on the ivory mount and settles front-parallel. Landscape: 64% of viewport height for portrait-format photos, 70% of width for landscape-format photos. Phone: 88% of width. Drift off while viewing (the skill's rule: nothing moves near a viewed photo). | outCubic | 0.7 s |
| **Photo → photo** | unchanged | Slide 4% + cross-fade. The bokeh tint re-targets to the new photo's palette over 600 ms (in parallel). | outCubic / inCubic, 60 ms overlap | 260 ms |
| **Video** (past ∞) | Ring past ∞ to u = 4 | The vista comes alive: a 6 s 720p loop fades in over the static plate (0.6 s). Then a 1.2 s cross-dissolve into the showreel player (HTML). | inOutCubic | 0.6 + 1.2 s |
| **Home in one tap** | From any state, the ring goes to hyperfocal. The viewer print shrinks back into its plane slot. | — | inOutCubic | 0.6 s |

## 4. Input mapping
| Action | Desktop | Phone |
|---|---|---|
| Turn focus (choose a field) | **Wheel or trackpad**: 120 px of deltaY = one detent. Continuous between detents, snapping after 150 ms idle. Wheel down = farther, the way a lens turns toward ∞. ↑ / ↓ = farther / nearer. Keys 1–5 jump to a detent. Clicking a scale mark does the same. | **Tap a plane** = focus there. A depth-map lookup gives the plane, the gesture everyone knows from their phone camera. **Tap a scale mark** = the same. A vertical swipe on the scale strip (not the whole canvas) gives fine focus: 18% of viewport height = one detent. |
| Open a room | Click a print. In a focused plane, ← → move a highlight across the prints and Enter opens. | Tap a print (only inside the focused plane; see risk 3) |
| Next / previous photo | ← → or the wheel (the wheel does not turn the ring while the viewer is open) | Horizontal swipe |
| Back to the plane | Esc, or a click on the bokeh | Swipe down, or ✕ |
| Home | Camera icon or H. A double-click on empty canvas also works. | Camera icon |
| Video | Wheel past ∞ (one more detent), key 5, or the ▶ mark | Tap ▶ on the scale |
| Parallax | Mouse position ±1.5% | Gyro ±1.5% after an explicit opt-in tap. Otherwise off. |

## 5. Motion sickness and reduced motion
B is the lowest-risk concept because there is no travel. Its risks are **flicker and pulsing** (fast blur changes, breathing) rather than vection.

| Variant | Trigger | What changes |
|---|---|---|
| **Default** | — | Blur may change by at most 48 px of diameter per 100 ms (no strobing on fast wheel spins). Breathing ≤ 2%. Drift ±0.3°. |
| **Comfort** | ⚙ toggle | Breathing 0, drift 0, parallax 0. Focus pulls 1.1 s. The bokeh tint is instant at 40% strength. |
| **Reduced motion** | `prefers-reduced-motion` | **Five pre-composed focus states** (hyperfocal + 4 planes), plus the video poster. 300 ms opacity cross-fade between them, no animated blur, no breathing, drift or gyro. The intro is the bokeh frame → a 300 ms cross-fade to hyperfocal, 0.8 s total. The viewer opens with a 200 ms fade, and the video does not autoplay (a tap plays it). |

## 6. Camera keyframe JSON sketch
```json
{
  "schema": "shiko-cam/1",
  "concept": "B-depth-of-field",
  "units": "m", "up": "Z", "fps": 24, "sensor_mm": [36, 24],
  "camera": {
    "desktop": { "pos": [0, 0, 1.55], "target": [-100, 0, -9.0], "focal_mm": 50 },
    "phone":   { "pos": [0, 0, 1.55], "target": [-100, 0, -14.3], "focal_mm": 35, "sensor": "rotated" }
  },
  "ring_detents": [
    { "u": 0, "focus_m": 1.5,  "field": "portraits" },
    { "u": 1, "focus_m": 12,   "field": "festivals" },
    { "u": 2, "focus_m": 120,  "field": "sport" },
    { "u": 3, "focus_m": 3000, "field": "surfing" },
    { "u": 4, "focus_m": null, "field": "video", "past_infinity": true }
  ],
  "blur": { "k_px_per_dioptre": { "desktop": 127, "phone": 58 }, "gain_behind": 3.0, "gain_front": 1.0, "max_px": 96, "unfocused_ev": -0.3 },
  "layers_m": { "ledge": 1.5, "pine_bough": 0.9, "meadow": 12, "canopies": 18, "stadium": 300, "sea": 3000 },
  "shots": [
    { "id": "intro", "duration": 6.0, "ease": "inOutCubic", "track": "focus",
      "keys": [
        { "t": 0.0, "focus_m": 0.3,  "fstop": 1.2, "breath": 1.0 },
        { "t": 2.0, "focus_m": 0.3,  "fstop": 1.2, "breath": 1.015 },
        { "t": 2.4, "focus_m": 3000, "fstop": 1.4 },
        { "t": 3.0, "focus_m": 120,  "fstop": 1.4 },
        { "t": 3.6, "focus_m": 12,   "fstop": 1.4 },
        { "t": 4.25,"focus_m": 1.5,  "fstop": 1.4, "breath": 1.02 },
        { "t": 5.2, "focus_m": "hyperfocal", "fstop": 11, "breath": 1.0 }
      ] },
    { "id": "focus_festivals", "duration": 0.9, "ease": "inOutCubic", "track": "focus",
      "keys": [ { "t": 0, "u": "current" }, { "t": 0.9, "u": 1 } ] },
    { "id": "open_print", "duration": 0.7, "ease": "outCubic", "track": "focus",
      "keys": [ { "t": 0, "u": "current" }, { "t": 0.7, "focus_m": 0.3, "fstop": 1.2 } ],
      "palette_tint": { "amount": 0.12, "duration": 0.6 } }
  ]
}
```
- **Blender:** the same camera renders each layer in its own view layer. The focus keys drive `cam.data.dof.focus_distance` and `aperture_fstop`, which is used only for the reference frames (key frame 2) that the shader blur must match.
- **three.js:** a fixed `PerspectiveCamera`. The focus tracks drive the shader uniforms `uFocusD` (dioptres), `uGainBehind` and `uBreath`.

## 7. Where a first-time visitor will get confused, and the fix
1. **Nothing looks clickable, and scroll "breaks" the picture (the biggest risk).** The visitor lands on one still, sharp photograph with no motion and no path. If they scroll as they would on any page, the image blurs, which reads as "loading" or "broken", not as "I chose a field".
   **Fix:**
   - The distance scale shows **field icons + names**, not metres. Metres are a small secondary line ("1.5 m") for photographers.
   - The first wheel or tap on a plane always lands **on a detent** with its prints rising and a 1-line chip ("Festivals · 7 rooms"). The visitor never sees an in-between blur state on the first interaction.
   - The intro's planes-to-icons sequence (shots 3–7) plus the closing peaking shimmer teaches the mapping.
2. **Far fields are hard to tell apart.** Physically, focusing at 120 m versus ∞ changes very little: about 9.5 px on a 2560 px frame. **Fix:** the 3× behind-gain, the −0.3 EV on unfocused planes, and the field chip. Art-critic gate: in a side-by-side, the "sport focused" and "surf focused" frames must be tellable apart at phone size.
3. **Mis-taps on the phone.** In a 390 px wide frame, 7 festival prints at 12 m are about 30 px tall and sit near the 1.5 m set. **Fix:**
   - Two-step on the phone: the first tap focuses a plane. Only prints in the **focused** plane are tappable, with hit areas expanded to at least 44 × 44 px.
   - When a plane is focused on the phone, its prints are mirrored in a bottom strip of true-ratio thumbnails, 64 px tall and horizontally scrollable, as a reliable fallback.
4. **Video is hidden "past ∞".** A non-photographer will never turn past infinity. **Fix:** the ▶ mark is a visible, labelled end of the scale, and Video also has a header icon.
5. **Fine-focus swipe against page and system gestures.** **Fix:** the vertical swipe works only on the scale strip, and the canvas uses `touch-action: manipulation` so double-tap zoom does not fire. Pull-to-refresh is disabled with `overscroll-behavior: none`.

## Verified vs assumed
- **Verified:** the concept text, room order, the skill rules, and the FOV and CoC arithmetic. K is computed from f²/N for 50 mm f/1.4 on a 36 mm sensor at 2560 px, and the result is the physical reason for the gain.
- **Assumed:** the layer distances (the scene is not modelled), the 3× gain and −0.3 EV values, the swipe and wheel constants, the 40 KB bokeh frame size, and the hit-area numbers. All need a prototype check on a 390 px phone. No animatic has been made.
