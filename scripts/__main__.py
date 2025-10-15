#!/usr/bin/env python3
 
import pygame
from typing import override
from core.colors import *
from core.debug import Debug
from tiles import *
from enemies import *
from core.gui_object import *
from texts import *
from pygame.locals import *
from pygame import mixer
from core.image import load_image
from core.application import Application
from core.camera import Camera
class Game(Application):
	def __init__(self):
		super().__init__((1440, 900), "TOWER DEFENSE", 165)
		self.start_money = 10000
		self.start_live = 10
		self.level = 1
		self.tab = "main_menu"	
		self.camera = Camera(Rect((0, 0), self.size))
		
		self.objects = {
			"menu": {
				"background"   : GUI_Object(self.size, (0,0)         , self.size  , "others/bg"),
				"logo"         : GUI_Object(self.size, ("CENTER", 50), (868, 140) , "others/logo"),
			},
			"main_menu": {
				"play"         : GUI_Object(self.size, ("CENTER", 250), (802, 82) , "button/play"      , "button/play2"),
				"contact"      : GUI_Object(self.size, ("CENTER", 350), (800, 80) , "button/contact_us", "button/contact_us2"),
				"exit"         : GUI_Object(self.size, ("CENTER", 450), (802, 82) , "button/exit"      , "button/exit2")
			},
			"contact": {
				"social_media" : GUI_Object(self.size, ("CENTER", 200), (600, 600), "others/social_media"),
				"back"         : GUI_Object(self.size, (70, 700)      , (299, 84) , "button/goBack"   , "button/goBack2")
			},
			"game": {

			}
		}

		self.game_background       = GUI_Object(self.size, (0,0), self.size, "others/gray_bg", None, ".jpg")

		self.buy_tower_buttons     = [
			GUI_Object(self.size, (1160, 255), (128, 128), "towers/buy_tower1"),
			GUI_Object(self.size, (1300, 260), (128, 128), "towers/buy_tower2"),
			GUI_Object(self.size, (1160, 440), (128, 128), "towers/buy_tower3"),
			GUI_Object(self.size, (1300, 440), (128, 128), "towers/buy_tower4")
		]

		self.start_pause_button    = GUI_Object(self.size, (1230, 650), (64, 64), "button/start")
		self.x2_button             = GUI_Object(self.size, (1310, 650), (64, 64), "button/2x")
		self.upgrade_planes_button = GUI_Object(self.size, (1160, 730), (270, 70), "button/upgrade_planes2", "button/upgrade_planes")
		self.menu_button           = GUI_Object(self.size, (1160, 820), (270, 70), "button/menu2", "button/menu")
		self.pause_music_button    = GUI_Object(self.size, (20, 20), (64, 64), "button/pauseMusic")
		self.resume_music_button   = GUI_Object(self.size, (20, 20), (64, 64), "button/resumeMusic")
		self.live_image            = GUI_Object(self.size, (1245, 210), (40, 40), "others/heart")
		self.live_texts            = [GUI_Object(self.size, (1275, 195), (64, 64), "numbers/" + str(i)) for i in range(self.start_live - 1)]
		self.live_text0            = GUI_Object(self.size, (1305, 195), (64, 64), "numbers/0")
		self.money_box             = GUI_Object(self.size, (self.width - 296, 72), (300, 125), "others/button")

		#-# Game Settings #-#
		self.speed = 1
		self.is_game_started = False
		self.map = map
		self.money = self.start_money
		self.live = self.start_live
		self.cursor_col = None
		self.cursor_row = None
		self.buying_tower_type = 0
		self.first_col = None
		self.first_row = None
		self.enemy_count_created_this_level = 0

		#-# Fonts #-#
		self.font = pygame.font.SysFont("ComicSansMs", 40)
		self.dollar_text_font = pygame.font.SysFont("ComicSansMs", 30)
		self.fee_text_font = pygame.font.SysFont("ComicSansMs", 20)

		#-# Tower Features #-#
		self.towers: list[Tower] = []
		self.selected_tower = None
		self.plane_level = 1
		self.tower_sell_prices = [[70], [350, 1000, 1750], [500, 1250], [700, 1600]]
		self.tower_prices      = [[100], [500, 750, 1000], [700, 1000], [1000, 1200]]
		self.tower_max_levels  = [1, 3, 2, 2]
		self.tower_ranges      = [[150], [110, 130, 150], [90, 110], [35, 35]]
		self.tower_damages     = [[20], [40, 50, 70], [80, 120], [100, 200]]
		self.tower_speeds      = [[1000], [2000, 3000, 4000], [5000, 7000], [4, 2]]
		self.bullet_speed      = []
		self.tower_fee_text_positions = [(self.width - 240, 380), (self.width - 97, 380), (self.width - 240, 590), (self.width - 105, 590)]

		#-# Enemy Features #-#
		self.enemies: list[Enemy] = []
		self.health: list[int] = []
		self.enemy_damage: list[int] = []
		self.mov_speed: list[int] = []
		self.start_time_enemy_created: int = 0
		self.enemy_count_created_all_time: int = 0

		#-# Tiles #-#
		self.block = load_image("tiles/block")
		self.enable = load_image("tiles/enable")

		#-# Texts #-#
		self.money_text  = Text(str(self.money), self.font, Green, (self.width - 255, 104))
		self.level_text  = Text("Level " + str(self.level), self.font, White, (self.width - 215, 2))
		self.dollar_text = Text("$", self.dollar_text_font, Green, (self.width - 60, 110))

		self.create_fee_texts()
		self.check_purchasing_power()

		self.fee_text_background = scale_surface(self.money_box.images[GUI_Object.STATE.NORMAL].image, (100, 50))
		self.tower_images = [load_image("towers/tower1L1"),
							load_image("towers/tower2L1"),
							load_image("towers/tower3L1"),
							load_image("towers/tower4L1"),
							load_image("towers/tower4L2")]

		self.is_music_paused = False
		
		self.IS_MUSIC_ENDED = pygame.USEREVENT
		mixer.music.set_endevent(self.IS_MUSIC_ENDED)
		self.start_music()

	def run(self):
		self.create_tiles()
		self.get_first_tile()
		super().run()

	def create_tiles(self):
		self.tiles: list[Tile] = []
		row_number = -1
		for row in self.map:
			row_number += 1
			col_number = -1
			for tile_type in row:	
				col_number += 1
				tile = Tile(tile_type, col_number, row_number, self)	
				self.tiles.append(tile)

	def get_first_tile(self):
		for tile in self.tiles:
			self.first_row, self.first_col = tile.get_first_tile()
			if self.first_row != None and self.first_col != None:
				break

	@override
	def handle_events(self, event):
		super().handle_events(event)

		for obj in self.objects[self.tab].values():
			obj.update(self.mouse.pos)

		if self.tab == "main_menu":
			if self.objects["main_menu"]["play"].is_clicked(event, self.mouse.pos):
				self.tab = "game"
			elif self.objects["main_menu"]["contact"].is_clicked(event, self.mouse.pos):
				self.tab = "contact"
			elif self.objects["main_menu"]["exit"].is_clicked(event, self.mouse.pos):
				self.on_exit()

			if event.type == pygame.MOUSEBUTTONUP:
				if self.is_music_paused and self.resume_music_button.is_clicked(event, self.mouse.pos):
					self.resume_music()
				elif self.pause_music_button.is_clicked(event, self.mouse.pos):
					self.pause_music()

			if event.type == self.IS_MUSIC_ENDED: # Music loop
				self.start_music()

		elif self.tab == "contactUs":
			if self.go_back_button.is_clicked(event, self.mouse.pos):	
				self.tab = "main_menu"
				
		elif self.tab == "game":
			self.camera.update_with_mouse(self.mouse.pos)

			if self.mouse.pos[0] < 1152:
				self.cursor_col = self.mouse.pos[0]//64
				self.cursor_row = self.mouse.pos[1]//64
	
			#-# Button Control #-#
			if self.menu_button.is_clicked(event, self.mouse.pos):	
				self.tab = "main_menu"
				self.GameStarted = False
				
			elif event.type == pygame.MOUSEBUTTONUP:
				
				#-# Choose Selected Tower #-#
				for tower in self.towers:
					if self.selected_tower == tower:
						tower.sell(self.mouse.pos, self)
						tower.upgrade(self.mouse.pos, self)

				#-# Selecting A Tower #-#
				if self.buying_tower_type == 0:
					is_clicked_to_a_tower = False
					for tower in self.towers:
						if self.cursor_col == tower.col and self.cursor_row == tower.row:
							is_clicked_to_a_tower = True
							if self.selected_tower != None and self.selected_tower == tower:
								self.selected_tower = None	
							else:		
								self.selected_tower = tower
					if not is_clicked_to_a_tower:
						self.selected_tower = None

					#-# Building a Tower #-#
				if self.mouse.pos[0] <= 1152:
					if self.buying_tower_type and not (self.cursor_row, self.cursor_col) in self.block_tiles:
						tower = Tower(self.buying_tower_type, self.cursor_row, self.cursor_col, self)   
						if tower.type == 4:	
							self.towers.append(tower)
						else:												
							self.towers.insert(0, tower)
						self.decrease_money(self.tower_sell_prices[tower.type - 1][0])
						self.buying_tower_type = 0

			#-# Upgrade planes button #-#
			if self.upgrade_planes_button.is_clicked(event, self.mouse.pos) and self.money >= 5000 and self.plane_level == 1:
				self.decrease_money(5000)
				self.buy_tower_buttons[3] = GUI_Object(self.size, (1300, 440), (128, 128), "towers/tower4L2")
				self.plane_level = 2

			#-# Start-Pause Button #-#
			if self.start_pause_button.is_clicked(event, self.mouse.pos):
				if self.start_pause_button.image_path == ("button", "start"):
					self.is_game_started = True
					self.start_pause_button.image_path = ("button", "pause")
				else:
					self.is_game_started = False
					self.start_pause_button.image_path = ("button", "start")

			#-# x2 Button #-#
			if self.x2_button.is_clicked(event, self.mouse.pos):
				if self.x2_button.image_path == ("button", "2x"):
					self.x2_button.image_path = ("button", "2x2")
				else:
					self.x2_button.image_path = ("button", "2x")

			#-# Buy Tower #-#
			for i, buy_tower_button in enumerate(self.buy_tower_buttons):
				if buy_tower_button.is_clicked(event, self.mouse.pos):
					if self.buying_tower_type == i + 1:
						self.buying_tower_type = 0
					else:
						self.buying_tower_type = i + 1

	def start_music(self):
		mixer.music.load("sounds/bg.mp3")
		mixer.music.play()

	def resume_music(self):
		mixer.music.unpause()
		self.is_music_paused = False
		
	def pause_music(self):
		mixer.music.pause()
		self.is_music_paused = True
	
	def draw_music_button(self):
		def get_music_button():
			return self.resume_music_button if self.is_music_paused else self.pause_music_button

		get_music_button().draw(self.window)

	def start_next_level(self):
		self.level += 1
		self.level_text.set("Level " + str(self.level))
		self.level_finish_time = None
		self.enemy_count_created_this_level = 0

	#-# Create Tower Fee Texts #-#
	def create_fee_texts(self):
		self.fee_texts = []
		for i in range(len(self.tower_sell_prices)):
			fee_text = Text(str(self.tower_sell_prices[i][0]) + " $", self.fee_text_font, Green, self.tower_fee_text_positions[i])
			self.fee_texts.append(fee_text)

	#-# Change color of tower fee texts to red which we cant buy it #-#
	def check_purchasing_power(self):
		for i in range(len(self.tower_sell_prices)):
			if self.money >= self.tower_sell_prices[i][0]:
				self.fee_texts[i].set_color(Green)
			else:
				self.fee_texts[i].set_color(Red)

		if self.money_text.color != Green and self.money != 0:
			self.money_text.set_color(Green)
			self.dollar_text.set_color(Green)

		if self.money == 0:
			self.money_text.set_color(Red)
			self.dollar_text.set_color(Red)

	def increase_money(self, additive):
		self.money += additive
		self.money_text.set(str(self.money))
		self.check_purchasing_power()

	def decrease_money(self, subtrahend):
		self.money -= subtrahend
		self.money_text.set(str(self.money))
		self.check_purchasing_power()

	@override
	def draw(self):
			
		if self.tab == "main_menu":
			for obj in self.objects["menu"].values():
				obj.draw(self.window)
			for obj in self.objects["main_menu"].values():
				obj.draw(self.window)
			self.draw_music_button()

		elif self.tab == "contactUs":
			for obj in self.objects["menu"].values():
				obj.draw(self.window)
			for obj in self.objects["contact"].values():
				obj.draw(self.window)
			self.draw_music_button()

		elif self.tab == "game":
			self.draw_game_background()
			self.draw_tiles()
			self.draw_towers()
			self.draw_enemies()
			self.draw_game_borders()
			self.draw_game_objects()

			#-# Choosing Blocked Tiles #-#
			if self.is_buying_tower():
				self.draw_buying_tower()

	def draw_game_background(self):
		self.game_background.draw(self.window)

	def draw_tiles(self):
		for tile in self.tiles:
			tile.draw(self.window, self)

	def draw_game_borders(self):
		#-# col Lines #-#
		pygame.draw.line(self.window, White, (1, 0), (1, 1440), 4)
		pygame.draw.line(self.window, White, (1151, 0), (1151, 900), 4)
		pygame.draw.line(self.window, White, (1437, 0), (1437, 900), 4)

		#-# row Lines #-#
		pygame.draw.line(self.window, White, (0, 1), (1440, 1), 4)
		pygame.draw.line(self.window, White, (1150, 65), (1440, 65), 4)
		pygame.draw.line(self.window, White, (1150, 200), (1440, 200), 4)
		pygame.draw.line(self.window, White, (1150, 255), (1438, 255), 4)
		pygame.draw.line(self.window, White, (1150, 640), (1440, 640), 4)
		pygame.draw.line(self.window, White, (1150, 720), (1440, 720), 4)
		pygame.draw.line(self.window, White, (1150, 810), (1440, 810), 4)
		pygame.draw.line(self.window, White, (0, 897), (1440, 897), 4)

	def draw_enemies(self):
		if self.is_game_started == True:
			
			#-# Create Enemies #-#
			enemy_count_will_created_this_level = self.level * 10

			if self.enemy_count_created_this_level < enemy_count_will_created_this_level:
				if self.enemy_count_created_this_level == enemy_count_will_created_this_level - 1:
					self.level_finish_time = pygame.time.get_ticks()
				if pygame.time.get_ticks() - self.start_time_enemy_created > 1000:
					self.enemy_count_created_this_level += 1
					self.enemy_count_created_all_time += 1
					self.enemies.append(Enemy(self.enemy_count_created_all_time, self.level, (self.first_row*64) - 32, self.first_col*64))
					self.start_time_enemy_created = pygame.time.get_ticks()
			elif self.level_finish_time and pygame.time.get_ticks() - self.level_finish_time > 5000:
				self.start_next_level()
			
			#-# Draw and Delete Enemies #-#
			for enemy in self.enemies:
				enemy.Walking = True 
				if enemy.pos.x >= self.width - 32:
					self.enemies.remove(enemy)
					if self.live >= enemy.damage:
						self.live -= enemy.damage
					else:
						self.live = 0
						#-# Game Over #-#
						self.exit()

				else:
					enemy.move(self.map, self.speed)
					enemy.draw(self.window)
		
		#-# Stop Enemies When Game Paused #-#
		elif not self.is_game_started and self.enemies:
			for enemy in self.enemies:
				enemy.draw(self.window)
				enemy.Walking = False

	def draw_towers(self):

		self.tower_positions = []
		for tower in self.towers:

			#-# Remove Planes #-#
			if tower.type == 4:
				if tower.pos.x > 1125:
					self.towers.remove(tower)

			tower.update_and_draw(self)

			#-# Draw Bullets #-#
			if tower.type != 4:
				self.tower_positions.append((tower.row, tower.col))

				for bullet in tower.bullets:
					if self.is_game_started:
						bullet.update(self)

					bullet.draw(self.window)

	def draw_game_objects(self):

		#-# Draw Objects #-#
		self.start_pause_button.draw(self.window)
		self.x2_button.draw(self.window)
		
		for buy_tower in self.buy_tower_buttons:
			buy_tower.draw(self.window)

		self.live_image.draw(self.window)
		self.live_texts[self.live if self.live != 10 else 1].draw(self.window)
		if self.live == 10:
			self.live_text0.draw(self.window)
		self.upgrade_planes_button.draw(self.window)
		self.menu_button.draw(self.window)

		#-# Texts #-#
		self.level_text.draw(self.window)
		self.money_box.draw(self.window)
		self.money_text.draw(self.window)
		self.dollar_text.draw(self.window)
		self.window.blit(self.fee_text_background, (self.width - 265, 370))
		self.window.blit(self.fee_text_background, (self.width - 125, 370))
		self.window.blit(self.fee_text_background, (self.width - 265, 580))
		self.window.blit(self.fee_text_background, (self.width - 125, 580))
		self.draw_fee_texts()

	def draw_fee_texts(self):
		for fee_text in self.fee_texts:
			fee_text.draw(self.window)

	def is_buying_tower(self):
		return self.buying_tower_type != 0

	def draw_buying_tower(self):
		self.block_tiles = []
		row_number = 0
		for row in self.map:
			row_number += 1
			col_number = 0
			for tile in row:
				col_number += 1
				if ((tile == "0" or tile == "3") and not((row_number - 1, col_number - 1) in self.tower_positions)) or self.buying_tower_type == 4:
					self.window.blit(self.enable, (64*(col_number - 1), 64*(row_number - 1)))
				else:
					self.window.blit(self.block, (64*(col_number - 1), 64*(row_number - 1)))
					self.block_tiles.append((row_number - 1, col_number - 1))

		#-# Drawing Buyyed Tower To Mouse Position
		index = self.buying_tower_type if self.buying_tower_type == 4 and self.plane_level == 2 else self.buying_tower_type - 1
		if self.mouse.pos[0] >= 1152:
			self.window.blit(self.tower_images[index], (self.mouse.pos[0] - 32, self.mouse.pos[1] - 32))
		else:
			#-# Show where you can build the tower #-#
			self.window.blit(self.tower_images[index], (self.cursor_col*64, self.cursor_row*64))

			#-# Draw Range of Tower #-#
			range = self.tower_ranges[self.buying_tower_type - 1][0]
			self.surface = pygame.Surface((range*2, range*2), pygame.SRCALPHA, 32)
			pygame.draw.circle(self.surface, (128, 128, 128, 120), (range, range), range, 0)
			if (self.cursor_row, self.cursor_col) in self.block_tiles:
				pygame.draw.circle(self.surface, (255, 0, 0, 120), (range, range), range, 5)
			else:				
				pygame.draw.circle(self.surface, (0, 200, 0, 120), (range, range), range, 5)
			self.window.blit(self.surface, ((self.cursor_col*64) + 32 - range, ((self.cursor_row*64) + 32 - range)))			

	@override
	def draw_debug(self):
		if not self.is_in_debug_mode:
			return
		
		debug_info = [
			self.mouse.get_info(),
			self.camera.get_info(),
			self.objects["main_menu"]["play"].get_info(),
		]
		DEBUG_FONT = pygame.font.SysFont("Consolas", 20)
		Debug.draw(self.window, DEBUG_FONT, debug_info)

	@override
	def on_exit(self):
		if self.tab == "main_menu":
			self.exit()
		elif self.tab == "contactUs":
			self.tab = "main_menu"
		elif self.tab == "game":
			self.tab = "main_menu"
			self.is_game_started = False

if (__name__ == "__main__"): # CHECK FOR NOT EXPORTING
	game = Game()
	game.run()
