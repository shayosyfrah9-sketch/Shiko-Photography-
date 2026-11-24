# QA guard audit: start of the WORLD 2.0 concept phase
Date: 2026-11-24 · Role: qa-security (read-only) · Worktree /home/user/shiko-world2 · No push, no change to main or the live site.
Label: no images in this report. Every result below comes from a command that was actually run (curl, md5sum, git). Nothing is assumed unless it says so.

## Summary
**Result: PASSED (all 7 checks).** The live site is byte-identical to 775a28d. The restore points are intact. Nothing on world2-dev can deploy. There are 4 observations to note (O1 to O4).

| # | Check | Result |
|---|---|---|
| 1 | Worktree on world2-dev, origin/main = 775a28d, local tag v153-live -> 775a28d, tag not on remote | PASSED |
| 2 | Live index.html, sw.js and 4 assets byte-identical to 775a28d | PASSED |
| 3 | origin/backup-v153-live = 775a28d; v153.bundle exists and verifies | PASSED |
| 4 | pre-push hook blocks refs/heads/main (simulated) | PASSED |
| 5 | No .github/workflows on world2-dev; CNAME unchanged | PASSED |
| 6 | devtools dev-only; vendor/three.min.js r128 and identical to main | PASSED |
| 7 | Secrets scan of world2-dev vs main | PASSED |

## Evidence
1. **Branches and tags**
   - `git branch --show-current` returns world2-dev. `git worktree list` shows shiko-world2 at f27537f [world2-dev] and the main checkout at 775a28d.
   - After `git fetch`, origin/main = 775a28d8981cc4f610fc20ee5967568d3694be31. `git ls-remote` confirms that remote refs/heads/main = 775a28d and refs/heads/world2-dev = f27537f.
   - `v153-live` is an annotated tag (object 2a61650) and `v153-live^{commit}` = 775a28d. The message is "v153 - protected live version".
   - `git ls-remote --tags origin` returns nothing, so the tag is **not on GitHub**. This matches GUARDRAILS §3: Shay still needs to create it.
   - world2-dev is 2 commits ahead of main (9438f33, f27537f), and 775a28d is its parent.
2. **Live site** (GitHub.com server; cache-busting query used)
   - index.html (722692 B): md5 f4544ba1bb6520c9088324f634403940 on live, on `/`, and in `git show 775a28d:index.html`. All identical.
   - sw.js (1404 B): md5 d575c7d101f4f45c8920df00cd4fde98 on live and in git. Identical.
   - Assets, picked at random with shuf from the files index.html references:
     - assets/logo-lens.png: 0cbc693d… MATCH
     - a3/mvill.webp: 2f765199… MATCH
     - media/about-shiko.jpg: f8fbebe9… MATCH
   - Extra asset: vendor/three.min.js, eb854986… MATCH.
3. **Restore points**
   - `git ls-remote` shows refs/heads/backup-v153-live = 775a28d (exact match, not just containing it).
   - /mnt/project-files/shiko-site/backup-v153-live/v153.bundle exists (172,667,619 B). `git bundle verify` reports "is okay" (exit 0) and "complete history". Its heads are main and backup-v153-live, both at 775a28d.
4. **pre-push hook** (/home/user/shiko-photography-/.git/hooks/pre-push, executable)
   - The worktree's hook path resolves to the same file, because core.hooksPath is not set.
   - I simulated it by piping lines on stdin with SHIKO_DEPLOY_OK unset. Nothing was pushed.
     - main: exit 1 (BLOCKED)
     - backup-v153-live: exit 1
     - delete of main: exit 1
     - multi-ref push with world2-dev first and main second: exit 1
     - world2-dev: exit 0
     - tag: exit 0
     - main with SHIKO_DEPLOY_OK=1: exit 0, which is the intended override.
5. **Workflows and CNAME**
   - `git ls-tree -r world2-dev` and origin/main contain no `.github/` path, and there is no .github directory on disk.
   - `git diff main world2-dev -- CNAME vendor/three.min.js` is empty. CNAME = shikophotography.com.
6. **devtools**
   - Installed versions are three 0.181.0, @gltf-transform/core and functions 4.5.1, ktx2-encoder 0.6.0, sharp 0.35.5.
   - `devtools/node_modules/` is ignored by `.gitignore:1` (`git check-ignore` confirms this, and `git status --ignored` shows `!!`). devtools/ is not tracked in any commit.
   - index.html at both 775a28d and world2-dev has the same md5. It has no reference to devtools, node_modules or gltf-transform. The only "ktx2" hits are the inline GLTFLoader's setKTX2Loader code, and "sharp" appears only as a word in a comment.
   - vendor/three.min.js contains `REVISION="128"`, so it is r128.
7. **Secrets**
   - I grepped the added lines of `git diff main..world2-dev` and of the uncommitted and untracked files (.gitignore, devtools/package.json, devtools/ktx2-smoke.mjs, studio/concepts/BRIEF.md, modified DECISIONS.md and TOOLS.md) for:
     - AWS, GitHub (ghp_/github_pat_), OpenAI and Anthropic (sk-/sk-ant-), Slack and Google API keys
     - private keys
     - the words api_key, secret, password, token, bearer and Authorization
   - The only hit is the word "secrets" in qa-security.md, which is the policy text itself.
   - strings on the 4 JPGs and the MP4 found no key patterns. No .env, .pem, .key or credentials files are tracked. The remote URL contains no embedded credentials.
   - The external URLs in the diff are Google Fonts (in studio/report-setup.html, which is not a live page) and one claude.ai artifact link.

## Observations (not failures)
- **O1:** The commit message of 775a28d reads "Stage 6 candidate (...) - NOT live". However, the live bytes match 775a28d exactly, so this is v153 as served. The message is just out of date. Do not rewrite it.
- **O2:** The pre-push hook covers only `git push` from this clone.
  - `git push --no-verify` bypasses it, and so do GitHub API or MCP writes (create_or_update_file, push_files, merge_pull_request).
  - GUARDRAILS says the proxy blocks API writes. I did **not** test this, on purpose, because testing it would risk main.
  - Recommendation: Shay enables GitHub branch protection on main and backup-* (needs his approval and is done in the GitHub UI).
- **O3:** The worktree has uncommitted changes:
  - modified studio/DECISIONS.md and TOOLS.md
  - untracked .gitignore, devtools/ and studio/concepts/
  - The .gitignore that excludes node_modules is itself **untracked**. Commit it before anyone runs `git add -A`, or node_modules could be staged.
- **O4:** The sw.js on live is the known cache-bug version. Per GUARDRAILS §6 it was left untouched.

## Not tested
- Regression, aspect, navigation and performance suites for the 18 rooms (reg.js and others): there is no build change in this phase, and live index.html is byte-identical to the approved baseline.
- Asset licences (CC0) and pinning of external scripts: no third-party assets were added. report-setup.html uses unpinned Google Fonts CSS, but it is a studio report, not the site.
- Whether the proxy blocks GitHub API writes (see O2).
