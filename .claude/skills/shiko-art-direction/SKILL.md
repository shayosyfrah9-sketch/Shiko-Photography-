---
name: shiko-art-direction
description: Art direction, luxury brand, award-level web/UI/UX and typography for SHIKO WORLD 2.0. Use when deciding a look, layout, interface, type, concept board or any visual direction for Shiko Photography.
---
# SHIKO Art Direction (covers: premium frontend design, creative art direction, award-winning web design, luxury brand experience, UI/UX, typography & composition, experimental interaction)

## Purpose
Every visual decision serves one idea: **the world is the stage, Shiko's photographs are the art.** The result must read as an international photographer's studio, not a game and not a template.

## Before you design (always)
1. Read `studio/VISION.md`, `studio/DESIGN_LANGUAGE.md`, `studio/GUARDRAILS.md`.
2. Write a one-paragraph brief: audience (event producers, models/brands, sports clubs), the single feeling of this screen, what the user must be able to do in 3 seconds (see work, book, WhatsApp).
3. Produce at least 3 genuinely different directions (different metaphor, not different colour). Kill the weakest with reasons.

## Principles
- **Hierarchy:** one hero per screen. Photos > world > UI. UI occupies < 12% of the viewport outside menus.
- **Restraint is luxury:** 2 type weights, 1 accent colour, generous negative space, hairlines not boxes, no drop shadows heavier than 8% black.
- **Type:** Latin display = thin geometric (Jost 300) caps with tracking .2–.35em; Hebrew = Rubik/Heebo 300–400, NEVER letter-spacing on Hebrew. RTL for he, LTR for en, everything in the chosen language; event names stay in their original language.
- **Composition:** rule of thirds or strong central symmetry; horizon never through the middle unless symmetric architecture; leading lines toward the action button.
- **Interaction:** every effect must answer "what does this tell the visitor?". Hover = reveal, not decorate. Max one signature interaction per screen (e.g. aperture iris, lens refraction).
- **Silhouette test:** each of the four domains (Festivals, Sport, Portraits & Branding, Video) must be recognisable as a black shape on white.
- **Contact is sacred:** booking + WhatsApp reachable in ≤ 1 tap from anywhere; never hidden behind an intro.

## Quality bar (pass all)
- Screenshot at 1440×900 and 390×844 reads clearly at 25% zoom (squint test).
- Contrast ≥ 4.5:1 for text, ≥ 3:1 for UI icons.
- No element looks like stock UI kit or "game HUD".
- Could plausibly appear on Awwwards SOTD: original idea + craft + usability.

## Common mistakes
Neon everywhere; too many fonts; UI cards over the photos; glassmorphism without purpose; centred everything; Hebrew with tracking; burying contact; "cool" intros that cannot be skipped.

## Process
Brief → 3 directions → pick → mock (HTML or render) → screenshot → run `shiko-visual-critique` → fix → compare side by side → repeat (min 3 rounds for key screens).

## Tools
HTML/CSS prototypes, Playwright screenshots, Blender stills for hero imagery, `artifact-design` skill for published pages, `design:design-critique`, `design:accessibility-review`, `design:ux-copy`.
