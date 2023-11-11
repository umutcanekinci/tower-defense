### IMPORTING THE PACKAGES ########################################################################################################################################################
import pygame
from colors import *
from objects import *
from projectiles import *
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
