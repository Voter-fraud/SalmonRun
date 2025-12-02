
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
        self.reference = reference


        self.finish_text = 'Quest Completed!'
        self.start_text = str(start_text)
        self.start_func = start_func
        self.end_func = end_func

        self.noti_font = pygame.font.SysFont('Comic Sans MS', 35 * map_mod.scale)
        self.cur_text = 0
        self.overtime = 0
        self.mode = 'start'
        self.live = True

    def update(self, reference):
        print(self.start_value)
        if reference[self.ref_key]-self.start_value[self.ref_key] >= self.goal:
            self.mode = 'finish'
        else:
            self.cur = reference[self.ref_key]-self.start_value[self.ref_key]

    def draw(self, ui_scale):
        win.blit(base, (reso_p.win_length-130*ui_scale, 90*ui_scale))
        win.blit(self.image, (reso_p.win_length-130*ui_scale, 90*ui_scale))
        win.blit(self.font.render(F'{self.cur}/{self.goal}', False, (0, 0, 0)), (reso_p.win_length-85*ui_scale, 110*ui_scale))

    def start(self, timer):
        self.start_func(self.name)
        self.start_value = copy.copy(self.reference) # updates the start value to when the quest is run
        if self.cur_text == len(self.start_text):
            self.overtime += 1
            if self.overtime >= 100:
                self.mode = False
                self.overtime, self.cur_text = 0, 0
        text = self.noti_font.render(F'{cut_string(self.start_text, self.cur_text)}', False, (0, 0, 0))
        text_box = text.get_rect(center=(reso_p.win_length/2, reso_p.win_height/4))
        win.blit(text, text_box.topleft)
        if timer % 10 == 0 and self.cur_text < len(self.start_text):
            self.cur_text += 1

    def finish(self, timer):
        self.end_func(self.name)
        if self.cur_text == len(self.finish_text):
            self.overtime += 1
            if self.overtime >= 100:
                self.mode = False
                self.live = False
                self.overtime, self.cur_text = 0, 0
        text = self.noti_font.render(F'{cut_string(self.finish_text, self.cur_text)}', False, (0, 0, 0))
        text_box = text.get_rect(center=(reso_p.win_length/2, reso_p.win_height/4))
        win.blit(text, text_box.topleft)
        if timer % 10 == 0 and self.cur_text < len(self.finish_text):
            self.cur_text += 1

