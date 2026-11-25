// Optimization pass 1: 1024 normal maps as ETC1S (quality 220) instead of UASTC (~1.3 MB each -> ~0.26 MB each).
// Usage: node prep-optimize-normals.mjs   (reads ../studio/village/techproof/raw, writes assets/*_nor_l.ktx2)
import { encodeToKTX2 } from 'ktx2-encoder'; import sharp from 'sharp'; import fs from 'fs';
const RAW = '../studio/village/techproof/raw', OUT = '../studio/village/techproof/assets';
const imageDecoder = async (b) => { const { data, info } = await sharp(Buffer.from(b)).ensureAlpha().raw().toBuffer({ resolveWithObject: true }); return { width: info.width, height: info.height, data: new Uint8Array(data) }; };
const Q = +(process.env.NOR_Q || 220);
for (const [m, short] of [['rock_boulder_cracked', 'rock'], ['aerial_grass_rock', 'ground'], ['brown_planks_03', 'wood']]) {
  const png = await sharp(`${RAW}/${m}_nor_gl_1k.jpg`).resize(1024, 1024, { fit: 'cover' }).png().toBuffer();
  const out = await encodeToKTX2(new Uint8Array(png), { isUASTC: false, qualityLevel: Q, generateMipmap: true, isNormalMap: true, imageDecoder });
  fs.writeFileSync(`${OUT}/${short}_nor_l.ktx2`, out); console.log(short, 'nor_l', out.length);
}
