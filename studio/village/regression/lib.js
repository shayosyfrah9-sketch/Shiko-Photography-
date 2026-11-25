const { chromium, devices } = require('playwright');
const E = require('./expected.js')('index.html');
const WA='972544351955';
async function open(kind){
  const args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'];
  const b=await chromium.launch({args});
  const opts=kind==='phone'?{...devices['iPhone 13']}:{viewport:{width:1280,height:800}};
  const ctx=await b.newContext({...opts,serviceWorkers:'block',locale:'he-IL'});
  const log={pageerrors:[],console:[],failed:[],http:[],popups:[],waReq:[]};
  await ctx.route(/wa\.me|whatsapp\.com|api\.whatsapp/,r=>{log.waReq.push(r.request().url());r.abort();});
  const p=await ctx.newPage();
  p.on('pageerror',e=>log.pageerrors.push(e.message.slice(0,200)));
  p.on('console',m=>{if(m.type()==='error')log.console.push(m.text().slice(0,200));});
  p.on('requestfailed',r=>{const u=r.url();if(!/wa\.me|whatsapp/.test(u))log.failed.push(u.slice(0,150)+' '+(r.failure()||{}).errorText);});
  p.on('response',r=>{if(r.status()>=400)log.http.push(r.status()+' '+r.url().slice(0,150));});
  ctx.on('page',pg=>{if(pg!==p)log.popups.push(pg.url());});
  return {b,ctx,p,log};
}
async function enter(p){
  await p.goto('https://shikophotography.com/',{waitUntil:'domcontentloaded',timeout:60000});
  await p.waitForTimeout(8000);
  const vp=p.viewportSize(); await p.mouse.click(vp.width/2,vp.height/2);
  const ok=await p.waitForFunction(()=>!/gate-on/.test(document.body.className),null,{timeout:60000}).then(()=>true).catch(()=>false);
  await p.waitForTimeout(2500); return ok;
}
const waitBody=(p,re,t=30000)=>p.waitForFunction(r=>new RegExp(r).test(document.body.className),re,{timeout:t}).then(()=>true).catch(()=>false);
module.exports={open,enter,waitBody,E,WA};
