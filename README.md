# Emploi_du_temps

Mon application est un gestionnaire d'emploi du temps pour des techniciens. C'est une application web utilisant le framework django sur python.

Pour utiliser mon application vous devez avoir une base de données MYSQL (configurer votre connexion dans le fichier settings.py du répertoire devproject)

Voici la partie de settings.py correspondant à votre connexion à la base de données :
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gestion_edt',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}
```

Penser à bien télécharger les ressources nécessaire pour faire fonctionner le projet. les requirements sont stockées dans le fichier requirements.txt. (Certains requirements sont nécessaire pour un hébergement chez heroku.)

Pour les télécharger veuillez installer python (j'utilise la version 3.11.1) avec pip
et executer les commandes suivantes dans votre terminal (ou dans votre environnement virtuel du projet) 

```
pip install Django
pip install pandas
```

Placer vous dans votre répertoire racine du projet (où se trouve manage.py) et executer les commandes suivantes
```
python manage.py makemigrations
python manage.py migrate
```

Votre projet est maintenant configuré. Vous pouvez lancer l'application en faisant la commande (dans votre répertoire racine) :
```
python manage.py runserver
```

et vous pouvez accéder à l'application web à l'adresse suivante : http://127.0.0.1:8000
