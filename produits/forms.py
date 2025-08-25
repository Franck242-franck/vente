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
        fields = ['produit', 'quantite']  # adapte si tu as plus de champs

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # récupère l'utilisateur depuis la vue
        super().__init__(*args, **kwargs)
        self.fields['produit'].queryset = Produit.objects.filter(utilisateur=user)

    def clean_quantite(self):
        quantite = self.cleaned_data.get("quantite")
        produit = self.cleaned_data.get("produit")

        if produit and quantite:
            if quantite > produit.quantite:
                raise forms.ValidationError(
                    f"Stock insuffisant : il reste seulement {produit.quantite} en stock."
                )

        return quantite
