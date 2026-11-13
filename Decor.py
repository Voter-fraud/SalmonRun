import pygame
from setup import map_mod
from setup.reso_p import win
from toolbox import load_asset, from_saves

class Decor(pygame.sprite.Sprite):
    decor_sprites = pygame.sprite.Group()
    @classmethod
    def create_sprite(cls, image=False, length=False, width=False, name=False, high_low="High", cords=(0, 0), preset=""):
        if not preset:
            ret = cls(image, length, width, name, high_low, cords)
        else:
            print(str(preset)+"PRESET")
            ret = cls(*decor_presets[preset], cords=cords)
        ret.rescale()
        cls.decor_sprites.add(ret)
        return ret

    def __init__(self, image, length, width, name, high_low:str, cords):
        super().__init__()
        self.image = image
        self.original = int(cords[0]), int(cords[1])
        self.cords = int(cords[0]) * map_mod.scale, int(cords[1]) * map_mod.scale
        self.length = int(length)
        self.width = int(width)
        self.rect = self.image.get_rect(topleft=self.cords)
        self.decor = high_low+'Decor' #if the decoration has position based rendering
        self.name = name

    def update(self):
        self.rect = self.image.get_rect(topleft=self.cords)

    def draw(self, xp, yp):
        win.blit(self.image, (self.cords[0]-xp, self.cords[1]-yp))

    def rescale(self):
        self.image = pygame.transform.scale(self.image, (self.length * map_mod.scale, self.width * map_mod.scale))



decor_imgs = {
    'fern': load_asset('fern.png', 'foliage'),
    'weird_bush': load_asset('weird_bush.png', 'foliage'),
    'bad_bush': load_asset('bad_bush.png', 'foliage'),
    'market': load_asset('market.png'),
    'duck': load_asset('duck.png'),
    'corgi': '',
}

decor_presets = {
    'fern': (decor_imgs['fern'], 32, 32, 'fern', "Low"),
    'weird_bush': (decor_imgs['weird_bush'], 32, 32, 'weird_bush', "High"),
    'bad_bush': (decor_imgs['bad_bush'], 32, 32, 'bad_bush', "High"),
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
            Decor.create_sprite(decor_imgs[decor[1]], decor[4], decor[5], decor[1], "Low", (decor[2], decor[3]))
        if decor[0] == 'HighDecor':
            Decor.create_sprite(decor_imgs[decor[1]], decor[4], decor[5], decor[1], "High", (decor[2], decor[3]))
    return formatted_list

def store_decor(doc):
    file = open(doc, 'w')
    file.truncate(0)
    for decor in Decor.decor_sprites.sprites():
        file.write(F'HighDecor,{decor.name},{decor.original[0]},{decor.original[1]},{decor.length},{decor.width}\r')
    for decor in Decor.decor_sprites.sprites():
        file.write(F'LowDecor,{decor.name},{decor.original[0]},{decor.original[1]},{decor.length},{decor.width}\r')
    file.close()

def init_decor():
    format_decor(from_saves('Decor positions.txt'))

    
init_decor()