"""class FishCatching:
    def __init__(self, catch_amount, fish_type, initial_values, img, font, start_text):
        self.amount = catch_amount
        self.type = fish_type
        self.initials = dict(initial_values) # makes a copy of the initial fish catching statistics
        self.caught = 0
        self.image = pygame.transform.scale(img, (128*Global.UI_scale, 48*Global.UI_scale))
        self.font = font

        self.finish_text = 'Quest Completed!'
        self.start_text = str(start_text)
        self.noti_font = pygame.font.SysFont('Comic Sans MS', 35 * map_mod.scale)
        self.cur_text = 0
        self.overtime = 0
        self.mode = 'start'
        self.live = True

    def update(self, values):
        if self.type:
            self.caught = (values[self.type]-self.initials[self.type])

        else:
            self.caught = (values['total'] - self.initials['total'])

        if self.caught == self.amount and self.live:
            self.mode = 'finish'

    def draw(self, ui_scale):
        win.blit(base, (reso_p.win_length-130*ui_scale, 90*ui_scale))
        win.blit(self.image, (reso_p.win_length-130*ui_scale, 90*ui_scale))
        win.blit(self.font.render(F'{self.caught}/{self.amount}', False, (0, 0, 0)), (reso_p.win_length-85*ui_scale, 110*ui_scale))

    def start(self, timer, initial_values):
        self.initials = dict(initial_values)
        if self.cur_text == len(self.start_text):
            self.overtime += 1
            if self.overtime >= 100:
                self.mode = False
                self.overtime, self.cur_text = 0, 0
        text = self.noti_font.render(F'{cut_string(self.start_text, self.cur_text)}', False, (0, 0, 0))
        text_box = text.get_rect(center=(reso_p.win_length/2, reso_p.win_height/4))
        win.blit(text, text_box.topleft)
        if timer % 10 == 0 and self.cur_text < len(self.start_text):
            self.cur_text += 1

    def finish(self, timer):
        if self.cur_text == len(self.finish_text):
            self.overtime += 1
            if self.overtime >= 100:
                self.mode = False
                self.live = False
                self.overtime, self.cur_text = 0, 0
        text = self.noti_font.render(F'{cut_string(self.finish_text, self.cur_text)}', False, (0, 0, 0))
        text_box = text.get_rect(center=(reso_p.win_length/2, reso_p.win_height/4))
        win.blit(text, text_box.topleft)
        if timer % 10 == 0 and self.cur_text < len(self.finish_text):
            self.cur_text += 1

class TalkTo:
    def __init__(self, character, img, font, newtext):
        self.character = character
        self.newtext = newtext
        self.image = pygame.transform.scale(img, (128*Global.UI_scale, 48*Global.UI_scale))
        self.font = font

        self.finish_text = 'New Quest!' # talking to a character is an intermediate quest so transitions should be clean
        self.start_text = f'talk to the {self.character.name}'
        self.noti_font = pygame.font.SysFont('Comic Sans MS', 35 * map_mod.scale)
        self.cur_text = 0
        self.overtime = 0
        self.mode = 'start'
        self.live = True

    def update(self, char):

        if char == self.character and self.live:
            self.mode = 'finish'

    def draw(self, ui_scale):
        win.blit(base, (reso_p.win_length-130*ui_scale, 90*ui_scale))
        win.blit(self.image, (reso_p.win_length-130*ui_scale, 90*ui_scale))
        win.blit(self.font.render(F'talk to {self.character.name}', False, (0, 0, 0)), (reso_p.win_length-85*ui_scale, 105*ui_scale))

    def start(self, timer, wah):
        if self.cur_text == len(self.start_text):
            self.overtime += 1
            if self.overtime >= 100:
                self.mode = False
                self.overtime, self.cur_text = 0, 0
        text = self.noti_font.render(F'{cut_string(self.start_text, self.cur_text)}', False, (0, 0, 0))
        text_box = text.get_rect(center=(reso_p.win_length/2, reso_p.win_height/4))
        win.blit(text, text_box.topleft)
        if timer % 10 == 0 and self.cur_text < len(self.start_text):
            self.cur_text += 1

    def finish(self, timer):
        if self.cur_text == len(self.finish_text):
            self.overtime += 1
            if self.overtime >= 100:
                self.mode = False
                self.live = False
                self.overtime, self.cur_text = 0, 0
        text = self.noti_font.render(F'{cut_string(self.finish_text, self.cur_text)}', False, (0, 0, 0))
        text_box = text.get_rect(center=(reso_p.win_length/2, reso_p.win_height/4))
        win.blit(text, text_box.topleft)
        if timer % 10 == 0 and self.cur_text < len(self.finish_text):
            self.cur_text += 1

class FishSelling:
    def __init__(self, catch_amount, fish_type, initial_values, img, font, start_text):
        self.amount = catch_amount
        self.type = fish_type
        self.initials = dict(initial_values) # makes a copy of the initial fish sold statistics
        self.sold = 0
        self.image = pygame.transform.scale(img, (128*Global.UI_scale, 48*Global.UI_scale))
        self.font = font

        self.finish_text = 'Quest Completed!'
        self.start_text = str(start_text)
        self.noti_font = pygame.font.SysFont('Comic Sans MS', 35 * map_mod.scale)
        self.cur_text = 0
        self.overtime = 0
        self.mode = 'start'
        self.live = True

    def update(self, values):
        if self.type:
            self.sold = (values[self.type] - self.initials[self.type])

        else:
            self.sold = (values['total'] - self.initials['total'])

        if self.sold == self.amount and self.live:
            self.mode = 'finish'

    def draw(self, ui_scale):
        win.blit(base, (reso_p.win_length-130*ui_scale, 90*ui_scale))
        win.blit(self.image, (reso_p.win_length-130*ui_scale, 90*ui_scale))
        win.blit(self.font.render(F'{self.sold}/{self.amount}', False, (0, 0, 0)), (reso_p.win_length - 85 * ui_scale, 110 * ui_scale))

    def start(self, timer, wah):
        if self.cur_text == len(self.start_text):
            self.overtime += 1
            if self.overtime >= 100:
                self.mode = False
                self.overtime, self.cur_text = 0, 0
        text = self.noti_font.render(F'{cut_string(self.start_text, self.cur_text)}', False, (0, 0, 0))
        text_box = text.get_rect(center=(reso_p.win_length/2, reso_p.win_height/4))
        win.blit(text, text_box.topleft)
        if timer % 10 == 0 and self.cur_text < len(self.start_text):
            self.cur_text += 1

    def finish(self, timer):
        if self.cur_text == len(self.finish_text):
            self.overtime += 1
            if self.overtime >= 100:
                self.mode = False
                self.live = False
                self.overtime, self.cur_text = 0, 0
        text = self.noti_font.render(F'{cut_string(self.finish_text, self.cur_text)}', False, (0, 0, 0))
        text_box = text.get_rect(center=(reso_p.win_length/2, reso_p.win_height/4))
        win.blit(text, text_box.topleft)
        if timer % 10 == 0 and self.cur_text < len(self.finish_text):
            self.cur_text += 1"""