"""Handles holding important game_state information
NOTHING project specific should be imported in here."""
import pygame
pygame.init()

class Global:
    """Namespace for global variables. DO NOT MAKE ANY INSTANCES"""
    def __new__(cls):
        raise ZeroDivisionError(" please do not create an instance >: ")

    scale = 1
    UI_scale = 1
    spritelist = pygame.sprite.Group()

    fishing_rods = {
        'starter': 1,
        'intermediate': 1.2,
        'advanced': 1.5,
    }
    fishing_rod = 'starter'

    @classmethod
    def fishing_mod(cls):
        return cls.fishing_rods[cls.fishing_rod]

    @classmethod
    def upgrade_rod(cls):
        match cls.fishing_rods[cls.fishing_rod]:
            case 1:
                cls.fishing_rod = 'intermediate'
            case 1.2:
                cls.fishing_rod = 'advanced'
            case 1.5:
                print('This rod is already max level')
                return False
            case _:
                cls.fishing_rod = 'starter'
                print("invalid rod??? how tf")
        return True

    # game_map is created in config
    game_map = ''

