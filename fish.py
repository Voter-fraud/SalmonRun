import logging, math
import config
import pygame, random
from toolbox import load_asset, fun_box_check
from reso_p import win
import map_mod

class Fish(pygame.sprite.Sprite):
    fish_types = {
        # fishtype: (swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname, nesting, baitlist)
        'salmon': (2, 1, 0.8, 1, 1.4, 'salmon', False,
                   { # baitlist
                        'worms': 1.3,
                        'plastic_bait': 1.1,
                        'insect_bait': 1.3,
                        'minnow': 2,
                        'default': 1.1
                   }
                ),

        # fishtype: (swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname, nesting, baitlist)
        'maternal_salmon': (2, 2, 0.4, 1, 0.4, 'maternal_salmon', (50, 0, 1, 1),# rang, speed, min max
                            {  # baitlist
                                'worms': 0.8,
                                'plastic_bait': 0.7,
                                'insect_bait': 0.8,
                                'minnow': 1,
                                'default': 0.7
                            }
                        ),


        'fish': (3, 3, 0.6, 1, 1.2, 'fish', False,
                 {  # baitlist
                     'worms': 1.5,
                     'plastic_bait': 1.2,
                     'insect_bait': 1.3,
                     'minnow': 1,
                     'default': 1.2
                 }
                 ),

        'carp': (3, 2, 0.4, 1, 1, 'carp', False,
                 {  # baitlist
                     'worms': 2,
                     'plastic_bait': 1.3,
                     'insect_bait': 1.7,
                     'minnow': 1,
                     'default': 1.2
                 }
                 ),

        # fishtype: (swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname, nesting, baitlist)
        'bass': (2, 2, 0.6, 1, 1.6, 'bass', False,
                 {  # baitlist
                     'worms': 1.5,
                     'plastic_bait': 1,
                     'insect_bait': 1.5,
                     'minnow': 3,
                     'default': 0.9
                 }
                 ),

        # fishtype: (swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname, nesting, baitlist)
        'present_fish': (4, 4, 2, 1, 2, 'present_fish', False,
                 {  # baitlist
                     'worms': 1.1,
                     'plastic_bait': 1,
                     'insect_bait': 1.1,
                     'minnow': 1,
                     'default': 1
                 }
                 ),

        # fishtype: (swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname, nesting, baitlist)
        'minnow': (4, 3, 0.5, 1, 0.7, 'minnow', (50, 0.6, 2, 3),# rang, speed, min, max,,
                         {  # baitlist
                             'worms': 2,
                             'plastic_bait': 3,
                             'insect_bait': 3,
                             'minnow': 1,
                             'default': 1
                         }
                         ),
    }

    fish_frames = {  # add vector based rotations for fish movemont
        '[0, -1]': load_asset('fishup1.png', 'fish scheiße'),
        '[0, 1]': load_asset('fishdown1.png', 'fish scheiße'),
        '[-1, 0]': load_asset('fishleft1.png', 'fish scheiße'),
        '[1, 0]': load_asset('fishright1.png', 'fish scheiße'),
        'spc': load_asset('collide.png', 'fish scheiße'),
        '1': load_asset('fishcircle1.png', 'fish scheiße'),
        '2': load_asset('fishcircle2.png', 'fish scheiße'),
        '3': load_asset('fishcircle3.png', 'fish scheiße'),
        '4': load_asset('fishcircle4.png', 'fish scheiße'),
    }

    fish_lists = {} # the only comprehensive list of fish.
    for fish in fish_types.keys():
        fish_lists[fish] = pygame.sprite.Group()

    fish_caught = False # checks if a fish is circling the hook when gravity is added remove this
    fish_took = False # keeps track of if a fish is on the hook

    @classmethod
    def stop_fishing(cls):
        Fish.fish_caught = False
        Fish.fish_took = False

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
    def create_fish(cls, cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, item, origin_bound, spritelist, bait_dict, inventory):
        """creates a new fish instance in the fish_list sprite group"""
        new = Fish(cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, item, origin_bound, bait_dict, inventory)
        cls.fish_lists[item].add(new)
        spritelist.add(new)
        return new

    @classmethod
    def update_fish(cls, player, timer, inventory, game_state, grid_ahead, yp, xp):
        """Handles fish AI on a high level"""
        for species_list in cls.fish_lists.values():
            for fish in species_list:
                if -50<(fish.cords[0]-xp)<850 and -50<(fish.cords[1]-yp)<650:
                    fish.check_hook_collision(player.hook_cords)
                    fish.complex_fish_movement(timer, player, inventory, game_state, grid_ahead)

    @classmethod
    def scared_check(cls, player_hook_cords):
        """scares fishes away from the hook when first cast"""
        check_radius = 60 * map_mod.scale
        if player_hook_cords:
            for species_list in cls.fish_lists.values():
                for fish in species_list:
                    difx, dify = abs(player_hook_cords[0] - fish.cords[0]), abs(player_hook_cords[1] - fish.cords[1])
                    expx, expy = abs(player_hook_cords[0] - fish.cords[0] + fish.vector[0]), abs(
                        player_hook_cords[1] - fish.cords[1] + fish.vector[1])
                    dif = math.sqrt(difx * difx + dify * dify)  # checks absolute distance between fish and your hook
                    e_dif = math.sqrt(expx * expx + expy * expy)  # checks if you are moving away or towards the hook
                    if dif <= check_radius and dif < e_dif:  # if within a circle within radius 64 and the fish is moving towards you turn it around
                        fish.vector.reverse()
                        fish.ignore = 50  # makes the fish not be tricked by the bait for 500 ticks

    def complex_fish_movement(self, timer, player, inventory, game_state, grid_ahead):
        bait = inventory.inventory.bait_slot
        if timer % 10 == 0:  # handles expensive operations such as swerving and baiting.
            if not self.baited(player.hook_cords, bait) and timer % 60 and self != Fish.fish_caught:
                # every second active fishes get a chance to swerve
                self.fish_swerve()
            elif self == Fish.fish_caught and not Fish.fish_took:
                # handles deciding when a circling fish grabs onto the hook
                x = random.randrange(-350, int(9*self.bait_dict(bait)))
                if x > 0:
                    Fish.fish_took = self
                    inventory.inventory.use_bait()  # the fish ate the bait
            elif self == Fish.fish_caught and Fish.fish_took:
                # handles deciding when a fish which grabbed onto the hook will run away
                y = random.randrange(-300, 15)
                if y > 0 and game_state != 'minigame':
                    player.hook_cords = False
                    Fish.fish_took = False
                    Fish.fish_caught = False
        if self != Fish.fish_caught:
            self.fish_move(grid_ahead)

    def __init__(self, cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, item, origin_bound, bait_dict, inventory):
        super().__init__()
        self.image = load_asset('fishleft1.png','fish scheiße') # change later to relate to a dict that matches fish type to image
        self.rect = self.image.get_rect() # creates rect for sprite class
        self.cords = (cords[0], cords[1]) #topleft cords of the fish
        self.speed = f_speed*map_mod.scale
        self.swerving = swerving # measure of how unpredictable the fish is when it turns
        self.un_decisiveness = un_decisiveness # measure of how often a fish turns
        self.vector = [1, 0]
        self.id = f_id
        self.circ_frame = 1
        self.ignore = 4
        self.cautiousness = cautiousness
        self.item = inventory.Item.new(item)
        self.side_length = 16
        self.origin_bound = bool(origin_bound)
        self.origin = origin_bound
        self.bait_dict_atr = bait_dict


    def bait_dict(self, bait):
        return self.bait_dict_atr.get(bait, self.bait_dict_atr['default'])

    def check_hook_collision(self, player_hook_cords):
        if player_hook_cords and not Fish.fish_caught:
            # check for hook collisions
            self.rect.topleft = self.cords  # updates the fishes hit-boxes. This only happens when a hook is cast to save resources
            if self.rect.collidepoint(player_hook_cords[0], player_hook_cords[1]) and not self.ignore:
                Fish.fish_caught = self  # returns a class instance if there is a collision

    def draw(self, player, game_state, timer, xp, yp):
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


    def fish_move(self, grid_ahead):
        """Makes the fish instance move based on speed and direction instance properties"""
        LocoLocka.move_swarms(grid_ahead)
        x = self.cords[0]
        y = self.cords[1]
        new_vector = self.vector
        ranlist = (-1, 1)
        escape = 1
        while True:
            if self.origin_bound:
                home_range = self.origin.range*map_mod.scale
            else:
                home_range = 9999999 * map_mod.scale
            if 'f' == grid_ahead((x+self.vector[0]*self.speed+(10*self.vector[0]*map_mod.scale), y+self.vector[1]*self.speed+(10*self.vector[1]*map_mod.scale)),
                16*map_mod.scale, 16*map_mod.scale)[-1]:
                if self.origin_bound:
                    if home_range >= abs(self.origin.cords[0]-(x+self.vector[0]*self.speed+(10*self.vector[0]*map_mod.scale)))+abs(self.origin.cords[1]-(y+self.vector[1]*self.speed+(10*self.vector[1]*map_mod.scale))):
                        self.cords = x + self.vector[0] * self.speed, y + self.vector[1] * self.speed
                        return
                    else:
                        if 0 in self.vector:
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
                else:
                # plus 20 is to keep the fish off of the sand
                    self.cords = x + self.vector[0]*self.speed, y + self.vector[1]*self.speed
                    return
            else:
                if 0 in self.vector:
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



    def baited(self, player_hook_cords, inventory_bait_slot): # sadly has to be probably changed a bit
        if self.ignore > 0:
            self.ignore -= 1
        elif player_hook_cords:
            if inventory_bait_slot == '':
                inventory_bait_slot = 1
            else:
                inventory_bait_slot = inventory_bait_slot.name
            dif = abs(player_hook_cords[0] - self.cords[0]) + abs(player_hook_cords[1] - self.cords[1])
            # if dif > player.baitlevel * 3 + 64*map_mod.scale:
                # return False
            for vector in ([0, -1], [0, 1], [1, 0], [-1, 0]):
                if vector != [self.vector[0]*-1, self.vector[1]*-1]: # does not check back of fish
                    ret = fun_box_check((self.cords[0], self.cords[1]), self.side_length, vector, 32 * map_mod.scale*self.bait_dict(inventory_bait_slot), player_hook_cords)
                    if ret:
                        self.vector = ret
                        return True

    def __str__(self):
        return self.cords

    def __repr__(self):
        return F'ID:{self.id}, cords:{self.cords}, vector:{self.vector}'

