from config import pygame, UI_scale
from reso_p import win
from toolbox import load_asset
import os, copy, reso_p, Decor
class Item:
    items = {

    } # list of all valid items
    @classmethod
    def ret_items(cls, prop):
        """Return a dict of all items that have the given property with their values being 0, as well as a total key"""
        item_dict = {}
        for key, value in cls.items.items():
            if getattr(value, prop, False):
                item_dict[key] = 0

        item_dict['total'] = 0
        return item_dict

    @classmethod
    def new(cls, name):
        """Creates a new item instance"""
        new = copy.copy(cls.items[name])
        return new

    def __init__(self, is_tool, is_fish, img, name):
        self.is_tool = is_tool
        self.is_fish = is_fish
        self.img = pygame.transform.scale(img, (32*UI_scale, 32*UI_scale))
        self.name = name

    def draw(self, cords):
        """Draws the item at the specefied cords"""
        win.blit(self.img, cords)

    def rescale(self):
        """Rescales an item in accordance with UI_scale"""
        self.img = pygame.transform.scale(self.img, (32 * UI_scale, 32 * UI_scale))

    def copy_new(self):
        """Returns a copy of an item instance"""
        new2 = self
        new = copy.copy(new2)
        return new

def item_from_str(item_str):
    """Adds an item to the items dict from a formatted string list."""
    # this function is likely to only ever be used by the import_item_list function because it had the right formatting
    is_tool, is_fish, name = item_str[0], item_str[1], item_str[2]
    if is_tool == 'False':
        is_tool = False
    if item_str == 'False':
        is_fish = False
    Item.items[name] = Item(is_tool, is_fish, load_asset(F'{name}_item.png', 'items', ), name)

def import_item_list(file):
    """Turns a text file containing formatted item information into a list of lists(items)"""
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

# this code configures the item list
for i in import_item_list('item.txt'):
    item_from_str(i)

class Inventory:

    @classmethod
    def rescale(cls):
        """Rescales the inventory based on UI_scale"""
        inventory.inventory_slot = pygame.transform.scale(inventory.inventory_slot, (32 * UI_scale, 32 * UI_scale))
        inventory.highlight = pygame.transform.scale(inventory.highlight, (32*UI_scale, 32*UI_scale))
        inventory.active = reso_p.win_height-110*UI_scale, 110*UI_scale

    def __init__(self):
        self.inventory_slot = load_asset('inventory_slot.png', 'items')
        self.inv = [
            [Item.new('fish'), '', ''],
            [Item.new('salmon'), '', ''],
            ['', '', ''],
        ]
        self.highlight = load_asset('inv_select.png', 'items')
        self.grabbed = '' # What you are currently holding
        self.bait_slot = ''
        self.active = reso_p.win_height-110*UI_scale, 110*UI_scale # area in which inventory collisions are checked
        self.slot_size = 32 * UI_scale
        self.gap = 2

    def draw(self, pos):
        """Draws the inventory, items in it, and the grabbed item"""
        y = reso_p.win_height-(self.slot_size+self.gap)*3 # starting y value. we draw left to right top to bottom.
        for row in self.inv:
            x = self.gap # starting x value
            for slot in row:
                box = pygame.Rect(x, y, self.slot_size, self.slot_size)
                win.blit(inventory.inventory_slot, (x, y))
                if box.collidepoint(pos):
                    win.blit(self.highlight, (x, y))
                if isinstance(slot, Item):
                    slot.draw((x, y))
                x += self.slot_size+self.gap
            y += self.slot_size+self.gap
        #bait slot
        x = self.gap*5+self.slot_size*3  # equivalent to 3 spaces right and a extra gap
        y -= self.slot_size+self.gap+12
        box = pygame.Rect(x, y, self.slot_size, self.slot_size)
        win.blit(inventory.inventory_slot, (x, y))
        if box.collidepoint(pos):
            win.blit(self.highlight, (x, y))
        if isinstance(self.bait_slot, Item):
            self.bait_slot.draw((x, y))

        if isinstance(self.grabbed, Item):
            self.grabbed.draw((pos[0]-(self.slot_size/2), pos[1]-(self.slot_size/2)))

    def click(self, pos):
        """Handles clicking when related to the inventory. (grabs items to move)"""
        # this function is only called when a click is in the self.active zone
        y = reso_p.win_height-(self.slot_size+self.gap)*3 # y cords
        for row_i, row in enumerate(self.inv):
            x = self.gap # x cords
            for slot_i, slot in enumerate(row):
                box = pygame.Rect(x, y, self.slot_size, self.slot_size)
                if box.collidepoint(pos):
                    if isinstance(slot, Item):
                        # grab the item
                        self.grabbed = slot.copy_new()
                        self.inv[row_i][slot_i] = ''
                        # the grabbed item is placed back into your inventory after releasing the skip
                    break
                x += self.slot_size+self.gap
            y += self.slot_size+self.gap

    def release(self, pos, grab_pos, player, balance, tracker):
        """Lets go of a grabbed item and places it in the given slot or sells it on the market."""
        if self.grabbed:
            for sprite in Decor.HighDecor.decor_sprites.sprites():
                if sprite.name == 'market':
                    if sprite.rect.collidepoint(grab_pos):
                        if isinstance(self.grabbed, Item) and self.grabbed.is_fish:
                            tracker.sell_fish(self.grabbed.name)
                        self.grabbed = ''
                        player.text_cur = 'sold'
                        balance.add_money(10) # make varying prices later
                        return ''
            y = reso_p.win_height-(self.slot_size+self.gap)*3 # y cords
            for row_i, row in enumerate(self.inv):
                x = self.gap  # x cords
                for slot_i, slot in enumerate(row):
                    box = pygame.Rect(x, y, self.slot_size, self.slot_size)
                    if box.collidepoint(pos) and isinstance(self.grabbed, Item) and not self.inv[row_i][slot_i]:
                        self.inv[row_i][slot_i] = self.grabbed.copy_new()
                        self.grabbed = ''
                        return slot
                    x += self.slot_size+self.gap
                y += self.slot_size+self.gap

            x = self.gap * 5 + self.slot_size * 3  # equivalent to 3 spaces right and a extra gap
            y -= self.slot_size + self.gap + 12
            box = pygame.Rect(x, y, self.slot_size, self.slot_size)
            if box.collidepoint(pos) and isinstance(self.grabbed, Item) and not self.bait_slot:
                self.bait_slot = self.grabbed.copy_new()
                self.grabbed = ''
                return "baitslot"

            self.add_item(self.grabbed)
            self.grabbed = ''

    def add_item(self, item):
        """Adds a new item """
        for row_i, row in enumerate(self.inv):
            for slot_i, slot in enumerate(row):
                if not slot:
                    self.inv[row_i][slot_i] = item.copy_new()
                    self.grabbed = ''
                    return ''

    def use_bait(self):
        self.bait_slot = ''

inventory = Inventory()
