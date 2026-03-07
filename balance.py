import pygame
from toolbox import load_asset
import reso_p
from reso_p import win, scale, ui_scale
from globals import Global


class Balance:
    def __init__(self, bal, game_long_balance):
        self.image = load_asset('coin_counter.png')
        self.f_cords = (reso_p.win_length-ui_scale(73), ui_scale(34))
        self.color = (0, 0, 0)
        self.cords = (reso_p.win_length-ui_scale(110), ui_scale(32))
        self.bal = bal
        self.total = game_long_balance
        self.font = pygame.font.SysFont('Comic Sans MS', 30)  # this is only one font size

    def draw(self):
        win.blit(self.image, self.cords)
        win.blit(self.font.render(str(self.bal), False, self.color), self.f_cords)

    def add_money(self, amount):
        self.bal += amount
        self.total += amount

    def use_money(self, amount):
        self.bal -= amount

    def rescale(self):
        self.image = pygame.transform.scale(self.image, (ui_scale(100), ui_scale(50)))
        self.font = pygame.font.SysFont('Comic Sans MS', ui_scale(30))

balance = Balance(0, 0)