class FishSpawner:
    FishSpawners = []

    @classmethod
    def new(cls, cords, fish_dict, cap, rang):
        new = FishSpawner(cords, fish_dict, cap, rang)
        cls.FishSpawners.append(new)
        return new

    @classmethod
    def spawn_all(cls, grid_ahead, inventory, spritelist):
        for spawner in cls.FishSpawners:
            spawner.spawn(grid_ahead, inventory, spritelist)

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

    def spawn(self, grid_ahead, inventory, spritelist):
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
                    swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname, origin_bound, bait_dict = Fish.fish_types[key]
                    if origin_bound:
                        rang, swarm_speed, mini, maxi = origin_bound
                        x = random.randrange(mini, maxi+1)
                        if swarm_speed == 0:
                            center = LocoLocka.create_nest_center(cords, rang)
                        else:
                            center = LocoLocka.create_swarm_center(cords, rang, [0, 1], swarm_speed)
                        for x in range(0, x):
                            new = Fish.create_fish(cords, swerving, un_decisiveness, f_speed, f_id, cautiousness,
                                                   fishname, center, spritelist, bait_dict, inventory)
                            center.add_fish()
                        self.cur.add(new)
                    else:
                        new = Fish.create_fish(cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname, False, spritelist, bait_dict, inventory)
                        self.cur.add(new)


