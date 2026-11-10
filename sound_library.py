import pygame
pygame.init()

sound_dict = {
    "walking_sound": pygame.mixer.Sound('assets/audio/walking sound.mp3'),
    "rod_cast_sound": pygame.mixer.Sound('assets/audio/rod_cast.mp3'),
    "rod_pull_sound": pygame.mixer.Sound('assets/audio/Fishingrod pull.mp3')
}



class Sound:
    """Controls sound engine settings"""
    effects_volume = 100
    sound_state = True

def update_volume():
    """Updates the volume of all sound effects to Sound.effects_volume"""
    for sound in sound_dict.values(): #sound is type pygame.Sound
        sound.set_volume(Sound.effects_volume / 100)