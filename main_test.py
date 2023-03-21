# Calcule le crop (taille) qu'il faut pour les blankings.
def getCrop(largeur: int, hauteur: int, ratio: float) -> (bool, int):
    letterbox = None
    crop = 0

    # Cas de blanking pilarbox.
    if ratio > 1.77:
        letterbox = True
        image_utile = largeur / ratio

        virgule = image_utile % 1
        paire = (image_utile - virgule) % 2

        # Si le nombre est pair, aucun souci et on continue.
        if paire == 0:
            image_utile = int(image_utile)
        # Si le nombre est impair, on a un souci...
        else:
            image_utile = image_utile - virgule + 1

        crop = (hauteur - image_utile) / 2

    elif ratio == 1.77:
        return (True, 0)
    # Cas de blanking letterbox.
    else:
        letterbox = False
        image_utile = hauteur * ratio
        print('image utile : ' + str(image_utile))
        image_utile = int(image_utile)
        crop = (largeur - image_utile) / 2

    return (letterbox, int(crop))


print('HD :')
print('Ratio 2.40 : ' + str(getCrop(1920, 1080, 2.40)))
print('Ratio 2.39 : ' + str(getCrop(1920, 1080, 2.39)))
print('Ratio 2.10 : ' + str(getCrop(1920, 1080, 2.1)))
print('Ratio 2.00 : ' + str(getCrop(1920, 1080, 2)))
print('Ratio 1.85 : ' + str(getCrop(1920, 1080, 1.85)))
print('Ratio 1.77 : ' + str(getCrop(1920, 1080, 1.77)))
print('Ratio 1.66 : ' + str(getCrop(1920, 1080, 1.666666666)))
print('Ratio 1.33 : ' + str(getCrop(1920, 1080, 1.333333333)))

print('')

print('UHD :')
print('Ratio 2.40 : ' + str(getCrop(3840, 2160, 2.40)))
print('Ratio 2.39 : ' + str(getCrop(3840, 2160, 2.39)))
print('Ratio 2.10 : ' + str(getCrop(3840, 2160, 2.1)))
print('Ratio 2.00 : ' + str(getCrop(3840, 2160, 2)))
print('Ratio 1.85 : ' + str(getCrop(3840, 2160, 1.85)))
print('Ratio 1.77 : ' + str(getCrop(3840, 2160, 1.77)))
print('Ratio 1.66 : ' + str(getCrop(3840, 2160, 1.666666666)))
print('Ratio 1.33 : ' + str(getCrop(3840, 2160, 1.333333333)))
