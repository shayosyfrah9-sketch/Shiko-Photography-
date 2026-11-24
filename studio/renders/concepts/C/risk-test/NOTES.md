# Concept C risk test (C3), notes
Scripts: studio/blender/concepts/C3_spray.py (all 4 render modes), C3_composite.py (labels + click mock-up), C3_phone.html + C3_phone_shot.js (phone UI, Playwright).
Engine: Blender 5.3 Cycles CPU (4 cores), AgX Punchy (edge pass: Standard so the photo keeps its colours), OIDN denoise (not on the edge pass).
| Image | Label | Settings | Time |
|---|---|---|---|
| C_rt_1_spray_RENDERED.png | Rendered | 1600x900, 96 spp, 2744 glass drops IOR 1.33 (2-8 mm, ~15% elongated, rim term in the shader) + 22 bokeh drops + mist volume, procedural sea/sand | 275 s |
| C_rt_2_click_MOCKUP.jpg | Mock-up | base render (same scene with traced absence) 1600x900 96 spp 285 s + edge pass (photo+mount as 3D emissive planes, 32 drops) 48 spp 9 s; PIL pastes the real photo, composites the drops by disc mask, adds the two small panels | 294 s |
| C_rt_3_phone_MOCKUP.png | Mock-up | backdrop = Rendered portrait 780x1688, 96 spp, 229 s (C_rt_3_phone_backdrop_RENDERED.png); HTML 390x844 @2x, Playwright. Font: Rubik + Jost via Google Fonts (loaded OK) | 229 s + screenshot |
Tests used: 6/6 (854x480, 16-24 spp). No fix rounds after the finals.
Licences: nothing downloaded. All geometry, textures and sky are procedural; photo = Shay's own surf0001.jpg; Rubik/Jost are OFL (Google Fonts).
Sun: elevation 32 deg, 14 deg left of view axis, behind the spray; sky = gradient tuned by eye to the photo's blue.
## What failed (honest)
- Spray reads as sparse transparent flecks, not as a curtain of water. The mist volume (final density 2.8) is still a grey haze; at 5.5 and 16 it fogged out the sea. No dense white fans/streaks like the photo.
- Sky and sea are hazy lavender-grey, far less saturated than the photo's ultramarine sky and turquoise sea, so the world does not match the photo (the click mock-up shows the mismatch plainly). Sun direction is plausible but nothing visibly agrees with the photo's light.
- Wet sand is a flat grey-brown slab; only a faint ripple normal. No wet sheen, no footprints.
- Drops themselves (zoom in) look like real glass beads with bright rims, but only 2744 survive the clumping filter and they are small.
- Hole: hand-traced silhouette, roughly +-3-5 px at 1600x900 (not 2 px), and the photo covers it in the click frame; it is only visible in the small "before" panel.
- Edge drops sit on the photo border but are small and few; the photo is far more saturated than the render, so continuity is weak.
- Phone: UI is legible (labels >=13 px, scrim backgrounds) but sits over a weak backdrop; four field chips scattered over the sky still read like a level-select map. Contrast was not measured with a tool, only reasoned (ivory on a 74% ink scrim).
