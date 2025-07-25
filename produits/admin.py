from django.contrib import admin
from .models import Produit, Vente

class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'quantite', 'prix', 'vendu')
    search_fields = ('nom',)
    list_filter = ('vendu',)

class VenteAdmin(admin.ModelAdmin):
    list_display = ('produit', 'utilisateur', 'date_heure')
    list_filter = ('date_heure', 'utilisateur')
    search_fields = ('produit__nom', 'utilisateur__username')

admin.site.register(Produit, ProduitAdmin)
admin.site.register(Vente, VenteAdmin)
