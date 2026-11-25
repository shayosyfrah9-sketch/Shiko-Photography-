import { encodeToKTX2 } from 'ktx2-encoder'; import sharp from 'sharp'; import fs from 'fs';
const imageDecoder = async (b) => { const { data, info } = await sharp(Buffer.from(b)).ensureAlpha().raw().toBuffer({ resolveWithObject: true }); return { width: info.width, height: info.height, data: new Uint8Array(data) }; };
for (const [m, s] of [['rock_boulder_cracked','rock'],['aerial_grass_rock','ground'],['brown_planks_03','wood']]) {
  for (const [sz, tag] of [[512,'m']]) {
    const png = await sharp(`../studio/village/techproof/raw/${m}_nor_gl_1k.jpg`).resize(sz, sz).png().toBuffer();
    const out = await encodeToKTX2(new Uint8Array(png), { isUASTC: false, generateMipmap: true, isNormalMap: true, imageDecoder });
    fs.writeFileSync(`../studio/village/techproof/assets/${s}_nor_etc_${tag}.ktx2`, out); console.log(s, sz, out.length);
  }
}
