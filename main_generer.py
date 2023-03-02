#!/usr/bin/env python
#-*- coding: utf-8 -*

"""
Version : 0.9.0

Information concernant ce programme :
On utilise un dossier "TMP" à la racine de l'ordinateur ainsi qu'un sous-dossier "png" pour le rendu.
Le programme utilise également un fichier CSV sur lequel il se base pour générer le générique.

TODO : Utiliser la 1ère ligne du générique pour définir preset pour toute une colonne.
"""

import platform
import csv
import cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw

dossier_travail = '/Users/macdevpro/Documents/GENERIQUE/'


# Indique si la font renseignée est pour cet OS.
def fontPourCetOS(os: str) -> bool:
    notre_os = platform.system()

    if notre_os == 'Darwin':
        notre_os = 'MacOS'

    if os == notre_os:
        return True
    else:
        return False


# Test que la font est disponible sur cette machine.
def fontExiste(fichier_font: str) -> bool:
    try:
        # Essaie de récupérer la font, on met une taille au pif, cela n'influence pas la recherche.
        ImageFont.truetype(fichier_font, 10)
        return True
    except:
        return False


# Retourne un nombre sur un certain nombre de digits.
def digit(nombre_digit: int, valeur: int) -> str:
    texte = ''

    for compteur in range(0, (nombre_digit - len(str(valeur)))):
        texte = '0' + texte

    return texte + str(valeur)


liste_font = []

# Récupère dans un CSV les fonts/polices qu'on peut utiliser :
with open(dossier_travail + 'ELEMENTS/CSV/font.csv', newline='', encoding='utf-8') as csvfile:
    contenu = csv.reader(csvfile, delimiter=';', quotechar='|')

    i = 0
    for ligne in contenu:
        if i != 0:
            # Il peut y avoir des lignes vides par erreur et on vérifie que la font est pour cet OS.
            if ligne[0] != '' and fontPourCetOS(ligne[1]):
                print('Font pour cet OS : ' + ligne[0])

                # Vérifie que chaque font existe. Si elle n'existe pas, on avertit par un message. Si le champ est vide c'est qu'on sait qu'il n'est pas supporté.
                for f in range(2, 5 + 1):
                    if ligne[f] != '' and not fontExiste(ligne[f]):
                        print('La font "' + ligne[0] + '" avec le fichier "' + ligne[f] + '" n\'existe pas.')

                # Même si des fichiers ne sont pas trouvé pour une font, on ne sait pas pour autant s'ils sont utilisé pour ce générique.
                liste_font.append({
                    'nom': ligne[0],
                    'normal': ligne[2],  # Ici ce sont les noms de fichier.
                    'gras': ligne[3],
                    'italique': ligne[4],
                    'italique-gras': ligne[5]
                    # [6] étant les commentaires, pas nécessaire dans le programme.
                })

        i = i + 1


print('Nombre de font(s) trouvée(s) : ' + str(len(liste_font)))


# Récupère une font via son nom (pas case sensitive).
def findFontByName(nom: str):
    for font in liste_font:
        if font['nom'].lower() == nom.lower():
            return font

    return None


liste_style = []


# Récupère le "tuple" (R, G, B, A) couleur d'une cellule.
def decodeCouleur(couleur: str) -> tuple:
    # On pourrait voir pour gérer l'hexadécimal + s'il n'y a pas d'alpha = 255 par-défaut.

    canaux = couleur.split()
    return (int(canaux[0]), int(canaux[1]), int(canaux[2]), int(canaux[3]))


# Normalement s'il y a une valeur, on la converti en int, sinon on met la valeur par défaut.
def intElseDefault(valeur: str, defaut: int) -> int:
    if valeur != '':
        return int(valeur)
    else:
        return defaut


