#initialisation
"""Fishing game scope

The fishing should be based on washington fishing.

-character customization? (deeply optional)

-2d world where you can walk around. The world should consist of: walkable tiles, fishable tiles, transfer tiles, interactable tiles.

-A couple of npcs should exist but they are very hollow and are just interactable tiles that spit information,

-fishing should be an actually fun minigame.

-There should be different fish for different areas.

-Start with 15 fish.
-Salmon (made)
-deep sea sable fish
-angler fish
-trout
-tuna
-hawk fish
-banded angel fish
-emporer angel fish
-bicolor angel fish
-jellyfish
-eel
-trash
-treasure
-masked rabbitfish
-parrotfish
-gift fish
-reindeer fish

-fish pokedex (optional)

-fish capture and display

-fish cooking

-atleast 4 areas probably under 10 total

-unlockable areas?
(mellow lake start)
(quick river)
(player house)
(close ocean boating)
(commercial shop)
(reef boating)
(deep sea boating)
(side plot house 1)
(dream world house)
(dream world fishing)

-starting areas should be self-sufficient with a place to fish and sell them.

-Maybe it depicts a rural town in a country turning bad. Pollution could be a good example of this. Once you get to sea fishing it could slowly get worse and worse. Eventually the game ending with the character putting down their fishing rod. You could also use a  anolouge to pollution. This could be anything from prions to Cthulu. It also sets up a sequel where you try to reclaim the water. It should also be christmas themed. There could be 2 endings one where you overfish and overstress too try and get a present for your family. The family would be sorta happy the lake would be depressed. In another you just gift the best fish you can instead and all eat it together. Since you did not overfish for money flying fish flow across the sky and stuff so it is happy. There could also be 2 other endings one were you overfish but don’t get the present instead keeping the money for yourself and everything really sucks. And then the best ending where you steal the gift/convince the seller to give it to you without overfishing or even by just making enough money non commercial fishing like with maybe a special type of rod that gives alot of treasure.

The game should have a mode where it only takes 10-20m.

It could be some sort of a magical world where at the end some fish manage to survive.
"""
import logging
import textM
from system_modules.fishing_quests import QuestSystem
from system_modules.stat_tracker import player_tracker

import Decor
from system_modules import minigame
from setup import map_mod
import sound_library
from setup.globals import Global

from system_modules.interactible_zone import market_zone

from ui_modules import balance, inventory, menu_handler

from setup.map_mod import win
from toolbox import return_corners, load_asset, blank_func

from entity_classes.fish import Fish
from entity_classes.fish_spawner import FishSpawner

from entity_classes.NPCs import old_man
from entity_classes import NPCs

from entity_classes.player_mod import player, PlayerSprite

from sound_library import *

pygame.display.set_caption('Gamble core')
clock = pygame.time.Clock()

from menu_functions import text_box

from setup import config

pygame.init() # I do not know if this is relevant

def init_main():
    """Adds all high decorations into the game and then rescales everything"""
    for decor in Decor.HighDecor.decor_sprites.sprites():
        Global.spritelist.add(decor)
    rescale_game()

Global.spritelist.add(player)

# quests are all initialized upon loading the game. They should not take up
# any processing power while the game is running. (besides the active quest)
quests = [
# start game with dialouge lines of the character wishing they could get a cool boat for fishing and leisure
QuestSystem(player_tracker.npcs_talked_to, "talk_to", 'old_man', 1,
            load_asset('talk to.png', 'quest_imgs'),
            pygame.font.SysFont('Comic Sans MS', 10),
            F"Talk to the old man", NPCs.old_man_quest_func, blank_func, 'tutorial1'),

QuestSystem(player_tracker.fish_caught, "catch_fish", 'total', 1,
        load_asset('catch fish.png', 'quest_imgs'),
        pygame.font.SysFont('Comic Sans MS', 10),
            F"Catch {1} fish", blank_func, blank_func, 'fish_catching1'),

QuestSystem(player_tracker.npcs_talked_to, "talk_to", 'old_man', 1,
            load_asset('talk to.png', 'quest_imgs'),
            pygame.font.SysFont('Comic Sans MS', 10),
            F"Talk to the {old_man.name}", NPCs.old_man_quest_func, blank_func, 'tutorial2'),

QuestSystem(player_tracker.fish_sold, "sell", 'total', 1,
        load_asset('sell fish.png', 'quest_imgs'),
        pygame.font.SysFont('Comic Sans MS', 10),
            F"sell {1} fish", blank_func, blank_func, 'fish_selling1'),

QuestSystem(player_tracker.npcs_talked_to, "talk_to", 'old_man', 1,
            load_asset('talk to.png', 'quest_imgs'),
            pygame.font.SysFont('Comic Sans MS', 10),
            F"Talk to the {old_man.name}", NPCs.old_man_quest_func, blank_func, 'tutorial3'),

QuestSystem(player_tracker.fish_caught, "catch_fish", 'salmon', 3,
        load_asset('catch fish.png', 'quest_imgs'),
        pygame.font.SysFont('Comic Sans MS', 10),
            F"Catch {3} salmon", blank_func, blank_func, 'fish_catching1'),

QuestSystem(player_tracker.npcs_talked_to, "talk_to", 'old_man', 1,
            load_asset('talk to.png', 'quest_imgs'),
            pygame.font.SysFont('Comic Sans MS', 10),
            F"Talk to the {old_man.name}", NPCs.old_man_quest_func, blank_func, 'tutorial4'),

QuestSystem(player_tracker.fish_caught, "catch_fish", 'bass', 1,
        load_asset('catch fish.png', 'quest_imgs'),
        pygame.font.SysFont('Comic Sans MS', 10),
            F"Catch {1} bass", blank_func, blank_func, 'fish_catching1'),

QuestSystem(player_tracker.npcs_talked_to, "talk_to", 'old_man', 1,
            load_asset('talk to.png', 'quest_imgs'),
            pygame.font.SysFont('Comic Sans MS', 10),
            F"Talk to the {old_man.name}", NPCs.old_man_quest_func, blank_func, 'tutorial5'),

QuestSystem(player_tracker.fish_caught, "catch_fish", 'total', 999,
        load_asset('catch fish.png', 'quest_imgs'),
        pygame.font.SysFont('Comic Sans MS', 10),
            F"Catch 9̶̪̥́̊9̵̔̒bass", blank_func, blank_func, 'fish_catching1'),
]

