/*
  Service worker de Relais Drive.

  Deux rôles :
  1. Garder une copie de l'application pour qu'elle s'ouvre vite une fois installée.
  2. Recevoir les fichiers envoyés depuis le menu « Partager » d'Android
     (Fichiers → sélectionner un .zip → Partager → Relais Drive) : ils sont
     rangés temporairement dans un cache, puis l'application les récupère.
*/
const CACHE = 'relais-drive-v1';    // changer ce numéro force la mise à jour
const CACHE_PARTAGE = 'relais-drive-partage';
const FICHIERS = ['./', 'index.html', 'manifest.webmanifest',
  'icones/icone-192.png', 'icones/icone-512.png', 'icones/icone-maskable-512.png'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FICHIERS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(cles => Promise.all(cles.filter(k => k !== CACHE && k !== CACHE_PARTAGE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.origin !== location.origin) return;

  // Fichiers reçus par le menu « Partager »
  if (e.request.method === 'POST' && url.pathname.endsWith('/partage')) {
    e.respondWith((async () => {
      const donnees = await e.request.formData();
      const fichiers = donnees.getAll('fichiers').filter(f => f && typeof f !== 'string');
      const cache = await caches.open(CACHE_PARTAGE);
      for (const ancienne of await cache.keys()) await cache.delete(ancienne);
      let i = 0;
      for (const f of fichiers) {
        await cache.put(new Request('partage-fichier/' + (i++)), new Response(f, {
          headers: { 'Content-Type': f.type || 'application/octet-stream', 'X-Nom': encodeURIComponent(f.name || 'fichier') }
        }));
      }
      return Response.redirect('./?partage=' + i, 303);
    })());
    return;
  }

  if (e.request.method !== 'GET') return;
  // Application : cache d'abord, mise à jour en arrière-plan
  e.respondWith(caches.open(CACHE).then(async cache => {
    const cle = url.search ? url.pathname : e.request;
    const enCache = await cache.match(cle);
    const reseau = fetch(e.request).then(r => {
      if (r.ok && !url.search) cache.put(e.request, r.clone());
      return r;
    }).catch(() => enCache);
    return enCache || reseau;
  }));
});