# Récupère dans un CSV les différents styles du projet :
with open(dossier_travail + 'ELEMENTS/CSV/style.csv', newline='', encoding='utf-8') as csvfile:
    contenu = csv.reader(csvfile, delimiter=';', quotechar='|')

    i = 0
    for ligne in contenu:
        if i != 0:

            # Il se peut qu'on mette des lignes vides (par erreur ou autre).
            if ligne[0] != '':

                font = findFontByName(ligne[1])  # Récupère toutes les possibilités.
                if ligne[4] == 'True' and ligne[5] == 'True':
                    font = font['italique-gras']
                elif ligne[5] == 'True':
                    font = font['italique']
                elif ligne[4] == 'True':
                    font = font['gras']
                else:
                    font = font['normal']

                souligner = True if ligne[6] == 'True' else False

                liste_style.append({
                    'nom': ligne[0],
                    'font': font,
                    'taille': int(ligne[2]),
                    'couleur': decodeCouleur(ligne[3]),
                    'souligner': souligner,
                    'epaisseur_souligner': intElseDefault(ligne[7], 1) if souligner else None,  # Epaisseur de la ligne pour le souligner.
                    'espace_souligner': intElseDefault(ligne[8], 0) if souligner else None,  # Espace entre texte et ligne pour le souligner.
                    'espace_gauche_droite': intElseDefault(ligne[9], 6),
                    'espace_ligne': intElseDefault(ligne[10], 2),
                    'espace_3colonnes': intElseDefault(ligne[11], 0)
                    # [12] étant les commentaires, on n'en a pas besoin dans le programme.
                })

        i = i + 1

print('Nombre de style(s) trouvée(s) : ' + str(len(liste_style)))


# Récupère un style selon son nom :
def findStyleByName(nom: str):

    if nom is None:
        return None

    for style in liste_style:
        if style['nom'].lower() == nom.lower():
            return style

    return None


# Paramètres :
fichier_csv = dossier_travail + 'ELEMENTS/CSV/generique.csv'


# Récupère dans un CSV les réglages du projet :
with open(dossier_travail + 'ELEMENTS/CSV/reglage.csv', newline='', encoding='utf-8') as csvfile:
    contenu = csv.reader(csvfile, delimiter=';', quotechar='|')

    i = 0
    for ligne in contenu:
        if i > 1:
            # Résoluton :
            largeur = int(ligne[0])
            hauteur = int(ligne[1])

            # Réglages :
            ratio = ligne[2]  # Ratio si on veut mettre un cache.
            vitesse = float(ligne[3])  # Vitesse de defilement.

            style_general = findStyleByName(ligne[4])

            print('Style général : ' + str(style_general))

            couleur_fond = decodeCouleur(ligne[5])  # Il faut une bonne raison pour que le fond ne soit pas noir.
            couleur_blanking = decodeCouleur(ligne[6])  # Couleur des blankings.

        i = i + 1

# Récupère dans un CSV les réglages d'exports (in, out -> pas résolution ???) du projet :
with open(dossier_travail + 'ELEMENTS/CSV/rendu.csv', newline='', encoding='utf-8') as csvfile:
    contenu = csv.reader(csvfile, delimiter=';', quotechar='|')

    i = 0
    for ligne in contenu:
        if i != 0:
            in_rendu = None if ligne[0] == 'None' else int(ligne[0])
            out_rendu = None if ligne[1] == 'None' else int(ligne[1])
            filtre_anti_aliasing = True if ligne[2] == 'True' else False

        i = i + 1


# Valeur du crop si un output blanking est appliqué (si un output blanking n'est pas reconnu, on n'en met pas).
crop = 0

# Crop HD :
if ratio == '2.39':
    crop = 138
elif ratio == '1.85':
    crop = 21
elif ratio == '2.00':
    crop = 60
elif ratio == '2.1':
    crop = 83
else:
    crop = 0

generique = {
    'gauche-gauche': [],  # Si on sépare en 2 : la partie de gauche.
    'style-gauche-gauche': [],
    'gauche-centre': [],
    'style-gauche-centre': [],
    'gauche-droite': [],
    'style-gauche-droite': [],

    'centre-gauche': [],
    'style-centre-gauche': [],
    'centre-centre': [],  # Généralement le nom de la section.
    'image-centre-centre': [],
    'style-centre-centre': [],
    'centre-droite': [],  # Nom de la personne.
    'style-centre-droite': [],

    'droite-gauche': [],  # Si on sépare en 2 : la partie de droite.
    'style-droite-gauche': [],
    'droite-centre': [],
    'style-droite-centre': [],
    'droite-droite': [],
    'style-droite-droite': [],

    'style-ligne': [],

    'y_debut': [],
    'y_fin': []
}


