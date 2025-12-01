#initialisation
import logging
import fishing_quests
import reso_p
import menu_handler

import Decor, minigame
import map_mod
import sound_library
import toolbox

from interactible_zone import market_zone

import config # just to run config
from globals import Global

import balance

from map_mod import win
from toolbox import return_corners, load_asset
from textM import text_box, textbox_font

import inventory

from fish import Fish, FishSpawner

from NPCs import old_man
import NPCs

from player_mod import player, PlayerSprite

from sound_library import *

from reso_p import scale

pygame.display.set_caption('Gamble core')
clock = pygame.time.Clock()

pygame.init() # I do not know if this is relevant

def init_main():
    """Adds all high decorations into the game and then rescales everything"""
    for decor in Decor.HighDecor.decor_sprites.sprites():
        Global.spritelist.add(decor)
    rescale_game()

class StatTracker:
    def __init__(self, linked_player):
        self.player = linked_player
        self.fish_caught = inventory.Item.ret_items('is_fish')
        self.fish_sold = inventory.Item.ret_items('is_fish')

    def catch_fish(self, fish_name):
        self.fish_caught[fish_name] += 1
        self.fish_caught['total'] += 1
        if isinstance(cur_quest, fishing_quests.FishCatching):
            cur_quest.update(player_tracker.fish_caught)

    def sell_fish(self, fish_name):
        self.fish_sold[fish_name] += 1
        self.fish_sold['total'] += 1
        if isinstance(cur_quest, fishing_quests.FishSelling):
            cur_quest.update(player_tracker.fish_sold)

class FishingRod:
    def __init__(self, use_anim, max_cast, lure):
        self.frames = use_anim
        self.max_cast = max_cast
        self.lure = lure



player_tracker = StatTracker(player)
Global.spritelist.add(player)

