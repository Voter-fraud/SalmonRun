from config import pygame, UI_scale
from reso_p import win
from toolbox import load_asset
import os, copy, reso_p, Decor
class Item:
    items = {

    }
    next_id = 1
    @classmethod
    def ret_fish(cls):
        ret = {}
        for key, value in cls.items.items():
            if value.is_fish:
                ret[key] = 0
        ret['total'] = 0
        return ret

    @classmethod
    def new(cls, name):
        new = copy.copy(cls.items[name])
        new.id = cls.next_id
        cls.next_id += 1
        return new

    def __init__(self, is_tool, is_fish, img, name):
        self.is_tool = is_tool
        self.is_fish = is_fish
        self.img = pygame.transform.scale(img, (32*UI_scale, 32*UI_scale))
        self.name = name
        self.id = 0
    def draw(self, cords):
        win.blit(self.img, cords)
    def copy_new(self):
        new2 = self
        new = copy.copy(new2)
        return new

item_imgs = {
    'fish':  load_asset('fish_item.png','items' ),
    'salmon': load_asset('salmon_item.png', 'items', ),
    'carp': load_asset('carp_item.png', 'items', ),
}

def item_from_str(item_str):
    if item_str[2] not in Item.items.keys():
        if item_str == 'False':
            item_str[0] = False
        if item_str == 'False':
            item_str[1] = False
        Item.items[item_str[2]] = Item(item_str[0], item_str[1], item_imgs[item_str[2]], item_str[2])

def import_item_list(file):
    read = open(file, 'r').readlines()
    item_raw = []
    for char in read:  # generates a row out of each line
        item_raw.append(char.strip())
    item = []
    for line in item_raw:  # makes each row a list of individual tiles.
        if line == '':
            break
        x = line.split(",")
        new_x = []
        for chat in x:
            chat.strip()
            blop = True
            i = 0
            while blop:
                if list(chat)[i] == '=':
                    new_x.append(chat[i+1:])
                    blop = False
                i += 1
        item.append(new_x)
    return item

for i in import_item_list('item.txt'):
    item_from_str(i)

class Inventory:
    inventory_slot = load_asset('inventory_slot.png', 'items')
    @classmethod
    def rescale(cls):
        cls.inventory_slot = pygame.transform.scale(cls.inventory_slot, (32 * UI_scale, 32 * UI_scale))
        inventory.highlight = pygame.transform.scale(inventory.highlight, (32*UI_scale, 32*UI_scale))
        inventory.active = reso_p.win_height-110*UI_scale, 110*UI_scale

    def __init__(self):
        self.tool_slot = ''
        self.inv = [
            [Item.new('fish'), '', ''],
            ['', '', ''],
            ['', '', ''],
        ]
        self.highlight = load_asset('inv_select.png', 'items')
        self.grabbed = ''
        self.active = reso_p.win_height-110*UI_scale, 110*UI_scale
    def draw(self, pos):
        y = reso_p.win_height-102*UI_scale
        for row in self.inv:
            x = 2
            for slot in row:
                box = pygame.Rect(x, y, 32*UI_scale, 32*UI_scale)
                win.blit(Inventory.inventory_slot, (x, y))
                if box.collidepoint(pos):
                    win.blit(self.highlight, (x, y))
                if isinstance(self.grabbed, Item):
                    self.grabbed.draw((pos[0]-16*UI_scale, pos[1]-16*UI_scale))
                if isinstance(slot, Item):
                    slot.draw((x, y))
                x += 32*UI_scale+2
            y += 32*UI_scale+2
    def click(self, pos):
        y = reso_p.win_height - 102*UI_scale
        yt = 0
        for row in self.inv:
            x = 2
            xt = 0
            for slot in row:
                box = pygame.Rect(x, y, 32*UI_scale, 32*UI_scale)
                if box.collidepoint(pos):
                    if isinstance(slot, Item):
                        self.grabbed = slot.copy_new()
                    else:
                        self.grabbed = ''
                    self.inv[yt][xt] = ''
                    break
                x += 32*UI_scale+2
                xt += 1
            y += 32*UI_scale+2
            yt+= 1
    def release(self, pos, grab_pos, player, balance, tracker):
        if self.grabbed:
            for sprite in Decor.HighDecor.decor_sprites.sprites():
                if sprite.name == 'market':
                    sprite.rescale()
                    sprite.update()
                    if sprite.rect.collidepoint(grab_pos):
                        if isinstance(self.grabbed, Item) and self.grabbed.is_fish:
                            tracker.sell_fish(self.grabbed.name)
                            print(tracker.fish_sold)
                        self.grabbed = ''
                        player.text_cur = 'sold'
                        balance.add_money(10)
                        return ''
            y = reso_p.win_height - 102*UI_scale
            yt = 0
            for row in self.inv:
                x = 2
                xt = 0
                for slot in row:
                    box = pygame.Rect(x, y, 32*UI_scale, 32*UI_scale)
                    if box.collidepoint(pos) and isinstance(self.grabbed, Item):
                        self.inv[yt][xt] = self.grabbed.copy_new()
                        self.grabbed = ''
                        return slot
                    x += 32*UI_scale+2
                    xt += 1
                y += 32*UI_scale+2
                yt += 1
            self.add_item(self.grabbed)
            self.grabbed = ''
    def add_item(self, item):
        yt = 0
        for row in self.inv:
            xt = 0
            for slot in row:
                if not slot:
                    self.inv[yt][xt] = item.copy_new()
                    self.grabbed = ''
                    return ''
                xt += 1
            yt += 1

inventory = Inventory()
