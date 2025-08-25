const CACHE_NAME = "vente-cache-v1";
const API_CACHE_NAME = "vente-api-cache-v1";
const urlsToCache = [
  "/",                       // page d'accueil
  "/static/offline/offline.html",            // page hors-ligne
  "/static/icons/10023618.png",// logo
  "/static/js/offline-sales.js"
];

// Installation
self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
        .then(() => self.skipWaiting())
    );
});

// Activation
self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(names => Promise.all(
            names.map(name => {
                if(name !== CACHE_NAME && name !== API_CACHE_NAME) return caches.delete(name);
            })
        ))
    );
    return self.clients.claim();
});

// Fetch : réponse hors-ligne
self.addEventListener("fetch", event => {
    // Ne gérer que les requêtes GET
    if (event.request.method !== 'GET') {
        // Pour les requêtes POST (comme les ventes), on essaie de les mettre en file d'attente
        if (event.request.url.includes('/api/ventes/ajouter/')) {
            event.respondWith(
                fetch(event.request.clone())
                .catch(() => {
                    // En cas d'échec, on retourne une réponse indiquant que la vente est stockée hors ligne
                    return new Response(JSON.stringify({ offline: true }), {
                        headers: { 'Content-Type': 'application/json' }
                    });
                })
            );
        }
        return;
    }

    event.respondWith(
        caches.match(event.request).then(response => {
            if (response) return response;

            // Stratégie de cache pour les API
            if (event.request.url.includes('/api/')) {
                return fetch(event.request)
                    .then(res => {
                        // Ne mettre en cache que les réponses réussies
                        if (!res || res.status !== 200) {
                            return res;
                        }

                        const responseToCache = res.clone();
                        caches.open(API_CACHE_NAME).then(cache => {
                            cache.put(event.request, responseToCache);
                        });

                        return res;
                    })
                    .catch(() => {
                        // En cas d'échec, essayer de récupérer depuis le cache API
                        return caches.match(event.request, { cacheName: API_CACHE_NAME });
                    });
            }

            // Pour les autres ressources
            return fetch(event.request)
                .then(res => {
                    // Ne pas mettre en cache les réponses d'erreur
                    if (!res || res.status !== 200) {
                        return res;
                    }

                    return caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, res.clone());
                        return res;
                    });
                })
                .catch(() => {
                    // Pour les requêtes de navigation, retourner la page hors ligne
                    if (event.request.mode === "navigate") {
                        return caches.match("/static/offline/offline.html");
                    }
                    // Pour les autres ressources, retourner une réponse vide
                    return new Response('', { status: 503 });
                });
        })
    );
});