# Style de la colonne est spécifique à cette entrée, mais le style de la ligne peut influencer le tout.
# Le style général est là s'il n'y a rien d'autre.
def getStyle(style_general, style_colonne, style_ligne):
    # Définit le style général comme le par-défaut.
    style = {
        'font': style_general['font'],
        'taille': style_general['taille'],
        'couleur': style_general['couleur'],
        'souligner': style_general['souligner'],
        'epaisseur_souligner': style_general['epaisseur_souligner'],
        'espace_souligner': style_general['espace_souligner'],
        'espace_gauche_droite': style_general['espace_gauche_droite'],
        'espace_ligne': style_general['espace_ligne'],
        'espace_3colonnes': style_general['espace_3colonnes'],
        'debut_x': 0  # Définit la valeur où le texte se positionne sur l'image en horizontal.
    }

    # Si on a un style dans la colonne, on l'utilise :
    if style_colonne is not None:
        style['font'] = style_colonne['font']
        style['taille'] = style_colonne['taille']
        style['couleur'] = style_colonne['couleur']
        style['souligner'] = style_colonne['souligner']
        style['epaisseur_souligner'] = style_colonne['epaisseur_souligner']
        style['espace_souligner'] = style_colonne['espace_souligner']
        style['espace_gauche_droite'] = style_colonne['espace_gauche_droite']

    # Si on a un style dans la colonne "style-ligne", on l'utilise :
    if style_ligne is not None:
        style['espace_3colonnes'] = style_ligne['espace_3colonnes']
        style['espace_ligne'] = style_ligne['espace_ligne']

    style['font_objet'] = ImageFont.truetype(style['font'], style['taille'])

    return style


# Trouve un paramètre ("espacer", par exemple) dans la colonne "style".
def styleValeurChiffre(style: str, parametre: str) -> int:
    elements = style.split()

    for n in range(0, len(elements)):
        if elements[n] == parametre:
            return int(elements[n + 1])

    return 0


# Si un parametre existe, on retourne True.
def styleValeurExiste(style: str, parametre: str) -> bool:
    elements = style.split()

    for n in range(0, len(elements)):
        if elements[n] == parametre:
            return True

    return False


# On calcule une fois pour toute la position des colonnes.
colonne_gauche = int(largeur / 3)
colonne_centre = int(largeur / 2)
colonne_droite = int((largeur / 3) * 2)

