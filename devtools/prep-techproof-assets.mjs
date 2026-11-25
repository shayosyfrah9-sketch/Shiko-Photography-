// Stage 1 tech proof: build KTX2 textures + meshopt GLBs. Dev-only. Output: ../studio/village/techproof/assets
import { encodeToKTX2 } from 'ktx2-encoder';
import sharp from 'sharp';
import fs from 'fs';
import path from 'path';
import { Document, NodeIO } from '@gltf-transform/core';
import { EXTMeshoptCompression } from '@gltf-transform/extensions';
import { meshopt } from '@gltf-transform/functions';
import { MeshoptEncoder } from 'meshoptimizer';

const RAW = '../studio/village/techproof/raw';
const OUT = '../studio/village/techproof/assets';
fs.mkdirSync(OUT, { recursive: true });
const report = [];

const imageDecoder = async (b) => {
  const { data, info } = await sharp(Buffer.from(b)).ensureAlpha().raw().toBuffer({ resolveWithObject: true });
  return { width: info.width, height: info.height, data: new Uint8Array(data) };
};
async function toKtx(srcPath, outName, { size, srgb, uastc = false, normal = false, fit = 'cover' }) {
  let img = sharp(srcPath);
  if (size) img = img.resize(size, size, { fit });
  const png = await img.png().toBuffer();
  const t0 = Date.now();
  const out = await encodeToKTX2(new Uint8Array(png), {
    isUASTC: uastc, generateMipmap: true, isSetKTX2SRGBTransferFunc: !!srgb, isNormalMap: !!normal, imageDecoder,
  });
  fs.writeFileSync(path.join(OUT, outName), out);
  report.push({ file: outName, bytes: out.length, ms: Date.now() - t0, srcBytes: fs.statSync(srcPath).size });
  console.log(outName, out.length);
}

// --- PBR sets: placeholder 256 (tiny, shown first) + full 1024
const TEX = !process.env.GEO_ONLY && !process.env.PHOTO_ONLY;
for (const m of TEX ? ['rock_boulder_cracked', 'aerial_grass_rock', 'brown_planks_03'] : []) {
  const short = { rock_boulder_cracked: 'rock', aerial_grass_rock: 'ground', brown_planks_03: 'wood' }[m];
  for (const [sz, tag] of [[256, 's'], [1024, 'l']]) {
    await toKtx(`${RAW}/${m}_diff_1k.jpg`, `${short}_diff_${tag}.ktx2`, { size: sz, srgb: true });
    await toKtx(`${RAW}/${m}_nor_gl_1k.jpg`, `${short}_nor_${tag}.ktx2`, { size: sz, uastc: true, normal: true });
    await toKtx(`${RAW}/${m}_rough_1k.jpg`, `${short}_rough_${tag}.ktx2`, { size: sz, srgb: false });
  }
}

// --- Photos as KTX2 vs JPG (tech only: how a real photo looks inside the world)
const photos = ['2w2a1130', '2w2a7966', '2w2a0403'];
for (const id of process.env.GEO_ONLY ? [] : photos) {
  const src = `../media/photos/${id}.jpg`;
  const meta = await sharp(src).metadata();
  const scale = 1600 / Math.max(meta.width, meta.height);
  const w = Math.round(meta.width * scale / 4) * 4, h = Math.round(meta.height * scale / 4) * 4;
  const buf = await sharp(src).resize(w, h).png().toBuffer();
  const out = await encodeToKTX2(new Uint8Array(buf), { isUASTC: false, generateMipmap: true, isSetKTX2SRGBTransferFunc: true, imageDecoder });
  fs.writeFileSync(path.join(OUT, `photo_${id}.ktx2`), out);
  const jpg = await sharp(src).resize(w, h).jpeg({ quality: 82, mozjpeg: true }).toBuffer();
  fs.writeFileSync(path.join(OUT, `photo_${id}.jpg`), jpg);
  report.push({ file: `photo_${id}`, w, h, ktx2: out.length, jpg: jpg.length });
  console.log('photo', id, w + 'x' + h, 'ktx2', out.length, 'jpg', jpg.length);
}

