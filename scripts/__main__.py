#!/usr/bin/env python3

#-# IMPORTING PACKAGES #-#
<<<<<<< HEAD
try:
	
	import sys, os, random, time, pygame
	from random import sample
	from colors import *
	from tiles import *
	from enemies import *
	from objects import *
	from window import *
	from texts import *
	from pygame.locals import *
	from pygame import mixer


except ImportError as e:
	print("==> Error ==> "+str(e)+"\n==> You need the install 'pygame' package to use this application.\n==> Use 'sudo apt-get install python3-pip && pip3 install pygame' command to download and install this packages in the terminal.")
	exit()
=======
import sys, pygame
from colors import *
from tiles import *
from enemies import *
from objects import *
from window import *
from texts import *
from pygame.locals import *
from pygame import mixer
from image import load_image
>>>>>>> master

#-# GAME CLASS #-#
class Game(object):
	def __init__(self):

		#-# Window Settings #-#
		self.FPS = 165
<<<<<<< HEAD
		self.windowSize = (self.windowWidth, self.WindowHeight) = (1440, 900)
		self.windowTitle = "TOWER DEFENSE"
		self.startMoney = 10000
		self.startLive = 10
=======
		self.window_size = (self.windowWidth, self.WindowHeight) = (1440, 900)
		self.window_title = "TOWER DEFENSE"
		self.start_money = 10000
		self.start_live = 10
>>>>>>> master
		self.level = 1

		#-# İnitialize Window #-#
		pygame.init()
		mixer.init()
<<<<<<< HEAD
		self.window = Window(self.windowSize, self.windowTitle)
		self.window.OpenWindow()
		self.tab = "menu"	

		#-# Objects #-#
		self.menuBackground = Object(self.windowSize, (0,0), self.windowSize, ("others", "bg"))
		self.gameBackground = Object(self.windowSize, (0,0), self.windowSize, ("others", "gray_bg"), None, ".jpg")	
		self.logo = Object(self.windowSize, ("CENTER", 50), (868, 140), ("others", "logo"))
		self.playButton = Object(self.windowSize, ("CENTER", 250), (802, 82), ("button", "play"), ("button", "play2"))
		self.contactUsButton = Object(self.windowSize, ("CENTER", 350), (800, 80),  ("button", "contact_us"), ("button", "contact_us2"))
		self.exitButton = Object(self.windowSize, ("CENTER", 450), (802, 82), ("button", "exit"), ("button", "exit2"))
		self.goBackButton = Object(self.windowSize, (70, 700), (299, 84), ("button", "goBack"), ("button", "goBack2"))
		self.socialMedia = Object(self.windowSize, ("CENTER", 200), (600, 600), ("others", "social_media"))
		self.buyTower1 = Object(self.windowSize, (1160, 255), (128, 128), ("towers", "buy_tower1"))
		self.buyTower2 = Object(self.windowSize, (1300, 260), (128, 128), ("towers", "buy_tower2"))
		self.buyTower3 = Object(self.windowSize, (1160, 440), (128, 128), ("towers", "buy_tower3"))
		self.buyTower4 = Object(self.windowSize, (1300, 440), (128, 128), ("towers", "buy_tower4"))
		self.startPauseButton = Object(self.windowSize, (1230, 650), (64, 64), ("button", "start"))
		self.x2Button = Object(self.windowSize, (1310, 650), (64, 64), ("button", "2x"))
		self.upgradePlanesButton = Object(self.windowSize, (1160, 730), (270, 70), ("button", "upgrade_planes2"), ("button", "upgrade_planes"))	
		self.menuButton = Object(self.windowSize, (1160, 820), (270, 70), ("button", "menu2"), ("button", "menu"))		
		self.pauseMusicButton = Object(self.windowSize, (20, 20), (64, 64), ("button", "pauseMusic"))		
		self.resumeMusicButton = Object(self.windowSize, (20, 20), (64, 64), ("button", "resumeMusic"))		
		self.liveImage = Object(self.windowSize, (1245, 210), (40, 40), ("others", "heart"))		
		self.liveText = Object(self.windowSize, (1275, 195), (64, 64), ("numbers", "1"))
		self.liveText0 = Object(self.windowSize, (1305, 195), (64, 64), ("numbers", "0"))
		self.moneyBox = Object(self.windowSize, (self.windowWidth - 296, 72), (300, 125), ("others", "button"))

		#-# Game Settings #-#
		self.speed = 1
		self.gameStarted = False
		self.map = map
		self.money = self.startMoney
		self.live = self.startLive
		self.cursorColumn = None
		self.cursorRow = None
		self.buyyingTowerType = 0
		self.run = True
		self.FirstColumn = None
		self.FirstRow = None
		self.enemyCountCreatedThisLevel = 0
		
		#-# Fonts #-#
		self.font = pygame.font.SysFont("ComicSansMs", 40)
		self.dollarTextFont = pygame.font.SysFont("ComicSansMs", 30)
		self.feeTextFont = pygame.font.SysFont("ComicSansMs", 20)

		#-# Tower Features #-#
		self.towers = []
		self.selectedTower = None
		self.planeLevel = 1
		self.towerSellPrices = [[70], [350, 1000, 1750], [500, 1250], [700, 1600]]
		self.towerPrices = [[100], [500, 750, 1000], [700, 1000], [1000, 1200]]
		self.towerMaxLevels = [1, 3, 2, 2]
		self.towerRanges = [[150], [110, 130, 150], [90, 110], [35, 35]]
		self.towerDamages = [[20], [40, 50, 70], [80, 120], [100, 200]]
		self.towerSpeeds = [[1000], [2000, 3000, 4000], [5000, 7000], [4, 2]]
		self.bulletSpeed = []
		self.towerFeeTextPositions = [(self.windowWidth - 240, 380), (self.windowWidth - 97, 380), (self.windowWidth - 240, 590), (self.windowWidth - 105, 590)]

		#-# Enemy Features #-#
		self.enemies = []
		self.health = []
		self.enemyDamage = []
		self.movSpeed = []
		self.startTimeEnemyCreated = 0
		self.enemyCountCreatedAllTime = 0

		#-# Tiles #-#
		self.block = pygame.image.load("images/tiles/block.png").convert_alpha()
		self.enable = pygame.image.load("images/tiles/enable.png").convert_alpha()
		
		#-# Texts #-#
		self.moneyText = Text(str(self.money), self.font, Green, (self.windowWidth - 255, 104))
		self.levelText = Text("Level " + str(self.level), self.font, White, (self.windowWidth - 215, 2))
		self.dollarText = Text("$", self.dollarTextFont, Green, (self.windowWidth - 60, 110))

		self.CreateFeeTexts()
		self.CheckPurchasingPower()
		
		self.BUYTBOX = pygame.transform.scale(self.moneyBox.Image1, (100, 50))
		self.towerImages = [pygame.image.load("images/towers/tower1L1.png").convert_alpha(),
							pygame.image.load("images/towers/tower2L1.png").convert_alpha(),
							pygame.image.load("images/towers/tower3L1.png").convert_alpha(),
							pygame.image.load("images/towers/tower4L1.png").convert_alpha(),
							pygame.image.load("images/towers/tower4L2.png").convert_alpha()]

		self.musicPaused = False
		
		self.MUSIC_ENDED = pygame.USEREVENT
		mixer.music.set_endevent(self.MUSIC_ENDED)
