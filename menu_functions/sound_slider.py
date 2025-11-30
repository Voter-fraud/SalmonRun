from sound_library import Sound

def s_change(dir):
    if dir == 'right' and Sound.effects_volume < 100: Sound.effects_volume += 1
    if dir == 'left' and Sound.effects_volume > 0: Sound.effects_volume -= 1

def t_update():
    return Sound.effects_volume