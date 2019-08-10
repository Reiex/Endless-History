# -*- coding:utf-8 -*

"""
    Fichier contenant toutes les classes et fonctions
    nécessaires à la création un objet fixe ou mobile et à la
    manipulation d'un objet fixe.
"""

from constantes import *
from xml.etree import ElementTree

# ----------------------------------------------------------------------------------------------------------------------
# ENTITE
# ----------------------------------------------------------------------------------------------------------------------

class Entite:
    """
        Classe servant de base pour tout ce qui est présent
        dans le jeu et qui n'est pas du décors sans interraction.
    """

    def __init__(self, x=0, y=0, w=BLOCSIZE, h=BLOCSIZE):
        """
            self.coord: Dictionnaire contenant les coordonnées de l'entite en
            pixels.
            self.sprites: Dictionnaire contenant tout les sprites de l'entite.
            self.actions: Liste de dictionnaires représentant chacun une action
            à traiter.
            self.quetes: Liste de dictionnaires indiquants quelles quêtes est
            lié à cet objet.
        """

        self.coord = {"x": x, "y": y, "w": w, "h": h}
        self.sprites = dict()

        self.actions = list()
        self.quetes = list()

    def collision(self, rect):
        """
            Fonction qui renvoie True s'il y a collision entre self et une
            seconde entité. La seconde entité peut soit être un objet hérité
            du type "Entite", soit être une liste ou un tuple contenant les
            4 coordonnées: x, y, w, h.
        """

        if isinstance(rect, list) or isinstance(rect, tuple):
            if self.coord["x"] >= rect[0] + rect[2] or \
                            rect[0] >= self.coord["x"] + self.coord["w"] or \
                            self.coord["y"] >= rect[1] + rect[3] or \
                            rect[1] >= self.coord["y"] + self.coord["h"]:
                return False
            else:
                return True
        elif "coord" in dir(rect):
            if self.coord["x"] >= rect.coord["x"] + rect.coord["w"] or \
                            rect.coord["x"] >= self.coord["x"] + self.coord["w"] or \
                            self.coord["y"] >= rect.coord["y"] + rect.coord["h"] or \
                            rect.coord["y"] >= self.coord["y"] + self.coord["h"]:
                return False
            else:
                return True

    def effectuer_quete(self, joueur, histoire, quete, carte):
        """
            Fonction qui charge une quête et effectue les actions auxquelles
            elle est liée, puis la retire de self.quetes
        """

        assert {"histoire": histoire, "quete": quete} in self.quetes

        for quete_joueur in joueur.quetes:
            if quete_joueur == {"histoire": histoire, "quete": quete}:
                quete_joueur["quete"] += 1

        for action_xml in ElementTree.parse("maps/quetes/"+str(histoire)+"-"+str(quete)+".xml").getroot().getchildren():
            action = None

            if action_xml.tag == "deplacement":
                action = {"type": 0, "direction": [int(action_xml.get("x")), int(action_xml.get("y"))]}
            elif action_xml.tag == "attaque_base":
                action = {"type": 1, "frame": 0, "vitesse": int(action_xml.get("vitesse"))}
            elif action_xml.tag == "mort":
                action = {"type": 2, "frame": 0, "vitesse": VITESSE_MORT}
            elif action_xml.tag == "immobilisation":
                action = {"type": 3, "frame": 0, "vitesse": int(action_xml.get("vitesse"))}
            elif action_xml.tag == "dialogue":
                action = {"type": 4, "message": action_xml.text}
            elif action_xml.tag == "donner_objet":
                joueur.ajouter_objet_inventaire(Objet(int(action_xml.get("type"))))
            elif action_xml.tag == "cinematique":
                action = {"type": 5, "nom": action_xml.get("nom")}
            elif action_xml.tag == "detruire":
                action = {"type": 6}
            elif action_xml.tag == "final":
                joueur.quete_finale = True

            if action is not None:
                if action_xml.get("joueur") == "True":
                    if action["type"] == 0:
                        carte.carte_bool[joueur.coord["x"]//BLOCSIZE, joueur.coord["y"]//BLOCSIZE] = True
                    joueur.actions.append(action)
                    self.actions.append({"type": 3, "frame": 0, "vitesse": 1})
                else:
                    if action["type"] == 0:
                        carte.carte_bool[self.coord["x"]//BLOCSIZE, self.coord["y"]//BLOCSIZE] = True
                    self.actions.append(action)
                    joueur.actions.append({"type": 3, "frame": 0, "vitesse": 1})


# ----------------------------------------------------------------------------------------------------------------------
# OBJET
# ----------------------------------------------------------------------------------------------------------------------

class Objet(Entite):
    """
        Classe représentant un objet, permettant de le créer et de le
        manipuler. Il y a plusieurs types d'objets, cette classe concerne
        ceux que le joueur peut ramasser (et qui vont donc soit dans
        l'inventaire, soit sont consommés immédiatement).
        Ces objets ne peuvent pas avoir de quêtes.
    """

    def __init__(self, type_objet):
        """
            self.type: Entier indiquant le type de l'objet.
            self.nom: Nom de l'objet (s'il peut aller dans l'inventaire).
            self.carac: Dictionnaire indiquant les caracteristiques que fait
            gagner l'objet au joueur s'il s'en equipe.
        """

        super(Objet, self).__init__()

        self.type = type_objet
        self.nom = CARAC_OBJETS[type_objet]["nom"]

        self.carac = {key: value for key, value in CARAC_OBJETS[type_objet].items() if key != "nom"}

        self.sprites = {"normal": sf.Sprite(OBJETS, ((self.type % 10)*BLOCSIZE, (self.type//10)*BLOCSIZE,
                                                     BLOCSIZE, BLOCSIZE))}

    def __str__(self):
        """
            Fonction permettant d'obtenir un texte descriptif de l'objet. Ce
            texte doit faire 8 lignes ou moins, de 37 caractères ou moins.
        """

        chaine = self.nom+"\n\n"
        for carac in self.carac.keys():

            if carac == "vitesse d'attaque":
                if self.carac[carac] < 0:
                    chaine += carac+": +"+str(-self.carac[carac])+"\n"
                elif self.carac[carac] > 0:
                    chaine += carac + ": "+str(-self.carac[carac])+"\n"
            elif carac == "charges":
                chaine += "charges restantes: " + str(self.carac[carac]) + "\n"
            elif carac == "vie":
                if self.carac[carac] > 0:
                    chaine += "vie: +" + str(self.carac[carac]/2) + "\n"
                elif self.carac[carac] < 0:
                    chaine += "vie: " + str(self.carac[carac]/2) + "\n"

            else:
                if self.carac[carac] > 0:
                    chaine += carac+": +"+str(self.carac[carac])+"\n"
                elif self.carac[carac] < 0:
                    chaine += carac+": "+str(self.carac[carac])+"\n"

        chaine = chaine[:-1]

        return chaine


# ----------------------------------------------------------------------------------------------------------------------
# MEUBLE
# ----------------------------------------------------------------------------------------------------------------------

class Meuble(Entite):
    """
        Classe représentant un meuble, permettant de le créer et de le
        manipuler. Un meuble est un objet faisant partie du décors et avec
        lequel le joueur peut interagir.
        Ces objets peuvent être assignés à des quêtes, et la quête est
        effectuée lorsque le joueur "parle" à l'objet, en utilisant la même
        touche que pour les PNJ.
    """

    def __init__(self, type_meuble):
        """
            self.type: Entier indiquant le type de meuble.
            self.description: Description qui sera affichée lorsque le joueur
            interagira avec le meuble.
        """

        super(Meuble, self).__init__()

        self.type = type_meuble
        self.description = str()

        self.charger()

    def charger(self):
        """
            Fonction qui charge les caractéristiques du meuble.
        """

        # Charger la description des meubles normaux

        if self.type in LISTE_MEUBLES_NORMAUX:
            with open("data/descriptions_meubles.txt") as fichier_descriptions:
                descriptions = fichier_descriptions.read().split("\n.")
                self.description = descriptions[self.type]

    def utiliser(self, spawn):
        """
            Fonction servant a définir ce qui se passe lorsque le joueur
            intéragit avec un meuble.
        """

        # Si c'est un meuble normal

        if self.type in LISTE_MEUBLES_NORMAUX:
            self.actions.append({"type": 4, "message": self.description})
            self.actions.append({"type": 3, "frame": 0, "vitesse": 60})

        # Si c'est un panneau

        elif self.type == 5:

            with open("data/descriptions_panneaux.txt", "r") as descriptions_panneaux:

                descriptions = descriptions_panneaux.read().split("\n.")
                descriptions = [description.split("\n") for description in descriptions]

                for description in descriptions:
                    coord = description[0].split(" ")
                    print((coord[0], int(coord[1]), int(coord[2])), (spawn["ID-map"], self.coord["x"], self.coord["y"]))
                    if (coord[0], int(coord[1]), int(coord[2])) == (spawn["ID-map"], self.coord["x"], self.coord["y"]):
                        self.description = "\n".join(description[1:])

            self.actions.append({"type": 4, "message": self.description})
            self.actions.append({"type": 3, "frame": 0, "vitesse": 60})