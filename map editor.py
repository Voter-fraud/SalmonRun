#initialisation
import copy, fishing_quests, reso_p, Decor
from config import math, random, map_mod, os, pygame, game_map
from map_mod import win
from textM import text_box, textbox_font
pygame.display.set_caption('Gamble core')
clock = pygame.time.Clock()
UI_scale = 2
#file loading
Decor.format_decor('Decor positions.txt')

spritelist = pygame.sprite.Group()

for sprite in Decor.HighDecor.decor_sprites.sprites():
    spritelist.add(sprite)

def save_game_info(length):
    file = open('custom_map.txt', 'w')  # w means write
    tilelisttemp = map_mod.Block.block_list.sprites()
    tilelist = []
    for c in range(0, length):
        row = []
        for tile in tilelisttemp:
            if int(tile.superpos[0]) == c:
                if tile.type == 'grass':
                    row.append('0')
                if tile.type == 'water':
                    row.append('1')
        tilelist.append(row)
    for line in tilelist:
        for char in line:
            file.write(F'{char}, ')
        file.write('\r')


def return_corners(cords, width, length): # cords must be inputted for easier checking of movement
    """Returns the cords of all 4 corners of a sprite in a tuple"""
    rect = pygame.Rect(cords[0], cords[1], width, length)
    return rect.center, rect.topleft, rect.topright, rect.bottomleft, rect.bottomright, rect.midleft, rect.midright,

class DecorSprite(pygame.sprite.Sprite):
    decor_sprites = pygame.sprite.Group()
    @classmethod
    def create_sprite(cls, image, cords, length, width):
        ret = cls(image, cords, length, width)
        spritelist.add(ret)
        cls.decor_sprites.add(ret)
        return ret

    def __init__(self, image, cords, length, width):
        super().__init__()
        self.image = image
        self.cords = cords[0]*map_mod.scale, cords[1]*map_mod.scale
        self.length = length
        self.width = width
        self.rect = self.image.get_rect(topleft=self.cords)

    def update(self):
        self.rect = self.image.get_rect(topleft=self.cords)

    def draw(self):
        win.blit(self.image, (self.cords[0]-xp, self.cords[1]-yp))

    def rescale(self):
        self.image = pygame.transform.scale(self.image, (self.length*map_mod.scale, self.width*map_mod.scale))

class Camera():
    """Player character long term information"""
    @classmethod
    def __init__(self):
        self.cords = [1800*map_mod.scale, 1200*map_mod.scale] # top left
        self.text_cur = False
        self.speed = 5
        self.can_move = True
        self.other_hold = False
        self.width = 16*map_mod.scale
        self.height = 32*map_mod.scale
        self.walking = False
        self.left_hold = 'grass'
        self.right_hold = Decor.LowDecor(Decor.decor_imgs['fern'], (0, 0), 32, 32, 'fern')


    @property
    def v_center(self):
        return reso_p.win_length / 2 - self.width / 2, reso_p.win_height / 2 - self.height / 2

    @property
    def corners(self):
        """Returns players corners"""
        return return_corners(self.cords, self.width, self.height)

    def update_can_move(self):
        if self.text_cur or self.other_hold:
            self.can_move = False
        else:
            self.can_move = True

    def sprint_toggle(self):
        if self.speed == 5:
            self.speed = 20
        elif self.speed == 20:
            self.speed = 5

    def inspect(self):
        for data_pair in map_mod.return_grids(corners=self.corners, g_map=game_map):
            if data_pair not in ('0', '1', '2', '3'):
                if data_pair != 'f':
                    if cam.text_cur:
                        cam.text_cur = False
                    else:
                        self.text_cur = dialouge_dict[data_pair]
                    return
                break
        if old_man.box.collidepoint(self.cords):
            old_man.talk()
            return
        if cam.text_cur:
            cam.text_cur = False

def return_ps():
    return cam.cords[1] - cam.v_center[1], cam.cords[0] - cam.v_center[0]

