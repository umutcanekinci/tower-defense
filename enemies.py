### IMPORTING THE PACKAGES ########################################################################################################################################################
import pygame
### ENEMY CLASS ###################################################################################################################################################################
class Enemy(object):
	def __init__(self, number, level, x, y):
		self.Number = number
		self.Walking = True
		self.X = x
		self.Y = y
		self.Image = pygame.image.load("images/enemy/E1.png").convert_alpha()
		self.move = "R"

		self.CalculateStats(level)

	def CalculateStats(self, level):
		self.maxHP = 10 * ((level//10) + 1)**2  
		self.HP = self.maxHP
		self.killMoney = ((level//5) + 1)*1
		self.damage = (level//25) + 1
		#self.MovSpeed = 1 + level*0.02
		self.MovSpeed = 1

	def Destroy(self, game):
		if self in game.enemies:
			game.enemies.remove(self)

	def DecreaseHP(self, damage, game):
		if self in game.enemies:
			self.HP -= damage

			if self.HP <= 0:
				self.Destroy(game)
				game.IncreaseMoney(self.killMoney)

	def GetColumn(self):
		return (self.X//64) + 1

	def GetRow(self):
		return (self.Y//64) + 1
	
	def Move(self, map, gameSpeed):
		self.RowNumber = 0

		#-# Rotate Enemy #-#
		for Row in map:
			self.RowNumber += 1
			self.ColumnNumber = 0
			for Column in Row:
				self.ColumnNumber += 1
				if(len(Column) >= 2 and self.ColumnNumber == self.GetColumn() and self.RowNumber == self.GetRow() and self.X % 64 == 0 and self.Y % 64 == 0): 		
					if(Column[1] == "R"):
						if(self.move == "U"):
							self.Image = pygame.transform.rotate(self.Image, -90)
						if(self.move == "D"):
							self.Image = pygame.transform.rotate(self.Image, +90)
						self.move = "R"
					elif(Column[1] == "U"):
						if(self.move == "R"):
							self.Image = pygame.transform.rotate(self.Image, +90)
						if(self.move == "L"):
							self.Image = pygame.transform.rotate(self.Image, -90)
						self.move = "U"
					elif(Column[1] == "L"):
						if(self.move == "U"):
							self.Image = pygame.transform.rotate(self.Image, +90)
						if(self.move == "D"):
							self.Image = pygame.transform.rotate(self.Image, -90)
						self.move = "L"
					elif(Column[1] == "D"):
						if(self.move == "R"):
							self.Image = pygame.transform.rotate(self.Image, -90)
						if(self.move == "L"):
							self.Image = pygame.transform.rotate(self.Image, +90)
						self.move = "D"

		#-# Move Enemy #-#
		if self.move == "R":
			self.X += self.MovSpeed*gameSpeed
		elif self.move == "U":
			self.Y -= self.MovSpeed*gameSpeed
		elif self.move == "L":
			self.X -= self.MovSpeed*gameSpeed
		elif self.move == "D":
			self.Y += self.MovSpeed*gameSpeed
		elif self.move == "B" or self.move == "E":
			self.X += self.MovSpeed*gameSpeed

	def Draw(self, surface):

		surface.blit(self.Image, (self.X, self.Y))
### END OF CLASS ##################################################################################################################################################################

