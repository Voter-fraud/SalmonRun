#initialisation
import copy, fishing_quests, reso_p, logging, real_menu_handler

import Decor, minigame
import toolbox
from config import math, random, map_mod, os, pygame, game_map, UI_scale, spritelist
from map_mod import win
from toolbox import return_corners, load_asset
from textM import text_box, textbox_font
import inventory
from fish import Fish, FishSpawner
from NPCs import old_man
import NPCs
pygame.display.set_caption('Gamble core')
clock = pygame.time.Clock()

walking_sound = pygame.mixer.Sound('walking sound.mp3')
rod_cast_sound = pygame.mixer.Sound('rod_cast.mp3')
rod_pull_sound = pygame.mixer.Sound('fishingrod pull.mp3')

def init_main():
    """Adds all decor into the game and then rescales everything"""
    for decor in Decor.HighDecor.decor_sprites.sprites():
        spritelist.add(decor)
    rescale_game()


class PlayerSprite(pygame.sprite.Sprite):
    """Player character long term information"""
    walking_anim = { # Ew
        'down': (load_asset('buff generic guy w1.png', 'player' ), load_asset('buff generic guy w1.png', 'player'), load_asset('buff generic guy w1.png', 'player'), load_asset('buff generic guy w2.png', 'player' ), load_asset('buff generic guy w2.png', 'player'), load_asset('buff generic guy w2.png', 'player')),
        'up': (load_asset('buff generic guy bw1.png', 'player'), load_asset('buff generic guy bw1.png', 'player' ), load_asset('buff generic guy bw1.png', 'player'), load_asset('buff generic guy bw2.png', 'player'),  load_asset('buff generic guy bw2.png', 'player'), load_asset('buff generic guy bw2.png', 'player')),
        'right': (load_asset('buff generic guy rw1.5.png', 'player'), load_asset('buff generic guy rw1.png', 'player'), load_asset('buff generic guy rw1.5.png', 'player'), load_asset('buff generic guy rw2.5.png', 'player'),  load_asset('buff generic guy rw2.png', 'player'), load_asset('buff generic guy rw2.5.png', 'player')),
        'left': (load_asset('buff generic guy lw1.5.png', 'player'), load_asset('buff generic guy lw1.png', 'player'), load_asset('buff generic guy lw1.5.png', 'player'), load_asset('buff generic guy lw2.5.png', 'player'), load_asset('buff generic guy lw2.png', 'player'), load_asset('buff generic guy lw2.5.png', 'player'))
    }

    fishing_anim = {
        'down': [load_asset(F'buff generic guy F{x}.png', 'player') for x in range(1, 4)],

        'up': [load_asset(F'buff generic guy bF{x}.png', 'player') for x in range(1, 4)],

        'left': [load_asset(F'buff generic guy lF{x}.png', 'player') for x in range(1, 4)],

        'right': [load_asset(F'buff generic guy rF{x}.png', 'player') for x in range(1, 4)],
    }

    still = {
        'down': load_asset('buff generic guy.png', 'player'),
        'up': load_asset('buff generic guy b.png', 'player'),
        'left': load_asset('buff generic guy l.png', 'player'),
        'right': load_asset('buff generic guy r.png', 'player'),
    }

    fish_passive = {
        'down': load_asset('buff generic guy F1b.png', 'player'),
        'up': load_asset('buff generic guy bF1b.png', 'player'),
        'left': load_asset('buff generic guy lF1b.png', 'player'),
        'right': load_asset('buff generic guy rF1b.png', 'player'),
    }

    @classmethod
    def rescale_player(cls):
        for key, value in cls.walking_anim.items():
            cls.walking_anim[key] = (pygame.transform.scale(value[0], (16 * map_mod.scale, 32 * map_mod.scale)),
                                     pygame.transform.scale(value[1], (16 * map_mod.scale, 32 * map_mod.scale)),
                                     pygame.transform.scale(value[2],(16 * map_mod.scale, 32 * map_mod.scale)),
                                     pygame.transform.scale(value[3], (16 * map_mod.scale, 32 * map_mod.scale)),
                                     pygame.transform.scale(value[4], (16 * map_mod.scale, 32 * map_mod.scale)),
                                     pygame.transform.scale(value[5], (16 * map_mod.scale, 32 * map_mod.scale)))
        for key, value in cls.fishing_anim.items():
            if key == 'left' or key == 'right':
                cls.fishing_anim[key] = (pygame.transform.scale(value[0], (16 * map_mod.scale, 32 * map_mod.scale)),
                                         pygame.transform.scale(value[1], (16 * map_mod.scale, 32 * map_mod.scale)),
                                         pygame.transform.scale(value[2], (20 * map_mod.scale, 32 * map_mod.scale)))
            else:
                cls.fishing_anim[key] = (pygame.transform.scale(value[0], (16 * map_mod.scale, 32 * map_mod.scale)),
                                         pygame.transform.scale(value[1], (16 * map_mod.scale, 32 * map_mod.scale)),
                                         pygame.transform.scale(value[2], (16 * map_mod.scale, 32 * map_mod.scale)))
        for key, value in cls.still.items():
            cls.still[key] = pygame.transform.scale(value, (16 * map_mod.scale, 32 * map_mod.scale))
        for key, value in cls.fish_passive.items():
            cls.fish_passive[key] = pygame.transform.scale(value, (16 * map_mod.scale, 32 * map_mod.scale))

    def __init__(self):
        super().__init__()
        self.bauble = load_asset('bauble.png','player')
        self.cords = [1800*map_mod.scale, 1200*map_mod.scale] # top left
        self.text_cur = False
        self.facing = 'up'
        self.hook_cords = [] # if empty hook is not cast
        self.speed = 5
        self.cast_length = 0
        self.can_move = True
        self.fish_hold = False
        self.baitlevel = 20
        self.width = 16*map_mod.scale
        self.height = 32*map_mod.scale
        self.rect = PlayerSprite.still['up'].get_rect(topleft=self.cords)
        self.walking = False
        self.walking_frame = 0
        self.boot_cords = [reso_p.win_length / 2, reso_p.win_height / 2-self.height/4]
        self.noclip = False

    @property
    def v_center(self):
        return reso_p.win_length / 2 - self.width / 2, reso_p.win_height / 2 - self.height / 2

    def draw(self):
        """Draws player sprite"""
        if self.walking:
            win.blit(PlayerSprite.walking_anim[self.facing][self.walking_frame], self.v_center)
            if timer % 10 == 0:
                self.walking_frame += 1
                if self.walking_frame == 6:
                    self.walking_frame = 0
        elif self.hook_cords:
            if self.facing == 'down':
                win.blit(PlayerSprite.fish_passive[self.facing], self.v_center)
                toolbox.draw_line(self.rect.topleft, (self.hook_cords[0] + 1.3*map_mod.scale, self.hook_cords[1]), (255, 255, 255), win,
                                  xp, yp, 1)
                toolbox.draw_line(self.rect.topleft, (self.rect.center[0], self.rect.center[1]+4*map_mod.scale), (139,69,19), win, xp, yp, 3)
            elif self.facing == 'up':
                connector = [self.rect.topright[0]-3*map_mod.scale, self.rect.topright[1]-3*map_mod.scale]
                toolbox.draw_line(connector, (self.hook_cords[0] + 1.3*map_mod.scale, self.hook_cords[1]), (255, 255, 255), win,
                                  xp, yp, 1)
                toolbox.draw_line(connector, (self.rect.center[0], self.rect.center[1]+4*map_mod.scale), (139,69,19), win, xp, yp, 3)
                win.blit(PlayerSprite.fish_passive[self.facing], self.v_center)
            elif self.facing == 'left':
                connector = [self.rect.topleft[0] - 20, self.rect.topright[1] + 15]
                toolbox.draw_line(connector, (self.hook_cords[0] + 1.3*map_mod.scale, self.hook_cords[1]), (255, 255, 255), win,
                                  xp, yp, 1)
                toolbox.draw_line(connector, (self.rect.center[0] - 1 * map_mod.scale, self.rect.center[1]),
                                  (139, 69, 19), win, xp, yp, 3)
                win.blit(PlayerSprite.fish_passive[self.facing], self.v_center)
            elif self.facing == 'right':
                connector = [self.rect.topright[0]+20, self.rect.topright[1]+15]
                toolbox.draw_line(connector, (self.hook_cords[0] + 1.3*map_mod.scale, self.hook_cords[1]), (255, 255, 255), win,
                                  xp, yp, 1)
                toolbox.draw_line(connector, (self.rect.center[0]+1*map_mod.scale, self.rect.center[1]), (139,69,19), win, xp, yp, 3)
                win.blit(PlayerSprite.fish_passive[self.facing], self.v_center)
        elif self.cast_length:
            if math.floor(self.cast_length/10) >= 2 and self.facing == 'right':
                win.blit(PlayerSprite.fishing_anim[self.facing][2], (self.v_center[0]-4*map_mod.scale, self.v_center[1]))
            elif math.floor(self.cast_length / 10) < 3:
                win.blit(PlayerSprite.fishing_anim[self.facing][math.floor(self.cast_length / 10)], self.v_center)
            else:
                win.blit(PlayerSprite.fishing_anim[self.facing][2],
                         (self.v_center[0], self.v_center[1]))
        else:
            win.blit(PlayerSprite.still[self.facing], self.v_center)
    @property
    def xp_yp(self):
        return self.cords[1] - self.v_center[1], self.cords[0] - self.v_center[0]

    @property
    def corners(self):
        """Returns players corners"""
        return return_corners(self.cords, self.width, self.height)

    def check_obst(self, dist, ):
        """returns the cords of your projected travel"""
        x = self.cords[0]
        y = self.cords[1]
        if self.facing == 'up':
            y -= dist
        elif self.facing == 'down':
            y += dist
        elif self.facing == 'left':
            x -= dist
        elif self.facing == 'right':
            x += dist
        return x, y

    def cast_rod(self):
        """Casts your fishing rod"""
        rod_cast_sound.play()
        new_box = copy.copy(self.rect)
        new_box.topleft = self.check_obst(self.cast_length)
        if self.facing == 'up':
            check = new_box.midtop[0], new_box.midtop[1]-10*map_mod.scale
        elif self.facing == 'down':
            check = new_box.midbottom[0], new_box.midbottom[1]+10*map_mod.scale
        elif self.facing == 'left':
            check = new_box.midleft[0]-10*map_mod.scale, new_box.midleft[1]
        elif self.facing == 'right':
            check = new_box.midright[0]+10*map_mod.scale, new_box.midright[1]
        else:
            logging.warning('player does not have a direction')
            return 'player has no position'
        try:
            if '1' in map_mod.return_grids((check, check), game_map): # checks to make sure the rod is going into water
                self.hook_cords = check # sets hook cords for fish collisions
        except IndexError:
            logging.warning('Player attempted to fish outside of game') # add some numerous comments for trying to do this in game

    def update_can_move(self):
        if self.text_cur or self.fish_hold or self.hook_cords:
            self.can_move = False
        else:
            self.can_move = True

    def stop_fishing(self):
        Fish.fish_caught = False
        Fish.fish_took = False
        self.hook_cords = False
        self.fish_hold = False

    def sprint_toggle(self):
        if self.speed == 5:
            self.speed = 20
        elif self.speed == 20:
            self.speed = 5

    def update(self):
        self.rect.topleft = self.cords
        self.rect.height = self.height
        self.rect.width = self.width

    def inspect(self):
        if self.rect.colliderect(old_man.box):
            old_man.talk(cur_quest, player)
            return
        if player.text_cur:
            player.text_cur = False

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

