from django import forms
from .models import *

# Gestion des formulaires par django.

# Gestion des formulaires pour l'ajout ou la modification de tâches
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

# Gestion des formulaires pour l'ajout ou la modification des absences
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