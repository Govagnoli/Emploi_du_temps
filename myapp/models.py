from django.db import models
# Le model django permet de gérer une base de données. Ici dans notre application se connecte à une BD MySQL local (configuré dans les settings.py)

# Génère la table myapp_techniciens
class Techniciens(models.Model):
    id_tech = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50,null=True,blank=True)
    prenom = models.CharField(max_length=50,null=True,blank=True)

# Génère la table myapp_absence, et la table d'association myapp_absence_techniciens
class Absence(models.Model):
    id_abs = models.AutoField(primary_key=True)
    motif = models.CharField(max_length=50,null=True,blank=True)
    start = models.DateTimeField(null=True,blank=True)
    end = models.DateTimeField(null=True,blank=True)
    techniciens = models.ManyToManyField(Techniciens)

# Génère la table Tache, et la table d'association tache_techniciens
class Tache(models.Model):
    notification = models.IntegerField(primary_key=True)
    start = models.DateTimeField(null=True,blank=True)
    end = models.DateTimeField(null=True,blank=True)
    titre = models.CharField(max_length=100,null=True,blank=True)    
    sn = models.CharField(max_length=50,null=True,blank=False)
    pn = models.CharField(max_length=50,null=True,blank=False)
    lieu = models.CharField(max_length=8,null=True,blank=False)
    type = models.CharField(max_length=5,null=True,blank=False)
    statut = models.CharField(max_length=10,null=True,blank=False)
    commentaire = models.CharField(max_length=300,null=True,blank=True)
    nom_client = models.CharField(max_length=50,null=True,blank=True)
    techniciens = models.ManyToManyField(Techniciens)

    class Meta:  
        db_table = "tache"