// Écouter les messages du service worker
navigator.serviceWorker.addEventListener('message', event => {
    if (event.data && event.data.type === 'GET_VENTES_OFFLINE') {
        // Renvoyer les ventes stockées dans localStorage
        const ventesOffline = JSON.parse(localStorage.getItem('ventesOffline')) || [];
        event.ports[0].postMessage({
            type: 'VENTES_OFFLINE',
            ventes: ventesOffline
        });
    } else if (event.data && event.data.type === 'REMOVE_VENTE_OFFLINE') {
        // Supprimer la vente spécifiée
        let ventes = JSON.parse(localStorage.getItem('ventesOffline')) || [];
        ventes = ventes.filter(v => v.timestamp !== event.data.timestamp);
        localStorage.setItem('ventesOffline', JSON.stringify(ventes));
    } else if (event.data && event.data.type === 'NOTIFICATION') {
        // Afficher la notification
        showNotification(event.data.message, event.data.notificationType);
    }
});

// Enregistrer la synchronisation en arrière-plan
function registerBackgroundSync() {
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
        navigator.serviceWorker.ready.then(swRegistration => {
            return swRegistration.sync.register('sync-ventes');
        }).catch(err => {
            console.error('Erreur lors de l\'enregistrement du background sync:', err);
        });
    }
}

// Fonction pour récupérer un cookie (nécessaire pour le CSRF)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Fonction pour ajouter une vente en mode hors ligne
function ajouterVenteOffline(produitId, quantite, montant) {
    // Récupérer les ventes stockées ou initialiser un tableau vide
    let ventesOffline = JSON.parse(localStorage.getItem('ventesOffline')) || [];

    // Créer un ID unique pour cette vente
    const venteId = Date.now().toString(36) + Math.random().toString(36).substr(2);

    // Ajouter la nouvelle vente avec un timestamp et un ID
    ventesOffline.push({
        id: venteId,
        produit: produitId,
        quantite: quantite,
        montant: montant,
        timestamp: new Date().toISOString(),
        synced: false
    });

    // Sauvegarder dans localStorage
    localStorage.setItem('ventesOffline', JSON.stringify(ventesOffline));

    // Afficher une notification
    showNotification("Vente enregistrée en attente de synchronisation", "info");

    // Enregistrer la synchronisation en arrière-plan
    registerBackgroundSync();

    // Essayer de synchroniser plus tard
    enregistrerVentesEnAttente();

    return venteId;
}
// Fonction pour synchroniser les ventes en attente
function enregistrerVentesEnAttente() {
    // Vérifier si on est en ligne
    if (!navigator.onLine) {
        console.log("Mode hors ligne, synchronisation différée");
        return;
    }

    // Récupérer les ventes stockées
    const ventesOffline = JSON.parse(localStorage.getItem('ventesOffline')) || [];
    if (ventesOffline.length === 0) return;

    // Filtrer uniquement les ventes non synchronisées
    const ventesASynchroniser = ventesOffline.filter(vente => !vente.synced);
    if (ventesASynchroniser.length === 0) return;

    // Afficher une notification de synchronisation en cours
    showNotification(`Synchronisation de ${ventesASynchroniser.length} vente(s)...`, "info");

    // Tenter d'envoyer chaque vente
    const promises = ventesASynchroniser.map(vente => {
        return fetch("/api/ventes/ajouter/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify({
                produit: vente.produit,
                quantite: vente.quantite,
                montant: vente.montant
            })
        })
        .then(response => {
            if (response.ok) {
                // Marquer la vente comme synchronisée
                let ventes = JSON.parse(localStorage.getItem('ventesOffline')) || [];
                const index = ventes.findIndex(v => v.id === vente.id);
                if (index !== -1) {
                    ventes[index].synced = true;
                    localStorage.setItem('ventesOffline', JSON.stringify(ventes));
                }
                return true;
            }
            return false;
        })
        .catch(error => {
            console.error("Erreur lors de la synchronisation:", error);
            return false;
        });
    });

    Promise.all(promises).then(results => {
        const successCount = results.filter(r => r).length;
        const failCount = results.length - successCount;

        if (successCount > 0) {
            showNotification(`${successCount} vente(s) synchronisée(s) avec succès!`, "success");
        }

        if (failCount > 0) {
            showNotification(`${failCount} vente(s) n'ont pas pu être synchronisées`, "warning");
        }

        // Nettoyer les ventes synchronisées après un délai
        setTimeout(() => {
            nettoyerVentesSynchronisees();
        }, 5000);
    });
}

// Fonction pour nettoyer les ventes synchronisées
function nettoyerVentesSynchronisees() {
    let ventes = JSON.parse(localStorage.getItem('ventesOffline')) || [];
    const avantNettoyage = ventes.length;

    // Ne garder que les ventes non synchronisées
    ventes = ventes.filter(vente => !vente.synced);

    if (ventes.length < avantNettoyage) {
        localStorage.setItem('ventesOffline', JSON.stringify(ventes));
        console.log(`Nettoyage de ${avantNettoyage - ventes.length} vente(s) synchronisée(s)`);
    }
}

// Fonction pour vérifier le statut des ventes en attente
function verifierVentesEnAttente() {
    const ventesOffline = JSON.parse(localStorage.getItem('ventesOffline')) || [];
    const nonSynced = ventesOffline.filter(vente => !vente.synced);

    if (nonSynced.length > 0) {
        showNotification(`${nonSynced.length} vente(s) en attente de synchronisation`, "warning");
    }
}

// Écouter les événements de connexion
window.addEventListener('online', () => {
    showNotification("Connexion rétablie, synchronisation en cours...", "info");
    enregistrerVentesEnAttente();
});

window.addEventListener('offline', () => {
    showNotification("Vous êtes hors ligne. Les ventes seront enregistrées localement.", "warning");
});

// Tenter de synchroniser au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    // Vérifier les ventes en attente
    verifierVentesEnAttente();

    // Tenter de synchroniser
    enregistrerVentesEnAttente();

    // Enregistrer le service worker pour le background sync
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
        navigator.serviceWorker.ready.then(swRegistration => {
            return swRegistration.sync.register('sync-ventes');
        }).catch(err => {
            console.error('Erreur lors de l\'enregistrement du background sync:', err);
        });
    }
});

// Fonction pour afficher les notifications
function showNotification(message, type = 'info') {
    // Vérifier si le conteneur de notifications existe
    let container = document.getElementById('notification-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        document.body.appendChild(container);
    }

    // Créer la notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;

    // Déterminer l'icône en fonction du type
    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-check-circle';
    if (type === 'error') icon = 'fa-exclamation-circle';
    if (type === 'warning') icon = 'fa-exclamation-triangle';

    notification.innerHTML = `
        <i class="fas ${icon}"></i>
        <div>${message}</div>
    `;

    // Ajouter la notification au conteneur
    container.appendChild(notification);

    // Auto-suppression après 5 secondes
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            if (container.contains(notification)) {
                container.removeChild(notification);
            }
        }, 300);
    }, 5000);
}