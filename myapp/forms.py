from django import forms
from .models import *

class tachesForm(forms.ModelForm):

    techniciens = forms.ModelMultipleChoiceField(
        queryset=Techniciens.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Tache
        fields = [
            'start', 
            'end',
            'titre',  
            'num_certif', 
            'sn',
            'pn', 
            'lieu', 
            'type', 
            'statut', 
            'commentaire',
            'nom_client',
        ]

class AbscenceForm(forms.ModelForm):
    
    techniciens = forms.ModelMultipleChoiceField(
        queryset=Techniciens.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    
    class Meta:
        model = Abscence
        fields = [
            'motif',
            'start', 
            'end',
        ]