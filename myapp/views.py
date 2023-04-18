from datetime import datetime, timedelta
from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from myapp.forms import * 
from myapp.models import Tache, Abscence
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

#redirige vers l'emploi du temps (index.html)
def index(request):
    all_events = Tache.objects.all()
    context = {
        "events":all_events,
    }
    return render(request,'index.html',context)

#Récupère toutes les tâches stockés dans la base de données et les envoie dans le calendrier du template index.html
def all_taches(request):                                                                                                 
    all_taches = Tache.objects.filter(start__range=[request.GET.get("start", None), request.GET.get("end", None)])
    out = []                                                                                                 
    for tache in all_taches:
        color = None
        if tache.type == "VGP":
            color = 'purple'
        elif tache.type == "Reper":
            color = 'blue'
        if tache.statut == 'fini':
            color = 'green'                                              
        out.append({                                                                                                     
            'id_tache': tache.id_tache,
            'start': tache.start.strftime('%Y-%m-%dT%H:%M:%S'),                                                         
            'end': tache.end.replace(hour=12, minute=0, second=0, microsecond=0),
            'title': tache.titre,                                                                           
            'num_certif': tache.num_certif,
            'sn': tache.sn,
            'pn' : tache.pn,
            'lieu' : tache.lieu,
            'type' : tache.type,
            'statut' : tache.statut,
            'commentaire': tache.commentaire,
            'nom_client': tache.nom_client,
            'color': color,
            'textColor' : '#F5F3F3'                                                   
        })
    return JsonResponse(out, safe=False)

def all_abscences(request):
    all_absences = Abscence.objects.filter(start__range=[request.GET.get("start", None), request.GET.get("end", None)])                                                                                
    out = []  
    for abscence in all_absences:
        techniciens = abscence.techniciens.all()
        if len(techniciens) > 1:
            backgroundColor = "#000000"
        elif techniciens[0].id_tech == 1:
            backgroundColor = "#808080"
        else :
            backgroundColor = "#805858"


        end = abscence.end
        end += timedelta(days=1)
        out.append({                                                                                                     
            'id_abs': abscence.id_abs,
            'start': abscence.start.strftime('%Y-%m-%d'),
            'end':end.strftime('%Y-%m-%d'),
            'rendering': 'background',
            'backgroundColor': '#000000',
            'titre': "Absence : " + abscence.motif,
            'type': 'absence',                 
        })
    return JsonResponse(out, safe=False)

# À partir du formulaire ajouter un évènement permet d'ajouter une tâche et ses techniciens associés dans la base de données 
def add_tache(request):
    if request.method == "POST":
        form = tachesForm(request.POST)
        if form.is_valid():
            form.cleaned_data['end'] = form.cleaned_data['end'].replace(hour=12, minute=0, second=0, microsecond=0)
            tache = form.save(commit=False)
            techniciens = form.cleaned_data['techniciens']
            tache.save()
            tache.techniciens.set(techniciens)
            return redirect('index') # Redirige vers la page d'accueil après ajout réussi
    else:
        form = tachesForm()
    return render(request, 'ajout.html', {'form': form})

def add_abscence(request):
    if request.method == "POST":
        form = AbscenceForm(request.POST)
        if form.is_valid():
            form.cleaned_data['end'] = form.cleaned_data['end'].replace(hour=12, minute=0, second=0, microsecond=0)
            abs = form.save(commit=False)
            techniciens = form.cleaned_data['techniciens']
            abs.save()
            abs.techniciens.set(techniciens)
            return redirect('index') # Redirige vers la page d'accueil après ajout réussi
    else:
        form = tachesForm()
    return render(request, 'Declaration_Abscences.html', {'form': form})

# À partir du calendrier permet lors de la modification d'une tache existante de mettre à jour les données et donc de possiblement les modifier
# à noter que toutes les données sont modifiés. Ca récupère toutes les données du formulaire puis écrase les données de la tache dans la base de données
def modifier_tache(request, id_tache):
    instance = get_object_or_404(Tache, id_tache=id_tache)
    form = tachesForm(request.POST, instance=instance)
    if form.is_valid():
        form.cleaned_data['end'] = form.cleaned_data['end'].replace(hour=12, minute=0, second=0, microsecond=0)
        tache = form.save(commit=False)
        techniciens = form.cleaned_data['techniciens']
        tache.save()
        tache.techniciens.set(techniciens)
        return redirect('index') # Redirige vers la page d'accueil après modification réussi
    context = {'form': form}
    return render(request, 'index.html', context)

#Permet de modifier la date d'une tache lors de son déplacement via l'interface du calendrier
def update(request, id_tache):
    tache = get_object_or_404(Tache, id_tache=id_tache)
    if request.method == 'POST':
        start_str = request.POST.get("start", None)
        end_str = request.POST.get("end", None)
        start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
        tache.start = start
        tache.end = end
        tache.save()
        data = {}
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Invalid request type'})
 
