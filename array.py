import pygame, os, copy, logging
from toolbox import load_asset
pygame.init()
import math, time
win = pygame.display.set_mode((1924, 1020))
# type changes
dirmult = 1 # lower value repulse stronger values attract
avgmult = 1 # changes whole as shape
# subtype changes
bouncer = 0 # makes the patterns more erratic through changing reflection behaviour
dirsub = 0 # makes more erratic behaviour


class GravitationalObject:
    def __init__(self, unit_decay, pull, cords, abs_range):
        self.decay = unit_decay #ignore rn
        self.pull = pull
        self.cords = cords
        self.ratio = (10, 10)
        self.range = abs_range

    def dir_angle(self, objt):
        print(F'{objt.angle}, current')
        dx = self.cords[0] - objt.cords[0]
        dy = self.cords[1] - objt.cords[1]
        ret = math.atan2(dy, dx)
        ret = math.degrees(ret)
        if objt.angle-ret > 180:
            ret += (270+bouncer)
        if objt.angle-ret < -180:
            ret -= (270+bouncer)
        print(F'{ret}goal')
        return (ret-dirsub)*dirmult

    def pull_entity(self, obj):
        direct = self.dir_angle(obj)
        difx, dify = abs(obj.cords[0] - self.cords[0]), abs(obj.cords[1] - self.cords[1])
        dist = math.sqrt(difx*difx+dify*dify)
        avg = ((obj.angle*3+direct*2+(5*direct*self.decay)/dist)/5+(6* self.decay/dist))
        print(F'{avg}next go')
        if dist <= self.range:

            return avg*avgmult
        return obj.angle

center = GravitationalObject(0.5, 10, (850, 505), 350)


class MovingEntity:
    def __init__(self, speed, cords, angle, name):
        self.speed = speed
        self.cords = cords
        self.angle = angle
        self.name = name
        self.image = load_asset('bauble.png', 'player')
        self.rect = self.image.get_rect(topleft=self.cords)

    @property
    def vector(self):
        return vector_from_angle(self.angle)

    def move(self):
        self.cords[0] += self.vector[0] * self.speed
        self.cords[1] += self.vector[1] * self.speed

    def turn(self, degrees):
        if abs(self.angle + degrees) < 360:
            self.angle += degrees
        else:
            self.angle += degrees

    def __str__(self):
        return F'{self.cords}, {self.name}'


def vector_from_angle(angle):
    a1 = math.radians(angle)
    a2 = math.radians(90) - a1
    s1 = math.sin(a2)
    s2 = math.sin(a1)
    ratio = abs(s1) + abs(s2)
    xv = s1 / ratio
    yv = s2 / ratio
    return xv, yv


ticks = 0
fish = MovingEntity(1, [1000, 400], 90, 'fish')
while True:
    ticks += 1
    fish.move()
    if ticks % 40 == 0:
        fish.angle = center.pull_entity(fish)
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                print(1)
                fish.turn(30)
    win.blit(fish.image, fish.cords)
    win.blit(fish.image, center.cords)
    pygame.display.update()

