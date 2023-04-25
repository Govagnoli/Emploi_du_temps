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
            'notification', 
            'sn',
            'pn', 
            'lieu', 
            'type', 
            'statut', 
            'commentaire',
            'nom_client',
        ]

class AbsenceForm(forms.ModelForm):
    
    techniciens = forms.ModelMultipleChoiceField(
        queryset=Techniciens.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    
    class Meta:
        model = Absence
        fields = [
            'motif',
            'start', 
            'end',
        ]