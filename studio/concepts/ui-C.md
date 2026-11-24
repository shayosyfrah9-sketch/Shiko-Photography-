# UI layer: Concept C, WHERE HE STOOD (the held moment)
UI/UX designer, 2026-11-24. Concept phase. Images are **Mock-ups** (static HTML, Playwright screenshots). The world is a placeholder: a real photo (`sol0177`, sun-lit stones, no people) stands in for the Cycles tidal flat.

- Mock-up file: `studio/concepts/ui-mock/C.html` (states `#home`, `#rooms`, `#viewer`) + `shared.css`
- Screenshots 390×844 @2x: `studio/renders/concepts/C/ui-phone.png`, `ui-phone-rooms.png`, `ui-phone-viewer.png`
- v153 baseline and data facts: see `ui-A.md` §0.

## 1. Shared shell
The same as A (`ui-A.md` §1): Home = camera + SHIKO at the start side; EN and sound at the end side; the dock **עבודות · הזמנת צילום · WhatsApp** is visible from the first frame; an all-rooms sheet; a true-ratio viewer.

## 2. Concept C interface
**Field switcher = footprints in the world.** Each held moment has a pair of footprints. On a phone, **every footprint carries a small dark label** with the field and its room count (גלישה 1 חדר · ספורט 3 · פסטיבלים 7 · פורטרטים ומיתוג 6 · וידאו "הזמן ממשיך"). The concept wants purely diegetic marks (no glowing markers), but at 390 px raked-light footprints are a few pixels wide and invisible, so the labels are required. A 6th, gold dashed mark, **"הרגע שלך · הזמנת צילום"**, is the empty vantage that opens booking.
**Phone.** Tap a footprint → a 1.2 s glide to Shay's vantage → the "click" registers the cover photo → tap to open the viewer. Inside a field a horizontal swipe circles to the next vantage (the next room: the 7 festivals in a ring, in data order). The gyro gives look-around, and only after an explicit button (iOS needs a permission prompt; never on load). The room list groups the rooms by held moment.
**Desktop.** Click footprints; ←/→ circles the vantages of a field, ↑/↓ changes field; drag looks ±25°; the wheel dollies back to the overview.
**Viewer.** Flattened print on the ivory mount, `01 / 07`, ←/→. A swipe up (or the button "↑ גב התמונה: למה עמדתי כאן") turns the print over to the back: Shay's line, place, time, shutter speed. Surfing has no full-gallery link in the data, so the viewer shows "כל 7 ברשת" plus a quiet note instead of a dead link (shown in the mock).
**Video** = time resumes for 5 s, then the showreel. Only one video decodes at a time.

## 3. 3-second test (first-time phone visitor)
Expert walkthrough, **not tested with users.**
| Goal | As written | With this UI layer |
|---|---|---|
| See work | **Fail.** The field icons fade in at 5 s; the footprints are diegetic and unlabelled; the people are deliberately missing, so the opening shows *no* photo and no person | **Pass (conditional).** Labelled footprints + the dock "עבודות" at 0 s. Still no photograph is visible on Home: the work appears only after the click |
| Booking | **Fail.** It fades in at 5 s | **Pass.** Dock + "הרגע שלך" |
| WhatsApp | **Fail.** It fades in at 5 s | **Pass.** Dock |
Extra risk: on a mid-range phone the real-time scene may not be interactive at 3 s at all. The dock is plain HTML and must not wait for WebGL.

## 4. Accessibility
- **Keyboard:** Tab → header → the field marks (DOM buttons positioned over the canvas, in data order, not screen order) → dock. ←/→ and ↑/↓ as on desktop; Enter = take the shot / open; Esc = rise back to the overview. Drag-to-look has no keyboard need: it is decorative.
- **Screen reader:** the canvas is `aria-hidden`. The marks are buttons ("פסטיבלים, 7 חדרים, רגע קפוא: חופה וקונפטי"). Arrival at a vantage is announced ("עומדים איפה ששי עמד: FreeEarth"). The back of the print is real text, and it is the best alt text of the three concepts (place, time, why).
- **Contrast (measured):** the minimum is 5.1:1 (the viewer note) and 5.3:1 (a room count over bright stones), so the labels need a ≥ 72% ink backing. On a sunset flat with gold spray the background is the brightest of the three concepts.
- **Reduced motion:** no glide (cut-dissolves between vantages), no 1 s audio burst, no "time resumes" (Video opens directly), no gyro.
- **Sound:** the click and the burst must never play before a gesture and must respect the mute. The viewer counts as a gesture only after a tap.
- Targets: marks 44 px tall, viewer buttons 44 px. No horizontal scroll (checked).

## 5. Concrete UX weaknesses
1. **Discoverability vs. purity (top risk).** The concept's beauty is the absence of UI: footprints revealed by raking light, icons only at 5 s. On a phone that hides all 18 rooms. Six labels over the scene (see ui-phone.png) make it usable but crowd the frame, and they pull it toward the "game HUD" look the brief forbids.
2. **No photograph on Home.** The world is built on the people being missing, so a first-time visitor's first 3 seconds contain none of Shay's work. A and B at least show a scene that looks like his photos.
3. **Heaviest load.** The only real-time 3D concept (≤ 3 MB phone budget, gyro, particles). A slow first interaction directly delays the 3-second goals unless the HTML layer is fully independent.
4. **Gesture conflicts.** A horizontal swipe circles vantages in the world, but swipes photos in the viewer, and swipe up flips the print. The same finger does three different things depending on the state, so the state must always be obvious.
5. **18 vantages, only covers register.** The "click" works for the cover photo; photos 2…N are just a normal viewer. Visitors may expect the magic on every photo.
6. **Eerie emptiness.** A frozen world with no people can feel cold for a brand built on people and parties; the gold "הרגע שלך" mark helps by making the visitor the missing person.
