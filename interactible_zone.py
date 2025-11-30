import pygame

"""
I want to make these zones very simple and easy to add mini functions into. 
Since these will be so simple unlike with the menu system we can probably keep the sub functions in here atleast for now
later add speceficity to which game map but currently that is completely unnecessary
"""
def market_func():
    ''

class InteractZone:

    zone_list = {}

    @classmethod
    def create_zone(cls, name, topleft, width, length, interact_func):
        """Creates a new zone object, adds it the class dict, and returns it."""
        new_zone = cls(topleft, width, length, interact_func)
        cls.zone_list[name] = new_zone
        return new_zone


    def __init__(self, topleft, width, length, interact_func):
        self.rect = pygame.rect.Rect(topleft[0], topleft[1], width, length)
        self.run = interact_func

    def check_interaction(self, check_rect):
        if self.rect.colliderect(check_rect):
            self.run()