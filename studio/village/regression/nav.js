// Desktop navigation + rooms: village -> house -> room -> grid/full gallery link -> back -> house -> home
const fs=require('fs');const {open,enter,waitBody,E}=require('./lib');
const only=process.env.ONLY?process.env.ONLY.split(','):null;
(async()=>{
 const {b,p,log}=await open('desktop'); const R={kind:'desktop-nav',steps:[],rooms:[]};
 const ev=(f,a)=>p.evaluate(f,a); const sleep=t=>p.waitForTimeout(t);
 const step=(n,ok,d)=>{R.steps.push({n,ok:!!ok,d});console.log(ok?'PASS':'FAIL',n,d===undefined?'':JSON.stringify(d));};
 step('gate → village',await enter(p));
 async function selectHall(i){ for(let k=0;k<6;k++){ const no=await ev(()=>document.getElementById('hNo').textContent); const cur=parseInt(no); if(cur===i+1) return true; await ev(()=>document.getElementById('hNext').click()); await p.waitForFunction(c=>parseInt(document.getElementById('hNo').textContent)!==c,cur,{timeout:8000}).catch(()=>{}); await sleep(1200);} return false; }
 for(let hi=0;hi<E.length;hi++){ const h=E[hi];
  if(only&&!h.sets.some(s=>only.includes(s.id))&&!(only.includes('video')&&h.key==='video')) continue;
  let okSel=await selectHall(hi); step('select house '+h.key,okSel);
  await ev(()=>document.getElementById('hEnter').click());
  const inHall=await waitBody(p,'v-hall|v-room',40000); await sleep(2500);
  if(h.sets[0].placeholder){ step('video house enters (empty/coming soon room)',inHall,await ev(()=>document.body.className)); await p.screenshot({path:'shots/desktop-video.png'}).catch(()=>{}); await ev(()=>document.getElementById('home').click()); await waitBody(p,'v-entrance',20000); await sleep(2500); continue; }
  const cards=await ev(()=>[...document.querySelectorAll('#hallCards > *')].map(c=>c.textContent.trim()));
  step('house '+h.key+' shows '+(h.key==='sport'?'3 sport groups (football/basketball/surfing)':h.sets.length+' room cards'),h.key==='sport'?cards.length===3:cards.length===h.sets.length,cards);
  for(let ri=0;ri<h.sets.length;ri++){ const s=h.sets[ri]; if(only&&!only.includes(s.id)) continue; const rec={id:s.id,checks:{}};
   try{
    if(h.key==='sport'){ const sm={matchday:[0,0],rishon:[1,0],miluim:[1,1],surf:[2,null]}[s.id]; await ev(i=>document.querySelectorAll('#hallCards > *')[i].click(),sm[0]); await sleep(3500); if(sm[1]!==null){ await ev(i=>document.querySelectorAll('#hallCards > *')[i].click(),sm[1]); } }
    else await ev(i=>document.querySelectorAll('#hallCards > *')[i].click(),ri);
    rec.checks.entersRoom=await waitBody(p,'v-room',40000); await sleep(2500);
    const sc=await ev(()=>document.getElementById('sCount').textContent); rec.sCount=sc;
    rec.checks.counter=new RegExp('/ 0*'+s.photos.length+'$').test(sc);
    await ev(()=>document.getElementById('sNext').click()); await sleep(1200); await ev(()=>document.getElementById('sNext').click()); await sleep(1200);
    rec.checks.stepsForward=(await ev(()=>document.getElementById('sCount').textContent)).startsWith('03');
    await ev(()=>document.getElementById('sPrev').click()); await sleep(1000);
    rec.checks.stepsBack=(await ev(()=>document.getElementById('sCount').textContent)).startsWith('02');
    await ev(()=>document.querySelector('.vt-b[data-v=grid]').click()); await sleep(3500);
    const g=await ev(()=>({hidden:document.getElementById('gal').hidden,title:document.getElementById('gTitle').textContent,linkHidden:document.getElementById('gLink').hidden,link:document.getElementById('gLink').href,srcs:[...document.querySelectorAll('#gal img')].map(i=>i.getAttribute('src')||i.dataset.src||''),broken:[...document.querySelectorAll('#gal img')].filter(i=>i.getAttribute('src')&&i.complete&&i.naturalWidth===0).length}));
    const ids=g.srcs.map(x=>x.replace(/^.*\//,'').replace(/(-sm)?\.(jpg|webp).*$/,'')).filter(x=>s.photos.includes(x));
    rec.gridIds=ids.length; rec.gridBroken=g.broken;
    rec.checks.gridOpens=!g.hidden;
    rec.checks.gridOrder=JSON.stringify(ids)===JSON.stringify(s.photos);
    rec.checks.gridTitle=g.title===s.title;
    rec.checks.fullGalleryLink=s.link?(!g.linkHidden&&g.link===s.link):g.linkHidden;
    if(!rec.checks.gridOrder) rec.gridNote={got:ids.length,want:s.photos.length,srcsSample:g.srcs.slice(0,3)};
    await ev(()=>document.querySelector('.vt-b[data-v="3d"]').click()); await sleep(1200);
    await ev(()=>document.getElementById('navBack').click());
    rec.checks.backToHouse=await waitBody(p,'v-hall',20000); await sleep(1500);
   }catch(e){ rec.error=e.message.split('\n')[0]; rec.checks.noError=false; }
   R.rooms.push(rec); const bad=Object.entries(rec.checks).filter(([k,v])=>!v).map(([k])=>k); console.log(bad.length?'FAIL':'PASS','room',s.id,rec.sCount,'grid',rec.gridIds+'/'+s.photos.length,bad.join(',')||'',rec.error||'');
   if(h.key==='sport'||!(await ev(()=>/v-hall/.test(document.body.className)))){ await ev(()=>document.getElementById('home').click()); await waitBody(p,'v-entrance',20000); await sleep(2500); await selectHall(hi); await ev(()=>document.getElementById('hEnter').click()); await waitBody(p,'v-hall',30000); await sleep(2500); }
  }
  await ev(()=>document.getElementById('hBack').click()); const home=await waitBody(p,'v-entrance',30000); step('house '+h.key+' → home (button) returns to village',home); await sleep(2500);
 }
 R.log=log; fs.writeFileSync('nav-results'+(only?'-partial':'')+'.json',JSON.stringify(R,null,1));
 console.log('LOG',JSON.stringify({pageerrors:log.pageerrors,console:log.console,failed:log.failed,http:log.http}).slice(0,1200));
 await b.close(); console.log('done');
})();
