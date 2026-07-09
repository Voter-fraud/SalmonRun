"""
This module defines functions for use by the sound slider button

It is a primary level module
"""

from sound_library import Sound

def s_change(dir):
    """Changes the sound level of the game through the sound slider"""
    if dir == 'right' and Sound.effects_volume < 100: Sound.effects_volume += 1
    if dir == 'left' and Sound.effects_volume > 0: Sound.effects_volume -= 1

def t_update():
    """updates the sound slider to accurately reflect Sound.effect_volume"""
    return Sound.effects_volume