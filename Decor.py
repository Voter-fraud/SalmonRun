import map_mod, pygame, os
from reso_p import win
from toolbox import load_asset

class HighDecor(pygame.sprite.Sprite):
    decor_sprites = pygame.sprite.Group()
    @classmethod
    def create_sprite(cls, image, cords, length, width, name):
        ret = cls(image, cords, length, width, name)
        ret.rescale()
        cls.decor_sprites.add(ret)
        return ret

    def __init__(self, image, cords, length, width, name):
        super().__init__()
        self.image = image
        self.original = int(cords[0]), int(cords[1])
        self.cords = int(cords[0])*map_mod.scale, int(cords[1])*map_mod.scale
        self.length = int(length)
        self.width = int(width)
        self.rect = self.image.get_rect(topleft=self.cords)
        self.decor = 'HighDecor'
        self.name = name

    def update(self):
        self.rect = self.image.get_rect(topleft=self.cords)

    def draw(self, xp, yp):
        win.blit(self.image, (self.cords[0]-xp, self.cords[1]-yp))
    def rescale(self):
        self.image = pygame.transform.scale(self.image, (self.length*map_mod.scale, self.width*map_mod.scale))

class LowDecor(pygame.sprite.Sprite):
    decor_sprites = pygame.sprite.Group()
    @classmethod
    def create_sprite(cls, image, cords, length, width, name):
        ret = cls(image, cords, length, width, name)
        ret.rescale()
        cls.decor_sprites.add(ret)
        return ret

    def __init__(self, image, cords, length, width, name):
        super().__init__()
        self.image = image
        self.original = int(cords[0]), int(cords[1])
        self.cords = int(cords[0])*map_mod.scale, int(cords[1])*map_mod.scale
        self.length = int(length)
        self.width = int(width)
        self.rect = self.image.get_rect(topleft=self.cords)
        self.decor = 'LowDecor'
        self.name = name

    def update(self):
        self.rect = self.image.get_rect(topleft=self.cords)

    def draw(self, xp, yp):
        win.blit(self.image, (self.cords[0]-xp, self.cords[1]-yp))

    def rescale(self):
        self.image = pygame.transform.scale(self.image, (self.length*map_mod.scale, self.width*map_mod.scale))


decor_imgs = {
    'fern': load_asset('fern.png', 'foliage'),
    'bush1': load_asset('weird bush2.png', 'foliage'),
    'bush2': load_asset('bad bush.png', 'foliage'),
    'market': load_asset('market.png'),
    'duck': load_asset('duck.png'),
    'corgi': '',
}


def format_decor(doc):
    """Turns a sprite_pos textfile read into a proper list
    see https://youtu.be/R93Uy0dQazE for a full explanation"""
    read = open(doc, 'r').readlines()
    row = []
    for char in read:  # generates a row out of each line
        row.append(char.strip())
    formatted_list = []
    for line in row:  # makes each row a list of individual tiles.
        x = line.split(",")
        formatted_list.append(x)
    for decor in formatted_list:
        if decor[0] == 'LowDecor':
            LowDecor.create_sprite(decor_imgs[decor[1]], (decor[2], decor[3]), decor[4], decor[5], decor[1])
        if decor[0] == 'HighDecor':
            HighDecor.create_sprite(decor_imgs[decor[1]], (decor[2], decor[3]), decor[4], decor[5], decor[1])
    return formatted_list

def store_decor(doc):
    file = open(doc, 'w')
    for decor in HighDecor.decor_sprites.sprites():
        file.write(F'HighDecor,{decor.name},{decor.original[0]},{decor.original[1]},{decor.length},{decor.width}\r')
    for decor in LowDecor.decor_sprites.sprites():
        file.write(F'LowDecor,{decor.name},{decor.original[0]},{decor.original[1]},{decor.length},{decor.width}\r')
    file.close()

def init_decor():
    format_decor('Decor positions.txt')
    
init_decor()