from django import forms
from .models import Produit

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'quantite', 'prix', 'vendu']
from django import forms
from .models import Vente, Produit


class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ['produit', 'quantite']
        widgets = {
            'quantite': forms.NumberInput(attrs={'min': 1})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # Ne montrer que les produits non vendus de l'utilisateur
        self.fields['produit'].queryset = Produit.objects.filter(utilisateur=user, vendu=False)

        # Ajouter une classe CSS pour le style si nécessaire
        self.fields['produit'].widget.attrs.update({'class': 'form-control'})
        self.fields['quantite'].widget.attrs.update({'class': 'form-control'})

    def clean_quantite(self):
        quantite = self.cleaned_data.get('quantite')
        produit = self.cleaned_data.get('produit')

        if quantite and produit:
            if quantite > produit.quantite:
                raise forms.ValidationError(f"Stock insuffisant. Il reste seulement {produit.quantite} unités.")

        return quantite