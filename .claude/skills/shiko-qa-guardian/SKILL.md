---
name: shiko-qa-guardian
description: Automated visual/functional testing, accessibility checks and protection of the live site (shikophotography.com v153) for SHIKO projects. Use before any publish, deploy, merge, or when touching repo branches.
---
# QA Guardian (covers: automated visual testing, accessibility & UX testing, live-site protection)

## Iron rules
- Live = GitHub Pages from branch `main` of shayosyfrah9-sketch/shiko-photography-. Official stable version 153 = commit 775a28d (branch `backup-v153-live`; offline bundle in /mnt/project-files/shiko-site/backup-v153-live/v153.bundle).
- WORLD 2.0 work only on branch `world2-dev` (worktree /home/user/shiko-world2) and its own preview artifact. Never the v153 preview link, never `main`.
- A local pre-push hook blocks pushes to main/backup branches unless `SHIKO_DEPLOY_OK=1`, which may only be set after Shay's explicit written approval in the thread.
- No fixes, optimisations or cache changes on the live site without approval (includes the known service-worker bug).

## Regression suite (scratchpad)
- `reg.js page [m]`: all 18 rooms — photo count, order, links, gallery, return home. Compare JSON with the last approved run (`reg5_*`, `reglive_*`).
- `aspq.js page`: photo plane aspect vs real image (≤ 0.1%), resolution ≥ 1500 px.
- `navlive.js d|m`: booking, about, menu, WhatsApp wa.me/972544351955, music responses.
- `perf6.js`/`perflive.js`: load budgets (see `shiko-asset-performance`).
- Live tests: launch Chromium with `proxy:{server:process.env.HTTPS_PROXY}`.

## Accessibility
Keyboard reachable controls, visible focus, aria-labels in the active language, `prefers-reduced-motion` honoured, contrast ≥ 4.5:1, a non-3D fallback page (classic.html) for weak devices, captions/alt text for photos where possible.

## Content safety
Never delete/alter photos, order, links, contact details. Diff `ROOMS` data before/after any change; any difference must be explained and approved.

## Report format
Passed / failed / not tested (with reason). Never report a capability as working unless a test ran.
