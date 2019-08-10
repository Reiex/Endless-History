# -*- coding:utf-8 -*

"""
    Fichier contenant toutes les classes et fonctions nécessaires à la création
    et manipulation de menus.
"""

import sfml as sf
from re import search


# ----------------------------------------------------------------------------------------------------------------------
# DEFINITIONS DE CONSTANTES
# ----------------------------------------------------------------------------------------------------------------------

# Chargement d'images
FOND = sf.Texture.from_file("images/fond.png")

ASCII = sf.Image.from_file("images/ascii.png")
ASCII_PASSAGE = sf.Image.from_file("images/ascii_passage.png")
ASCII_SELECTION = sf.Image.from_file("images/ascii_selection.png")

# Caractères autorisés dans les entrées de texte
CARACTERES_AUTORISES = r"[A-Za-zÀ-ÿ0-9]"

# Flags pour le positionnement
VERTICAL = 0
HORIZONTAL = 1

# FPS pour tout les menus
FPS = 60

# ----------------------------------------------------------------------------------------------------------------------
# DEFINITIONS DE FONCTIONS DE BASE
# ----------------------------------------------------------------------------------------------------------------------


def limiter_fps(chronometre):

    # C'est sale, mais sinon j'ai des bugs avec time.sleep...
    # print(chronometre.elapsed_time.milliseconds)
    while chronometre.elapsed_time.milliseconds < 1000//FPS:
        continue
    chronometre.restart()


# ----------------------------------------------------------------------------------------------------------------------
# DEFINITIONS DE CLASSES
# ----------------------------------------------------------------------------------------------------------------------


