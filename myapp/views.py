from datetime import datetime, timedelta
from datetime import datetime
import os
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseBadRequest, JsonResponse
from myapp.forms import * 
from myapp.models import Tache, Absence
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

#redirige vers l'emploi du temps (index.html)
def index(request):
    all_events = Tache.objects.all()
    context = {
        "events":all_events,
    }
    return render(request,'index.html',context)

#Récupère toutes les tâches stockés dans la base de données et les envoie dans le calendrier du template index.html
def all_taches(request):                                                                                                 
    all_taches = Tache.objects.all() #Important de tout généré (avec all() et pas filtre()) sinon erreur sur les cas avec des dates sur deux mois du style date de début en mars et date de fin en avril. On verra la tache le mois de mars mais pas en avril.
    out = []                                                                                               
    for tache in all_taches:
        color = None
        if tache.type == "VGP":
            color = 'rgba(35,153,214,0.8)' # Bleu hydro clair 'rgba(35,153,214,0.8)'                # Magenta hydro 'rgba(229,0,125,0.8)'
        elif tache.type == "Reper":
            color = 'rgba(0,62,119,0.8)'    # Bleu hydro foncé 'rgba(0,62,119,0.8)'         # Jaune hydro 'rgba(255,222,27,0.8)'
        if tache.lieu == "on site":
            color = 'rgba(196,102,213,0.8)'  # Violet 'rgba(196,102,213,0.8)'
        if (len(tache.techniciens.all())==0) :
            color = 'rgba(204,204,204,0.2)'  # Gris hydro
            textColor = 'rgba(111,111,111,1)'
        else :
            textColor = 'rgba(245,243,243,1)'      

        if tache.statut == 'fini':
            color = 'rgba(17,176,48,0.8)'   # Vert 'rgba(17,176,48,0.8)'                    # Vert Hydro 'rgba(161,198,17,0.8)'
            textColor = 'rgba(245,243,243,1)'
        if tache.statut == 'Non valide':
            color = 'rgba(255,0,0,0.8)'     # Rouge 'rgba(255,0,0,0.8)'                     # Rouge Hydro 'rgba(227,0,15,0.8)'
            textColor = 'rgba(245,243,243,1)'
        
        out.append({                                                                                                     
            'notification': tache.notification,
            'start': tache.start.strftime('%Y-%m-%dT%H:%M:%S'),                                                         
            'end': tache.end.replace(hour=12, minute=0, second=0, microsecond=0),
            'title': tache.titre,
            'sn': tache.sn,
            'pn' : tache.pn,
            'lieu' : tache.lieu,
            'type' : tache.type,
            'statut' : tache.statut,
            'commentaire': tache.commentaire,
            'nom_client': tache.nom_client,
            'color': color,
            'textColor' : textColor                                                  
        })
    return JsonResponse(out, safe=False)

