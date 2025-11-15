import pygame
import os

# initialising programs
pygame.init()
pygame.mixer.init()
pygame.font.init()
# display window setup
win = pygame.display.set_mode((1000, 600))
pygame.display.set_caption('Gamble core')
# global variables
clock = pygame.time.Clock()
my_font = pygame.font.SysFont('Comic Sans MS', 30)  # this is only one font size
money_amount = 100
soundstate = True
bet_amount = 10
game_state = 'main_menu'
# loading in game assets
menu1 = pygame.image.load(os.path.join('menu-frames', 'menu1.png'))
menu2 = pygame.image.load(os.path.join('menu-frames', 'menus.png'))


class Menu:
	@classmethod
	def create_button(cls):
		''

	def __init__(self, button_names_and_num, img_files_and_num, location):
		self.framelist = img_files_and_num  # button ID then its unselected frame, then selected frame
		self.buttons = button_names_and_num  # button ID then its name
		self.location = location  # button ID then its coordinates
		self.select = 1  # button currently selected

	class TransferButton:
		''

	class ToggleButton:
		''

	class Slider:
		''


	def draw(self):
		'''For each button if it is selected we draw its selected frame and draw all others normally'''
		win.fill((0, 0, 0))  # screen background
		for key, value in self.buttons.items():
			x = self.location[key][0]
			y = self.location[key][1]
			if key == str(self.select):
				win.blit((self.framelist[key][1]), (x, y))
				win.blit(my_font.render(self.buttons[key], False, (0, 0, 0)), (x, y))
			else:  # font renders each time independently which is moderately inefficient
				win.blit((self.framelist[key][0]), (x, y))
				win.blit(my_font.render(self.buttons[key], False, (0, 0, 0)), (x, y))
		pygame.display.update()

	# could add
	def handle_menu_nav(self, event):
		'''Lets you linearly navigate through menus with up or down keys.'''
		if event.key == pygame.K_UP:  # could make the numbers matrices, so you can move selected from side to side too.
			if main_menu.select > 1:
				main_menu.select -= 1
		elif event.key == pygame.K_DOWN:
			if main_menu.select < len(main_menu.buttons):
				main_menu.select += 1


main_menu = Menu({'1': 'Resume', '2': 'options'},
				{'1': (menu1, menu2), '2': (menu1, menu2)},
				{'1': (130, 10), '2': (130, 100)})
def main_loop():
	while True:
		clock.tick(30)
		main_menu.draw()
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if game_state == 'main_menu':
					main_menu.handle_menu_nav(event)
					if event.key == pygame.K_RETURN:
						if main_menu.select == 1:
							pygame.mixer.music.load('startsound.mp3')
							pygame.mixer.music.play(1, 0)
						if main_menu.select == 2:
							pygame.mixer.music.load('quitsound.mp3')
							pygame.mixer.music.play(1, 0)
main_loop()