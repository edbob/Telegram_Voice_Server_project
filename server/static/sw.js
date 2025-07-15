//PWA Service Worker
self.addEventListener('install', e => {
  const assets = [
    '/',
    '/static/css/style.css',
    '/static/script/script.js'
  ];
  e.waitUntil(
    caches.open('static-cache-v1').then(c => c.addAll(assets))
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(
    caches.match(e.request).then(r => r || fetch(e.request))
  );
});