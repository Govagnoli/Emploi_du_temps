from django.db import models

class Techniciens(models.Model):
    id_tech = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50,null=True,blank=True)
    prenom = models.CharField(max_length=50,null=True,blank=True)

class Abscence(models.Model):
    id_abs = models.AutoField(primary_key=True)
    motif = models.CharField(max_length=50,null=True,blank=True)
    start = models.DateTimeField(null=True,blank=True)
    end = models.DateTimeField(null=True,blank=True)
    techniciens = models.ManyToManyField(Techniciens)

class Tache(models.Model):
    id_tache = models.AutoField(primary_key=True)
    start = models.DateTimeField(null=True,blank=True)
    end = models.DateTimeField(null=True,blank=True)
    titre = models.CharField(max_length=50,null=True,blank=True)  
    num_certif = models.DecimalField(max_digits=9, decimal_places=0,null=True,blank=False)
    sn = models.CharField(max_length=50,null=True,blank=False)
    pn = models.CharField(max_length=50,null=True,blank=False)
    lieu = models.CharField(max_length=8,null=True,blank=False)
    type = models.CharField(max_length=5,null=True,blank=False)
    statut = models.CharField(max_length=8,null=True,blank=False)
    commentaire = models.CharField(max_length=300,null=True,blank=True)
    nom_client = models.CharField(max_length=50,null=True,blank=True)
    techniciens = models.ManyToManyField(Techniciens)

    class Meta:  
        db_table = "tache"