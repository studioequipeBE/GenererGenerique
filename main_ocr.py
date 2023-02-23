import cv2 as cv2
import pytesseract
from pytesseract import Output

# Il faut bien mettre le nom du fichier sinon on a une erreur d'accès.
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Ratio du film et donc ce qu'il faut analyser.
ratio = '2.39'
# Toutes les combien d'images ont regarde le texte.
x = 150
# Compteur.
i = 0

cap = cv2.VideoCapture('C:\\TMP\\Generique_NB_1080p_24fps.mov')

if not cap.isOpened():
    exit('Erreur ouverture fichier.')

# On a configuré ici pour le français (on a importé les fichiers).
custom_config = r'--oem 3 -l fra --psm 6'

f = open('C:\\TMP\\Generique_NB_1080p_24fps_textes.txt', 'a')
# f_d = open('C:\\TMP\\Generique_NB_1080p_24fps_data.json', 'a')

texte_en_ligne = []
# param_par_ligne = []


# Supprime vide dans le texte :
def surpression_vide(dictionnaire):
    index_suprime = []

    taille = len(dictionnaire['text'])

    # On doit faire à l’envers sinon problème d'indexe :
    for i in reversed(range(0, taille)):
        if dictionnaire['text'][i] == '':
            dictionnaire['text'].pop(i)
            index_suprime.append(i)

    # Supprime les champs vides :
    for i in index_suprime:
        dictionnaire['level'].pop(i)
        dictionnaire['page_num'].pop(i)
        dictionnaire['par_num'].pop(i)
        dictionnaire['top'].pop(i)
        dictionnaire['height'].pop(i)
        dictionnaire['conf'].pop(i)

        # Ce qui nous intéresse :
        dictionnaire['block_num'].pop(i)
        dictionnaire['line_num'].pop(i)
        dictionnaire['word_num'].pop(i)
        dictionnaire['left'].pop(i)
        dictionnaire['width'].pop(i)

    return dictionnaire


# Récupère les données triées par ligne :
def par_ligne(dictionnaire):
    lignes_param = {}

    # Parcoure tout le dictionnaire (valeur et non clef) :
    for j in range(len(dictionnaire['text'])):

        # On vérifie que le numéro de ligne n'est pas déjà dans le dictionnaire.
        if str(dictionnaire['par_num'][j]) + '-' + str(dictionnaire['line_num'][j]) not in lignes_param:
            # print(str(dictionnaire['line_num'][i]) + ' not in ' + str(lignes_param))
            # S'il n'y est pas, on l'ajoute avec la valeur qu'on a.
            lignes_param[str(dictionnaire['par_num'][j]) + '-' + str(dictionnaire['line_num'][j])] = [
                {
                    'block_num': dictionnaire['block_num'][j],
                    'word_num': dictionnaire['word_num'][j],
                    'left': dictionnaire['left'][j],
                    'width': dictionnaire['width'][j],
                    'text': dictionnaire['text'][j]
                }
            ]

        # Sinon, elle existe déjà, et on ajoute à la ligne la valeur qu'on a :
        else:
            # print('La ligne (' + str(dictionnaire['line_num'][i]) + ') existe !')
            # index = lignes_param.index(dictionnaire['line_num'][i])
            lignes_param[str(dictionnaire['par_num'][j]) + '-' + str(dictionnaire['line_num'][j])].append(
                {
                    'block_num': dictionnaire['block_num'][j],
                    'word_num': dictionnaire['word_num'][j],
                    'left': dictionnaire['left'][j],
                    'width': dictionnaire['width'][j],
                    'text': dictionnaire['text'][j]
                }
            )

    # Tri des clefs si elles ne le sont pas.
    sorted_keys = sorted(lignes_param.keys())
    lignes_param = {key: lignes_param[key] for key in sorted_keys}

    return lignes_param


while cap.isOpened():

    ret, img = cap.read()

    # Traitement :
    # Prendre rectangle image utile (2.39 par exemple).

    # Traiter 1 image sur X.

    # print('ret : ' + str(ret))
    # print('frame : ' + str(frame))

    if (i % x) == 1 and ret:
        texte = pytesseract.image_to_string(img, config=custom_config)

        # Récupère les paramètres (attention qu'une correction est fait entre ces données brutes et le "image_to_string".
        # d = pytesseract.image_to_data(img, output_type=Output.DICT)
        # print('1 : ' + str(d))

        # d = surpression_vide(d)
        # d = par_ligne(d)

        # print('data : ' + str(texte))

        xml = pytesseract.image_to_alto_xml(img)
        print('xml : ' + str(xml))

        try:
            osd = pytesseract.image_to_osd(img)
            print('osd : ' + str(osd))
        except:
            print('OSD non utilisable.')

        lignes = texte.splitlines()

        # print('lignes : ' + str(lignes))




        if len(lignes) > 2:
            # print('lignes 2 : ' + str(lignes[0]))
            try:
                index_01 = texte_en_ligne.index(lignes[0])
                index_02 = texte_en_ligne.index(lignes[1])

                # print('index_01 : ' + str(index_01))
                # print('index_02 : ' + str(index_02))

                if index_01 > 0 and index_02 > 0 and (index_01 == index_02 - 1):
                    texte_en_ligne = texte_en_ligne[0:index_01]
                    param_par_ligne = param_par_ligne[0:index_01]

                texte_en_ligne.extend(lignes)

                # On ajoute chaque ligne.
                # for clef in d:
                #     param_par_ligne.append(d[clef])

            except:
                # print('Pas trouvé : ' + str(len(texte_en_ligne)))
                texte_en_ligne.extend(lignes)

                # On ajoute chaque ligne.
                # for clef in d:
                #     param_par_ligne.append(d[clef])
        else:
            texte_en_ligne.extend(lignes)

            # On ajoute chaque ligne.
            # for clef in d:
            #     param_par_ligne.append(d[clef])

        # d = pytesseract.image_to_data(img, output_type=Output.DICT)
        # keys = list(d.keys())
        # f_d.write(str(d) + '\n')

        # print(str(keys))
        # print(str(d['text']))
        # print(str(d['block_num']))
        # print(str(d['line_num']))
        # print(str(d['word_num']))
        # print(str(d['left']))
        # print(str(d['top']))
        # print(str(d['width']))
        # print(str(d['height']))

    if not ret:
        break

    i = i + 1


j = 0
for ligne in texte_en_ligne:
    f.write(ligne + '\n')

    j = j + 1

cap.release()
f.close()
# f_d.close()
