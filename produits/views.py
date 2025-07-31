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


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProduitForm
from .models import Produit


# Ajouter un produit (lié automatiquement à l'utilisateur connecté)
@login_required
def ajouter_produit(request):
    if request.method == "POST":
        form = ProduitForm(request.POST)
        if form.is_valid():
            produit = form.save(commit=False)
            produit.utilisateur = request.user  # assigner automatiquement
            produit.save()
            return redirect('lister')
    else:
        form = ProduitForm()
    return render(request, "produits/ajouter.html", {"form": form})


# Modifier un produit (seulement si c'est le sien ou s'il est admin)
@login_required
def modifier_produit(request, id):
    if request.user.is_superuser:
        produit = get_object_or_404(Produit, id=id)
    else:
        produit = get_object_or_404(Produit, id=id, utilisateur=request.user)

    if request.method == "POST":
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            form.save()
            return redirect('lister')
    else:
        form = ProduitForm(instance=produit)
    return render(request, "produits/modifier.html", {"form": form, "produit": produit})


# Supprimer un produit (seulement si c'est le sien ou s'il est admin)
@login_required
def supprimer_produit(request, id):
    if request.user.is_superuser:
        produit = get_object_or_404(Produit, id=id)
    else:
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
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.contrib.auth.models import User

@staff_member_required
def gerer_utilisateurs(request):
    utilisateurs = User.objects.all()
    return render(request, 'produits/gerer_utilisateurs.html', {'utilisateurs': utilisateurs})

@login_required
def enregistrer_vente(request):
    if request.method == "POST":
        form = VenteForm(request.POST, user=request.user)  # ← ici
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
        form = VenteForm(user=request.user)  # ← ici aussi

    produits = Produit.objects.filter(utilisateur=request.user)  # ← pour JS
    return render(request, "produits/enregistrer_vente.html", {
        "form": form,
        "produits": produits
    })


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

@staff_member_required
def ajouter_utilisateur(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gerer_utilisateurs')  # Assure-toi que ce nom correspond à ta vue
    else:
        form = UserCreationForm()
    return render(request, 'produits/ajouter_utilisateur.html', {'form': form})


@staff_member_required
def supprimer_utilisateur(request, id):
    utilisateur = get_object_or_404(User, id=id)
    if request.method == "POST":
        utilisateur.delete()
        return redirect('gerer_utilisateurs')
    return render(request, "produits/supprimer_utilisateur.html", {"utilisateur": utilisateur})


@login_required
def lister_produits(request):
    query = request.GET.get('q')

    # Admin voit tout, utilisateur voit ses produits
    if request.user.is_superuser:
        produits = Produit.objects.all()
    else:
        produits = Produit.objects.filter(utilisateur=request.user)

    # Appliquer la recherche si elle existe
    if query:
        produits = produits.filter(nom__icontains=query)

    return render(request, "produits/lister.html", {"produits": produits})


from django.db.models import Sum
from django.utils.timezone import now, timedelta
from django.db.models.functions import TruncDay, TruncMonth
from django.shortcuts import render
from .models import Vente
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_caisse(request):
    today = now().date()
    seven_days_ago = today - timedelta(days=6)

    # Ventes des 7 derniers jours de l'utilisateur connecté
    ventes_journalieres = (
        Vente.objects.filter(utilisateur=request.user, date_heure__date__gte=seven_days_ago)
        .annotate(jour=TruncDay('date_heure'))
        .values('jour')
        .annotate(total=Sum('montant_total'))
        .order_by('jour')
    )

    # Ventes mensuelles de l'utilisateur connecté
    ventes_mensuelles = (
        Vente.objects.filter(utilisateur=request.user)
        .annotate(mois=TruncMonth('date_heure'))
        .values('mois')
        .annotate(total=Sum('montant_total'))
        .order_by('-mois')[:6]
    )

    return render(request, 'produits/dashboard_caisse.html', {
        'ventes_journalieres': ventes_journalieres,
        'ventes_mensuelles': ventes_mensuelles,
    })
