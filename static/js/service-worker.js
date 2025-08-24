const CACHE_NAME = "vente-cache-v1";
const urlsToCache = [
  "/",                       // page d'accueil
  ""/static/offline/offline.html"",            // page hors-ligne
  "/static/icons/10023618.png",// logo
  "/static/js/offline-sales.js"
];

// Installation
self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(urlsToCache))
    );
});

// Activation
self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys().then(names => Promise.all(
            names.map(name => { if(name !== CACHE_NAME) return caches.delete(name); })
        ))
    );
});

// Fetch : réponse hors-ligne
self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            if (response) return response;
            return fetch(event.request)
                .then(res => {
                    return caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, res.clone());
                        return res;
                    });
                })
                .catch(() => {
                    if (event.request.mode === "navigate") {
                        return caches.match("/static/offline/offline.html");
                    }
                });
        })
    );
});
