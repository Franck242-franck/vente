from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Produit, Vente
from .forms import ProduitForm
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import VenteForm  # Il faut créer ce formulaire dans forms.py

# Vérifier si utilisateur est admin
def is_admin(user):
    return user.is_staff

@login_required
def lister_produits(request):
    produits = Produit.objects.filter(utilisateur=request.user)
    return render(request, "produits/lister.html", {"produits": produits})

@login_required
def ajouter_produit(request):
    if request.method == "POST":
        form = ProduitForm(request.POST)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.utilisateur = request.user
            produit.save()
            return redirect('lister')
    else:
        form = ProduitForm()
    return render(request, "produits/ajouter.html", {"form": form})

@login_required
def modifier_produit(request, id):
    produit = get_object_or_404(Produit, id=id, utilisateur=request.user)
    if request.method == "POST":
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('lister')
    else:
        form = ProduitForm(instance=produit)
    return render(request, "produits/modifier.html", {"form": form, "produit": produit})

@login_required
def supprimer_produit(request, id):
    produit = get_object_or_404(Produit, id=id, utilisateur=request.user)
    if request.method == "POST":
        produit.delete()
        return redirect('lister')
    return render(request, "produits/supprimer.html", {"produit": produit})

@login_required
def historique_ventes(request):
    ventes = Vente.objects.filter(utilisateur=request.user).order_by('-date_heure')
    return render(request, "produits/historique.html", {"ventes": ventes})

# Gestion utilisateurs réservée aux admins
@user_passes_test(is_admin)
def gerer_utilisateurs(request):
    utilisateurs = User.objects.all()
    return render(request, "produits/gerer_utilisateurs.html", {"utilisateurs": utilisateurs})

@login_required
def enregistrer_vente(request):
    if request.method == "POST":
        form = VenteForm(request.POST)
        if form.is_valid():
            vente = form.save(commit=False)
            produit = vente.produit

            if vente.quantite > produit.quantite:
                messages.error(request, f"Stock insuffisant. Il reste seulement {produit.quantite} unités de {produit.nom}.")
            else:
                produit.quantite -= vente.quantite
                produit.save()
                vente.utilisateur = request.user
                vente.save()
                messages.success(request, "Vente enregistrée avec succès.")
                return redirect('lister')
    else:
        form = VenteForm()

    produits = Produit.objects.all()  # Pour ton JS de calcul automatique
    return render(request, "produits/enregistrer_vente.html", {
        "form": form,
        "produits": produits
    })

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def ajouter_utilisateur(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lister')  # Le nom de ta vue de liste
    else:
        form = UserCreationForm()
    return render(request, 'produits/ajouter_utilisateur.html', {'form': form})


@login_required
def supprimer_utilisateur(request, id):
    utilisateur = get_object_or_404(User, id=id)
    if request.method == "POST":
        utilisateur.delete()
        return redirect('gerer_utilisateurs')  # ou la bonne vue de liste des utilisateurs
    return render(request, "produits/supprimer_utilisateur.html", {"utilisateur": utilisateur})



def lister_produits(request):
    query = request.GET.get('q')
    if query:
        produits = Produit.objects.filter(nom__icontains=query)
    else:
        produits = Produit.objects.all()
    return render(request, 'produits/lister.html', {'produits': produits})

from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.db.models.functions import TruncDay, TruncMonth
from django.shortcuts import render
from .models import Vente

def dashboard_caisse(request):
    # Ventes des 7 derniers jours
    today = now().date()
    seven_days_ago = today - timedelta(days=6)

    ventes_journalieres = (
        Vente.objects.filter(date_heure__date__gte=seven_days_ago)
        .annotate(jour=TruncDay('date_heure'))
        .values('jour')
        .annotate(total=Sum('montant_total'))
        .order_by('jour')
    )

    # Ventes par mois (derniers 6 mois)
    ventes_mensuelles = (
        Vente.objects.annotate(mois=TruncMonth('date_heure'))
        .values('mois')
        .annotate(total=Sum('montant_total'))
        .order_by('-mois')[:6]
    )

    return render(request, 'produits/dashboard_caisse.html', {
        'ventes_journalieres': ventes_journalieres,
        'ventes_mensuelles': ventes_mensuelles,
    })


