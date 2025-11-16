#initialisation
import copy, fishing_quests, reso_p, logging, real_menu_handler

import Decor, minigame
import toolbox
from config import math, random, map_mod, os, pygame, game_map, UI_scale
from map_mod import win
from toolbox import return_corners, load_asset
from textM import text_box, textbox_font
import inventory
pygame.display.set_caption('Gamble core')
clock = pygame.time.Clock()
#file loading
spritelist = pygame.sprite.Group()

walking_sound = pygame.mixer.Sound('walking sound.mp3')
rod_cast_sound = pygame.mixer.Sound('rod_cast.mp3')
rod_pull_sound = pygame.mixer.Sound('fishingrod pull.mp3')

def init_main():
    """Adds all decor into the game and then rescales everything"""
    for decor in Decor.HighDecor.decor_sprites.sprites():
        spritelist.add(decor)
    rescale_game()

class Fish(pygame.sprite.Sprite):
    fish_types = {
        # fishtype: (swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname)
        'salmon': (2, 1, 0.4, 1, 5, 'salmon'),
        'fish': (3, 3, 0.6, 1, 5, 'fish'),
        'carp': (3, 2, 1, 1, 5, 'carp'),
    }

    fish_lists = {} # the only comprehensive list of fish.
    for fish in fish_types.keys():
        fish_lists[fish] = pygame.sprite.Group()

    fish_caught = False # checks if a fish is circling the hook when gravity is added remove this
    fish_took = False # keeps track of if a fish is on the hook

    fish_frames = { # add vector based rotations for fish movemont
            '[0, -1]': load_asset('fishup1.png', 'fish scheiße'),
            '[0, 1]': load_asset('fishdown1.png','fish scheiße' ),
            '[-1, 0]': load_asset('fishleft1.png','fish scheiße' ),
            '[1, 0]': load_asset('fishright1.png', 'fish scheiße' ),
            'spc': load_asset('collide.png', 'fish scheiße' ),
            '1': load_asset('fishcircle1.png', 'fish scheiße' ),
            '2': load_asset('fishcircle2.png', 'fish scheiße' ),
            '3': load_asset('fishcircle3.png', 'fish scheiße' ),
            '4': load_asset('fishcircle4.png', 'fish scheiße' ),
        }

    @classmethod
    def rescale(cls):
        """Rescales fish images to current resolution"""
        for key, value in cls.fish_frames.items():
            cls.fish_frames[key] = pygame.transform.scale(value, (16*map_mod.scale, 16*map_mod.scale))
            for species_list in cls.fish_lists.values(): # 16 represents base side lengths
                for fish in species_list:
                    fish.rect = fish.image.get_rect()
                    fish.rect.height = 16 * map_mod.scale
                    fish.rect.width = 16 * map_mod.scale

    @classmethod
    def create_fish(cls, cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, item):
        """creates a new fish instance in the fish_list sprite group"""
        new = Fish(cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, item)
        cls.fish_lists[item].add(new)
        spritelist.add(new)
        return new

    @classmethod
    def update_fish(cls):
        """updates each fishes center and returns any hook collisions if applicable"""
        for species_list in cls.fish_lists.values():
            for fish in species_list:
                fish.center = (fish.cords[0]-8, fish.cords[1]-8) # updates center
                if player.hook_cords and not cls.fish_caught:
                    # check for hook collisions
                    fish.rect.topleft = fish.cords # updates the fishes hit-boxes. This only happens when a hook is cast to save resources
                    if fish.rect.collidepoint(player.hook_cords[0], player.hook_cords[1]) and not fish.ignore:
                        cls.fish_caught = fish # returns a class instance if there is a collision
                elif cls.fish_caught:
                    return cls.fish_caught
            # else: cls.fish_caught = False (Seemed to not be needed)
        return False # returns false if no fish is colliding

    @classmethod
    def fish_moving(cls):
        """Handles predictable fish movements"""
        for species_list in cls.fish_lists.values():
            if timer%10 == 0: # handles expensive operations such as swerving and baiting.
                for fish in species_list:
                    if not fish.baited() and timer%60 and fish != cls.fish_caught:
                        # every second active fishes get a chance to swerve
                        fish.fish_swerve()
                    elif fish == cls.fish_caught and not cls.fish_took:
                        # handles deciding when a circling fish grabs onto the hook
                        x = random.randrange(-300, 10)
                        if x > 0:
                            cls.fish_took = fish
                    elif fish == cls.fish_caught and cls.fish_took:
                        # handles deciding when a fish which grabbed onto the hook will run away
                        y = random.randrange(-490, 15)
                        if y > 0 and game_state != 'minigame':
                            player.hook_cords = False
                            cls.fish_took = False
                            cls.fish_caught = False
            for fish in species_list:
                # moves fish along their current trajectory. This is not a super expensive operation so it is handled every tick.
                if fish != cls.fish_caught:
                    fish.fish_move()

    def __init__(self, cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, item):
        super().__init__()
        self.image = load_asset('fishleft1.png','fish scheiße') # change later to relate to a dict that matches fish type to image
        self.rect = self.image.get_rect() # creates rect for sprite class
        self.cords = (cords[0], cords[1]) #topleft cords of the fish
        self.center = (self.cords[0]-8, self.cords[1]-8) #central fish cords
        self.speed = f_speed*map_mod.scale
        self.swerving = swerving # measure of how unpredictable the fish is when it turns
        self.un_decisiveness = un_decisiveness # measure of how often a fish turns
        self.vector = [1, 0]
        self.id = f_id
        self.box = self.rect.center = self.center[0]+self.vector[0]*16*map_mod.scale, self.center[1]+self.vector[1]*16*map_mod.scale
        self.circ_frame = 1
        self.ignore = 4
        self.cautiousness = cautiousness
        self.item = inventory.Item.new(item)
        self.side_length = 16

    def __str__(self):
        return self.cords

    def __repr__(self):
        return F'ID:{self.id}, cords:{self.cords}, vector:{self.vector}'

    def draw(self):
        if Fish.fish_caught == self and player.hook_cords:  # draws the fish circling the hook and handles frame logic
            if game_state == 'minigame':
                win.blit(Fish.fish_frames[str(self.vector)],
                         (player.hook_cords[0] - xp - 6 * map_mod.scale, player.hook_cords[1] - yp - 6 * map_mod.scale))
            else:
                win.blit(Fish.fish_frames[str(self.circ_frame)],
                         (player.hook_cords[0] - xp - 6 * map_mod.scale, player.hook_cords[1] - yp - 6 * map_mod.scale))
                if timer % 12 == 0:
                    self.circ_frame = (self.circ_frame % 4 + 1)
            if Fish.fish_took:
                win.blit(Fish.fish_frames['spc'], (
                    player.hook_cords[0] - xp - 6 * map_mod.scale, player.hook_cords[1] - yp - 6 * map_mod.scale))
        else:
            win.blit(Fish.fish_frames[str(self.vector)],
                     (self.cords[0] - xp, self.cords[1] - yp))  # should be changed to a rotation based on vector


    def fish_swerve(self): # replace with gravity
        """Makes the fish instance change direction based on swerving and un_decisiveness instance properties"""
        new_vector = self.vector
        ranlist = (-1, 1)
        x = random.randrange(-10, self.un_decisiveness)
        if 0 < x:
            new_vector.reverse()
            if new_vector[0] == 0:
                new_vector[1] = ranlist[random.randrange(-1, 1)]
                new_vector[0] = 0
            else:
                new_vector[0] = ranlist[random.randrange(-1, 1)]
                new_vector[1] = 0
            self.vector = new_vector


    def fish_move(self):
        """Makes the fish instance move based on speed and direction instance properties"""
        x = self.cords[0]
        y = self.cords[1]
        new_vector = self.vector
        ranlist = (-1, 1)
        escape = 1
        while True:
            if 'f' == grid_ahead((x+self.vector[0]*self.speed+(10*self.vector[0]*map_mod.scale), y+self.vector[1]*self.speed+(10*self.vector[1]*map_mod.scale)), 16*map_mod.scale, 16*map_mod.scale)[-1]: # plus 20 is to keep the fish off of the sand
                self.cords = x + self.vector[0]*self.speed, y + self.vector[1]*self.speed
                return
            else:
                if 0 in self.vector: # potentially keepable with a little variation for gravity
                    new_vector.reverse()
                    if new_vector[0] == 0:
                        new_vector[1] = ranlist[random.randrange(-1, 1)]
                        new_vector[0] = 0
                    else:
                        new_vector[0] = ranlist[random.randrange(-1, 1)]
                        new_vector[1] = 0
                self.vector = new_vector
            escape += 1
            if escape == 10:
                logging.warning('fish may be trapped')
                break



    def baited(self): # sadly has to be probably changed a bit
        if self.ignore > 0:
            self.ignore -= 1
        elif player.hook_cords:
            dif = abs(player.hook_cords[0] - self.cords[0]) + abs(player.hook_cords[1] - self.cords[1])
            if dif > player.baitlevel * 3 + 64*map_mod.scale:
                return False
            ret = fun_box_check(self.cords, self.vector, True, True, 16*map_mod.scale, 16*map_mod.scale, player.baitlevel/3, player.baitlevel/3)
            if ret:
                self.vector = ret
                return True
            ret = fun_box_check(self.cords, self.vector, True, False, 16*map_mod.scale, 16*map_mod.scale, player.baitlevel/3, player.baitlevel/3)
            if ret:
                self.vector = ret
                return True
            ret = fun_box_check(self.cords, self.vector, False, False, 16*map_mod.scale, 16*map_mod.scale, player.baitlevel, player.baitlevel)
            if ret:
                self.vector = ret
                return True
        return False

    @classmethod
    def scared_check(cls):
        """scares fishes away from the hook when first cast"""
        check_radius = 60*map_mod.scale
        if player.hook_cords:
            for species_list in cls.fish_lists.values():
                for fish in species_list:
                    difx, dify = abs(player.hook_cords[0] - fish.cords[0]), abs(player.hook_cords[1] - fish.cords[1])
                    expx, expy = abs(player.hook_cords[0] - fish.cords[0]+fish.vector[0]), abs(player.hook_cords[1] - fish.cords[1]+fish.vector[1])
                    dif = math.sqrt(difx*difx+dify*dify) # checks absolute distance between fish and your hook
                    e_dif = math.sqrt(expx * expx + expy * expy) # checks if you are moving away or towards the hook
                    if dif <= check_radius and dif < e_dif: # if within a circle within radius 64 and the fish is moving towards you turn it around
                        fish.vector.reverse()
                        fish.ignore = 50 # makes the fish not be tricked by the bait for 500 ticks



