"""
This module handles some global variables and initializations.
Only.
"""

import pygame
import map_mod



game_map = map_mod.format_game_map('custom')
UI_scale = 1
spritelist = pygame.sprite.Group() # this sprite list does not include the tile_map, map creation is done before config