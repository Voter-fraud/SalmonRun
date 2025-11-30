"""
This module handles some global variables and initializations.
Only. map_mod, reso_p, and globals should really feed into here
"""

import pygame
import map_mod
from globals import Global

Global.game_map = map_mod.format_game_map('custom')
