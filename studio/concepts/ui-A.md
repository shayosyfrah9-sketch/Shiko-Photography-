# UI layer: Concept A, SUNLINE (one day of light)
UI/UX designer, 2026-11-24. Concept phase. Images are **Mock-ups** (static HTML, Playwright screenshots), not renders and not a prototype. The world in the screenshots is a placeholder: a real photo (`maya8612`) stands in for the Cycles time-slice.

- Mock-up file: `studio/concepts/ui-mock/A.html` (states: `#home`, `#rooms`, `#viewer`) + `shared.css`
- Screenshots 390×844 @2x: `studio/renders/concepts/A/ui-phone.png` (Home), `ui-phone-rooms.png` (all 18 rooms), `ui-phone-viewer.png` (photo viewer)

## 0. What Shay already approved on the live site (v153, read from index.html)
Verified by reading the code. A headless screenshot of the live page timed out on its WebGL scene, so the live screens were not looked at.
- Hebrew is the default (`<html lang="he" dir="rtl">`), with an EN/עברית toggle. Every label switches language and `dir`.
- Header: the "Shiko PHOTOGRAPHY" wordmark is Home. Desktop tools: מי אני (About), EN, sound, Matcha icon, WhatsApp icon.
- **Phone (≤600 px):** every header tool is hidden behind a hamburger. The menu holds an accordion of the 4 halls with their rooms, then About, Booking, WhatsApp, Matcha, sound and language. **Result: on v153 phones, WhatsApp and booking are 2 taps from Home and cannot be seen in the first 3 seconds.** WORLD 2.0 must fix this.
- Room: Home (house icon) + "Booking ↓"; a 3D / Gallery (grid) toggle; a "Full Gallery ↗" pill that is hidden when the room has no link; a stepper `← 01 / NN →`. The lightbox has ✕ ← → and swipe.
- Booking sheet: "Start My Request →" + WhatsApp (wa.me/972544351955) + Matcha.
- Data facts the UI must handle: 17 photo rooms + Video (empty, "coming soon") = 18. **6 rooms have no full-gallery link** (Maccabi TA, Reservists League, Surfing, Shira, Noa, Eden). Portrait order in the data is Mayu, Maya, Amit, Shira, **Noa, Eden** (CONCEPTS.md lists Eden before Noa: the data wins). Real counts: Shira 42 and FreeEarth 11, not the 24 and 30 in the CONCEPTS mock-up captions.

