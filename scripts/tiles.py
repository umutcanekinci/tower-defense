from towers import *
from image import load_image

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

class Tile(object):
	def __init__(self, type, col, row, Game):
		self.type, self.row, self.col, self.image2 = type, row, col, None
		self.x, self.y = self.col * 64, self.row * 64 

		if self.type[0] == "0":
			self.image = load_image("tiles/grass.png")
		elif self.type[0] == "1":
			self.image = load_image("tiles/clay.png")
		elif self.type[0] == "2":
			self.image = load_image("tiles/stone.png")
		elif self.type[0] == "3":
			self.image = load_image("tiles/sand.png")

		if len(self.type) > 2 and self.type[1] + self.type[2] == "+B":
			self.image2 = load_image("tiles/B" + self.type[self.type.index("+B") + 2] + ".png")

	def draw(self, window):
		window.blit(self.image, (self.x, self.y))
		if self.image2 == None:
			return
		window.blit(self.image2, (self.x, self.y))
	
	def get_first_tile(self):
		if len(self.type) > 1 and self.type[1] == "B":
			return [self.col, self.row]
		return [None, None]

	def get_last_tile(self):
		if len(self.type) > 1 and self.type[1] == "E":
			return [self.col, self.row]
		return [None, None]
