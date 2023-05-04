# Générer générique
Traite les génériques, déroulant dans un 1er temps.

Demande initiale : Générer un générique déroulant sur base d'un document Excel.

# Comment l'utiliser ?
Il faut s'assurer que le fichier [`configuration/font.csv`](configuration/font.csv) contient des polices d'écriture.

Pour générer un générique, il faut les fichier suivant dans le dossier [`examples`](example) :
* [`generique.csv`](example/generique.csv) : contient le texte du déroulant.
* [`reglage.csv`](example/reglage.csv) : paramètres du projet (résolution, vitesse de déroulement).
* [`rendu.csv`](example/reglage.csv) : paramètres d'export.
* [`style.csv`](example/style.csv) : différents styles pour le projet (font, taille, couleur, etc).

Définir le dossier de sortie.

Puis on peut run `main_generer.py`.