class Menu:
    """
        Classe représentant un menu, elle regroupe des ensembles de boutons.
        Elle sert à lancer le menu, créer et renvoyer la sortie de ce menu...
    """

    def __init__(self, fond=FOND):
        """
            self.ensembles: Liste des ensembles faisant partie de ce menu.
            self.fond: sf.Texture qui servira d'image de fond au menu.
        """

        self.ensembles = list()

        self.fond = fond

    def ajouter_ensemble(self, ensemble):
        """
            Fonction qui ajoute un ensemble au menu après avoir fait quelques
            vérifications.
        """

        assert isinstance(ensemble, Ensemble)

        self.ensembles.append(ensemble)

    def lancer(self, window, resolution, chronometre, touche_menu):
        """
            Fonction qui affiche le menu et le fait intéragire avec
            l'utilisateur.
            La fonction s'arrête dès qu'un bouton est cliqué, dès que
            l'utilisateur ferme le programme, dès que l'utilisateur
            modifie la taille de la fenêtre ou dès qu'il quitte le menu en
            appuyant sur la touche spécifiée en argument.
            Si un bouton a été cliqué, le retour de la fonction sera un
            dictionnaire dont la construction est détaillée ci-dessous, si le
            programme a été fermé, la fonction retourne None, si la fenêtre
            à été redimmensionnée, la fonction retourne 0, et si le menu à été
            quitté via la touche spécifiée, la fonction retourne 1.

            Liste des arguments du dictionnaire retourné:
                - "choix": ID du bouton sur lequel le joueur à cliqué pour finir
                la boucle du menu
                - "selection": Liste de listes [groupe, ID] qui indiquent quels
                boutons sont selectionnés pour chaque groupe.
                - "valeurs": Liste de listes [ID, valeur] qui indiquent quelles
                valeurs sont contenues dans chaque entrée de texte.
        """

        liste_boutons = list()

        for ensemble in self.ensembles:
            ensemble.verifier()
            for bouton in ensemble.boutons:
                liste_boutons.append(bouton)

        sortie = {"choix": None, "selection": list(), "valeurs": list()}
        position_souris = (sf.Mouse.get_position(window).x, sf.Mouse.get_position(window).y)

        while sortie["choix"] is None:

            limiter_fps(chronometre)
            window.display()

            # ----------------------------------------------------------------------------------------------------------
            # GESTION DES EVENEMENTS
            # ----------------------------------------------------------------------------------------------------------

            for event in window.events:

                # Redimensionner l'ecran
                if isinstance(event, sf.ResizeEvent):
                    resolution["w"], resolution["h"] = event.width, event.height
                    window.view.reset((0, 0, resolution["w"], resolution["h"]))
                    return 0

                # Quitter le programme
                if isinstance(event, sf.CloseEvent):
                    return None

                # Quitter le menu
                if isinstance(event, sf.KeyEvent):
                    if event.released and event.code == touche_menu:
                        return 1

                # Déplacer la souris
                if isinstance(event, sf.MouseMoveEvent):
                    position_souris = (event.position.x, event.position.y)

                # TOUCHE PRESSEE

                if isinstance(event, sf.TextEvent):
                    for bouton in liste_boutons:
                        if isinstance(bouton, EntreeTexte):
                            if bouton.selectionne:
                                if search(CARACTERES_AUTORISES, chr(event.unicode)) is not None:
                                    if len(bouton.valeur) < bouton.maxlength:
                                        bouton.valeur += chr(event.unicode)
                                elif event.unicode == 8:
                                    if len(bouton.valeur) > 0:
                                        bouton.valeur = bouton.valeur[:-1]

                # CLIC

                if isinstance(event, sf.MouseButtonEvent):
                    if event.released:
                        for bouton in liste_boutons:

                            # Boutons normaux
                            if isinstance(bouton, Bouton):
                                if bouton.coord["x"] < position_souris[0] < bouton.coord["x"]+bouton.coord["w"] and \
                                   bouton.coord["y"] < position_souris[1] < bouton.coord["y"]+bouton.coord["h"]:
                                    sortie["choix"] = bouton.id

                            # Boutons selectionnables
                            elif isinstance(bouton, BoutonSelectionnable):
                                if bouton.coord["x"] < position_souris[0] < bouton.coord["x"]+bouton.coord["w"] and \
                                   bouton.coord["y"] < position_souris[1] < bouton.coord["y"]+bouton.coord["h"]:
                                    selection_ajoutee = False
                                    for selection in sortie["selection"]:
                                        if selection[0] == bouton.groupe:
                                            selection_ajoutee = True
                                            selection[1] = bouton.id
                                    if not selection_ajoutee:
                                        sortie["selection"].append([bouton.groupe, bouton.id])

                            # Entrées de texte
                            elif isinstance(bouton, EntreeTexte):
                                for autre_bouton in liste_boutons:
                                    if isinstance(autre_bouton, EntreeTexte):
                                        autre_bouton.selectionne = False
                                bouton.selectionne = True

            # ----------------------------------------------------------------------------------------------------------
            # AFFICHAGE DU MENU
            # ----------------------------------------------------------------------------------------------------------

            ratio = (resolution["w"]/self.fond.size.x, resolution["h"]/self.fond.size.y)
            sprite = sf.Sprite(self.fond)
            sprite.scale(ratio)
            window.draw(sprite)

            for ensemble in self.ensembles:
                if ensemble.fond is not None:
                    sprite = sf.Sprite(ensemble.fond)
                    sprite.position = (ensemble.coord["x"], ensemble.coord["y"])
                    ratio = (ensemble.coord["w"]/ensemble.fond.size.x, ensemble.coord["h"]/ensemble.fond.size.y)
                    sprite.scale(ratio)
                    window.draw(sprite)

            for bouton in liste_boutons:

                # BOUTONS NORMAUX

                if isinstance(bouton, Bouton):
                    if bouton.coord["x"] < position_souris[0] < bouton.coord["x"]+bouton.coord["w"] and \
                       bouton.coord["y"] < position_souris[1] < bouton.coord["y"]+bouton.coord["h"]:
                        if sf.Mouse.is_button_pressed(sf.Mouse.LEFT) and bouton.sprites["clic"] is not None:
                            sprite = sf.Sprite(bouton.sprites["clic"])
                        else:
                            if bouton.sprites["passage"] is not None:
                                sprite = sf.Sprite(bouton.sprites["passage"])
                            else:
                                sprite = sf.Sprite(bouton.sprites["normal"])
                    else:
                        sprite = sf.Sprite(bouton.sprites["normal"])

                    sprite.position = (bouton.coord["x"], bouton.coord["y"])
                    window.draw(sprite)

                # BOUTONS SELECTIONNABLES

                elif isinstance(bouton, BoutonSelectionnable):
                    if [bouton.groupe, bouton.id] in sortie["selection"]:
                        sprite = sf.Sprite(bouton.sprites["selection"])
                    elif bouton.coord["x"] < position_souris[0] < bouton.coord["x"]+bouton.coord["w"] and \
                         bouton.coord["y"] < position_souris[1] < bouton.coord["y"]+bouton.coord["h"]:
                        if sf.Mouse.is_button_pressed(sf.Mouse.LEFT) and bouton.sprites["clic"] is not None:
                            sprite = sf.Sprite(bouton.sprites["clic"])
                        else:
                            if bouton.sprites["passage"] is not None:
                                sprite = sf.Sprite(bouton.sprites["passage"])
                            else:
                                sprite = sf.Sprite(bouton.sprites["normal"])
                    else:
                        sprite = sf.Sprite(bouton.sprites["normal"])

                    sprite.position = (bouton.coord["x"], bouton.coord["y"])
                    window.draw(sprite)

                # ENTREES DE TEXTE

                elif isinstance(bouton, EntreeTexte):
                    if bouton.selectionne:
                        sprite_bouton = sf.Sprite(bouton.sprites["selection"])
                    else:
                        sprite_bouton = sf.Sprite(bouton.sprites["normal"])

                    if len(bouton.valeur) > 0:

                        image_texte = sf.Image.create(len(bouton.valeur)*32, 64)
                        for l, lettre in enumerate(bouton.valeur):
                            image_texte.blit(ASCII_SELECTION if bouton.selectionne else ASCII, (l*32, 0),
                                             ((ord(lettre) % 10)*32, (ord(lettre)//10)*64, 32, 64))
                        image_texte.create_mask_from_color(sf.Color(255, 255, 255))

                        sprite_texte = sf.Sprite(sf.Texture.from_image(image_texte))
                        decalage = (bouton.coord["w"]-bouton.maxlength*32)//2
                        sprite_texte.position = (bouton.coord["x"]+decalage, bouton.coord["y"]+bouton.coord["h"]-68)

                        window.draw(sprite_texte)

                    sprite_bouton.position = (bouton.coord["x"], bouton.coord["y"])
                    window.draw(sprite_bouton)

                # TEXTES

                elif isinstance(bouton, Texte):
                    sprite = sf.Sprite(bouton.sprites["normal"])
                    sprite.position = (bouton.coord["x"], bouton.coord["y"])
                    window.draw(sprite)

        # Créer la sortie

        for bouton in liste_boutons:
            if isinstance(bouton, EntreeTexte):
                sortie["valeurs"].append([bouton.id, bouton.valeur])

        return sortie


class Ensemble:
    """
        Classe représentant un ensemble de bouton.
        Un ensemble de bouton sert principalement, voir exclusivement, à placer
        plus facilement les boutons d'un menu.
    """

    def __init__(self, fond=None):
        """
            self.boutons: Liste des boutons qui composent cet ensemble.
            self.fond: sf.Texture qui servira d'image de fond au menu.
            self.coord: Coordonnées de l'ensemble par rapport au menu.
        """

        self.boutons = list()
        self.fond = fond
        self.coord = {"x": 0, "y": 0, "w": 0, "h": 0}

    def ajouter_bouton(self, bouton):
        """
            Fonction qui après avoir vérifié la validité d'un bouton, ajoute
            ce bouton à l'ensemble.
        """

        liste_types_boutons = (Bouton, BoutonSelectionnable, EntreeTexte, Texte)

        try:
            assert type(bouton) in liste_types_boutons
        except AssertionError:
            raise ValueError(bouton, " n'est pas un bouton valide.")

        self.boutons.append(bouton)

    def verifier(self):
        """
            Fonction vérifiant si un menu peut fonctionner, retournant une erreur
            si elle rencontre une anomalie.
        """

        assert isinstance(self.fond, sf.Texture) or self.fond is None

        for bouton in self.boutons:
            if isinstance(bouton, Bouton):
                assert isinstance(bouton.sprites["normal"], sf.Texture)
            elif isinstance(bouton, BoutonSelectionnable):
                assert isinstance(bouton.sprites["normal"], sf.Texture)
                assert isinstance(bouton.sprites["selection"], sf.Texture)
            elif isinstance(bouton, EntreeTexte):
                assert isinstance(bouton.sprites["normal"], sf.Texture)
                assert isinstance(bouton.sprites["selection"], sf.Texture)

    def position_auto_boutons(self, x, y, w, h, disposition=VERTICAL):
        """
            Fonction definissant automatiquement à partir de la résolution et
            de la taille des sprites la taille des boutons et leur positions.
        """

        self.verifier()

        # Calculer la taille de chaque bouton et la taille de tout les boutons mis bout à bout
        taille_totale = [0, 0]
        for bouton in self.boutons:
            bouton.coord["w"] = bouton.sprites["normal"].width
            taille_totale[0] += bouton.coord["w"]
            bouton.coord["h"] = bouton.sprites["normal"].height
            taille_totale[1] += bouton.coord["h"]

        # Calculer les coordonnées x et y de chaque bouton
        curseur = 0
        for bouton in self.boutons:

            if disposition == VERTICAL:
                bouton.coord["x"] = (w-bouton.coord["w"])//2
                bouton.coord["y"] = curseur+(h-taille_totale[1])//(len(self.boutons)+1)
                curseur = bouton.coord["y"]+bouton.coord["h"]

            elif disposition == HORIZONTAL:
                bouton.coord["y"] = (h-bouton.coord["h"])//2
                bouton.coord["x"] = curseur+(w-taille_totale[0])//(len(self.boutons)+1)
                curseur = bouton.coord["x"]+bouton.coord["w"]

        for bouton in self.boutons:
            bouton.coord["x"] += x
            bouton.coord["y"] += y

        self.coord = {"x": x, "y": y, "w": w, "h": h}


class Bouton:
    """
        Classe représentant un bouton normal.
        Un bouton normal est un bouton qui arrête le menu quand on clique dessus,
        puis qui renvoie son ID.
    """

    def __init__(self, id_bouton):
        """
            self.id: ID du bouton, il sert à identifier quel bouton a été cliqué
            quand on analyse le retour de l'affichage du menu.
            self.coord: Dictionnaire contenant les coordonnées du bouton: x, y,
            w et h.
            self.sprites: Dictionnaire contenant les divers sprites du bouton.
        """

        self.id = id_bouton
        self.coord = {"x": 0, "y": 0, "w": 0, "h": 0}
        self.sprites = {"normal": None, "passage": None, "clic": None}

    def charger_sprites(self, normal, passage=None, clic=None):
        """
            Fonction qui après avoir vérifier que les arguments passés sont
            bien des sf.Textures, les assignes à self.sprites.
        """

        try:
            assert isinstance(normal, sf.Texture)
            assert isinstance(passage, sf.Texture) or passage is None
            assert isinstance(clic, sf.Texture) or clic is None
        except AssertionError:
            raise ValueError("L'un des arguments n'est ni une sf.Texture, ni None:", normal, passage, clic)

        self.sprites = {"normal": normal, "passage": passage, "clic": clic}

    def creer_sprites_str(self, chaine):
        """
            Fonction qui créer les sprites du bouton à partir d'une chaine de
            caractères.
        """

        try:
            assert isinstance(chaine, str)
        except AssertionError:
            raise ValueError(chaine, " n'est pas une chaine de caractère.")

        # Créer les images
        self.sprites["normal"] = sf.Image.create(len(chaine)*32, 64, sf.Color(255, 255, 255))
        self.sprites["passage"] = sf.Image.create(len(chaine) * 32, 64, sf.Color(255, 255, 255))

        # Dessiner les caractères sur les images
        for l, lettre in enumerate(chaine):
            coord_lettre = ((ord(lettre) % 10)*32, (ord(lettre)//10)*64, 32, 64)
            self.sprites["normal"].blit(ASCII, (l*32, 0), coord_lettre)
            self.sprites["passage"].blit(ASCII_PASSAGE, (l * 32, 0), coord_lettre)

        # Transformer les images en textures
        self.sprites["normal"].create_mask_from_color(sf.Color(255, 255, 255))
        self.sprites["passage"].create_mask_from_color(sf.Color(255, 255, 255))

        self.sprites["normal"] = sf.Texture.from_image(self.sprites["normal"])
        self.sprites["passage"] = sf.Texture.from_image(self.sprites["passage"])


class BoutonSelectionnable:
    """
        Classe représentant un bouton sélectionnable
        Un bouton sélectionnable possède un groupe et une ID. L'ID est propre
        au bouton tandis que le groupe détermine si en selectionnant ce bouton
        on en déselectionne un autre.
        Quand l'affichage d'un menu se termine, il renvoie pour tout les groupes
        l'ID du bouton selectionné, sinon None.
    """

    def __init__(self, id_bouton, id_groupe):
        """
            self.id: ID du bouton, il sert à identifier quel bouton a été cliqué
            quand on analyse le retour de l'affichage du menu.
            self.groupe: Groupe du bouton, il sert à identifier à quel groupe
            appartient un bouton selectionnable.
            self.coord: Dictionnaire contenant les coordonnées du bouton: x, y,
            w et h.
            self.sprites: Dictionnaire contenant les divers sprites du bouton.
        """

        self.id = id_bouton
        self.groupe = id_groupe
        self.coord = {"x": 0, "y": 0, "w": 0, "h": 0}
        self.sprites = {"normal": None, "selection": None, "passage": None, "clic": None}

    def charger_sprites(self, normal, selection, passage=None, clic=None):
        """
            Fonction qui après avoir vérifier que les arguments passés sont
            bien des sf.Textures, les assignes à self.sprites.
        """

        try:
            assert isinstance(normal, sf.Texture)
            assert isinstance(selection, sf.Texture)
            assert isinstance(passage, sf.Texture) or passage is None
            assert isinstance(clic, sf.Texture) or clic is None
        except AssertionError:
            raise ValueError("L'un des arguments n'est ni une sf.Texture ni None:", normal, selection, passage, clic)

        self.sprites = {"normal": normal, "selection": selection, "passage": passage, "clic": clic}

    def creer_sprites_str(self, chaine):
        """
            Fonction qui créer les sprites du bouton à partir d'une chaine de
            caractères.
        """

        try:
            assert isinstance(chaine, str)
        except AssertionError:
            raise ValueError(chaine, " n'est pas une chaine de caractère.")

        # Créer des images
        self.sprites["normal"] = sf.Image.create(len(chaine)*32, 64, sf.Color(255, 255, 255))
        self.sprites["selection"] = sf.Image.create(len(chaine)*32, 64, sf.Color(255, 255, 255))
        self.sprites["passage"] = sf.Image.create(len(chaine)*32, 64, sf.Color(255, 255, 255))

        # Dessiner les caractères sur les images
        for l, lettre in enumerate(chaine):
            coord_lettre = ((ord(lettre) % 10)*32, (ord(lettre)//10)*64, 32, 64)
            self.sprites["normal"].blit(ASCII, (l*32, 0), coord_lettre)
            self.sprites["selection"].blit(ASCII_SELECTION, (l*32, 0), coord_lettre)
            self.sprites["passage"].blit(ASCII_PASSAGE, (l*32, 0), coord_lettre)

        # Transformer les images en textures
        self.sprites["normal"].create_mask_from_color(sf.Color(255, 255, 255))
        self.sprites["selection"].create_mask_from_color(sf.Color(255, 255, 255))
        self.sprites["passage"].create_mask_from_color(sf.Color(255, 255, 255))

        self.sprites["normal"] = sf.Texture.from_image(self.sprites["normal"])
        self.sprites["selection"] = sf.Texture.from_image(self.sprites["selection"])
        self.sprites["passage"] = sf.Texture.from_image(self.sprites["passage"])


class EntreeTexte:
    """
        Classe représentant une entrée de texte.
        Une entrée de texte est une zone dans laquelle on peut taper du texte.
        Quand le menu se termine il renvoie pour chaque entrée de texte une
        chaine de caractère correspondant à ce qui a été tapé.
    """

    def __init__(self, id_bouton, maxlength=10, valeur=str()):
        """
            self.id: ID du bouton, il sert à identifier quel bouton a été cliqué
            quand on analyse le retour de l'affichage du menu.
            self.coord: Dictionnaire contenant les coordonnées du bouton: x, y,
            w et h.
            self.sprites: Dictionnaire contenant les divers sprites du bouton.

            self.selectionne: Booléen qui indique si l'entrée de texte est
            selectionnée.
            self.valeur: Chaine de caractère entrée par l'utilisateur
            self.maxlength: Longueur maximale de la chaine de self.valeur
        """

        self.id = id_bouton
        self.coord = {"x": 0, "y": 0, "w": 0, "h": 0}
        self.sprites = {"normal": None, "selection": None}

        self.selectionne = False
        self.valeur = valeur
        self.maxlength = maxlength

    def creer_sprites_str(self, chaine):
        """
            Fonction qui créer les sprites du bouton à partir d'une chaine de
            caractères.
        """

        try:
            assert isinstance(chaine, str)
        except AssertionError:
            raise ValueError(chaine, " n'est pas une chaine de caractère.")

        # Créer les images
        self.sprites["normal"] = sf.Image.create(len(chaine)*32, 64, sf.Color(255, 255, 255))
        self.sprites["selection"] = sf.Image.create(len(chaine)*32, 64, sf.Color(255, 255, 255))

        # Dessiner le message sur les images
        for l, lettre in enumerate(chaine):
            coord_lettre = ((ord(lettre) % 10)*32, (ord(lettre)//10)*64, 32, 64)
            self.sprites["normal"].blit(ASCII, (l*32, 0), coord_lettre)
            self.sprites["selection"].blit(ASCII_SELECTION, (l*32, 0), coord_lettre)

        # Créer le dessin de la zone de saisie
        largeur_bouton = len(chaine)*32 if len(chaine)*32 > self.maxlength*32+8 else self.maxlength*32+8
        zone_saisie = sf.RectangleShape()
        zone_saisie.size = (self.maxlength*32+4, 68)
        zone_saisie.fill_color = sf.Color(255, 255, 255)
        zone_saisie.outline_thickness = 2
        zone_saisie.position = ((largeur_bouton-self.maxlength*32-4)//2, 68)

        # Créer des sf.RenderTexture pour y dessiner le sprite final
        render_texture_normal = sf.RenderTexture(largeur_bouton, 138)
        render_texture_selection = sf.RenderTexture(largeur_bouton, 138)

        # Dessiner les sprites
        zone_saisie.outline_color = sf.Color(255, 242, 0)
        render_texture_normal.draw(sf.Sprite(sf.Texture.from_image(self.sprites["normal"])))
        render_texture_normal.draw(zone_saisie)

        zone_saisie.outline_color = sf.Color(63, 72, 204)
        render_texture_selection.draw(sf.Sprite(sf.Texture.from_image(self.sprites["selection"])))
        render_texture_selection.draw(zone_saisie)

        # Obtenir les images finales
        self.sprites["normal"] = render_texture_normal.texture.to_image()
        self.sprites["selection"] = render_texture_selection.texture.to_image()

        self.sprites["normal"].flip_vertically()
        self.sprites["selection"].flip_vertically()

        self.sprites["normal"].create_mask_from_color(sf.Color(255, 255, 255))
        self.sprites["selection"].create_mask_from_color(sf.Color(255, 255, 255))

        # Convertir les images finales en textures
        self.sprites["normal"] = sf.Texture.from_image(self.sprites["normal"])
        self.sprites["selection"] = sf.Texture.from_image(self.sprites["selection"])


class Texte:
    """
        Classe représentant un texte affiché à l'ecran, cette classe peut en
        fait servir pour l'affichage de n'importe quel image dans le menu.
    """

    def __init__(self):
        """
            self.coord: Dictionnaire contenant les coordonnées du bouton: x, y,
            w et h.
            self.sprites: Dictionnaire contenant les divers sprites du bouton.
        """

        self.coord = {"x": 0, "y": 0, "w": 0, "h": 0}
        self.sprites = {"normal": None}

    def charger_sprites(self, normal):
        """
            Fonction qui après avoir vérifier que l'argument passé est bien une
            sf.Texture, l'assigne à self.sprites.
        """

        try:
            assert isinstance(normal, sf.Texture)
        except AssertionError:
            raise ValueError("L'un des arguments n'est ni une sf.Texture, ni None:", normal)

        self.sprites = {"normal": normal}

    def creer_sprites_str(self, message):
        """
            Fonction qui créer le sprite du texte à partir d'une chaine de
            caractères.
        """

        try:
            assert isinstance(message, str)
        except AssertionError:
            raise ValueError(message, " n'est pas une chaine de caractère.")

        # Créer l'image
        chaines = message.split("\n")
        taille_chaine_max = sorted(chaines, key=lambda x: -len(x))[0]
        self.sprites["normal"] = sf.Image.create(taille_chaine_max*32, len(chaines)*64, sf.Color(255, 255, 255))

        # Dessiner les caractères sur l'image
        for l, ligne in enumerate(chaines):
            for c, caractere in enumerate(ligne):
                coord_lettre = ((ord(caractere) % 10)*32, (ord(caractere)//10)*64, 32, 64)
                self.sprites["normal"].blit(ASCII, (c*32+(taille_chaine_max-len(ligne)*32)//2, l*64), coord_lettre)

        # Transformer l'image en texture
        self.sprites["normal"].create_mask_from_color(sf.Color(255, 255, 255))

        self.sprites["normal"] = sf.Texture.from_image(self.sprites["normal"])

