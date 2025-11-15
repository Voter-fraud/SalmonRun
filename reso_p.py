import pygame
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
win_lengthw = int(res[0]) # fix rendering based on these 640x320 reccomended base size
win_heightw = int(res[1])
win_lengthf = int(res[0]) # fix rendering based on these 640x320 reccomended base size
win_heightf = int(res[1])
win_length = win_lengthw
win_height = win_heightw
win_mode = 'windowed'
win = pygame.display.set_mode((win_length, win_height))

def fullscreen_toggle():
    global win_lengthw, win_heightw,  win_lengthf, win_heightf, win_height, win_length, win, win_mode
    if win_mode == 'windowed':
        win = pygame.display.set_mode((win_lengthf, win_heightf), pygame.FULLSCREEN)
        win_mode = 'fullscreen'
        win_length = win_lengthf
        win_height = win_heightf
    elif win_mode == 'fullscreen':
        win = pygame.display.set_mode((win_lengthw, win_heightw))
        win_mode = 'windowed'
        win_length = win_lengthw
        win_height = win_heightw