def remove(request, id_tache):
    tache = get_object_or_404(Tache, id_tache=id_tache)
    tache.techniciens.clear()
    tache.delete()
    data = {}
    return JsonResponse(data)

def get_techniciens(request, id_tache):
    tache = get_object_or_404(Tache, id_tache=id_tache)
    techniciens = tache.techniciens.all()
    techniciens_list = []
    for technicien in techniciens:
        techniciens_list.append({'prenom': technicien.prenom, 'nom': technicien.nom})
    return JsonResponse({'techniciens': techniciens_list})

def get_techniciens_abs(request, id_abs):
    absence = get_object_or_404(Abscence, id_abs=id_abs)
    techniciens = absence.techniciens.all()
    techniciens_list = []
    for technicien in techniciens:
        techniciens_list.append({'prenom': technicien.prenom, 'nom': technicien.nom})
    return JsonResponse({'techniciens': techniciens_list})

def alerteVGP(request):
    dfTaches = pd.DataFrame()
    date_limite = datetime.now() + timedelta(days=60)
    taches = Tache.objects.filter(type="VGP", start__range=[datetime.now(), date_limite]).order_by('start')
    if taches:
        for tache in taches:
            dfTaches = pd.concat([dfTaches, pd.DataFrame([tache.__dict__])])
        dfTaches = dfTaches.rename(columns={'start': 'date de début', 'end': 'date de fin', 'sn': 'Serial number', 'nom_client': 'nom client', 'num_certif': 'numéro certificat'})
        
        dfTaches['date de début'] = pd.to_datetime(dfTaches['date de début'])
        dfTaches['date de début'] = dfTaches['date de début'].dt.strftime('%d/%m/%Y')

        dfTaches['date de fin'] = pd.to_datetime(dfTaches['date de fin'])
        dfTaches['date de fin'] = dfTaches['date de fin'].dt.strftime('%d/%m/%Y')

        dfTaches = dfTaches[['titre', 'date de début', 'date de fin', 'numéro certificat', 'Serial number', 'pn', 'lieu', 'type', 'statut', 'commentaire', 'nom client']]
        dfTaches = dfTaches.reset_index(drop=True)
        return render(request, 'Alerte.html', {'taches': dfTaches.to_html()})
    return render(request, 'Alerte.html', {'taches': "Vous n'avez pas de prochaines taches VGP."})

@csrf_exempt
def save_tache(request):
    if request.method == 'POST':
        Tache.objects.create(
            titre = request.POST.get("titre", None),
            start = request.POST.get("start", None),
            end = datetime.strptime(request.POST.get("end", None) + " 1:00:00", '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),
            num_certif = request.POST.get("num_certif", None),
            sn = request.POST.get("sn", None),
            pn = request.POST.get("pn", None),
            lieu = request.POST.get("lieu", None),
            type = request.POST.get("type", None),
            statut = "à faire",
            nom_client = request.POST.get("nom_client", None),
            commentaire = request.POST.get("commentaire", None)
        )
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})
    
def absences(request):
    absences = Abscence.objects.filter(end__gte=datetime.today()).order_by('start')
    if not absences:
        return render(request, 'Absences.html', {'absences': "Aucune absence n'est programmée"})
    tab = '<table border="1" class="dataframe" id="tab"> <thead> <tr style="text-align: right;"></th><th></th><th>Motif d\'absence</th> <th>date de début</th> <th>date de fin</th> </tr> </thead> <tbody>'
    i=0
    for absence in absences:
        start = absence.start.strftime('%d/%m/%Y')
        end = absence.end.strftime('%d/%m/%Y')
        tab += '<tr id="' + str(absence.id_abs) +'"><th>' + str(i) +'</th><td>' + str(absence.motif) +'</td><td>' + str(start) +'</td><td>' + str(end) +'</td></tr>'
        i += 1
    tab += '</tbody></table>'
    return render(request, 'Absences.html', {'absences': tab})

def getAbsenceById(request, id_abs):
    absence = get_object_or_404(Abscence, id_abs=id_abs)
    listAbsence = []
    listAbsence.append(absence.id_abs)
    listAbsence.append(absence.motif)
    listAbsence.append(absence.start)
    listAbsence.append(absence.end)
    return JsonResponse({'abscense': listAbsence})

def modifier_absence(request, id_abs):
    instance = get_object_or_404(Abscence, id_abs=id_abs)
    form = AbscenceForm(request.POST, instance=instance)
    if form.is_valid():
        form.cleaned_data['end'] = form.cleaned_data['end'].replace(hour=12, minute=0, second=0, microsecond=0)
        absence = form.save(commit=False)
        techniciens = form.cleaned_data['techniciens']
        absence.save()
        absence.techniciens.set(techniciens)
        return redirect('index') # Redirige vers la page d'accueil après modification réussi
    context = {'form': form}
    return render(request, 'Absences.html', context)