# Decisions log
- 2026-11-24 Studio set up on branch world2-dev, isolated from main. Skills consolidated from 34 requested domains into 7 project skills (see TOOLS.md). 12 agents defined with minimal tools.
- 2026-11-24 Rendering: Blender 5.3 bpy headless, Cycles CPU (no GPU, so no EEVEE). Real-time bridge = baked lighting + glTF/meshopt + pre-rendered backplates.
- 2026-11-24 Blender MCP not used: it drives a GUI Blender over a local socket; here bpy is called directly, which gives the same control headlessly.