=======
		self.window = Window(self.window_size, self.window_title)
		self.window.open()
		self.tab = "menu"	

		#-# Objects #-#
		self.menu_background = GUI_Object(self.window_size, (0,0), self.window_size, ("others", "bg"))
		self.game_background = GUI_Object(self.window_size, (0,0), self.window_size, ("others", "gray_bg"), None, ".jpg")	
		self.logo = GUI_Object(self.window_size, ("CENTER", 50), (868, 140), ("others", "logo"))
		self.play_button = GUI_Object(self.window_size, ("CENTER", 250), (802, 82), ("button", "play"), ("button", "play2"))
		self.contact_us_button = GUI_Object(self.window_size, ("CENTER", 350), (800, 80),  ("button", "contact_us"), ("button", "contact_us2"))
		self.exit_button = GUI_Object(self.window_size, ("CENTER", 450), (802, 82), ("button", "exit"), ("button", "exit2"))
		self.go_back_button = GUI_Object(self.window_size, (70, 700), (299, 84), ("button", "goBack"), ("button", "goBack2"))
		self.social_media = GUI_Object(self.window_size, ("CENTER", 200), (600, 600), ("others", "social_media"))
		self.buy_tower1 = GUI_Object(self.window_size, (1160, 255), (128, 128), ("towers", "buy_tower1"))
		self.buy_tower2 = GUI_Object(self.window_size, (1300, 260), (128, 128), ("towers", "buy_tower2"))
		self.buy_tower3 = GUI_Object(self.window_size, (1160, 440), (128, 128), ("towers", "buy_tower3"))
		self.buy_tower4 = GUI_Object(self.window_size, (1300, 440), (128, 128), ("towers", "buy_tower4"))
		self.start_pause_button = GUI_Object(self.window_size, (1230, 650), (64, 64), ("button", "start"))
		self.x2_button = GUI_Object(self.window_size, (1310, 650), (64, 64), ("button", "2x"))
		self.upgrade_planes_button = GUI_Object(self.window_size, (1160, 730), (270, 70), ("button", "upgrade_planes2"), ("button", "upgrade_planes"))	
		self.menu_button = GUI_Object(self.window_size, (1160, 820), (270, 70), ("button", "menu2"), ("button", "menu"))		
		self.pause_music_button = GUI_Object(self.window_size, (20, 20), (64, 64), ("button", "pauseMusic"))		
		self.resume_music_button = GUI_Object(self.window_size, (20, 20), (64, 64), ("button", "resumeMusic"))		
		self.live_image = GUI_Object(self.window_size, (1245, 210), (40, 40), ("others", "heart"))		
		self.live_text = GUI_Object(self.window_size, (1275, 195), (64, 64), ("numbers", "1"))
		self.live_text0 = GUI_Object(self.window_size, (1305, 195), (64, 64), ("numbers", "0"))
		self.money_box = GUI_Object(self.window_size, (self.windowWidth - 296, 72), (300, 125), ("others", "button"))

		#-# Game Settings #-#
		self.speed = 1
		self.is_game_started = False
		self.map = map
		self.money = self.start_money
		self.live = self.start_live
		self.cursor_col = None
		self.cursor_row = None
		self.buying_tower_type = 0
		self.run = True
		self.first_col = None
		self.first_row = None
		self.enemy_count_created_this_level = 0

		#-# Fonts #-#
		self.font = pygame.font.SysFont("ComicSansMs", 40)
		self.dollar_text_font = pygame.font.SysFont("ComicSansMs", 30)
		self.fee_text_font = pygame.font.SysFont("ComicSansMs", 20)

		#-# Tower Features #-#
		self.towers = []
		self.selected_tower = None
		self.plane_level = 1
		self.tower_sell_prices = [[70], [350, 1000, 1750], [500, 1250], [700, 1600]]
		self.tower_prices = [[100], [500, 750, 1000], [700, 1000], [1000, 1200]]
		self.tower_max_levels = [1, 3, 2, 2]
		self.tower_ranges = [[150], [110, 130, 150], [90, 110], [35, 35]]
		self.tower_damages = [[20], [40, 50, 70], [80, 120], [100, 200]]
		self.tower_speeds = [[1000], [2000, 3000, 4000], [5000, 7000], [4, 2]]
		self.bullet_speed = []
		self.tower_fee_text_positions = [(self.windowWidth - 240, 380), (self.windowWidth - 97, 380), (self.windowWidth - 240, 590), (self.windowWidth - 105, 590)]

		#-# Enemy Features #-#
		self.enemies: list[Enemy] = []
		self.health: list[int] = []
		self.enemy_damage: list[int] = []
		self.mov_speed: list[int] = []
		self.start_time_enemy_created: int = 0
		self.enemy_count_created_all_time: int = 0

		#-# Tiles #-#
		self.block = load_image("tiles/block.png")
		self.enable = load_image("tiles/enable.png")

		#-# Texts #-#
		self.money_text = Text(str(self.money), self.font, Green, (self.windowWidth - 255, 104))
		self.level_text = Text("Level " + str(self.level), self.font, White, (self.windowWidth - 215, 2))
		self.dollar_text = Text("$", self.dollar_text_font, Green, (self.windowWidth - 60, 110))

		self.create_fee_texts()
		self.check_purchasing_power()

		self.BUY_BOX = pygame.transform.scale(self.money_box.image1, (100, 50))
		self.tower_images = [load_image("towers/tower1L1.png"),
							load_image("towers/tower2L1.png"),
							load_image("towers/tower3L1.png"),
							load_image("towers/tower4L1.png"),
							load_image("towers/tower4L2.png")]

		self.is_music_paused = False
		
		self.IS_MUSIC_ENDED = pygame.USEREVENT
		mixer.music.set_endevent(self.IS_MUSIC_ENDED)