class LocoLocka: # swarming or fish nesting behaviour
    swarms = set()
    @classmethod
    def create_swarm_center(cls, cords, rang, movement_vector, speed):
        new_instance = LocoLocka(cords, rang, movement_vector, speed)
        cls.swarms.add(new_instance)
        return new_instance

    @classmethod
    def create_nest_center(cls, cords, rang):
        new_instance = LocoLocka(cords, rang, (0, 0), 0)
        return new_instance

    @classmethod
    def move_swarms(cls, grid_ahead):
        for swarm in cls.swarms:
            swarm.center_move(grid_ahead)

    def __init__(self, cords, rang, movement_vector, speed):
        self.cords = cords
        self.range = rang
        self.vector = movement_vector
        self.speed = speed/120 # yikes
        self.fish_attached = 0

    def add_fish(self):
        self.fish_attached += 1

    def remove_fish(self):
        self.fish_attached -= 1
        if self.fish_attached <= 0: # remove this object to save memory.
            LocoLocka.swarms.remove(self)
            del self

    def center_move(self, grid_ahead):
        """Makes the swarm move based on speed and direction instance properties"""
        x = self.cords[0]
        y = self.cords[1]
        new_vector = self.vector
        ranlist = (-1, 1)
        escape = 1
        while True:
            if 'f' == grid_ahead((x+self.vector[0]*self.speed+(10*self.vector[0]*map_mod.scale), y+self.vector[1]*self.speed+(10*self.vector[1]*map_mod.scale)),
                16*map_mod.scale, 16*map_mod.scale)[-1]:
                # plus 20 is to keep the swarm  off of the sand
                self.cords = x + self.vector[0]*self.speed, y + self.vector[1]*self.speed
                return
            else:
                if 0 in self.vector:
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
                logging.warning('swarm may be trapped')
                break


FishSpawner.new([1500, 1191], {
    'carp': 7,
    'salmon': 0,
}, 3, 120)
FishSpawner.new([1500, 1191], {
    'minnow': 4,
}, 2, 120)
FishSpawner.new([1500, 1191], {
    'carp': 6,
    'salmon': 0,
}, 4, 500 )
FishSpawner.new([1500, 1191], {
    'minnow': 4,
    'salmon': 0,
}, 3, 500 )
FishSpawner.new([1700, 1191], {
'carp': 6,
    'bass': 3,
    'present_fish': 2,
    'salmon': 0,
}, 4, 500 )
FishSpawner.new([1350, 775], {
    'fish': 0,
    'carp': 0,
    'salmon': 4,
    'maternal_salmon': 3,
}, 4, 75 )
FishSpawner.new([250, 500], {
    'present_fish': 5,
}, 1, 50 )
FishSpawner.new([750, 2300], {
'carp': 6,
    'bass': 5,
    'present_fish': 2,
    'minnow': 3,
}, 4, 50 )
FishSpawner.new([450, 900], {
    'salmon': 3,
}, 3, 50 )