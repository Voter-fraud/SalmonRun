import pygame, math, copy, logging

from toolbox import load_asset, return_corners
import toolbox

from map_mod import scale
import map_mod

import reso_p
from reso_p import win

import config
from globals import Global

from sound_library import rod_cast_sound

pygame.init()


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
        player_size = (16 * scale, 32 * scale)
        for key, value in cls.walking_anim.items():
            cls.walking_anim[key] = (pygame.transform.scale(value[0], player_size),
                                     pygame.transform.scale(value[1], player_size),
                                     pygame.transform.scale(value[2], player_size),
                                     pygame.transform.scale(value[3], player_size),
                                     pygame.transform.scale(value[4], player_size),
                                     pygame.transform.scale(value[5], player_size))
        for key, value in cls.fishing_anim.items():
            if key == 'left' or key == 'right':
                cls.fishing_anim[key] = (pygame.transform.scale(value[0], player_size),
                                         pygame.transform.scale(value[1], player_size),
                                         pygame.transform.scale(value[2], (20 * scale, 32 * scale))) # why is this one different?
            else:
                cls.fishing_anim[key] = (pygame.transform.scale(value[0], player_size),
                                         pygame.transform.scale(value[1], player_size),
                                         pygame.transform.scale(value[2], player_size))
        for key, value in cls.still.items():
            cls.still[key] = pygame.transform.scale(value, player_size)
        for key, value in cls.fish_passive.items():
            cls.fish_passive[key] = pygame.transform.scale(value, player_size)

    def __init__(self):
        super().__init__()
        self.bauble = load_asset('bauble.png','player')
        self.cords = [1800 * scale, 1200 * scale] # top left
        self.text_cur = False
        self.facing = 'up'
        self.hook_cords = [] # if empty hook is not cast
        self.speed = 5
        self.cast_length = 0
        self.can_move = True
        self.fish_hold = False
        self.baitlevel = 20
        self.width = 16 * scale
        self.height = 32 * scale
        self.rect = PlayerSprite.still['up'].get_rect(topleft=self.cords)
        self.walking = False
        self.walking_frame = 0
        self.boot_cords = [reso_p.win_length / 2, reso_p.win_height / 2-self.height/4]
        self.noclip = False

    @property
    def v_center(self):
        return reso_p.win_length / 2 - self.width / 2, reso_p.win_height / 2 - self.height / 2

    def draw(self, timer):
        """Draws player sprite"""
        yp, xp = self.xp_yp
        if self.walking:
            win.blit(PlayerSprite.walking_anim[self.facing][self.walking_frame], self.v_center)
            if timer % 10 == 0:
                self.walking_frame += 1
                if self.walking_frame == 6:
                    self.walking_frame = 0

        elif self.hook_cords:
            if self.facing == 'down':
                win.blit(PlayerSprite.fish_passive[self.facing], self.v_center)
                toolbox.draw_line(self.rect.topleft, (self.hook_cords[0] + 1.3 * scale, self.hook_cords[1]), (255, 255, 255), win,
                                  xp, yp, 1)
                toolbox.draw_line(self.rect.topleft, (self.rect.center[0], self.rect.center[1] + 4 * scale), (139, 69, 19), win, xp, yp, 3)
            elif self.facing == 'up':
                connector = [self.rect.topright[0] - 3 * scale, self.rect.topright[1] - 3 * scale]
                toolbox.draw_line(connector, (self.hook_cords[0] + 1.3 * scale, self.hook_cords[1]), (255, 255, 255), win,
                                  xp, yp, 1)
                toolbox.draw_line(connector, (self.rect.center[0], self.rect.center[1] + 4 * scale), (139, 69, 19), win, xp, yp, 3)
                win.blit(PlayerSprite.fish_passive[self.facing], self.v_center)
            elif self.facing == 'left':
                connector = [self.rect.topleft[0] - 20, self.rect.topright[1] + 15]
                toolbox.draw_line(connector, (self.hook_cords[0] + 1.3 * scale, self.hook_cords[1]), (255, 255, 255), win,
                                  xp, yp, 1)
                toolbox.draw_line(connector, (self.rect.center[0] - 1 * scale, self.rect.center[1]),
                                  (139, 69, 19), win, xp, yp, 3)
                win.blit(PlayerSprite.fish_passive[self.facing], self.v_center)
            elif self.facing == 'right':
                connector = [self.rect.topright[0]+20, self.rect.topright[1]+15]
                toolbox.draw_line(connector, (self.hook_cords[0] + 1.3 * scale, self.hook_cords[1]), (255, 255, 255), win,
                                  xp, yp, 1)
                toolbox.draw_line(connector, (self.rect.center[0] + 1 * scale, self.rect.center[1]), (139, 69, 19), win, xp, yp, 3)
                win.blit(PlayerSprite.fish_passive[self.facing], self.v_center)

        elif self.cast_length:
            if math.floor(self.cast_length/10) >= 2 and self.facing == 'right':
                win.blit(PlayerSprite.fishing_anim[self.facing][2], (self.v_center[0] - 4 * scale, self.v_center[1]))
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

    def cast_rod(self):
        """Casts your fishing rod"""
        rod_cast_sound.play()
        new_box = copy.copy(self.rect)
        new_box.topleft = self.check_obst(self.cast_length)
        if self.facing == 'up':
            check = new_box.midtop[0], new_box.midtop[1] - 10 * scale
        elif self.facing == 'down':
            check = new_box.midbottom[0], new_box.midbottom[1] + 10 * scale
        elif self.facing == 'left':
            check = new_box.midleft[0] - 10 * scale, new_box.midleft[1]
        elif self.facing == 'right':
            check = new_box.midright[0] + 10 * scale, new_box.midright[1]
        else:
            logging.warning('player does not have a direction')
            return 'player has no position'
        try:
            if '1' in map_mod.return_grids((check, check), Global.game_map): # checks to make sure the rod is going into water
                self.hook_cords = check # sets hook cords for fish collisions
        except IndexError:
            logging.warning('Player attempted to fish outside of game') # add some numerous comments for trying to do this in game

    def update_can_move(self):
        if self.text_cur or self.fish_hold or self.hook_cords:
            self.can_move = False
        else:
            self.can_move = True

    def stop_fishing(self, Fish):
        Fish.stop_fishing()
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

    def inspect(self, old_man, cur_quest):
        if self.rect.colliderect(old_man.box):
            old_man.talk(cur_quest, player)
            return
        if player.text_cur:
            player.text_cur = False

player = PlayerSprite()