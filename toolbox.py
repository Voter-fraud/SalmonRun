import pygame, os
def cut_string(string, count):
    """removes the first x digits of a string"""
    list_string = list(string)
    ret_string = ''
    for i in range(0, count):
        ret_string += list_string[i]
    return ret_string

def return_corners(cords, width, length): # cords must be inputted for easier checking of movement
    """Returns the cords of all 4 corners of a sprite in a tuple"""
    rect = pygame.Rect(cords[0], cords[1], width, length)
    return rect.center, rect.topleft, rect.topright, rect.bottomleft, rect.bottomright, rect.midleft, rect.midright, rect.midtop, rect.midbottom

def load_asset(file, *directories):
    """Loads the chosen image file from the assets folder. Directories entered go from highest to lowest level left to right."""
    return pygame.image.load(os.path.join('assets', *directories, file))

def draw_line(start, end, color, surf, xp, yp, size):
    slope = (end[1]-start[1])/(end[0]-start[0])
    x = start[0]
    y = start[1]
    while True:
        if start[0] < end[0]:
            intercept = slope*start[0]-start[1]
            pygame.draw.rect(surf, color, (x-xp, y-yp, size, size))
            x+=0.1
            y+=slope/10
            if x >= end[0]:
                return
        elif start[0] > end[0]:
            intercept = slope * start[0] - start[1]
            pygame.draw.rect(surf, color, (x-xp, y-yp, size, size))
            x -= 0.1
            y -= slope/10
            if x <= end[0]:
                return

def sum_of_two_numbers(num1, num2):
    return num1+num2
sum = sum_of_two_numbers(1, 5)