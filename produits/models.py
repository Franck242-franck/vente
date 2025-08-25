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

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Vente(models.Model):
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    montant_total = models.IntegerField(editable=False)
    date_heure = models.DateTimeField(auto_now_add=True)
    caisse = models.ForeignKey('Caisse', null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        # Calcul du montant total
        self.montant_total = self.produit.prix * self.quantite

        # Mise à jour du stock uniquement si nouvelle vente
        if not self.pk:
            if self.quantite > self.produit.quantite:
                raise ValidationError(f"Stock insuffisant : {self.produit.quantite} restant")
            self.produit.quantite -= self.quantite
            self.produit.save()

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

class Caisse(models.Model):
    date_ouverture = models.DateField(auto_now_add=True)
    date_fermeture = models.DateField(null=True, blank=True)
    total_journalier = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    statut = models.CharField(max_length=10, choices=[('ouverte', 'Ouverte'), ('fermée', 'Fermée')], default='ouverte')

    def __str__(self):
        return f"Caisse du {self.date_ouverture} ({self.statut})"
