// Screenshot C3_phone.html at 390x844 @2x with Playwright (chromium). Usage: node C3_phone_shot.js OUT.png
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const out = process.argv[2];
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, locale: 'he-IL' });
  const p = await ctx.newPage();
  await p.goto('file://' + path.join(__dirname, 'C3_phone.html'));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(1500);
  const info = await p.evaluate(() => ({ rubik: document.fonts.check('16px Rubik', 'שלום'), jost: document.fonts.check('16px Jost'),
    fonts: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight) }));
  console.log(JSON.stringify(info));
  await p.screenshot({ path: out });
  await b.close();
})();
