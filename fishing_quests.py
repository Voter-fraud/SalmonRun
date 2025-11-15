import config
from toolbox import cut_string, load_asset
from config import pygame, UI_scale
from reso_p import win
import os, reso_p, map_mod
pygame.init()

base = pygame.transform.scale(load_asset('base.png','quest_imgs', ), (128*UI_scale, 48*UI_scale))
mid_font = pygame.font.SysFont('Comic Sans MS', 10*UI_scale)

class FishCatching:
    def __init__(self, catch_amount, fish_type, initial_values, img, font, start_text):
        self.amount = catch_amount
        self.type = fish_type
        self.initials = dict(initial_values) # makes a copy of the initial fish catching statistics
        self.caught = 0
        self.image = pygame.transform.scale(img, (128*UI_scale, 48*UI_scale))
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
        self.image = pygame.transform.scale(img, (128*UI_scale, 48*UI_scale))
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
        self.image = pygame.transform.scale(img, (128*UI_scale, 48*UI_scale))
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
            self.cur_text += 1