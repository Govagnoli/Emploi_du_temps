from django.contrib import admin
from django.urls import path
from myapp import views  
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'), 
    path('all_taches/', views.all_taches, name='all_taches'), 
    path('add_tache/', views.add_tache, name='add_tache'), 
    path('update/<int:id_tache>/', views.update, name='update'),
    path('remove/<int:id_tache>/', views.remove, name='remove'),
    path('get_techniciens/<int:id_tache>/', views.get_techniciens, name='get_techniciens'),
    path('modifier_tache/<int:id_tache>/', views.modifier_tache, name='modifier_tache'),
    path('alerteVGP/', views.alerteVGP, name='alerteVGP'),
    path('save_tache/', views.save_tache, name='save_tache'),
]