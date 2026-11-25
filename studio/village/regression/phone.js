const fs=require('fs');const {open,enter,E,WA}=require('./lib');
const only=process.env.ONLY?process.env.ONLY.split(','):null;
(async()=>{
 const {b,p,log}=await open('phone'); const R={kind:'phone',steps:[],rooms:[],t0:new Date().toISOString()};
 const step=(n,ok,d)=>{R.steps.push({n,ok,d});console.log(ok?'PASS':'FAIL',n,d||'');};
 step('gate → village',await enter(p));
 const hamb=await p.$('#hamb'); step('hamburger present (phone menu)',!!hamb&&await hamb.isVisible());
 let menuRetries=0; async function openMenu(){ for(let a=0;a<3;a++){ const on=await p.evaluate(()=>document.getElementById('mnu').classList.contains('on')); if(!on) await p.evaluate(()=>document.getElementById('hamb').click()); const ok=await p.waitForSelector('#mnu.on',{timeout:5000}).then(()=>true).catch(()=>false); if(ok){ await p.waitForTimeout(500); return; } menuRetries++; } throw new Error('menu did not open after 3 attempts'); }
 async function room(hi,ri,hall,s,lang){
  const rec={hall:hall.key,id:s.id,title:s.title,expected:s.photos.length,lang,checks:{}};
  try{
   await openMenu();
   rec.menuTitle=await p.evaluate(([hi,ri])=>{const c=document.querySelectorAll('#mnu .mn-cat')[hi];c.querySelector('.mn-h').click();const it=c.querySelectorAll('.mn-r')[ri];const t=it.innerText.replace(/\s+/g,' ');setTimeout(()=>it.click(),500);return t;},[hi,ri]);
   if(s.placeholder){ await p.waitForTimeout(3000); rec.view=await p.evaluate(()=>document.body.className+' | mroomHidden='+document.getElementById('mroom').hidden); rec.checks.noCrash=true; return rec; }
   await p.waitForSelector('#mroom.in',{timeout:20000}); await p.waitForTimeout(800);
   for(let k=0;k<40;k++){ const done=await p.evaluate(()=>{const sc=document.getElementById('mrSc');sc.scrollTop+=sc.clientHeight*0.8;return sc.scrollTop+sc.clientHeight>=sc.scrollHeight-2;}); await p.waitForTimeout(250); if(done)break; }
   await p.waitForTimeout(2500);
   const d=await p.evaluate(()=>{const ims=[...document.querySelectorAll('#mrSc .mr-t img')];
     return {ids:ims.map(i=>(i.getAttribute('src')||'').replace(/^.*\//,'').replace(/\.jpg.*$/,'')),broken:ims.filter(i=>!(i.complete&&i.naturalWidth>0)).length,
       gal:[...document.querySelectorAll('#mroom a[data-a=gal]')].map(a=>a.href),bot:[...document.querySelectorAll('#mrBot a')].map(a=>a.href),
       title:document.getElementById('mrT').textContent,n:document.getElementById('mrN').textContent,dir:document.getElementById('mroom').dir,
       endBtns:[...document.querySelectorAll('#mroom .mr-end button,#mroom .mr-end a')].map(x=>x.textContent.trim())};});
   rec.n=d.ids.length; rec.broken=d.broken; rec.title=d.title; rec.dir=d.dir; rec.endBtns=d.endBtns; rec.gal=d.gal;
   rec.checks.count=d.ids.length===s.photos.length;
   rec.checks.order=JSON.stringify(d.ids)===JSON.stringify(s.photos);
   rec.checks.allLoaded=d.broken===0;
   rec.checks.title=d.title===s.title;
   rec.checks.galleryLink=s.link?(d.gal.includes(s.link)&&d.bot.includes(s.link)):(d.gal.length===0&&d.bot.length===0);
   rec.checks.bookBtn=d.endBtns.length>=2;
   if(!rec.checks.order){ rec.orderDiff=d.ids.map((x,i)=>x===s.photos[i]?null:i).filter(x=>x!==null).slice(0,5); }
   await p.evaluate(()=>{document.getElementById('mrSc').scrollTop=0;}); await p.waitForTimeout(300);
   await (await p.$('#mrSc .mr-t')).click(); await p.waitForTimeout(1500);
   rec.checks.lightbox=await p.evaluate(()=>!document.getElementById('lb').hidden);
   await p.click('#lbX').catch(()=>{}); await p.waitForTimeout(500);
   await p.click('#mrX'); await p.waitForTimeout(1200);
   rec.checks.closes=await p.waitForFunction(()=>document.getElementById('mroom').hidden,null,{timeout:6000}).then(()=>true).catch(()=>false);
  }catch(e){ rec.error=e.message.split('\n')[0]; rec.checks.noError=false; try{await p.click('#mrX',{timeout:2000});}catch(_){} }
  return rec; }
 let hi=0; for(const h of E){ let ri=0; for(const s of h.sets){ if(!only||only.includes(s.id)){ const r=await room(hi,ri,h,s,'he'); R.rooms.push(r); const bad=Object.entries(r.checks).filter(([k,v])=>!v).map(([k])=>k); console.log(bad.length?'FAIL':'PASS','room',s.id,r.n+'/'+s.photos.length,bad.join(',')||'',r.error||'',r.view||''); await p.screenshot({path:'shots/phone-'+s.id+'.png'}).catch(()=>{}); } ri++; } hi++; }
 R.menuRetries=menuRetries; console.log('menuRetries',menuRetries); fs.writeFileSync('phone-results.json',JSON.stringify({R,log},null,1));
 await b.close(); console.log('done');
})();