>>>>>>> master
		self.StartMusic()

	def StartMusic(self):
		mixer.music.load("sounds/bg.mp3")
		mixer.music.play()

	def ResumeMusic(self):
		mixer.music.unpause()
<<<<<<< HEAD
		self.musicPaused = False
		
	def PauseMusic(self):
		mixer.music.pause()
		self.musicPaused = True
	
	def DrawMusicButton(self):
		if self.musicPaused:
			self.resumeMusicButton.Draw(self.window, self.mousePosition)
		else:	
			self.pauseMusicButton.Draw(self.window, self.mousePosition)

	#-# Start Next Level #-#
	def StartNextLevel(self):
		self.level += 1
		self.levelText.ChangeText("Level " + str(self.level))
		self.levelFinihTime = None
		self.enemyCountCreatedThisLevel = 0

	#-# Create Tower Fee Texts #-#
	def CreateFeeTexts(self):
		self.feeTexts = []
		for i in range(len(self.towerSellPrices)):
			feeText = Text(str(self.towerSellPrices[i][0]) + " $", self.feeTextFont, Green, self.towerFeeTextPositions[i])
			self.feeTexts.append(feeText)

	#-# Change color of tower fee texts to red which we cant buy it #-#
	def CheckPurchasingPower(self):
		for i in range(len(self.towerSellPrices)):
			if self.money >= self.towerSellPrices[i][0]:
				self.feeTexts[i].ChangeColor(Green)
			else:
				self.feeTexts[i].ChangeColor(Red)
			
		if self.moneyText.color != Green and self.money != 0:
			self.moneyText.ChangeColor(Green)
			self.dollarText.ChangeColor(Green)

		if self.money == 0:
			self.moneyText.ChangeColor(Red)
			self.dollarText.ChangeColor(Red)

	#-# Create Tower Fee Texts #-#
	def DrawFeeTexts(self):
		for feeText in self.feeTexts:
			feeText.Draw(self.window)

	#-# Create Tower Fee Texts #-#
	def IncreaseMoney(self, additive):
		self.money += additive
		self.moneyText.ChangeText(str(self.money))
		self.CheckPurchasingPower()

	#-# Create Tower Fee Texts #-#
	def DecreaseMoney(self, subtrahend):
		self.money -= subtrahend
		self.moneyText.ChangeText(str(self.money))
		self.CheckPurchasingPower()

	#-# SetFPS #-#
	def SetFPS(self):
		clock = pygame.time.Clock()
		clock.tick(self.FPS)

	#-# Get Mouse Position #-#
	def GetmousePosition(self):
		self.mousePosition = pygame.mouse.get_pos()

	#-# Create Tiles #-#
	def CreateTiles(self):
		self.tiles = []
		rowNumber = -1
		for row in self.map:
			rowNumber += 1
			columnNumber = -1
			for tileType in row:	
				columnNumber += 1
				tile = Tile(tileType, columnNumber, rowNumber, self)	
				self.tiles.append(tile)

	#-# Get First Tile #-#
	def GetFirstTile(self):
		for tile in self.tiles:
			self.FirstRow, self.FirstColumn = tile.GetFirstTile()
			if self.FirstRow != None and self.FirstColumn != None:
				break
		
	#-# Draw Menu Bacground #-#
	def DrawMenuBackgorund(self):
		self.menuBackground.Draw(self.window)

	#-# Draw Game Bacground #-#
	def DrawGameBackground(self):
		self.gameBackground.Draw(self.window)

	#-# Draw Tiles #-#
	def DrawTiles(self):
		for tile in self.tiles:
			tile.Draw(self.window)
	
	#-# Draw Game Borders #-#
	def DrawGameBorders(self):
		
		#-# Column Lines #-#
