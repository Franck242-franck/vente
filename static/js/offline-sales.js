// Vérifie la compatibilité IndexedDB
if (!window.indexedDB) {
    console.log("Votre navigateur ne supporte pas IndexedDB !");
}

// Ouvre / crée la base de données
const request = indexedDB.open("VentesDB", 1);
let db;

request.onupgradeneeded = function(event) {
    db = event.target.result;
    const store = db.createObjectStore("ventes", { autoIncrement: true });
    store.createIndex("date", "date", { unique: false });
};

request.onsuccess = function(event) {
    db = event.target.result;
    console.log("IndexedDB prête !");
    // Si connecté, envoie les ventes stockées
    if (navigator.onLine) syncVentes();
};

request.onerror = function(event) {
    console.log("Erreur IndexedDB :", event.target.errorCode);
};

// Fonction pour ajouter une vente hors ligne
function ajouterVenteOffline(produit, quantite, montant) {
    const transaction = db.transaction(["ventes"], "readwrite");
    const store = transaction.objectStore("ventes");
    const vente = { produit, quantite, montant, date: new Date() };
    store.add(vente);
    console.log("Vente stockée offline :", vente);
}

// Fonction pour synchroniser les ventes dès que la connexion revient
function syncVentes() {
    const transaction = db.transaction(["ventes"], "readonly");
    const store = transaction.objectStore("ventes");
    const getAll = store.getAll();

    getAll.onsuccess = function() {
        const ventes = getAll.result;
        ventes.forEach((vente) => {
            fetch("/api/ventes/ajouter/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify(vente)
            })
            .then(response => response.json())
            .then(data => {
                console.log("Vente synchronisée :", data);
                // Supprimer la vente de IndexedDB après succès
                const delTransaction = db.transaction(["ventes"], "readwrite");
                const delStore = delTransaction.objectStore("ventes");
                delStore.delete(vente.id);
            })
            .catch(err => console.log("Erreur sync :", err));
        });
    };
}

// Écoute le retour en ligne
window.addEventListener("online", () => {
    console.log("Connexion rétablie ! Synchronisation...");
    syncVentes();
});

// Fonction pour récupérer le CSRF token (nécessaire pour Django)
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