class Balance:
    def __init__(self, bal, game_long_balance):
        self.image = load_asset('coin_counter.png')
        self.f_cords = (reso_p.win_length-73*UI_scale, 34*UI_scale)
        self.color = (0, 0, 0)
        self.cords = (reso_p.win_length-110*UI_scale, 32*UI_scale)
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
        self.image = pygame.transform.scale(self.image, (100*UI_scale, 50*UI_scale))
        self.font = pygame.font.SysFont('Comic Sans MS', 30*UI_scale)

balance = Balance(0, 0)

player = PlayerSprite()
player_tracker = StatTracker(player)
spritelist.add(player)

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
    text_box = pygame.transform.scale(text_box, (510*UI_scale, 70*UI_scale))
    textbox_font = pygame.font.SysFont('Comic Sans MS', 20*UI_scale)
    inventory.Inventory.rescale()
    balance.rescale()

def rescale_game():
    rescale_ui()
    for sprite in spritelist.sprites():
        if not isinstance(sprite, PlayerSprite):
            sprite.rescale()
    for sprite in Decor.LowDecor.decor_sprites.sprites():
        sprite.rescale()
    player.rescale_player()

def generate_surface():
    pss = player.xp_yp
    return map_mod.create_surface(game_map, pss[0], pss[1])

