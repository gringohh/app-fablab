/*
  Service worker du tableau de bord des projets STI2D
  © 2026 H. Hammadou – Tous droits réservés.

  Rôle : garder une copie de l'application sur la tablette ou l'ordinateur
  pour qu'elle s'ouvre même sans réseau, une fois installée.
  - Les fichiers de l'application sont servis depuis le cache, puis mis à jour
    en arrière-plan (la nouvelle version s'affiche au lancement suivant).
  - Les adresses /api/ (mode serveur du lycée) ne sont jamais mises en cache.
  - Aucune donnée de projet ne transite par ici : les projets restent dans le navigateur.
*/
const CACHE = 'projets-sti2d-v1';
const FICHIERS = ['./', 'index.html', 'manifest.webmanifest',
  'icones/icone-192.png', 'icones/icone-512.png', 'icones/icone-maskable-512.png', 'icones/apple-touch-icon.png'];

// Installation : mise en cache des fichiers de l'application
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FICHIERS)).then(() => self.skipWaiting()));
});

// Activation : suppression des anciennes versions du cache
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(cles => Promise.all(cles.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

// Requêtes : cache d'abord, mise à jour en arrière-plan
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin || url.pathname.includes('/api/')) return;
  e.respondWith(caches.open(CACHE).then(async cache => {
    // « ?projet=… » (lien de la page professeur) : on sert la même page d'accueil
    const cle = url.search ? url.pathname : e.request;
    const enCache = await cache.match(cle);
    const reseau = fetch(e.request).then(r => {
      if (r.ok && !url.search) cache.put(e.request, r.clone());
      return r;
    }).catch(() => enCache);
    return enCache || reseau;
  }));
});
