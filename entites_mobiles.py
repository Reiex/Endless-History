# -*- coding:utf-8 -*

"""
    Fichier contenant toutes les classes et fonctions
    nécessaires à la manipulation d'un PNJ, d'un joueur, d'une attaque,
    ou de toute entite capable de se déplacer.
"""

from entites import *
from copy import deepcopy
import menu


# ----------------------------------------------------------------------------------------------------------------------
# ENTITE MOBILE
# ----------------------------------------------------------------------------------------------------------------------

class EntiteMobile(Entite):
    """
        Classe servant de base pour toutes les entites qui se déplacent
        ou s'orientent dans le jeu, comme le joueur, les PNJ, ou les attaques.
    """

    def __init__(self):
        """
            self.deplacement: Dictionnaire indiquant dans quelle direction
            s'oriente l'entite.
            self.vitesse: Vitesse de déplacement en pixel/frame, cette vitesse
            doit être un entier.
        """

        super(EntiteMobile, self).__init__()

        self.deplacement = {"x": 0, "y": 1}
        self.vitesse = 0

    def deplacer(self):
        """
            Fonction qui permet de déplacer une entité à partir de self.actions
            et de self.deplacement.
            Si le déplacement est terminé, il est retiré de self.actions.
        """

        if len(self.actions) > 0:
            if self.actions[0]["type"] == 0:

                self.deplacement["x"], self.deplacement["y"] = self.actions[0]["direction"]

                # Si l'entité se tourne juste

                if 2 in [abs(self.deplacement["x"]), abs(self.deplacement["y"])]:
                    self.deplacement["x"] = self.deplacement["x"] // 2
                    self.deplacement["y"] = self.deplacement["y"] // 2
                    sf.sleep(sf.milliseconds(600-self.vitesse*10))
                    del self.actions[0]

                # Sinon elle se déplace

                else:

                    # Déterminer sur quel axe se déplace l'entité
                    if self.deplacement["x"] != 0:
                        axe = "x"
                    else:
                        axe = "y"
                    if self.deplacement[axe] > 0 and BLOCSIZE - (self.coord[axe] % BLOCSIZE) < self.vitesse:
                        self.coord[axe] += BLOCSIZE - (self.coord[axe] % BLOCSIZE)
                    elif self.deplacement[axe] < 0 != self.coord[axe] % BLOCSIZE < self.vitesse:
                        self.coord[axe] -= self.coord[axe] % BLOCSIZE
                    else:
                        self.coord[axe] += self.deplacement[axe] * self.vitesse

                    # Effacer le déplacement s'il est terminé
                    if self.coord[axe] % BLOCSIZE == 0:
                        del self.actions[0]


# ----------------------------------------------------------------------------------------------------------------------
# JOUEUR
# ----------------------------------------------------------------------------------------------------------------------