=======
		self.is_music_paused = False
		
	def PauseMusic(self):
		mixer.music.pause()
		self.is_music_paused = True
	
	def draw_music_button(self):
		if self.is_music_paused:
			self.resume_music_button.draw(self.window, self.mouse_pos)
		else:	
			self.pause_music_button.draw(self.window, self.mouse_pos)

	#-# Start Next Level #-#
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

	def draw_fee_texts(self):
		for fee_text in self.fee_texts:
			fee_text.draw(self.window)

	def increase_money(self, additive):
		self.money += additive
		self.money_text.set(str(self.money))
		self.check_purchasing_power()

	def decrease_money(self, subtrahend):
		self.money -= subtrahend
		self.money_text.set(str(self.money))
		self.check_purchasing_power()

	def set_fps(self):
		clock = pygame.time.Clock()
		clock.tick(self.FPS)

	def get_mouse_position(self):
		self.mouse_pos = pygame.mouse.get_pos()

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

	def draw_menu_background(self):
		self.menu_background.draw(self.window)

	def draw_game_background(self):
		self.game_background.draw(self.window)

	def draw_tiles(self):
		for tile in self.tiles:
			tile.draw(self.window)

	def draw_game_borders(self):
		
		#-# col Lines #-#
>>>>>>> master
		pygame.draw.line(self.window, White, (1, 0), (1, 1440), 4)
		pygame.draw.line(self.window, White, (1151, 0), (1151, 900), 4)
		pygame.draw.line(self.window, White, (1437, 0), (1437, 900), 4)

<<<<<<< HEAD
		#-# Row Lines #-#
=======
		#-# row Lines #-#
>>>>>>> master
		pygame.draw.line(self.window, White, (0, 1), (1440, 1), 4)
		pygame.draw.line(self.window, White, (1150, 65), (1440, 65), 4)
		pygame.draw.line(self.window, White, (1150, 200), (1440, 200), 4)
		pygame.draw.line(self.window, White, (1150, 255), (1438, 255), 4)
		pygame.draw.line(self.window, White, (1150, 640), (1440, 640), 4)
		pygame.draw.line(self.window, White, (1150, 720), (1440, 720), 4)
		pygame.draw.line(self.window, White, (1150, 810), (1440, 810), 4)
		pygame.draw.line(self.window, White, (0, 897), (1440, 897), 4)

	#-# Draw Enemies #-#
<<<<<<< HEAD
	def DrawEnemies(self):

		if self.gameStarted == True:
			
			#-# Create Enemies #-#
			enemyCountWillCreatedThisLevel = self.level * 10
			
			if self.enemyCountCreatedThisLevel < enemyCountWillCreatedThisLevel:
				if self.enemyCountCreatedThisLevel == enemyCountWillCreatedThisLevel - 1:
					self.levelFinihTime = pygame.time.get_ticks()
				if pygame.time.get_ticks() - self.startTimeEnemyCreated > 1000:
					self.enemyCountCreatedThisLevel += 1
					self.enemyCountCreatedAllTime += 1
					self.enemies.append(Enemy(self.enemyCountCreatedAllTime, self.level, (self.FirstRow*64) - 32, self.FirstColumn*64))
					self.startTimeEnemyCreated = pygame.time.get_ticks()
			elif self.levelFinihTime and pygame.time.get_ticks() - self.levelFinihTime > 5000:
				self.StartNextLevel()
=======
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
>>>>>>> master
			
			#-# Draw and Delete Enemies #-#
			for enemy in self.enemies:
				enemy.Walking = True 
<<<<<<< HEAD
				if enemy.X >= self.windowWidth - 32:
=======
				if enemy.pos.x >= self.windowWidth - 32:
>>>>>>> master
					self.enemies.remove(enemy)
					if self.live >= enemy.damage:
						self.live -= enemy.damage
					else:
						self.live = 0
						#-# Game Over #-#
