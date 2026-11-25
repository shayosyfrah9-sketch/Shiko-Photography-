// Local test server: wraps the artifact fragment in the skeleton the publisher adds, serves assets, and maps the jsdelivr three.js paths to devtools/node_modules (no network needed).
import http from 'http'; import fs from 'fs'; import path from 'path'; import { fileURLToPath } from 'url';
const here = path.dirname(fileURLToPath(import.meta.url)); const three = path.resolve(here, '../../../devtools/node_modules/three');
const types = { '.js': 'text/javascript', '.mjs': 'text/javascript', '.wasm': 'application/wasm', '.glb': 'model/gltf-binary', '.ktx2': 'image/ktx2', '.jpg': 'image/jpeg', '.json': 'application/json' };
http.createServer((req, res) => {
  const u = new URL(req.url, 'http://x'); let p = u.pathname;
  if (p === '/' || p === '/index.html') { const frag = fs.readFileSync(path.join(here, 'index.html'), 'utf8'); res.writeHead(200, { 'content-type': 'text/html', ...(process.env.CSP ? { 'content-security-policy': "default-src 'none'; script-src 'unsafe-inline' https://cdn.jsdelivr.net; worker-src blob:; connect-src 'self'; img-src 'self' data: blob:; style-src 'unsafe-inline'; font-src data:" } : {}) }); return res.end('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light}</style></head><body>' + frag + '</body></html>'); }
  if (/\.(ktx2|glb)\.png$/.test(p)) p = p.slice(0, -4);
  let f = p.startsWith('/__three/') ? path.join(three, p.slice(9)) : path.join(here, p);
  if (!f.startsWith(here) && !f.startsWith(three)) { res.writeHead(403); return res.end(); }
  fs.readFile(f, (e, b) => { if (e) { res.writeHead(404); return res.end('nf'); } res.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream', 'cache-control': 'no-store' }); res.end(b); });
}).listen(Number(process.env.PORT || 8099), () => console.log('serving 8099'));
