<<<<<<< HEAD
### IMPORTING THE PACKAGES ########################################################################################################################################################
=======
>>>>>>> master
import pygame
from colors import *
from objects import *
from projectiles import *
<<<<<<< HEAD
from math import pi, atan2, degrees
### TOWER CLASS ###################################################################################################################################################################
class Tower(object):
	def __init__(self, TowerType, Row, Column, Game):
		self.Type, self.Row, self.Column, self.Level, self.Angle, self.LastReloadTime = TowerType, Row, Column, 1, 0, 0
		self.maxLevel, self.X, self.Y, self.Bullets = Game.towerMaxLevels[self.Type - 1], self.Column * 64, self.Row * 64, []

	def Upgrade(self, MousePosition, Game):	
		if self.Type != 4 and self.Level + 1 <= self.maxLevel and Game.money >= self.price and pygame.Rect(self.X - 40, self.Y - self.range - 42, 50, 50).collidepoint(MousePosition):
			self.Level += 1
			Game.money -= self.price	
			Game.selectedTower = self

	def Sell(self, MousePosition, Game):
		if self.Type != 4 and Game.selectedTower == self and pygame.Rect(self.X + 40, self.Y - self.range - 54, 50, 50).collidepoint(MousePosition):			
			Game.IncreaseMoney(self.sellPrice)
			Game.towers.remove(self)

	def Draw(self, Game):

		#-# Tower Features #-#
		self.Image = pygame.image.load("images/towers/tower" + str(self.Type) + "L" + str(self.Level) + ".png").convert_alpha()
		self.range = Game.towerRanges[self.Type - 1][self.Level - 1]
		self.damage = Game.towerDamages[self.Type - 1][self.Level - 1]
		self.speed = Game.towerSpeeds[self.Type - 1][self.Level - 1]

		self.Now = pygame.time.get_ticks()		
		if self.Type == 2:
			self.Image = pygame.image.load("images/towers/tower" + str(self.Type) + "L" + str(self.Level) + "_.png").convert_alpha()
			if self.Now - self.LastReloadTime > self.speed - 1000:
				self.Image = pygame.image.load("images/towers/tower" + str(self.Type) + "L" + str(self.Level) + ".png").convert_alpha()

		#-# Move the Plane #-#
		if self.Type == 4:
			self.Level = Game.planeLevel
			self.Shadow = pygame.image.load("images/towers/tower" + str(self.Type) + "shadow" + str(self.Level) + ".png").convert_alpha()
			if Game.gameStarted == True and self.X <= 1125:
				self.X += self.speed
				self.Column = (self.X // 64)
			Game.window.blit(self.Shadow, (self.X - 20, self.Y + 20))
		else:
			#-# prices #-#
			self.priceFont = pygame.font.SysFont("ComicSansMs", 30)
			self.sellPrice = Game.towerSellPrices[self.Type - 1][self.Level - 1]
			self.sellPriceText = self.priceFont.render(str(self.sellPrice) + " $", 2, White)
			if self.Level != self.maxLevel:
				self.price = Game.towerSellPrices[self.Type - 1][self.Level]
				self.priceText = self.priceFont.render(str(self.price) + " $", 2, White)

			#-# Objects #-#
			self.SellButton = Object("", (self.X + 40, self.Y - self.range - 54), (50, 50), ("button","sell"))
			self.UpgradeButton = Object("", (self.X - 40, self.Y - self.range - 42), (50, 50), ("button", "upgrade"))
			self.Max = Object("", (self.X - 40, self.Y - self.range - 26), (50, 25), ("button","max"))
			self.Platform = pygame.image.load("images/towers/tower" + str(self.Type) + "platform" + str(self.Level) + ".png").convert_alpha()
			Game.window.blit(self.Platform, (self.X, self.Y))
		
		if Game.selectedTower == self:

			#-# Draw range #-#
			self.Surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA, 32) 
			pygame.draw.circle(self.Surface, (128, 128, 128, 120), (int(self.range), int(self.range)), int(self.range), 0)				
			pygame.draw.circle(self.Surface, (0, 200, 0, 120), (int(self.range), int(self.range)), int(self.range), 2)		
			Game.window.blit(self.Surface, (self.X + 32 - self.range, self.Y + 32 - self.range))

			#-# Draw Sell and Upgrade Button #-#
			if self.Type != 4:
				if self.Level == self.maxLevel:
					self.Max.Draw(Game.window)
				else:
					self.UpgradeButton.Draw(Game.window)
					Game.window.blit(self.priceText, (self.X - 35, self.Y - self.range + 10))
				Game.window.blit(self.sellPriceText, (self.X + 45, self.Y - self.range + 10))
				self.SellButton.Draw(Game.window)

		self.Distances, self.DistanceXY = [], []

		if Game.gameStarted == True and Game.enemies != [] and self.Type != 4:
			for Enemy in Game.enemies:
				self.DistanceX = self.Y - Enemy.Y
				self.DistanceY = self.X - Enemy.X
				self.Distance = (abs(self.DistanceX)**2 + abs(self.DistanceY)**2)**(1 / 2)
				self.Distances.append(self.Distance)
				self.DistanceXY.append([self.DistanceX, self.DistanceY])

			self.TheNearestDistance = min(self.Distances)
			self.TheNearestEnemyXY = self.DistanceXY[self.Distances.index(self.TheNearestDistance)]

			if 	self.TheNearestDistance <= self.range:

				#-# Rotate the Tower to the Enemys #-#
				self.Radian = atan2(-self.TheNearestEnemyXY[1], self.TheNearestEnemyXY[0])
				self.Angle = degrees(self.Radian)
				
				#-# Attack #-#
				self.Now = pygame.time.get_ticks()
				if self.Now - self.LastReloadTime > self.speed:
					self.LastReloadTime = self.Now
					self.Bullet = Projectile(Game.enemies[self.Distances.index(self.TheNearestDistance)], self, self.Angle)
					self.Bullets.append(self.Bullet)

		#-# Rotate the Tower It's Last Angle #-#
		self.Rect = [self.X + 32, self.Y + 32]
		self.Image = pygame.transform.rotate(self.Image, -self.Angle)
		self.Rect = self.Image.get_rect(center = self.Rect)
		if self.Type == 3 or (self.Type == 2 and self.Level == 3):
			self.Rect[1] -= 20

		Game.window.blit(self.Image, self.Rect)
