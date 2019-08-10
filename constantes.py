# -*- coding:utf-8 -*

"""
    Fichier contenant toutes les constantes du jeu, comprenant
    entre autres: les images et textures, les possibles shaders,
    les variables de conversions bloc => couleur...
"""

import sfml as sf

# ----------------------------------------------------------------------------------------------------------------------
# CHARGEMENT DES IMAGES, TEXTURES ET SHADERS
# ----------------------------------------------------------------------------------------------------------------------

tileset_image = sf.Image.from_file("images/tileset.png")
joueur_image = sf.Image.from_file("images/joueur.png")
monstres_image = sf.Image.from_file("images/monstres.png")
pnjs_image = sf.Image.from_file("images/pnjs.png")
objets_image = sf.Image.from_file("images/objets.png")
meubles_image = sf.Image.from_file("images/meubles.png")
attaques_image = sf.Image.from_file("images/attaques.png")
projectiles_image = sf.Image.from_file("images/projectiles.png")
autres_image = sf.Image.from_file("images/autres.png")
INTERFACE_IMAGE = sf.Image.from_file("images/interface.png")

tileset_image.create_mask_from_color(sf.Color(255, 255, 255))
joueur_image.create_mask_from_color(sf.Color(255, 255, 255))
monstres_image.create_mask_from_color(sf.Color(255, 255, 255))
pnjs_image.create_mask_from_color(sf.Color(255, 255, 255))
objets_image.create_mask_from_color(sf.Color(255, 255, 255))
meubles_image.create_mask_from_color(sf.Color(255, 255, 255))
attaques_image.create_mask_from_color(sf.Color(255, 255, 255))
projectiles_image.create_mask_from_color(sf.Color(255, 255, 255))
autres_image.create_mask_from_color(sf.Color(255, 255, 255))
INTERFACE_IMAGE.create_mask_from_color(sf.Color(255, 255, 255))

TILESET = sf.Texture.from_image(tileset_image)
JOUEUR = sf.Texture.from_image(joueur_image)
MONSTRES = sf.Texture.from_image(monstres_image)
PNJS = sf.Texture.from_image(pnjs_image)
OBJETS = sf.Texture.from_image(objets_image)
MEUBLES = sf.Texture.from_image(meubles_image)
ATTAQUES = sf.Texture.from_image(attaques_image)
PROJECTILES = sf.Texture.from_image(projectiles_image)
AUTRES = sf.Texture.from_image(autres_image)
INTERFACE = sf.Texture.from_image(INTERFACE_IMAGE)
MAP = sf.Texture.from_file("images/map.png")
ERREURS = sf.Texture.from_file("images/erreurs.png")
LEVEL_MAP = sf.Image.from_file("images/level_map.png")
OBJETS_IMAGE = sf.Image.from_file("images/objets.png")
ASCII_MESSAGE = sf.Image.from_file("images/ascii_message.png")

SHADER_CAVERNE = sf.Shader.from_file(None, "shaders/shader_caverne.frag")
SHADER_MONTAGNE = sf.Shader.from_file(None, "shaders/shader_montagne.frag")

# ----------------------------------------------------------------------------------------------------------------------
# VARIABLES CONCERNANT LA GESTION DE LA MAP
# ----------------------------------------------------------------------------------------------------------------------

