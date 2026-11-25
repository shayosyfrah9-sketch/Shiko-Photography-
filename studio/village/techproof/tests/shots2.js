const { chromium, devices } = require('playwright');
(async () => {
  const kind = process.env.KIND || 'desktop', tiers = (process.env.TIERS || '0,2').split(',').map(Number), ts = (process.env.TS || '0.06,0.5').split(',').map(Number);
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const ctx = await b.newContext(kind === 'phone' ? { ...devices['iPhone 13'] } : { viewport: { width: 1280, height: 720 } });
  await ctx.route('https://cdn.jsdelivr.net/npm/three@0.181.0/**', async (r) => { const u = new URL(r.request().url()); const resp = await fetch('http://localhost:8099/__three/' + u.pathname.replace('/npm/three@0.181.0/', '')); r.fulfill({ status: resp.status, body: Buffer.from(await resp.arrayBuffer()), headers: { 'content-type': 'text/javascript', 'access-control-allow-origin': '*', 'timing-allow-origin': '*' } }); });
  const p = await ctx.newPage(); const logs = [];
  p.on('console', (m) => { if (m.type() === 'error') logs.push(m.text().slice(0, 250)); }); p.on('pageerror', (e) => logs.push('PAGEERROR: ' + e.message.slice(0, 300)));
  await p.goto('http://localhost:8099/', { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => window.__tp && window.__tp.state && window.__tp.state.zoneBReady, null, { timeout: 200000 }).catch(() => console.log('zone B not ready'));
  await p.evaluate(() => { window.__tp.api.setAuto(false); document.getElementById('bHide').click(); });
  for (const t of tiers) {
    await p.evaluate((t) => window.__tp.api.setTier(t), t); await p.waitForFunction((t) => window.__tp.state['ready_' + window.__tp.api.tiers[t].key], t, { timeout: 120000 }).catch(() => {});
    for (const x of ts) {
      await p.evaluate((x) => window.__tp.api.setT(x), x); await p.waitForTimeout(t >= 2 ? 22000 : 8000);
      await p.screenshot({ path: `/tmp/claude-0/tp/final-${kind}-t${t}-c${String(x).replace('.', '')}.png` });
      console.log(kind, 'tier', t, 'cam', x, JSON.stringify(await p.evaluate(() => { const s = window.__tp.api.snapshot(); return { calls: s.drawCalls, tris: s.triangles, tex: s.textures, geo: s.geometries, assets: s.assetsBytes, fps: s.fps }; })));
    }
  }
  console.log(logs.join('\n')); await b.close();
})();
