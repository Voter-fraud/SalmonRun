"""This is an independent module full of many different generically useful functions. No functions in this module should use
anything project specific. Functions listed in here should be well commented and explain any assumptions in the docstring"""

import pygame, os
def cut_string(string, count):
    """removes the first x digits of a string and then returns the new string back"""
    list_string = list(string)
    ret_string = ''
    for i in range(0, count):
        ret_string += list_string[i]
    return ret_string

def return_corners(cords, width, length):
    """Returns the cords of all 4 corners of a sprite in a tuple. (the input should be the topleft cords). (output is more than 4 corners)"""
    rect = pygame.Rect(cords[0], cords[1], width, length)
    return rect.center, rect.topleft, rect.topright, rect.bottomleft, rect.bottomright, rect.midleft, rect.midright, rect.midtop, rect.midbottom

def load_asset(file, *directories):
    """Loads the chosen image file from the 'assets' folder. Directories entered go from highest to lowest level left to right."""
    return pygame.image.load(os.path.join('assets', *directories, file))

def draw_line(start, end, color, surf, xp, yp, size):
    """Draws a line based on the inputs by drawing squares of the given size"""
    slope = (end[1]-start[1])/(end[0]-start[0])
    x = start[0]
    y = start[1]
    while True:
        if start[0] < end[0]:
            # draws the line from left to right
            pygame.draw.rect(surf, color, (x-xp, y-yp, size, size))
            # for every 1 pixel moved along the x-axis the y goes up by the slope
            x+=1
            y+=slope
            if x >= end[0]:
                return
        elif start[0] > end[0]:
            # draws the line from right to left
            pygame.draw.rect(surf, color, (x-xp, y-yp, size, size))
            x -= 1
            y -= slope
            if x <= end[0]:
                return
        else: # starting position is the same as ending position
            # just draw a dot
            pygame.draw.rect(surf, color, (x - xp, y - yp, size, size))
            return

def multi_sum(*nums):
    """Returns the sum of all given numbers"""
    total = 0
    for num in list(*nums):
        total += num
    return total

def box_from_4_cords(cord1, cord2, cord3, cord4):
    """Returns a pygame box from any 4 given cords"""
    if isinstance(cord1, int):
        return False
    x_list = [cord1[0], cord2[0], cord3[0], cord4[0]]
    y_list = [cord1[1], cord2[1], cord3[1], cord4[1]]
    width = max(x_list)-min(x_list)
    height = max(y_list)-min(y_list)
    topleft = min((cord1, cord2, cord3, cord4))
    box = pygame.rect.Rect(topleft[0], topleft[1], width, height)
    return box


