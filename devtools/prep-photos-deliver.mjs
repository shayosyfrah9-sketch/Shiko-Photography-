// Display-adapted photo variants: xs (blur-up placeholder), m (960 px), l (1920 px), each as AVIF q65 and WebP q88 (+ the old 1600 JPG stays as the last fallback).
import sharp from 'sharp'; import fs from 'fs';
const OUT = '../studio/village/techproof/assets', ids = ['2w2a1130', '2w2a7966', '2w2a0403'], rep = [];
for (const id of ids) {
  const src = `../media/photos/${id}.jpg`, meta = await sharp(src).metadata();
  const base = (w) => sharp(src).resize({ width: w, height: w, fit: 'inside', withoutEnlargement: true });
  const xs = await base(256).webp({ quality: 60, effort: 5 }).toBuffer(); fs.writeFileSync(`${OUT}/photo_${id}_xs.webp`, xs); const row = { id, source: `${meta.width}x${meta.height}`, xs_webp: xs.length };
  for (const [tag, w] of [['m', 960], ['l', 1920]]) {
    const a = await base(w).avif({ quality: 65, effort: 4 }).toBuffer(), b = await base(w).webp({ quality: 88, effort: 5 }).toBuffer();
    fs.writeFileSync(`${OUT}/photo_${id}_${tag}.avif`, a); fs.writeFileSync(`${OUT}/photo_${id}_${tag}.webp`, b); row[`${tag}_avif`] = a.length; row[`${tag}_webp`] = b.length;
  }
  rep.push(row); console.log(JSON.stringify(row));
}
fs.writeFileSync(`${OUT}/_photos-report.json`, JSON.stringify(rep, null, 1));
