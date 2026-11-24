# UI layer: Concept B, DEPTH OF FIELD (the focus ring is the map)
UI/UX designer, 2026-11-24. Concept phase. Images are **Mock-ups** (static HTML, Playwright screenshots). The world is a placeholder: a real photo (`goa0413`, Goaland stage) stands in for the Cycles ridge view.

- Mock-up file: `studio/concepts/ui-mock/B.html` (states `#home`, `#rooms`, `#viewer`) + `shared.css`
- Screenshots 390×844 @2x: `studio/renders/concepts/B/ui-phone.png`, `ui-phone-rooms.png`, `ui-phone-viewer.png`
- v153 baseline and data facts: see `ui-A.md` §0 (the phone hides WhatsApp/booking behind the hamburger; 6 rooms have no full-gallery link; Noa comes before Eden).

## 1. Shared shell
The same as A (`ui-A.md` §1): Home = camera + SHIKO at the start side; EN and sound at the end side; the dock **עבודות · הזמנת צילום · WhatsApp** is visible from the first frame; an all-rooms sheet; a true-ratio viewer on an ivory mount.
**Change from the concept:** CONCEPTS.md puts booking + WhatsApp as two icons top-right. On a phone that is the hardest corner to reach with the thumb and it competes with the language button, so they move to the dock. On desktop they can also sit in the header, as on v153.

## 2. Concept B interface
**Field switcher = the lens distance scale.** A ruler above the dock with 5 labelled stops. In Hebrew near is on the right: `1.5 m פורטרטים · 12 m פסטיבלים · 120 m ספורט · ∞ גלישה · ∞› וידאו`. A gold `H` caret marks hyperfocal (= Home, everything sharp). Each stop is a 48 px button. Distances are written in Latin digits with `m`, isolated as LTR runs.
**Focus labels in the world** ("peaking labels"): on Home every plane has a small dark label at its own height in the frame (surfing near the horizon, sport above the middle, festivals in the middle, portraits low). This is the only way a first-time visitor learns *where to tap*. A one-line tip at the top, "הקישו על מה שתרצו לחדד", fades after the first focus.
**Phone.** Tap anywhere to focus that plane (the phone-camera gesture). A vertical swipe is fine focus. When a plane is in focus, its rooms appear as small prints in the plane (e.g. the 7 festival canopies, mirrored order in Hebrew); a tap opens the viewer. Swipe down in the viewer returns to the plane. The room list groups the rooms by distance (1.5 m portraits ×6, 12 m festivals ×7, 120 m sport ×3, ∞ surfing, past ∞ video).
**Desktop.** The wheel is the focus ring with detents; keys 1–5 and ↑/↓ jump between stops; hover shows focus peaking plus the plane's label; the scale is centred at the bottom, 640 px wide.
**Viewer.** The world drops to f/1.2 (pure bokeh, in the mock a 22 px blur at 40% brightness) and leans 10–15% toward the photo's palette. The photo itself is never tinted.
**Video** = turning past ∞. It also has its own stop on the scale, so nobody has to discover "past infinity" by accident.

## 3. 3-second test (first-time phone visitor)
Expert walkthrough, **not tested with users.**
| Goal | As written | With this UI layer |
|---|---|---|
| See work | **Fail.** The first 2–4.5 s are pure bokeh (nothing recognisable), the scale only fades in at 4.5 s, and "focus" is not a known way to navigate | **Pass (conditional).** The dock "עבודות" is visible at 0 s; the plane labels + scale tell you where the fields are. The scene itself still shows no photograph until you focus |
| Booking | Pass (icons top-right, "always visible") but icon-only, top-right corner | **Pass.** Dock, gold, words |
| WhatsApp | Pass (icon) | **Pass.** Dock |
Required change: the bokeh intro must not hide the dock, and the planes need written labels on Home.

## 4. Accessibility
- **Keyboard:** Tab → header → the 5 scale stops (a `role="group"` named "טבעת המיקוד. עכשיו: הכול חד"; each stop is a button with `aria-pressed`) → the prints in the focused plane → dock. 1–5 / ↑↓ change focus, Enter opens a print, Esc goes back one level (viewer → plane → hyperfocal). The wheel is bound only over the canvas.
- **Screen reader:** the canvas is `aria-hidden`. The planes are mirrored as DOM buttons ("פסטיבלים, 12 מטר, 7 חדרים"). A focus change is announced once via a polite live region ("בפוקוס: פסטיבלים"). Ambient sound mixed by focus is decorative and is never the only cue.
- **Contrast (measured):** the minimum is 5.1:1 (header "EN" over the stage). The `H` caret measured 3.5:1, but that is a measuring artefact (its own gold triangle sat under the text box); by eye it is gold on ≥ 82% ink. The scale needs an ≥ 82% ink gradient behind it: at 60% the gold caret fell under 4.5:1 over a bright stage.
- **Reduced motion:** no rack-focus animation, a 300 ms cross-fade between 5 pre-composed focus states, no breathing, no handheld drift, gyro off.
- Targets: scale stops 72×48 px, plane labels 40 px tall (raise to 44 in the build). No horizontal scroll (checked).

## 5. Concrete UX weaknesses
1. **Abstract navigation (top risk).** "Turn the focus to choose a field" is a photographer's idea. A non-photographer sees one pretty picture with nothing to press. Without the written plane labels and the dock it fails the 3-second test. With them, the signature gesture becomes optional, which partly dilutes the concept.
2. **Tiny targets in the focused plane.** 7 festival prints in one plane on a 390 px screen are ≈ 40 px each, side by side: under the 44 px target and easy to mis-tap. Use a horizontal strip of larger prints, or open the room list for that plane.
3. **Ambiguous taps.** Tap-to-focus where planes overlap (a canopy in front of the stadium) picks the wrong plane. It needs generous, depth-ordered hit regions and a visible reticle that shows what was chosen.
4. **Swipe-down to go back** fights pull-to-refresh and browser chrome on phones: it needs `overscroll-behavior: none`, and ✕ must remain the main way back.
5. **One fixed view** can feel small and repetitive by the third room ("where is the *world*?"). Shay asked for a world.
6. **Video past ∞** is undiscoverable except through the scale stop, so the stop is mandatory.