# Récupère générique d'un CSV :
with open(fichier_csv, newline='', encoding='utf-8') as csvfile:
    contenu = csv.reader(csvfile, delimiter=';', quotechar='|')

    i = 0
    for ligne in contenu:
        # A la ligne 2, on a les lignes qui concernent le générique.
        if i > 1:

            # Si la colonne "style-ligne" a quelque chose, on le renseigne.
            style_ligne = None
            if ligne[18] != '':
                style_ligne = {
                    'espace_3colonnes': styleValeurChiffre(ligne[18], 'espace_3colonnes'),
                    'espace_ligne': styleValeurChiffre(ligne[18], 'espace_ligne')
                }

            generique['gauche-gauche'].append(ligne[0].rstrip())
            generique['style-gauche-gauche'].append(getStyle(style_general, findStyleByName(ligne[1]), style_ligne))
            generique['style-gauche-gauche'][-1]['debut_x'] = colonne_gauche - generique['style-gauche-gauche'][-1]['espace_gauche_droite'] - generique['style-gauche-gauche'][-1]['espace_3colonnes']
            generique['gauche-centre'].append(ligne[2].strip())
            generique['style-gauche-centre'].append(getStyle(style_general, findStyleByName(ligne[3]), style_ligne))
            generique['style-gauche-centre'][-1]['debut_x'] = colonne_gauche - generique['style-gauche-centre'][-1]['espace_3colonnes']
            generique['gauche-droite'].append(ligne[4].lstrip())
            generique['style-gauche-droite'].append(getStyle(style_general, findStyleByName(ligne[5]), style_ligne))
            generique['style-gauche-droite'][-1]['debut_x'] = colonne_gauche + generique['style-gauche-droite'][-1]['espace_gauche_droite'] - generique['style-gauche-droite'][-1]['espace_3colonnes']

            generique['centre-gauche'].append(ligne[6].rstrip())
            generique['style-centre-gauche'].append(getStyle(style_general, findStyleByName(ligne[7]), style_ligne))
            generique['style-centre-gauche'][-1]['debut_x'] = colonne_centre - generique['style-centre-gauche'][-1]['espace_gauche_droite']

            analyse = ligne[8].split()

            # S'il y a deux éléments, peut-être que c'est une image.
            if len(analyse) == 2:
                if analyse[0] == '<image>':
                    generique['image-centre-centre'].append(analyse[1])
                else:
                    generique['image-centre-centre'].append(None)
                    generique['centre-centre'].append(ligne[8].strip())
            else:
                generique['image-centre-centre'].append(None)
                generique['centre-centre'].append(ligne[8].strip())

            style_centre = getStyle(style_general, findStyleByName(ligne[9]), style_ligne)

            generique['style-centre-centre'].append(style_centre)
            generique['style-centre-centre'][-1]['debut_x'] = colonne_centre
            generique['centre-droite'].append(ligne[10].lstrip())
            generique['style-centre-droite'].append(getStyle(style_general, findStyleByName(ligne[11]), style_ligne))
            generique['style-centre-droite'][-1]['debut_x'] = colonne_centre + generique['style-centre-droite'][-1]['espace_gauche_droite']

            generique['droite-gauche'].append(ligne[12].rstrip())
            generique['style-droite-gauche'].append(getStyle(style_general, findStyleByName(ligne[13]), style_ligne))
            generique['style-droite-gauche'][-1]['debut_x'] = colonne_droite - generique['style-droite-gauche'][-1]['espace_gauche_droite'] + generique['style-droite-gauche'][-1]['espace_3colonnes']
            generique['droite-centre'].append(ligne[14].strip())
            generique['style-droite-centre'].append(getStyle(style_general, findStyleByName(ligne[15]), style_ligne))
            generique['style-droite-centre'][-1]['debut_x'] = colonne_droite + generique['style-droite-centre'][-1]['espace_3colonnes']
            generique['droite-droite'].append(ligne[16].lstrip())
            generique['style-droite-droite'].append(getStyle(style_general, findStyleByName(ligne[17]), style_ligne))
            generique['style-droite-droite'][-1]['debut_x'] = colonne_droite + generique['style-droite-droite'][-1]['espace_gauche_droite'] + generique['style-droite-droite'][-1]['espace_3colonnes']

            debut_y = hauteur  # La 1ère fois, la valeur est la hauteur de l'image (pour commencer hor-champ.
            if len(generique['y_fin']) != 0:
                debut_y = generique['y_fin'][-1]

            debut_y = debut_y + style_centre['taille']  # On doit ajouter la taille du texte, sinon cela ne fonctionne pas.

            generique['y_debut'].append(debut_y)

            hauteur_texte = debut_y + style_centre['espace_ligne']

            generique['y_fin'].append(hauteur_texte)

            generique['style-ligne'].append(style_ligne)
        elif i == 1:
            print('Ligne 1, ligne de réglage par colonne : ' + str(ligne))

        i = i + 1

print('Dernier y : ' + str(generique['y_fin'][-1]))

# Taille de l'image PNG avec tout le générique. On doit rajouter encore une fois la hauteur pour que le dernier texte quitte l'écran.
# On soustrait la taille du dernier texte...
hauteur_image = generique['y_fin'][-1] - generique['style-centre-centre'][-1]['espace_ligne'] - (generique['style-centre-centre'][-1]['taille'] * 2) + hauteur

print('Taille théorique de l\'image : ' + str(hauteur_image))

# Pour calculer le déroulant, on ne doit pas tenir compte de la hauteur ajouté, ce n'est pas de l'image utile.
nb_image = (hauteur_image - hauteur) / vitesse

# S'il y a un morceau d'image nécessaire, on ajoute une image.
if (nb_image % 1) > 0:
    nb_image = int(nb_image) + 1

print('Durée calculée du générique (en image) : ' + str(nb_image))  # 4615


