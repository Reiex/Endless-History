# -*- coding:utf-8 -*

"""
    Fichier qui sera executé, contenant l'appel de toutes les
    grosses classes et fonctions écrites dans les autres fichiers.
"""

# ----------------------------------------------------------------------------------------------------------------------
# INITIALISATION DU JEU
# ----------------------------------------------------------------------------------------------------------------------

import sfml as sf
from sys import exit as quitter_programme
from os import remove

# Ouvrir la fenêtre et démarrer le chronometre (permettant de mesurer le temps entre de calcul deux frames)

resolution = {"w": 1024, "h": 576}
window = sf.RenderWindow(sf.VideoMode(resolution["w"], resolution["h"]), "Endless-history")
window.vertical_synchronization = False
chronometre = sf.Clock()

# Afficher l'ecran de chargement du jeu

CHARGEMENT = sf.Texture.from_file("images/chargement_jeu.png")

sprite = sf.Sprite(CHARGEMENT)
sprite.ratio *= (resolution["w"]/CHARGEMENT.width)
window.draw(sprite)
window.display()

# Importer les classes et fonctions du jeu

from utilisateur import *

# Obtenir les données de l'utilisateur et initialiser des variables

utilisateur = Utilisateur()
carte = Carte()
joueur = Joueur()
continuer_map = False
continuer_jeu = False
continuer_programme = True
spawn = {"ID-map": str(), "x": int(), "y": int()}

# ----------------------------------------------------------------------------------------------------------------------
# BOUCLE DU PROGRAMME
# ----------------------------------------------------------------------------------------------------------------------

