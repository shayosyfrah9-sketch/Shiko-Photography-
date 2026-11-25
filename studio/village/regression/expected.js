const fs=require('fs');
module.exports=function(file){const s=fs.readFileSync(file||'index.html','utf8');
const i=s.indexOf('var ROOMS=[');let d=0,j=i+'var ROOMS='.length;
for(;j<s.length;j++){if(s[j]=='[')d++;else if(s[j]==']'){d--;if(!d)break}}
const R=eval(s.slice(i+'var ROOMS='.length,j+1));
return R.map(h=>{let sets=h.sets||[];if(h.groups){sets=[];h.groups.forEach(g=>g.sets.forEach(x=>sets.push(x)));}
 if(!sets.length)sets=[{id:h.key+'-soon',title:h.key==='video'?'Showreel':'Coming Soon',photos:[],placeholder:true}];
 return {key:h.key,sets:sets.map(x=>({id:x.id,title:x.title,link:x.link||'',placeholder:!!x.placeholder,photos:(x.photos||[]).map(p=>p[0])}))};});};