def draw_notifications():
    if cur_quest.mode == 'start':
        cur_quest.start(timer,  player_tracker.fish_caught)
    elif cur_quest.mode == 'finish':
        cur_quest.finish(timer)
    elif not cur_quest.mode:
        ''

def draw_ui():
    balance.draw()
    inventory.inventory.draw(pos)
    small_font = pygame.font.SysFont('Comic Sans MS', 10)
    if player.text_cur: # draws sprite inspection dialog
        win.blit(text_box, ((reso_p.win_length-510*UI_scale)/2, reso_p.win_height-80*UI_scale))
        win.blit(textbox_font.render(str(player.text_cur), False, (0, 0, 0)), ((reso_p.win_length-475*UI_scale)/2, reso_p.win_height-65*UI_scale))
    pos_p = (pos[0] + xp, pos[1] + yp)
    win.blit(small_font.render(str(pos_p), False, (0, 0, 0)), (700, 10))  # shows cursor cords
    cur_quest.draw(UI_scale)

def dynamic_drawing():
    """Draws inputted sprites in order of how high their Y cord is for example y=5 is drawn over y=4"""
    s_list = [] # becomes list of sprites to draw in order
    spritelist_copy = spritelist.sprites().copy() # initial list of sprites
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
    return map_mod.return_grids(corners, game_map)

