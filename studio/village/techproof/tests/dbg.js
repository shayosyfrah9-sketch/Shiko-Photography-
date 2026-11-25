const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await b.newContext({ viewport: { width: 640, height: 400 } });
  await ctx.route('https://cdn.jsdelivr.net/npm/three@0.181.0/**', async (r) => { const u = new URL(r.request().url()); const resp = await fetch('http://localhost:8099/__three/' + u.pathname.replace('/npm/three@0.181.0/', '')); r.fulfill({ status: resp.status, body: Buffer.from(await resp.arrayBuffer()), headers: { 'content-type': 'text/javascript', 'access-control-allow-origin': '*' } }); });
  const p = await ctx.newPage(); p.on('pageerror', (e) => console.log('PAGEERROR', e.message));
  await p.goto('http://localhost:8099/', { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => window.__tp && window.__tp.state && window.__tp.state.ready_med, null, { timeout: 150000 });
  console.log(JSON.stringify(await p.evaluate(() => { const t = window.__tp.dbg.terrain, g = t.geometry; g.computeBoundingBox(); const bb = g.boundingBox; const m = t.material; return { vis: t.visible, parent: !!t.parent, bb: [bb.min.toArray(), bb.max.toArray()].map(a=>a.map(v=>+v.toFixed(1))), idx: g.index && g.index.count, pos: g.attributes.position.count, posType: g.attributes.position.array.constructor.name, matMap: !!m.map, transparent: m.transparent, opacity: m.opacity, side: m.side, scale: t.scale.toArray(), frustumCulled: t.frustumCulled, sph: g.boundingSphere && g.boundingSphere.radius }; })));
  await b.close();
})();
