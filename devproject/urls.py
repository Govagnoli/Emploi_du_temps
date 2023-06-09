from django.contrib import admin
from django.urls import path
from myapp import views  

# Permet d'associer une url avec la view en question
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'), 
    path('all_taches/', views.all_taches, name='all_taches'),
    path('all_absences/', views.all_absences, name='all_absences'), 
    path('add_tache/', views.add_tache, name='add_tache'),
    path('add_absence/', views.add_absence, name='add_absence'), 
    path('update/<int:notification>/', views.update, name='update'),
    path('remove/<int:notification>/', views.remove, name='remove'),
    path('get_techniciens/<int:notification>/', views.get_techniciens, name='get_techniciens'),
    path('get_techniciens_abs/<int:id_abs>/', views.get_techniciens_abs, name='get_techniciens_abs'),
    path('modifier_tache/<int:oldNotification>/<int:newNotification>/', views.modifier_tache, name='modifier_tache'),
    path('alerteVGP/', views.alerteVGP, name='alerteVGP'),
    path('save_tache/', views.save_tache, name='save_tache'),
    path('absences/', views.absences, name='absences'),
    path('getAbsenceById/<int:id_abs>/', views.getAbsenceById, name='getAbsenceById'),
    path('modifier_absence/<int:id_abs>/', views.modifier_absence, name='modifier_modifier_absencetache'),
    path('removeAbsence/<int:id_abs>/', views.removeAbsence, name='removeAbsence'),
    path('add_Excell_taches/', views.add_Excell_taches, name='add_Excell_taches'),   
    path('get_Id_techniciens/<int:notification>/', views.get_Id_techniciens, name='get_Id_techniciens'), 
    path('getAllTacheFini/', views.getAllTacheFini, name='getAllTacheFini'),
    path('getTacheById/<int:notification>/', views.getTacheById, name='getTacheById'),        
]