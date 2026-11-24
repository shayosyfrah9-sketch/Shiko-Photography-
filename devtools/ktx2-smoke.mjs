import { encodeToKTX2 } from 'ktx2-encoder';
import sharp from 'sharp';
import fs from 'fs';
const buf = fs.readFileSync('/tmp/claude-0/t.png');
const imageDecoder = async (b) => { const { data, info } = await sharp(Buffer.from(b)).ensureAlpha().raw().toBuffer({ resolveWithObject: true }); return { width: info.width, height: info.height, data: new Uint8Array(data) }; };
const out = await encodeToKTX2(new Uint8Array(buf), { isUASTC: false, generateMipmap: true, imageDecoder });
fs.writeFileSync('/tmp/claude-0/t.ktx2', out); console.log('ktx2 bytes', out.length, Buffer.from(out.slice(0,12)).toString('latin1'));