quests = [
# start game with dialouge lines of the character wishing they could get a cool boat for fishing and leisure
fishing_quests.TalkTo(old_man, load_asset('talk to.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 10), NPCs.old_man_linear1),
fishing_quests.FishCatching(1, False, player_tracker.fish_caught, load_asset('catch fish.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 20), 'Catch 3 Fish'),
fishing_quests.TalkTo(old_man, load_asset('talk to.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 10), NPCs.old_man_seller),
fishing_quests.FishSelling(1, False, player_tracker.fish_sold, load_asset('sell fish.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 20), 'Sell 3 fish'),
fishing_quests.TalkTo(old_man, load_asset('talk to.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 10), NPCs.old_man_salmon),
fishing_quests.FishCatching(1, 'salmon', player_tracker.fish_caught, load_asset('catch fish.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 20), 'Catch 2 salmon'),
fishing_quests.FishSelling(1, 'salmon', player_tracker.fish_sold, load_asset('sell fish.png', 'quest_imgs'), pygame.font.SysFont('Comic Sans MS', 20), 'Sell 3 fish'),
]

cur_quest = quests[0]

def rescale_ui():
    global text_box, textbox_font
    text_box = pygame.transform.scale(text_box, (510*Global.UI_scale, 70*Global.UI_scale))
    textbox_font = pygame.font.SysFont('Comic Sans MS', 20*Global.UI_scale)
    inventory.Inventory.rescale()
    balance.balance.rescale()

def rescale_game():
    rescale_ui()
    for sprite in Global.spritelist.sprites():
        if not isinstance(sprite, PlayerSprite):
            sprite.rescale()
    for sprite in Decor.LowDecor.decor_sprites.sprites():
        sprite.rescale()
    player.rescale_player()

def generate_surface():
    pss = player.xp_yp
    return map_mod.tile_convert(Global.game_map)

def draw_notifications():
    if cur_quest.mode == 'start':
        cur_quest.start(timer,  player_tracker.fish_caught)
    elif cur_quest.mode == 'finish':
        cur_quest.finish(timer)
    elif not cur_quest.mode:
        ''

def draw_ui():
    balance.balance.draw()
    inventory.inventory.draw(pos)
    small_font = pygame.font.SysFont('Comic Sans MS', 10)
    if player.text_cur: # draws sprite inspection dialog
        win.blit(text_box, ((reso_p.win_length-510*Global.UI_scale)/2, reso_p.win_height-80*Global.UI_scale))
        win.blit(textbox_font.render(str(player.text_cur), False, (0, 0, 0)), ((reso_p.win_length-475*Global.UI_scale)/2, reso_p.win_height-65*Global.UI_scale))
    pos_p = (pos[0] + xp, pos[1] + yp)
    win.blit(small_font.render(str(pos_p), False, (0, 0, 0)), (700, 10))  # shows cursor cords
    cur_quest.draw(Global.UI_scale)

def dynamic_drawing():
    """Draws inputted sprites in order of how high their Y cord is for example y=5 is drawn over y=4"""
    s_list = [] # becomes list of sprites to draw in order
    spritelist_copy = Global.spritelist.sprites().copy() # initial list of sprites
    for sprite in spritelist_copy:
        s_list.append((sprite.rect.bottomleft[1])) # tracks each sprites bottom coordinates
        s_list.sort()
    while True:
        for sprite in spritelist_copy:
            if sprite.rect.bottomleft[1] == s_list[0]: # looks through the initial list of sprites for a match
                if isinstance(sprite, Decor.HighDecor) or isinstance(sprite, NPCs.Conversible): #draws the matched sprite
                    sprite.draw(xp, yp)
                elif isinstance(sprite, Fish):
                    sprite.draw(player, game_state, timer, xp, yp)
                elif isinstance(sprite, PlayerSprite):
                    sprite.draw(timer)
                else:
                    sprite.draw()
                s_list.pop(0) # removes the drawn sprite so the process can start again
                spritelist_copy.remove(sprite)
                break
        if not s_list and not spritelist_copy: # if there is no more sprites to draw end the process
            return

def drawmap():
    """Draws player map"""
    win.blit(tile_map, (0-xp, 0-yp))
    if player.hook_cords:
        win.blit(player.bauble, (player.hook_cords[0]-xp, player.hook_cords[1]-yp))
    for spritedecor in Decor.LowDecor.decor_sprites.sprites():
        spritedecor.draw(xp, yp)
    dynamic_drawing()
    draw_ui()
    draw_notifications()

def grid_ahead(cords, length, width):
    corners = return_corners(cords, width, length)
    return map_mod.return_grids(corners, Global.game_map)

def check_walkable(noclip, dist):
    if noclip:
        return True
    if '1' in grid_ahead(player.check_obst(dist), player.height, player.width):
        return False
    if '3' in grid_ahead(player.check_obst(dist), player.height, player.width):
        return False
    return True

def handle_events():
    global game_state
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                if not player.hook_cords:
                    player.fish_hold = False
                    player.cast_rod()
                    Fish.scared_check(player.hook_cords)
                else:
                    player.stop_fishing(Fish)
                player.cast_length = 0
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                if player.inspect(old_man, cur_quest):
                    if player.text_cur:
                        player.text_cur = False
                else:
                    market_zone.check_interaction(player.rect)
            if event.key == pygame.K_ESCAPE:
                if player.text_cur:
                    player.text_cur = False
                else:
                    menu_handler.run_menu('main')
            if event.key == pygame.K_q:
                player.sprint_toggle()
            if event.key == pygame.K_SPACE:
                handle_rod()
            if event.key == pygame.K_F11:
                game_state = 'minigame'
        inv = inventory.inventory
        if event.type == pygame.MOUSEBUTTONDOWN:
            grab_pos()  # prints cursor location useful for debugging
            if event.button == 1:
                if pos[1] > inv.active[0] and inv.active[
                    1] or inv.grabbed:  # checks if you are withing the inventories cords to avoid pointless and relatively expensive checks
                    inv.click(pos)
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if pos[1] > inv.active[0] and inv.active[1] or inv.grabbed:
                    inv.release(pos, grab_pos(), player, balance, player_tracker)

def handle_key_holds():
    if player.can_move:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # make high-end functions more readable
            player.facing = 'left'
            if check_walkable(player.noclip, player.speed):
                player.cords[0] += -player.speed
            elif check_walkable(player.noclip, 1):
                player.cords[0] += -1
            player.walking = True

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.facing = 'right'
            if check_walkable(player.noclip, player.speed):
                player.cords[0] += player.speed
            elif check_walkable(player.noclip, 1):
                player.cords[0] += 1
            player.walking = True

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.facing = 'up'
            if check_walkable(player.noclip, player.speed):
                player.cords[1] += -player.speed
            elif check_walkable(player.noclip, 1):
                player.cords[1] += -1
            player.walking = True

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.facing = 'down'
            if check_walkable(player.noclip, player.speed):
                player.cords[1] += player.speed
            elif check_walkable(player.noclip, 1):
                player.cords[1] += 1
            player.walking = True

        if player.walking:
            if timer%30 == 0:
                walking_sound.play()

    if not player.hook_cords and not player.text_cur and keys[pygame.K_SPACE]:
        if not player.fish_hold:
            player.fish_hold = True
        player.cast_length += 1

def grab_pos():
    print(pos[0] + xp, pos[1] + yp)
    return pos[0] + xp, pos[1] + yp
timer = 0

def handle_rod():
    global game_state
    if player.hook_cords and hooked_fsh:
        if Fish.fish_took == hooked_fsh: # if fish is catchable when you pull the rod
            game_state = 'minigame'

init_main()
tile_map = generate_surface()
game_state = 'main'
Fish.rescale()
Fish.update_fish(player, timer, inventory, game_state, grid_ahead)
while True:
    sound_library.update_volume()
    pos = pygame.mouse.get_pos()
    ps = player.xp_yp
    yp, xp =  ps[0], ps[1]
    drawmap()
    clock.tick(60)
    # timer
    timer += 1
    if timer > 9999:
        timer = 0
    if timer % 120 == 0:
        if not cur_quest.live:
            quests.pop(0)
            cur_quest = quests[0]
            if isinstance(cur_quest, fishing_quests.TalkTo):
                old_man.linear_list = cur_quest.newtext
                old_man.status = 0
                old_man.active = True
        FishSpawner.spawn_all(grid_ahead, inventory, Global.spritelist)

    #update fish then map
    Fish.update_fish(player, timer, inventory, game_state, grid_ahead) # checks to see if a fish is on the hook. updates Fish.fish_caught
    hooked_fsh = Fish.fish_caught
    Fish.rescale()
    player.update()
    for decorr in Decor.HighDecor.decor_sprites.sprites():
        decorr.update()
    player.walking = False
    #keyholds
    #event handler
    if game_state == 'main':
        keys = pygame.key.get_pressed()
        handle_key_holds()
        handle_events()

    elif game_state == 'minigame':
        if minigame.run((player.cords[0]-xp, player.cords[1]-yp)) == 'success':
            game_state = 'main'
            if player.hook_cords:
                rod_pull_sound.play()
            if isinstance(hooked_fsh, Fish):
                player_tracker.catch_fish(hooked_fsh.item.name)
                inventory.inventory.add_item(hooked_fsh.item)
                hooked_fsh.kill()
            else: # silly goofy error handling for if a fish is not on the line
                logging.warning("that's not a fish!")
                player.text_cur = "that's no fish!"
            player.stop_fishing(Fish)
            player.cast_length = 0
        elif minigame.run((player.cords[0]-xp, player.cords[1]-yp)) == 'failure':
            game_state = 'main'
            if isinstance(hooked_fsh, Fish):
                hooked_fsh.kill()
                Fish.fish_caught.ignore = 10
            player.stop_fishing()
            player.cast_length = 0
    pygame.display.update()
    player.update_can_move() # checks whether the player should be able to move or not