def fun_box_check(topleft, orig_vector, check_inverse, check_reflection, width, length, check_length, check_width):
    """Returns the vector needed to move towards a nearby point"""
    prime_vector = orig_vector.copy()
    if check_inverse:
        prime_vector.reverse()
    if check_reflection:
        prime_vector[0] *= -1
        prime_vector[1] *= -1
    box_width, box_length = width + abs(prime_vector[0] * check_length), length + abs(prime_vector[1] * check_width)
    box2 = pygame.Rect(0, 0, box_width, box_length)
    if 1 in prime_vector:
        box2.topleft = topleft[0] + prime_vector[0] * width, topleft[1] + prime_vector[1] * length
    elif -1 in prime_vector and not check_inverse and not check_reflection:
        box2.topleft = (topleft[0] + prime_vector[0] * width + prime_vector[0] * player.baitlevel, topleft[1] +
                        prime_vector[1] * length + prime_vector[1] * player.baitlevel)
    elif -1 in prime_vector:
        box2.topleft = topleft[0] + prime_vector[0] * width + prime_vector[0] * player.baitlevel/3, topleft[1] + \
                       prime_vector[1] * length + prime_vector[1] * player.baitlevel/3
    if box2.collidepoint(player.hook_cords[0], player.hook_cords[1]):
        return prime_vector
    return False

