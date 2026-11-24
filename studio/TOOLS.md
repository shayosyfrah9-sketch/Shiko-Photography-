# Tools — verified status (2026-11-24, cloud session)
Status words: WORKS = used successfully in this session · NEEDS APPROVAL · NOT AVAILABLE.

| Tool | Status | Evidence / note |
| Blender 5.3 (bpy wheel, headless) + Cycles CPU | WORKS | reinstall per container: python3.13 venv + pip bpy==5.3.0 (/tmp/claude-0/bpyenv) |
| OpenImageDenoise | WORKS | denoised 16–64 spp renders |
| EEVEE / GPU rendering | NOT AVAILABLE | no GPU in the cloud container |
| Blender MCP | NOT NEEDED | it remote-controls a GUI Blender; here bpy is driven directly |
| Poly Haven API + downloads (CC0 HDRIs, textures, models) | WORKS | qwantani_dusk_2, kloofendal_48d, rock_face_03, concrete_wall_008, forest_ground_04, aerial_rocks_02 |
| Physical sky (Multiple Scattering) | WORKS | round 3–4 |
| Playwright + Chromium (swiftshader) | WORKS | full live-site QA of v153 |
| gltfpack / meshoptimizer | WORKS | trees 10.8 MB → 1.9 MB |
| ffmpeg | WORKS | animatic encoding |
| Python PIL | WORKS | comparisons, contact sheets |
| three.js r128 (local) | WORKS | current site |
| three@0.181.0 + @gltf-transform 4.5.1 (devtools/) | WORKS | approved 2026-11-24, dev only; live stays r128 |
| KTX2 / Basis (ktx2-encoder wasm, devtools/) | WORKS | approved 2026-11-24; toktx binaries blocked (GitHub releases 403) |
| Figma MCP | NEEDS APPROVAL | in the connector directory, needs Shay's Figma account |
| AI image/concept generation | NOT AVAILABLE | no such tool connected; concepts come from Blender renders and code |
| Real-device GPU profiling | NEEDS SHAY | swiftshader is CPU; real fps needs his phone/computer (Remote Control) |
| GitHub branches push | WORKS | backup-v153-live, world2-dev |
| GitHub tags / API writes | NOT AVAILABLE | proxy blocks; Shay can create tag v153-live on GitHub |
| Project skills (.claude/skills/shiko-*) | WORKS | loaded in session; shiko-visual-critique invoked |
| Project agents (.claude/agents/*) | PARTLY | files valid; not registered in a session that started before they existed. Ran the art-critic definition 4× through a general-purpose agent. Will load as named agents in a new session opened on world2-dev (to verify). |
