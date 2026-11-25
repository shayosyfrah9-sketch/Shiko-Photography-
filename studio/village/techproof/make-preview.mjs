// Builds a standalone, self-contained preview folder (full HTML document + assets) that can be pushed to a SEPARATE repo / static host.
// Usage: node make-preview.mjs [outDir]   (default ./preview-dist, git-ignored). Never run this inside the Shiko-Photography repo's served branch.
import fs from 'fs'; import path from 'path';
const here = path.dirname(new URL(import.meta.url).pathname), out = path.resolve(process.argv[2] || path.join(here, 'preview-dist'));
fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
const frag = fs.readFileSync(path.join(here, 'index.html'), 'utf8');
const doc = '<!doctype html>\n<html lang="he" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="robots" content="noindex,nofollow"><title>Shiko Tech Proof (preview)</title><style>:root{color-scheme:light}</style></head><body>\n' + frag + '\n</body></html>\n';
fs.writeFileSync(path.join(out, 'index.html'), doc); fs.writeFileSync(path.join(out, '.nojekyll'), ''); fs.writeFileSync(path.join(out, 'robots.txt'), 'User-agent: *\nDisallow: /\n');
let n = 0, bytes = 0;
for (const d of ['assets', 'basis']) (function walk(rel) { for (const e of fs.readdirSync(path.join(here, rel), { withFileTypes: true })) { const r = path.join(rel, e.name); if (e.isDirectory()) { if (e.name === 'raw') continue; walk(r); } else if (!e.name.startsWith('_')) { fs.mkdirSync(path.dirname(path.join(out, r)), { recursive: true }); fs.copyFileSync(path.join(here, r), path.join(out, r)); n++; bytes += fs.statSync(path.join(here, r)).size; } } })(d);
console.log(`preview built: ${out} (${n} files, ${(bytes / 1048576).toFixed(1)} MB)`);