<<<<<<< HEAD
						self.Exit()

				else:
					enemy.Move(self.map, self.speed)
					enemy.Draw(self.window)
		
		#-# Stop Enemies When Game Paused #-#
		elif not self.gameStarted and self.enemies:
			for enemy in self.enemies:
				enemy.Draw(self.window)
				enemy.Walking = False

	#-# Draw Towers #-#
	def DrawTowers(self):

		self.TowerPositions = []
		for tower in self.towers:

			#-# Remove Planes #-#
			if tower.Type == 4:
				if tower.X > 1125:
					self.towers.remove(tower)
			
			tower.Draw(self)

			#-# Draw Bullets #-#
			if tower.Type != 4:
				self.TowerPositions.append((tower.Row, tower.Column))
				
				for bullet in tower.Bullets:
					if self.gameStarted:
						bullet.Move(self)
					
					tower.Bullet.Draw(self.window)

	#-# Draw Game Objects #-#
	def DrawGameObjects(self):

		#-# Draw Objects #-#
		self.startPauseButton.Draw(self.window, self.mousePosition)
		self.x2Button.Draw(self.window, self.mousePosition)
		self.buyTower1.Draw(self.window, self.mousePosition)
		self.buyTower2.Draw(self.window, self.mousePosition)
		self.buyTower3.Draw(self.window, self.mousePosition)
		self.buyTower4.Draw(self.window, self.mousePosition)
		self.liveImage.Draw(self.window, self.mousePosition)
		self.liveText.ImagePath = list(self.liveText.ImagePath)
		self.liveText.ImagePath[1] = str(self.live)[0]
		self.liveText.ImagePath = tuple(self.liveText.ImagePath)
		self.liveText.Draw(self.window, self.mousePosition)
		if self.live == 10:
			self.liveText0.Draw(self.window, self.mousePosition)
		self.upgradePlanesButton.Draw(self.window, self.mousePosition)
		self.menuButton.Draw(self.window, self.mousePosition)

		#-# Texts #-#
		self.levelText.Draw(self.window)
		self.moneyBox.Draw(self.window)
		self.moneyText.Draw(self.window)
		self.dollarText.Draw(self.window)
		self.window.blit(self.BUYTBOX, (self.windowWidth - 265, 370))
		self.window.blit(self.BUYTBOX, (self.windowWidth - 125, 370))
		self.window.blit(self.BUYTBOX, (self.windowWidth - 265, 580))
		self.window.blit(self.BUYTBOX, (self.windowWidth - 125, 580))
		self.DrawFeeTexts()

	def Start(self):
		self.CreateTiles()
		self.GetFirstTile()

		while self.run:
			self.GetmousePosition()
			self.SetFPS()
=======
						self.exit()

				else:
					enemy.move(self.map, self.speed)
					enemy.draw(self.window)
		
		#-# Stop Enemies When Game Paused #-#
		elif not self.is_game_started and self.enemies:
			for enemy in self.enemies:
				enemy.draw(self.window)
				enemy.Walking = False

	#-# Draw Towers #-#
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

	#-# Draw Game Objects #-#
	def draw_game_objects(self):

		#-# Draw Objects #-#
		self.start_pause_button.draw(self.window, self.mouse_pos)
		self.x2_button.draw(self.window, self.mouse_pos)
		self.buy_tower1.draw(self.window, self.mouse_pos)
		self.buy_tower2.draw(self.window, self.mouse_pos)
		self.buy_tower3.draw(self.window, self.mouse_pos)
		self.buy_tower4.draw(self.window, self.mouse_pos)
		self.live_image.draw(self.window, self.mouse_pos)
		self.live_text.image_path = list(self.live_text.image_path)
		self.live_text.image_path[1] = str(self.live)[0]
		self.live_text.image_path = tuple(self.live_text.image_path)
		self.live_text.draw(self.window, self.mouse_pos)
		if self.live == 10:
			self.live_text0.draw(self.window, self.mouse_pos)
		self.upgrade_planes_button.draw(self.window, self.mouse_pos)
		self.menu_button.draw(self.window, self.mouse_pos)

		#-# Texts #-#
		self.level_text.draw(self.window)
		self.money_box.draw(self.window)
		self.money_text.draw(self.window)
		self.dollar_text.draw(self.window)
		self.window.blit(self.BUY_BOX, (self.windowWidth - 265, 370))
		self.window.blit(self.BUY_BOX, (self.windowWidth - 125, 370))
		self.window.blit(self.BUY_BOX, (self.windowWidth - 265, 580))
		self.window.blit(self.BUY_BOX, (self.windowWidth - 125, 580))
		self.draw_fee_texts()

	def start(self):
		self.create_tiles()
		self.get_first_tile()

		while self.run:
			self.get_mouse_position()
			self.set_fps()
>>>>>>> master
			
			if self.tab == "menu":

				#-# Get pygame events #-#
				for self.Event in pygame.event.get():
				
					#-# Button Control #-#
<<<<<<< HEAD
					if self.exitButton.Click(self.Event, self.mousePosition):
						self.Exit()
					if self.contactUsButton.Click(self.Event, self.mousePosition):	
						self.tab = "contactUs"	
					if self.playButton.Click(self.Event, self.mousePosition):
=======
					if self.exit_button.is_mouse_click(self.Event, self.mouse_pos):
						self.exit()
					if self.contact_us_button.is_mouse_click(self.Event, self.mouse_pos):
						self.tab = "contactUs"
					if self.play_button.is_mouse_click(self.Event, self.mouse_pos):
>>>>>>> master
						self.tab = "game"

					#-# Keyboard Keys Control #-#
					if self.Event.type == pygame.QUIT:
<<<<<<< HEAD
						self.Exit()
=======
						self.exit()
