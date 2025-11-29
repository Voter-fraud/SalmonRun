import logging, math
import config
import pygame, random
from toolbox import load_asset, fun_box_check
from reso_p import win
import map_mod

pygame.init()

class Fish(pygame.sprite.Sprite):
    fish_types = {
        # fishtype: (swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname)
        'salmon': (2, 1, 0.4, 1, 5, 'salmon', False), # slightly re work undecisiveness
        'maternal_salmon': (2, 2, 0.4, 1, 5, 'salmon', True),
        'fish': (3, 3, 0.6, 1, 5, 'fish', False),
        'carp': (3, 2, 1, 1, 5, 'carp', False),
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
    def create_fish(cls, cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, item, origin_bound, spritelist, inventory):
        """creates a new fish instance in the fish_list sprite group"""
        new = Fish(cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, item, origin_bound, inventory)
        new.origin = cords #original fish position
        cls.fish_lists[item].add(new)
        spritelist.add(new)
        return new

    @classmethod
    def update_fish(cls, player, timer, inventory, game_state, grid_ahead):
        """Handles fish AI on a high level"""
        for species_list in cls.fish_lists.values():
            for fish in species_list:
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
        if timer % 10 == 0:  # handles expensive operations such as swerving and baiting.
            if not self.baited(player.hook_cords) and timer % 60 and self != Fish.fish_caught:
                # every second active fishes get a chance to swerve
                self.fish_swerve()
            elif self == Fish.fish_caught and not Fish.fish_took:
                # handles deciding when a circling fish grabs onto the hook
                x = random.randrange(-300, 10)
                if x > 0:
                    Fish.fish_took = self
                    inventory.inventory.use_bait()  # the fish ate the bait
            elif self == Fish.fish_caught and Fish.fish_took:
                # handles deciding when a fish which grabbed onto the hook will run away
                y = random.randrange(-490, 15)
                if y > 0 and game_state != 'minigame':
                    player.hook_cords = False
                    Fish.fish_took = False
                    Fish.fish_caught = False
        if self != Fish.fish_caught:
            self.fish_move(grid_ahead)

    def __init__(self, cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, item, origin_bound, inventory):
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
        self.origin_bound = origin_bound
        self.origin = (0, 0)

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
        x = self.cords[0]
        y = self.cords[1]
        new_vector = self.vector
        ranlist = (-1, 1)
        escape = 1
        while True:
            if self.origin_bound:
                home_range = 50*map_mod.scale
            else:
                home_range = 9999999 * map_mod.scale
            if 'f' == grid_ahead((x+self.vector[0]*self.speed+(10*self.vector[0]*map_mod.scale), y+self.vector[1]*self.speed+(10*self.vector[1]*map_mod.scale)),
                16*map_mod.scale, 16*map_mod.scale)[-1] and \
                home_range >= abs(self.origin[0]-(x+self.vector[0]*self.speed+(10*self.vector[0]*map_mod.scale)))+abs(self.origin[1]-(y+self.vector[1]*self.speed+(10*self.vector[1]*map_mod.scale))):
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



    def baited(self, player_hook_cords): # sadly has to be probably changed a bit
        if self.ignore > 0:
            self.ignore -= 1
        elif player_hook_cords:
            dif = abs(player_hook_cords[0] - self.cords[0]) + abs(player_hook_cords[1] - self.cords[1])
            # if dif > player.baitlevel * 3 + 64*map_mod.scale:
                # return False
            for vector in ([0, -1], [0, 1], [1, 0], [-1, 0]):
                if vector != [self.vector[0]*-1, self.vector[1]*-1]: # does not check back of fish
                    ret = fun_box_check((self.cords[0], self.cords[1]), self.side_length, vector, 32 * map_mod.scale, player_hook_cords)
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
                    swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname, origin_bound = Fish.fish_types[key]

                    new = Fish.create_fish(cords, swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname, origin_bound, spritelist, inventory)
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
    'maternal_salmon': 4,
}, 6, 75 )
