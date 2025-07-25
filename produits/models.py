from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Produit(models.Model):
    nom = models.CharField(max_length=50)
    quantite = models.IntegerField()
    prix = models.IntegerField()
    vendu = models.BooleanField(default=True)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='produits')

    def __str__(self):
        return self.nom

from django.db import transaction
from django.core.exceptions import ValidationError

class Vente(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    quantite = models.PositiveIntegerField(default=1)
    montant_total = models.IntegerField(editable=False)
    date_heure = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calcul du montant total uniquement (sans modifier le stock)
        self.montant_total = self.produit.prix * self.quantite
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.produit.nom} - {self.quantite} unité(s) - {self.montant_total} FCFA"

class HistoriqueVente(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    date_vente = models.DateTimeField()
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.quantite} de {self.produit.nom} le {self.date_vente}"
