import math, os, pygame, random, logging
from reso_p import win, win_heightw
from toolbox import load_asset
if win_heightw == 600:
    scale = 2
else:
    scale = 3
tile_size = 32*scale

grass_tile = [load_asset('center_grass.png', 'tileset'), load_asset('center_grass2.png', 'tileset')
, load_asset('center_grass3.png', 'tileset')] # you can always turn this into a list comprehension
water_tile = load_asset('center_water.png', 'tileset') # is this a wasted load?

map_dict = {
    'test': open('game_map.txt', 'r').readlines(),
    'custom': open('custom_map.txt', 'r').readlines()
}

class Block(pygame.sprite.Sprite):

    block_list = pygame.sprite.Group()
    tile_map = ''

    @classmethod
    def init_surface(cls, g_map):
        length = len(g_map)
        width = len(g_map[0])
        cls.tile_map = pygame.Surface((length * tile_size, width * tile_size))

    @classmethod
    def update_surface(cls):
        for sprite in cls.block_list.sprites():
            cls.tile_map.blit(sprite.image, sprite.cords)
        return cls.tile_map

    @classmethod
    def new_block(cls, img, cords, b_type, superposition):
        new_block = cls(img, cords, b_type, superposition)
        cls.block_list.add(new_block)

    def __init__(self, img, cords, b_type, superposition):
        super().__init__()
        self.image = img
        self.cords = cords
        self.superpos = superposition
        self.type = b_type

    def draw(self):
        win.blit(self.image, self.cords)

    def update(self, g_map):
        self.image = never(self, g_map)

    def __str__(self):
        return self.type

    def __repr__(self):
        return self.type, self.cords

def create_surface(g_map, xp, yp):
    length = len(g_map)
    width = len(g_map[0])
    surf = pygame.Surface((length*tile_size, width*tile_size))
    return tile_convert(g_map, xp, yp, surf)

def tile_convert(g_map, xp, yp, surface):
    Block.init_surface(g_map)
    v = 0
    for item in g_map:  # draws game debug map
        h = 0
        for blarg in item:  # square representations for debugging

            if blarg not in ('0', '1', '2', 'S'):
                pygame.draw.rect(Block.tile_map, (255, 0, 255), (h*tile_size, v*tile_size, tile_size, tile_size))
            if blarg == 'S':
                # pygame.draw.rect(drawn_surf, (0, 255, 200), (h*tile_size, v*tile_size, tile_size, tile_size))
                x = random.randrange(0, 3)
                # drawn_surf.blit(pygame.transform.scale(grass_tile[x], (tile_size, tile_size)), (h*tile_size, v*tile_size))
                Block.new_block(pygame.transform.scale(grass_tile[x], (tile_size, tile_size)),(h*tile_size, v*tile_size), 'grass', (v, h))
            if blarg == '1':
                # drawn_surf.blit(never(int(v), int(h), g_map), (h*tile_size, v*tile_size))
                Block.new_block(pygame.transform.scale(water_tile, (tile_size, tile_size)), (h*tile_size, v*tile_size), 'water', (v, h))
                # pygame.draw.rect(drawn_surf, (0, 0, 255), (h*tile_size, v*tile_size, tile_size, tile_size))
            if blarg == '0':
                # pygame.draw.rect(drawn_surf, (0, 255, 0), (h * tile_size, v * tile_size, tile_size, tile_size))
                x = random.randrange(0, 3)
                Block.new_block(pygame.transform.scale(grass_tile[x], (tile_size, tile_size)), (h*tile_size, v*tile_size), 'grass', (v, h))
                # drawn_surf.blit(pygame.transform.scale(grass_tile[x], (tile_size, tile_size)), (h*tile_size, v*tile_size))
            h += 1
        v += 1
    for sprite in Block.block_list.sprites():
        if sprite.type == 'water':
            sprite.update(g_map)
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
    try:
        for sprite in Block.block_list.sprites():
            if sprite.superpos == (v, h):
                if sprite.type not in ('water', 'grass'):
                    return 'grass'
                else:
                    return sprite.type
    except:
        logging.warning('Index Error')
        return block.type
def never(block, g_map):
    v = block.superpos[0]
    h = block.superpos[1]
    """Returns the correct tile_image"""
    gonna = [
        safe_return(v - 1, h - 1, block), safe_return(v-1, h, block), safe_return(v - 1, h + 1, block),

        safe_return(v, h-1, block),                                   safe_return(v, h+1, block),

        safe_return(v + 1, h - 1, block), safe_return(v+1, h, block), safe_return(v + 1, h + 1, block)
    ]

    print(gonna)

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

def create_water_list():
    """"""

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