class FishSpawner:
    FishSpawners = []

    @classmethod
    def new(cls, cords, fish_dict, cap, rang):
        new = FishSpawner(cords, fish_dict, cap, rang)
        cls.FishSpawners.append(new)
        return new

    @classmethod
    def spawn_all(cls):
        for spawner in cls.FishSpawners:
            spawner.spawn()

    def __init__(self, cords, fish_dict, cap, rang):
        self.cords = cords[0], cords[1]
        self.spawns = fish_dict
        tot = 0
        special_dict = {}
        for key, value in fish_dict.items():
            prevtot = tot
            tot += value
            special_dict[key] = (prevtot+1, tot)
        self.tot = tot
        self.spwn_list = special_dict
        self.cap = cap
        self.cur = pygame.sprite.Group()
        self.range = rang*map_mod.scale # range is half a square length. Not using circles because I have no real reason to

    def spawn(self):
        if  len(self.cur.sprites()) < self.cap:
            cords =0,0
            run = True
            while run:
                cords = [self.cords[0]*map_mod.scale+random.randrange(-self.range, self.range), self.cords[1]*map_mod.scale+random.randrange(-self.range, self.range)]
                if 'f' in grid_ahead(cords,  16*map_mod.scale, 16*map_mod.scale):
                    run = False
            r = random.randrange(0, self.tot)
            for key, value in self.spwn_list.items():
                if value[0] < r <= value[1]:
                    swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname = Fish.fish_types[key]

                    new = Fish.create_fish(cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname)
                    self.cur.add(new)

FishSpawner.new([1500, 1191], {
    'fish': 3,
    'carp': 4,
    'salmon': 0,
}, 3, 120)
FishSpawner.new([1500, 1191], {
    'fish': 2,
    'carp': 4,
    'salmon': 0,
}, 5, 500 )
FishSpawner.new([1350, 775], {
    'fish': 0,
    'carp': 0,
    'salmon': 4,
}, 6, 75 )
Fish.rescale()
Fish.update_fish()

