# -*- coding:utf-8 -*

"""
    Fichier contenant toutes les classes et fonctions
    nécessaires à la manipulation d'une map.
"""

from entites_mobiles import *
from numpy import ndarray, uint16
from random import randrange


class Carte:
    """
        Classe regroupant toutes les variables et toutes les fonctions
        propres à une map, ainsi que tout ce qui doit être affiché sur
        la map et qui n'est pas un menu: joueur, interface, monstres, PNJ...
    """

    def __init__(self):
        """
            self.taille: [Largeur de la carte, Hauteur de la carte].
            self.blocs: Liste à deux dimensions contenant dans le type de
            chaque bloc.
            self.carte_bool: Liste à deux dimensions servant de carte pour les
            collisions, True signifie que le bloc est traversable.
            self.textures: Liste à deux dimensions contenant les textures à
            dessiner à l'ecran.
            self.carte_texture: Image dans laquelle la valeur de la couleur des
            pixels est le type de bloc (utilisé pour les shaders)

            self.monstres: Liste de tout les monstres présents sur la map.
            self.pnjs: Liste de tout les pnjs présents sur la map.
            self.objets: Liste de tout les objets présents sur la map.
            self.meubles: Liste des meubles présents sur la map.
            self.places: Liste des places présentes sur la map. Les places sont
            des entites invisibles qui servent à déclencher des quêtes lorsque
            le joueur marche dessus.
            self.attaques: Liste des attaques présentes sur la map.

            self.blocs_importants: Dictionnaire regroupant les emplacements
            et données de blocs particuliers que l'on doit souvent rechercher
            sans avoir à parcourir tout les blocs de la map.
            self.message: Données d'une boîte de dialogue qui s'affiche à
            l'écran.

            self.decalage: Position de l'ecran, en pixels, par rapport à la
            carte.
            self.liste_rafraichir: Pour afficher quelque chose à l'écran, une
            entité doit être ajoutée à cette liste avec son plan (voir le dossier types/plans).
            self.tempo: Variable qui sert d'horloge interne et qui revient à 0
            toute les 60 frames.
        """

        self.taille = list()
        self.blocs = ndarray(list(), uint16)
        self.carte_bool = ndarray(list(), bool)
        self.textures = ndarray(list(), sf.RenderTexture)
        self.carte_texture = sf.Image.create(0, 0)

        self.monstres = list()
        self.pnjs = list()
        self.objets = list()
        self.meubles = list()
        self.places = list()
        self.attaques = list()

        self.blocs_importants = {"portes": list()}
        self.message = {"texture": sf.Texture.create(1, 1), "afficher": False, "x": 0, "y": 0}

        self.decalage = [0, 0]
        self.liste_rafraichir = list()
        self.tempo = 0

    # ------------------------------------------------------------------------------------------------------------------
    # GERER LA MAP, L'INTERFACE ET L'AFFICHAGE
    # ------------------------------------------------------------------------------------------------------------------

    def charger(self, id_carte):
        """
            Fonction qui à partir d'une ID charge les fichiers correspondants à
            la map puis en extrait toutes les données nécessaires.
            Une fois toutes ces données obtenues, la fonction modifie self.textures
            pour y dessiner des textures de taille propre à la carte graphique
            de l'utilisateur.
        """

        plan_carte = sf.Image.from_file("maps/"+id_carte+".png")
        self.taille = [plan_carte.width, plan_carte.height]

        # OBTENTION DES DONNEES DE CHAQUE BLOC

        self.carte_texture = sf.Image.create(self.taille[0], self.taille[1])
        self.blocs.resize(self.taille)
        self.carte_bool.resize(self.taille)
        for x in range(self.taille[0]):
            for y in range(self.taille[1]):

                chaine_couleur = str(plan_carte[x, y].r)+","+str(plan_carte[x, y].g)+","+str(plan_carte[x, y].b)

                # Si c'est un bloc normal
                if chaine_couleur in COULEUR_BLOC.keys():
                    self.blocs[x, y] = COULEUR_BLOC[chaine_couleur]
                    self.carte_bool[x, y] = TRAVERSABLE[self.blocs[x, y]]

                # Si c'est un bloc spécial
                else:

                    # Si c'est un monstre
                    if plan_carte[x, y].r == 255:
                        monstre = Monstre(plan_carte[x, y].b)
                        monstre.coord["x"], monstre.coord["y"] = x*BLOCSIZE, y*BLOCSIZE
                        self.monstres.append(monstre)

                        self.blocs[x, y] = plan_carte[x, y].g
                        self.carte_bool[x, y] = False

                    # Si c'est une porte
                    elif plan_carte[x, y].g == 255:
                        self.blocs[x, y] = plan_carte[x, y].r
                        self.blocs_importants["portes"].append({"ID": plan_carte[x, y].b, "x": x, "y": y})
                        self.carte_bool[x, y] = TRAVERSABLE[self.blocs[x, y]]

                    # Si c'est un PNJ
                    elif plan_carte[x, y].b == 255:
                        pnj = Pnj(plan_carte[x, y].g)
                        pnj.coord["x"], pnj.coord["y"] = x*BLOCSIZE, y*BLOCSIZE
                        self.pnjs.append(pnj)

                        self.blocs[x, y] = plan_carte[x, y].r
                        self.carte_bool[x, y] = False

                    # Si c'est un objet
                    elif plan_carte[x, y].r == 254:
                        objet = Objet(plan_carte[x, y].b)
                        objet.coord["x"], objet.coord["y"] = x*BLOCSIZE, y*BLOCSIZE
                        self.objets.append(objet)

                        self.blocs[x, y] = plan_carte[x, y].g
                        self.carte_bool[x, y] = TRAVERSABLE[self.blocs[x, y]]

                    # Si c'est un meuble
                    elif plan_carte[x, y].g == 254:
                        meuble = Meuble(plan_carte[x, y].b)
                        meuble.coord["x"], meuble.coord["y"] = x*BLOCSIZE, y*BLOCSIZE
                        self.meubles.append(meuble)

                        self.blocs[x, y] = plan_carte[x, y].r
                        self.carte_bool[x, y] = False

        for x in range(self.taille[0]):
            for y in range(self.taille[1]):
                self.carte_texture[x, y] = sf.Color(self.blocs[x, y], self.blocs[x, y], self.blocs[x, y])
        self.carte_texture = sf.Texture.from_image(self.carte_texture)

        # DESSINER LES BLOCS SUR DES RENDERTEXTURES SFML

        self.dessiner_blocs_textures()

        # CHARGER LES ENTITES DE QUETES

        entites_quetes = ElementTree.parse("maps/entites_quetes/"+id_carte+".xml")

        # Monstres
        for monstre_xml in entites_quetes.find("monstres"):
            monstre = Monstre(int(monstre_xml.get("type")))
            monstre.coord["x"], monstre.coord["y"] = int(monstre_xml.attrib["x"]), int(monstre_xml.attrib["y"])
            for quete in monstre_xml.findall("quete"):
                monstre.quetes.append({"histoire": int(quete.get("histoire")), "quete": int(quete.get("quete"))})
            self.carte_bool[monstre.coord["x"]//64, monstre.coord["y"]//64] = False
            self.monstres.append(monstre)

        # PNJS
        for pnj_xml in entites_quetes.find("pnjs"):
            pnj = Pnj(int(pnj_xml.get("type")))
            pnj.coord["x"], pnj.coord["y"] = int(pnj_xml.get("x")), int(pnj_xml.get("y"))
            for quete in pnj_xml.findall("quete"):
                pnj.quetes.append({"histoire": int(quete.get("histoire")), "quete": int(quete.get("quete"))})
            self.carte_bool[pnj.coord["x"]//64, pnj.coord["y"]//64] = False
            self.pnjs.append(pnj)

        # Meubles
        for meuble_xml in entites_quetes.find("meubles"):
            meuble = Meuble(int(meuble_xml.get("type")))
            meuble.coord["x"], meuble.coord["y"] = int(meuble_xml.get("x")), int(meuble_xml.get("y"))
            for quete in meuble_xml.findall("quete"):
                meuble.quetes.append({"histoire": int(quete.get("histoire")), "quete": int(quete.get("quete"))})
            self.carte_bool[meuble.coord["x"]//64, meuble.coord["y"]//64] = False
            self.meubles.append(meuble)

        # Places
        for place_xml in entites_quetes.find("places"):
            place = Entite(int(place_xml.get("x")), int(place_xml.get("y")),
                           int(place_xml.get("w")), int(place_xml.get("h")))
            for quete in place_xml.findall("quete"):
                place.quetes.append({"histoire": int(quete.get("histoire")), "quete": int(quete.get("quete"))})
            self.places.append(place)

    def dessiner_blocs_textures(self):
        """
            Fonction qui dessine tout les blocs de la map sur des sf.RenderTexture
            pour pouvoir les afficher après sur l'ecran.
        """

        # Créer les textures
        self.textures.resize([(self.taille[0]*BLOCSIZE)//TEXTURE_MAX+1, (self.taille[1]*BLOCSIZE)//TEXTURE_MAX+1])
        for x, colonne in enumerate(self.textures):
            for y, texture in enumerate(colonne):
                self.textures[x, y] = sf.RenderTexture(TEXTURE_MAX, TEXTURE_MAX)

        # Dessiner les blocs
        for x in range(self.taille[0]):
            for y in range(self.taille[1]):
                fenetre_sprite = ((self.blocs[x, y] % 10)*BLOCSIZE, (self.blocs[x, y]//10)*BLOCSIZE, BLOCSIZE, BLOCSIZE)
                sprite = sf.Sprite(TILESET, fenetre_sprite)
                sprite.position = ((x*BLOCSIZE) % TEXTURE_MAX, (y*BLOCSIZE) % TEXTURE_MAX)
                self.textures[(x*BLOCSIZE)//TEXTURE_MAX, (y*BLOCSIZE)//TEXTURE_MAX].draw(sprite)

        # Mettre à jour les textures
        for colonne in self.textures:
            for texture in colonne:
                texture.display()

    def afficher(self, window, resolution, joueur, spawn):
        """
            Fonction qui dessine le fond de la carte et toutes les entités qui
            sont dans self.liste_rafraichir en respectant les plans.
        """

        shader_en_cours = None
        if spawn["ID-map"].split("-")[0] == "caverne":
            shader_en_cours = SHADER_CAVERNE
            self.parametrer_shader_caverne(joueur, resolution)
        elif spawn["ID-map"] == "main-2":
            shader_en_cours = SHADER_MONTAGNE
            self.parametrer_shader_montagne(joueur, resolution)

        # Effacer l'ecran

        window.clear(sf.Color(0, 0, 0))

        # Afficher le fond

        for x, colonne in enumerate(self.textures):
            for y, texture in enumerate(colonne):
                if self.decalage[0]-TEXTURE_MAX < x*TEXTURE_MAX < self.decalage[0]+resolution["w"] and \
                   self.decalage[1]-TEXTURE_MAX < y*TEXTURE_MAX < self.decalage[1]+resolution["h"]:
                    sprite = sf.Sprite(texture.texture)
                    sprite.position = (x*TEXTURE_MAX-self.decalage[0], y*TEXTURE_MAX-self.decalage[1])
                    window.draw(sprite, sf.RenderStates(shader=shader_en_cours))

        # Dessiner toutes les entités

        for entite in sorted(self.liste_rafraichir, key=lambda objet: objet[1]):
            entite[0].position = (entite[0].position.x-self.decalage[0], entite[0].position.y-self.decalage[1])
            if entite[1] <= 11:
                window.draw(entite[0], sf.RenderStates(shader=shader_en_cours))
            else:
                window.draw(entite[0])

        self.liste_rafraichir = list()

        # Calculer le décalage entre le repère de l'ecran et le repere de la map

        if not joueur.quete_finale:

            self.decalage = [joueur.coord["x"]+(BLOCSIZE-resolution["w"])//2,
                             joueur.coord["y"]+(BLOCSIZE-resolution["h"])//2]

            if resolution["w"] >= self.taille[0]*BLOCSIZE:
                self.decalage[0] = (self.taille[0]*BLOCSIZE-resolution["w"])//2
            else:
                if self.decalage[0] < 0:
                    self.decalage[0] = 0
                elif self.decalage[0]+resolution["w"] >= self.taille[0]*BLOCSIZE:
                    self.decalage[0] = self.taille[0]*BLOCSIZE-resolution["w"]

            if resolution["h"] >= self.taille[1]*BLOCSIZE:
                self.decalage[1] = (self.taille[1]*BLOCSIZE-resolution["h"])//2
            else:
                if self.decalage[1] < 0:
                    self.decalage[1] = 0
                elif self.decalage[1]+resolution["h"] >= self.taille[1]*BLOCSIZE:
                    self.decalage[1] = self.taille[1]*BLOCSIZE-resolution["h"]

    def afficher_interface(self, joueur, resolution):
        """
            Fonction qui affiche l'interface du jeu en fonction des
            caractéristiques du joueur.
        """

        # Afficher la vie du joueur
        curseur_vie = 0
        while curseur_vie < joueur.vie_maximum:
            if joueur.vie-curseur_vie >= 2:
                sprite = sf.Sprite(INTERFACE, (152, 0, 64, 64))
            elif joueur.vie-curseur_vie == 1:
                sprite = sf.Sprite(INTERFACE, (216, 0, 64, 64))
            else:
                sprite = sf.Sprite(INTERFACE, (280, 0, 64, 64))
            sprite.position = (66*(curseur_vie//2)+self.decalage[0]+10, self.decalage[1]+10)
            curseur_vie += 2
            self.liste_rafraichir.append([sprite, 12])

        # Afficher l'objet actuellement en utilisation
        image = sf.Image.create(76, 76, sf.Color(255, 255, 255))
        image.blit(INTERFACE_IMAGE, (0, 0), (0, 24, 76, 76))
        if joueur.inventaire[4][0] is not None:
            image.blit(OBJETS_IMAGE, (6, 6), ((joueur.inventaire[4][0].type % 10)*BLOCSIZE,
                                              (joueur.inventaire[4][0].type//10)*BLOCSIZE, BLOCSIZE, BLOCSIZE))
        sprite = sf.Sprite(sf.Texture.from_image(image))
        sprite.position = (self.decalage[0]+resolution["w"]-86, self.decalage[1]+10)
        self.liste_rafraichir.append([sprite, 12])

    @staticmethod
    def obtenir_taille_message(message):
        """
            Fonction permettant d'obtenir la taille en pixels d'un message dans
            une boite de dialogue.
        """

        # Constantes
        epaisseur_cadre = 4
        taille_bouton = (64, 24)

        # Calcule de la largeur du message
        chaine_longueur_maximale = sorted([len(ligne) for ligne in message.split("\n")], reverse=True)[0]
        if chaine_longueur_maximale*8 > taille_bouton[0]:
            largeur = chaine_longueur_maximale*8+epaisseur_cadre*2
        else:
            largeur = taille_bouton[0]+epaisseur_cadre*2

        # Calcule de la hauteur du message
        hauteur = len(message.split("\n"))*16+taille_bouton[1]+epaisseur_cadre*2

        return largeur, hauteur

    def creer_message(self, message, x_message, y_message):
        """
            Fonction qui ouvre une boîte de dialogue, modifie self.message,
            et y met les coordonnées de la texture et  la texture à afficher
            après l'avoir créée à partir du message à afficher.
        """

        assert isinstance(message, str)

        # Créer l'image

        taille = self.obtenir_taille_message(message)
        self.message["texture"] = sf.RenderTexture(taille[0], taille[1])

        # Dessiner le cadre sur l'image

        cadre = sf.RectangleShape()
        cadre.size = (self.message["texture"].width-4, self.message["texture"].height-4)
        cadre.outline_color = sf.Color(0, 0, 0)
        cadre.outline_thickness = 2
        cadre.position = (2, 2)

        self.message["texture"].draw(cadre)
        self.message["texture"].display()

        self.message["texture"] = self.message["texture"].texture.to_image()

        # Dessinner les caractères sur l'image

        for l, ligne in enumerate(message.split("\n")):
            for c, car in enumerate(ligne):
                self.message["texture"].blit(ASCII_MESSAGE,
                                             (c*8+(self.message["texture"].width-len(ligne)*8)//2, 4+l*16),
                                             ((ord(car) % 10)*8, (ord(car)//10)*16, 8, 16))

        # Transformer l'image en texture et mettre à jour self.message

        self.message["x"], self.message["y"] = x_message, y_message
        self.message["texture"] = sf.Texture.from_image(self.message["texture"])
        self.message["afficher"] = True

        # S'assurer que le cadre ne sort pas de l'ecran

        if self.message["x"] < self.decalage[0]:
            self.message["x"] = self.decalage[0]
        if self.message["y"] < self.decalage[1]:
            self.message["y"] = self.decalage[1]

    def afficher_message(self, window):
        """
            Fonction activée si self.message["afficher"] vaut True, elle
            affiche le message en question.
        """

        # Dessiner le message

        sprite = sf.Sprite(self.message["texture"])
        sprite.position = (self.message["x"], self.message["y"])
        self.liste_rafraichir.append([sprite, 14])

        # Dessiner le bouton et le fait interagir avec l'utilisateur

        position_souris = sf.Mouse.get_position(window)
        position_bouton = (self.message["x"]+(self.message["texture"].width-64)//2,
                           self.message["y"]+self.message["texture"].height-28)

        if position_bouton[0] < position_souris.x+self.decalage[0] < position_bouton[0]+64 and \
           position_bouton[1] < position_souris.y+self.decalage[1] < position_bouton[1]+24:
            sprite = sf.Sprite(INTERFACE, (64, 0, 64, 24))
        else:
            sprite = sf.Sprite(INTERFACE, (0, 0, 64, 24))

        sprite.position = (position_bouton[0], position_bouton[1])
        self.liste_rafraichir.append([sprite, 14])

    def detecter_fin_message(self, position_clic):
        """
            Fonction qui detecte si le joueur clic sur le bouton d'arrête d'une
            boite de dialogue et qui l'arrête si c'est le cas.
        """

        position_bouton = (self.message["x"]+(self.message["texture"].width-64)//2,
                           self.message["y"]+self.message["texture"].height-28)

        if position_bouton[0] < position_clic[0]+self.decalage[0] < position_bouton[0]+64 and \
           position_bouton[1] < position_clic[1]+self.decalage[1] < position_bouton[1]+24:
            self.message["afficher"] = False

    def parametrer_shader_caverne(self, joueur, resolution):
        """
            Envoie au shader les coordonnées du joueur
        """

        coord = (joueur.coord["x"]+32-self.decalage[0], joueur.coord["y"]+32-self.decalage[1])
        SHADER_CAVERNE.set_2float_parameter("pos_joueur", coord[0], coord[1])
        SHADER_CAVERNE.set_2float_parameter("resolution", resolution["w"], resolution["h"])
        SHADER_CAVERNE.set_2float_parameter("taille_map", self.taille[0], self.taille[1])
        SHADER_CAVERNE.set_2float_parameter("decalage", self.decalage[0], self.decalage[1])
        SHADER_CAVERNE.set_texture_parameter("map", self.carte_texture)

    def parametrer_shader_montagne(self, joueur, resolution):

        level = LEVEL_MAP[joueur.coord["x"]//BLOCSIZE, joueur.coord["y"]//BLOCSIZE].r / 255

        coord = (joueur.coord["x"]+32-self.decalage[0], joueur.coord["y"]+32-self.decalage[1])
        SHADER_MONTAGNE.set_2float_parameter("pos_joueur", coord[0], coord[1])
        SHADER_MONTAGNE.set_2float_parameter("resolution", resolution["w"], resolution["h"])
        SHADER_MONTAGNE.set_1float_parameter("level", level)

    # ------------------------------------------------------------------------------------------------------------------
    # GERER LE JOUEUR
    # ------------------------------------------------------------------------------------------------------------------

    def determiner_actions_joueur(self, raccourcis, window, joueur):
        """
            Fonction qui détermine à partir des touches pressées sur le clavier
            et des boutons pressés de la souris quelle action le joueur est en
            train d'effectuer, et qui modifie joueur.actions en conséquances.
        """

        # Déterminer si le joueur se déplace

        if len(joueur.actions) == 0:

            deplacer = False

            if sf.Keyboard.is_key_pressed(raccourcis["deplacer-haut"]):
                joueur.deplacement["x"], joueur.deplacement["y"] = 0, -1
                deplacer = True

            elif sf.Keyboard.is_key_pressed(raccourcis["deplacer-bas"]):
                joueur.deplacement["x"], joueur.deplacement["y"] = 0, 1
                deplacer = True

            elif sf.Keyboard.is_key_pressed(raccourcis["deplacer-droite"]):
                joueur.deplacement["x"], joueur.deplacement["y"] = 1, 0
                deplacer = True

            elif sf.Keyboard.is_key_pressed(raccourcis["deplacer-gauche"]):
                joueur.deplacement["x"], joueur.deplacement["y"] = -1, 0
                deplacer = True

            if deplacer:
                coord_apres_deplacement = (joueur.coord["x"]//BLOCSIZE+joueur.deplacement["x"],
                                           joueur.coord["y"]//BLOCSIZE+joueur.deplacement["y"])
                if self.carte_bool[coord_apres_deplacement]:
                    joueur.actions.append({"type": 0, "direction": [joueur.deplacement["x"], joueur.deplacement["y"]]})
                    self.carte_bool[coord_apres_deplacement] = False
                    self.carte_bool[joueur.coord["x"]//BLOCSIZE, joueur.coord["y"]//BLOCSIZE] = True

        # Déterminer si le joueur attaque

        if len(joueur.actions) == 0:
            if sf.Mouse.is_button_pressed(sf.Mouse.LEFT):
                position_souris = sf.Mouse.get_position(window)
                position_souris = [position_souris.x+self.decalage[0]-joueur.coord["x"]-32,
                                   position_souris.y+self.decalage[1]-joueur.coord["y"]-32]

                if position_souris[0] >= abs(position_souris[1]):
                    joueur.deplacement["x"], joueur.deplacement["y"] = 1, 0

                elif -position_souris[0] >= abs(position_souris[1]):
                    joueur.deplacement["x"], joueur.deplacement["y"] = -1, 0

                elif position_souris[1] > abs(position_souris[0]):
                    joueur.deplacement["x"], joueur.deplacement["y"] = 0, 1

                else:
                    joueur.deplacement["x"], joueur.deplacement["y"] = 0, -1

                joueur.actions.append({"type": 1, "frame": 0, "vitesse": joueur.vitesse_attaque})

    def effectuer_actions_joueur(self, joueur):
        """
            Fonction qui à partir de joueur.actions fait avancer l'action
            effectuée par le joueur d'une frame.
        """

        # Déplacer le joueur

        joueur.deplacer()

        if len(joueur.actions) > 0:

            # FAIRE AVANCER L'ATTAQUE DU JOUEUR

            if joueur.actions[0]["type"] == 1:

                joueur.actions[0]["frame"] += 1

                # Infliger des dégats aux monstres qui sont dans l'attaque
                if joueur.actions[0]["frame"] == joueur.actions[0]["vitesse"]//2:
                    coord_degats = (joueur.coord["x"]+joueur.deplacement["x"]*(BLOCSIZE//2),
                                    joueur.coord["y"]+joueur.deplacement["y"]*(BLOCSIZE//2),
                                    BLOCSIZE, BLOCSIZE)
                    for monstre in self.monstres:
                        if monstre.collision(coord_degats):
                            monstre.mort = True

                # Finir l'attaque
                if joueur.actions[0]["frame"] >= joueur.actions[0]["vitesse"]:
                    del joueur.actions[0]

            # FAIRE AVANCER LA MORT DU JOUEUR

            elif joueur.actions[0]["type"] == 2:
                joueur.actions[0]["frame"] += 1

            # FAIRE AVANCER L'IMMOBILISATION OU L'UTILISATION D'OBJET DU JOUEUR

            elif joueur.actions[0]["type"] in [3, 7]:

                joueur.actions[0]["frame"] += 1
                if joueur.actions[0]["frame"] >= joueur.actions[0]["vitesse"]:
                    del joueur.actions[0]

            # FAIRE PARLER LE JOUEUR

            elif joueur.actions[0]["type"] == 4 and not self.message["afficher"]:

                taille_message = self.obtenir_taille_message(joueur.actions[0]["message"])
                coord = (joueur.coord["x"]-(taille_message[0]-BLOCSIZE)//2, joueur.coord["y"]-taille_message[1])

                self.creer_message(joueur.actions[0]["message"], coord[0], coord[1])
                del joueur.actions[0]

    def afficher_joueur(self, joueur):
        """
            Fonction qui affiche le joueur en fonction des actions qu'il
            effectue et de la direction dans laquelle il se tourne.
        """

        # DETERMINER DANS QUELLE DIRECTION SE TOURNE LE JOUEUR

        if joueur.deplacement["x"] == 1:
            direction = "droite"
        elif joueur.deplacement["x"] == -1:
            direction = "gauche"
        elif joueur.deplacement["y"] == -1:
            direction = "haut"
        else:
            direction = "bas"

        # DETERMINER QUELLE ACTION EFFECTUE LE JOUEUR

        if len(joueur.actions) > 0:

            # Si le joueur se déplace
            if joueur.actions[0]["type"] == 0:
                action = "course"+str(self.tempo//15)

            # Si le joueur attaque
            elif joueur.actions[0]["type"] == 1:
                numero_sprite = str(joueur.actions[0]["frame"]//(joueur.actions[0]["vitesse"]//3+1))
                action = "attaque"+numero_sprite
                position = (joueur.coord["x"]+joueur.deplacement["x"]*(BLOCSIZE//2),
                            joueur.coord["y"]+joueur.deplacement["y"]*(BLOCSIZE//2))
                joueur.sprites[direction]["clavier"+numero_sprite].position = position

                self.liste_rafraichir.append([joueur.sprites[direction]["clavier"+numero_sprite], 11])

            # Si le joueur meurt
            elif joueur.actions[0]["type"] == 2:
                numero_sprite = str(joueur.actions[0]["frame"]//(joueur.actions[0]["vitesse"]//4+1))
                action = "mort"+numero_sprite

            # Si le joueur utilise un objet
            elif joueur.actions[0]["type"] == 7:
                numero_sprite = str(joueur.actions[0]["frame"]//(joueur.actions[0]["vitesse"]//3+1))
                action = "attaque"+numero_sprite

            # Si ce que fait le joueur n'est pas déterminé
            else:
                action = "arret"
        # Si le joueur est à l'arrêt
        else:
            action = "arret"

        # AFFICHER LE BON SPRITE AU BON EMPLACEMENT

        joueur.sprites[direction][action].position = (joueur.coord["x"], joueur.coord["y"])
        if joueur.invincible:
            joueur.sprites[direction][action].color = sf.Color(255, 255, 255, 200)
        else:
            joueur.sprites[direction][action].color = sf.Color(255, 255, 255, 255)
        self.liste_rafraichir.append([joueur.sprites[direction][action], 10])

    def collision_joueur_porte(self, joueur, spawn):
        """
            Fonction qui calcule si le joueur se trouve dans une porte, et qui,
            si c'est le cas, modifie le spawn pour qu'il soit au bon endroit
            dans la bonne map, en retournant un signal indiquant qu'il faut
            changer de map.
        """

        collision = False
        for porte in self.blocs_importants["portes"]:
            if joueur.collision((porte["x"]*BLOCSIZE, porte["y"]*BLOCSIZE, BLOCSIZE, BLOCSIZE)):
                with open("maps/portes/"+spawn["ID-map"]+".txt") as fichier_portes:
                    liste_portes = [data.split(" ") for data in fichier_portes.read().split("\n")]
                    spawn = {"ID-map": liste_portes[porte["ID"]][0],
                             "x": int(liste_portes[porte["ID"]][1]),
                             "y": int(liste_portes[porte["ID"]][2])}
                collision = True
        return spawn, collision

    # ------------------------------------------------------------------------------------------------------------------
    # GERER LES MONSTRES
    # ------------------------------------------------------------------------------------------------------------------

    def determiner_actions_monstres(self, resolution, joueur):
        """
            Fonction qui pour chaque monstre détermine s'il est actif ou non et
            lui donne une action à faire s'il n'en a pas.
        """

        for monstre in self.monstres:
            monstre.actif = monstre.collision((self.decalage[0], self.decalage[1], resolution["w"], resolution["h"]))

            if monstre.actif:

                # ------------------------------------------------------------------------------------------------------
                # MONSTRE DE BASE
                # ------------------------------------------------------------------------------------------------------

                if monstre.type == 0:

                    # FAIRE MOURIR LE MONSTRE

                    if monstre.mort:
                        declencher_mort = True
                        bloc_libere = False
                        for action in monstre.actions:
                            if action["type"] == 2:
                                declencher_mort = False

                        # Libérer le bloc reservé s'il est en déplacement
                        if len(monstre.actions) > 0:
                            if monstre.actions[0]["type"] == 0 and declencher_mort:
                                position_occupee = (monstre.coord["x"]//BLOCSIZE+monstre.deplacement["x"],
                                                    monstre.coord["y"]//BLOCSIZE+monstre.deplacement["y"])
                                if monstre.deplacement["x"] > 0 or monstre.deplacement["y"] > 0:
                                    self.carte_bool[position_occupee] = True
                                    bloc_libere = True
                                else:
                                    if monstre.coord["x"] % BLOCSIZE == 0 == monstre.coord["y"] % BLOCSIZE:
                                        self.carte_bool[position_occupee] = True
                                        bloc_libere = True

                        if declencher_mort:
                            if not bloc_libere:
                                self.carte_bool[monstre.coord["x"]//BLOCSIZE, monstre.coord["y"]//BLOCSIZE] = True

                            # Déclencher la quête du monstre s'il le faut
                            monstre.actions = list()
                            for quete in monstre.quetes:
                                if quete in joueur.quetes or quete["quete"] == 0:
                                    monstre.effectuer_quete(joueur, quete["histoire"], quete["quete"], self)
                                    break

                            monstre.actions.append({"type": 2, "frame": 0, "vitesse": VITESSE_MORT})

                    # DETERMINER L'ACTION DU MONSTRE S'IL N'EST PAS MORT

                    if len(monstre.actions) == 0:

                        # Calculer la trajectoire pour aller au joueur
                        coord_joueur = [joueur.coord["x"]//BLOCSIZE, joueur.coord["y"]//BLOCSIZE]
                        trajectoire = monstre.trouver_trajectoire(coord_joueur, deepcopy(self.carte_bool))

                        if len(trajectoire) > 0:

                            monstre.deplacement["x"] = trajectoire[0][0]-(monstre.coord["x"]//BLOCSIZE)
                            monstre.deplacement["y"] = trajectoire[0][1]-(monstre.coord["y"]//BLOCSIZE)

                            # Si le monstre est à proximité du joueur
                            if trajectoire[0] == coord_joueur:
                                monstre.actions.append({"type": 1, "frame": 0, "vitesse": monstre.vitesse_attaque})

                            # Si le monstre doit se déplacer
                            else:
                                coord_apres_deplacement = (monstre.coord["x"]//BLOCSIZE+monstre.deplacement["x"],
                                                           monstre.coord["y"]//BLOCSIZE+monstre.deplacement["y"])
                                monstre.actions.append({"type": 0, "direction": [monstre.deplacement["x"],
                                                                                 monstre.deplacement["y"]]})
                                self.carte_bool[coord_apres_deplacement] = False
                                self.carte_bool[monstre.coord["x"]//BLOCSIZE, monstre.coord["y"]//BLOCSIZE] = True
                        else:
                            monstre.actions.append({"type": 1, "frame": 0, "vitesse": monstre.vitesse_attaque})

                # ------------------------------------------------------------------------------------------------------
                # MONSTRE CORPS A CORPS LONGUE PORTEE
                # ------------------------------------------------------------------------------------------------------

                elif monstre.type == 1:

                    # FAIRE MOURIR LE MONSTRE

                    if monstre.mort:
                        declencher_mort = True
                        bloc_libere = False
                        for action in monstre.actions:
                            if action["type"] == 2:
                                declencher_mort = False

                        # Libérer le bloc reservé s'il est en déplacement
                        if len(monstre.actions) > 0:
                            if monstre.actions[0]["type"] == 0 and declencher_mort:
                                position_occupee = (monstre.coord["x"]//BLOCSIZE+monstre.deplacement["x"],
                                                    monstre.coord["y"]//BLOCSIZE+monstre.deplacement["y"])
                                if monstre.deplacement["x"] > 0 or monstre.deplacement["y"] > 0:
                                    self.carte_bool[position_occupee] = True
                                    bloc_libere = True
                                else:
                                    if monstre.coord["x"] % BLOCSIZE == 0 == monstre.coord["y"] % BLOCSIZE:
                                        self.carte_bool[position_occupee] = True
                                        bloc_libere = True

                        if declencher_mort:
                            if not bloc_libere:
                                self.carte_bool[
                                    monstre.coord["x"]//BLOCSIZE, monstre.coord["y"]//BLOCSIZE] = True

                            # Déclencher la quête du monstre s'il le faut
                            monstre.actions = list()
                            for quete in monstre.quetes:
                                if quete in joueur.quetes or quete["quete"] == 0:
                                    monstre.effectuer_quete(joueur, quete["histoire"], quete["quete"], self)
                                    break

                            monstre.actions.append({"type": 2, "frame": 0, "vitesse": VITESSE_MORT})

                    # DETERMINER L'ACTION DU MONSTRE S'IL N'EST PAS MORT

                    if len(monstre.actions) == 0:

                        # Calculer la trajectoire pour aller au joueur
                        coord_joueur = [joueur.coord["x"]//BLOCSIZE, joueur.coord["y"]//BLOCSIZE]
                        cibles_potentielles = [[coord_joueur[0]+2, coord_joueur[1]],
                                               [coord_joueur[0]-2, coord_joueur[1]],
                                               [coord_joueur[0], coord_joueur[1]+2],
                                               [coord_joueur[0], coord_joueur[1]-2]]
                        self.carte_bool[monstre.coord["x"]//BLOCSIZE, monstre.coord["y"]//BLOCSIZE] = True
                        for c, cible in enumerate(cibles_potentielles):
                            if not (0 <= cible[0] < self.taille[0] and 0 <= cible[1] < self.taille[1]):
                                cibles_potentielles[c].append(self.taille[0]**2 + self.taille[1]**2)
                            elif self.carte_bool[cible[0], cible[1]]:
                                score = (monstre.coord["x"]//BLOCSIZE-cible[0])**2+(monstre.coord["y"]//BLOCSIZE-cible[1])**2
                                cibles_potentielles[c].append(score)
                            else:
                                cibles_potentielles[c].append(self.taille[0]**2 + self.taille[1]**2)
                        self.carte_bool[monstre.coord["x"]//BLOCSIZE, monstre.coord["y"]//BLOCSIZE] = False

                        cible = sorted(cibles_potentielles, key=lambda cible: cible[2])
                        cible = cible[0][:2]
                        trajectoire = monstre.trouver_trajectoire(cible, deepcopy(self.carte_bool))

                        if len(trajectoire) > 0:

                            monstre.deplacement["x"] = trajectoire[0][0]-(monstre.coord["x"]//BLOCSIZE)
                            monstre.deplacement["y"] = trajectoire[0][1]-(monstre.coord["y"]//BLOCSIZE)

                            coord_apres_deplacement = (monstre.coord["x"]//BLOCSIZE+monstre.deplacement["x"],
                                                       monstre.coord["y"]//BLOCSIZE+monstre.deplacement["y"])
                            monstre.actions.append({"type": 0, "direction": [monstre.deplacement["x"],
                                                                             monstre.deplacement["y"]]})
                            self.carte_bool[coord_apres_deplacement] = False
                            self.carte_bool[monstre.coord["x"]//BLOCSIZE, monstre.coord["y"]//BLOCSIZE] = True
                        else:
                            monstre.deplacement["x"] = joueur.coord["x"]-monstre.coord["x"]
                            if monstre.deplacement["x"] != 0:
                                monstre.deplacement["x"] = monstre.deplacement["x"]//abs(monstre.deplacement["x"])
                                monstre.deplacement["y"] = 0
                            else:
                                monstre.deplacement["y"] = joueur.coord["y"]-monstre.coord["y"]
                                if monstre.deplacement["y"] != 0:
                                    monstre.deplacement["y"] = monstre.deplacement["y"]//abs(monstre.deplacement["y"])

                            monstre.actions.append({"type": 1, "frame": 0, "vitesse": monstre.vitesse_attaque})

                # ------------------------------------------------------------------------------------------------------
                # MONSTRE A DISTANCE IMMOBILE ET MONSTRE A DISTANCE BLEU
                # ------------------------------------------------------------------------------------------------------

                elif monstre.type in [2, 3]:

                    # FAIRE MOURIR LE MONSTRE

                    if monstre.mort:
                        declencher_mort = True
                        bloc_libere = False
                        for action in monstre.actions:
                            if action["type"] == 2:
                                declencher_mort = False

                        if declencher_mort:
                            if not bloc_libere:
                                self.carte_bool[monstre.coord["x"]//BLOCSIZE, monstre.coord["y"]//BLOCSIZE] = True

                            # Déclencher la quête du monstre s'il le faut
                            monstre.actions = list()
                            for quete in monstre.quetes:
                                if quete in joueur.quetes or quete["quete"] == 0:
                                    monstre.effectuer_quete(joueur, quete["histoire"], quete["quete"], self)
                                    break

                            monstre.actions.append({"type": 2, "frame": 0, "vitesse": VITESSE_MORT})

                    # DETERMINER L'ACTION DU MONSTRE S'IL N'EST PAS MORT

                    if len(monstre.actions) == 0:

                        if abs(monstre.coord["x"]-joueur.coord["x"]) >= abs(monstre.coord["y"]-joueur.coord["y"]):
                            if monstre.coord["x"] > joueur.coord["x"]:
                                monstre.deplacement = {"x": -1, "y": 0}
                            else:
                                monstre.deplacement = {"x": 1, "y": 0}
                        else:
                            if monstre.coord["y"] > joueur.coord["y"]:
                                monstre.deplacement = {"x": 0, "y": -1}
                            else:
                                monstre.deplacement = {"x": 0, "y": 1}

                        monstre.actions.append({"type": 1, "frame": 0, "vitesse": monstre.vitesse_attaque})

    def effectuer_actions_monstres(self, joueur):
        """
            Fonction qui pour chaque monstre fait avancer l'action qu'il est
            en train d'effectuer s'il en a une.
        """

        for monstre in self.monstres:

            if monstre.actif:

                # DEPLACER LE MONSTRE

                monstre.deplacer()

                if len(monstre.actions) > 0:

                    # FAIRE AVANCER L'ATTAQUE DU MONSTRE

                    if monstre.actions[0]["type"] == 1:

                        # Monstre de base ------------------------------------------------------------------------------
                        if monstre.type == 0:
                            monstre.actions[0]["frame"] += 1
                            if monstre.actions[0]["frame"] == monstre.actions[0]["vitesse"]//2:
                                coord_degats = (monstre.coord["x"]+monstre.deplacement["x"]*(BLOCSIZE//2),
                                                monstre.coord["y"]+monstre.deplacement["y"]*(BLOCSIZE//2),
                                                BLOCSIZE, BLOCSIZE)
                                if joueur.collision(coord_degats) and monstre.attaque > joueur.armure:
                                    joueur.vie -= monstre.attaque-joueur.armure

                            if monstre.actions[0]["frame"] >= monstre.actions[0]["vitesse"]:
                                del monstre.actions[0]

                        # Monstre corps à corps longue portée ----------------------------------------------------------
                        elif monstre.type == 1:
                            monstre.actions[0]["frame"] += 1

                            if monstre.actions[0]["frame"] == 2*monstre.actions[0]["vitesse"]//3+1:
                                coord_degats = (monstre.coord["x"]-BLOCSIZE*abs(monstre.deplacement["x"])+3*monstre.deplacement["x"]*(BLOCSIZE//2),
                                                monstre.coord["y"]-BLOCSIZE*abs(monstre.deplacement["y"])+3*monstre.deplacement["y"]*(BLOCSIZE//2),
                                                BLOCSIZE+BLOCSIZE*abs(monstre.deplacement["x"]),
                                                BLOCSIZE+BLOCSIZE*abs(monstre.deplacement["y"]))
                                if joueur.collision(coord_degats) and monstre.attaque > joueur.armure:
                                    joueur.vie -= monstre.attaque-joueur.armure

                            if monstre.actions[0]["frame"] >= monstre.actions[0]["vitesse"]:
                                del monstre.actions[0]

                        # Monstre à distance immobile ------------------------------------------------------------------
                        elif monstre.type == 2:
                            monstre.actions[0]["frame"] += 1

                            if monstre.actions[0]["frame"] >= monstre.actions[0]["vitesse"]:

                                attaque = Attaque(0)
                                attaque.deplacement["x"] = monstre.deplacement["x"]
                                attaque.deplacement["y"] = monstre.deplacement["y"]
                                attaque.coord["x"] = monstre.coord["x"] + BLOCSIZE*attaque.deplacement["x"]
                                attaque.coord["y"] = monstre.coord["y"] + BLOCSIZE*attaque.deplacement["y"]

                                self.attaques.append(attaque)

                                del monstre.actions[0]

                        # Monstre à distance bleu ----------------------------------------------------------------------
                        elif monstre.type == 3:
                            monstre.actions[0]["frame"] += 1

                            if monstre.actions[0]["frame"] >= monstre.actions[0]["vitesse"]:

                                # Projectile
                                if monstre.data["prochaine_attaque"] == 0:

                                    attaque = Attaque(0)
                                    attaque.deplacement["x"] = monstre.deplacement["x"]
                                    attaque.deplacement["y"] = monstre.deplacement["y"]
                                    attaque.coord["x"] = monstre.coord["x"] + BLOCSIZE*attaque.deplacement["x"]
                                    attaque.coord["y"] = monstre.coord["y"] + BLOCSIZE*attaque.deplacement["y"]

                                    self.attaques.append(attaque)

                                # Explosions
                                else:

                                    directions = [[0, 1], [0, -1], [1, 1], [1, 0], [1, -1], [-1, 1], [-1, 0], [-1, -1]]

                                    for d in directions:
                                        attaque = Attaque(3)
                                        attaque.coord["x"] = monstre.coord["x"] + d[0]*BLOCSIZE
                                        attaque.coord["y"] = monstre.coord["y"] + d[1]*BLOCSIZE
                                        self.attaques.append(attaque)

                                monstre.data["prochaine_attaque"] = 1 - monstre.data["prochaine_attaque"]

                                del monstre.actions[0]

                    # FAIRE AVANCER L'IMMOBILISATION DU MONSTRE

                    elif monstre.actions[0]["type"] == 3:

                        monstre.actions[0]["frame"] += 1
                        if monstre.actions[0]["frame"] >= monstre.actions[0]["vitesse"]:
                            del monstre.actions[0]

                    # FAIRE PARLER LE MONSTRE

                    elif monstre.actions[0]["type"] == 4 and not self.message["afficher"]:

                        taille_message = self.obtenir_taille_message(monstre.actions[0]["message"])
                        coord = (monstre.coord["x"]-(taille_message[0]-BLOCSIZE)//2,
                                 monstre.coord["y"]-taille_message[1])

                        self.creer_message(monstre.actions[0]["message"], coord[0], coord[1])
                        del monstre.actions[0]

        # FAIRE AVANCER LA MORT DU MONSTRE

        compteur = 0
        while compteur < len(self.monstres):
            if len(self.monstres[compteur].actions) > 0:

                if self.monstres[compteur].actions[0]["type"] == 2:
                    self.monstres[compteur].actions[0]["frame"] += 1

                    # Faire apparaître un coeur
                    if self.monstres[compteur].actions[0]["frame"] == 1 and randrange(10) == 0:
                        objet = Objet(0)
                        objet.coord["x"] = self.monstres[compteur].coord["x"]
                        objet.coord["y"] = self.monstres[compteur].coord["y"]
                        self.objets.append(objet)

                    # Faire apparaître un parchemin chez les monstres à distance
                    elif self.monstres[compteur].type == 2:
                        if self.monstres[compteur].actions[0]["frame"] == 1 and randrange(30) == 0:
                            objet = Objet(6)
                            objet.coord["x"] = self.monstres[compteur].coord["x"]
                            objet.coord["y"] = self.monstres[compteur].coord["y"]
                            self.objets.append(objet)

                    # Faire apparaître un parchemin chez les monstres explosifs
                    elif self.monstres[compteur].type == 3:
                        if self.monstres[compteur].actions[0]["frame"] == 1 and randrange(30) == 0:
                            objet = Objet(12)
                            objet.coord["x"] = self.monstres[compteur].coord["x"]
                            objet.coord["y"] = self.monstres[compteur].coord["y"]
                            self.objets.append(objet)

                    # Effacer le monstre
                    if self.monstres[compteur].actions[0]["frame"] == self.monstres[compteur].actions[0]["vitesse"]:
                        del self.monstres[compteur]
                        compteur -= 1

                elif self.monstres[compteur].actions[0]["type"] == 6:
                    del self.monstres[compteur]
                    compteur -= 1

            compteur += 1

    def afficher_monstres(self):
        """
            Fonction qui affiche les monstres à l'ecran en fonction de l'action
            qu'ils effectuent et de la direction dans laquelle ils se tournent.
        """

        for monstre in self.monstres:

            if monstre.actif:

                # DETERMINER DANS QUELLE DIRECTION SE TOURNE LE MONSTRE

                if monstre.deplacement["x"] == 1:
                    direction = "droite"
                elif monstre.deplacement["x"] == -1:
                    direction = "gauche"
                elif monstre.deplacement["y"] == -1:
                    direction = "haut"
                else:
                    direction = "bas"

                # DETERMINER QUELLE ACTION EFFECTUE LE MONSTRE

                if len(monstre.actions) > 0:

                    # Si le monstre se déplace
                    if monstre.actions[0]["type"] == 0:
                        action = "course"+str(self.tempo//15)

                    # Si le monstre attaque
                    elif monstre.actions[0]["type"] == 1:
                        numero_sprite = int(monstre.actions[0]["frame"]//(monstre.actions[0]["vitesse"]/3))
                        action = "attaque"+str(numero_sprite)

                        # Si le monstre qui attaque est un monstre corps à corps longue portée
                        if monstre.type == 1:
                            temps_sprite = monstre.actions[0]["vitesse"]//3
                            if monstre.actions[0]["frame"] > temps_sprite:
                                if temps_sprite <= monstre.actions[0]["frame"] < 2 * temps_sprite:
                                    if direction == "bas":
                                        sprite = sf.Sprite(ATTAQUES, (0, 128, BLOCSIZE, BLOCSIZE))
                                    elif direction == "haut":
                                        sprite = sf.Sprite(ATTAQUES, (64, 128, BLOCSIZE, BLOCSIZE))
                                    elif direction == "droite":
                                        sprite = sf.Sprite(ATTAQUES, (128, 128, BLOCSIZE, BLOCSIZE))
                                    else:
                                        sprite = sf.Sprite(ATTAQUES, (192, 128, BLOCSIZE, BLOCSIZE))
                                    sprite.position = ((monstre.coord["x"]+monstre.deplacement["x"]*BLOCSIZE,
                                                        monstre.coord["y"]+monstre.deplacement["y"]*BLOCSIZE))
                                    self.liste_rafraichir.append([sprite, 6])
                                else:
                                    if direction == "bas":
                                        sprites = (sf.Sprite(ATTAQUES, (0, 0, BLOCSIZE, BLOCSIZE)),
                                                   sf.Sprite(ATTAQUES, (0, 64, BLOCSIZE, BLOCSIZE)))
                                    elif direction == "haut":
                                        sprites = (sf.Sprite(ATTAQUES, (64, 0, BLOCSIZE, BLOCSIZE)),
                                                   sf.Sprite(ATTAQUES, (64, 64, BLOCSIZE, BLOCSIZE)))
                                    elif direction == "droite":
                                        sprites = (sf.Sprite(ATTAQUES, (128, 0, BLOCSIZE, BLOCSIZE)),
                                                   sf.Sprite(ATTAQUES, (128, 64, BLOCSIZE, BLOCSIZE)))
                                    else:
                                        sprites = (sf.Sprite(ATTAQUES, (192, 0, BLOCSIZE, BLOCSIZE)),
                                                   sf.Sprite(ATTAQUES, (192, 64, BLOCSIZE, BLOCSIZE)))
                                    sprites[0].position = ((monstre.coord["x"]+monstre.deplacement["x"]*BLOCSIZE,
                                                            monstre.coord["y"]+monstre.deplacement["y"]*BLOCSIZE))
                                    sprites[1].position = ((monstre.coord["x"]+monstre.deplacement["x"]*BLOCSIZE*2,
                                                            monstre.coord["y"]+monstre.deplacement["y"]*BLOCSIZE*2))
                                    self.liste_rafraichir.append([sprites[0], 6])
                                    self.liste_rafraichir.append([sprites[1], 6])

                    # Si le monstre meurt
                    elif monstre.actions[0]["type"] == 2:
                        numero_sprite = int(monstre.actions[0]["frame"]//(monstre.actions[0]["vitesse"]/4))
                        action = "mort"+str(numero_sprite)

                    # Si ce que fait le monstre n'est pas déterminé
                    else:
                        action = "arret"
                # Si le monstre est à l'arrêt
                else:
                    action = "arret"

                # AFFICHER LE BON SPRITE AU BON EMPLACEMENT

                monstre.sprites[direction][action].position = (monstre.coord["x"], monstre.coord["y"])
                self.liste_rafraichir.append([monstre.sprites[direction][action], 6])

    # ------------------------------------------------------------------------------------------------------------------
    # GERER LES PNJ
    # ------------------------------------------------------------------------------------------------------------------

    def determiner_actions_pnj(self, resolution, joueur, raccourcis):
        """
            Fonction qui détermine les actions à effectuer par le PNJ, à partir
            de ses répliques et de sa trajectoire.
        """

        for pnj in self.pnjs:
            pnj.actif = pnj.collision((self.decalage[0], self.decalage[1], resolution["w"], resolution["h"]))

            if pnj.actif and len(pnj.actions) == 0:

                # FAIRE INTERAGIR LE PNJ

                coord_collision = (joueur.coord["x"]+joueur.deplacement["x"]*BLOCSIZE,
                                   joueur.coord["y"]+joueur.deplacement["y"]*BLOCSIZE, BLOCSIZE, BLOCSIZE)
                if pnj.collision(coord_collision) and sf.Keyboard.is_key_pressed(raccourcis["interagir"]):

                    # Déterminer si le PNJ a une quête que le joueur doit faire
                    quete_effectuee = False
                    for quete in pnj.quetes:
                        if quete in joueur.quetes:
                            pnj.effectuer_quete(joueur, quete["histoire"], quete["quete"], self)
                            quete_effectuee = True

                    if not quete_effectuee:
                        pnj.actions.append({"type": 4, "message": pnj.repliques[randrange(len(pnj.repliques))]})
                        pnj.actions.append({"type": 3, "frame": 0, "vitesse": 1})

                # ORIENTER LE PNJ

                elif -2 in pnj.trajectoire[pnj.index_trajectoire] or 2 in pnj.trajectoire[pnj.index_trajectoire]:

                    if pnj.trajectoire[pnj.index_trajectoire][0] == -2:
                        pnj.deplacement["x"], pnj.deplacement["y"] = -1, 0
                    elif pnj.trajectoire[pnj.index_trajectoire][0] == 2:
                        pnj.deplacement["x"], pnj.deplacement["y"] = 1, 0
                    elif pnj.trajectoire[pnj.index_trajectoire][1] == -2:
                        pnj.deplacement["x"], pnj.deplacement["y"] = 0, -1
                    else:
                        pnj.deplacement["x"], pnj.deplacement["y"] = 0, 1

                    pnj.index_trajectoire = (pnj.index_trajectoire+1) % len(pnj.trajectoire)
                    pnj.actions.append({"type": 3, "frame": 0, "vitesse": 1})

                # DEPLACER LE PNJ

                elif -1 in pnj.trajectoire[pnj.index_trajectoire] or 1 in pnj.trajectoire[pnj.index_trajectoire]:
                    coord_apres_deplacement = (pnj.coord["x"]//BLOCSIZE+pnj.trajectoire[pnj.index_trajectoire][0],
                                               pnj.coord["y"]//BLOCSIZE+pnj.trajectoire[pnj.index_trajectoire][1])
                    if self.carte_bool[coord_apres_deplacement]:
                        pnj.actions.append({"type": 0, "direction": pnj.trajectoire[pnj.index_trajectoire]})
                        self.carte_bool[pnj.coord["x"]//BLOCSIZE, pnj.coord["y"]//BLOCSIZE] = True
                        self.carte_bool[coord_apres_deplacement] = False
                        pnj.index_trajectoire = (pnj.index_trajectoire+1) % len(pnj.trajectoire)

    def effectuer_actions_pnj(self):
        """
            Fonction qui effectue les actions de chaque PNJ s'ils en ont une.
        """

        for pnj in self.pnjs:

            if pnj.actif:

                # FAIRE SE DEPLACER LE PNJ

                pnj.deplacer()

                if len(pnj.actions) > 0:

                    # FAIRE ATTAQUER LE PNJ

                    if pnj.actions[0]["type"] == 1:

                        pnj.actions[0]["frame"] += 1
                        if pnj.actions[0]["frame"] >= pnj.actions[0]["vitesse"]:
                            del pnj.actions[0]

                    # FAIRE AVANCER L'IMMOBILISATION DU PNJ

                    elif pnj.actions[0]["type"] == 3:

                        pnj.actions[0]["frame"] += 1
                        if pnj.actions[0]["frame"] >= pnj.actions[0]["vitesse"]:
                            del pnj.actions[0]

                    # FAIRE PARLER LE PNJ

                    elif pnj.actions[0]["type"] == 4 and not self.message["afficher"]:

                        taille_message = self.obtenir_taille_message(pnj.actions[0]["message"])
                        position = (pnj.coord["x"]+(BLOCSIZE-taille_message[0])//2, pnj.coord["y"]-taille_message[1])

                        self.creer_message(pnj.actions[0]["message"], position[0], position[1])
                        del pnj.actions[0]

        # FAIRE AVANCER LA MORT DU PNJ

        compteur = 0
        while compteur < len(self.pnjs):
            if len(self.pnjs[compteur].actions) > 0:

                if self.pnjs[compteur].actions[0]["type"] == 2:
                    self.pnjs[compteur].actions[0]["frame"] += 1
                    if self.pnjs[compteur].actions[0]["frame"] == self.pnjs[compteur].actions[0]["vitesse"]:
                        del self.pnjs[compteur]
                        compteur -= 1

                elif self.pnjs[compteur].actions[0]["type"] == 6:
                    del self.pnjs[compteur]
                    compteur -= 1

            compteur += 1

    def afficher_pnj(self):
        """
            Fonction qui affiche les PNJS à l'ecran en fonction de l'action
            qu'ils effectuent et de la direction dans laquelle ils se tournent.
        """

        for pnj in self.pnjs:

            if pnj.actif:

                # DETERMINER DANS QUELLE DIRECTION SE TOURNE LE PNJ

                if pnj.deplacement["x"] == 1:
                    direction = "droite"
                elif pnj.deplacement["x"] == -1:
                    direction = "gauche"
                elif pnj.deplacement["y"] == -1:
                    direction = "haut"
                else:
                    direction = "bas"

                # DETERMINER QUELLE ACTION EFFECTUE LE PNJ

                if len(pnj.actions) > 0:

                    # Si le PNJ se déplace
                    if pnj.actions[0]["type"] == 0:
                        action = "course"+str(self.tempo//15)

                    # Si le PNJ attaque
                    elif pnj.actions[0]["type"] == 1:
                        numero_sprite = int(pnj.actions[0]["frame"]//(pnj.actions[0]["vitesse"]/3))
                        action = "attaque"+str(numero_sprite)

                    # Si le PNJ meurt
                    elif pnj.actions[0]["type"] == 2:
                        numero_sprite = int(pnj.actions[0]["frame"]//(pnj.actions[0]["vitesse"]/4))
                        action = "mort"+str(numero_sprite)

                    # Si ce que fait le PNJ n'est pas déterminé
                    else:
                        action = "arret"
                # Si le PNJ est à l'arrêt
                else:
                    action = "arret"

                # AFFICHER LE BON SPRITE AU BON EMPLACEMENT

                pnj.sprites[direction][action].position = (pnj.coord["x"], pnj.coord["y"])
                self.liste_rafraichir.append([pnj.sprites[direction][action], 8])

    # ------------------------------------------------------------------------------------------------------------------
    # GERER LES ATTAQUES
    # ------------------------------------------------------------------------------------------------------------------

    def determiner_actions_attaque(self, joueur, resolution):
        """
            Fonction qui détermine si une attaque est active, et si oui, détermine ce qu'elle fait,
            avancer, exploser...
        """

        for attaque in self.attaques:
            attaque.active = attaque.collision((self.decalage[0], self.decalage[1], resolution["w"], resolution["h"]))

            if attaque.active:

                # ------------------------------------------------------------------------------------------------------
                # PROJECTILES
                # ------------------------------------------------------------------------------------------------------

                if attaque.type in ATTAQUES_PROJECTILES:

                    # Si le projectile n'a pas d'action en cours, le faire avancer si possible
                    if len(attaque.actions) == 0:

                        x_valide = 0 <= attaque.coord["x"]//BLOCSIZE < self.taille[0]
                        y_valide = 0 <= attaque.coord["y"]//BLOCSIZE < self.taille[1]

                        if not (x_valide and y_valide):
                            attaque.detruite = True
                        elif self.carte_bool[attaque.coord["x"]//BLOCSIZE, attaque.coord["y"]//BLOCSIZE]:
                            direction = [attaque.deplacement["x"], attaque.deplacement["y"]]
                            attaque.actions.append({"type": 0, "direction": direction})
                        else:
                            attaque.detruite = True

                        if attaque.detruite:
                            attaque.actions = [{"type": 2, "frame": 0, "vitesse": 20}]

                    # Si le projectile a une action en cours alors qu'il est détruit
                    elif attaque.actions[0]["type"] != 2 and attaque.detruite:
                        attaque.actions = [{"type": 2, "frame": 0, "vitesse": 20}]

                # ATTAQUES DE FEU --------------------------------------------------------------------------------------

                elif attaque.type == 2 and len(attaque.actions) == 0:

                    # Détruire un bloc de glace devant le joueur s'il y en a un
                    for meuble in self.meubles:
                        if meuble.type == 9:
                            if meuble.collision(attaque):
                                for quete in meuble.quetes:
                                    if quete in joueur.quetes:
                                        meuble.effectuer_quete(joueur, quete["histoire"], quete["quete"], self)
                                meuble.actions = [{"type": 2, "frame": 0, "vitesse": 20}]

                    # Tuer les monstres en contact avec l'attaque
                    for monstre in self.monstres:
                        if monstre.collision(attaque):
                            monstre.mort = True

                    # Détruire l'attaque dès qu'elle apparait
                    attaque.actions = [{"type": 2, "frame": 0, "vitesse": joueur.vitesse_attaque}]

                # EXPLOSIONS MONSTRE A DISTANCE BLEU -------------------------------------------------------------------

                elif attaque.type == 3 and len(attaque.actions) == 0:

                    # Infliger des dégats au joueur s'il est en contact avec l'attaque
                    if joueur.collision(attaque):
                        joueur.vie -= attaque.degats

                    # Tuer les monstres en contact avec le projectile et detruire le projectile
                    for monstre in self.monstres:
                        if monstre.collision(attaque):
                            monstre.mort = True
                            attaque.detruite = True

                    # Détruire l'attaque dès qu'elle apparait
                    attaque.actions = [{"type": 2, "frame": 0, "vitesse": 20}]

                # EXPLOSIONS PARCHEMIN JOUEUR --------------------------------------------------------------------------

                elif attaque.type == 4 and len(attaque.actions) == 0:

                    # Tuer les monstres en contact avec le projectile et detruire le projectile
                    for monstre in self.monstres:
                        if monstre.collision(attaque):
                            monstre.mort = True
                            attaque.detruite = True

                    # Détruire l'attaque dès qu'elle apparait
                    attaque.actions = [{"type": 2, "frame": 0, "vitesse": 20}]

            else:

                attaque.actions = [{"type": 6}]

    def effectuer_actions_attaque(self, joueur):
        """
            Fonction qui effectue les actions des attaques si elles en ont une.
        """

        for attaque in self.attaques:

            if attaque.active:

                attaque.deplacer()

                # ------------------------------------------------------------------------------------------------------
                # PROJECTILES
                # ------------------------------------------------------------------------------------------------------

                if attaque.type in ATTAQUES_PROJECTILES:

                    # Tuer les monstres en contact avec le projectile et detruire le projectile
                    for monstre in self.monstres:
                        if monstre.collision(attaque):
                            monstre.mort = True
                            attaque.detruite = True

                    # Détruire le projectile s'il est en contact avec un pnj
                    for pnj in self.pnjs:
                        if pnj.collision(attaque):
                            attaque.detruite = True

                    # Infliger des dégats au joueur s'il est en contact avec le projectile et détruire le projectile
                    if attaque.type in ATTAQUES_HOSTILES and joueur.collision(attaque):
                        joueur.vie -= attaque.degats
                        attaque.detruite = True

                    # Détruire le projectile s'il est en contact avec une attaque
                    for attaque2 in self.attaques:
                        if attaque2.collision(attaque) and not attaque2 is attaque and not attaque2.detruite:
                            if attaque.type in ATTAQUES_HOSTILES:
                                attaque.detruite = True
                            if attaque2.type in ATTAQUES_HOSTILES:
                                attaque2.detruite = True

        # Detruire les attaques

        compteur = 0
        while compteur < len(self.attaques):

            if len(self.attaques[compteur].actions) > 0:

                # ------------------------------------------------------------------------------------------------------
                # PROJECTILES
                # ------------------------------------------------------------------------------------------------------

                if self.attaques[compteur].type in ATTAQUES_PROJECTILES:

                    if self.attaques[compteur].actions[0]["type"] == 2:
                        self.attaques[compteur].actions[0]["frame"] += 1
                        if self.attaques[compteur].actions[0]["frame"] >= self.attaques[compteur].actions[0]["vitesse"]:
                            del self.attaques[compteur]
                            compteur -= 1
                    elif self.attaques[compteur].actions[0]["type"] == 6:
                        del self.attaques[compteur]
                        compteur -= 1

                # AUTRES ATTAQUES A DESTRUCTIONS CLASSIQUES ------------------------------------------------------------

                elif self.attaques[compteur].type in [2, 3, 4]:

                    if self.attaques[compteur].actions[0]["type"] == 2:
                        self.attaques[compteur].actions[0]["frame"] += 1
                        if self.attaques[compteur].actions[0]["frame"] >= self.attaques[compteur].actions[0]["vitesse"]:
                            del self.attaques[compteur]
                            compteur -= 1
                    elif self.attaques[compteur].actions[0]["type"] == 6:
                        del self.attaques[compteur]
                        compteur -= 1

            compteur += 1

    def afficher_attaque(self):
        """
            Fonction qui affiche les attaques à l'ecran en fonction de leur direction
            et de si elles sont detruites où non.
        """

        for attaque in self.attaques:

            if attaque.active:

                # ------------------------------------------------------------------------------------------------------
                # PROJECTILES
                # ------------------------------------------------------------------------------------------------------

                if attaque.type in ATTAQUES_PROJECTILES:

                    if attaque.deplacement["x"] == 1:
                        direction = "droite"
                    elif attaque.deplacement["x"] == -1:
                        direction = "gauche"
                    elif attaque.deplacement["y"] == -1:
                        direction = "haut"
                    else:
                        direction = "bas"

                    if attaque.actions[0]["type"] == 2:
                        numero_sprite = int(attaque.actions[0]["frame"]//(attaque.actions[0]["vitesse"]/4))
                        action = "detruit"+str(numero_sprite)
                    else:
                        action = "avance"+str(self.tempo // 15)

                    # AFFICHER LE BON SPRITE AU BON EMPLACEMENT

                    attaque.sprites[direction][action].position = (attaque.coord["x"], attaque.coord["y"])
                    self.liste_rafraichir.append([attaque.sprites[direction][action], 4])

                # ATTAQUES DE FEU --------------------------------------------------------------------------------------

                elif attaque.type == 2:

                    if attaque.deplacement["x"] == 1:
                        direction = "droite"
                    elif attaque.deplacement["x"] == -1:
                        direction = "gauche"
                    elif attaque.deplacement["y"] == -1:
                        direction = "haut"
                    else:
                        direction = "bas"

                    if attaque.actions[0]["type"] == 2:
                        numero_sprite = int(attaque.actions[0]["frame"]//(attaque.actions[0]["vitesse"]/3))
                        action = "clavier"+str(numero_sprite)
                    else:
                        action = "clavier0"

                    attaque.sprites[direction][action].position = (attaque.coord["x"], attaque.coord["y"])
                    self.liste_rafraichir.append([attaque.sprites[direction][action], 11])

                # EXPLOSIONS MONSTRES A DISTANCE BLEU ET PARCHEMIN JOUEUR ----------------------------------------------

                elif attaque.type in [3, 4]:

                    if attaque.actions[0]["type"] == 2:
                        numero_sprite = int(attaque.actions[0]["frame"]//(attaque.actions[0]["vitesse"]/4))
                        action = "explosion"+str(numero_sprite)
                    else:
                        action = "explosion0"

                    attaque.sprites[action].position = (attaque.coord["x"], attaque.coord["y"])
                    self.liste_rafraichir.append([attaque.sprites[action], 4])

    # ------------------------------------------------------------------------------------------------------------------
    # GERER LES OBJETS, MEUBLES ET PLACES
    # ------------------------------------------------------------------------------------------------------------------

    def ramasser_afficher_objets(self, joueur):
        """
            Fonction qui détecte si le joueur marche sur un objet, et qui, si
            c'est le cas, le ramasse ou l'utilise, en fonction de son type,
            puis qui l'affiche.
        """

        compteur = 0
        while compteur < len(self.objets):

            # Afficher l'objet
            self.objets[compteur].sprites["normal"].position = (self.objets[compteur].coord["x"],
                                                                self.objets[compteur].coord["y"])
            self.liste_rafraichir.append([self.objets[compteur].sprites["normal"], 2])

            # Ramasser l'objet s'il est en collision avec le joueur et que le jeu tourne (pas de message affiché)
            if self.objets[compteur].collision(joueur) and not self.message["afficher"]:

                if self.objets[compteur].type == 0:
                    joueur.vie += 2
                elif self.objets[compteur].type in LISTE_RAMASSABLES:
                    joueur.ajouter_objet_inventaire(self.objets[compteur])

                del self.objets[compteur]
                compteur -= 1

            compteur += 1

    def utiliser_objet(self, joueur, window):
        """
            Fonction qui utilise l'objet que le joueur a dans la case prévue à
            cet effet dans l'inventaire.
        """

        if joueur.inventaire[4][0] is not None:

            # Potion de vie --------------------------------------------------------------------------------------------
            if joueur.inventaire[4][0].type == 5:

                if joueur.vie < joueur.vie_maximum:
                    joueur.inventaire[4][0] = None
                    joueur.vie = joueur.vie_maximum

            # Parchemin d'attaque --------------------------------------------------------------------------------------
            elif joueur.inventaire[4][0].type == 6:

                attaque = Attaque(1)

                pos = sf.Mouse.get_position()
                pos.x = pos.x + self.decalage[0]
                pos.y = pos.y + self.decalage[1]

                if abs(pos.x - joueur.coord["x"]) >= abs(pos.y - joueur.coord["y"]):
                    if pos.x > joueur.coord["x"]:
                        attaque.deplacement = {"x": 1, "y": 0}
                    else:
                        attaque.deplacement = {"x": -1, "y": 0}
                else:
                    if pos.y > joueur.coord["y"]:
                        attaque.deplacement = {"x": 0, "y": 1}
                    else:
                        attaque.deplacement = {"x": 0, "y": -1}

                attaque.coord["x"] = joueur.coord["x"] + attaque.deplacement["x"]*BLOCSIZE
                attaque.coord["y"] = joueur.coord["y"] + attaque.deplacement["y"]*BLOCSIZE
                attaque.coord["w"] = BLOCSIZE
                attaque.coord["h"] = BLOCSIZE

                self.attaques.append(attaque)

                joueur.inventaire[4][0].carac["charges"] -= 1
                if joueur.inventaire[4][0].carac["charges"] <= 0:
                    joueur.inventaire[4][0] = None

            # Parchemin d'attaque de feu -------------------------------------------------------------------------------
            elif joueur.inventaire[4][0].type == 7 and len(joueur.actions) == 0:

                attaque = Attaque(2)

                position_souris = sf.Mouse.get_position(window)
                position_souris = [position_souris.x + self.decalage[0] - joueur.coord["x"] - 32,
                                   position_souris.y + self.decalage[1] - joueur.coord["y"] - 32]

                if position_souris[0] >= abs(position_souris[1]):
                    joueur.deplacement["x"], joueur.deplacement["y"] = 1, 0
                    attaque.deplacement["x"], attaque.deplacement["y"] = 1, 0

                elif -position_souris[0] >= abs(position_souris[1]):
                    joueur.deplacement["x"], joueur.deplacement["y"] = -1, 0
                    attaque.deplacement["x"], attaque.deplacement["y"] = -1, 0

                elif position_souris[1] > abs(position_souris[0]):
                    joueur.deplacement["x"], joueur.deplacement["y"] = 0, 1
                    attaque.deplacement["x"], attaque.deplacement["y"] = 0, 1

                else:
                    joueur.deplacement["x"], joueur.deplacement["y"] = 0, -1
                    attaque.deplacement["x"], attaque.deplacement["y"] = 0, -1

                attaque.coord["x"] = joueur.coord["x"] + attaque.deplacement["x"]*BLOCSIZE//2
                attaque.coord["y"] = joueur.coord["y"] + attaque.deplacement["y"]*BLOCSIZE//2
                attaque.coord["w"] = BLOCSIZE
                attaque.coord["h"] = BLOCSIZE

                self.attaques.append(attaque)
                joueur.actions.append({"type": 7, "frame": 0, "vitesse": joueur.vitesse_attaque})

            # Parchemin d'explosion ------------------------------------------------------------------------------------
            elif joueur.inventaire[4][0].type == 12:

                position_souris = sf.Mouse.get_position(window)
                position_souris = [position_souris.x + self.decalage[0] - joueur.coord["x"] - 32,
                                   position_souris.y + self.decalage[1] - joueur.coord["y"] - 32]

                if position_souris[0] >= abs(position_souris[1]):
                    joueur.deplacement["x"], joueur.deplacement["y"] = 1, 0
                elif -position_souris[0] >= abs(position_souris[1]):
                    joueur.deplacement["x"], joueur.deplacement["y"] = -1, 0
                elif position_souris[1] > abs(position_souris[0]):
                    joueur.deplacement["x"], joueur.deplacement["y"] = 0, 1
                else:
                    joueur.deplacement["x"], joueur.deplacement["y"] = 0, -1

                directions = [[0, 1], [0, -1], [1, 1], [1, 0], [1, -1], [-1, 1], [-1, 0], [-1, -1]]

                for d in directions:

                    attaque = Attaque(4)

                    attaque.coord["x"] = joueur.coord["x"] + d[0]*BLOCSIZE
                    attaque.coord["y"] = joueur.coord["y"] + d[1]*BLOCSIZE
                    attaque.coord["w"] = BLOCSIZE
                    attaque.coord["h"] = BLOCSIZE

                    self.attaques.append(attaque)

                joueur.inventaire[4][0].carac["charges"] -= 1
                if joueur.inventaire[4][0].carac["charges"] <= 0:
                    joueur.inventaire[4][0] = None

    def gerer_meubles(self, joueur, raccourcis, resolution, spawn):
        """
            Fonction qui affiche les meubles et affiche la description si le
            joueur intéragit avec.
        """

        for meuble in self.meubles:

            if meuble.collision((self.decalage[0], self.decalage[1], resolution["w"], resolution["h"])):

                # FAIRE INTERAGIR LE MEUBLE AVEC LE JOUEUR

                if not self.message["afficher"] and len(meuble.actions) == 0:
                    coord_collision = (joueur.coord["x"]+joueur.deplacement["x"]*BLOCSIZE,
                                       joueur.coord["y"]+joueur.deplacement["y"]*BLOCSIZE, BLOCSIZE, BLOCSIZE)
                    if meuble.collision(coord_collision) and sf.Keyboard.is_key_pressed(raccourcis["interagir"]):

                        # Déterminer si le meuble a une quête que le joueur doit faire
                        quete_effectuee = False
                        for quete in meuble.quetes:
                            if quete in joueur.quetes:
                                meuble.effectuer_quete(joueur, quete["histoire"], quete["quete"], self)
                                quete_effectuee = True

                        if not quete_effectuee:
                            meuble.utiliser(spawn)

                # EFFECTUER LES ACTIONS DU MEUBLE

                if len(meuble.actions) > 0 and not self.message["afficher"]:

                    # Faire avancer l'immobilisation du meuble
                    if meuble.actions[0]["type"] == 3:
                        meuble.actions[0]["frame"] += 1
                        if meuble.actions[0]["frame"] == meuble.actions[0]["vitesse"]:
                            del meuble.actions[0]

                    # Faire parler le meuble
                    elif meuble.actions[0]["type"] == 4 and not self.message["afficher"]:
                        taille_message = self.obtenir_taille_message(meuble.actions[0]["message"])
                        coord = (meuble.coord["x"]-(taille_message[0]-BLOCSIZE)//2, meuble.coord["y"]-taille_message[1])
                        self.creer_message(meuble.actions[0]["message"], coord[0], coord[1])
                        del meuble.actions[0]

                # AFFICHER LE MEUBLE

                sprite = sf.Sprite(MEUBLES, ((meuble.type % 10)*BLOCSIZE,
                                             (meuble.type//10)*BLOCSIZE,BLOCSIZE, BLOCSIZE))

                if meuble.type == 9 and len(meuble.actions) > 0:
                    if meuble.actions[0]["type"] == 2:
                        numero_sprite = int(meuble.actions[0]["frame"]//(meuble.actions[0]["vitesse"]/4))
                        sprite = sf.Sprite(AUTRES, (numero_sprite*BLOCSIZE, 0, BLOCSIZE, BLOCSIZE))

                sprite.position = (meuble.coord["x"], meuble.coord["y"])
                self.liste_rafraichir.append([sprite, 1])

        # DETRUIRE LES MEUBLES

        compteur = 0
        while compteur < len(self.meubles):

            if len(self.meubles[compteur].actions) > 0:
                if self.meubles[compteur].actions[0]["type"] in [2, 6]:

                    # Si c'est un bloc de glace qui fond
                    if self.meubles[compteur].type == 9 and self.meubles[compteur].actions[0]["type"] == 2:
                        if self.meubles[compteur].actions[0]["frame"] < self.meubles[compteur].actions[0]["vitesse"]:
                            self.meubles[compteur].actions[0]["frame"] += 1
                        else:
                            coord = (self.meubles[compteur].coord["x"] // BLOCSIZE,
                                     self.meubles[compteur].coord["y"] // BLOCSIZE)
                            self.carte_bool[coord] = TRAVERSABLE[self.blocs[coord]]
                            del self.meubles[compteur]
                            compteur -= 1

                    # Si c'est n'importe quel autre type de meuble
                    else:
                        coord = (self.meubles[compteur].coord["x"]//BLOCSIZE,
                                 self.meubles[compteur].coord["y"]//BLOCSIZE)
                        self.carte_bool[coord] = TRAVERSABLE[self.blocs[coord]]
                        del self.meubles[compteur]
                        compteur -= 1
            compteur += 1

    def gerer_places(self, joueur):
        """
            Fonction qui détecte si le joueur est en collision avec une place,
            déclenche la quête adéquate, et déclenche les effets liés à cette
            quête (dialogue, cinématique...)
        """

        # DETECTER S'IL FAUT LANCER UNE QUÊTE

        for place in self.places:
            if joueur.collision(place):
                for quete in place.quetes:
                    if quete in joueur.quetes:
                        place.effectuer_quete(joueur, quete["histoire"], quete["quete"], self)


def fin(window, resolution, joueur, chronometre, utilisateur, carte, spawn):

    carte.afficher(window, resolution, joueur, spawn)
    window.display()
    sf.sleep(sf.seconds(10))

    fenetres = [sf.Sprite(ERREURS, (0, 0, 329, 172)),
                sf.Sprite(ERREURS, (0, 172, 238, 133))]

    bouton_oui = [sf.Sprite(ERREURS, (329, 0, 83, 23)),
                  sf.Sprite(ERREURS, (329, 23, 83, 23)),
                  sf.Sprite(ERREURS, (329, 46, 83, 23))]

    bouton_non = [sf.Sprite(ERREURS, (412, 0, 83, 23)),
                  sf.Sprite(ERREURS, (412, 23, 83, 23)),
                  sf.Sprite(ERREURS, (412, 46, 83, 23))]

    bouton_ok = [sf.Sprite(ERREURS, (238, 172, 83, 23)),
                 sf.Sprite(ERREURS, (238, 195, 83, 23)),
                 sf.Sprite(ERREURS, (238, 218, 83, 23))]

    decalages = [(139, 138), (231, 138), (139, 99)]

    fenetre_affichee = 0
    continuer_fin = True
    while continuer_fin:

        # Afficher le jeu

        carte.afficher(window, resolution, joueur, spawn)

        # AFFICHER LES FENETRES D'ERREURS

        position_souris = sf.Mouse.get_position(window)

        if fenetre_affichee == 0:

            fenetres[0].position = (resolution["w"]//2 - 165, resolution["h"]//2 - 86)
            window.draw(fenetres[0])

            coord = (fenetres[0].position.x + decalages[0][0], fenetres[0].position.y + decalages[0][1])
            if coord[0] <= position_souris.x <= coord[0] + 83 and coord[1] <= position_souris.y <= coord[1] + 23:
                if sf.Mouse.is_button_pressed(sf.Mouse.LEFT):
                    bouton_oui[2].position = coord
                    window.draw(bouton_oui[2])
                else:
                    bouton_oui[1].position = coord
                    window.draw(bouton_oui[1])
            else:
                bouton_oui[0].position = coord
                window.draw(bouton_oui[0])

            coord = (fenetres[0].position.x + decalages[1][0], fenetres[0].position.y + decalages[1][1])
            if coord[0] <= position_souris.x <= coord[0] + 83 and coord[1] <= position_souris.y <= coord[1] + 23:
                if sf.Mouse.is_button_pressed(sf.Mouse.LEFT):
                    bouton_non[2].position = coord
                    window.draw(bouton_non[2])
                else:
                    bouton_non[1].position = coord
                    window.draw(bouton_non[1])
            else:
                bouton_non[0].position = coord
                window.draw(bouton_non[0])

        elif fenetre_affichee == 1:

            fenetres[1].position = (resolution["w"]//2 - 119, resolution["h"]//2 - 67)
            window.draw(fenetres[1])

            coord = (fenetres[1].position.x + decalages[2][0], fenetres[1].position.y + decalages[2][1])

            if coord[0] <= position_souris.x <= coord[0] + 83 and coord[1] <= position_souris.y <= coord[1] + 23:
                if sf.Mouse.is_button_pressed(sf.Mouse.LEFT):
                    bouton_ok[2].position = coord
                    window.draw(bouton_ok[2])
                else:
                    bouton_ok[1].position = coord
                    window.draw(bouton_ok[1])
            else:
                bouton_ok[0].position = coord
                window.draw(bouton_ok[0])

        # Rafraichir l'image

        menu.limiter_fps(chronometre)
        window.display()

        # TRAITER LES EVENEMENTS DE LA FENETRE

        for event in window.events:

            # Redimensioner l'écran
            if isinstance(event, sf.ResizeEvent):
                resolution["w"], resolution["h"] = event.width, event.height
                window.view.reset((0, 0, resolution["w"], resolution["h"]))

            # Clic
            elif isinstance(event, sf.MouseButtonEvent):
                if event.button == sf.Mouse.LEFT and event.released:
                    if fenetre_affichee == 0:

                        coord = (fenetres[0].position.x + decalages[0][0], fenetres[0].position.y + decalages[0][1])
                        if coord[0] <= position_souris.x <= coord[0] + 83 and \
                           coord[1] <= position_souris.y <= coord[1] + 23:
                            fenetre_affichee = 1

                        coord = (fenetres[0].position.x + decalages[1][0], fenetres[0].position.y + decalages[1][1])
                        if coord[0] <= position_souris.x <= coord[0] + 83 and \
                           coord[1] <= position_souris.y <= coord[1] + 23:
                            continuer_fin = False

                    elif fenetre_affichee == 1:

                        coord = (fenetres[1].position.x + decalages[2][0], fenetres[1].position.y + decalages[2][1])
                        if coord[0] <= position_souris.x <= coord[0] + 83 and \
                           coord[1] <= position_souris.y <= coord[1] + 23:
                            fenetre_affichee = 0

        # AFFICHER LE JEU

        carte.afficher_monstres()
        carte.afficher_pnj()
        carte.afficher_attaque()
        carte.ramasser_afficher_objets(joueur)
        carte.afficher_interface(joueur, resolution)
        carte.gerer_meubles(joueur, utilisateur.raccourcis, window, resolution, spawn)

    sf.sleep(sf.seconds(10))
