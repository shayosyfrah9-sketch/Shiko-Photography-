# Decisions log
- 2026-11-24 Studio set up on branch world2-dev, isolated from main. Skills consolidated from 34 requested domains into 7 project skills (see TOOLS.md). 12 agents defined with minimal tools.
- 2026-11-24 Rendering: Blender 5.3 bpy headless, Cycles CPU (no GPU, so no EEVEE). Real-time bridge = baked lighting + glTF/meshopt + pre-rendered backplates.
- 2026-11-24 Blender MCP not used: it drives a GUI Blender over a local socket; here bpy is called directly, which gives the same control headlessly.
- Setup report page: https://claude.ai/artifact/LbN6qtfEYi4niELaWd6Wn6 (separate from the v153 preview).
- 2026-11-24 (concept phase start, Shay's OK): verified live index.html + sw.js on shikophotography.com are byte-identical to 775a28d → local annotated tag v153-live on 775a28d (push still blocked by the proxy; Shay can create it on GitHub).
- 2026-11-24 Dev-only tooling in devtools/ (node_modules git-ignored): three@0.181.0 (exact), @gltf-transform/{core,extensions,functions}@4.5.1, ktx2-encoder 0.6.0 + sharp (KTX2 encode verified: devtools/ktx2-smoke.mjs). Compatibility: the live site and v153 keep vendor/three.min.js r128 untouched; new three is ES-module only (no global build since r160) with new colour management, so it is used only for WORLD 2.0 code. Rollback = delete devtools/ (nothing else depends on it).
- 2026-11-24 Project agents are not registered as named agent types in this session (session started outside the repo). They run as general-purpose agents that load their own .claude/agents/<name>.md definition; reports say which ran.