class PlayerSprite(pygame.sprite.Sprite):
    """Player character long term information"""
    walking_anim = { # Ew
        'down': (load_asset('buff generic guy w1.png', 'player' ), load_asset('buff generic guy w1.png', 'player'), load_asset('buff generic guy w1.png', 'player'), load_asset('buff generic guy w2.png', 'player' ), load_asset('buff generic guy w2.png', 'player'), load_asset('buff generic guy w2.png', 'player')),
        'up': (load_asset('buff generic guy bw1.png', 'player'), load_asset('buff generic guy bw1.png', 'player' ), load_asset('buff generic guy bw1.png', 'player'), load_asset('buff generic guy bw2.png', 'player'),  load_asset('buff generic guy bw2.png', 'player'), load_asset('buff generic guy bw2.png', 'player')),
        'right': (load_asset('buff generic guy rw1.5.png', 'player'), load_asset('buff generic guy rw1.png', 'player'), load_asset('buff generic guy rw1.5.png', 'player'), load_asset('buff generic guy rw2.5.png', 'player'),  load_asset('buff generic guy rw2.png', 'player'), load_asset('buff generic guy rw2.5.png', 'player')),
        'left': (load_asset('buff generic guy lw1.5.png', 'player'), load_asset('buff generic guy lw1.png', 'player'), load_asset('buff generic guy lw1.5.png', 'player'), load_asset('buff generic guy lw2.5.png', 'player'), load_asset('buff generic guy lw2.png', 'player'), load_asset('buff generic guy lw2.5.png', 'player'))
    }

    fishing_anim = {
        'down': [load_asset(F'buff generic guy F{x}.png', 'player') for x in range(1, 4)],

        'up': [load_asset(F'buff generic guy bF{x}.png', 'player') for x in range(1, 4)],

        'left': [load_asset(F'buff generic guy lF{x}.png', 'player') for x in range(1, 4)],

        'right': [load_asset(F'buff generic guy rF{x}.png', 'player') for x in range(1, 4)],
    }

    still = {
        'down': load_asset('buff generic guy.png', 'player'),
        'up': load_asset('buff generic guy b.png', 'player'),
        'left': load_asset('buff generic guy l.png', 'player'),
        'right': load_asset('buff generic guy r.png', 'player'),
    }

    fish_passive = {
        'down': load_asset('buff generic guy F1b.png', 'player'),
        'up': load_asset('buff generic guy bF1b.png', 'player'),
        'left': load_asset('buff generic guy lF1b.png', 'player'),
        'right': load_asset('buff generic guy rF1b.png', 'player'),
    }

    @classmethod
    def rescale_player(cls):
        for key, value in cls.walking_anim.items():
            cls.walking_anim[key] = (pygame.transform.scale(value[0], (16 * map_mod.scale, 32 * map_mod.scale)),
                                     pygame.transform.scale(value[1], (16 * map_mod.scale, 32 * map_mod.scale)),
                                     pygame.transform.scale(value[2],(16 * map_mod.scale, 32 * map_mod.scale)),
                                     pygame.transform.scale(value[3], (16 * map_mod.scale, 32 * map_mod.scale)),
                                     pygame.transform.scale(value[4], (16 * map_mod.scale, 32 * map_mod.scale)),
                                     pygame.transform.scale(value[5], (16 * map_mod.scale, 32 * map_mod.scale)))
        for key, value in cls.fishing_anim.items():
            if key == 'left' or key == 'right':
                cls.fishing_anim[key] = (pygame.transform.scale(value[0], (16 * map_mod.scale, 32 * map_mod.scale)),
                                         pygame.transform.scale(value[1], (16 * map_mod.scale, 32 * map_mod.scale)),
                                         pygame.transform.scale(value[2], (20 * map_mod.scale, 32 * map_mod.scale)))
            else:
                cls.fishing_anim[key] = (pygame.transform.scale(value[0], (16 * map_mod.scale, 32 * map_mod.scale)),
                                         pygame.transform.scale(value[1], (16 * map_mod.scale, 32 * map_mod.scale)),
                                         pygame.transform.scale(value[2], (16 * map_mod.scale, 32 * map_mod.scale)))
        for key, value in cls.still.items():
            cls.still[key] = pygame.transform.scale(value, (16 * map_mod.scale, 32 * map_mod.scale))
        for key, value in cls.fish_passive.items():
            cls.fish_passive[key] = pygame.transform.scale(value, (16 * map_mod.scale, 32 * map_mod.scale))

    def __init__(self):
        super().__init__()
        self.bauble = load_asset('bauble.png','player')
        self.cords = [1800*map_mod.scale, 1200*map_mod.scale] # top left
        self.text_cur = False
        self.facing = 'up'
        self.hook_cords = [] # if empty hook is not cast
        self.speed = 5
        self.cast_length = 0
        self.can_move = True
        self.fish_hold = False
        self.baitlevel = 20
        self.width = 16*map_mod.scale
        self.height = 32*map_mod.scale
        self.rect = PlayerSprite.still['up'].get_rect(topleft=self.cords)
        self.walking = False
        self.walking_frame = 0
        self.boot_cords = [reso_p.win_length / 2, reso_p.win_height / 2-self.height/4]
        self.noclip = False

    @property
    def v_center(self):
        return reso_p.win_length / 2 - self.width / 2, reso_p.win_height / 2 - self.height / 2

    def draw(self):
        """Draws player sprite"""
        if self.walking:
            win.blit(PlayerSprite.walking_anim[self.facing][self.walking_frame], self.v_center)
            if timer % 10 == 0:
                self.walking_frame += 1
                if self.walking_frame == 6:
                    self.walking_frame = 0
        elif self.hook_cords:
            if self.facing == 'down':
                win.blit(PlayerSprite.fish_passive[self.facing], self.v_center)
                toolbox.draw_line(self.rect.topleft, (self.hook_cords[0] + 1.3*map_mod.scale, self.hook_cords[1]), (255, 255, 255), win,
                                  xp, yp, 1)
                toolbox.draw_line(self.rect.topleft, (self.rect.center[0], self.rect.center[1]+4*map_mod.scale), (139,69,19), win, xp, yp, 3)
            elif self.facing == 'up':
                connector = [self.rect.topright[0]-3*map_mod.scale, self.rect.topright[1]-3*map_mod.scale]
                toolbox.draw_line(connector, (self.hook_cords[0] + 1.3*map_mod.scale, self.hook_cords[1]), (255, 255, 255), win,
                                  xp, yp, 1)
                toolbox.draw_line(connector, (self.rect.center[0], self.rect.center[1]+4*map_mod.scale), (139,69,19), win, xp, yp, 3)
                win.blit(PlayerSprite.fish_passive[self.facing], self.v_center)
            elif self.facing == 'left':
                connector = [self.rect.topleft[0] - 20, self.rect.topright[1] + 15]
                toolbox.draw_line(connector, (self.hook_cords[0] + 1.3*map_mod.scale, self.hook_cords[1]), (255, 255, 255), win,
                                  xp, yp, 1)
                toolbox.draw_line(connector, (self.rect.center[0] - 1 * map_mod.scale, self.rect.center[1]),
                                  (139, 69, 19), win, xp, yp, 3)
                win.blit(PlayerSprite.fish_passive[self.facing], self.v_center)
            elif self.facing == 'right':
                connector = [self.rect.topright[0]+20, self.rect.topright[1]+15]
                toolbox.draw_line(connector, (self.hook_cords[0] + 1.3*map_mod.scale, self.hook_cords[1]), (255, 255, 255), win,
                                  xp, yp, 1)
                toolbox.draw_line(connector, (self.rect.center[0]+1*map_mod.scale, self.rect.center[1]), (139,69,19), win, xp, yp, 3)
                win.blit(PlayerSprite.fish_passive[self.facing], self.v_center)
        elif self.cast_length:
            if math.floor(self.cast_length/10) >= 2 and self.facing == 'right':
                win.blit(PlayerSprite.fishing_anim[self.facing][2], (self.v_center[0]-4*map_mod.scale, self.v_center[1]))
            elif math.floor(self.cast_length / 10) < 3:
                win.blit(PlayerSprite.fishing_anim[self.facing][math.floor(self.cast_length / 10)], self.v_center)
            else:
                win.blit(PlayerSprite.fishing_anim[self.facing][2],
                         (self.v_center[0], self.v_center[1]))
        else:
            win.blit(PlayerSprite.still[self.facing], self.v_center)
    @property
    def xp_yp(self):
        return self.cords[1] - self.v_center[1], self.cords[0] - self.v_center[0]

    @property
    def corners(self):
        """Returns players corners"""
        return return_corners(self.cords, self.width, self.height)

    def check_obst(self, dist, ):
        """returns the cords of your projected travel"""
        x = self.cords[0]
        y = self.cords[1]
        if self.facing == 'up':
            y -= dist
        elif self.facing == 'down':
            y += dist
        elif self.facing == 'left':
            x -= dist
        elif self.facing == 'right':
            x += dist
        return x, y

    def cast_rod(self, dist):
        """Casts your fishing rod"""
        rod_cast_sound.play()
        new_box = copy.copy(self.rect)
        new_box.topleft = self.check_obst(dist)
        if self.facing == 'up':
            check = new_box.midtop[0], new_box.midtop[1]-10*map_mod.scale
        elif self.facing == 'down':
            check = new_box.midbottom[0], new_box.midbottom[1]+10*map_mod.scale
        elif self.facing == 'left':
            check = new_box.midleft[0]-10*map_mod.scale, new_box.midleft[1]
        elif self.facing == 'right':
            check = new_box.midright[0]+10*map_mod.scale, new_box.midright[1]
        else:
            logging.warning('player does not have a direction')
            return 'player has no position'
        try:
            if '1' in map_mod.return_grids((check, check), game_map): # checks to make sure the rod is going into water
                self.hook_cords = check # sets hook cords for fish collisions
        except IndexError:
            logging.warning('Player attempted to fish outside of game') # add some numerous comments for trying to do this in game
        Fish.scared_check()

    def update_can_move(self):
        if self.text_cur or self.fish_hold or self.hook_cords:
            self.can_move = False
        else:
            self.can_move = True

    def stop_fishing(self):
        Fish.fish_caught = False
        Fish.fish_took = False
        self.hook_cords = False
        self.fish_hold = False

    def sprint_toggle(self):
        if self.speed == 5:
            self.speed = 20
        elif self.speed == 20:
            self.speed = 5

    def update(self):
        self.rect.topleft = self.cords
        self.rect.height = self.height
        self.rect.width = self.width

    def inspect(self):
        if self.rect.colliderect(old_man.box):
            old_man.talk()
            return
        if player.text_cur:
            player.text_cur = False

