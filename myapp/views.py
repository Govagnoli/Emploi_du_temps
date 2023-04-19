from datetime import datetime, timedelta
from datetime import datetime
import math
import os
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from myapp.forms import * 
from myapp.models import Tache, Absence
import pandas as pd
from django.views.decorators.csrf import csrf_exempt

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

def all_absences(request):
    all_absences = Absence.objects.filter(start__range=[request.GET.get("start", None), request.GET.get("end", None)])                                                                                
    out = []  
    for absence in all_absences:
        techniciens = absence.techniciens.all()
        if len(techniciens) > 1:
            backgroundColor = "#000000"
        elif techniciens[0].id_tech == 1:
            backgroundColor = "#808080"
        else :
            backgroundColor = "#805858"

        end = absence.end
        end += timedelta(days=1)
        out.append({                                                                                                     
            'id_abs': absence.id_abs,
            'start': absence.start.strftime('%Y-%m-%d'),
            'end':end.strftime('%Y-%m-%d'),
            'rendering': 'background',
            'backgroundColor': '#000000',
            'titre': "Absence : " + absence.motif,
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

def add_absence(request):
    if request.method == "POST":
        form = AbsenceForm(request.POST)
        if form.is_valid():
            form.cleaned_data['end'] = form.cleaned_data['end'].replace(hour=12, minute=0, second=0, microsecond=0)
            abs = form.save(commit=False)
            techniciens = form.cleaned_data['techniciens']
            abs.save()
            abs.techniciens.set(techniciens)
            return redirect('index') # Redirige vers la page d'accueil après ajout réussi
    else:
        form = tachesForm()
    return render(request, 'Declaration_Absences.html', {'form': form})

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
    absence = get_object_or_404(Absence, id_abs=id_abs)
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
    absences = Absence.objects.filter(end__gte=datetime.today()).order_by('start')
    if not absences:
        messages.success(request, 'Aucune absence à venir.')
    tab = '<table border="1" class="dataframe" id="tab"> <thead> <tr style="text-align: right;"></th><th></th><th>Motif d\'absence</th> <th>date de début</th> <th>date de fin</th> </tr> </thead> <tbody>'
    i=0
    for absence in absences:
        start = absence.start.strftime('%d/%m/%Y')
        end = absence.end.strftime('%d/%m/%Y')
        tab += '<tr id="' + str(absence.id_abs) +'"><th>' + str(i) +'</th><td>' + str(absence.motif) +'</td><td>' + str(start) +'</td><td>' + str(end) +'</td></tr>'
        i += 1
    tab += '</tbody></table>'

    absences2 = Absence.objects.filter(end__lt=datetime.today()).order_by('start')
    if not absences2:
        messages.error(request, 'Aucune absence programmé.')
    tab2 = '<table border="1" class="dataframe" id="tab2"> <thead> <tr style="text-align: right;"></th><th></th><th>Motif d\'absence</th> <th>date de début</th> <th>date de fin</th> </tr> </thead> <tbody>'
    i=0
    for absence in absences2:
        start = absence.start.strftime('%d/%m/%Y')
        end = absence.end.strftime('%d/%m/%Y')
        tab2 += '<tr id="' + str(absence.id_abs) +'"><th>' + str(i) +'</th><td>' + str(absence.motif) +'</td><td>' + str(start) +'</td><td>' + str(end) +'</td></tr>'
        i += 1
    tab2 += '</tbody></table>'

    return render(request, 'Absences.html', {'absencesFiltrees': tab, 'absencesSansFiltre': tab2})

def getAbsenceById(request, id_abs):
    absence = get_object_or_404(Absence, id_abs=id_abs)
    listAbsence = []
    listAbsence.append(absence.id_abs)
    listAbsence.append(absence.motif)
    listAbsence.append(absence.start)
    listAbsence.append(absence.end)
    return JsonResponse({'absence': listAbsence})

def modifier_absence(request, id_abs):
    instance = get_object_or_404(Absence, id_abs=id_abs)
    form = AbsenceForm(request.POST, instance=instance)
    if form.is_valid():
        form.cleaned_data['end'] = form.cleaned_data['end'].replace(hour=12, minute=0, second=0, microsecond=0)
        absence = form.save(commit=False)
        techniciens = form.cleaned_data['techniciens']
        absence.save()
        absence.techniciens.set(techniciens)
        return redirect('index') # Redirige vers la page d'accueil après modification réussi
    context = {'form': form}
    return render(request, 'Absences.html', context)

def removeAbsence(request, id_abs):
    absence = get_object_or_404(Absence, id_abs=id_abs)
    absence.techniciens.clear()
    absence.delete()
    data = {}
    return JsonResponse(data)

from django.contrib import messages

def add_Excell_taches(request):
    if request.method != 'POST':
        messages.error(request, None)
        return render(request, 'AjoutParExcell.html')

    # Récupération du fichier Excell
    file = request.FILES.get('xlsx_file')
    if not file:
        messages.error(request, 'Erreur : fichier manquant.')
        return render(request, 'AjoutParExcell.html')
    
    # Vérification de l'extension du fichier
    if not file.name.endswith('.XLSX') :
        if not file.name.endswith('.xlsx'):
            messages.error(request, 'Erreur : le fichier doit être un document Excel avec l\'extension .xlsx.')
            return render(request, 'AjoutParExcell.html')
        
    # Écriture du fichier sur le disque
    try:
        filepath = os.path.join(settings.EXCELL_DIR, file.name)
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'écriture du fichier : {e}.')
        return render(request, 'AjoutParExcell.html')

    # Récupération des données du fichier Excell.
    try:
        dfFic = pd.read_excel(os.path.join(settings.EXCELL_DIR, file.name))
    except FileNotFoundError:
        messages.error(request, 'Erreur : le fichier est manquant : {e}.')
        return render(request, 'AjoutParExcell.html')
    except ValueError:
        messages.error(request, 'Erreur : la feuille demandée n\'existe pas : {e}.')
        return render(request, 'AjoutParExcell.html')
    
    #Il me manque la date de début, le pn, le lieu, le type, le statut
    dfFic = dfFic[['Order', 'Requested deliv.date', 'Notification', 'Serial Number', 'Material', 'Service Material', 'System Status', 'Name 1', 'Description', 'Tech. Evaluation']]
    dfFic = dfFic.rename(columns={'Service Material': 'lieu','Material': 'pn','Order':'id_tache', 'Requested deliv.date': 'end', 'System Status': 'type','Serial Number': 'sn', 'Name 1': 'nom_client', 'Notification': 'num_certif', 'Tech. Evaluation' : 'Technicien', 'Description': 'commentaire'})

    # il manque le type (je ne connais pas l'abréviation)
    # order id unique

    # On garde seulent les tache ayant un id(order)
    dfFic = dfFic.dropna(subset=['id_tache'])
    
    #Création des dates de départ. J'estime qu'une tache dure 7jours. Donc La date de livraison - 7 jours donne la date de début de la tache
    for index, dateF in dfFic['end'].items():
        if isinstance(dateF, pd.Timestamp):
            dateF_datetime = dateF.to_pydatetime()
            dateD = dateF_datetime - timedelta(days=7)
            dfFic.loc[index, 'start'] = dateD
            dfFic.loc[index, 'end'] = dateF_datetime.replace(hour=12, minute=0, second=0)
        else: 
            messages.error(request, 'Erreur : Les dates de fin (Requested deliv.date) doivent être au format date (JJ/MM/AAAA). (pour les devs) Si le problème persiste vérifier que les données sont au format pandas.Timestamp dans python: {e}.')

    # Récupération du lieu du déroulement de l'opération
    for index, lieu in dfFic['lieu'].items():
        if(lieu[-6:] == 'ONSITE') :
            dfFic.loc[index, 'lieu'] = 'on site'
        else:
            dfFic.loc[index, 'lieu'] = 'in house'

    # Création du statut de la tache à 'à faire' pour chaque tache.
    dfFic = dfFic.assign(statut='à faire')
    # Assignation des techniciens
    for index, technicien in dfFic['Technicien'].items():
        technicien = str(technicien)
        nom_tech = technicien[1:]
        nom_tech = nom_tech.upper()
        if(nom_tech == "GALVE") :
            nom_tech = "Galve"
            prenom_tech = "Franck"
        elif(nom_tech == "AURIOL"):
            nom_tech = "Auriol"
            prenom_tech = "Clément"
        elif nom_tech=="AN":
            nom_tech = ""
            prenom_tech = ""
        else :
            nom_tech = "non définis"
            prenom_tech = "non définis"
        dfFic.loc[index, 'nom'] = nom_tech
        dfFic.loc[index, 'prenom'] = prenom_tech
    dfFic.drop('Technicien', axis=1, inplace=True)

    # Supprime les valeur NaN dans les colonnes obligatoires par non renseigné (SN, PN, Nom_client) et pour commentaire met une valeur null
    dfFic['sn'].fillna('non renseigné', inplace=True)
    dfFic['pn'].fillna('non renseigné', inplace=True)
    dfFic['nom_client'].fillna('non renseigné', inplace=True)
    dfFic['commentaire'].fillna("", inplace=True)

    # La colonne id est castée en int. Elle passe de float à integer
    dfFic['id_tache'] = dfFic['id_tache'].astype(int)

    # Défnition du titre de la tache
    for index, colonnes in dfFic[["commentaire", "id_tache", "nom_client"]].iterrows():
        if len(colonnes["commentaire"])>0:
            dfFic.loc[index, 'titre'] = colonnes["commentaire"]
        elif (len(colonnes["nom_client"]) != 'non renseigné' and ( len(str(colonnes["id_tache"]) + " " + colonnes["nom_client"]) < 51)): 
            dfFic.loc[index, 'titre'] = str(colonnes["id_tache"]) + " " + colonnes["nom_client"]
        else:
            dfFic.loc[index, 'titre'] = str(colonnes["id_tache"])
    
# 
# ATTENTION CETTE ETAPE EST TEMPORAIRE, JE NE PEUX PAS CONNAITRE LE TYPE DE LA TACHE (pour l'instant)
# 

    # Assignation du type
    for index, types in dfFic["type"].items():
        mesTypes = types.split(" ")
        # L'abréviation me permettant de définir si la tache est VGP¨ou Reper
        VGP = "PRC"
        Reper = "CNF"
        if Reper in mesTypes:
            dfFic.loc[index, 'type'] = "Reper"
        elif VGP in mesTypes:
            dfFic.loc[index, 'type'] = "VGP"
        else:
            dfFic.loc[index, 'type'] = "NUll"

    # Le commentaire est entièrement défnis à vide
    dfFic = dfFic.assign(commentaire="")
    
    dfFic = dfFic.dropna(subset=['id_tache'])
    dfFic = dfFic[['id_tache', 'titre','start', 'end', 'num_certif', 'sn', 'pn', 'lieu', 'type','statut', 'nom_client', 'commentaire', 'nom', 'prenom']]
    dfFic = dfFic.reset_index(drop=True)

    # Mise à jour de la base de données avec le dataframe
    for index, colonnes in dfFic.iterrows():
        # création d'un dictionnaire contenant les champs à mettre à jour ou à créer
        data = {
            'id_tache': colonnes['id_tache'],
            'titre': colonnes['titre'],
            'start': colonnes['start'],
            'end': colonnes['end'],
            'num_certif': colonnes['num_certif'],
            'sn': colonnes['sn'],
            'pn': colonnes['pn'],
            'lieu': colonnes['lieu'],
            'type': colonnes['type'],
            'statut': colonnes['statut'],
            'nom_client': colonnes['nom_client'],
            'commentaire': colonnes['commentaire'],
        }
        # mise à jour ou création de l'enregistrement correspondant dans la base de données
        obj, created = Tache.objects.update_or_create(id_tache=colonnes['id_tache'], defaults=data)

    messages.success(request, 'Le fichier Excel a été importé avec succès!')
    return render(request, 'AjoutParExcell.html', {'dfExcell': dfFic.to_html})