# Ecrit un texte dans l'image.
def drawText(draw, xy, texte, style, anchor):
    draw.text(
        xy=xy,
        text=texte,
        font=style['font_objet'],
        fill=style['couleur'],
        anchor=anchor
    )

    # Si doit être souligné le texte.
    if style['souligner']:
        left, top, right, bottom = draw.textbbox(xy=(0, 0), text=texte, font=style['font_objet'])
        twidth = right - left
        if anchor == 'rs':
            lx = xy[0] - twidth  # Pour mettre sur la gauche.
        elif anchor == 'ms':
            lx = xy[0] - (twidth / 2)  # Centre pour ms
        elif anchor == 'ls':
            lx = xy[0]  # Pour mettre sur la droite.
        else:
            lx = 0

        # Souligne de l'épaisseur demandée.
        # style['espace_souligner'] = à partir de quand on souligne (si espace entre texte et ligne).
        for l_px in range(style['espace_souligner'], style['espace_souligner'] + style['epaisseur_souligner']):
            draw.line((lx, xy[1] + l_px, lx + twidth, xy[1] + l_px), fill=style['couleur'])


in_rendu = in_rendu if in_rendu is not None else 0
out_rendu = out_rendu if out_rendu is not None else nb_image

# Créé une grande image du générique.

# L'image PNG.
# Pas de canal alpha en plus.
image = Image.new(mode='RGBA', size=(largeur, hauteur_image), color=couleur_fond)

# create new image
draw = ImageDraw.Draw(image)
draw.fontmode = 'l'  # Anti-aliasing. TODO : je ne sais pas s'il fonctionne...

for i in range(0, len(generique['centre-centre'])):
    # Pour anchor : https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html

    hauteur_texte = generique['y_debut'][i]

    # Gauche :
    if generique['gauche-gauche'][i] != '':
        drawText(
            draw=draw,
            xy=(
                generique['style-gauche-gauche'][i]['debut_x'],
                hauteur_texte
            ),
            texte=generique['gauche-gauche'][i],
            style=generique['style-gauche-gauche'][i],
            anchor='rs'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la droite.
        )
    if generique['gauche-centre'][i] != '':
        drawText(
            draw=draw,
            xy=(
                generique['style-gauche-centre'][i]['debut_x'],
                hauteur_texte
            ),
            texte=generique['gauche-centre'][i],
            style=generique['style-gauche-centre'][i],
            anchor='ms'  # Dire qu'on est basé sur la "baseline" et d'aligner au centre.
        )
    if generique['gauche-droite'][i] != '':
        drawText(
            draw=draw,
            xy=(
                generique['style-gauche-droite'][i]['debut_x'],
                hauteur_texte
            ),
            texte=generique['gauche-droite'][i],
            style=generique['style-gauche-droite'][i],
            anchor='ls'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la gauche.
        )

    # Centre :
    if generique['centre-gauche'][i] != '':
        drawText(
            draw=draw,
            xy=(
                generique['style-centre-gauche'][i]['debut_x'],
                hauteur_texte
            ),
            texte=generique['centre-gauche'][i],
            style=generique['style-centre-gauche'][i],
            anchor='rs'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la droite.
        )
    if generique['centre-centre'][i] != '':
        drawText(
            draw=draw,
            xy=(
                generique['style-centre-centre'][i]['debut_x'],
                hauteur_texte
            ),
            texte=generique['centre-centre'][i],
            style=generique['style-centre-centre'][i],
            anchor='ms'  # Dire qu'on est basé sur la "baseline" et d'aligner le texte au centre.
        )
    if generique['centre-droite'][i] != '':
        drawText(
            draw=draw,
            xy=(
                generique['style-centre-droite'][i]['debut_x'],
                hauteur_texte
            ),
            texte=generique['centre-droite'][i],
            style=generique['style-centre-droite'][i],
            anchor='ls'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la gauche.
        )

    # S'il y a une image, on l'ajoute.
    if generique['image-centre-centre'][i] is not None:
        image_ajouter = Image.open(dossier_travail + 'ELEMENTS/IMAGE/' + generique['image-centre-centre'][i])
        # Le mask est obligatoire pour une image alpha car sinon cela "ajoute l'alpha" à l'image (remplace le fond par un truc transparent).
        # Du coup avec le masque, on code que les pixels qui changent.
        image.paste(image_ajouter, (int(colonne_centre - (image_ajouter.width/2)), hauteur_texte), mask=image_ajouter)

    # Droite :
    if generique['droite-gauche'][i] != '':
        drawText(
            draw=draw,
            xy=(
                generique['style-droite-gauche'][i]['debut_x'],
                hauteur_texte
            ),
            texte=generique['droite-gauche'][i],
            style=generique['style-droite-gauche'][i],
            anchor='rs'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la droite.
        )
    if generique['droite-centre'][i] != '':
        drawText(
            draw=draw,
            xy=(
                generique['style-droite-centre'][i]['debut_x'],
                hauteur_texte
            ),
            texte=generique['droite-centre'][i],
            style=generique['style-droite-centre'][i],
            anchor='ms'  # Dire qu'on est basé sur la "baseline" et d'aligner au centre.
        )
    if generique['droite-droite'][i] != '':
        drawText(
            draw=draw,
            xy=(
                generique['style-droite-droite'][i]['debut_x'],
                hauteur_texte
            ),
            texte=generique['droite-droite'][i],
            style=generique['style-droite-droite'][i],
            anchor='ls'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la gauche.
        )