class Conversible(pygame.sprite.Sprite):
    talkables = []

    @classmethod
    def new(cls, name, img, linear_list, loop_list, cords, converse_box, func, width, height):
        new_c = cls(name, img, linear_list, loop_list, cords, converse_box, width, height)
        if func:
            new_c.func = func
        cls.talkables.append(new_c)
        spritelist.add(new_c)
        return new_c

    @classmethod
    def draw_convs(cls):
        for conv in cls.talkables:
            if isinstance(conv, Conversible):
                conv.draw()

    @classmethod
    def rescale(cls):
        for sprite in cls.talkables:
            sprite.image = pygame.transform.scale(sprite.image, (sprite.width*map_mod.scale, sprite.height*map_mod.scale))
            sprite.big_box = sprite.big_box[0]*map_mod.scale, sprite.big_box[1]*map_mod.scale

    def __init__(self, name, img, linear_list, loop_list, cords, converse_box, width, height):
        super().__init__()
        self.loop_list = loop_list
        self.linear_list = linear_list
        self.image = img
        self.name = name
        self.status = 0
        self.active = True
        self.cords = (cords[0]*map_mod.scale/2, cords[1]*map_mod.scale/2)
        self.rect = self.image.get_rect(topleft=self.cords)
        self.width = width
        self.height = height
        self.big_box = converse_box

    def __str__(self):
        return F'Name:{self.name}'

    def __repr__(self):
        return F'Name:{self.name}, Active:{self.active}, Line:{self.status}, Position:{self.cords}'

    @property
    def box(self):
        new_box = pygame.Rect(self.cords[0]-self.big_box[0]/2, self.cords[1]-self.big_box[1]/2, self.big_box[0], self.big_box[1])
        return new_box

    def talk(self):
        if self.active:
            cam.text_cur = self.linear_list[self.status]
            self.status += 1
        else:
            if self.status >= len(self.loop_list):
                self.status = 0
            if not cam.text_cur:
                cam.text_cur = self.loop_list[self.status]
                self.status += 1
            else:
                cam.text_cur = False
        if self.status == len(self.linear_list):
            self.active = False
            cam.text_cur = False
            self.status += 1
    def draw(self):
        win.blit(self.image, (self.cords[0]-xp, self.cords[1]-yp))



old_man_linear = [
    'my names Grobelc nice to meet you',
    'you must be new to these waters!',
    'theres a couple things that you should know',
    'First these fish spook easily',
    'second never trust the 1% ',
    'those bastards would drink the oceans dry if they could',
]
old_man_loop = ['Fishing takes my worries away', 'I could go for a beer right about now']
old_man_img = pygame.image.load('old_man_placehold.png')
old_man = Conversible.new('old_man', old_man_img, old_man_linear, old_man_loop, (3093.0, 2054.0), (64, 64), False, 24, 36)





dialouge_dict = { # get a better system later for inspection lines.
    'a': 'the mass of worms is wriggling and writhing',
    'b':  'why is it pink?',
    'd': 'this duck seems to be a daddy',
    'S': 'sell your fish here!',
    'O': 'womp womp'
}


cam = Camera()

def rescale_ui():
    global text_box, textbox_font
    text_box = pygame.transform.scale(text_box, (510*UI_scale, 70*UI_scale))
    textbox_font = pygame.font.SysFont('Comic Sans MS', 20*UI_scale)


def rescale_game():
    global duck, market
    rescale_ui()
    for sprite in spritelist.sprites():
        if not isinstance(sprite, Camera):
            sprite.rescale()
    for sprite in Decor.LowDecor.decor_sprites.sprites():
        sprite.rescale()
rescale_game()

def generate_surface():
    pss = return_ps()
    return map_mod.create_surface(game_map, pss[0], pss[1])
tile_map = generate_surface()

def draw_ui():
    small_font = pygame.font.SysFont('Comic Sans MS', 10)
    if cam.text_cur: # draws sprite inspection dialog
        win.blit(text_box, ((reso_p.win_length-510*UI_scale)/2, reso_p.win_height-80*UI_scale))
        win.blit(textbox_font.render(str(cam.text_cur), False, (0, 0, 0)), ((reso_p.win_length - 475 * UI_scale) / 2, reso_p.win_height - 65 * UI_scale))
    pos_p = (pos[0] + xp, pos[1] + yp)
    win.blit(small_font.render(str(pos_p), False, (0, 0, 0)), (700, 10))  # shows cursor cords
    win.blit(cam.right_hold.image, pos)

def dynamic_drawing():
    s_list = []
    spritelist_copy = spritelist.sprites().copy()
    for sprite in spritelist_copy:
        s_list.append((sprite.rect.bottomleft[1]))
        s_list.sort()
    while True:
        for sprite in spritelist_copy:
            if sprite.rect.bottomleft[1] == s_list[0]:
                if isinstance(sprite, Decor.HighDecor):
                    sprite.draw(xp, yp)
                else:
                    sprite.draw()
                s_list.pop(0)
                spritelist_copy.remove(sprite)
                break
        if not s_list and not spritelist_copy:
            return





def drawmap():
    """Draws map"""
    win.blit(tile_map, (0-xp, 0-yp))
    for spritedecor in Decor.LowDecor.decor_sprites.sprites():
        spritedecor.draw(xp, yp)
    dynamic_drawing()
    draw_ui()

def grid_ahead(cords, length, width):
    corners = return_corners(cords, length, width)
    return map_mod.return_grids(corners, game_map)

def handle_key_holds():
    if cam.can_move:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # make high-end functions more readable
            cam.cords[0] += -cam.speed
            cam.walking = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            cam.cords[0] += cam.speed
            cam.walking = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            cam.cords[1] += -cam.speed
            cam.walking = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            cam.facing = 'down'
            cam.cords[1] += cam.speed
            cam.walking = True
    if not cam.text_cur and keys[pygame.K_SPACE]:
        ''

