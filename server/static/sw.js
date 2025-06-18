self.addEventListener('install', e => {
  const assets = ['./', '/static/style.css', '/static/script.js'];
  e.waitUntil(caches.open('static-cache-v1').then(c => c.addAll(assets)));
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});