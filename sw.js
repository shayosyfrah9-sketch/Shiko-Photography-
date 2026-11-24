/* Shiko: keep the site's files on the visitor's device so a second visit opens almost instantly.
   Pages: network first (updates show at once). Files: from the device, refreshed in the background. */
var C="shiko-v2"; /* v154: new name on each big release so visitors drop old files */
self.addEventListener("install",function(e){ self.skipWaiting(); });
self.addEventListener("activate",function(e){ e.waitUntil(caches.keys().then(function(ks){ return Promise.all(ks.filter(function(k){ return /^shiko-/.test(k)&&k!==C; }).map(function(k){ return caches.delete(k); })); }).then(function(){ return self.clients.claim(); })); });
self.addEventListener("fetch",function(e){ var r=e.request; if(r.method!=="GET") return; var u=new URL(r.url);
  if(u.origin!==location.origin||r.headers.has("range")||/\.(mp3|mp4|mov|webm|m4a)$/i.test(u.pathname)) return;
  if(r.mode==="navigate"||/\/$|\.html$/.test(u.pathname)){
    e.respondWith(fetch(r).then(function(res){ if(res.ok){ var c=res.clone(); caches.open(C).then(function(ca){ ca.put(r,c); }); } return res; }).catch(function(){ return caches.match(r); })); return; }
  e.respondWith(caches.open(C).then(function(ca){ return ca.match(r).then(function(hit){
    var net=fetch(r).then(function(res){ if(res.ok&&res.status===200) ca.put(r,res.clone()); return res; });
    if(hit){ e.waitUntil(net.catch(function(){})); return hit; } return net; }); }));
});
