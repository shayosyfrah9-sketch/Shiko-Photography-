// Fallback textures for browsers/sandboxes where KTX2 (worker + wasm) cannot run: plain JPG copies with the same names.
import sharp from 'sharp'; import fs from 'fs';
const RAW = '../studio/village/techproof/raw', OUT = '../studio/village/techproof/assets/fb'; fs.mkdirSync(OUT, { recursive: true });
let total = 0;
for (const [m, s] of [['rock_boulder_cracked', 'rock'], ['aerial_grass_rock', 'ground'], ['brown_planks_03', 'wood']]) {
  const jobs = [['diff', 's', 256], ['diff', 'l', 1024], ['rough', 's', 256], ['rough', 'l', 1024]];
  for (const [kind, tag, size] of jobs) { const f = `${OUT}/${s}_${kind}_${tag}.jpg`; await sharp(`${RAW}/${m}_${kind === 'diff' ? 'diff' : 'rough'}_1k.jpg`).resize(size, size).jpeg({ quality: 80, mozjpeg: true }).toFile(f); total += fs.statSync(f).size; }
  for (const [tag, size] of [['l', 1024], ['etc_m', 512]]) { const f = `${OUT}/${s}_nor_${tag}.jpg`; await sharp(`${RAW}/${m}_nor_gl_1k.jpg`).resize(size, size).jpeg({ quality: 82, mozjpeg: true }).toFile(f); total += fs.statSync(f).size; }
}
console.log('fallback jpg bytes', total);