# Récupère les absences dans la base de données et les renvoie dans le calendrier du template index.html
def all_absences(request):
    all_absences = Absence.objects.filter(start__range=[request.GET.get("start", None), request.GET.get("end", None)])                                                                                
    out = []  
    for absence in all_absences:
        techniciens = absence.techniciens.all()
        if len(techniciens) > 1:
            backgroundColor = "#000000" # gris foncé
        elif techniciens[0].id_tech == 1:
            backgroundColor = "#808080" # gris clair
        else :
            backgroundColor = "#805858" # marron clair

        end = absence.end
        end += timedelta(days=1)
        out.append({                                                                                                     
            'id_abs': absence.id_abs,
            'start': absence.start.strftime('%Y-%m-%d'),
            'end':end.strftime('%Y-%m-%d'),
            'rendering': 'background',
            'backgroundColor': backgroundColor,
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
            tache, created = Tache.objects.update_or_create(
                notification=form.cleaned_data['notification'],
                defaults={
                    'start': form.cleaned_data['start'],
                    'end': form.cleaned_data['end'],
                    'titre': form.cleaned_data['titre'],
                    'notification': form.cleaned_data['notification'],
                    'sn': form.cleaned_data['sn'],
                    'pn': form.cleaned_data['pn'],
                    'lieu': form.cleaned_data['lieu'],
                    'type': form.cleaned_data['type'],
                    'statut': form.cleaned_data['statut'],
                    'commentaire': form.cleaned_data['commentaire'],
                    'nom_client': form.cleaned_data['nom_client'],
                }
            )
            techniciens = form.cleaned_data['techniciens']
            tache.techniciens.set(techniciens)
            return redirect('index') # Redirige vers la page d'accueil après ajout réussi
    else:
        form = tachesForm()
    return render(request, 'ajout.html', {'form': form})

# Permet d'ajouter une absence dans la base de données via le formulaire de déclaration des absences
def add_absence(request):
    if request.method == "POST":
        form = AbsenceForm(request.POST)
        if form.is_valid():
            form.cleaned_data['end'] = form.cleaned_data['end'].replace(hour=12, minute=0, second=0, microsecond=0)
            abs = form.save(commit=False)
            techniciens = form.cleaned_data['techniciens']
            abs.save()
            abs.techniciens.set(techniciens)
            return redirect('absences') # Redirige vers la page d'absences après ajout réussi
    else:
        form = tachesForm()
    return render(request, 'Declaration_Absences.html', {'form': form})

# À partir du calendrier permet lors de la modification d'une tache existante de mettre à jour les données et donc de possiblement les modifier
# à noter que toutes les données sont modifiés. Ca récupère toutes les données du formulaire puis écrase les données de la tache dans la base de données
def modifier_tache(request, oldNotification, newNotification):
    # Si la notification est modifié et qu'elle référence déjà une autre donnée de la base alors il n'est pas possible de l'utiliser comme notification
    print(newNotification)
    if(oldNotification!=newNotification and Tache.objects.filter(notification=newNotification).exists()):
        return JsonResponse({'error': 'Le formulaire est invalide'}, status=400)

    instance = get_object_or_404(Tache, notification=oldNotification)
    form = tachesForm(request.POST, instance=instance)
    if form.is_valid():
        form.cleaned_data['end'] = form.cleaned_data['end'].replace(hour=12, minute=0, second=0, microsecond=0)
        tache = form.save(commit=False)
        techniciens = form.cleaned_data['techniciens']
        tache.save()
        tache.techniciens.set(techniciens)
        return redirect('index') # Redirige vers la page d'accueil après modification réussi
    return HttpResponseBadRequest("le formulaire est invalide.")

# Permet de modifier la date d'une tache lors de son déplacement via l'interface du calendrier
def update(request, notification):
    tache = get_object_or_404(Tache, notification=notification)
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
    
# Supprime une tache (identifié par sa notification) et enlève par la suite la référence de travail entre les techniciens et cette tâches
def remove(request, notification):
    tache = get_object_or_404(Tache, notification=notification)
    tache.techniciens.clear()
    tache.delete()
    data = {}
    return JsonResponse(data)

# Récupère les techniciens associés à une tache identifié par sa notification et renvoie dans une liste le nom et le prénom des ou du technicien(s) concerné(s)
def get_techniciens(request, notification):
    techniciens_list = []
    if int(notification) <0:
        return JsonResponse({'techniciens': techniciens_list})
    tache = get_object_or_404(Tache, notification=notification)
    techniciens = tache.techniciens.all()
    for technicien in techniciens:
        techniciens_list.append({'prenom': technicien.prenom, 'nom': technicien.nom})
    return JsonResponse({'techniciens': techniciens_list})

# Récupère les techniciens associés à une tache identifié par sa notification et renvoie dans une liste l'id_tech des ou du technicien(s) concerné(s)
def get_Id_techniciens(request, notification):
    techniciens_list = []
    if int(notification) <0:
        return JsonResponse({'techniciens': techniciens_list})
    tache = get_object_or_404(Tache, notification=notification)
    techniciens = tache.techniciens.all()
    for technicien in techniciens:
        techniciens_list.append({'id_tech': technicien.id_tech})
    return JsonResponse({'techniciens': techniciens_list})

# Récupère les techniciens associés à une absence identifié par l'id absence
def get_techniciens_abs(request, id_abs):
    absence = get_object_or_404(Absence, id_abs=id_abs)
    techniciens = absence.techniciens.all()
    techniciens_list = []
    for technicien in techniciens:
        techniciens_list.append({'prenom': technicien.prenom, 'nom': technicien.nom})
    return JsonResponse({'techniciens': techniciens_list})

# Renvoie un dataframe (un tableau) de Pandas contenant toutes les VGP des deux prochains mois. Si aucune VGP alors affichage du message "Vous n'avez pas de prochaines taches VGP."
def alerteVGP(request):
    dfTaches = pd.DataFrame()
    date_limite = datetime.now() + timedelta(days=60)
    taches = Tache.objects.filter(type="VGP", start__range=[datetime.now(), date_limite]).order_by('start')
    if taches:
        for tache in taches:
            dfTaches = pd.concat([dfTaches, pd.DataFrame([tache.__dict__])])
        dfTaches = dfTaches.rename(columns={'start': 'date de début', 'end': 'date de fin', 'sn': 'Serial number', 'nom_client': 'nom client', 'notification': 'Service notification'})
        
        dfTaches['date de début'] = pd.to_datetime(dfTaches['date de début'])
        dfTaches['date de début'] = dfTaches['date de début'].dt.strftime('%d/%m/%Y')

        dfTaches['date de fin'] = pd.to_datetime(dfTaches['date de fin'])
        dfTaches['date de fin'] = dfTaches['date de fin'].dt.strftime('%d/%m/%Y')

        dfTaches = dfTaches[['titre', 'date de début', 'date de fin', 'Service notification', 'Serial number', 'pn', 'lieu', 'type', 'statut', 'commentaire', 'nom client']]
        dfTaches = dfTaches.reset_index(drop=True)
        return render(request, 'Alerte.html', {'taches': dfTaches.to_html()})
    return render(request, 'Alerte.html', {'taches': "Vous n'avez pas de prochaines taches VGP."})

# Permet la création ou la modification d'une tâche reprogrammé lorsqu'une tâche de type VGP sur site est défini comme fini. 
@csrf_exempt
def save_tache(request):
    if request.method == 'POST':
        notification = int(request.POST.get("notification", None))
        nbr0 = len(str(notification))-1
        unitePoidFort = str(notification)[0]
        VALEUR_ID_REPROGRAM_A_SOUSTRAIRE = int(unitePoidFort + "0" * nbr0) # Le numéro service notification, n'est pas encore défini dans SAP lors des tache reprogrammé. J'effectue une règle pour retrouver directement mes tâches reprogrammées en fonction de sa tache initial. Comme les taches sont forcément constituées de 9 chiffres. Je récupère le 1er chiffres en partant de la gauche et je lui rajoute 8 zéros à droite. Je soustrait ensuite ma notification avec mon nouveaun nbr pour avoir la notification reprogrammé.

        Tache.objects.update_or_create(
            notification=int(int(request.POST.get("notification", None)) - VALEUR_ID_REPROGRAM_A_SOUSTRAIRE),
            defaults={
                'start': request.POST.get("start", None),
                'end': datetime.strptime(request.POST.get("end", None) + " 1:00:00", '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S'),
                'titre': "À MODIFIER, ref VGP année dernière : " + request.POST.get("titre", None),
                'notification': int(int(request.POST.get("notification", None)) - VALEUR_ID_REPROGRAM_A_SOUSTRAIRE),
                'sn': request.POST.get("sn", None),
                'pn': request.POST.get("pn", None),
                'lieu': request.POST.get("lieu", None),
                'type': request.POST.get("type", None),
                'statut': "Non valide",
                'commentaire': "Cette VGP à été reprogrammé par le système. Il faut modifier les informations en particulier le service notification !",
                'nom_client': request.POST.get("nom_client", None),
            }
        )
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})

