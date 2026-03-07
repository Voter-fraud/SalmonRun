"""This is an independent module full of many different generically useful functions. No functions in this module should use
anything project specific. Functions listed in here should be well commented and explain any assumptions in the docstring"""

import pygame, os
def img_dim_lst(image):
    """Returns the half the dimensions of a singular image or of the first in a list of images. Returns: (Length, width)"""
    if isinstance(image, list) or isinstance(image, tuple):
        return image[0].get_rect().width/2, image[0].get_rect().height/2
    return image.get_rect().width/2, image.get_rect().height/2

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
    return pygame.image.load(os.path.join('assets', *directories, file)).convert_alpha()

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
            x+=0.1
            y+=slope/10
            if x >= end[0]:
                return
        elif start[0] > end[0]:
            # draws the line from right to left
            pygame.draw.rect(surf, color, (x-xp, y-yp, size, size))
            x -= 0.1
            y -= slope/10
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

def fun_box_check(topleft, side_lengths, vectora, rang, check):
    """Checks to see if a box collides  with a  given point where the box is in a given direction and then returns the vector"""
    s_l = side_lengths
    topleft_changer = {
        (0, 1): [[0, 1], [1, 1]], # down
        (0, -1): [[0, 0], [1, 0]], # up
        (-1, 0): [[0, 0], [0, 1]], # left
        (1, 0): [[1, 1], [1, 0]], # right
    }
    # finds the index of the vector value we are actually moving across
    significant_index = 0
    significant_vector = 0
    for index, value in enumerate(vectora):
        if value:
            significant_index = index
            significant_vector = vectora[significant_index]

    # the two point connected to the fish and then away from
    inner_bounds = topleft_changer[tuple(vectora)]
    outer_bounds = inner_bounds.copy()


    for index, pair in enumerate(inner_bounds):
        inner_bounds[index] = [topleft[ind2]+value*s_l for ind2, value in enumerate(pair)] # [[x+0*s_L, y+1*s_L], [x+1*s_L, y+1*s_L]]

    for index, pair in enumerate(outer_bounds):
        outer_bounds[index] = [topleft[ind2]+value*s_l for ind2, value in enumerate(pair)] # [[x+0*s_L, y+1*s_L], [x+1*s_L, y+1*s_L]]
        outer_bounds[index][significant_index]+=significant_vector*rang # shift each point by rang via the significant vector

    first, second = inner_bounds
    third, fourth = outer_bounds

    box = box_from_4_cords(first, second, third, fourth)
    # pygame.draw.rect(win, (0, 0, 0), (box.topleft[0]-xp, box.topleft[1]-yp, box.width, box.height), 0)
    if box.collidepoint(check):
            return vectora
    return None

def init_resc(scaler, const):
    return scaler*const

def blank_func(*args):
    ''