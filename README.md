# Emploi_du_temps

Mon application est un emploi du temps professionnel. C'est une application web qui utilise le framework Django en Python. Elle fut développée en avril 2023.

Vous pouvez tester la démo de l'application sur le lien: [http://34.175.103.55:8080/](http://34.175.51.131:8080/)

Pour utiliser mon application, vous devez avoir une base de données MySQL (configurez votre connexion dans le fichier settings.py du répertoire devproject).

Voici la partie de settings.py correspondant à votre connexion à la base de données : J'utilise ici une base de données local avec WampServer
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

Pensez à bien télécharger les ressources nécessaires pour faire fonctionner le projet. Les requirements sont stockés dans le fichier requirements.txt.

Pour les télécharger, veuillez installer Python (j'utilise la version 3.11.1) avec pip et exécuter les commandes suivantes dans votre terminal (ou dans votre environnement virtuel du projet) :

```
pip install Django
pip install pandas
pip install mysqlclient
pip install openpyxl
```

Placez-vous dans votre répertoire racine du projet (où se trouve manage.py) et exécutez les commandes suivantes (il faut au préalable avoir une base de données MySQL nommé gestion_edt dans mon cas) :
```
python manage.py makemigrations
python manage.py migrate
```

Votre projet est maintenant configuré. Vous pouvez lancer l'application en faisant la commande (dans votre répertoire racine) :
```
python manage.py runserver
```

Vous pouvez accéder à l'application web à l'adresse suivante si vous êtes en local: http://127.0.0.1:8000