// --- Geometry: terrain (2 LODs) + rock (2 LODs), meshopt-compressed GLB
function rng(seed) { let s = seed >>> 0; return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296); }
function noise2(seed) {
  const r = rng(seed), P = new Float32Array(256 * 256); for (let i = 0; i < P.length; i++) P[i] = r();
  const at = (x, y) => P[((y & 255) << 8) | (x & 255)];
  return (x, y) => { const xi = Math.floor(x), yi = Math.floor(y), xf = x - xi, yf = y - yi;
    const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
    return at(xi, yi) * (1 - u) * (1 - v) + at(xi + 1, yi) * u * (1 - v) + at(xi, yi + 1) * (1 - u) * v + at(xi + 1, yi + 1) * u * v; };
}
const N = noise2(7);
const fbm = (x, y) => { let a = 0.5, f = 1, s = 0; for (let o = 0; o < 5; o++) { s += a * N(x * f, y * f); f *= 2; a *= 0.5; } return s; };
const terrainH = (x, z) => (fbm(x * 0.012 + 3, z * 0.012 + 9) - 0.45) * 38 * (0.35 + 0.65 * Math.min(1, Math.hypot(x, z) / 120));
function terrainMesh(res, size = 400) {
  const n = res + 1, pos = new Float32Array(n * n * 3), uv = new Float32Array(n * n * 2), nor = new Float32Array(n * n * 3);
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const x = (i / res - 0.5) * size, z = (j / res - 0.5) * size, k = j * n + i;
    pos.set([x, terrainH(x, z), z], k * 3); uv.set([i / res * 40, j / res * 40], k * 2); }
  for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const k = j * n + i;
    const hl = pos[(j * n + Math.max(0, i - 1)) * 3 + 1], hr = pos[(j * n + Math.min(res, i + 1)) * 3 + 1], hd = pos[(Math.max(0, j - 1) * n + i) * 3 + 1], hu = pos[(Math.min(res, j + 1) * n + i) * 3 + 1];
    const dx = size / res * 2, nx = hl - hr, nz = hd - hu, ny = dx; const l = Math.hypot(nx, ny, nz); nor.set([nx / l, ny / l, nz / l], k * 3); }
  const idx = new Uint32Array(res * res * 6); let q = 0;
  for (let j = 0; j < res; j++) for (let i = 0; i < res; i++) { const a = j * n + i, b = a + 1, c = a + n, d = c + 1; idx.set([a, c, b, b, c, d], q); q += 6; }
  return { pos, uv, nor, idx };
}
function rockMesh(sub) { // displaced icosphere-ish via subdivided cube sphere
  const faces = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]], n = sub + 1;
  const P = [], U = [], I = []; const rn = noise2(11);
  faces.forEach((f, fi) => { const ax = f[0] ? [0, 1, 0] : [1, 0, 0], ay = f[2] ? [0, 1, 0] : [0, 0, 1]; const base = P.length / 3;
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) { const u = i / sub * 2 - 1, v = j / sub * 2 - 1;
      const p = [f[0] + ax[0] * u + ay[0] * v, f[1] + ax[1] * u + ay[1] * v, f[2] + ax[2] * u + ay[2] * v]; const l = Math.hypot(...p); const q = p.map((c) => c / l);
      const disp = 1 + 0.38 * (rn(q[0] * 2.3 + 5, q[1] * 2.3 + q[2] * 2.1) - 0.5) + 0.12 * (rn(q[0] * 6 + 1, q[2] * 6 + q[1] * 5) - 0.5);
      P.push(q[0] * disp * 1.1, q[1] * disp * 0.8, q[2] * disp); U.push((q[0] * 0.5 + 0.5 + fi) * 0.6, q[1] * 0.5 + 0.5 + q[2] * 0.3); }
    for (let j = 0; j < sub; j++) for (let i = 0; i < sub; i++) { const a = base + j * n + i, b = a + 1, c = a + n, d = c + 1; I.push(a, b, c, b, d, c); } });
  const pos = new Float32Array(P), idx = new Uint32Array(I), nor = new Float32Array(pos.length);
  for (let t = 0; t < idx.length; t += 3) { const [a, b, c] = [idx[t], idx[t + 1], idx[t + 2]]; const A = [pos[a*3], pos[a*3+1], pos[a*3+2]], B = [pos[b*3], pos[b*3+1], pos[b*3+2]], C = [pos[c*3], pos[c*3+1], pos[c*3+2]]; const e1 = [B[0]-A[0], B[1]-A[1], B[2]-A[2]], e2 = [C[0]-A[0], C[1]-A[1], C[2]-A[2]]; const n = [e1[1]*e2[2]-e1[2]*e2[1], e1[2]*e2[0]-e1[0]*e2[2], e1[0]*e2[1]-e1[1]*e2[0]]; const cen = [(A[0]+B[0]+C[0])/3, (A[1]+B[1]+C[1])/3, (A[2]+B[2]+C[2])/3]; if (n[0]*cen[0]+n[1]*cen[1]+n[2]*cen[2] < 0) { idx[t+1] = c; idx[t+2] = b; } }
  for (let t = 0; t < idx.length; t += 3) { const [a, b, c] = [idx[t], idx[t + 1], idx[t + 2]]; const A = pos.subarray(a * 3, a * 3 + 3), B = pos.subarray(b * 3, b * 3 + 3), C = pos.subarray(c * 3, c * 3 + 3);
    const e1 = [B[0] - A[0], B[1] - A[1], B[2] - A[2]], e2 = [C[0] - A[0], C[1] - A[1], C[2] - A[2]]; const nn = [e1[1] * e2[2] - e1[2] * e2[1], e1[2] * e2[0] - e1[0] * e2[2], e1[0] * e2[1] - e1[1] * e2[0]];
    for (const v of [a, b, c]) { nor[v * 3] += nn[0]; nor[v * 3 + 1] += nn[1]; nor[v * 3 + 2] += nn[2]; } }
  for (let v = 0; v < nor.length; v += 3) { const l = Math.hypot(nor[v], nor[v + 1], nor[v + 2]) || 1; nor[v] /= l; nor[v + 1] /= l; nor[v + 2] /= l; }
  return { pos, uv: new Float32Array(U), nor, idx };
}
async function writeGlb(name, m, plain = false) {
  await MeshoptEncoder.ready;
  const doc = new Document(); const buf = doc.createBuffer(); const scene = doc.createScene();
  const mk = (arr, type) => doc.createAccessor().setArray(arr).setType(type).setBuffer(buf);
  const prim = doc.createPrimitive().setAttribute('POSITION', mk(m.pos, 'VEC3')).setAttribute('NORMAL', mk(m.nor, 'VEC3')).setAttribute('TEXCOORD_0', mk(m.uv, 'VEC2')).setIndices(mk(m.idx, 'SCALAR'));
  const mesh = doc.createMesh(name).addPrimitive(prim); scene.addChild(doc.createNode(name).setMesh(mesh));
  if (!plain) doc.createExtension(EXTMeshoptCompression).setRequired(true).setEncoderOptions({ method: EXTMeshoptCompression.EncoderMethod.FILTER });
  if (!plain) await doc.transform(meshopt({ encoder: MeshoptEncoder, level: 'medium' }));
  const io = new NodeIO().registerExtensions([EXTMeshoptCompression]).registerDependencies({ 'meshopt.encoder': MeshoptEncoder }); const bytes = await io.writeBinary(doc);
  fs.writeFileSync(path.join(OUT, name + '.glb'), bytes);
  report.push({ file: name + '.glb', bytes: bytes.length, tris: m.idx.length / 3, verts: m.pos.length / 3 });
  console.log(name, bytes.length, 'tris', m.idx.length / 3);
}
if (!process.env.PHOTO_ONLY && process.env.GEO_ONLY) { await writeGlb('terrain_lod1_plain', terrainMesh(48), true); await writeGlb('terrain_lod0_plain', terrainMesh(192), true); await writeGlb('rock_lod1_plain', rockMesh(8), true); await writeGlb('rock_lod0_plain', rockMesh(14), true); }
await writeGlb('terrain_lod1', terrainMesh(48));
await writeGlb('terrain_lod0', terrainMesh(192));
await writeGlb('rock_lod1', rockMesh(8));
await writeGlb('rock_lod0', rockMesh(14));
if (TEX || process.env.PHOTO_ONLY) fs.writeFileSync(path.join(OUT, process.env.PHOTO_ONLY ? '_photo-report.json' : '_asset-report.json'), JSON.stringify(report, null, 1)); else fs.writeFileSync(path.join(OUT, '_geo-report.json'), JSON.stringify(report, null, 1));
fs.writeFileSync(path.join(OUT, '_terrain-fn.txt'), 'terrainH(x,z)=(fbm(x*0.012+3,z*0.012+9)-0.45)*38*(0.35+0.65*min(1,hypot(x,z)/120)); size 400; value-noise seed 7, 5 octaves');
console.log('done');