class Joueur(EntiteMobile):
    """
        Classe permettant de représenter un joueur, contenant toutes les
        variables propres à sa manipulation ainsi que certaines de ses
        fonctions. Le reste des fonctions permettant de manipuler un joueur
        se trouvent dans la classe Carte.
    """

    def __init__(self):
        """
            Variables privées:
                - self._vie: Le nom parle de lui même, c'est la vie actuelle
                du joueur.
                - self._invincible: Dictionnaire contenant une sf.Clock qui
                indique la dernière fois que le joueur a été mis en invincible et
                la durée en secondes de cette invincibilité.

            Variables publiques:
                - self.vie: C'est la vie actuelle du joueur.
                - self.vie_maximum: C'est la vie maximale du joueur.
                - self.invincible: Booléen valant True si le joueur est invincible
                et False s'il ne l'est pas.
                - self.duree_invincibilite: Durée en secondes de l'invincibilité
                du joueur.

                - self.armure: Réduction des dégats subits par le joueur.
                - self.vitesse_attaque: Temps en frames d'une attaque.

                - self.inventaire: Liste à deux dimensions représentant
                l'inventaire du joueur.
                - self.quete_finale: Indique si la quête finale a été déclenchée
        """

        super(Joueur, self).__init__()

        self._vie = 6
        self.vie_maximum = 6
        self._invincible = {"bool": False, "temps": sf.Clock(), "duree": 0}
        self.duree_invincibilite = 1

        self.armure = 0
        self.vitesse_attaque = 45

        self.inventaire = list()
        self.quete_finale = False

        self.charger()

    def charger(self):
        """
            Fonction qui définit les caractéristiques et charge les sprites du
            joueur.
        """

        # Charger les sprites du joueur

        self.sprites = dict()
        for d, direction in enumerate(DIRECTIONS):
            self.sprites[direction] = dict()
            for a, action in enumerate(ACTIONS_JOUEUR):
                self.sprites[direction][action] = sf.Sprite(JOUEUR, (d*BLOCSIZE, a*BLOCSIZE, BLOCSIZE, BLOCSIZE))

        # Définir les caractéristiques du joueur

        self.vitesse = 3
        self.quetes = []
        for i in range(10):
            self.quetes.append({"histoire": i, "quete": 0})

        # Créer l'inventaire du joueur

        self.inventaire = [[None, None, None, None, None, None, None, None, None, None],
                           [None, None, None, None, None, None, None, None, None, None],
                           [None, None, None, None, None, None, None, None, None, None],
                           [None, None, None, None, None, None, None, None, None, None],
                           [None],
                           [None, None, None, None]]

    def ouvrir_inventaire(self, window, resolution, raccourcis, chronometre):
        """
            Fonction qui ouvre l'inventaire du joueur, le modifie, et le fait
            intéragir avec l'utilisateur.
            Si le joueur quitte le programme, cette fonction retourne 1, sinon,
            elle retourne None.
        """

        # Retrouver les caracteristiques du joueur sans l'armure
        carac_sans_armure = {value: self.__getattribute__(key) for key, value in LISTE_CARAC.items()}
        for objet in self.inventaire[5]:
            if objet is not None:
                for nom_carac, carac in objet.carac.items():
                    carac_sans_armure[nom_carac] -= carac

        fond_inventaire = sf.Texture.from_image(window.capture())
        selectionne = None
        valeur_retournee = None
        continuer_inventaire = True

        # BOUCLE DE L'INVENTAIRE

        while continuer_inventaire:

            # ----------------------------------------------------------------------------------------------------------
            # CREER LE MENU
            # ----------------------------------------------------------------------------------------------------------

            inventaire = menu.Menu(fond_inventaire)
            ensemble = menu.Ensemble(sf.Texture.from_image(INTERFACE_IMAGE, (0, 100, 774, 460)))
            ensemble.coord = {"x": resolution["w"]//2-387, "y": resolution["h"]//2-230, "w": 774, "h": 460}

            # CREER LA FENÊTRE DE L'INVENTAIRE

            for l, ligne in enumerate(self.inventaire):
                for o, objet in enumerate(ligne):

                    # Coordonnées des cases normales de l'inventaire
                    if l < 4:
                        bouton = menu.Bouton("objet-"+str(l)+"-"+str(o))
                        bouton.coord["x"] = ensemble.coord["x"]+7+76*o
                        bouton.coord["y"] = ensemble.coord["y"]+149+l*76
                        bouton.coord["w"], bouton.coord["h"] = 76, 76

                    # Coordonnées de l'emplacement de l'objet en cours d'utilisation
                    elif l == 4:
                        bouton = menu.Bouton("util-"+str(l)+"-"+str(o))
                        bouton.coord["x"] = ensemble.coord["x"]+691
                        bouton.coord["y"] = ensemble.coord["y"]+71
                        bouton.coord["w"], bouton.coord["h"] = 76, 76

                    # Coordonnées des emplacements d'armures
                    else:
                        bouton = menu.Bouton("armure-"+str(l)+"-"+str(o))
                        bouton.coord["x"] = ensemble.coord["x"]+7+76*o
                        bouton.coord["y"] = ensemble.coord["y"]+71
                        bouton.coord["w"], bouton.coord["h"] = 76, 76

                    # Dessiner les sprites
                    sprites = [sf.Image.create(76, 76, sf.Color(255, 255, 255)),
                               sf.Image.create(76, 76, sf.Color(255, 255, 255))]
                    sprites[0].blit(INTERFACE_IMAGE, (0, 0), (0, 24, 76, 76))
                    sprites[1].blit(INTERFACE_IMAGE, (0, 0), (76, 24, 76, 76))
                    if objet is not None:
                        sprites[0].blit(OBJETS_IMAGE, (6, 6),
                                        ((objet.type % 10)*BLOCSIZE, (objet.type//10)*BLOCSIZE, BLOCSIZE, BLOCSIZE))
                        sprites[1].blit(OBJETS_IMAGE, (6, 6),
                                        ((objet.type % 10)*BLOCSIZE, (objet.type//10)*BLOCSIZE, BLOCSIZE, BLOCSIZE))
                    bouton.charger_sprites(sf.Texture.from_image(sprites[0]), sf.Texture.from_image(sprites[1]))

                    ensemble.ajouter_bouton(bouton)

            # CREER LA FENÊTRE DESCRIPTIVE DE L'OBJET SELECTIONNE

            if selectionne is not None:
                bouton = menu.Texte()

                # Créer l'image de la fenêtre descriptive
                chaines = str(selectionne).split("\n")
                taille = len(sorted(chaines, key=lambda x: -len(x))[0])*8+8
                fenetre = sf.Image.create(taille, len(chaines)*16+8, sf.Color(255, 255, 255))

                # Dessiner le texte
                for l, ligne in enumerate(chaines):
                    for c, caractere in enumerate(ligne):
                        coord = ((ord(caractere) % 10)*8, (ord(caractere)//10)*16, 8, 16)
                        fenetre.blit(ASCII_MESSAGE, (c*8+(taille-len(ligne)*8)//2, l*16+4), coord)

                # Ajouter le texte au menu
                bouton.coord = {"x": resolution["w"]//2-75+(300-taille)//2,
                                "y": resolution["h"]//2-223+(140-len(chaines)*16-8)//2,
                                "w": taille, "h": len(chaines)*16+8}
                bouton.charger_sprites(sf.Texture.from_image(fenetre))
                ensemble.ajouter_bouton(bouton)

            # LANCER LE MENU

            inventaire.ajouter_ensemble(ensemble)
            sortie = inventaire.lancer(window, resolution, chronometre, raccourcis["inventaire"])

            # ----------------------------------------------------------------------------------------------------------
            # ANALYSER LA SORTIE DU MENU
            # ----------------------------------------------------------------------------------------------------------

            if isinstance(sortie, dict):
                # Obtenir la case cliquée
                case = [int(coord) for coord in sortie["choix"].split("-")[1:]]

                # Echanger l'objet selectionné avec la case ciblée
                if selectionne is not None:
                    if case[0] < 4 or (case[0] == 4 and selectionne.type in LISTE_UTIL) or \
                            (case[0] == 5 and case[1] == 0 and selectionne.type in LISTE_CASQUES) or \
                            (case[0] == 5 and case[1] == 1 and selectionne.type in LISTE_PLASTRONS) or \
                            (case[0] == 5 and case[1] == 2 and selectionne.type in LISTE_JAMBIERES) or \
                            (case[0] == 5 and case[1] == 3 and selectionne.type in LISTE_BOTTES):
                        selectionne, self.inventaire[case[0]][case[1]] = self.inventaire[case[0]][case[1]], selectionne
                else:
                    selectionne, self.inventaire[case[0]][case[1]] = self.inventaire[case[0]][case[1]], selectionne

            elif sortie is None:
                valeur_retournee = 1
                continuer_inventaire = False
            elif sortie == 1:
                continuer_inventaire = False

        # TRAITEMENTS A LA SORTIE DE L'INVENTAIRE

        # Remettre l'objet selectionné dans l'inventaire s'il y en a un
        if selectionne is not None:
            for l, ligne in enumerate(self.inventaire):
                for c, case in enumerate(ligne):
                    if case is None:
                        self.inventaire[l][c] = selectionne
                        selectionne = None

        # Calculer les nouvelles caracteristiques du joueur
        for objet in self.inventaire[5]:
            if objet is not None:
                for nom_carac, carac in objet.carac.items():
                    carac_sans_armure[nom_carac] += carac

        # Mettre ces caracteristiques au joueur
        liste_attributs = {v: k for k, v in LISTE_CARAC.items()}
        for nom_carac, carac in carac_sans_armure.items():
            if nom_carac == "vie" and self.vie > carac:
                self.vie = carac
            self.__setattr__(liste_attributs[nom_carac], carac)

        return valeur_retournee

    def ouvrir_map(self, window, resolution, raccourcis, chronometre, spawn):
        """
            Fonction qui ouvre la map. Si le joueur quitte le programme,
            cette fonction retourne 1, sinon, elle retourne None.
        """

        # Calculer le zoom

        taille_map = (MAP.size.x, MAP.size.y)
        min_zoom = max(resolution["w"]/taille_map[0], resolution["h"]/taille_map[1])
        max_zoom = 3*min_zoom
        zoom = min_zoom

        # Calculer l'emplacement du joueur sur la carte

        if spawn["ID-map"] in INFO_MAP.keys():
            ajustable = INFO_MAP[spawn["ID-map"]]["ajustable"]
            coin = INFO_MAP[spawn["ID-map"]]["coin"]
        else:
            ajustable = False
            coin = (0, 0)
        tempo = 0
        tete = sf.Sprite(INTERFACE, (408, 0, 32, 32))

        # Calculer la position de la carte sur l'ecran

        if ajustable:
            position = [resolution["w"]/2 - self.coord["x"]*4.5*zoom/BLOCSIZE - coin[0]*zoom,
                        resolution["h"]/2 - self.coord["y"]*4.5*zoom/BLOCSIZE - coin[1]*zoom]
        else:
            position = [resolution["w"]/2 - coin[0]*zoom,
                        resolution["h"]/2 - coin[1]*zoom]

        map = sf.Sprite(MAP)
        map.ratio = (zoom, zoom)
        map.position = position

        # BOUCLE DE LA MAP

        position_souris = sf.Mouse.get_position()
        continuer = True
        while continuer:

            # Corriger la position de la map si nécessaire

            if position[0] >= 0:
                position[0] = 0
            elif position[0] + taille_map[0]*zoom <= resolution["w"]:
                position[0] = resolution["w"] - taille_map[0]*zoom
            if position[1] >= 0:
                position[1] = 0
            elif position[1] + taille_map[1]*zoom <= resolution["h"]:
                position[1] = resolution["h"] - taille_map[1]*zoom
            map.position = position

            # Dessiner la map et l'indicateur de la position du joueur

            window.clear(sf.Color(255, 255, 255))
            window.draw(map)

            tempo = (tempo + 1) % 60
            if tempo < 30:
                if ajustable:
                    tete.position = (coin[0]*zoom + position[0] + self.coord["x"]*4.5*zoom/BLOCSIZE - 16,
                                     coin[1]*zoom + position[1] + self.coord["y"]*4.5*zoom/BLOCSIZE - 16)
                else:
                    tete.position = (coin[0]*zoom + position[0] - 16, coin[1]*zoom + position[1] - 16)
                window.draw(tete)

            window.display()
            menu.limiter_fps(chronometre)

            # GESTION DES EVENEMENTS

            for event in window.events:

                # Redimensionner l'ecran
                if isinstance(event, sf.ResizeEvent):
                    resolution["w"], resolution["h"] = event.width, event.height
                    window.view.reset((0, 0, resolution["w"], resolution["h"]))

                    min_zoom = max(resolution["w"]/taille_map[0], resolution["h"]/taille_map[1])
                    max_zoom = 3*min_zoom

                    if zoom <= min_zoom:
                        zoom = min_zoom
                    elif zoom >= max_zoom:
                        zoom = max_zoom
                    map.ratio = (zoom, zoom)

                # Quitter le programme
                if isinstance(event, sf.CloseEvent):
                    return 1

                # Quitter le menu
                if isinstance(event, sf.KeyEvent):
                    if event.released and event.code == raccourcis["map"]:
                        return None

                # Déplacer la souris
                if isinstance(event, sf.MouseMoveEvent):
                    if sf.Mouse.is_button_pressed(sf.Mouse.LEFT):
                        position[0] += (event.position[0] - position_souris[0])*1.5
                        position[1] += (event.position[1] - position_souris[1])*1.5

                    position_souris = event.position

                # Utiliser la roue de la souris
                if isinstance(event, sf.MouseWheelEvent):

                    z = zoom

                    zoom *= (1 + event.delta/10)
                    zoom = max(min_zoom, zoom)
                    zoom = min(max_zoom, zoom)
                    map.ratio = (zoom, zoom)

                    position[0] = resolution["w"]/2 - (zoom/z)*(resolution["w"]/2 - position[0])
                    position[1] = resolution["h"]/2 - (zoom/z)*(resolution["h"]/2 - position[1])
                    map.position = position

    def ajouter_objet_inventaire(self, objet_a_placer):
        """
            Fonction qui cherche une case vide dans l'inventaire pour y placer
            un objet. S'il n'y a pas de case vide, l'objet sera placé en
            derniere position, effaçant par la même occasion l'objet qui s'y
            trouvait.
        """

        objet_donne = False
        for l, ligne in enumerate(self.inventaire[:4]):
            for o, objet in enumerate(ligne):
                if objet is None and not objet_donne:
                    self.inventaire[l][o] = objet_a_placer
                    objet_donne = True
                if l == 4 and o == 9 and not objet_donne:
                    self.inventaire[l][o] = objet_a_placer
                    objet_donne = True

    @property
    def invincible(self):
        """
            Fonction getter de self.invincible:
            En fonction de self._invincible, elle détermine si le joueur est
            invincible ou non, puis retourne True si c'est le cas, sinon False.
        """
        return self._invincible["temps"].elapsed_time.seconds < self._invincible["duree"]

    @invincible.setter
    def invincible(self, valeur):
        """
            Fonction setter de self.invincible:
            Elle déclenche ou annule l'invincibilité. Si elle la déclenche,
            la durée de l'invincibilité vaut self.duree_invincibilite
        """
        if valeur:
            self._invincible["duree"] = self.duree_invincibilite
            self._invincible["temps"].restart()
        else:
            self._invincible["duree"] = self._invincible["temps"].elapsed_time.seconds-1

    @property
    def vie(self):
        """
            Fonction sans grand intérêt, retourne la vie actuelle du joueur,
            cette fonction est néanmoins nécéssaire à l'encapsulation de self.vie.
        """
        return self._vie

    @vie.setter
    def vie(self, valeur):
        """
            Fonction setter de self.vie:
            La nouvelle valeur peut déclencher l'invincibilité.
            Elle peut également être modifié si elle est plus haute
            que self.vie_maximum, voir être annulée si le joueur est
            invincible.
        """

        if valeur < self._vie:
            if not self.invincible:
                self._vie = valeur
                self.invincible = True
                if self._vie < 0:
                    self.vie = 0
        elif valeur > self.vie_maximum:
            self._vie = self.vie_maximum
        else:
            self._vie = valeur


# ----------------------------------------------------------------------------------------------------------------------
# MONSTRE
# ----------------------------------------------------------------------------------------------------------------------

class Monstre(EntiteMobile):
    """
        Classe permettant de représenter un monstre, contenant toutes les
        variables propres à sa manipulation ainsi que certaines de ses
        fonctions. Le reste des fonctions permettant de manipuler un monstre
        se trouvent dans la classe Carte.
    """

    def __init__(self, type_monstre):
        """
            self.type: Type de monstre, la liste se trouve dans /types/Monstres.txt.
            self.actif: Booléen indiquant si le monstre est dans l'écran ou non.
            self.mort: Booléen indiquant si le monstre est mort ou non.

            self.vitesse_attaque: Temps en frames d'une attaque.
            self.attaque: Points de vies infligés au joueur à chaque coup de ce
            monstre.
            self.data: Dictionnaire permettant de stocker des données supplémentaires si
            nécessaire
        """

        super(Monstre, self).__init__()

        self.type = type_monstre
        self.actif = False
        self.mort = False

        self.vitesse_attaque = 0
        self.attaque = 0

        self.data = {}

        self.charger()

    def charger(self):
        """
            Fonction qui charge tout les sprites du monstre dans self.sprites
            et qui définit les caractéristiques du monstre.
        """

        # Charger les sprites du monstre

        self.sprites = dict()
        for d, direction in enumerate(DIRECTIONS):
            self.sprites[direction] = dict()
            for a, action in enumerate(ACTIONS):
                self.sprites[direction][action] = sf.Sprite(MONSTRES, ((d+len(DIRECTIONS)*self.type)*BLOCSIZE,
                                                                       a*BLOCSIZE, BLOCSIZE, BLOCSIZE))

        # Définir les caractéristiques du monstre

        self.attaque = CARAC_MONSTRES[self.type]["attaque"]
        self.vitesse = CARAC_MONSTRES[self.type]["vitesse"]
        self.vitesse_attaque = CARAC_MONSTRES[self.type]["vitesse_attaque"]

        # Initialiser quelques données supplémentaires si nécéssaire

        if self.type == 3:
            self.data["prochaine_attaque"] = 0  # 0 pour un projectile, 1 pour une explosion

    def trouver_trajectoire(self, cible, graph):
        """
            Cette fonction prend en arguments la cible, sous forme de
            coordonnees [x, y] du graph et le graph ne contenant que des
            booléens: True si le noeud est traversable, sinon False.

            Fonction qui execute un algorithme A* afin de déterminer une
            trajectoire permettant au monstre d'aller au joueur, retourne
            la liste de noeuds par lesquels le monstre doit passer.

            Si aucun chemin n'est trouvé après un certain nombre de noeuds,
            la fonction retourne la dernière trajectoire explorée.
        """

        # Initialisation de l'algorithme

        graph[cible[0]][cible[1]] = True
        noeud_actuel = {"x": self.coord["x"]//64, "y": self.coord["y"]//64, "parent": None}
        noeud_actuel["valeur"] = ((cible[0]-noeud_actuel["x"])**2+(cible[1]-noeud_actuel["y"])**2)**(1/2)
        noeuds_possibles = [noeud_actuel]
        noeuds_explores = list()
        compteur = 0

        # ALGORITHME A*:

        while len(noeuds_possibles) > 0 and (noeud_actuel["x"] != cible[0] or noeud_actuel["y"] != cible[1]) and \
                compteur < 40:

            # Sortir de la liste le noeud le plus interessant
            noeuds_possibles = sorted(noeuds_possibles, key=lambda noeud: -noeud["valeur"])
            noeud_actuel = noeuds_possibles.pop()

            noeuds_explores.append((noeud_actuel["x"], noeud_actuel["y"]))

            # Trouver les noeuds voisins du noeud actuel
            noeuds_voisins = [{"x": noeud_actuel["x"]+1, "y": noeud_actuel["y"]},
                              {"x": noeud_actuel["x"]-1, "y": noeud_actuel["y"]},
                              {"x": noeud_actuel["x"], "y": noeud_actuel["y"]+1},
                              {"x": noeud_actuel["x"], "y": noeud_actuel["y"]-1}]

            # Trier les noeuds voisins pour n'obtenir que les noeuds interessants

            coord_possibles = [(noeud["x"], noeud["y"]) for noeud in noeuds_possibles]
            for noeud in noeuds_voisins:
                coord = (noeud["x"], noeud["y"])
                if coord not in noeuds_explores and coord not in coord_possibles and graph[noeud["x"]][noeud["y"]]:
                    noeud["valeur"] = ((cible[0]-noeud["x"])**2+(cible[1]-noeud["y"])**2)**(1/2)
                    noeud["parent"] = deepcopy(noeud_actuel)
                    noeuds_possibles.append(noeud)

            compteur += 1

        # EXPLOITATION DES RESULTATS

        liste_points = list()
        while noeud_actuel["parent"] is not None:
            liste_points.append([noeud_actuel["x"], noeud_actuel["y"]])
            noeud_actuel = noeud_actuel["parent"]
        liste_points.reverse()
        return liste_points


# ----------------------------------------------------------------------------------------------------------------------
# PNJ
# ----------------------------------------------------------------------------------------------------------------------

class Pnj(EntiteMobile):
    """
        Classe permettant de représenter un PNJ, de le manipuler, de
        l'afficher...
    """

    def __init__(self, type_pnj):
        """
            self.repliques: Liste de chaines de caractères que le PNJ dira à
            chaque fois que le joueur interagira avec lui.
            self.trajectoire: Liste de listes à deux coordonnées x et y qui
            indiquent l'orientation ou le déplacement du PNJ: Si les valeurs
            sont -1 ou 1, c'est le déplacement qui est définie, si les valeurs
            sont -2 ou 2, c'est l'orientation.
            self.index_trajectoire: Entier indiquant quelle est le dernier
            déplacement effectué sur la trajectoire du PNJ.

            self.type: Type de PNJ, sert à connaître son apparence et ses
            répliques.
            self.actif: Booléen indiquant si le PNJ est actif ou non.
        """

        super(Pnj, self).__init__()

        self.repliques = list()
        self.trajectoire = [[0, 2]]
        self.index_trajectoire = 0

        self.type = type_pnj
        self.actif = False

        self.charger()

    def charger(self):
        """
            Méthode qui charge les sprite et initialise les caractéristiques
            du PNJ.
        """

        # Charger les sprites du PNJ

        marge = len(DIRECTIONS)*self.type
        self.sprites = dict()
        for d, direction in enumerate(DIRECTIONS):
            self.sprites[direction] = dict()
            for a, action in enumerate(ACTIONS):
                self.sprites[direction][action] = sf.Sprite(PNJS, ((d+marge)*BLOCSIZE, a*BLOCSIZE, BLOCSIZE, BLOCSIZE))

        # Obtenir les répliques du PNJ

        with open("data/pnjs/repliques"+str(self.type)+".txt") as repliques_pnj:
            self.repliques = repliques_pnj.read().split("\n.")

        # Obtenir la trajectoire du PNJ

        with open("data/pnjs/trajectoire"+str(self.type)+".txt") as trajectoire_pnj:
            self.trajectoire = [etape.split(" ") for etape in trajectoire_pnj.read().split("\n")]
            self.trajectoire = [[int(coord) for coord in etape] for etape in self.trajectoire]

        self.vitesse = VITESSES_PNJS[self.type]


# ----------------------------------------------------------------------------------------------------------------------
# ATTAQUE
# ----------------------------------------------------------------------------------------------------------------------

class Attaque(EntiteMobile):
    """
        Classe représentant une attaque dans le jeu
        On a basiquement deux types d'attaques: les simples projectiles et les autres.
        Les simples projectiles ont tous le même comportement à peu de détails près, seuls
        les sprites, les dégats, et les possibilités de traverser les murs et/ou entités
        changent.
    """

    def __init__(self, type_attaque):
        """
            self.type: Evident

            self.active: Détermine si l'attaque est dans l'ecran
            self.detruite: Détermine si l'attaque est détruite où non

            self.degats: Dégats que subit le personnage s'il entre en collision avec l'attaque
        """

        super(Attaque, self).__init__()

        self.type = type_attaque

        self.active = False
        self.detruite = False

        self.degats = 0

        self.charger()

    def charger(self):
        """
            Fonction qui charge les sprites et données de l'attaque à partir de son type
        """

        self.degats = CARAC_ATTAQUES[self.type][0]
        self.vitesse = CARAC_ATTAQUES[self.type][1]

        # Simples projectiles

        if self.type in ATTAQUES_PROJECTILES:

            self.coord["w"] = BLOCSIZE
            self.coord["h"] = BLOCSIZE

            for d, direction in enumerate(DIRECTIONS):
                self.sprites[direction] = dict()
                for a, action in enumerate(ACTIONS_PROJECTILES):
                    self.sprites[direction][action] = sf.Sprite(PROJECTILES, ((d+len(DIRECTIONS)*self.type)*BLOCSIZE,
                                                                              a*BLOCSIZE, BLOCSIZE, BLOCSIZE))

        # Attaque de feu

        elif self.type == 2:

            self.coord["w"] = BLOCSIZE
            self.coord["h"] = BLOCSIZE

            for d, direction in enumerate(DIRECTIONS):
                self.sprites[direction] = dict()
                for a, action in enumerate(["clavier0", "clavier1", "clavier2"]):
                    self.sprites[direction][action] = sf.Sprite(ATTAQUES, ((d+4)*BLOCSIZE, a*BLOCSIZE,
                                                                           BLOCSIZE, BLOCSIZE))

        # Explosions du monstre à distance bleu

        elif self.type == 3:

            self.coord["w"] = BLOCSIZE
            self.coord["h"] = BLOCSIZE

            for a, action in enumerate(["explosion0", "explosion1", "explosion2", "explosion3"]):
                self.sprites[action] = sf.Sprite(ATTAQUES, (a*BLOCSIZE, 3*BLOCSIZE, BLOCSIZE, BLOCSIZE))

        # Explosions parchemin joueur

        elif self.type == 4:

            self.coord["w"] = BLOCSIZE
            self.coord["h"] = BLOCSIZE

            for a, action in enumerate(["explosion0", "explosion1", "explosion2", "explosion3"]):
                self.sprites[action] = sf.Sprite(ATTAQUES, (a*BLOCSIZE, 4*BLOCSIZE, BLOCSIZE, BLOCSIZE))
