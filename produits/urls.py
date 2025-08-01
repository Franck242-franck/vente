from django.urls import path
from . import views
from .views import ajouter_utilisateur
urlpatterns = [
    path('', views.lister_produits, name='lister'),
    path('ajouter/', views.ajouter_produit, name='ajouter'),
    path('modifier/<int:id>/', views.modifier_produit, name='modifier'),
    path('supprimer/<int:id>/', views.supprimer_produit, name='supprimer'),
    path('historique/', views.historique_ventes, name='historique'),
    path('gerer_utilisateurs/', views.gerer_utilisateurs, name='gerer_utilisateurs'),
    path('enregistrer_vente/', views.enregistrer_vente, name='enregistrer_vente'),
    path('ajouter_utilisateur/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
    path("supprimer_utilisateur/<int:id>/", views.supprimer_utilisateur, name="supprimer_utilisateur"),

    path('caisse/', views.dashboard_caisse, name='dashboard_caisse'),

]
