import pygame, random

from setup import map_mod

from entity_classes.fish import Fish, fish_types
from entity_classes.lockolock import LocoLock

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
        self.range = rang * map_mod.scale # range is half a square length. Not using circles because I have no real reason to

    def spawn(self, grid_ahead, inventory, spritelist):
        if  len(self.cur.sprites()) < self.cap:
            cords =0,0
            run = True
            while run:
                cords = [self.cords[0] * map_mod.scale + random.randrange(-self.range, self.range), self.cords[1] * map_mod.scale + random.randrange(-self.range, self.range)]
                if 'f' in grid_ahead(cords, 16 * map_mod.scale, 16 * map_mod.scale):
                    run = False
            r = random.randrange(0, self.tot)
            for key, value in self.spwn_list.items():
                if value[0] < r <= value[1]:
                    swerving, un_decisiveness, f_speed, f_id, cautiousness, fishname, origin_bound, bait_dict = fish_types[key]
                    if origin_bound:
                        rang, swarm_speed, mini, maxi = origin_bound
                        x = random.randrange(mini, maxi+1)
                        if swarm_speed == 0:
                            center = LocoLock.create_nest_center(cords, rang)
                        else:
                            center = LocoLock.create_swarm_center(cords, rang, [0, 1], swarm_speed)
                        for x in range(0, x):
                            new = Fish.create_fish(cords, spritelist, inventory, *fish_types[key])
                            new.origin = center
                            center.add_fish()
                        self.cur.add(new)
                    else:
                        new = Fish.create_fish(cords, spritelist, inventory, *fish_types[key])
                        self.cur.add(new)


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