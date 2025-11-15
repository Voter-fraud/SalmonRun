import pygame, math, map_mod, random, time, os
pygame.init()
pygame.mixer.init()
pygame.font.init()
game_map = map_mod.format_game_map('custom')
UI_scale = 1