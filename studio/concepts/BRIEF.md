# Concept brief — SHIKO WORLD 2.0 (2026-11-24, approved by Shay to start the concept phase)

## Shay's conditions (verbatim intent)
- v153 (commit 775a28d, live on shikophotography.com) is protected. Nothing on `main` or the live site changes. All work on `world2-dev` only.
- Do NOT start building the new site. This phase delivers concepts only. Shay picks and approves one first.
- THREE original concepts, fundamentally different from each other (not three skins of one idea).
- Each concept must include:
  1. A central idea that is original, not generic.
  2. A cinematic AND interactive experience.
  3. A natural integration of his four fields: Festivals, Sport (football, basketball, surfing), Portraits & Branding, Video.
  4. A central place for the photographs themselves (the world is the stage, the photos are the art).
  5. Visualisations at the highest quality possible (here: Blender 5.3 Cycles CPU renders; label every image Rendered / Interactive prototype / Mock-up).
  6. Camera movement and navigation explained.
  7. Performance on desktop AND phone addressed.
- The independent critic judges each concept on: originality, visual quality, user experience, brand fit, performance — with reasons and weaknesses, not only a number.
- Goal: an exceptional digital experience with an original artistic identity that does NOT look like a ready-made template or a computer game.

## Who Shay is (facts)
- Shiko Photography (Instagram shiko.photography_), logo = white camera on black, "Shiko PHOTOGRAPHY". 27, started photographing October 2025 after long army reserve duty; looks for "the decisive moment" that tells the whole story without words.
- Fields: festivals & parties (FreeEarth, Ozora, Zoodana), sport (Maccabi Tel Aviv football at Bloomfield, Maccabi Rishon basketball, reservists league, surfing), portraits & branding (Mayu, Maya, Amit, Shira, Noa), video. He also founded Matcha (event gallery platform).
- He prefers: real, not game-like; fast loading (leads leave); simple navigation; Home always returns to the main world; Hebrew RTL / English LTR, Rubik/round fonts; quick smooth transitions, no colour takeovers; each room's environment matches the vibe of its photos (forest, sea…); icons instead of text in the header.
- Must survive: all 18 rooms, original photos and their order, gallery links, contact (WhatsApp 0544351955), booking.

## Previous ideas (may be used, rejected or transformed — originality is judged)
VISION.md lists A Floating World, B Cinematic Valley, C World Beyond the Lens. The experiment "Aperture Pavilion" (glass box on a cliff) was judged a cliché: originality must come from the concept itself.
The current live site is a 3D alpine village of 4 wooden cabins on a rock pillar: WORLD 2.0 must be clearly beyond it.

## Resources
- Photos: media/photos/*.jpg (358 files, his real work). Backdrops: a3/bg-*.jpg.
- Blender: `/tmp/claude-0/bpyenv/bin/python` (bpy 5.3, Cycles CPU, OIDN; 4 cores, 15 GB RAM, no GPU). Poly Haven CC0 downloads work (api.polyhaven.com, dl.polyhaven.org).
- three.js 0.181 + @gltf-transform 4.5.1 + ktx2-encoder (KTX2 works) in devtools/ (dev only). Live site stays on vendor/three.min.js r128.
- Output folders: studio/concepts/ (text), studio/renders/concepts/<A|B|C>/round-N/ (images).