class StatTracker:
    def __init__(self, linked_player):
        self.player = linked_player
        self.fish_caught = inventory.Item.ret_items('is_fish')
        self.fish_sold = inventory.Item.ret_items('is_fish')

    def catch_fish(self, fish_name):
        self.fish_caught[fish_name] += 1
        self.fish_caught['total'] += 1
        if isinstance(cur_quest, fishing_quests.FishCatching):
            cur_quest.update(player_tracker.fish_caught)

    def sell_fish(self, fish_name):
        self.fish_sold[fish_name] += 1
        self.fish_sold['total'] += 1
        if isinstance(cur_quest, fishing_quests.FishSelling):
            cur_quest.update(player_tracker.fish_sold)

class FishingRod:
    def __init__(self, use_anim, max_cast, lure):
        self.frames = use_anim
        self.max_cast = max_cast
        self.lure = lure

class Balance:
    def __init__(self, bal, game_long_balance):
        self.image = load_asset('coin_counter.png')
        self.f_cords = (reso_p.win_length-73*UI_scale, 34*UI_scale)
        self.color = (0, 0, 0)
        self.cords = (reso_p.win_length-110*UI_scale, 32*UI_scale)
        self.bal = bal
        self.total = game_long_balance
        self.font = pygame.font.SysFont('Comic Sans MS', 30)  # this is only one font size

    def draw(self):
        win.blit(self.image, self.cords)
        win.blit(self.font.render(str(self.bal), False, self.color), self.f_cords)

    def add_money(self, amount):
        self.bal += amount
        self.total += amount

    def use_money(self, amount):
        self.bal -= amount

    def rescale(self):
        self.image = pygame.transform.scale(self.image, (100*UI_scale, 50*UI_scale))
        self.font = pygame.font.SysFont('Comic Sans MS', 30*UI_scale)