def check_walkable(noclip, dist):
    if noclip:
        return True
    if '1' in grid_ahead(player.check_obst(dist), player.height, player.width):
        return False
    if '3' in grid_ahead(player.check_obst(dist), player.height, player.width):
        return False
    return True

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
Fish.update_fish(player.hook_cords)
while True:
    walking_sound.set_volume(real_menu_handler.sound/100)
    rod_pull_sound.set_volume(real_menu_handler.sound/100)
    rod_cast_sound.set_volume(real_menu_handler.sound/100)
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
        FishSpawner.spawn_all(grid_ahead, inventory, spritelist)

    #update fish then map
    hooked_fsh = Fish.update_fish(player.hook_cords) # checks to see if a fish is on the hook.
    Fish.rescale()
    player.update()
    for decorr in Decor.HighDecor.decor_sprites.sprites():
        decorr.update()
    player.walking = False
    Fish.fish_moving(timer, inventory, player, game_state, grid_ahead)
    #keyholds
    #event handler
    if game_state == 'main':
        keys = pygame.key.get_pressed()
        handle_key_holds()

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
                        player.stop_fishing()
                    player.cast_length = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                        player.inspect()
                if event.key == pygame.K_ESCAPE:
                    if player.text_cur:
                        player.text_cur = False
                    else:
                        real_menu_handler.run_menu()
                if event.key == pygame.K_q:
                    player.sprint_toggle()
                if event.key == pygame.K_SPACE:
                    handle_rod()
                if event.key == pygame.K_F11:
                    game_state = 'minigame'
            inv = inventory.inventory
            if event.type == pygame.MOUSEBUTTONDOWN:
                grab_pos() # prints cursor location useful for debugging
                if event.button == 1:
                    if pos[1] > inv.active[0] and inv.active[1] or inv.grabbed: # checks if you are withing the inventories cords to avoid pointless and relatively expensive checks
                        inv.click(pos)
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if pos[1] > inv.active[0] and inv.active[1] or inv.grabbed:
                        inv.release(pos, grab_pos(), player, balance, player_tracker)
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
            player.stop_fishing()
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

