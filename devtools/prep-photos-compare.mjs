// Photo delivery comparison (quality first): JPEG (current) vs WebP vs AVIF at equal width; PSNR + SSIM against the lossless resize.
// Output: table to stdout, JSON + 1:1 crop strips to ../studio/village/techproof/compare/
import sharp from 'sharp'; import fs from 'fs';
const ids = ['2w2a1130', '2w2a7966', '2w2a0403'], OUT = '../studio/village/techproof/compare'; fs.mkdirSync(OUT, { recursive: true });
const gray = async (buf) => { const { data, info } = await sharp(buf).greyscale().raw().toBuffer({ resolveWithObject: true }); return { d: data, w: info.width, h: info.height }; };
function ssim(a, b) { // mean SSIM over 8x8 windows (stride 4), luma only
  const C1 = 6.5025, C2 = 58.5225; let sum = 0, n = 0;
  for (let y = 0; y + 8 <= a.h; y += 4) for (let x = 0; x + 8 <= a.w; x += 4) { let ma = 0, mb = 0; for (let j = 0; j < 8; j++) for (let i = 0; i < 8; i++) { const k = (y + j) * a.w + x + i; ma += a.d[k]; mb += b.d[k]; } ma /= 64; mb /= 64; let va = 0, vb = 0, cv = 0;
    for (let j = 0; j < 8; j++) for (let i = 0; i < 8; i++) { const k = (y + j) * a.w + x + i, da = a.d[k] - ma, db = b.d[k] - mb; va += da * da; vb += db * db; cv += da * db; } va /= 63; vb /= 63; cv /= 63;
    sum += ((2 * ma * mb + C1) * (2 * cv + C2)) / ((ma * ma + mb * mb + C1) * (va + vb + C2)); n++; }
  return sum / n;
}
function psnr(a, b) { let e = 0; for (let i = 0; i < a.d.length; i++) { const d = a.d[i] - b.d[i]; e += d * d; } e /= a.d.length; return 10 * Math.log10(255 * 255 / Math.max(e, 1e-9)); }
const V = [['jpeg q82 (current)', (s) => s.jpeg({ quality: 82, mozjpeg: true })], ['jpeg q88', (s) => s.jpeg({ quality: 88, mozjpeg: true })], ['webp q80', (s) => s.webp({ quality: 80, effort: 5 })], ['webp q88', (s) => s.webp({ quality: 88, effort: 5 })], ['avif q55', (s) => s.avif({ quality: 55, effort: 4 })], ['avif q65', (s) => s.avif({ quality: 65, effort: 4 })]];
const rows = [];
for (const id of ids) for (const W of [960, 1600]) {
  const src = `../media/photos/${id}.jpg`, meta = await sharp(src).metadata(); const ref = await sharp(src).resize({ width: W, height: W, fit: 'inside' }).png().toBuffer(); const rg = await gray(ref); const crops = [];
  for (const [name, fn] of V) { const t = Date.now(); const buf = await fn(sharp(ref)).toBuffer(); const enc = Date.now() - t; const g = await gray(buf); rows.push({ id, width: W, src: `${meta.width}x${meta.height}`, variant: name, bytes: buf.length, psnr: +psnr(rg, g).toFixed(2), ssim: +ssim(rg, g).toFixed(4), encodeMs: enc });
    const m = await sharp(buf).metadata(); const cw = Math.min(480, m.width), ch = Math.min(320, m.height); crops.push(await sharp(buf).extract({ left: Math.floor((m.width - cw) / 2), top: Math.floor((m.height - ch) / 2), width: cw, height: ch }).png().toBuffer()); }
  if (W === 1600) { const cw = 480, ch = 320; await sharp({ create: { width: cw * 3, height: ch * 2, channels: 3, background: '#111' } }).composite(crops.map((c, i) => ({ input: c, left: (i % 3) * cw, top: Math.floor(i / 3) * ch }))).png().toFile(`${OUT}/crops-${id}-1600.png`); }
}
fs.writeFileSync(`${OUT}/photo-compare.json`, JSON.stringify(rows, null, 1));
for (const r of rows) console.log(r.id, r.width, r.variant.padEnd(20), String(r.bytes).padStart(8), 'psnr', r.psnr, 'ssim', r.ssim, r.encodeMs + 'ms');
