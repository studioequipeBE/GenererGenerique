#!/usr/bin/env python
#-*- coding: utf-8 -*

"""
Version : 0.9.0

Information concernant ce programme :
On utilise un dossier "TMP" à la racine de l'ordinateur ainsi qu'un sous-dossier "png" pour le rendu.
Le programme utilise également un fichier CSV sur lequel il se base pour générer le générique.

TODO : Amélioration intéressante à ajouter, savoir mettre des logos. (colonne métadonnées ?)
"""

import csv
from PIL import Image, ImageDraw, ImageFont


# Retourne un nombre sur un certain nombre de digits.
def digit(nombre_digit: int, valeur: int) -> str:
    texte = ''

    for compteur in range(0, (nombre_digit - len(str(valeur)))):
        texte = '0' + texte

    return (texte + str(valeur))


# Paramètres :
fichier_csv = 'C:\\TMP\\generique.csv'

# Résoluton :
largeur = 1920
hauteur = 1080

# Réglages :
ratio = '2.39'  # Ratio si on veut mettre un cache.
vitesse = 2  # Vitesse de defilement.

majuscule_poste = True
majuscule_nom_famille = True  # Pas opérationnel, car comment savoir ce qui est du nom de famille et du prénom ?

typo_principale = 'arial.ttf'
taille_typo = 20
espace_ligne = 2
espace = 6  # Espace entre "poste" et nom de la personne.

couleur_fond = 'black'  # Il faut une bonne raison pour que le fond ne soit pas noir.
couleur_texte = (235, 235, 235)

generique = {
    'gauche-gauche': [],  # Si on sépare en 2 : la partie de gauche.
    'droite-gauche': [],

    'gauche-centre': [],
    'centre': [],  # Généralement le nom de la section.
    'droite-centre': [],  # Nom de la personne.

    'gauche-droite': [],  # Si on sépare en 2 : la partie de droite.
    'droite-droite': [],
}

# Récupère générique d'un CSV :
with open(fichier_csv, newline='', encoding='utf-8') as csvfile:
    contenu = csv.reader(csvfile, delimiter=';', quotechar='|')
    i = 0
    for ligne in contenu:
        if i != 0:
            generique['gauche-gauche'].append(ligne[0])
            generique['droite-gauche'].append(ligne[1])

            generique['gauche-centre'].append(ligne[2])
            generique['centre'].append(ligne[3])
            generique['droite-centre'].append(ligne[4])

            generique['gauche-droite'].append(ligne[5])
            generique['droite-droite'].append(ligne[6])

        i = i + 1

fnt = ImageFont.truetype(typo_principale, taille_typo)

# TODO : on devrait, depuis le nombre de ligne du CSV calculer le nombre d'image nécessaire.
nb_image = 600

for j in range(0, nb_image):
    print('Image : ' + str(j) + '/' + str(nb_image))

    # L'image PNG.
    image = Image.new(mode='RGB', size=(1920, 1080), color=couleur_fond)

    # create new image
    draw = ImageDraw.Draw(image)
    draw.fontmode = 'l'  # Anti-aliasing. TODO : je ne sais pas s'il fonctionne...

    for i in range(0, len(generique['centre'])):
        # Pour anchor : https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html

        draw.text(
            xy=(
                (largeur / 3) - espace,
                hauteur + ((taille_typo + espace_ligne) * i) - (j * (vitesse * 2))
            ),
            text=generique['gauche-gauche'][i].upper() if majuscule_poste else generique['gauche'][i],
            font=fnt,
            fill=couleur_texte,
            anchor='rs'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la droite.
        )
        draw.text(
            xy=(
                (largeur / 3) + espace,
                hauteur + ((taille_typo + espace_ligne) * i) - (j * (vitesse * 2))
            ),
            text=generique['droite-gauche'][i],
            font=fnt,
            fill=couleur_texte,
            anchor='ls'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la gauche.
        )

        # Centre
        draw.text(
            xy=(
                (largeur / 2) - espace,
                hauteur + ((taille_typo + espace_ligne) * i) - (j * (vitesse * 2))
            ),
            text=generique['gauche-centre'][i].upper() if majuscule_poste else generique['gauche'][i],
            font=fnt,
            fill=couleur_texte,
            anchor='rs'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la droite.
        )
        draw.text(
            xy=(
                (largeur / 2),
                hauteur + ((taille_typo + espace_ligne) * i) - (j * (vitesse * 2))
            ),
            text=generique['centre'][i],
            font=fnt,
            fill=couleur_texte,
            anchor='ms'  # Dire qu'on est basé sur la "baseline" et d'aligner le texte au centre.
        )
        draw.text(
            xy=(
                (largeur / 2) + espace,
                hauteur + ((taille_typo + espace_ligne) * i) - (j * (vitesse * 2))
            ),
            text=generique['droite-centre'][i],
            font=fnt,
            fill=couleur_texte,
            anchor='ls'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la gauche.
        )

        # Droite
        draw.text(
            xy=(
                ((largeur / 3) * 2) - espace,
                hauteur + ((taille_typo + espace_ligne) * i) - (j * (vitesse * 2))
            ),
            text=generique['gauche-droite'][i].upper() if majuscule_poste else generique['gauche'][i],
            font=fnt,
            fill=couleur_texte,
            anchor='rs'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la droite.
        )
        draw.text(
            xy=(
                ((largeur / 3) * 2) + espace,
                hauteur + ((taille_typo + espace_ligne) * i) - (j * (vitesse * 2))
            ),
            text=generique['droite-droite'][i],
            font=fnt,
            fill=couleur_texte,
            anchor='ls'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la gauche.
        )

    draw.rectangle(((0, 0), (largeur, 140)), fill='black')
    draw.rectangle(((0, hauteur), (largeur, hauteur - 140)), fill='black')

    # Après création de l'image, on sauve.
    image.save('C:\\TMP\\png\\generique_' + digit(8, j) + '.png')
