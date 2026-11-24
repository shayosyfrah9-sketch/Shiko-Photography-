# Guardrails — protecting shikophotography.com (read first)
1. Official, stable, approved live version: **v153**, commit 775a28d on `main`. GitHub Pages publishes only `main`.
2. Restore points: branch `backup-v153-live` (GitHub), offline full bundle /mnt/project-files/shiko-site/backup-v153-live/v153.bundle (all code, photos, models, textures, music; `git clone v153.bundle`), older `backup-v146-live`. Rollback: push backup-v153-live to main (only with approval).
3. A git tag `v153-live` could not be pushed from the cloud session (proxy blocks tag pushes/API writes): Shay can create it on GitHub (Releases → new tag v153-live on 775a28d).
4. WORLD 2.0 lives only on `world2-dev` and in its own preview artifact. No CI/Actions, no automatic deploy, nothing on world2-dev reaches the domain.
5. Local pre-push hook blocks pushes to main/backup branches unless SHIKO_DEPLOY_OK=1, set only after Shay's explicit approval in writing.
6. No changes to the live site at all — not even small fixes, optimisation, or the known service-worker bug — without approval.
7. Never publish to the v153 preview artifact (claude.ai/artifact/UjVMF5hvojrxwuYKkABQ6b) for WORLD 2.0 work.
8. External installs, paid services, account connections, or access to Shay's computer need separate approval.