balance = Balance(0, 0)

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
        for rescalible in cls.talkables:
            rescalible.image = pygame.transform.scale(rescalible.image, (rescalible.width*map_mod.scale, rescalible.height*map_mod.scale))
            rescalible.big_box = rescalible.big_box[0]*map_mod.scale, rescalible.big_box[1]*map_mod.scale

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
        if isinstance(cur_quest, fishing_quests.TalkTo):
            cur_quest.update(self)
        if self.active:
            player.text_cur = self.linear_list[self.status]
            self.status += 1
        else:
            if self.status >= len(self.loop_list):
                self.status = 0
            if not player.text_cur:
                player.text_cur = self.loop_list[self.status]
                self.status += 1
            else:
                player.text_cur = False
        if self.status == len(self.linear_list):
            self.active = False
            player.text_cur = False
            self.status += 1

    def draw(self):
        win.blit(self.image, (self.cords[0]-xp, self.cords[1]-yp))

old_man_linear1 = [
    'My names PLACEHOLDER nice to meet you',
    'You must be new to these waters!',
    "I'll show you how to get started",
    "to cast your fishing rod...",
    "Hold space then release",
    "To catch a fish interested in your hook... ",
    "wait until bubbles form... ",
    "then press space again",
    "Now go and catch 3 fishes"
]
old_man_seller = [
    'Nice job catching those fish',
    'To sell a fish go to the market...',
    'and drag the fish from your inventory...',
    'onto the market.',
    ''
]
old_man_salmon = [
    'There are many types of fish here',
    'Catch and sell 2 salmon for me',
    'Salmon can be found in the river above us.',
    ''
]
old_man_loop = ['Fishing takes my worries away', 'I could go for a beer right about now']
old_man_img = pygame.image.load('old_man_placehold.png')
old_man = Conversible.new('old_man', old_man_img, old_man_linear1, old_man_loop, (3093.0, 2054.0), (64, 64), False, 24, 36)

