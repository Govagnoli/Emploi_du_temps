# Emploi_du_temps

Mon application est un gestionnaire d'emploi du temps pour des techniciens. C'est une application web qui utilise le framework Django en Python.

Pour utiliser mon application, vous devez avoir une base de données MySQL (configurez votre connexion dans le fichier settings.py du répertoire devproject).

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

Pensez à bien télécharger les ressources nécessaires pour faire fonctionner le projet. Les requirements sont stockés dans le fichier requirements.txt. (Certains requirements sont nécessaires pour un hébergement chez Heroku.)

Pour les télécharger, veuillez installer Python (j'utilise la version 3.11.1) avec pip et exécuter les commandes suivantes dans votre terminal (ou dans votre environnement virtuel du projet) :

```
pip install Django
pip install pandas
pip install mysqlclient
pip install openpyxl
```

Placez-vous dans votre répertoire racine du projet (où se trouve manage.py) et exécutez les commandes suivantes :
```
python manage.py makemigrations
python manage.py migrate
```

Votre projet est maintenant configuré. Vous pouvez lancer l'application en faisant la commande (dans votre répertoire racine) :
```
python manage.py runserver
```

Vous pouvez accéder à l'application web à l'adresse suivante : http://127.0.0.1:8000

Quelques images de quoi ressemble l'application:

Le calendrier avec FullCalendar

![image](https://user-images.githubusercontent.com/81430707/234508179-8485b8d7-00e1-46a3-acb4-4c2d1fa3f5c5.png)
![image](https://user-images.githubusercontent.com/81430707/234509741-10c7cfbf-7975-4163-8b52-259ae9da0779.png)

Les popUps bootstrap pour avoir une description des taches et pour modifier/supprimer facilement les tâches

![image](https://user-images.githubusercontent.com/81430707/234510794-4b5a0960-2d1b-4418-a348-395f9881124d.png)
![image](https://user-images.githubusercontent.com/81430707/234510651-d0319934-aa2b-45b6-aaf7-b4b29841e530.png)

Permet l'importation des données par fichier Excel

![image](https://user-images.githubusercontent.com/81430707/234508254-4867dabe-bb51-439c-b4db-9da617d11550.png)

Permet l'ajout d'absences

![image](https://user-images.githubusercontent.com/81430707/234511241-7f81d764-d1ca-4152-88b4-1b911578cd05.png)

Permet de voir les absences. Le tableau est interactif. On peut cliquer sur les élements pour la modification ou la suppression

![image](https://user-images.githubusercontent.com/81430707/234508453-618a7904-d845-4d78-82c0-4dd99d31cf87.png)
![image](https://user-images.githubusercontent.com/81430707/234511905-d9aaaa86-38ee-4af7-9e73-d7e869af316b.png)

Permet de visualiser certains type de tâches sur une période dynamique

![image](https://user-images.githubusercontent.com/81430707/234512923-cabd011b-d064-4479-a5a8-50054320de68.png)