while continuer_programme:

    # Créer le menu et le lancer

    menu_programme = menu.Menu()

    ensemble = menu.Ensemble()

    bouton = menu.Bouton("Commencer l'aventure")
    bouton.creer_sprites_str("Commencer l'aventure")
    ensemble.ajouter_bouton(bouton)

    if utilisateur.sauvegarde_utilisable:
        bouton = menu.Bouton("Continuer l'aventure")
        bouton.creer_sprites_str("Continuer l'aventure")
        ensemble.ajouter_bouton(bouton)

    ensemble.position_auto_boutons(0, 0, resolution["w"], resolution["h"])
    menu_programme.ajouter_ensemble(ensemble)

    sortie = menu_programme.lancer(window, resolution, chronometre, utilisateur.raccourcis["menu"])

    # Traiter la sortie

    if isinstance(sortie, dict):

        if sortie["choix"] == "Commencer l'aventure":
            continuer_jeu = True
            spawn = {"ID-map": "main-0", "x": 12224, "y": 6144}
            joueur = Joueur()
            utilisateur.utiliser_sauvegarde = False

        elif sortie["choix"] == "Continuer l'aventure":
            utilisateur.utiliser_sauvegarde = True
            continuer_jeu = True

    elif sortie is None:
        utilisateur.enregistrer()
        quitter_programme()

    # ------------------------------------------------------------------------------------------------------------------
    # BOUCLE DU JEU
    # ------------------------------------------------------------------------------------------------------------------

    while continuer_jeu:

        # CHARGER LA CARTE ET LES COORDONNEES DU JOUEUR

        # Si le joueur utilise sa sauvegarde

        if utilisateur.utiliser_sauvegarde:

            joueur, carte, spawn = utilisateur.recuperer_donnees_sauvegarde()
            carte.liste_rafraichir = list()
            sauvegarde_presente = True
            utilisateur.utiliser_sauvegarde = False

        # Si le joueur n'utilise pas sa sauvegarde

        else:

            carte = Carte()
            carte.charger(spawn["ID-map"])
            joueur.coord["x"], joueur.coord["y"] = spawn["x"], spawn["y"]
            carte.carte_bool[joueur.coord["x"]//BLOCSIZE, joueur.coord["y"]//BLOCSIZE] = False

        continuer_map = True
        ancien_spawn = deepcopy(spawn)
        mort_quete = False
        collision = False
        jeu_fini = False

        # --------------------------------------------------------------------------------------------------------------
        # BOUCLE DE MAP
        # --------------------------------------------------------------------------------------------------------------

        while continuer_map:

            # Rafraichir l'image

            carte.afficher(window, resolution, joueur, spawn)
            menu.limiter_fps(chronometre)
            window.display()

            # TRAITER LES EVENEMENTS DE LA FENETRE

            for event in window.events:

                # Evenements communs
                if isinstance(event, sf.CloseEvent):
                    utilisateur.sauvegarder_partie(carte, joueur, spawn)
                    utilisateur.enregistrer()
                    quitter_programme()
                elif isinstance(event, sf.ResizeEvent):
                    resolution["w"], resolution["h"] = event.width, event.height
                    window.view.reset((0, 0, resolution["w"], resolution["h"]))

                # Clic
                elif isinstance(event, sf.MouseButtonEvent):
                    if event.button == sf.Mouse.LEFT and event.released:
                        carte.detecter_fin_message((event.position.x, event.position.y))
                    elif event.button == sf.Mouse.RIGHT and event.released:
                        carte.utiliser_objet(joueur, window)

                elif isinstance(event, sf.KeyEvent) and not jeu_fini:

                    # Inventaire
                    if event.released and event.code == utilisateur.raccourcis["inventaire"]:
                        if joueur.ouvrir_inventaire(window, resolution, utilisateur.raccourcis, chronometre) == 1:
                            utilisateur.sauvegarder_partie(carte, joueur, spawn)
                            utilisateur.enregistrer()
                            quitter_programme()

                    # Map
                    elif event.released and event.code == utilisateur.raccourcis["map"]:
                        if joueur.ouvrir_map(window, resolution, utilisateur.raccourcis, chronometre, spawn) == 1:
                            utilisateur.sauvegarder_partie(carte, joueur, spawn)
                            utilisateur.enregistrer()
                            quitter_programme()

                    # MENU DU JEU

                    elif event.released and event.code == utilisateur.raccourcis["menu"]:
                        utilisateur.sauvegarder_partie(carte, joueur, spawn)
                        utilisateur.enregistrer()

                        menu_jeu = menu.Menu()
                        ensemble = menu.Ensemble()

                        chaines = ("Continuer", "Revenir au menu", "Quitter le jeu")
                        for chaine in chaines:
                            bouton = menu.Bouton(chaine)
                            bouton.creer_sprites_str(chaine)
                            ensemble.ajouter_bouton(bouton)

                        ensemble.position_auto_boutons(0, 0, resolution["w"], resolution["h"])
                        menu_jeu.ajouter_ensemble(ensemble)

                        sortie = menu_jeu.lancer(window, resolution, chronometre, utilisateur.raccourcis["menu"])

                        if isinstance(sortie, dict):

                            if sortie["choix"] == "Revenir au menu":
                                continuer_jeu = False
                                continuer_map = False

                            elif sortie["choix"] == "Quitter le jeu":
                                quitter_programme()

                        elif sortie is None:
                            quitter_programme()

            # FAIRE FONCTIONNER LE JEU

            if not (carte.message["afficher"] or jeu_fini):

                # Faire avancer le tempo
                carte.tempo = (carte.tempo + 1) % 60

                # Faire fonctionner les places
                carte.gerer_places(joueur)

                # Faire fonctionner le joueur
                carte.effectuer_actions_joueur(joueur)
                carte.determiner_actions_joueur(utilisateur.raccourcis, window, joueur)

                # Faire fonctionner les monstres
                carte.effectuer_actions_monstres(joueur)
                carte.determiner_actions_monstres(resolution, joueur)

                # Faire fonctionner les PNJS
                carte.effectuer_actions_pnj()
                carte.determiner_actions_pnj(resolution, joueur, utilisateur.raccourcis)

                # Faire fonctionner les attaques
                carte.effectuer_actions_attaque(joueur)
                carte.determiner_actions_attaque(joueur, resolution)

            elif carte.message["afficher"]:
                # Afficher la boite de dialogue
                carte.afficher_message(window)

            # AFFICHER LE JEU

            if not (collision and joueur.quete_finale):
                carte.afficher_joueur(joueur)
            else:
                jeu_fini = True
            carte.afficher_monstres()
            carte.afficher_pnj()
            carte.afficher_attaque()
            carte.ramasser_afficher_objets(joueur)
            carte.afficher_interface(joueur, resolution)
            carte.gerer_meubles(joueur, utilisateur.raccourcis, resolution, spawn)

            # VERIFIER QUE LA BOUCLE NE DOIT PAS S'ARRETER

            # Si le joueur est mort
            if joueur.vie <= 0:
                if len(joueur.actions) == 0:
                    joueur.actions = [{"type": 2, "frame": 0, "vitesse": 60}]
                elif joueur.actions[0]["type"] != 2:
                    joueur.actions = [{"type": 2, "frame": 0, "vitesse": 60}]
                elif joueur.actions[0]["type"] == 2 and joueur.actions[0]["frame"] >= joueur.actions[0]["vitesse"]:
                    continuer_map = False
                    if utilisateur.sauvegarde_utilisable:
                        utilisateur.utiliser_sauvegarde = True

            # Si le joueur meurt pour une quête
            if len(joueur.actions) != 0:
                if joueur.actions[0]["type"] == 2 and joueur.vie > 0:
                    if joueur.actions[0]["frame"] == joueur.actions[0]["vitesse"]:
                        if spawn["ID-map"] == "main-2":
                            del joueur.actions[0]
                            spawn["ID-map"] = "maison-2-2-2"
                            spawn["x"], spawn["y"] = 320, 320
                        continuer_map = False
                        mort_quete = True

            # Si le joueur est dans une porte
            spawn, collision = carte.collision_joueur_porte(joueur, spawn)
            if collision and not joueur.quete_finale:
                continuer_map = False
                joueur.actions = []
            elif joueur.quete_finale:
                spawn = {"ID-map": "main-3", "x": 5120, "y": 576}

            # FINIR LE JEU

            if jeu_fini:
                fin(window, resolution, joueur, chronometre, utilisateur, carte, spawn)
                continuer_jeu = False
                continuer_map = False

        # Si le joueur change de map et que ce n'est pas parce qu'il est mort, sauvegarder
        if not utilisateur.utiliser_sauvegarde and ancien_spawn != spawn and not mort_quete and not jeu_fini:
            utilisateur.sauvegarder_partie(carte, joueur, ancien_spawn)
            utilisateur.enregistrer()

        # Si le jeu est fini, détruire la sauvegarde
        if jeu_fini:
            if "save.elh" in listdir(getcwd()):
                remove("save.elh")
                utilisateur = Utilisateur()