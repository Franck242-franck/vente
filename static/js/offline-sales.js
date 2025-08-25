// Fonction pour ajouter une vente en mode hors ligne
function ajouterVenteOffline(produit, quantite, montant) {
    // Récupérer les ventes stockées ou initialiser un tableau vide
    let ventesOffline = JSON.parse(localStorage.getItem('ventesOffline')) || [];

    // Ajouter la nouvelle vente avec un timestamp
    ventesOffline.push({
        produit,
        quantite,
        montant,
        timestamp: new Date().toISOString()
    });

    // Sauvegarder dans localStorage
    localStorage.setItem('ventesOffline', JSON.stringify(ventesOffline));

    // Essayer de synchroniser plus tard
    enregistrerVentesEnAttente();
}

// Fonction pour synchroniser les ventes en attente
function enregistrerVentesEnAttente() {
    // Vérifier si on est en ligne
    if (!navigator.onLine) return;

    // Récupérer les ventes stockées
    const ventesOffline = JSON.parse(localStorage.getItem('ventesOffline')) || [];

    if (ventesOffline.length === 0) return;

    // Tenter d'envoyer chaque vente
    const promises = ventesOffline.map(vente => {
        return fetch("/api/ventes/ajouter/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: JSON.stringify(vente)
        })
        .then(response => {
            if (response.ok) {
                // Supprimer la vente du localStorage
                let ventes = JSON.parse(localStorage.getItem('ventesOffline')) || [];
                ventes = ventes.filter(v => v.timestamp !== vente.timestamp);
                localStorage.setItem('ventesOffline', JSON.stringify(ventes));
                return true;
            }
            return false;
        })
        .catch(() => false);
    });

    Promise.all(promises).then(results => {
        const successCount = results.filter(r => r).length;
        if (successCount > 0) {
            showNotification(`${successCount} vente(s) synchronisée(s) !`);
        }
    });
}

// Écouter les événements de connexion
window.addEventListener('online', enregistrerVentesEnAttente);

// Tenter de synchroniser au chargement de la page
document.addEventListener('DOMContentLoaded', enregistrerVentesEnAttente);