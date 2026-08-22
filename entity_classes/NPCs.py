import pygame
from setup import map_mod
from system_modules import stat_tracker
from setup.reso_p import win
from setup.globals import Global
from toolbox import load_asset


class Conversible(pygame.sprite.Sprite):
    talkables = []

    @classmethod
    def new(cls, name, img, loop_list, cords, converse_box, func, width, height):
        new_c = cls(name, img, loop_list, cords, converse_box, width, height)
        if func:
            new_c.func = func
        cls.talkables.append(new_c)
        Global.spritelist.add(new_c)
        return new_c

    @classmethod
    def draw_convs(cls, xp, yp):
        for conv in cls.talkables:
            if isinstance(conv, Conversible):
                conv.draw(xp, yp)

    @classmethod
    def rescale(cls):
        for rescalible in cls.talkables:
            rescalible.image = pygame.transform.scale(rescalible.image, (rescalible.width * map_mod.scale, rescalible.height * map_mod.scale))
            rescalible.big_box = rescalible.big_box[0] * map_mod.scale, rescalible.big_box[1] * map_mod.scale

    def __init__(self, name, img, loop_list, cords, converse_box, width, height):
        super().__init__()
        self.loop_list = loop_list
        self.linear_list = ['', '']
        self.image = img
        self.name = name
        self.status = 0
        self.active = True
        self.cords = (cords[0] * map_mod.scale / 2, cords[1] * map_mod.scale / 2)
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

    def talk(self, cur_quest, player):
        if cur_quest.ref_key == self.name:
            stat_tracker.player_tracker.talk_to(self.name)
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

    def draw(self, xp, yp):
        win.blit(self.image, (self.cords[0]-xp, self.cords[1]-yp))

old_man_quest_dialouge = {
'tutorial1' : [
    'My names PLACEHOLDER nice to meet you',
    'You must be new to these waters!',
    "I'll show you how to get started",
    "to cast your fishing rod...",
    "Hold space then release",
    "To catch a fish interested in your hook... ",
    "wait until bubbles form... ",
    "then press space again",
    "by pressing escape...",
    "you can open up your menu",
    "Check the controls page",
    "Now go and catch a fish"
],
'tutorial2' : [
    'Nice job catching that fish',
    'To sell a fish go to the market...',
    'and drag the fish from your inventory...',
    'onto the market.',
    ''
],
'tutorial3': [
    'There are many types of fish here',
    'Catch 3 salmon for me',
    'Salmon can be found in the rivers.',
    'Salmon move quickly and look like...',
   " they know where they're going",
    ''
],
'tutorial4': [
    'I have been trying to catch...',
    'a specific fish for a while now...',
    'but I just cant seem to find one.',
    'Could you catch a bass for me?',
    'They move relatively quickly...',
    'but unlike salmon they make many turns.',
    'They also like minnows as bait'
],
'tutorial5': [
    'Thanks for your help.',
    'That is everything I have planed.',
    'Enjoy your time in salmon run!',
],
'tutorial6': [
    'Thanks for your help.',
    'That is everything I have planed.',
    'Enjoy your time in salmon run!',
],
}

def old_man_quest_func(quest_name):
    old_man.linear_list = old_man_quest_dialouge[quest_name]
    old_man.status = 0
    old_man.active = True


old_man_loop = ['Fishing takes my worries away', 'I could go for a beer right about now']
old_man_img = load_asset("old_man_placehold.png")
old_man = Conversible.new('old_man', old_man_img, old_man_loop, (3093.0, 2054.0), (64, 64), False, 24, 36)