# Permet de récupérer les absences antérieurs et ultérieurs à aujourd'hui et les séparés dans deux dataframes (tableaux) différents avant de les envoyer sur la pages Absences.html
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

    absences2 = Absence.objects.filter(end__lt=datetime.today()).order_by('-start')
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

# Récupère toutes les tâches fini et les renvoie dans un tableau html à HistoriqueTacheFini.html 
def getAllTacheFini(request) :
    taches = Tache.objects.filter(statut="fini").order_by('start')
    if not taches:
        messages.success(request, "Aucune tache n'est défini comme 'fini'.")
        return render(request, 'HistoriqueTacheFini.html', {'estVide': True})
    
    tab = '<table border="1" class="dataframe" id="tab"> <thead> <tr style="text-align: right;"></th><th></th><th>Titre</th> <th>date de début</th> <th>date de fin</th> <th>Service notification</th> <th>Serial number</th> <th>pn</th> <th>Lieu</th> <th>Type</th> <th>Statut</th><th>Nom client</th> </tr> </thead> <tbody>'
    i=0
    for tache in taches:
        start = tache.start.strftime('%d/%m/%Y')
        end = tache.end.strftime('%d/%m/%Y')
        tab += '<tr id="' + str(tache.notification) +'"><th>' + str(i) +'</th><td>' + str(tache.titre) +'</td><td>' + str(start) +'</td><td>' + str(end) +'</td><td>' + str(tache.notification) +'</td><td>' + str(tache.sn) +'</td><td>' + str(tache.pn) +'</td><td>' + str(tache.lieu) +'</td><td>' + str(tache.type) +'</td><td>' + str(tache.statut) +'</td><td>' + str(tache.nom_client) +'</td></tr>'
        i += 1
    tab += '</tbody></table>'
    return render(request, 'HistoriqueTacheFini.html', {'TachesFinies': tab, 'estVide': False})