>>>>>>> master
					elif self.Event.type == pygame.KEYUP:
						if self.Event.key == pygame.K_F11:
							if self.window.fullScreen:
								self.window.MakeMinimizeScreen()
							else:
								self.window.MakeFullScreen()
						elif self.Event.key == pygame.K_ESCAPE:
<<<<<<< HEAD
							self.Exit()
					elif self.Event.type == pygame.MOUSEBUTTONUP:
						if self.musicPaused:
							if self.resumeMusicButton.Click(self.Event, self.mousePosition):
								self.ResumeMusic()
						elif self.pauseMusicButton.Click(self.Event, self.mousePosition):
							self.PauseMusic()

					if self.Event.type == self.MUSIC_ENDED:
=======
							self.exit()
					elif self.Event.type == pygame.MOUSEBUTTONUP:
						if self.is_music_paused:
							if self.resume_music_button.is_mouse_click(self.Event, self.mouse_pos):
								self.ResumeMusic()
						elif self.pause_music_button.is_mouse_click(self.Event, self.mouse_pos):
							self.PauseMusic()

					if self.Event.type == self.IS_MUSIC_ENDED:
>>>>>>> master
						self.StartMusic()

			elif self.tab == "contactUs":
				
				#-# Get pygame events #-#
				for self.Event in pygame.event.get():

					#-# Button Control #-#
<<<<<<< HEAD
					if self.goBackButton.Click(self.Event, self.mousePosition):	
=======
					if self.go_back_button.is_mouse_click(self.Event, self.mouse_pos):	
>>>>>>> master
						self.tab = "menu"

					#-# Keyboard Keys Control #-#
					if self.Event.type == pygame.QUIT:
<<<<<<< HEAD
						self.Exit()
=======
						self.exit()
>>>>>>> master
					
					elif self.Event.type == pygame.KEYUP:
						if self.Event.key == pygame.K_F11:
							if self.window.fullScreen:
								self.window.MakeMinimizeScreen()
							else:
								self.window.MakeFullScreen()
						elif self.Event.key == pygame.K_ESCAPE:
							self.tab = "menu"
					
			elif self.tab == "game":
				
				#-# Calculating Which Tile is mouse on it #-#
<<<<<<< HEAD
				if self.mousePosition[0] < 1152:
					self.CursorColumn = self.mousePosition[0]//64
					self.CursorRow = self.mousePosition[1]//64
=======
				if self.mouse_pos[0] < 1152:
					self.cursor_col = self.mouse_pos[0]//64
					self.cursor_row = self.mouse_pos[1]//64
>>>>>>> master

				#-# Get pygame events #-#
				for self.Event in pygame.event.get():
					
					#-# Button Control #-#
<<<<<<< HEAD
					if self.menuButton.Click(self.Event, self.mousePosition):	
=======
					if self.menu_button.is_mouse_click(self.Event, self.mouse_pos):	
>>>>>>> master
						self.tab = "menu"
						self.GameStarted = False
						
					#-# Keyboard Keys Control #-#
					if self.Event.type == pygame.QUIT:
<<<<<<< HEAD
						self.Exit()
=======
						self.exit()
>>>>>>> master

					elif self.Event.type == pygame.KEYUP:
						if self.Event.key == pygame.K_F11:
							if self.window.fullScreen:
								self.window.MakeMinimizeScreen()
							else:
								self.window.MakeFullScreen()
						elif self.Event.key == pygame.K_ESCAPE:
							self.tab = "menu"

					elif self.Event.type == pygame.MOUSEBUTTONUP:
						
						#-# Choose Selected Tower #-#
						for tower in self.towers:
<<<<<<< HEAD
							if self.selectedTower == tower:
								tower.Sell(self.mousePosition, self)
								tower.Upgrade(self.mousePosition, self)		
					
						
						#-# Selecting A Tower #-#
						if self.buyyingTowerType == 0:
							clickedATower = False
							for tower in self.towers:
								if self.CursorColumn == tower.Column and self.CursorRow == tower.Row:
									clickedATower = True
									if self.selectedTower != None and self.selectedTower == tower:
										self.selectedTower = None	
									else:		
										self.selectedTower = tower
							if not clickedATower:
								self.selectedTower = None

							#-# Building a Tower #-#
						if self.mousePosition[0] <= 1152:
							if self.buyyingTowerType and not (self.CursorRow, self.CursorColumn) in self.BlockTiles:
								tower = Tower(self.buyyingTowerType, self.CursorRow, self.CursorColumn, self)   
								if tower.Type == 4:	
									self.towers.append(tower)
								else:												
									self.towers.insert(0, tower)
								self.DecreaseMoney(self.towerSellPrices[tower.Type - 1][0])
								self.buyyingTowerType = 0

					#-# Upgrade planes button #-#
					if self.upgradePlanesButton.Click(self.Event, self.mousePosition) and self.money >= 5000 and self.planeLevel == 1:
						self.DecreaseMoney(5000)
						self.buyTower4.ImagePath[1] = "tower4L2"
						self.planeLevel = 2

					#-# Start-Pause Button #-#
					if self.startPauseButton.Click(self.Event, self.mousePosition):
						if self.startPauseButton.ImagePath == ("button", "start"):
							self.gameStarted = True
							self.startPauseButton.ImagePath = ("button", "pause")
						else:
							self.gameStarted = False
							self.startPauseButton.ImagePath = ("button", "start")

					#-# x2 Button #-#
					if self.x2Button.Click(self.Event, self.mousePosition):
						if self.x2Button.ImagePath == ("button", "2x"):
							self.x2Button.ImagePath = ("button", "2x2")
							#self.FPS *= 2
							#self.speed = 2
						else:
							self.x2Button.ImagePath = ("button", "2x")
