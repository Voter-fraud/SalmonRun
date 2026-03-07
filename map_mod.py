"""map_mod this module is for interacting with the game map. Only reso_p should reasonably be imported here.
it is a pretty independent module"""

import math, os, pygame, random, logging
from reso_p import win
from toolbox import load_asset
from globals import Global
scale = Global.scale

tile_size = 32*scale

grass_tile = [load_asset('center_grass.png', 'tileset'), load_asset('center_grass2.png', 'tileset')
, load_asset('center_grass3.png', 'tileset')] # you can always turn this into a list comprehension
water_tile = load_asset('center_water.png', 'tileset')

map_dict = {
    # contains all relevant map files. this would be useful for creating loaded areas like player housing or an island
    'test': open('game_map.txt', 'r').readlines(),
    'custom': open('custom_map.txt', 'r').readlines()
}

class Block(pygame.sprite.Sprite):
    """Only directly accessed by this map_mod.py and the map editor."""

    block_list = pygame.sprite.Group()
    super_pos_dict = {}
    tile_map = '' # turns into a pygame surface upon initialization

    @classmethod
    def init_surface(cls, g_map):
        """Initialize tile_map as the base layer game_map"""
        length = len(g_map)
        width = len(g_map[0])
        cls.tile_map = pygame.Surface((length * tile_size, width * tile_size))

    @classmethod
    def update_surface(cls):
        """Redraws and updates the tile_map and then returns said tile_map"""
        for sprite in cls.block_list.sprites():
            cls.tile_map.blit(sprite.image, sprite.cords)
        return cls.tile_map

    @classmethod
    def new_block(cls, img, cords, b_type, superposition):
        """Creates a new block instance and adds it both to a superposition key based dictionary and pygame group"""
        new_block = cls(img, cords, b_type, superposition)
        cls.super_pos_dict[superposition] = new_block
        cls.block_list.add(new_block)

    def __init__(self, img, cords, b_type, superposition):
        super().__init__()
        self.image = img
        self.cords = cords
        self.superpos = superposition # coordinates in terms of blocks instead of pixels
        self.type = b_type

    def draw(self):
        """draws the block"""
        win.blit(self.image, self.cords)

    def update(self, g_map):
        """Updates the image of a given block"""
        self.image = never(self, g_map)

    def __str__(self):
        return self.type

    def __repr__(self):
        return self.type, self.cords

def tile_convert(g_map):
    """Turns a str text map into pygame group of blocks"""
    Block.init_surface(g_map)
    v = 0
    for item in g_map:
        h = 0
        for block_name in item:
            match block_name:
                case '0': # grass
                    x = random.randrange(0, 3) # chooses the grass variant
                    Block.new_block(pygame.transform.scale(grass_tile[x], (tile_size, tile_size)), (h*tile_size, v*tile_size), 'grass', (v, h))
                case '1': # water
                    Block.new_block(pygame.transform.scale(water_tile, (tile_size, tile_size)),
                                    (h * tile_size, v * tile_size), 'water', (v, h))
                case 'S':  # indicates special actions can be done.
                    # there are currently no use cases of this block type, nor planned usages
                    x = random.randrange(0, 3)
                    Block.new_block(pygame.transform.scale(grass_tile[x], (tile_size, tile_size)),
                                    (h * tile_size, v * tile_size), 'grass', (v, h))
                case _:
                    logging.warning("Block type not recognized")
                    pygame.draw.rect(Block.tile_map, (255, 0, 255), (h*tile_size, v*tile_size, tile_size, tile_size))
            h += 1
        v += 1
    for sprite in Block.block_list.sprites():
        if sprite.type == 'water':
            sprite.update(g_map) # finds the right type of water tile from its tile-set
    Block.update_surface()
    return Block.tile_map

def tile_img(sides, corners, origin):
    """Returns a tile image based on its 3x3 tile set. is a function instead of dict due to abstract categorization"""
    types_dict = {
        0: 'top',
        1: 'right',
        2: 'bot',
        3: 'left',
        10: 'top left corner',
        11: 'top right corner',
        12: 'bot right corner',
        13: 'bot left corner',
    }
    name = [place for place, block in enumerate(sides) if block != origin]
    if not name:
        name = [place for place, block in enumerate(corners) if block != origin]
        if name:
            name = name[0]+10 # this 10 is to differentiate corners in types_dict
            ret_name = types_dict[name]+'.png'
        else:
            ret_name = 'borderless.png'
    else:
        ret_name = []
        for index, thing in enumerate(name):
            ret_name.append(F'{types_dict[thing]} ')
        ret_name.sort(key=len) # this way the name is always top/bot then left/right instead of being un-ordered
        ret_name.append('border.png')
        ret_name = ''.join(ret_name)
    try:
        return load_asset(ret_name, 'tileset') # the tileset folder should later be changed to a variable
    except FileNotFoundError:
        logging.warning(F'tileset error: File, ({ret_name}) not found in tileset folder')
        return load_asset('borderless.png',  'tileset')

def safe_return(v, h, block):
    """Returns the type of block at position v, h. if no block exists it returns the inputted blocks type instead"""
    try:
        return Block.super_pos_dict[(v, h)].type
    except KeyError:
        return block.type

def never(block, g_map):
    """Returns the correct tile_image"""
    v = block.superpos[0]
    h = block.superpos[1]
    gonna = [
        safe_return(v - 1, h - 1, block), safe_return(v-1, h, block), safe_return(v - 1, h + 1, block),

        safe_return(v, h-1, block),                                   safe_return(v, h+1, block),

        safe_return(v + 1, h - 1, block), safe_return(v+1, h, block), safe_return(v + 1, h + 1, block)
    ] # this is just a list of surrounded block types

    give = gonna[1], gonna[4], gonna[6], gonna[3]

    you = gonna[0], gonna[2], gonna[7], gonna[5]

    up = pygame.transform.scale(tile_img(give, you, safe_return(v, h, block)), (tile_size, tile_size)) # do I need the third safe_return?
    return up


def format_game_map(map_id):
    """Turns a game_map textfile read into a proper game_map list
    see https://youtu.be/dQw4w9WgXcQ for a full explanation"""
    read_file = map_dict[map_id]
    row = []
    for char in read_file: # generates a row out of each line
        row.append(char.strip())
    temp_game_map = []
    for line in row: # makes each row a list of individual tiles.
        x = line.split(",")
        temp_game_map.append(x)
    for line in temp_game_map:
        for spot, value in enumerate(line):  # removes spaces from each row list
            if len(value)==2:
                line[spot] = value[1]
    return temp_game_map

def return_grids(corners, g_map):
    """Returns the game_map tiles colliding with each of the sprites corners"""
    gridlist = []
    for corner in corners:
            y = math.floor(corner[1] / tile_size) #  returns the nearest multiple of block_size
            x = math.floor(corner[0] / tile_size)
            gridlist.append(g_map[y][x])

    if gridlist.count('1') == len(gridlist):
        gridlist.append('f')
    return gridlist

