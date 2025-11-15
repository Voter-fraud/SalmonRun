import pygame, random
from reso_p import win
from map_mod import scale
from config import UI_scale
from toolbox import load_asset
clock = pygame.time.Clock()

# rhythm game shows the player struggling over the fish and pressing 2-4 buttons as they are highlighted as fast as possible to keep a bar from
# falling to low. a fishes difficulty increases the rate at which the bar decays, a set amount of time you have to struggle or
# reaching the far end of the bar can work as game finishes
# fish is slowly reeled in instead of having a overall progress bar

bar_base = load_asset('bar.png', 'minigame')
a_key = load_asset('a_key.png', 'minigame')
s_key = load_asset('s_key.png', 'minigame')
d_key = load_asset( 'd_key.png', 'minigame')
sel = load_asset('sel_key.png', 'minigame')
n_key = load_asset('next_key.png', 'minigame')

bar_base=pygame.transform.scale(bar_base, (80*UI_scale, 20*UI_scale))
sel=pygame.transform.scale(sel, (16*UI_scale, 16*UI_scale))
a_key=pygame.transform.scale(a_key, (16*UI_scale, 16*UI_scale))
s_key=pygame.transform.scale(s_key, (16*UI_scale, 16*UI_scale))
d_key=pygame.transform.scale(d_key, (16*UI_scale, 16*UI_scale))
n_key=pygame.transform.scale(n_key, (16*UI_scale, 16*UI_scale))


class GameBar(pygame.sprite.Sprite):
    def __init__(self, base, color, cords):
        super().__init__()
        self.image = base
        self.color = color
        self.filled = 0.5
        self.decays = 0.0003
        self.cords = cords
        self.rect = self.image.get_rect(topleft=self.cords)

    def draw(self):
        win.blit(self.image, self.cords)
        pygame.draw.rect(win, self.color, (self.cords[0]+2, self.cords[1]+2, self.rect.width*self.filled-4, self.rect.height-4))

    def decay(self):
        self.filled -= self.decays

    def fill(self, amount):
        self.filled += amount
        if self.filled > 1:
            self.filled = 1
        if self.filled < 0:
            self.filled = 0

class OtherBar(pygame.sprite.Sprite):
    key_colors = {
        'a': (0, 0, 0),
        's': (150, 112, 255),
        'd': (130, 130, 130)
    }
    def __init__(self, base, color, cords):
        super().__init__()
        self.image = base
        self.color = color
        self.cords = cords
        #
        self.per_spot = 0.6
        self.perf_rang = 0.15
        #
        self.next_spot = 0.3
        self.next_rang = 0.2
        #
        self.cur_spot = 0.0
        self.move_rate = 0.0035

    @property
    def rect(self):
        ret = self.image.get_rect(topleft=self.cords)
        return ret

    @property
    def perf_rect(self):
        return pygame.rect.Rect(self.cords[0]+self.rect.width*self.per_spot, self.cords[1], self.perf_rang*self.rect.width, self.rect.height)

    @property
    def can_click(self):
        if self.perf_rect.collidepoint(self.cords[0]+self.rect.width*self.cur_spot, self.cords[1]+3):
            return True

    def new_run(self):
        x = random.randrange(20, 75)
        i = random.randrange(10, 25)
        self.cur_spot = 0
        self.per_spot = self.next_spot
        self.perf_rang = self.next_rang
        self.next_spot = x/100
        self.next_rang = i/100

    def tick(self):
        self.cur_spot  += self.move_rate
        if self.cur_spot >= 1:
            self.new_run()
            return True

    def draw(self):
        andrew = self.rect.width*self.per_spot
        mirasae = self.rect.width*self.next_spot
        dey = self.rect.width*self.cur_spot
        win.blit(self.image, self.cords)
        pygame.draw.rect(win, (255, 100, 0), (self.cords[0] + mirasae, self.cords[1] + 2, self.next_rang * self.rect.width, self.rect.height - 4))
        pygame.draw.rect(win, self.color, (self.cords[0] + andrew, self.cords[1] + 2, self.perf_rang * self.rect.width, self.rect.height - 4))
        pygame.draw.rect(win, OtherBar.key_colors[cur_key], (self.cords[0]+dey, self.cords[1]-3, 2, self.rect.height+6))



def random_key():
    x = random.randrange(0, 3)
    keys = ['a', 's', 'd']
    return keys[x]

def key_ref(inp, cords):
    if inp == 'a':
        return cords[0]-20, cords[1]-50
    elif inp == 's':
        return cords[0], cords[1]-50
    elif inp == 'd':
        return cords[0]+20, cords[1]-50

def draw_keys(cords):
    win.blit(a_key, (cords[0]-20, cords[1]-50))
    win.blit(s_key, (cords[0], cords[1]-50))
    win.blit(d_key, (cords[0]+20, cords[1]-50))
    win.blit(n_key, key_ref(next_key, cords))
    win.blit(sel, key_ref(cur_key, cords))

cur_key = 'a'
next_key = 's'

bar = GameBar(bar_base, (255, 0, 0), (10, 10))
hit_bar = OtherBar(bar_base, (0, 255, 0), (120, 10))

key_timer = 0
timer = 0

def hit():
    global cur_key, next_key, key_timer
    if hit_bar.can_click:
        bar.fill(0.15)
        cur_key = next_key
        next_key = random_key()
        key_timer = 0
        hit_bar.new_run()
    else:
        bar.fill(-0.005)

def reset():
    global cur_key, next_key, key_timer
    bar.filled = 0.5
    cur_key = next_key
    next_key = random_key()
    key_timer = 0
    hit_bar.new_run()

def run(cords):
    hit_bar.cords = cords[0]-hit_bar.rect.width/3, cords[1]-hit_bar.rect.height-5
    global timer, key_timer, next_key, cur_key
    if hit_bar.can_click:
        print('can')
    timer += 1
    key_timer+=1
    if timer  >= 99999:
        timer = 0
    bar.decay()
    if hit_bar.tick():
        cur_key = next_key
        next_key = random_key()
        key_timer = 0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                if cur_key == 'a':
                    hit()
                else:
                    bar.fill(-0.01)
            elif event.key == pygame.K_s:
                if cur_key == 's':
                    hit()
                else:
                    bar.fill(-0.01)
            elif event.key == pygame.K_d:
                if cur_key == 'd':
                    hit()
                else:
                    bar.fill(-0.01)
    bar.draw()
    hit_bar.draw()
    draw_keys(cords)
    if bar.filled <= 0:
        return 'failure'
    elif bar.filled >= 1:
        return 'success'
    return(True)
