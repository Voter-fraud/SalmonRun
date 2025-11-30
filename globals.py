"""Handles holding important game_state information
NOTHING project specific should be imported in here."""
import pygame
pygame.init()

class Global:
    """Namespace for global variables. DO NOT MAKE ANY INSTANCES"""
    def __new__(cls):
        raise ZeroDivisionError("please do not create an instance (:")

    scale = 1
    UI_scale = 1
    spritelist = pygame.sprite.Group()
    # game_map is created in config
    game_map = ''