QuestSystem.quest_init(quests) # starts the tutorial quests

"""Rescales all UI_scale based elements"""
def rescale_ui():
    text_box.textbox.image = pygame.transform.scale(text_box.textbox.image, text_box.textbox.dimensions)
    inventory.Inventory.rescale()
    balance.balance.rescale()
    # dialouge box is defined already rescaled

"""Rescales all game scale based elements"""
def rescale_game():
    rescale_ui()
    for sprite in Global.spritelist.sprites():
        if not isinstance(sprite, PlayerSprite):
            sprite.rescale()
    for sprite in Decor.LowDecor.decor_sprites.sprites():
        sprite.rescale()
    player.rescale_player()

"""Returns full map surface to draw"""
def generate_surface():
    return map_mod.tile_convert(Global.game_map)

"""Draws out quest notifications"""
def draw_notifications():
    if QuestSystem.cur_quest().mode == 'start':
        QuestSystem.cur_quest().start(timer)
    elif QuestSystem.cur_quest().mode == 'finish':
        QuestSystem.cur_quest().finish(timer)
    elif not QuestSystem.cur_quest().mode:
        ''

"""Draws all UI elements"""
def draw_ui():
    balance.balance.draw()
    inventory.inventory.draw(pos)
    text_box.textbox.draw()
    pos_p = (pos[0] + xp, pos[1] + yp)
    win.blit(textM.small_comic.render(str(pos_p), False, (0, 0, 0)), (700, 10))  # shows cursor cords
    QuestSystem.cur_quest().draw(Global.UI_scale)

def dynamic_drawing(): # TO DO: make this o(n) time by only checking neighborhood and also make it so that I am not drawing everything
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
                if player.inspect(old_man, QuestSystem.cur_quest()):
                    ''
                elif player.text_cur:
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
ps = player.xp_yp
yp, xp =  ps[0], ps[1]
Fish.update_fish(player, timer, inventory, game_state, grid_ahead, yp, xp)
while True:
    sound_library.update_volume()
    pos = pygame.mouse.get_pos()
    ps = player.xp_yp
    yp, xp =  ps[0], ps[1]
    drawmap()
    clock.tick(60)
    # timer
    timer += 1
    if timer > 9999: # check for bugs every now and then.
        timer = 0
    if timer % 120 == 0:
        if not QuestSystem.cur_quest().live:
            quests.pop(0)
            QuestSystem.cur_quest_value = 0
        FishSpawner.spawn_all(grid_ahead, inventory, Global.spritelist)

    #update fish then map
    Fish.update_fish(player, timer, inventory, game_state, grid_ahead, yp, xp) # checks to see if a fish is on the hook. updates Fish.fish_caught
    hooked_fsh = Fish.fish_caught
    # Fish.rescale()
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
        state = minigame.run((player.cords[0] - xp, player.cords[1] - yp), Fish.fish_took.cautiousness)
        if state == 'success':
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
        elif state == 'failure':
            game_state = 'main'
            if isinstance(hooked_fsh, Fish):
                hooked_fsh.kill()
                Fish.fish_caught.ignore = 10
            player.stop_fishing(Fish)
            player.cast_length = 0
    pygame.display.update()
    player.update_can_move() # checks whether the player should be able to move or not

