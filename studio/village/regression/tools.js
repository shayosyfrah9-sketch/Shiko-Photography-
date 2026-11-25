// Tools/booking/language test. KIND=phone|desktop
const fs=require('fs');const {open,enter,WA}=require('./lib');
const KIND=process.env.KIND||'phone';
(async()=>{
 const {b,p,log}=await open(KIND); const R={kind:KIND,steps:[]};
 const step=(n,ok,d)=>{R.steps.push({n,ok:!!ok,d});console.log(ok?'PASS':'FAIL',n,d===undefined?'':JSON.stringify(d));};
 const ev=(f,a)=>p.evaluate(f,a);
 const sleep=t=>p.waitForTimeout(t);
 step('gate → village',await enter(p));
 const phone=KIND==='phone';
 async function menuOpen(){ for(let a=0;a<4;a++){ const on=await ev(()=>document.getElementById('mnu').classList.contains('on')); if(!on) await ev(()=>document.getElementById('hamb').click()); const ok=await p.waitForFunction(()=>document.getElementById('mnu').classList.contains('on'),null,{timeout:4000}).then(()=>true).catch(()=>false); if(ok){ await sleep(600); return; } } throw new Error('menu did not open'); }
 const clickTool=async(txtRe)=>{ if(phone){ await menuOpen(); await ev(re=>{[...document.querySelectorAll('#mnu .mn-tools > *')].find(e=>new RegExp(re).test(e.textContent)).click();},txtRe); } };
 // header buttons (desktop) / menu (phone)
 const hdr=await ev(()=>({wa:document.getElementById('waTop').href,mt:document.getElementById('mtTop').href,about:!!document.getElementById('aboutTop'),lang:document.getElementById('lang').textContent}));
 step('WhatsApp link correct',hdr.wa.includes(WA),hdr.wa);
 step('Matcha link correct',/matcha\.photo/.test(hdr.mt),hdr.mt);
 if(phone){ await menuOpen(); const items=await ev(()=>[...document.querySelectorAll('#mnu .mn-tools > *')].map(e=>({t:e.textContent.trim(),h:e.href||''}))); step('phone menu tools',items.length>=6,items); await ev(()=>document.getElementById('hamb').click()); await sleep(600); }
 // About
 if(phone){ await clickTool('מי אני|About'); } else { await ev(()=>document.getElementById('aboutTop').click()); }
 await sleep(2500);
 const vis=(id,cls)=>p.waitForFunction(([id,cls])=>{const e=document.getElementById(id);const r=e.getBoundingClientRect();return getComputedStyle(e).display!=='none'&&r.width>100&&r.height>100&&(!cls||e.classList.contains(cls));},[id,cls],{timeout:10000}).then(()=>true).catch(()=>false);
 step('About opens',await vis('about'),await ev(()=>document.querySelector('#about .ab-lead')?.textContent.slice(0,60)));
 await p.screenshot({path:`shots/${KIND}-about.png`}).catch(()=>{});
 await ev(()=>document.getElementById('aboutX').click()); await sleep(1200);
 step('About closes',await ev(()=>document.getElementById('about').hidden));
 // Booking
 if(phone){ await clickTool('הזמנות|Booking'); } else { await ev(()=>{const h=document.getElementById('hubBook');h.click();}); }
 await sleep(3000);
 step('Booking opens',await vis('book','in'));
 const bk=await ev(()=>({waBig:document.getElementById('waBig').href,tel:[...document.querySelectorAll('#book a[href^="tel:"]')].map(a=>a.href),ig:[...document.querySelectorAll('#book a[href*="instagram"]')].map(a=>a.href),steps:document.getElementById('wzN')?.textContent}));
 step('Booking WhatsApp button href',bk.waBig.includes(WA),bk.waBig); step('Booking phone link',bk.tel.some(t=>t.includes('972544351955')),bk.tel); step('Booking Instagram link',bk.ig.length>0,bk.ig);
 await p.screenshot({path:`shots/${KIND}-booking.png`}).catch(()=>{});
 // wizard (no real send: wa.me is aborted at network level)
 try{
  await ev(()=>document.getElementById('bkGo').click()); await sleep(1500);
  await ev(()=>document.getElementById('wzNext').click()); await sleep(900);
  await p.fill('#fPlace','Test',{timeout:5000}).catch(()=>{}); await p.fill('#fMsg','regression test - do not answer',{timeout:5000}).catch(()=>{});
  await ev(()=>document.getElementById('wzNext').click()); await sleep(900);
  await p.fill('#fName','Regression Test',{timeout:5000}).catch(()=>{}); await p.fill('#fPhone','0500000000',{timeout:5000}).catch(()=>{});
  const before=log.waReq.length+log.popups.length;
  await ev(()=>document.getElementById('wzNext').click()); await sleep(3500);
  const after=log.waReq.concat(log.popups);
  step('Booking wizard submit builds WhatsApp link to correct number (blocked at network, nothing sent)',after.some(u=>u.includes(WA)),after.slice(0,2).map(u=>u.slice(0,120)));
  step('Wizard end state shown',await ev(()=>({n:document.getElementById('wzN')?.textContent,err:document.getElementById('err')?.textContent,hidden:document.getElementById('err')?.hidden})));
 }catch(e){ step('Booking wizard',false,e.message.split('\n')[0]); }
 await ev(()=>document.getElementById('bookX').click()); await sleep(1500);
 step('Booking closes',await ev(()=>document.getElementById('book').hidden));
 // Language
 const L0=await ev(()=>({btn:document.getElementById('lang').textContent,dir:document.documentElement.dir,lang:document.documentElement.lang,bodyDir:document.body.dir}));
 if(phone){ await clickTool('English|עברית'); } else { await ev(()=>document.getElementById('lang').click()); }
 await sleep(1500);
 const L1=await ev(()=>({btn:document.getElementById('lang').textContent,dir:document.documentElement.dir,lang:document.documentElement.lang,hub:document.querySelector('.hublinks')?.innerText.trim().replace(/\s+/g,' '),about:document.getElementById('aboutTop')?.textContent,enter:document.querySelector('#hEnter')?.innerText.trim()}));
 step('Language HE→EN',L1.btn!==L0.btn,{before:L0,after:L1});
 await p.screenshot({path:`shots/${KIND}-english.png`}).catch(()=>{});
 if(phone){ await clickTool('English|עברית'); } else { await ev(()=>document.getElementById('lang').click()); }
 await sleep(1200);
 const L2=await ev(()=>({btn:document.getElementById('lang').textContent,dir:document.documentElement.dir}));
 step('Language EN→HE',L2.btn===L0.btn,L2);
 R.log=log; fs.writeFileSync(`tools-${KIND}-results.json`,JSON.stringify(R,null,1));
 console.log('LOG',JSON.stringify(log).slice(0,1500));
 await b.close(); console.log('done');
})();
