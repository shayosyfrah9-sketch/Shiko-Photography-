const { chromium, devices } = require('playwright'); const fs = require('fs');
(async () => {
  const kind = process.env.KIND || 'desktop';
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await b.newContext(kind === 'phone' ? { ...devices['iPhone 13'] } : { viewport: { width: 800, height: 500 } });
  await ctx.route('https://cdn.jsdelivr.net/npm/three@0.181.0/**', async (r) => { const u = new URL(r.request().url()); const resp = await fetch('http://localhost:8099/__three/' + u.pathname.replace('/npm/three@0.181.0/', '')); r.fulfill({ status: resp.status, body: Buffer.from(await resp.arrayBuffer()), headers: { 'content-type': 'text/javascript', 'access-control-allow-origin': '*', 'timing-allow-origin': '*' } }); });
  const p = await ctx.newPage(); const logs = []; const pass = [];
  const ck = (n, ok, d) => { pass.push({ n, ok: !!ok, d }); console.log(ok ? 'PASS' : 'FAIL', n, d === undefined ? '' : JSON.stringify(d)); };
  p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text().slice(0, 250)); }); p.on('pageerror', (e) => logs.push('PAGEERROR: ' + e.message.slice(0, 300)));
  await p.goto('http://localhost:8099/', { waitUntil: 'domcontentloaded' });
  ck('first frame', await p.waitForFunction(() => window.__tp?.state?.firstFrame, null, { timeout: 120000 }).then(() => true).catch(() => false));
  ck('zone B streamed', await p.waitForFunction(() => window.__tp?.state?.zoneBReady, null, { timeout: 200000 }).then(() => true).catch(() => false), await p.evaluate(() => window.__tp.api.results().zoneBStreamMs));
  const jc0=(sel)=>p.evaluate((s)=>document.querySelector(s).click(),sel);
  // tier buttons
  for (const t of [0, 1, 2, 3]) { await jc0(`[data-tier="${t}"]`); const ok = await p.waitForFunction((t) => window.__tp.state['ready_' + window.__tp.api.tiers[t].key], t, { timeout: 150000 }).then(() => true).catch(() => false); ck('tier ' + t + ' loads', ok, await p.evaluate(() => { const s = window.__tp.api.snapshot(); return { calls: s.drawCalls, tris: s.triangles, tex: s.textures, geo: s.geometries, assets: s.assetsBytes }; })); await p.waitForTimeout(3000); if (t === 3) await p.screenshot({ path: `/tmp/claude-0/tp/${kind}-tier3.png` }); }
  await p.evaluate(()=>window.__tp.api.setTier(1)); await p.waitForTimeout(4000);
  const jc=(sel)=>p.evaluate((s)=>document.querySelector(s).click(),sel);
  // fly to B
  await jc('#bFly'); await p.waitForTimeout(1500); ck('fly button flips', (await p.textContent('#bFly')).includes('A'));
  // photo toggle
  await jc('#bPhoto'); await p.waitForTimeout(4000); ck('photo toggle to JPG', (await p.textContent('#bPhoto')) === 'JPG', await p.evaluate(() => window.__tp.dbg && 1));
  await jc('#bPhoto'); await p.waitForTimeout(3000);
  // details panel
  await jc('#details summary'); await p.waitForTimeout(1500); await p.screenshot({ path: `/tmp/claude-0/tp/${kind}-details.png` });
  // benchmark
  await jc('#bBench'); const t0 = Date.now(); const done = await p.waitForFunction(() => !document.getElementById('bBench').disabled, null, { timeout: 400000 }).then(() => true).catch(() => false);
  const bench = await p.evaluate(() => window.__tp.bench); ck('benchmark finishes (4 tiers)', done && bench && bench.length === 4, { sec: Math.round((Date.now() - t0) / 1000), bench });
  await jc('#bCopy'); await p.waitForTimeout(1500); const out = await p.inputValue('#out'); let j = null; try { j = JSON.parse(out); } catch (_) {}
  ck('copy results produces valid JSON', !!j && j.benchmark.length === 4 && j.device && j.timeline.length > 5, j && { keys: Object.keys(j), bytes: out.length });
  if (j) fs.writeFileSync(`/tmp/claude-0/tp/results-${kind}.json`, JSON.stringify(j, null, 1));
  await p.screenshot({ path: `/tmp/claude-0/tp/${kind}-after.png` });
  ck('no page errors', !logs.some((l) => l.startsWith('PAGEERROR')), logs.slice(0, 5));
  fs.writeFileSync(`/tmp/claude-0/tp/func-${kind}.json`, JSON.stringify({ pass, logs }, null, 1)); await b.close(); console.log('done');
})();
