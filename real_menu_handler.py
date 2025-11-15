from inspect import isclass

import pygame
import os, reso_p
from reso_p import win
from toolbox import load_asset

from pygame import K_LEFT

# initialising programs
pygame.init()
pygame.mixer.init()
pygame.font.init()
# display window setup
pygame.display.set_caption('Gamble core')
# global variables
clock = pygame.time.Clock()
my_font = pygame.font.SysFont('Comic Sans MS', 30)  # this is only one font size
small_font = pygame.font.SysFont('Comic Sans MS', 30)  # this is only one font size
money_amount = 100
soundstate = True
bet_amount = 10
game_state = 'main'
sound = 100
# loading in game assets
menu_backgrounds = {
    'good one': load_asset('fucking_beatifull_bkg.png', 'menu'),
    'controls': load_asset('controls_page.png', 'menu')
}
sound_toggle = (load_asset('sound_sel.png', 'menu'), (load_asset('sound_off.png', 'menu' ), load_asset('sound_on.png', 'menu' )))
sound_trans =(load_asset('sound_sel.png', 'menu'), load_asset('sound_trans.png', 'menu'))
sound_slid = (load_asset('sound_sel.png', 'menu'), load_asset('sound_slider.png', 'menu'))

controls_toggle = load_asset('controls.png', 'menu')
graphics_toggle = (load_asset('800x600.png', 'menu'), load_asset('1280x1024.png', 'menu'),
load_asset('1920x1090.png', 'menu'))
def s_toggle():
    global sound
    if sound:
        sound = 0
    else:
        sound = 50

def r_toggle():
    file = open('Reso.txt', 'w')
    if reso_p.res[0] == '800':
        reso_p.res = '1280', '1024'
        file.write('1280, 1024')
    elif reso_p.res[0] == '1280':
        reso_p.res = '1920', '1080'
        file.write('1920, 1080')
    else:
        reso_p.res = '800', '600'
        file.write('800, 600')
    file.close()

def r_upd():
    if reso_p.res[0] == '800':
        return 0
    elif reso_p.res[0] == '1280':
        return 1
    else:
        return 2

def s_upd():
    if sound == 0:
        return 0
    if sound:
        return 1


def s_change(dir):
    global sound
    if dir == 'right' and sound < 100: sound += 1
    if dir == 'left' and sound > 0: sound -= 1
def t_update():
    return sound

