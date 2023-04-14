from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from myapp.forms import tachesForm 
from myapp.models import Tache
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
    all_taches = Tache.objects.all()                                                                                    
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
            'start': tache.start,                                                         
            'end': tache.end + timedelta(days=1),
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
            'textColor': '#F5F3F3'                                                             
        })
    return JsonResponse(out, safe=False) 

# À partir du formulaire ajouter un évènement permet d'ajouter une tâche et ses techniciens associés dans la base de données 
def add_tache(request):
    if request.method == "POST":
        form = tachesForm(request.POST)
        if form.is_valid():
            tache = form.save(commit=False)
            techniciens = form.cleaned_data['techniciens']
            tache.save()
            tache.techniciens.set(techniciens)
            return redirect('index') # Redirige vers la page d'accueil après ajout réussi
    else:
        form = tachesForm()
    return render(request, 'ajout.html', {'form': form})

# À partir du calendrier permet lors de la modification d'une tache existante de mettre à jour les données et donc de possiblement les modifier
# à noter que toutes les données sont modifiés. Ca récupère toutes les données du formulaire puis écrase les données de la tache dans la base de données
def modifier_tache(request, id_tache):
    instance = get_object_or_404(Tache, id_tache=id_tache)
    form = tachesForm(request.POST, instance=instance)
    if form.is_valid():
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
        start = datetime.strptime(start_str, '%Y-%m-%d').date()
        end = datetime.strptime(end_str, '%Y-%m-%d').date()
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

def alerteVGP(request):
    dfTaches = pd.DataFrame()
    date_limite = datetime.now() + timedelta(days=60)
    taches = Tache.objects.filter(type="VGP", start__range=[datetime.now(), date_limite]).order_by('start')
    for tache in taches:
         dfTaches = pd.concat([dfTaches, pd.DataFrame([tache.__dict__])])
    dfTaches[['date de début', 'date de fin', 'Serial number', 'nom client']] = dfTaches[['start', 'end', 'sn', 'nom_client']]     
    dfTaches = dfTaches[['titre', 'date de début', 'date de fin', 'num_certif', 'Serial number', 'pn', 'lieu', 'type', 'statut', 'commentaire', 'nom client']]
    dfTaches = dfTaches.reset_index(drop=True)
    return render(request, 'Alerte.html', {'taches': dfTaches.to_html()})

@csrf_exempt
def save_tache(request):
    if request.method == 'POST':
        Tache.objects.create(
            titre = request.POST.get("titre", None),
            start = request.POST.get("start", None),
            end = request.POST.get("end", None),
            num_certif = request.POST.get("num_certif", None),
            sn = request.POST.get("sn", None),
            pn = request.POST.get("pn", None),
            lieu = request.POST.get("lieu", None),
            type = request.POST.get("type", None),
            statut = request.POST.get("statut", None),
            nom_client = request.POST.get("nom_client", None),
            commentaire = request.POST.get("commentaire", None)
        )
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False})