# Taille en pixel des textures d'une map, dépend de la carte graphique de l'utilisateur, doit être multiple de 64
TEXTURE_MAX = (sf.Texture.get_maximum_size()//2)-((sf.Texture.get_maximum_size()//2) % 64)

# Taille d'un bloc en pixels
BLOCSIZE = 64

# Dictionnaire qui associe à chaque couleur le type de bloc correspondant
COULEUR_BLOC = {"255,255,255": 0, "0,0,0": 1, "1,1,1": 2, "2,2,2": 3, "3,3,3": 4, "4,4,4": 5, "5,5,5": 6,
                "6,6,6": 7, "7,7,7": 8, "8,8,8": 9, "9,9,9": 10, "10,10,10": 11, "11,11,11": 12, "12,12,12": 13,
                "13,13,13": 14, "14,14,14": 15, "15,15,15": 16, "16,16,16": 17, "17,17,17": 18, "18,18,18": 19,
                "19,19,19": 20, "20,20,20": 21, "21,21,21": 22, "22,22,22": 23, "23,23,23": 24, "24,24,24": 25,
                "25,25,25": 26, "26,26,26": 27, "27,27,27": 28, "28,28,28": 29, "29,29,29": 30, "30,30,30": 31,
                "31,31,31": 32, "32,32,32": 33, "33,33,33": 34, "34,34,34": 35, "35,35,35": 36, "50,50,50": 37,
                "51,51,51": 39, "52,52,52": 40, "53,53,53": 41, "54,54,54": 42, "254,254,254": 43, "55,55,55": 44,
                "56,56,56": 45, "57,57,57": 46, "58,58,58": 47, "59,59,59": 48, "60,60,60": 49, "61,61,61": 50,
                "62,62,62": 51, "63,63,63": 52, "64,64,64": 53, "65,65,65": 54, "66,66,66": 55, "67,67,67": 56,
                "36,36,36": 61, "37,37,37": 62, "38,38,38": 63, "39,39,39": 64, "40,40,40": 65, "41,41,41": 66,
                "42,42,42": 67, "43,43,43": 68, "44,44,44": 69, "45,45,45": 70, "46,46,46": 71, "47,47,47": 72,
                "48,48,48": 73, "49,49,49": 74, "70,70,70": 75, "71,71,71": 76, "72,72,72": 77, "73,73,73": 78,
                "74,74,74": 79, "75,75,75": 80, "76,76,76": 81, "77,77,77": 82, "78,78,78": 83, "79,79,79": 84,
                "80,80,80": 85, "81,81,81": 86, "82,82,82": 87, "83,83,83": 88, "84,84,84": 89, "85,85,85": 90,
                "86,86,86": 91, "87,87,87": 92, "88,88,88": 93, "89,89,89": 94, "90,90,90": 95, "91,91,91": 96,
                "92,92,92": 97, "93,93,93": 98, "94,94,94": 99, "95,95,95": 100, "96,96,96": 101, "97,97,97": 102,
                "98,98,98": 103, "99,99,99": 104, "100,100,100": 105, "101,101,101": 106, "102,102,102": 107,
                "103,103,103": 108, "104,104,104": 109, "105,105,105": 110, "106,106,106": 111, "107,107,107": 112,
                "253,253,253": 113, "108,108,108": 114, "109,109,109": 115, "110,110,110": 116, "111,111,111": 117,
                "112,112,112": 118, "113,113,113": 119, "114,114,114": 120, "115,115,115": 121, "116,116,116": 122,
                "117,117,117": 123, "118,118,118": 124, "119,119,119": 125, "120,120,120": 126, "121,121,121": 127,
                "122,122,122": 128, "123,123,123": 129, "124,124,124": 130, "125,125,125": 131, "126,126,126": 132,
                "127,127,127": 133, "128,128,128": 134, "252,252,252": 135, "129,129,129": 136, "130,130,130": 137,
                "131,131,131": 138, "132,132,132": 139, "133,133,133": 140, "134,134,134": 141, "135,135,135": 142,
                "136,136,136": 143, "137,137,137": 144, "138,138,138": 145, "139,139,139": 146, "140,140,140": 147,
                "141,141,141": 148, "142,142,142": 149, "143,143,143": 150, "144,144,144": 151, "145,145,145": 152,
                "146,146,146": 153, "147,147,147": 154, "148,148,148": 155, "149,149,149": 156, "150,150,150": 157,
                "151,151,151": 158, "152,152,152": 159, "153,153,153": 160, "154,154,154": 161, "155,155,155": 162,
                "156,156,156": 163, "157,157,157": 164, "158,158,158": 165, "159,159,159": 166, "160,160,160": 167,
                "161,161,161": 168, "162,162,162": 169, "163,163,163": 170, "164,164,164": 171, "165,165,165": 172,
                "166,166,166": 173, "167,167,167": 174, "168,168,168": 175, "169,169,169": 176, "170,170,170": 177,
                "251,251,251": 186, "171,171,171": 187, "172,172,172": 188, "173,173,173": 189, "174,174,174": 190,
                "175,175,175": 191, "176,176,176": 192, "177,177,177": 193, "178,178,178": 194, "179,179,179": 199,
                "180,180,180": 200, "181,181,181": 201, "182,182,182": 202, "183,183,183": 203, "184,184,184": 204,
                "185,185,185": 205, "186,186,186": 206, "187,187,187": 207, "188,188,188": 208, "189,189,189": 209,
                "190,190,190": 210, "191,191,191": 211, "192,192,192": 212, "193,193,193": 213, "194,194,194": 214,
                "195,195,195": 215, "196,196,196": 216, "197,197,197": 217, "198,198,198": 218, "199,199,199": 219,
                "200,200,200": 220, "201,201,201": 221, "202,202,202": 222, "203,203,203": 223, "204,204,204": 224,
                "205,205,205": 225, "206,206,206": 226, "207,207,207": 227}

# Liste définissant si un bloc est traversable ou non par le joueur, les monstres, les attaques...
TRAVERSABLE = [True, False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, True, True, True, True, True,
               True, True, True, True, True, True, True, False, True, False,
               False, False, False, True, False, False, False, False, False, False,
               False, False, False, False, False, False, False, True, True, True,
               True, False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, True, True, True, True, True,
               True, True, True, True, True, True, True, True, True, True,
               True, True, True, True, False, False, False, False, False, False,
               True, True, True, True, True, True, True, True, True, True,
               True, True, True, True, True, True, True, False, False, False,
               True, True, False, False, False, False, False, False, False, False,
               False, False, False, False, False, True, False, False, False, False,
               False, False, False, False, False, False, False, False, True, True,
               True, True, True, True, True, True, True, True, True, True,
               True, True, True, True, True, True, True, True, True, True,
               True, True, False, False, False, False, False, False, True, True,
               True, True, True, True, True, True, True, False, False, False,
               False, False, False, False, False, True, True, True, True, False,
               False, False, False, True, True, True, True, True, True, True,
               True, False, False, False, False, False, False, False, False, False,
               False, False, False, False, False, False, False, False]

INFO_MAP = {"main-0": {"coin": (1052.5, 2511.5), "ajustable": True},
            "main-1": {"coin": (706.0, 2381.0), "ajustable": True},
            "main-2": {"coin": (1083.5, 1908.5), "ajustable": True},
            "main-3": {"coin": (1083.5, 972.5), "ajustable": True},

            "maison-0-0": {"coin": (1915.0, 2822.0), "ajustable": False},
            "maison-0-1": {"coin": (1859.0, 2661.0), "ajustable": False},
            "maison-1-0": {"coin": (849.0, 2489.0), "ajustable": False},
            "maison-1-1": {"coin": (789.0, 2550.0), "ajustable": False},
            "maison-1-2": {"coin": (736.0, 2557.0), "ajustable": False},
            "maison-1-3": {"coin": (738.0, 2435.0), "ajustable": False},
            "maison-1-4": {"coin": (937.0, 2510.0), "ajustable": False},
            "maison-1-5": {"coin": (792.0, 2510.0), "ajustable": False},
            "maison-1-6": {"coin": (995.0, 2582.0), "ajustable": False},
            "maison-1-7": {"coin": (944.0, 2550.0), "ajustable": False},
            "maison-1-8": {"coin": (944.0, 2409.0), "ajustable": False},
            "maison-2-0": {"coin": (1324.0, 2219.0), "ajustable": False},
            "maison-2-1": {"coin": (1856.0, 2216.0), "ajustable": False},
            "maison-2-2-0": {"coin": (1908.0, 1971.0), "ajustable": False},
            "maison-2-2-1": {"coin": (1908.0, 1971.0), "ajustable": False},
            "maison-2-2-2": {"coin": (1908.0, 1971.0), "ajustable": False},
            "maison-3-0": {"coin": (1469.0, 1432.0), "ajustable": False},
            "maison-3-1": {"coin": (953.0, 539.0), "ajustable": False},

            "caverne-2-0-0": {"coin": (1863.0, 2022.0), "ajustable": False},
            "caverne-2-0-1": {"coin": (1863.0, 2022.0), "ajustable": False},
            "caverne-2-1": {"coin": (1246.0, 2197.0), "ajustable": False},
            "caverne-2-2-0": {"coin": (1130.0, 1896.0), "ajustable": False},
            "caverne-2-2-1": {"coin": (1130.0, 1896.0), "ajustable": False},
            "caverne-3-0": {"coin": (1298.0, 988.0), "ajustable": False},
            "caverne-3-1-0": {"coin": (1298.0, 988.0), "ajustable": False},
            "caverne-3-1-1": {"coin": (1298.0, 988.0), "ajustable": False},
            "caverne-3-2-0": {"coin": (1387.0, 1277.0), "ajustable": False},
            "caverne-3-2-1": {"coin": (1387.0, 1277.0), "ajustable": False},
            "caverne-3-2-2": {"coin": (1387.0, 1277.0), "ajustable": False},
            "caverne-3-2-3": {"coin": (1387.0, 1277.0), "ajustable": False},
            "caverne-3-2-4": {"coin": (1387.0, 1277.0), "ajustable": False},
            "caverne-3-2-5": {"coin": (1387.0, 1277.0), "ajustable": False},
            "caverne-3-2-6": {"coin": (1387.0, 1277.0), "ajustable": False},
            "caverne-3-2-7": {"coin": (1387.0, 1277.0), "ajustable": False},
            "caverne-3-2-8": {"coin": (1387.0, 1277.0), "ajustable": False},
            "caverne-3-2-9": {"coin": (1387.0, 1277.0), "ajustable": False},

            "antre-1-0": {"coin": (738.0, 2435.0), "ajustable": False},
            "antre-3-0-0": {"coin": (1298.0, 988.0), "ajustable": False},
            "antre-3-0-1": {"coin": (1298.0, 988.0), "ajustable": False},

            "val-3-0": {"coin": (903.0, 517.0), "ajustable": True},
            "val-3-1": {"coin": (903.0, 517.0), "ajustable": True},

            "col-1-0": {"coin": (966.0, 2376.0), "ajustable": False}}

# ----------------------------------------------------------------------------------------------------------------------
# VARIABLES CONCERNANT LA GESTION DES MONSTRES, DES PNJS, DU JOUEUR ET DES ATTAQUES
# ----------------------------------------------------------------------------------------------------------------------

# Liste qui contient pour chaque type de monstre un dictionnaire indiquant les caractéristiques de ce type
CARAC_MONSTRES = [{"attaque": 2, "vitesse": 1, "vitesse_attaque": 60},
                  {"attaque": 2, "vitesse": 1, "vitesse_attaque": 90},
                  {"attaque": None, "vitesse": 0, "vitesse_attaque": 120},
                  {"attaque": None, "vitesse": 0, "vitesse_attaque": 90}]

# Variable universelle indiquant la vitesse de la mort d'un monstre, d'un PNJ, ou du joueur en frames
VITESSE_MORT = 60

# Variable indiquant la liste des directions que peut prendre une entité mobile
DIRECTIONS = ["bas", "haut", "droite", "gauche"]

# Variable indiquant la liste des actions que peuvent effectuer les monstres et PNJS
ACTIONS = ["arret", "course0", "course1", "course2", "course3", "attaque0", "attaque1", "attaque2", "mort0", "mort1",
           "mort2", "mort3"]

# Variable indiquant la liste des actions que peut effectuer le joueur
ACTIONS_JOUEUR = ["arret", "course0", "course1", "course2", "course3", "attaque0", "attaque1", "attaque2", "clavier0",
                  "clavier1", "clavier2", "mort0", "mort1", "mort2", "mort3"]

# Liste contenant les vitesses de tout les types de PNJ du jeu
VITESSES_PNJS = [1, 1, 1, 2, 2]

# Liste indiquant pour chaque type d'attaque: [degats, vitesse]
CARAC_ATTAQUES = [[1, 8], [1, 8], [1, 0], [1, 0], [1, 0]]

# Variable indiquant si une attaque n'est qu'un simple projectile et qu'elle n'a donc pas d'effets particuliers
ATTAQUES_PROJECTILES = [0, 1]

# Variable qui détermine si une attaque touche le joueur: les attaques touchent les monstres dans tout les cas
ATTAQUES_HOSTILES = [0, 3]

# Liste des sprites d'un projectile
ACTIONS_PROJECTILES = ["avance0", "avance1", "avance2", "avance3", "detruit0", "detruit1", "detruit2", "detruit3"]

# ----------------------------------------------------------------------------------------------------------------------
# VARIABLES CONCERNANT LA GESTION DES OBJETS ET MEUBLES
# ----------------------------------------------------------------------------------------------------------------------

# Dictionnaire des caractéristiques améliorables pour le joueur de forme {attribut_joueur: nom_caracteristique}
LISTE_CARAC = {"armure": "armure",
               "vie_maximum": "vie",
               "vitesse": "vitesse",
               "vitesse_attaque": "vitesse d'attaque"}

# Liste qui associe a chaque type d'objet un dictionnaire contenant les données necessaires
CARAC_OBJETS = [{"nom": "Coeur"},

                {"nom": "Casque en cuir", "vitesse d'attaque": -1},
                {"nom": "Tunique", "vitesse d'attaque": -1},
                {"nom": "Pantalon", "vitesse d'attaque": -1},
                {"nom": "Bottes", "vitesse": 1},

                {"nom": "Potion de vie:\nVous rend toute votre vie\n- Consommable"},
                {"nom": "Parchemin d'attaque:\nEnvoie une boule d'énergie\n- Consommable",
                 "charges": 10},
                {"nom": "Parchemin d'attaque de feu:\nEmbrase votre clavier\nle temps d'une attaque\n"
                        "Utilisable à l'infini"},

                {"nom": "Bonnet de montagnard", "vitesse d'attaque": -2},
                {"nom": "Veste chaude de montagnard", "vitesse d'attaque": -2, "vie": 2},
                {"nom": "Pantalon ample de montagnard", "vitesse d'attaque": -2, "vitesse": 1},
                {"nom": "Chaussures de marche de\nmontagnard", "vitesse d'attaque": -1, "vitesse": 1},

                {"nom": "Parchemin d'explosions\nProvoque des explosions\ntout autour de vous\n - Consommable",
                 "charges": 10},
                {"nom": "Cristal orange\nIl est magnifique !"}]

# Listes regroupant les types d'objets qui correspondent à des utilisations précises
LISTE_CASQUES = [1, 8]
LISTE_PLASTRONS = [2, 9]
LISTE_JAMBIERES = [3, 10]
LISTE_BOTTES = [4, 11]
LISTE_UTIL = [5, 6, 7, 12]

# Liste des objets qui vont dans l'inventaire lorsqu'on marche dessus
LISTE_RAMASSABLES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

# Liste des meubles qui ne font rien d'autre qu'afficher la description quand on intéragit avec
LISTE_MEUBLES_NORMAUX = [0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