=======
							if self.selected_tower == tower:
								tower.sell(self.mouse_pos, self)
								tower.upgrade(self.mouse_pos, self)

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
						if self.mouse_pos[0] <= 1152:
							if self.buying_tower_type and not (self.cursor_row, self.cursor_col) in self.block_tiles:
								tower = Tower(self.buying_tower_type, self.cursor_row, self.cursor_col, self)   
								if tower.type == 4:	
									self.towers.append(tower)
								else:												
									self.towers.insert(0, tower)
								self.decrease_money(self.tower_sell_prices[tower.type - 1][0])
								self.buying_tower_type = 0

					#-# Upgrade planes button #-#
					if self.upgrade_planes_button.is_mouse_click(self.Event, self.mouse_pos) and self.money >= 5000 and self.plane_level == 1:
						self.decrease_money(5000)
						self.buy_tower4.image_path[1] = "tower4L2"
						self.plane_level = 2

					#-# Start-Pause Button #-#
					if self.start_pause_button.is_mouse_click(self.Event, self.mouse_pos):
						if self.start_pause_button.image_path == ("button", "start"):
							self.is_game_started = True
							self.start_pause_button.image_path = ("button", "pause")
						else:
							self.is_game_started = False
							self.start_pause_button.image_path = ("button", "start")

					#-# x2 Button #-#
					if self.x2_button.is_mouse_click(self.Event, self.mouse_pos):
						if self.x2_button.image_path == ("button", "2x"):
							self.x2_button.image_path = ("button", "2x2")
							#self.FPS *= 2
							#self.speed = 2
						else:
							self.x2_button.image_path = ("button", "2x")
>>>>>>> master
							#self.FPS *= 1/2,
							#self.speed = 1
		
					#-# Buy Tower #-#
<<<<<<< HEAD
					if self.buyTower1.Click(self.Event,self.mousePosition) and self.money >= self.towerSellPrices[0][0]:
						if self.buyyingTowerType == 1:
							self.buyyingTowerType = 0
						else:
							self.buyyingTowerType = 1
					elif self.buyTower2.Click(self.Event,self.mousePosition) and self.money >=self.towerSellPrices[1][0]:
						if self.buyyingTowerType == 2:
							self.buyyingTowerType = 0
						else:
							self.buyyingTowerType = 2
					elif self.buyTower3.Click(self.Event,self.mousePosition) and self.money >=self.towerSellPrices[2][0]:
						if self.buyyingTowerType == 3:
							self.buyyingTowerType = 0
						else:
							self.buyyingTowerType = 3
					elif self.buyTower4.Click(self.Event,self.mousePosition) and self.money >=self.towerSellPrices[3][0]:
						if self.buyyingTowerType == 4:
							self.buyyingTowerType = 0
						else:
							self.buyyingTowerType = 4

			#-# Draw Objects #-#
			self.Draw()

	#-# Drawing All Things to the Window in game tab #-#
	def Draw(self):
			
		if self.tab == "menu":
			self.DrawMenuBackgorund()
			self.logo.Draw(self.window)
			self.playButton.Draw(self.window, self.mousePosition)
			self.contactUsButton.Draw(self.window, self.mousePosition)
			self.exitButton.Draw(self.window, self.mousePosition)
			self.DrawMusicButton()

		elif self.tab =="contactUs":
			self.menuBackground.Draw(self.window)
			self.logo.Draw(self.window)
			self.socialMedia.Draw(self.window)	
			self.goBackButton.Draw(self.window, self.mousePosition)
			self.DrawMusicButton()

		elif self.tab == "game":

			self.DrawGameBackground()
			self.DrawTiles()
			self.DrawTowers()
			self.DrawEnemies()
			self.DrawGameBorders()
			self.DrawGameObjects()

			#-# Choosing Blocked Tiles #-#
			if self.buyyingTowerType != 0:
				self.BlockTiles = []
				rowNumber = 0
				for row in self.map:
					rowNumber += 1
					columnNumber = 0
					for tile in row:
						columnNumber += 1
						if ((tile == "0" or tile == "3") and not((rowNumber - 1, columnNumber - 1) in self.TowerPositions)) or self.buyyingTowerType == 4:   
							self.window.blit(self.enable, (64*(columnNumber - 1), 64*(rowNumber - 1)))					
						else:				
							self.window.blit(self.block, (64*(columnNumber - 1), 64*(rowNumber - 1)))
							self.BlockTiles.append((rowNumber - 1, columnNumber - 1))
				
				#-# Drawing Buyyed Tower To Mouse Position
				if self.mousePosition[0] >= 1152:
					if self.buyyingTowerType == 4 and self.planeLevel == 2:
						self.window.blit(self.towerImages[self.buyyingTowerType], (self.mousePosition[0] - 32, self.mousePosition[1] - 32))
					else:
						self.window.blit(self.towerImages[self.buyyingTowerType - 1], (self.mousePosition[0] - 32, self.mousePosition[1] - 32))
				else:
					#-# Show where you can build the tower #-#
					if self.buyyingTowerType == 4 and self.planeLevel == 2:				
						self.window.blit(self.towerImages[self.buyyingTowerType], (self.CursorColumn*64, self.CursorRow*64))
					else:
						self.window.blit(self.towerImages[self.buyyingTowerType - 1], (self.CursorColumn*64, self.CursorRow*64))

					#-# Draw Range of Tower #-#
					range = self.towerRanges[self.buyyingTowerType - 1][0]		
					self.Surface = pygame.Surface((range*2, range*2), pygame.SRCALPHA, 32)
					pygame.draw.circle(self.Surface, (128, 128, 128, 120), (range, range), range, 0)
					if (self.CursorRow, self.CursorColumn) in self.BlockTiles:
						pygame.draw.circle(self.Surface, (255, 0, 0, 120), (range, range), range, 5)
					else:				
						pygame.draw.circle(self.Surface, (0, 200, 0, 120), (range, range), range, 5)
					self.window.blit(self.Surface, ((self.CursorColumn*64) + 32 - range, ((self.CursorRow*64) + 32 - range)))			
		
		self.window.Draw()
