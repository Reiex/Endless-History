# -*- coding:utf-8 -*

"""
    Fichier contenant toutes les classes et fonctions nécessaires à la
    manipulation des données de l'utilisateur.
"""

from carte import *
from pickle import Pickler, Unpickler
from os import getcwd, listdir


class Utilisateur:
    """
        Classe représentant un utilisateur, contenant toutes ses données
        (progression dans le jeu, nom, options...) et permettant de les
        manipuler (sauvegarde, modification des raccourcis clavier...).
    """

    def __init__(self):
        """
            self.raccourcis: Dictionnaire avec pour clés le nom de raccourcis et
            pour valeur le bouton du clavier assigné a ce raccourcis.

            self.sauvegarde_utilisable: Booléen indiquant si la progression du
            joueur est enregistrée et disponnible a l'utilisation.
            self.sauvegarde: Dictionnaire contenant toutes les données à
            sauvegarder.
        """

        self.raccourcis = dict()

        self.utiliser_sauvegarde = False
        self.sauvegarde_utilisable = False
        self.sauvegarde = dict()

        self.charger_donnees()

    def charger_donnees(self):
        """
            Méthode appelée à la création de l'utilisateur, permettant de
            charger toutes les données sauvegardées, ou de les créer si le
            joueur n'a aucune données sauvegardées.
        """

        # CHARGER LES DONNEES

        if "save.elh" in listdir(getcwd()):

            with open("save.elh", "rb") as fichier_sauvegarde:
                unpickler = Unpickler(fichier_sauvegarde)
                utilisateur_sauvegarde = unpickler.load()
                for key, value in utilisateur_sauvegarde.__dict__.items():
                    self.__setattr__(key, value)

        # CREER LES DONNEES

        else:

            self.raccourcis["deplacer-haut"] = sf.Keyboard.Z
            self.raccourcis["deplacer-bas"] = sf.Keyboard.S
            self.raccourcis["deplacer-droite"] = sf.Keyboard.D
            self.raccourcis["deplacer-gauche"] = sf.Keyboard.Q
            self.raccourcis["menu"] = sf.Keyboard.ESCAPE
            self.raccourcis["interagir"] = sf.Keyboard.E
            self.raccourcis["inventaire"] = sf.Keyboard.SPACE
            self.raccourcis["map"] = sf.Keyboard.M

            self.sauvegarde_utilisable = False
            self.sauvegarde = dict()

    def sauvegarder_partie(self, carte, joueur, spawn):
        """
            Fonction qui place les données de l'utilisateur dans self.sauvegarde
            et active l'utilisation de la sauvegarde.
        """

        self.sauvegarde_utilisable = True
        types_python_sauvegardables = [int, float, str, bool]

        def explorer(item):
            """
                Fonction qui, par recursivité, inspecte un élément et renvoie
                une version de cet élément ne contenant que des valeurs
                sauvegardables. Les valeurs qui ne peuvent pas être sauvegardées
                sont remplacées par None
            """

            if type(item) in types_python_sauvegardables:
                return item
            elif type(item) in (tuple, list):
                item_copy = list()
                for other_item in item:
                    item_copy.append(explorer(other_item))
                return item_copy
            elif isinstance(item, dict):
                item_copy = dict()
                for cle, valeur in item.items():
                    item_copy[cle] = explorer(valeur)
                return item_copy
            elif isinstance(item, ndarray):
                return item.tolist()
            else:
                return None

        # Placer les données du joueur
        self.sauvegarde["joueur"] = dict()
        for key, value in joueur.__dict__.items():
            if key == "inventaire":
                self.sauvegarde["joueur"]["inventaire"] = list()
                for l, ligne in enumerate(value):
                    self.sauvegarde["joueur"]["inventaire"].append(list())
                    for o, objet in enumerate(ligne):
                        self.sauvegarde["joueur"]["inventaire"][l].append(dict())
                        if objet is None:
                            self.sauvegarde["joueur"]["inventaire"][l][o] = None
                        else:
                            for cle, valeur in objet.__dict__.items():
                                if explorer(valeur) is not None:
                                    self.sauvegarde["joueur"]["inventaire"][l][o][cle] = explorer(valeur)
            elif explorer(value) is not None:
                self.sauvegarde["joueur"][key] = explorer(value)

        # Placer les données de la carte
        self.sauvegarde["carte"] = dict()
        for key, value in carte.__dict__.items():
            if explorer(value) is not None:
                self.sauvegarde["carte"][key] = explorer(value)

        # Placer les données des monstres
        self.sauvegarde["monstres"] = list()
        for m, monstre in enumerate(carte.monstres):
            self.sauvegarde["monstres"].append(dict())
            for key, value in monstre.__dict__.items():
                if explorer(value) is not None:
                    self.sauvegarde["monstres"][m][key] = explorer(value)

        # Placer les données des pnjs
        self.sauvegarde["pnjs"] = list()
        for p, pnj in enumerate(carte.pnjs):
            self.sauvegarde["pnjs"].append(dict())
            for key, value in pnj.__dict__.items():
                if explorer(value) is not None:
                    self.sauvegarde["pnjs"][p][key] = explorer(value)

        # Placer les données des objets
        self.sauvegarde["objets"] = list()
        for o, objet in enumerate(carte.objets):
            self.sauvegarde["objets"].append(dict())
            for key, value in objet.__dict__.items():
                if explorer(value) is not None:
                    self.sauvegarde["objets"][o][key] = explorer(value)

        # Placer les données des meubles
        self.sauvegarde["meubles"] = list()
        for m, meuble in enumerate(carte.meubles):
            self.sauvegarde["meubles"].append(dict())
            for key, value in meuble.__dict__.items():
                if explorer(value) is not None:
                    self.sauvegarde["meubles"][m][key] = explorer(value)

        # Placer les données des attaques
        self.sauvegarde["attaques"] = list()
        for a, attaque in enumerate(carte.attaques):
            self.sauvegarde["attaques"].append(dict())
            for key, value in attaque.__dict__.items():
                if explorer(value) is not None:
                    self.sauvegarde["attaques"][a][key] = explorer(value)

        # Placer les données des places
        self.sauvegarde["places"] = list()
        for p, place in enumerate(carte.places):
            self.sauvegarde["places"].append(dict())
            for key, value in place.__dict__.items():
                if explorer(value) is not None:
                    self.sauvegarde["places"][p][key] = explorer(value)

        # Placer le spawn
        self.sauvegarde["spawn"] = spawn

    def recuperer_donnees_sauvegarde(self):
        """
            Fonction qui, à partir de self.sauvegarde, renvoie un objet de la
            classe Carte et un objet de la classe Joueur contenant les données
            sauvegardées.
        """

        def remplacer_valeur(valeur_remplacee, valeur_sauvegardee):
            """
                Fonction qui à partir d'une valeur sauvegardée complète une
                valeur à remplacer.
            """

            if isinstance(valeur_sauvegardee, type(valeur_remplacee)):
                if isinstance(valeur_sauvegardee, list):
                    valeur_retournee = list()
                    for v, valeur in enumerate(valeur_sauvegardee):
                        valeur_retournee.append(valeur)
                        if v < len(valeur_remplacee):
                            if valeur is None:
                                valeur_retournee[v] = valeur_remplacee[v]
                            else:
                                valeur_retournee[v] = remplacer_valeur(valeur_remplacee[v], valeur)
                    return valeur_retournee
                elif isinstance(valeur_sauvegardee, dict):
                    valeur_retournee = dict()
                    for cle, valeur in valeur_sauvegardee.items():
                        valeur_retournee[cle] = valeur
                        if cle in valeur_remplacee.keys():
                            if valeur is None:
                                valeur_retournee[cle] = valeur_remplacee[cle]
                            else:
                                valeur_retournee[cle] = remplacer_valeur(valeur_remplacee[cle], valeur)
                    return valeur_retournee
                else:
                    return valeur_sauvegardee
            else:
                return valeur_sauvegardee

        # Récuperer les données du joueur
        joueur = Joueur()
        for key, value in self.sauvegarde["joueur"].items():
            if key == "inventaire":
                for l, ligne in enumerate(value):
                    for o, objet in enumerate(ligne):
                        if objet is None:
                            joueur.inventaire[l][o] = None
                        else:
                            obj = Objet(objet["type"])
                            for cle, valeur in objet.items():
                                obj.__setattr__(cle, remplacer_valeur(obj.__getattribute__(cle), valeur))
                            joueur.inventaire[l][o] = obj
            else:
                joueur.__setattr__(key, remplacer_valeur(joueur.__getattribute__(key), value))

        # Récuperer les données de la carte
        carte = Carte()
        for key, value in self.sauvegarde["carte"].items():
            carte.__setattr__(key, remplacer_valeur(carte.__getattribute__(key), value))

        blocs = ndarray(list(), uint16)
        carte_bool = ndarray(list(), bool)
        blocs.resize(carte.taille)
        carte_bool.resize(carte.taille)
        for x in range(carte.taille[0]):
            for y in range(carte.taille[1]):
                blocs[x, y] = carte.blocs[x][y]
                carte_bool[x, y] = carte.carte_bool[x][y]
        carte.blocs = blocs
        carte.carte_bool = carte_bool

        carte.textures = ndarray(list(), sf.RenderTexture)
        carte.dessiner_blocs_textures()

        # Récuperer les données des monstres
        carte.monstres = list()
        for donnees_monstre in self.sauvegarde["monstres"]:
            monstre = Monstre(donnees_monstre["type"])
            for key, value in donnees_monstre.items():
                monstre.__setattr__(key, remplacer_valeur(monstre.__getattribute__(key), value))
            carte.monstres.append(monstre)

        # Récuperer les données des pnjs
        carte.pnjs = list()
        for donnees_pnj in self.sauvegarde["pnjs"]:
            pnj = Pnj(donnees_pnj["type"])
            for key, value in donnees_pnj.items():
                pnj.__setattr__(key, remplacer_valeur(pnj.__getattribute__(key), value))
            carte.pnjs.append(pnj)

        # Récuperer les données des objets
        carte.objets = list()
        for donnees_objet in self.sauvegarde["objets"]:
            objet = Objet(donnees_objet["type"])
            for key, value in donnees_objet.items():
                objet.__setattr__(key, remplacer_valeur(objet.__getattribute__(key), value))
            carte.objets.append(objet)

        # Récuperer les données des meubles
        carte.meubles = list()
        for donnees_meuble in self.sauvegarde["meubles"]:
            meuble = Meuble(donnees_meuble["type"])
            for key, value in donnees_meuble.items():
                meuble.__setattr__(key, remplacer_valeur(meuble.__getattribute__(key), value))
            carte.meubles.append(meuble)

        # Récuperer les données des attaques
        carte.attaques = list()
        for donnees_attaques in self.sauvegarde["attaques"]:
            attaque = Attaque(donnees_attaques["type"])
            for key, value in donnees_attaques.items():
                attaque.__setattr__(key, remplacer_valeur(attaque.__getattribute__(key), value))
            carte.attaques.append(attaque)

        # Récuperer les données des places
        carte.places = list()
        for donnees_place in self.sauvegarde["places"]:
            place = Entite()
            for key, value in donnees_place.items():
                place.__setattr__(key, remplacer_valeur(place.__getattribute__(key), value))
            carte.places.append(place)

        return joueur, carte, self.sauvegarde["spawn"]

    def enregistrer(self):
        """
            Fonction qui enregistre toutes les données de l'utilisateur dans
            un fichier save.elh
        """

        with open("save.elh", "wb") as fichier_sauvegarde:
            pickler = Pickler(fichier_sauvegarde)
            pickler.dump(self)
