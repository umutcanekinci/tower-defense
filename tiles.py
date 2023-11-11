### IMPORTING THE PACKAGES ########################################################################################################################################################
import pygame
from towers import *

map =   [["0",    "0",    "0",    "0",    "0",    "0+B1", "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0+B8", "0",    "0",    "0",    "0"],
			["0",    "0",    "0",    "0",    "0",    "0",    "0+B2", "0",    "0",    "0+B7", "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0"],
			["0",    "0",    "1R",   "1R",   "1R",   "1D",   "0",    "0",    "1R",   "1R",   "1R",   "1R",   "1R",   "1R",   "1R",   "1R",   "1R",   "1E"],
			["0",    "0",    "1U",   "0",    "0",    "1D",   "0",    "0",    "1U",   "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0"],
			["0",    "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "2U",   "2L",   "2L",   "2L",   "2L",   "2L",   "2L",   "2L",   "0",    "0"],
			["0",    "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "2U",   "0",    "0"],
			["0+B2", "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "2U",   "0",    "0"],
			["0",    "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "2U",   "0",    "0"],
			["0",    "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "2U",   "0",    "0"],
			["0+B4", "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "2U",   "0",    "0"],
			["0",    "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "2U",   "0",    "0"],
			["1B",   "1R",   "1U",   "0",    "0",    "2R",   "2R",   "2R",   "2R",   "2R",   "2R",   "2R",   "2R",   "2R",   "2R",   "2U",   "0",    "0"],
			["0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0+B5", "0",    "0",    "0",    "0+B7", "0",    "0",    "0+B1", "0",    "0"],
			["0",    "0+B6", "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0"]]

### TILE CLASS ###################################################################################################################################################################
class Tile(object):
	def __init__(self, Type, Column, Row, Game):
		self.Type, self.Row, self.Column, self.Image2 = Type, Row, Column, None
		self.X, self.Y = self.Column * 64, self.Row * 64 

		if self.Type[0] == "0":
			self.Image = pygame.image.load("images/tiles/grass.png").convert_alpha()
		elif self.Type[0] == "1":
			self.Image = pygame.image.load("images/tiles/clay.png").convert_alpha()
		elif self.Type[0] == "2":
			self.Image = pygame.image.load("images/tiles/stone.png").convert_alpha()
		elif self.Type[0] == "3":
			self.Image = pygame.image.load("images/tiles/sand.png").convert_alpha()

		if len(self.Type) > 2 and self.Type[1] + self.Type[2] == "+B":
			self.Image2 = pygame.image.load("images/tiles/B" + self.Type[self.Type.index("+B") + 2] + ".png").convert_alpha()

	def Draw(self, Window):
		Window.blit(self.Image, (self.X, self.Y))
		if self.Image2 != None:
			Window.blit(self.Image2, (self.X, self.Y))
	
	def GetFirstTile(self):
		if len(self.Type) > 1:
			if self.Type[1] == "B":
				return [self.Column, self.Row]
		return [None, None]
			
	def GetLastTile(self):
		if len(self.Type) > 1:
			if self.Type[1] == "E":
				return [self.Column, self.Row]
		return [None, None]
### END OF CLASS ##################################################################################################################################################################