### END OF CLASS ##################################################################################################################################################################
=======
from game_math import angle_between_delta
from image import load_image
from game_object import GameObject

class Tower(GameObject):
	PRICE_FONT = pygame.font.SysFont("ComicSansMs", 15)

	def __init__(self, tower_type, row, col, game):
		super().__init__((col * 64 + 32, row * 64 + 32))
		self.type, self.row, self.col, self.level, self.last_reload_time = tower_type, row, col, 1, 0
		self.max_level = game.tower_max_levels[self.type - 1]
		self.bullets: list[Projectile] = []
		self.load_image()

		if not self.is_plane():
			self.platform = GameObject(self.pos)
			self.platform.load_image("towers/tower" + str(self.type) + "platform" + str(self.level) + ".png")

	def load_image(self):
		super().load_image("towers/tower" + str(self.type) + "L" + str(self.level) + ".png")

	def is_plane(self):
		return self.type == 4

	def is_max_level(self):
		return self.level >= self.max_level

	def upgrade(self, mouse_pos, game):	
		if self.is_plane() or self.is_max_level() or game.money < self.price or not pygame.Rect(self.pos.x - 72, self.pos.y - self.range - 74, 50, 50).collidepoint(mouse_pos):
			return

		self.level += 1
		game.money -= self.price
		game.selected_tower = self

	def sell(self, mouse_pos, game):
		if self.is_plane() or game.selected_tower != self:
			return
		
		if pygame.Rect(self.pos.x + 40, self.pos.y - self.range - 54, 50, 50).collidepoint(mouse_pos):			
			game.increase_money(self.sell_price)
			game.towers.remove(self)

	def update_and_draw(self, game):
		#-# Tower Features #-#
		self.load_image()
		self.range =  game.tower_ranges [self.type - 1][self.level - 1]
		self.damage = game.tower_damages[self.type - 1][self.level - 1]
		self.speed =  game.tower_speeds [self.type - 1][self.level - 1]

		self.now = pygame.time.get_ticks()
		if self.type == 2:
			self.image = load_image("towers/tower" + str(self.type) + "L" + str(self.level) + "_.png")
			if self.now - self.last_reload_time > self.speed - 1000:
				self.image = load_image("towers/tower" + str(self.type) + "L" + str(self.level) + ".png")

		if self.is_plane():
			self.move_plane(game)
		else:
			self.platform.draw(game.window)

		if self.is_selected(game):
			self.draw_range(game)

			if not self.is_plane():
				self.draw_selected(game)

		self.work(game)

		#if self.type == 3 or (self.type == 2 and self.level == 3):
		#	self.rect[1] -= 20

		self.draw(game.window)

	def is_selected(self, game) -> bool:
		return game.selected_tower == self

	def move_plane(self, game):
		self.level = game.plane_level
		self.shadow = load_image("towers/tower" + str(self.type) + "shadow" + str(self.level) + ".png")
		if game.is_game_started == True and self.pos.x <= 1125:
			self.pos.x += self.speed
			self.column = (self.pos.x // 64)
		game.window.blit(self.shadow, (self.pos.x - 20, self.pos.y + 20))

	def draw_range(self, game):
		self.surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA, 32) 
		pygame.draw.circle(self.surface, (128, 128, 128, 120), (int(self.range), int(self.range)), int(self.range), 0)				
		pygame.draw.circle(self.surface, (0, 200, 0, 120),     (int(self.range), int(self.range)), int(self.range), 2)		
		game.window.blit(self.surface, (self.pos.x - self.range, self.pos.y - self.range))

	def draw_selected(self, game):
		self.sell_button    = GUI_Object("", self.pos + Vector2(20,  -110), (50, 50), ("button","sell"))
		self.upgrade_button = GUI_Object("", self.pos + Vector2(-55, -105), (50, 50), ("button", "upgrade"))
		self.max_button     = GUI_Object("", self.pos + Vector2(-60, -85), (50, 25), ("button","max"))

		self.sell_price = game.tower_sell_prices[self.type - 1][self.level - 1]
		self.sell_price_text = self.PRICE_FONT.render(str(self.sell_price) + " $", 2, White)

		if self.is_max_level():
			self.max_button.draw(game.window)
		else:
			self.price = game.tower_sell_prices[self.type - 1][self.level]
			self.price_text = self.PRICE_FONT.render(str(self.price) + " $", 2, White)
			game.window.blit(self.price_text, self.pos + Vector2(-50, - 60))
			self.upgrade_button.draw(game.window)

		game.window.blit(self.sell_price_text, self.pos + Vector2(30, - 60))
		self.sell_button.draw(game.window)

	def work(self, game):
		if game.is_game_started != True or game.enemies == [] or self.is_plane():
			return
		
		distances: list[Vector2] = [enemy.pos - self.pos for enemy in game.enemies]
		lengths  : list[float]   = [dist.length() for dist in distances]
		nearest_distance = min(lengths)
		nearest_enemy_index = lengths.index(nearest_distance)
		the_nearest_enemy_distance = distances[nearest_enemy_index]

		if not self.is_in_range(nearest_distance):
			return
		
		self.rotate_to_angle(angle_between_delta(the_nearest_enemy_distance))

		if self.is_attack_ready():
			self.shoot(game.enemies[nearest_enemy_index])

	def is_in_range(self, distance: float) -> bool:
		return distance <= self.range

	def is_attack_ready(self) -> bool:
		self.now = pygame.time.get_ticks()
		return self.now - self.last_reload_time > self.speed

	def shoot(self, target) -> None:
		self.bullet = Projectile(target, self)
		self.bullets.append(self.bullet)
		self.last_reload_time = self.now
>>>>>>> master
