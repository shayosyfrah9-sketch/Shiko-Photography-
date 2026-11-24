---
name: shiko-cinematic-motion
description: Cinematic lighting, camera moves, motion design, VFX, transitions, storytelling and sound for SHIKO WORLD 2.0. Use when designing an intro, a camera path, a transition between areas, particles, or ambient audio.
---
# Cinematic & Motion (covers: cinematic lighting, camera movement, motion design, VFX, immersive storytelling, interactive transitions, spatial audio & sound)

## Story spine
Darkness → light → lens → world → choice. Every visit tells it in ≤ 6 s (first visit) and ≤ 1.5 s (return visit, remembered via localStorage). Always skippable (tap/click/Esc), never blocks booking/WhatsApp.

## Camera language
- Lenses: 24–35 mm for establishing (drone feel), 50 mm for buildings, 85 mm for details. Never > 70° vertical FOV.
- Moves: dolly-in, crane up reveal, orbit ≤ 25°, parallax push. One move per shot. Ease with cubic in-out; never linear starts/stops.
- Speed: establishing 2–4 m/s at human scale; transitions 0.9–1.6 s; respect `prefers-reduced-motion` with cross-fades only.
- Composition per frame: subject on thirds, horizon on thirds, foreground element for depth, leading line to the target.
- Plan every path as keyframes (position, target, FOV, time) in JSON so Blender and three.js share it.

## Lighting for drama
Key/fill/rim contrast 4:1–8:1, warm key vs cool ambient, practical lights motivate colour (festival = magenta/amber, sport = cold white 5600 K floods, portrait = soft north light, video = deep teal + warm screen spill). Light reveals architecture; darkness frames photos.

## Motion & VFX rules
- Particles: < 2 000 on desktop, < 600 on phone, additive only for light (dust in beams, embers), never confetti noise.
- Ambient life (birds, clouds, water, wind on foliage) at low amplitude; nothing moves near a photo while it is being viewed.
- Transitions are diegetic when possible: aperture iris, lens refraction, portal through a frame, light bloom—not generic slides.

## Sound
Silent until the first user gesture (browser policy + respect). Layers: ambience bed per area, one music cue, UI micro-sounds (shutter). Crossfade 1.2–1.6 s; master ≤ -16 LUFS; one mute button always visible; remember choice.

## Deliverables
Shot list (table), camera JSON, animatic (ffmpeg from Blender frames: `ffmpeg -framerate 24 -i f%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p out.mp4`), timing sheet.

## Mistakes to avoid
Long unskippable intros; motion sickness (roll, fast yaw); bloom on everything; sound on load; camera passing through geometry; cuts that lose orientation.