str_largeur = str(largeur)
str_hauteur = str(hauteur)

# Après création de l'image, on sauve.
image.save(dossier_travail + 'EXPORTS/generique_ref_' + str_largeur + 'x' + str_hauteur + '.png')

# -- Quelques configs pour flou vertical : --
size = 5  # Grandeur du flou.
# generating the kernel (?)
kernel_motion_blur = np.zeros((size, size))

# Que vertial :
kernel_motion_blur[:, int((size - 1) / 2)] = np.ones(size)

kernel_motion_blur = kernel_motion_blur / size

# Valeur en plus à la fin, plus lumineux, mais mieux pour lisibilité... C'est +9%
"""
kernel_motion_blur[0, 3] = 0.082857142857143 + 0.00
kernel_motion_blur[1, 3] = 0.142857142857143 + 0.02
kernel_motion_blur[2, 3] = 0.162857142857143 + 0.02
kernel_motion_blur[3, 3] = 0.222857142857143 + 0.01  # Milieu, 0,142857142857143 pour 7 valeurs.
kernel_motion_blur[4, 3] = 0.162857142857143 + 0.02
kernel_motion_blur[5, 3] = 0.142857142857143 + 0.02
kernel_motion_blur[6, 3] = 0.082857142857143 + 0.00
"""
# Ajoute 3% de luminosité.
kernel_motion_blur[0, 2] = 0.2 - 0.080
kernel_motion_blur[1, 2] = 0.2 - 0.060 + 0.01
kernel_motion_blur[2, 2] = 0.2 + 0.280 + 0.02  # Milieu, 0,142857142857143 pour 7 valeurs.
kernel_motion_blur[3, 2] = 0.2 - 0.060 + 0.01
kernel_motion_blur[4, 2] = 0.2 - 0.080
# -- Fin config flou vertical. --

# À partir de la grande image, on génère la séquence d'image :
for i in range(in_rendu, out_rendu):
    print(str(i) + '/' + str(out_rendu))
    decalage = int(i * vitesse)
    sequence = image.crop((0, decalage, largeur, hauteur + decalage))

    # L'output blanking :
    if crop != 0:
        draw = ImageDraw.Draw(sequence)
        draw.rectangle(((0, 0), (largeur, crop)), fill=couleur_blanking)
        draw.rectangle(((0, hauteur), (largeur, hauteur - crop)), fill=couleur_blanking)

    nom_fichier = dossier_travail + 'EXPORTS/normal/generique_' + str_largeur + 'x' + str_hauteur + '_' + digit(8, i) + '.png'
    sequence.save(nom_fichier)

    # Motion blur :
    if filtre_anti_aliasing:
        # Applique le "kernel" sur l'image.
        output = cv2.filter2D(cv2.imread(nom_fichier), -1, kernel_motion_blur)
        cv2.imwrite(dossier_travail + 'EXPORTS/motion-blur/generique_motion-blur_' + str_largeur + 'x' + str_hauteur + '_' + digit(8, i) + '.png', output)