=======
					if self.buy_tower1.is_mouse_click(self.Event,self.mouse_pos) and self.money >= self.tower_sell_prices[0][0]:
						if self.buying_tower_type == 1:
							self.buying_tower_type = 0
						else:
							self.buying_tower_type = 1
					elif self.buy_tower2.is_mouse_click(self.Event,self.mouse_pos) and self.money >=self.tower_sell_prices[1][0]:
						if self.buying_tower_type == 2:
							self.buying_tower_type = 0
						else:
							self.buying_tower_type = 2
					elif self.buy_tower3.is_mouse_click(self.Event,self.mouse_pos) and self.money >=self.tower_sell_prices[2][0]:
						if self.buying_tower_type == 3:
							self.buying_tower_type = 0
						else:
							self.buying_tower_type = 3
					elif self.buy_tower4.is_mouse_click(self.Event,self.mouse_pos) and self.money >=self.tower_sell_prices[3][0]:
						if self.buying_tower_type == 4:
							self.buying_tower_type = 0
						else:
							self.buying_tower_type = 4

			#-# Draw Objects #-#
			self.draw()

	#-# Drawing All Things to the Window in game tab #-#
	def draw(self):
			
		if self.tab == "menu":
			self.draw_menu_background()
			self.logo.draw(self.window)
			self.play_button.draw(self.window, self.mouse_pos)
			self.contact_us_button.draw(self.window, self.mouse_pos)
			self.exit_button.draw(self.window, self.mouse_pos)
			self.draw_music_button()

		elif self.tab == "contactUs":
			self.menu_background.draw(self.window)
			self.logo.draw(self.window)
			self.social_media.draw(self.window)	
			self.go_back_button.draw(self.window, self.mouse_pos)
			self.draw_music_button()

		elif self.tab == "game":

			self.draw_game_background()
			self.draw_tiles()
			self.draw_towers()
			self.draw_enemies()
			self.draw_game_borders()
			self.draw_game_objects()

			#-# Choosing Blocked Tiles #-#
			if self.buying_tower_type != 0:
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
				if self.mouse_pos[0] >= 1152:
					if self.buying_tower_type == 4 and self.plane_level == 2:
						self.window.blit(self.tower_images[self.buying_tower_type], (self.mouse_pos[0] - 32, self.mouse_pos[1] - 32))
					else:
						self.window.blit(self.tower_images[self.buying_tower_type - 1], (self.mouse_pos[0] - 32, self.mouse_pos[1] - 32))
				else:
					#-# Show where you can build the tower #-#
					if self.buying_tower_type == 4 and self.plane_level == 2:				
						self.window.blit(self.tower_images[self.buying_tower_type], (self.cursor_col*64, self.cursor_row*64))
					else:
						self.window.blit(self.tower_images[self.buying_tower_type - 1], (self.cursor_col*64, self.cursor_row*64))

					#-# Draw Range of Tower #-#
					range = self.tower_ranges[self.buying_tower_type - 1][0]
					self.surface = pygame.Surface((range*2, range*2), pygame.SRCALPHA, 32)
					pygame.draw.circle(self.surface, (128, 128, 128, 120), (range, range), range, 0)
					if (self.cursor_row, self.cursor_col) in self.block_tiles:
						pygame.draw.circle(self.surface, (255, 0, 0, 120), (range, range), range, 5)
					else:				
						pygame.draw.circle(self.surface, (0, 200, 0, 120), (range, range), range, 5)
					self.window.blit(self.surface, ((self.cursor_col*64) + 32 - range, ((self.cursor_row*64) + 32 - range)))			

		self.window.draw()
>>>>>>> master

		#-# Update All Things to the Screen #-#
		pygame.display.update()

<<<<<<< HEAD
	#-# Exit #-#
	def Exit(self):
=======
	def exit(self):
>>>>>>> master
		self.Run = False		
		pygame.quit()
		sys.exit()
					
#-# CHECK FOR NOT EXPORTING #-#
if (__name__ == "__main__"):
	game = Game()
<<<<<<< HEAD
	game.Start()
=======
	game.start()
>>>>>>> master
