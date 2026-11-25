// Repeatable measurement run (software renderer: load phases / bytes / long tasks are meaningful as RELATIVE numbers, fps is not).
// env: KIND=desktop|phone  TIER=0..3  RUNS=n  BENCH=1  LABEL=before|after  OUT=dir
const { chromium, devices } = require('playwright'); const fs = require('fs');
const KIND = process.env.KIND || 'desktop', TIER = process.env.TIER || (KIND === 'phone' ? '1' : '2'), RUNS = +(process.env.RUNS || 3), BENCH = process.env.BENCH === '1', LABEL = process.env.LABEL || 'run', OUT = process.env.OUT || __dirname + '/../baseline';
const URL = process.env.URL || 'http://localhost:8099/';
(async () => {
  fs.mkdirSync(OUT, { recursive: true }); const all = [];
  for (let r = 0; r < RUNS + (BENCH ? 1 : 0); r++) {
    const doBench = BENCH && r === RUNS;
    const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
    const ctx = await b.newContext(KIND === 'phone' ? { ...devices['iPhone 13'] } : { viewport: { width: 1280, height: 800 } });
    await ctx.route('https://cdn.jsdelivr.net/npm/three@0.181.0/**', async (rt) => { const u = new globalThis.URL(rt.request().url()); const resp = await fetch('http://localhost:8099/__three/' + u.pathname.replace('/npm/three@0.181.0/', '')); rt.fulfill({ status: resp.status, body: Buffer.from(await resp.arrayBuffer()), headers: { 'content-type': 'text/javascript', 'access-control-allow-origin': '*', 'timing-allow-origin': '*' } }); });
    const p = await ctx.newPage(); const errs = []; p.on('pageerror', (e) => errs.push(e.message.slice(0, 200)));
    await p.goto(URL + '?tier=' + TIER, { waitUntil: 'domcontentloaded' });
    await p.waitForFunction(() => window.__tp && window.__tp.abs && window.__tp.abs.worldComplete, null, { timeout: 280000 }).catch(() => console.log('world not complete'));
    await p.waitForTimeout(2500);
    const rec = await p.evaluate(async (doBench) => { if (doBench) await window.__tp.api.runBench(); return window.__tp.api.results(); }, doBench);
    rec.errors = errs; rec.run = r; rec.kind = KIND; rec.tierParam = TIER; rec.label = LABEL; rec.benchRun = doBench; all.push(rec);
    console.log(KIND, 'tier', TIER, 'run', r, JSON.stringify({ phases: rec.phases, lt: rec.longTasks && { boot: rec.longTasks.boot, loading: rec.longTasks.loading }, bytes: { total: rec.bytes.total, ff: rec.bytes.beforeFirstFrame, wc: rec.bytes.beforeWorldComplete, cat: rec.bytes.byCategory }, errs: errs.length }));
    await b.close();
  }
  fs.writeFileSync(`${OUT}/${LABEL}-${KIND}-tier${TIER}.json`, JSON.stringify(all, null, 1));
})();