def grab_pos():
    print(pos[0] + xp, pos[1] + yp)
    return pos[0] + xp, pos[1] + yp

timer = 0

decor_types = {
    'fern': 'Low',
    'bush1': 'high',
'bush2': 'high',
'duck': 'high',
}
rescale_game()

while True:
    pos = pygame.mouse.get_pos()
    ps = return_ps()
    yp, xp =  ps[0], ps[1]
    clock.tick(60)
    # timer
    timer += 1
    if timer > 9999:
        timer = 0
    #update fish then map
    for sprite in DecorSprite.decor_sprites.sprites():
        sprite.update()
    drawmap()
    cam.walking = False
    pygame.display.update()
    #keyholds
    keys = pygame.key.get_pressed()
    handle_key_holds()
    #event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                    cam.inspect()
            if event.key == pygame.K_ESCAPE:
                if cam.text_cur:
                    cam.text_cur = False
            if event.key == pygame.K_q:
                cam.sprint_toggle()
            if event.key == pygame.K_F11:
                reso_p.fullscreen_toggle() # toggles on or off full screen mode
            if event.key == pygame.K_F5:
                for sprite in map_mod.Block.block_list.sprites():
                    if sprite.type == 'water':
                        sprite.update(game_map)
                map_mod.Block.init_surface(game_map)
                tile_map = map_mod.Block.update_surface()
                for sprite in Decor.HighDecor.decor_sprites.sprites():
                    sprite.update()
                for sprite in Decor.LowDecor.decor_sprites.sprites():
                    sprite.update()
                rescale_game()

            if event.key == pygame.K_F7:
                save_game_info(80)
                Decor.store_decor('Decor positions.txt')
            #decor sprites
            if event.key == pygame.K_1:
                cam.right_hold = Decor.HighDecor(Decor.decor_imgs['duck'], (0, 0), 24, 24, 'duck')
            if event.key == pygame.K_2:
                cam.right_hold = Decor.HighDecor(Decor.decor_imgs['bush1'], (0, 0), 32, 32, 'bush1')
            if event.key == pygame.K_3:
                cam.right_hold = Decor.HighDecor(Decor.decor_imgs['bush2'], (0, 0), 32, 32, 'bush2')
            if event.key == pygame.K_4:
                cam.right_hold = Decor.LowDecor(Decor.decor_imgs['fern'], (0, 0), 32, 32, 'fern')
            if event.key == pygame.K_r:
                pos2 = grab_pos()
                for sprite in Decor.HighDecor.decor_sprites.sprites():
                    if sprite.rect.collidepoint(pos2[0], pos2[1]):
                        Decor.HighDecor.decor_sprites.remove(sprite)
                        spritelist.remove(sprite)
                for sprite in Decor.LowDecor.decor_sprites.sprites():
                    if sprite.rect.collidepoint(pos2[0], pos2[1]):
                        Decor.LowDecor.decor_sprites.remove(sprite)
        if event.type == pygame.MOUSEBUTTONDOWN:
            grab_pos() # prints cursor location useful for debugging
            if event.button == 1:
                pos2 = grab_pos()
                y = math.floor(pos2[1] / map_mod.tile_size)  # returns the nearest multiple of block_size
                x = math.floor(pos2[0] / map_mod.tile_size)
                for sprite in map_mod.Block.block_list.sprites():
                    if sprite.superpos == (y, x):
                        sprite.type = cam.left_hold.type
                        x= random.randrange(0, 2)
                        sprite.image = cam.left_hold.image

                map_mod.Block.init_surface(game_map)
                tile_map = map_mod.Block.update_surface()
            if event.button == 2:
                pos_t = grab_pos()
                pos2 = math.floor(pos_t[0]/map_mod.scale), math.floor(pos_t[1]/map_mod.scale)
                if isinstance(cam.right_hold, Decor.HighDecor):
                    new = Decor.HighDecor.create_sprite(cam.right_hold.image, pos2, cam.right_hold.length, cam.right_hold.width, cam.right_hold.name)
                    spritelist.add(new)
                if isinstance(cam.right_hold, Decor.LowDecor):
                    Decor.LowDecor.create_sprite(cam.right_hold.image, pos2, cam.right_hold.length, cam.right_hold.width, cam.right_hold.name)
            if event.button == 3:
                pos2 = grab_pos()
                y = math.floor(pos2[1] / map_mod.tile_size)  # returns the nearest multiple of block_size
                x = math.floor(pos2[0] / map_mod.tile_size)
                for sprite in map_mod.Block.block_list.sprites():
                    if sprite.superpos == (y, x):
                        cam.left_hold = copy.copy(sprite)

    cam.update_can_move() # checks whether the player should be able to move or not