const CACHE_NAME = "vente-cache-v1";
const API_CACHE_NAME = "vente-api-cache-v1";
const OFFLINE_URL = "/static/offline/offline.html";

// Ressources à mettre en cache lors de l'installation
const urlsToCache = [
    "/",                       // page d'accueil
    OFFLINE_URL,               // page hors-ligne
    "/static/icons/10023618.png", // logo
    "/static/js/offline-sales.js",
    // Ajouter les ressources nécessaires pour la page offline
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-solid-900.woff2",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/webfonts/fa-regular-400.woff2"
];

// Installation
self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
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
    // Ne gérer que les requêtes GET pour le cache
    if (event.request.method === 'GET') {
        event.respondWith(
            caches.match(event.request).then(response => {
                // Si la ressource est dans le cache, on la retourne
                if (response) {
                    return response;
                }
                // Sinon, on essaie de la récupérer depuis le réseau
                return fetch(event.request)
                    .then(response => {
                        // Ne mettre en cache que les réponses réussies
                        if (!response || response.status !== 200) {
                            return response;
                        }
                        // Cloner la réponse car elle ne peut être utilisée qu'une fois
                        const responseToCache = response.clone();
                        // Stratégie de cache pour les API
                        if (event.request.url.includes('/api/')) {
                            caches.open(API_CACHE_NAME).then(cache => {
                                cache.put(event.request, responseToCache);
                            });
                        }
                        // Stratégie de cache pour les ressources Font Awesome
                        else if (event.request.url.includes('cdnjs.cloudflare.com')) {
                            caches.open(CACHE_NAME).then(cache => {
                                cache.put(event.request, responseToCache);
                            });
                        }
                        // Pour les autres ressources
                        else {
                            caches.open(CACHE_NAME).then(cache => {
                                cache.put(event.request, responseToCache);
                            });
                        }
                        return response;
                    })
                    .catch(() => {
                        // En cas d'échec réseau, on retourne la page hors ligne pour les requêtes de navigation
                        if (event.request.mode === 'navigate') {
                            return caches.match(OFFLINE_URL);
                        }
                        // Pour les requêtes de polices Font Awesome
                        if (event.request.url.includes('webfonts') ||
                            event.request.url.includes('font-awesome')) {
                            // Retourner une réponse vide pour les polices
                            return new Response('', { status: 200 });
                        }
                        // Pour les autres ressources, on retourne une réponse d'erreur
                        return new Response('Erreur réseau', { status: 503, statusText: 'Service Unavailable' });
                    });
            })
        );
    } else {
        // Pour les requêtes non GET (POST, PUT, etc.)
        // On ne les intercepte pas, on les laisse passer
        // Mais on pourrait implémenter une stratégie de background sync ici
        event.respondWith(fetch(event.request));
    }
});

// Gestion des messages
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// Gestion de la synchronisation en arrière-plan
self.addEventListener('sync', event => {
    if (event.tag === 'sync-ventes') {
        event.waitUntil(
            // Récupérer les ventes depuis localStorage
            getVentesFromLocalStorage()
                .then(ventes => {
                    if (ventes.length === 0) {
                        return Promise.resolve();
                    }

                    // Envoyer chaque vente au serveur
                    const promises = ventes.map(vente => {
                        return fetch("/api/ventes/ajouter/", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                "X-CSRFToken": getCSRFToken()
                            },
                            body: JSON.stringify({
                                produit: vente.produit,
                                quantite: vente.quantite,
                                montant: vente.montant
                            })
                        })
                        .then(response => {
                            if (response.ok) {
                                // Supprimer la vente du localStorage
                                return removeVenteFromLocalStorage(vente.timestamp);
                            }
                            return Promise.reject(new Error('Échec de la synchronisation'));
                        })
                        .catch(error => {
                            console.error('Erreur lors de la synchronisation:', error);
                            return Promise.reject(error);
                        });
                    });

                    return Promise.all(promises);
                })
                .then(() => {
                    // Notifier le client que la synchronisation est terminée
                    notifyClients('Synchronisation terminée avec succès', 'success');
                })
                .catch(error => {
                    console.error('Erreur lors de la synchronisation des ventes:', error);
                    notifyClients('Erreur lors de la synchronisation', 'error');
                })
        );
    }
});

// Fonction pour récupérer les ventes depuis localStorage
function getVentesFromLocalStorage() {
    return new Promise((resolve, reject) => {
        // Envoyer un message à tous les clients pour récupérer les ventes
        self.clients.matchAll().then(clients => {
            if (clients && clients.length > 0) {
                // Envoyer un message au premier client actif
                clients[0].postMessage({
                    type: 'GET_VENTES_OFFLINE'
                });

                // Écouter la réponse du client
                const messageChannel = new MessageChannel();
                messageChannel.port1.onmessage = event => {
                    if (event.data && event.data.type === 'VENTES_OFFLINE') {
                        resolve(event.data.ventes);
                    } else {
                        resolve([]);
                    }
                };

                clients[0].postMessage({
                    type: 'GET_VENTES_OFFLINE'
                }, [messageChannel.port2]);
            } else {
                resolve([]);
            }
        }).catch(reject);
    });
}

// Fonction pour supprimer une vente du localStorage
function removeVenteFromLocalStorage(timestamp) {
    return new Promise((resolve, reject) => {
        self.clients.matchAll().then(clients => {
            if (clients && clients.length > 0) {
                clients[0].postMessage({
                    type: 'REMOVE_VENTE_OFFLINE',
                    timestamp: timestamp
                });
                resolve();
            } else {
                reject(new Error('Aucun client actif'));
            }
        }).catch(reject);
    });
}

// Fonction pour obtenir le token CSRF
function getCSRFToken() {
    // Cette fonction est un placeholder car le service worker n'a pas accès aux cookies
    // Dans une implémentation réelle, vous devriez stocker le token CSRF dans IndexedDB
    // ou le transmettre via un message depuis le client
    return '';
}

// Fonction pour notifier les clients
function notifyClients(message, type = 'info') {
    self.clients.matchAll().then(clients => {
        clients.forEach(client => {
            client.postMessage({
                type: 'NOTIFICATION',
                message: message,
                notificationType: type
            });
        });
    });
}