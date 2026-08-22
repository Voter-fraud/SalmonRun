
import config
from globals import Global

from toolbox import cut_string, load_asset
from reso_p import win
import reso_p, map_mod
import pygame, copy
pygame.init()

base = pygame.transform.scale(load_asset('base.png','quest_imgs', ), (128*Global.UI_scale, 48*Global.UI_scale))
mid_font = pygame.font.SysFont('Comic Sans MS', 10*Global.UI_scale)

class QuestSystem:
    cur_quest_value = 0
    quest_list = ['']

    """begins a set of linear quests"""
    @classmethod
    def quest_init(cls, questlist):
        cls.quest_list = questlist

    @classmethod
    def cur_quest(cls):
        return cls.quest_list[cls.cur_quest_value]


    def __init__(self, reference, quest_type, ref_key, quantity, img, font, start_text, start_func, end_func, id):
        self.goal = quantity
        self.cur = 0
        self.quest_type = quest_type
        self.ref_key = ref_key
        self.start_value = copy.copy(reference)
        print(self.start_value)
        self.image = pygame.transform.scale(img, (128*Global.UI_scale, 48*Global.UI_scale))
        self.font = font
        self.name = id
        self.reference = reference # the stat tracker used for referencing progress


        self.finish_text = 'Quest Completed!'
        self.start_text = str(start_text)
        self.start_func = start_func
        self.end_func = end_func

        self.noti_font = pygame.font.SysFont('Comic Sans MS', 35 * map_mod.scale)
        self.cur_text = 0
        self.holdtime = 0
        self.mode = 'start'
        self.live = True

    def update(self, reference):
        print(self.start_value)
        if reference[self.ref_key]-self.start_value[self.ref_key] >= self.goal:
            if self.mode != 'finish':
                self.reset()
                self.mode = 'finish'
        else:
            self.cur = reference[self.ref_key]-self.start_value[self.ref_key]

    def reset(self):
        self.holdtime, self.cur_text = 0, 0

    def draw(self, ui_scale):
        win.blit(base, (reso_p.win_length-130*ui_scale, 90*ui_scale))
        win.blit(self.image, (reso_p.win_length-130*ui_scale, 90*ui_scale))
        win.blit(self.font.render(F'{self.cur}/{self.goal}', False, (0, 0, 0)), (reso_p.win_length-85*ui_scale, 110*ui_scale))

    def start(self, timer):
        self.start_func(self.name)
        self.start_value = copy.copy(self.reference) # updates the start value to when the quest is run
        if self.cur_text == len(self.start_text): #checks to see if notification is displayed fully
            self.holdtime += 1 # holds the fully displayed message for a little while
            if self.holdtime >= 100:
                self.mode = False
                self.holdtime, self.cur_text = 0, 0
        text = self.noti_font.render(F'{cut_string(self.start_text, self.cur_text)}', False, (0, 0, 0))
        text_box = text.get_rect(center=(reso_p.win_length/2, reso_p.win_height/4))
        win.blit(text, text_box.topleft)
        if timer % 10 == 0 and self.cur_text < len(self.start_text):
            self.cur_text += 1

    def finish(self, timer):
        self.end_func(self.name)
        if self.cur_text == len(self.finish_text):
            self.holdtime += 1
            if self.holdtime >= 100:
                self.mode = False
                self.live = False
                self.holdtime, self.cur_text = 0, 0
        print(self.finish_text)
        print(self.cur_text)
        text = self.noti_font.render(F'{cut_string(self.finish_text, self.cur_text)}', False, (0, 0, 0))
        text_box = text.get_rect(center=(reso_p.win_length/2, reso_p.win_height/4))
        win.blit(text, text_box.topleft)
        if timer % 10 == 0 and self.cur_text < len(self.finish_text):
            self.cur_text += 1

