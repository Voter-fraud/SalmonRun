import pygame
pygame.init()

walking_sound = pygame.mixer.Sound('walking sound.mp3')
rod_cast_sound = pygame.mixer.Sound('rod_cast.mp3')
rod_pull_sound = pygame.mixer.Sound('fishingrod pull.mp3')

class Sound:
    effects_volume = 100
    sound_state = True


def update_volume():
    walking_sound.set_volume(Sound.effects_volume / 100)
    rod_pull_sound.set_volume(Sound.effects_volume / 100)
    rod_cast_sound.set_volume(Sound.effects_volume / 100)