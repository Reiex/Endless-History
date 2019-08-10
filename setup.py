# -*- coding:utf-8 -*

"""
    Fichier permettant de convertir le jeu en dossier executable windows.
"""

import sys
import os.path
from cx_Freeze import setup, Executable

sfml_dir = os.path.join(sys.exec_prefix, "lib", "site-packages", "sfml")
build_exe_options = {"includes": ["numbers"], "excludes": ["sfml"], "include_files": [(sfml_dir, "sfml")]}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(name="Endless-History",
      options={"build_exe": build_exe_options},
      executables=[Executable("main.py", base=base, targetName="Endless-History.exe", icon="icon.ico")])
