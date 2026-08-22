import random, logging

from setup import map_mod

class LocoLock: # swarming or fish nesting behaviour
    swarms = set()
    @classmethod
    def create_swarm_center(cls, cords, rang, movement_vector, speed):
        new_instance = LocoLock(cords, rang, movement_vector, speed)
        cls.swarms.add(new_instance)
        return new_instance

    @classmethod
    def create_nest_center(cls, cords, rang):
        new_instance = LocoLock(cords, rang, (0, 0), 0)
        return new_instance

    @classmethod
    def move_swarms(cls, grid_ahead, xp, yp):
        for swarm in cls.swarms:
            if 0 < (swarm.cords[0] - xp) < 8 and 0 < (swarm.cords[1] - yp) < 600:
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
            LocoLock.swarms.remove(self)
            del self

    def center_move(self, grid_ahead):
        """Makes the swarm move based on speed and direction instance properties"""
        x = self.cords[0]
        y = self.cords[1]
        new_vector = self.vector
        ranlist = (-1, 1)
        escape = 1
        while True:
            if 'f' == grid_ahead((x+self.vector[0]*self.speed+(10 * self.vector[0] * map_mod.scale), y + self.vector[1] * self.speed + (10 * self.vector[1] * map_mod.scale)),
                                 16 * map_mod.scale, 16 * map_mod.scale)[-1]:
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