# Permet de récupérer une absence en fonction de son identifiant et renvoie chaque information de l'absence sous forme de tableau python.
def getAbsenceById(request, id_abs):
    absence = get_object_or_404(Absence, id_abs=id_abs)
    listAbsence = []
    listAbsence.append(absence.id_abs)
    listAbsence.append(absence.motif)
    listAbsence.append(absence.start.replace(hour=12, minute=0, second=0, microsecond=0))
    listAbsence.append(absence.end.replace(hour=12, minute=0, second=0, microsecond=0))
    return JsonResponse({'absence': listAbsence})

# Permet de récupérer une tache en fonction de son identifiant et renvoie chaque information de la tache sous forme de tableau python.
def getTacheById(request, notification):
    tache = get_object_or_404(Tache, notification=notification)
    listTaches = []
    listTaches.append(tache.titre)      #0
    listTaches.append(tache.start)      #1
    listTaches.append(tache.end)        #2
    listTaches.append(tache.sn)         #3
    listTaches.append(tache.pn)         #4
    listTaches.append(tache.lieu)       #5
    listTaches.append(tache.type)       #6
    listTaches.append(tache.statut)     #7
    listTaches.append(tache.commentaire)#8
    listTaches.append(tache.nom_client) #9
    return JsonResponse({'tache': listTaches})

# Permet de modifier une absence en fonction de son identifiant
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

# Permet de supprimer une absence en fonction de son identifiant.
def removeAbsence(request, id_abs):
    absence = get_object_or_404(Absence, id_abs=id_abs)
    absence.techniciens.clear()
    absence.delete()
    data = {}
    return JsonResponse(data)