class Menu:

    def __init__(self, bkg_img, menu_name):
        self.name = menu_name
        self.background = bkg_img
        self.next_id = 0
        self.select = 0
        self.button_list = []

    class ToggleButton:
        def __init__(self, img_list, sel_img, name, cords, id):
            self.id = id
            self.cords = cords
            self.name = name
            self.img_list = img_list
            self.sel_img = sel_img
            self.cur_img = 0
            self.length = len(img_list)
            self.type = 'toggle'
            self.rect = self.img_list[0].get_rect(topleft=self.cords)

        def draw(self, select):
            win.blit(self.img_list[self.cur_img], self.cords)
            if select == self.id:
                win.blit(self.sel_img, self.cords)

    class TransferButton:
        def __init__(self, img, sel_img, name, cords, id, trans):
            self.id = id
            self.cords = cords
            self.name = name
            self.img = img
            self.sel_img = sel_img
            self.trans = trans
            self.type = 'transfer'
            self.rect = self.img.get_rect(topleft=self.cords)

        def draw(self, select):
            win.blit(self.img, self.cords)
            if select == self.id:
                win.blit(self.sel_img, self.cords)

        def clicked(self):
            global game_state
            game_state = self.trans

    class Slider:
        def __init__(self, img, sel_img, name, cords, txt_cords, txt_def, font, id):
            self.img = img
            self.sel_img = sel_img
            self.name = name
            self.cords = cords
            self.text_cords = txt_cords
            self.id = id
            self.text = txt_def
            self.font = font
            self.type = 'slider'
            self.rect= self.img.get_rect(topleft=self.cords)

        def draw(self, select):
            win.blit(self.img, self.cords)
            win.blit(self.font.render(F'{self.text}', False, (0, 0, 0)), self.text_cords)
            if select == self.id:
                win.blit(self.sel_img, self.cords)

    def draw(self):
        win.blit(self.background, (0, 0))
        for value in self.button_list:
            value.draw(self.select)
        pygame.display.update()

    def create_toggle_button(self, name, sel_img, img_list, cords, func, upd_func):
        new_button = self.ToggleButton(img_list, sel_img, name, cords, self.next_id)
        new_button.clicked = func
        new_button.update = upd_func
        self.button_list.append(new_button)
        self.next_id += 1

    def create_transfer_button(self, img, sel_img, name, cords, trans):
        new_button = self.TransferButton(img, sel_img, name, cords, self.next_id, trans)
        self.button_list.append(new_button)
        self.next_id += 1

    def create_slider_button(self, img, sel_img, name, cords, text_cords, txt_def, font, update_func, prime_func):
        new_button = self.Slider(img, sel_img, name, cords, text_cords, txt_def, font, self.next_id)
        new_button.update = update_func
        new_button.clicked = prime_func
        self.button_list.append(new_button)
        self.next_id += 1

    def handle_menu_nav(self, event):
        """Lets you linearly navigate through menus with up or down keys."""
        if event.key == pygame.K_DOWN:  # could make the numbers matrices, so you can move selected from side to side too.
            if self.select < len(self.button_list)-1:
                self.select += 1
        elif event.key == pygame.K_UP:
            if self.select > 0:
                self.select -= 1


    def run_menu(self, framerate):
        global game_state
        internal_timer = 10
        while game_state == self.name:
            clock.tick(framerate)
            t_button = self.button_list[self.select]
            for button in self.button_list:
                if button.type == 'toggle':
                    button.cur_img = button.update()
                if button.type == 'slider':
                    button.text = button.update()
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    self.handle_menu_nav(event)
                    t_button = self.button_list[self.select]
                    if event.key == pygame.K_RETURN:
                        if t_button.type != "slider":
                            t_button.clicked()
                            if t_button.type == 'toggle':
                                t_button.cur_img = t_button.cur_img % (t_button.length) - 1
                    elif event.key == pygame.K_ESCAPE:
                        if game_state == 'main':
                            return 'quit'
                        game_state = 'main'
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        pos = pygame.mouse.get_pos()
                        for button in self.button_list:
                            if button.rect.collidepoint(pos):
                                if self.button_list[self.select] == button:
                                    if button.type != "slider":
                                        button.clicked()
                                        if button.type == 'toggle':
                                            button.cur_img = button.cur_img % button.length - 1
                                else:
                                    for place, n_button in enumerate(self.button_list):
                                        if n_button == button:
                                            self.select = place
                    if event.button == 5 and t_button.type == 'slider':
                        t_button.clicked('left')
                        internal_timer = 10
                    if event.button == 4 and t_button.type == 'slider':
                        t_button.clicked('right')
                        internal_timer = 10
            press = pygame.key.get_pressed()
            if press[pygame.K_LEFT] and t_button.type == 'slider' and internal_timer == 0:
                t_button.clicked('left')
                internal_timer = 10
            elif press[pygame.K_RIGHT] and t_button.type == 'slider' and internal_timer == 0:
                t_button.clicked('right')
                internal_timer = 10
            if internal_timer > 0:
                internal_timer -= 1

main_menu = Menu(menu_backgrounds['good one'], 'main')
main_menu.create_toggle_button('resolution', sound_toggle[0], graphics_toggle, (350, 250), r_toggle, r_upd)
main_menu.create_slider_button(sound_slid[1], sound_slid[0], 'sound slider',  (350, 350), (430, 370),
                                str(sound), small_font, t_update,s_change)
main_menu.create_transfer_button(controls_toggle, sound_trans[0], 'controls trans', (350, 450), 'controls') # controls (static screen)
# main_menu.create_transfer_button(sound_trans[1], sound_trans[0], 'sound trans', (350, 550), 'credits') # credits (static screen)

#reso toggle

controls_menu = Menu(menu_backgrounds['controls'], 'controls')
controls_menu.create_slider_button(sound_slid[1], sound_slid[0], 'sound slider',  (350000, 450), (30000, 470),
                                str(sound), small_font, t_update,s_change)


menu_dict = {
    'main': main_menu,
    'controls': controls_menu
}

def run_menu():
    while True:
        if menu_dict[game_state].run_menu(60) == 'quit':
            return
