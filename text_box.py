import pygame
from toolbox import load_asset
from globals import Global
from reso_p import win
import reso_p
import textM
from player_mod import player

class Textbox(pygame.sprite.Sprite):
    def __init__(self, base_dimensions):
        pygame.sprite.Sprite.__init__(self)
        self.image = load_asset("textbox.png")
        self.rect = self.image.get_rect()
        # 510, 70
        self.dimensions = (base_dimensions[0]*Global.UI_scale,
                           base_dimensions[1]*Global.UI_scale)

    def draw(self):
        win.blit(self.image, ((reso_p.win_length - self.dimensions) / 2, reso_p.win_height - self.dimensions))
        win.blit(textM.standard_comic.render(str(player.text_cur), False, (0, 0, 0)),
                 ((reso_p.win_length - 475 * Global.UI_scale) / 2, reso_p.win_height - 65 * Global.UI_scale))

textbox = Textbox((510, 70))