# Permet d'enregistrer des tâches à partir du fichier Excel généré par SAP. Plusieurs type d'erreurs sont pris en compte si l'opération se déroule mal.
def add_Excell_taches(request):
    if request.method != 'POST':
        messages.error(request, None)
        return render(request, 'AjoutParExcell.html')
    
    # Récupération du fichier Excell
    file = request.FILES.get('xlsx_file')
    if not file:
        messages.error(request, 'Erreur : fichier manquant.', extra_tags='erreur_Excell')
        return render(request, 'AjoutParExcell.html', {'erreur_Excell': True})
    
    # Vérification de l'extension du fichier
    if not file.name.endswith('.XLSX') :
        if not file.name.endswith('.xlsx'):
            messages.error(request, 'Erreur : le fichier doit être un document Excel avec l\'extension .xlsx.', extra_tags='erreur_Excell')
            return render(request, 'AjoutParExcell.html', {'erreur_Excell': True})
        
    # Écriture du fichier sur le disque
    try:
        filepath = os.path.join(settings.EXCELL_DIR, file.name)
        with open(filepath, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    except Exception as e:
        messages.error(request, f'Erreur lors de l\'écriture du fichier : {e}.', extra_tags='erreur_Excell')
        return render(request, 'AjoutParExcell.html', {'erreur_Excell': True})
    
    # Récupération des données du fichier Excell.
    try:
        dfFic = pd.read_excel(os.path.join(settings.EXCELL_DIR, file.name))
    except FileNotFoundError:
        messages.error(request, 'Erreur : le fichier est manquant : {e}.', extra_tags='erreur_Excell')
        return render(request, 'AjoutParExcell.html', {'erreur_Excell': True})
    except ValueError:
        messages.error(request, 'Erreur : la feuille demandée n\'existe pas : {e}.', extra_tags='erreur_Excell')
        return render(request, 'AjoutParExcell.html', {'erreur_Excell': True})
    
    # Je récupère et renomme les colonnes dont j'ai besoin.
    dfFic = dfFic[['Order', 'Requested deliv.date', 'Notification', 'Serial Number', 'Material', 'Service Material', 'System Status', 'Name 1', 'Description', 'Tech. Evaluation']]
    dfFic = dfFic.rename(columns={'Service Material': 'lieu','Material': 'pn','Requested deliv.date': 'end', 'System Status': 'type','Serial Number': 'sn', 'Name 1': 'nom_client', 'Notification': 'notification', 'Tech. Evaluation' : 'Technicien', 'Description': 'commentaire'})
    
    # On garde seulement les taches ayant une order (qui est commandé par le client)
    dfFic = dfFic.dropna(subset=['Order'])
    
    #Création des dates de départ. J'estime qu'une tache dure 7jours. Donc La date de livraison - 7 jours donne la date de début de la tache
    for index, dateF in dfFic['end'].items():
        if isinstance(dateF, pd.Timestamp):
            dateF_datetime = dateF.to_pydatetime()
            dateD = dateF_datetime - timedelta(days=7)
            dfFic.loc[index, 'start'] = dateD
            dfFic.loc[index, 'end'] = dateF_datetime.replace(hour=12, minute=0, second=0)
        else: 
            messages.error(request, 'Erreur : Les dates de fin (Requested deliv.date) doivent être au format date (JJ/MM/AAAA). (pour les devs) Si le problème persiste vérifier que les données sont au format pandas.Timestamp dans python: {e}.', extra_tags='erreur_Excell')
            return render(request, 'AjoutParExcell.html', {'erreur_Excell': True})

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
        if(nom_tech == "TITI") :
            nom_tech = "Titi"
            prenom_tech = "Léo"
        elif(nom_tech == "TOTO"):
            nom_tech = "Toto"
            prenom_tech = "Julien"
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

    # La colonne notification est castée en int. Elle passe de float à integer
    dfFic['notification'] = dfFic['notification'].astype(int)

    # Définition du titre de la tache
    for index, colonnes in dfFic[["commentaire", "notification", "nom_client"]].iterrows():
        if len(colonnes["commentaire"])>0:
            dfFic.loc[index, 'titre'] = colonnes["commentaire"]
        elif (len(colonnes["nom_client"]) != 'non renseigné' and ( len(str(colonnes["notification"]) + " " + colonnes["nom_client"]) < 51)): 
            dfFic.loc[index, 'titre'] = str(colonnes["notification"]) + " " + colonnes["nom_client"]
        else:
            dfFic.loc[index, 'titre'] = str(colonnes["notification"])
    
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

    # Le commentaire est entièrement définis à vide
    dfFic = dfFic.assign(commentaire="")
    
    # On supprime les lignes ayant une notification null
    dfFic = dfFic.dropna(subset=['notification'])
    dfFic = dfFic[['notification', 'titre','start', 'end', 'sn', 'pn', 'lieu', 'type','statut', 'nom_client', 'commentaire', 'nom', 'prenom']]
    dfFic = dfFic.reset_index(drop=True)
    
    # Mise à jour de la base de données avec le dataframe
    for index, colonnes in dfFic.iterrows():
        # création d'un dictionnaire contenant les champs à mettre à jour ou à créer
        data = {
            'notification': colonnes['notification'],
            'titre': colonnes['titre'],
            'start': colonnes['start'],
            'end': colonnes['end'],
            'sn': colonnes['sn'],
            'pn': colonnes['pn'],
            'lieu': colonnes['lieu'],
            'type': colonnes['type'],
            'statut': colonnes['statut'],
            'nom_client': colonnes['nom_client'],
            'commentaire': colonnes['commentaire'],
        }
        # mise à jour ou création de l'enregistrement correspondant dans la base de données
        Tache.objects.update_or_create(notification=colonnes['notification'], defaults=data)

    messages.success(request, 'Le fichier Excel a été importé avec succès!', extra_tags='erreur_Excell')
    return render(request, 'AjoutParExcell.html', {'erreur_Excell': True})
