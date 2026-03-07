import pygame
from toolbox import load_asset
from globals import Global

pygame.init()
text_box = load_asset( 'textbox.png')
textbox_font = pygame.font.SysFont('Comic Sans MS', 20*Global.UI_scale)

standard_comic = pygame.font.SysFont('Comic Sans MS', 30*Global.UI_scale)  # this is only one font size