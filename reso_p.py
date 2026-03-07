"""
This module creates and then is able to manage game resolution.
Under no circumstances should ANY project specific modules be imported besides globals.
"""


import pygame
from globals import Global

pygame.init()
def format_resolution(txt):
    """Turns a game_map textfile read into a proper game_map list
    see https://youtu.be/dQw4w9WgXcQ for a full explanation"""
    read_file = open(txt, 'r').readlines()
    for char in read_file:
        print(char)
    main = read_file[0].strip()
    x = main.split(",")
    for spot, item in enumerate(x):
        x[spot] = item.strip()
    return x


res = format_resolution('Reso.txt')
win_lengthw = int(res[0]) # windowed
win_heightw = int(res[1])

win_length = win_lengthw
win_height = win_heightw
win_mode = 'windowed' # currently no fullscreen because it is not super important
win = pygame.display.set_mode((win_length, win_height))

if win_heightw == 600: # sets entire game scale
    Global.scale = 2
    Global.UI_scale = 1
else:
    Global.scale = 3
    Global.UI_scale = 1