## 1. Shared shell (identical in A, B and C, so the concepts are compared on their idea only)
| Element | Phone 390×844 | Desktop 1440×900 |
|---|---|---|
| Home | Camera icon + "SHIKO" at the start side (top-right in he, top-left in en). 44×44 target. One tap returns to the concept's Home view from any state. | Same, top start corner |
| Language | `EN` / `עב` text button, header end side. Switches `lang`, `dir`, every label and aria-label, and mirrors the concept's axis. Event names keep their original language (`lang="en"` + `unicode-bidi:isolate` so counts do not jump sides). | Same |
| Sound | Icon, header end. Silent until the first gesture. | Same |
| About, Matcha | In the room-list sheet footer (phone), so the header keeps 3 items | Header text button + Matcha icon, as on v153 |
| **Dock** (always visible, from the first frame, above any intro) | 72 px bar, 3 equal text buttons: **עבודות** (Work → all-rooms sheet) · **הזמנת צילום** (Booking, gold #f3dcb0, underline) · **WhatsApp** (glyph + word, opens wa.me directly). The dock sits in the thumb zone. | Compact centred dock, max 520 px wide, same 3 items; WhatsApp also stays as the header icon, as on v153 |
| Room list | Bottom sheet under the header, above the dock. All 18 rooms as 40 px chips with photo counts, grouped by the concept's own axis; it fits one phone screen without scrolling (verified in the screenshot) | A side panel on the end side, 360 px |
| Photo viewer | Header + dock stay. Title row (room · field) + ✕ (back to the room's place in the world). Photo front-parallel on a 4 px ivory mount at true aspect ratio (no crop). `→ 02 / 25 ←` (in RTL "next" points left), 44 px buttons. "Full gallery ↗" only when the room has a link, else "All N in a grid". Swipe or ←/→ keys. | Photo ≤ 70% of the viewport width/height, arrows beside it, the same links under it |

## 2. Concept A interface
**Field switcher = the sun-arc.** A hairline arc under the header with 5 labelled marks in clock order: גלישה 06:10, פסטיבלים 11:00, פורטרטים 18:30, ספורט 20:15, וידאו 00:00. In Hebrew dawn is on the right and time runs right→left; in English it is mirrored. The current hour reads large (Jost 300, "18:42") with a plain-language line under it: "שעת זהב · פורטרטים ומיתוג". The marks carry **text labels**: the concept's icon-only marks do not pass the 3-second test (see §3).

**Phone.** A vertical swipe scrubs time; a tap on an arc mark jumps there; a tap on a pinned room label in the world ("Maya Portraits · 25 תמונות") enters the room. A hint above the dock teaches the gesture once ("↕ גללו כדי להזיז את השמש · הקישו על נקודה כדי לקפוץ") and hides after the first scrub. The room list groups the rooms by hour (06:10 Surfing / 11:00–19:40 the 7 festivals / 18:30 the 6 portrait sets / 20:15 the 3 sport rooms / 00:00 Video).
**Desktop.** The arc is centred at the top (max 720 px). Wheel, horizontal drag or ←/→ scrub with inertia and snap to each room's minute. Room labels show on hover along the coast.
**Viewer.** Time pauses ("⏸ הזמן עצר ב־18:42" under the title). The world behind is dimmed to 35% and blurred, and its colour never touches the photo.
**Booking.** The dock button opens the v153 booking flow. Its first question is "Which light?" (dawn / day / golden / night), and it can be skipped. WhatsApp is never behind the question.

## 3. 3-second test (first-time phone visitor)
Method: expert walkthrough of the mock-up and the concept text. **Not tested with real users.**
| Goal | As written in CONCEPTS.md | With this UI layer (mock-up) |
|---|---|---|
| See work | **Fail.** The arc and its icons appear only at 4 s, and the marks are unlabelled icons. | **Pass.** Labelled arc + "עבודות" in the dock from the first frame |
| Booking | **Fail.** It appears at 4 s with the arc. | **Pass.** Gold dock button, thumb zone |
| WhatsApp | **Fail.** It appears at 4 s. | **Pass.** Dock, word + glyph, one tap to wa.me |
Required change to the concept: the dock is painted with the first frame (over the intro), and the arc marks get words.

## 4. Accessibility
- **Keyboard:** Tab order is header (Home, sound, language) → arc marks (as buttons, `aria-current` on the active hour) → pinned room labels → dock. ←/→ steps between room minutes, Home/End go to dawn/midnight, Enter enters, Esc leaves the viewer or sheet, ←/→ moves photos inside the viewer. Visible 2 px gold focus ring. The wheel scrubs only while the pointer is over the canvas; there is no global scroll hijack.
- **Screen reader:** the video/canvas is `aria-hidden`. A real DOM `<nav aria-label="תחומים לפי שעה ביום">` mirrors the arc. The hour readout is an `aria-live="polite"` region, announced only on snap (not every frame). The viewer is `role="dialog"`, with "Maya Portraits, תמונה 2 מתוך 25" and alt text per photo. Every aria-label is in the active language.
- **Contrast (measured** on the mock-up against the brightest 5% of background pixels behind each text run): with the top scrim, the minimum is 8.1:1 on Home and 4.8:1 on the viewer hint. **Without the scrim, the "18:42" readout over a bright sky measured 1.2:1, a hard fail.** A therefore needs a permanent top scrim (≈ 80% ink over the top third), and it must hold at noon over white sand, the worst hour.
- **Reduced motion:** no time-lapse flight. 400 ms cross-fades between the hour stills, the arc sun jumps, there is no inertia, and Video does not autoplay.
- Targets: all controls ≥ 44 px tall except the arc marks (≈ 66×56 px: OK). No horizontal page scroll (checked).

## 5. Concrete UX weaknesses
1. **Scroll hijack (top risk).** On a phone the vertical swipe *is* the time scrub. People swipe to "scroll the page" and will fly through the day, overshooting 7 festival minutes packed between 11:00 and 19:40 (≈ 1 snap per 75 min of day, a few mm of thumb travel). Mitigation: strong magnetic snaps, one room per swipe, and the tappable arc as the main method.
2. **18 rooms on one axis.** Festivals need 7 snaps but surfing gets 1, so the arc is uneven, and portraits (18:30) sit between festivals that run until 19:40, so the clock order and the data order collide. The room list sheet has to carry the real navigation.
3. **UI over a changing sky.** The UI colour is fixed while the world goes from white noon to black midnight. Text is legible only with a scrim that darkens the very image the concept sells (visible in ui-phone.png: the top third is dimmed).
4. **Colour shifts across the day** could read as the "colour takeovers" Shay dislikes, especially in the transitions between rooms.
5. **"Which light?" in booking** is charming but adds a step for a lead who just wants to book. It must be skippable, and WhatsApp must never sit behind it.
6. **Segment streaming:** scrubbing far ahead (e.g. tapping 00:00) lands on a segment that has not loaded. It needs a still frame for each room minute as an instant fallback.