player = PlayerSprite()
player_tracker = StatTracker(player)
spritelist.add(player)

quests = [
# start game with dialouge lines of the character wishing they could get a cool boat for fishing and leisure
fishing_quests.TalkTo(old_man, load_asset('talk to.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 10), old_man_linear1),
fishing_quests.FishCatching(1, False, player_tracker.fish_caught, load_asset('catch fish.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 20), 'Catch 3 Fish'),
fishing_quests.TalkTo(old_man, load_asset('talk to.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 10), old_man_seller),
fishing_quests.FishSelling(1, False, player_tracker.fish_sold, load_asset('sell fish.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 20), 'Sell 3 fish'),
fishing_quests.TalkTo(old_man, load_asset('talk to.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 10), old_man_salmon),
fishing_quests.FishCatching(1, 'salmon', player_tracker.fish_caught, load_asset('catch fish.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 20), 'Catch 2 salmon'),
fishing_quests.FishSelling(1, 'salmon', player_tracker.fish_sold, load_asset('sell fish.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 20), 'Sell 3 fish'),
]

cur_quest = quests[0]

def rescale_ui():
    global text_box, textbox_font
    text_box = pygame.transform.scale(text_box, (510*UI_scale, 70*UI_scale))
    textbox_font = pygame.font.SysFont('Comic Sans MS', 20*UI_scale)
    inventory.Inventory.rescale()
    balance.rescale()

def rescale_game():
    rescale_ui()
    for sprite in spritelist.sprites():
        if not isinstance(sprite, PlayerSprite):
            sprite.rescale()
    for sprite in Decor.LowDecor.decor_sprites.sprites():
        sprite.rescale()
    player.rescale_player()

def generate_surface():
    pss = player.xp_yp
    return map_mod.create_surface(game_map, pss[0], pss[1])

def draw_notifications():
    if cur_quest.mode == 'start':
        cur_quest.start(timer,  player_tracker.fish_caught)
    elif cur_quest.mode == 'finish':
        cur_quest.finish(timer)
    elif not cur_quest.mode:
        ''

def draw_ui():
    balance.draw()
    inventory.inventory.draw(pos)
    small_font = pygame.font.SysFont('Comic Sans MS', 10)
    if player.text_cur: # draws sprite inspection dialog
        win.blit(text_box, ((reso_p.win_length-510*UI_scale)/2, reso_p.win_height-80*UI_scale))
        win.blit(textbox_font.render(str(player.text_cur), False, (0, 0, 0)), ((reso_p.win_length-475*UI_scale)/2, reso_p.win_height-65*UI_scale))
    pos_p = (pos[0] + xp, pos[1] + yp)
    win.blit(small_font.render(str(pos_p), False, (0, 0, 0)), (700, 10))  # shows cursor cords
    cur_quest.draw(UI_scale)

def dynamic_drawing():
    """Draws inputted sprites in order of how high their Y cord is for example y=5 is drawn over y=4"""
    s_list = [] # becomes list of sprites to draw in order
    spritelist_copy = spritelist.sprites().copy() # initial list of sprites
    for sprite in spritelist_copy:
        s_list.append((sprite.rect.bottomleft[1])) # tracks each sprites bottom coordinates
        s_list.sort()
    while True:
        for sprite in spritelist_copy:
            if sprite.rect.bottomleft[1] == s_list[0]: # looks through the initial list of sprites for a match
                if isinstance(sprite, Decor.HighDecor): #draws the matched sprite
                    sprite.draw(xp, yp)
                else:
                    sprite.draw()
                s_list.pop(0) # removes the drawn sprite so the process can start again
                spritelist_copy.remove(sprite)
                break
        if not s_list and not spritelist_copy: # if there is no more sprites to draw end the process
            return

def drawmap():
    """Draws player map"""
    win.blit(tile_map, (0-xp, 0-yp))
    if player.hook_cords:
        win.blit(player.bauble, (player.hook_cords[0]-xp, player.hook_cords[1]-yp))
    for spritedecor in Decor.LowDecor.decor_sprites.sprites():
        spritedecor.draw(xp, yp)
    dynamic_drawing()
    draw_ui()
    draw_notifications()

def grid_ahead(cords, length, width):
    corners = return_corners(cords, width, length)
    return map_mod.return_grids(corners, game_map)

def check_walkable(noclip, dist):
    if noclip:
        return True
    if '1' in grid_ahead(player.check_obst(dist), player.height, player.width):
        return False
    if '3' in grid_ahead(player.check_obst(dist), player.height, player.width):
        return False
    return True

def handle_key_holds():
    if player.can_move:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # make high-end functions more readable
            player.facing = 'left'
            if check_walkable(player.noclip, player.speed):
                player.cords[0] += -player.speed
            elif check_walkable(player.noclip, 1):
                player.cords[0] += -1
            player.walking = True

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.facing = 'right'
            if check_walkable(player.noclip, player.speed):
                player.cords[0] += player.speed
            elif check_walkable(player.noclip, 1):
                player.cords[0] += 1
            player.walking = True

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.facing = 'up'
            if check_walkable(player.noclip, player.speed):
                player.cords[1] += -player.speed
            elif check_walkable(player.noclip, 1):
                player.cords[1] += -1
            player.walking = True

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.facing = 'down'
            if check_walkable(player.noclip, player.speed):
                player.cords[1] += player.speed
            elif check_walkable(player.noclip, 1):
                player.cords[1] += 1
            player.walking = True

        if player.walking:
            if timer%30 == 0:
                walking_sound.play()

    if not player.hook_cords and not player.text_cur and keys[pygame.K_SPACE]:
        if not player.fish_hold:
            player.fish_hold = True
        player.cast_length += 1

def grab_pos():
    print(pos[0] + xp, pos[1] + yp)
    return pos[0] + xp, pos[1] + yp
timer = 0

def handle_rod():
    global game_state
    if player.hook_cords and hooked_fsh:
        if Fish.fish_took == hooked_fsh: # if fish is catchable when you pull the rod
            minigame.reset()
            game_state = 'minigame'

init_main()
tile_map = generate_surface()
game_state = 'main'
while True:
    walking_sound.set_volume(real_menu_handler.sound/100)
    rod_pull_sound.set_volume(real_menu_handler.sound/100)
    rod_cast_sound.set_volume(real_menu_handler.sound/100)
    pos = pygame.mouse.get_pos()
    ps = player.xp_yp
    yp, xp =  ps[0], ps[1]
    clock.tick(60)
    # timer
    timer += 1
    if timer > 9999:
        timer = 0
    if timer % 120 == 0:
        if not cur_quest.live:
            quests.pop(0)
            cur_quest = quests[0]
            if isinstance(cur_quest, fishing_quests.TalkTo):
                old_man.linear_list = cur_quest.newtext
                old_man.status = 0
                old_man.active = True
        FishSpawner.spawn_all()

    #update fish then map
    hooked_fsh = Fish.update_fish() # checks to see if a fish is on the hook.
    Fish.rescale()
    player.update()
    for decorr in Decor.HighDecor.decor_sprites.sprites():
        decorr.update()
    drawmap()
    player.walking = False
    Fish.fish_moving()
    #keyholds
    #event handler
    if game_state == 'main':
        keys = pygame.key.get_pressed()
        handle_key_holds()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    if not player.hook_cords:
                        player.fish_hold = False
                        player.cast_rod(player.cast_length)
                    else:
                        player.stop_fishing()
                    player.cast_length = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                        player.inspect()
                if event.key == pygame.K_ESCAPE:
                    if player.text_cur:
                        player.text_cur = False
                    else:
                        real_menu_handler.run_menu()
                if event.key == pygame.K_q:
                    player.sprint_toggle()
                if event.key == pygame.K_SPACE:
                    handle_rod()
                if event.key == pygame.K_F11:
                    minigame.reset()
                    game_state = 'minigame'
            inv = inventory.inventory
            if event.type == pygame.MOUSEBUTTONDOWN:
                grab_pos() # prints cursor location useful for debugging
                if event.button == 1:
                    if pos[1] > inv.active[0] and inv.active[1] or inv.grabbed: # checks if you are withing the inventories cords to avoid pointless and relatively expensive checks
                        inv.click(pos)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if pos[1] > inv.active[0] and inv.active[1] or inv.grabbed:
                        inv.release(pos, grab_pos(), player, balance, player_tracker)
    elif game_state == 'minigame':
        if minigame.run((player.cords[0]-xp, player.cords[1]-yp)) == 'success':
            game_state = 'main'
            if player.hook_cords:
                rod_pull_sound.play()
            if isinstance(hooked_fsh, Fish):
                player_tracker.catch_fish(hooked_fsh.item.name)
                inventory.inventory.add_item(hooked_fsh.item)
                hooked_fsh.kill()
            else: # silly goofy error handling for if a fish is not on the line
                logging.warning("that's not a fish!")
                player.text_cur = "that's no fish!"
            player.stop_fishing()
            player.cast_length = 0
        elif minigame.run((player.cords[0]-xp, player.cords[1]-yp)) == 'failure':
            game_state = 'main'
            if isinstance(hooked_fsh, Fish):
                hooked_fsh.kill()
                Fish.fish_caught.ignore = 10
            player.stop_fishing()
            player.cast_length = 0
    pygame.display.update()
    player.update_can_move() # checks whether the player should be able to move or not

