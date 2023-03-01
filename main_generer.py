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
from PIL import Image, ImageFont, ImageDraw

dossier_travail = 'C:\\TMP\\'


# Retourne un nombre sur un certain nombre de digits.
def digit(nombre_digit: int, valeur: int) -> str:
    texte = ''

    for compteur in range(0, (nombre_digit - len(str(valeur)))):
        texte = '0' + texte

    return (texte + str(valeur))


liste_font = []

# Récupère dans un CSV les fonts/polices qu'on peut utiliser :
with open(dossier_travail + 'font.csv', newline='', encoding='utf-8') as csvfile:
    contenu = csv.reader(csvfile, delimiter=';', quotechar='|')

    i = 0
    for ligne in contenu:
        if i != 0:
            print(ligne[0])

            # Il peut y avoir des lignes vides par erreur.
            if ligne[0] != '':
                liste_font.append({
                    'nom': ligne[0],
                    'normal': ligne[1],  # Ici ce sont les noms de fichier.
                    'gras': ligne[2],
                    'italique': ligne[3],
                    'italique-gras': ligne[4]
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
    canaux = couleur.split()
    return (int(canaux[0]), int(canaux[1]), int(canaux[2]), int(canaux[3]))


# Récupère dans un CSV les différents styles du projet :
with open(dossier_travail + 'style.csv', newline='', encoding='utf-8') as csvfile:
    contenu = csv.reader(csvfile, delimiter=';', quotechar='|')

    i = 0
    for ligne in contenu:
        if i != 0:

            # Il se peut qu'on mette des lignes vides (par erreur ou autre).
            if ligne[0] != '':

                font = findFontByName(ligne[1]) # Récupère toutes les possibilités.
                if ligne[4] == 'True' and ligne[5] == 'True':
                    font = font['italique-gras']
                elif ligne[5] == 'True':
                    font = font['italique']
                elif ligne[4] == 'True':
                    font = font['gras']
                else:
                    font = font['normal']

                liste_style.append({
                    'nom': ligne[0],
                    'font': font,
                    'souligner': True if ligne[6] == 'True' else False,
                    'taille': int(ligne[2]),
                    'couleur': decodeCouleur(ligne[3]),
                    'espace_gauche_droite': int(ligne[7]),
                    'espace_3colonnes': int(ligne[8]),
                    'espace_ligne': int(ligne[9])
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
fichier_csv = dossier_travail + 'generique.csv'


# Récupère dans un CSV les réglages du projet :
with open(dossier_travail + 'reglage.csv', newline='', encoding='utf-8') as csvfile:
    contenu = csv.reader(csvfile, delimiter=';', quotechar='|')

    i = 0
    for ligne in contenu:
        if i > 1:
            # Résoluton :
            largeur = int(ligne[0])
            hauteur = int(ligne[1])

            # Réglages :
            ratio = ligne[2]  # Ratio si on veut mettre un cache.
            vitesse = int(ligne[3])  # Vitesse de defilement.

            style_general = findStyleByName(ligne[4])

            print('Style général : ' + str(style_general))

            couleur_fond = decodeCouleur(ligne[5])  # Il faut une bonne raison pour que le fond ne soit pas noir.
            couleur_blanking = decodeCouleur(ligne[6])  # Couleur des blankings.

        i = i + 1

# Récupère dans un CSV les réglages d'exports (in, out -> pas résolution ???) du projet :
with open(dossier_travail + 'rendu.csv', newline='', encoding='utf-8') as csvfile:
    contenu = csv.reader(csvfile, delimiter=';', quotechar='|')

    i = 0
    for ligne in contenu:
        if i != 0:
            in_rendu = None if ligne[0] == 'None' else int(ligne[0])
            out_rendu = None if ligne[1] == 'None' else int(ligne[1])

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
    'y_fin': [],

    'commentaire': []
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
        'espace_gauche_droite': style_general['espace_gauche_droite'],
        'espace_3colonnes': style_general['espace_3colonnes'],
        'espace_ligne': style_general['espace_ligne']
    }

    # Si on a un style dans la colonne, on l'utilise :
    if style_colonne is not None:
        style['font'] = style_colonne['font']
        style['taille'] = style_colonne['taille']
        style['couleur'] = style_colonne['couleur']
        style['souligner'] = style_colonne['souligner']
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


# Récupère générique d'un CSV :
with open(fichier_csv, newline='', encoding='utf-8') as csvfile:
    contenu = csv.reader(csvfile, delimiter=';', quotechar='|')

    i = 0
    for ligne in contenu:
        if i != 0:

            # Si la colonne "style-ligne" a quelque chose, on le renseigne.
            style_ligne = None
            if ligne[18] != '':
                style_ligne = {
                    'espace_3colonnes': styleValeurChiffre(ligne[18], 'espace_3colonnes'),
                    'espace_ligne': styleValeurChiffre(ligne[18], 'espace_ligne')
                }

            generique['gauche-gauche'].append(ligne[0].rstrip())
            generique['style-gauche-gauche'].append(getStyle(style_general, findStyleByName(ligne[1]), style_ligne))
            generique['gauche-centre'].append(ligne[2].strip())
            generique['style-gauche-centre'].append(getStyle(style_general, findStyleByName(ligne[3]), style_ligne))
            generique['gauche-droite'].append(ligne[4].lstrip())
            generique['style-gauche-droite'].append(getStyle(style_general, findStyleByName(ligne[5]), style_ligne))

            generique['centre-gauche'].append(ligne[6].rstrip())
            generique['style-centre-gauche'].append(getStyle(style_general, findStyleByName(ligne[7]), style_ligne))

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

            generique['style-centre-centre'].append(getStyle(style_general, findStyleByName(ligne[9]), style_ligne))
            generique['centre-droite'].append(ligne[10].lstrip())
            generique['style-centre-droite'].append(getStyle(style_general, findStyleByName(ligne[11]), style_ligne))

            generique['droite-gauche'].append(ligne[12].rstrip())
            generique['style-droite-gauche'].append(getStyle(style_general, findStyleByName(ligne[13]), style_ligne))
            generique['droite-centre'].append(ligne[14].strip())
            generique['style-droite-centre'].append(getStyle(style_general, findStyleByName(ligne[15]), style_ligne))
            generique['droite-droite'].append(ligne[16].lstrip())
            generique['style-droite-droite'].append(getStyle(style_general, findStyleByName(ligne[17]), style_ligne))

            # hauteur_texte = hauteur + ((style_general['taille'] + style_general['espace_ligne']) * i)

            # generique['y_debut'].append()
            # generique['y_fin'].append()

            generique['style-ligne'].append(style_ligne)
            generique['commentaire'].append(ligne[19])

        i = i + 1

# TODO : on devrait, depuis le nombre de ligne du CSV calculer le nombre d'image nécessaire.
nb_image = (24 * 60 * 3) + 50


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

        # Souligne d'une ligne.
        draw.line((lx, xy[1], lx + twidth, xy[1]), fill=style['couleur'])

        # En UHD, on souligne 2x :
        if style['taille'] > 20:
            draw.line((lx, xy[1]+1, lx + twidth, xy[1]+1), fill=style['couleur'])


in_rendu = in_rendu if in_rendu is not None else 0
out_rendu = out_rendu if out_rendu is not None else nb_image

# On calcule une fois pour toute la position des colonnes.
colonne_gauche = int(largeur / 3)
colonne_centre = int(largeur / 2)
colonne_droite = int((largeur / 3) * 2)

image = None

for j in range(in_rendu, out_rendu):
    print('Image : ' + str(j) + '/' + str(out_rendu))

    # L'image PNG.
    # Pas de canal alpha en plus. couleur_fond
    image = Image.new(mode='RGBA', size=(largeur, hauteur*16), color=couleur_fond)

    # create new image
    draw = ImageDraw.Draw(image)
    draw.fontmode = 'l'  # Anti-aliasing. TODO : je ne sais pas s'il fonctionne...

    for i in range(0, len(generique['centre-centre'])):
        # Pour anchor : https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html

        hauteur_texte = hauteur + ((style_general['taille'] + style_general['espace_ligne']) * i) - (j * (vitesse * 2))

        # Gauche :
        if generique['gauche-gauche'][i] != '':
            drawText(
                draw=draw,
                xy=(
                    colonne_gauche - generique['style-gauche-gauche'][i]['espace_gauche_droite'] - generique['style-gauche-gauche'][i]['espace_3colonnes'],
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
                    colonne_gauche - generique['style-gauche-centre'][i]['espace_3colonnes'],
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
                    colonne_gauche + generique['style-gauche-droite'][i]['espace_gauche_droite'] - generique['style-gauche-droite'][i]['espace_3colonnes'],
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
                    colonne_centre - generique['style-centre-gauche'][i]['espace_gauche_droite'],
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
                    colonne_centre,
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
                    colonne_centre + generique['style-centre-droite'][i]['espace_gauche_droite'],
                    hauteur_texte
                ),
                texte=generique['centre-droite'][i],
                style=generique['style-centre-droite'][i],
                anchor='ls'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la gauche.
            )

        # S'il y a une image, on l'ajoute.
        if generique['image-centre-centre'][i] is not None:
            image_ajouter = Image.open(dossier_travail + 'image_a_ajouter\\' + generique['image-centre-centre'][i])
            # Le mask est obligatoire pour une image alpha car sinon cela "ajoute l'alpha" à l'image (remplace le fond par un truc transparent).
            # Du coup avec le masque, on code que les pixels qui change.
            image.paste(image_ajouter, (int(colonne_centre - (image_ajouter.width/2)), hauteur_texte), mask=image_ajouter)

        # Droite :
        if generique['droite-gauche'][i] != '':
            drawText(
                draw=draw,
                xy=(
                    colonne_droite - generique['style-droite-gauche'][i]['espace_gauche_droite'] + generique['style-droite-gauche'][i]['espace_3colonnes'],
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
                    colonne_droite + generique['style-droite-centre'][i]['espace_3colonnes'],
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
                    colonne_droite + generique['style-droite-droite'][i]['espace_gauche_droite'] + generique['style-droite-droite'][i]['espace_3colonnes'],
                    hauteur_texte
                ),
                texte=generique['droite-droite'][i],
                style=generique['style-droite-droite'][i],
                anchor='ls'  # Dire qu'on est basé sur la "baseline" et d'aligner sur la gauche.
            )

    # L'output blanking :
    if crop != 0:
        draw.rectangle(((0, 0), (largeur, crop)), fill=couleur_blanking)
        draw.rectangle(((0, hauteur), (largeur, hauteur - crop)), fill=couleur_blanking)

    # Après création de l'image, on sauve.
    image.save('C:\\TMP\\png\\generique_' + str(largeur) + 'x' + str(hauteur) + '_' + digit(8, j) + '.png')

    # exif_ifd = {piexif.ExifIFD.UserComment: 'my message'}
    # exif_dict = {"0th": {}, "Exif": exif_ifd, "1st": {}, "thumbnail": None, "GPS": {}}
    # exif_dat = piexif.dump(exif_dict)
    # image.save('C:\\TMP\\png\\generique_' + str(largeur) + 'x' + str(hauteur) + '_' + digit(8, j) + '.tif', compression='tiff_lzw', exif=exif_dat)


# Ici, on sait que l'image est générée
for i in range(0, nb_image):
    print('Ici ?')
    sequence = image.crop((0, i * (vitesse * 2), largeur, i * (vitesse * 2) + hauteur))
    sequence.save('C:\\TMP\\png\\autre\\generique_' + str(largeur) + 'x' + str(hauteur) + '_' + digit(8, i) + '.png')
