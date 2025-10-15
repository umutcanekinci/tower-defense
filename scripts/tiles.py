from towers import *
from core.image import load_image, scale_surface_by

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

class Tile(GameObject):
	tiles = {"0": "tiles/grass", "1": "tiles/clay", "2": "tiles/stone", "3": "tiles/sand"}

	def __init__(self, type, col, row, Game):
		super().__init__(self.tiles[type[0]], (col * 64 + 32, row * 64 + 32))
		self.type, self.row, self.col, self.decoration = type, row, col, None

		self.load_image(self.tiles[self.type[0]])

		if len(self.type) > 2 and self.type[1] + self.type[2] == "+B":
			self.decoration = GameObject("tiles/B" + self.type[self.type.index("+B") + 2], self.pos)

	def draw(self, surface, game):
		game.camera.draw(surface, self)
		if self.decoration == None:
			return
		game.camera.draw(surface, self.decoration)

	def get_first_tile(self):
		if len(self.type) > 1 and self.type[1] == "B":
			return [self.col, self.row]
		return [None, None]

	def get_last_tile(self):
		if len(self.type) > 1 and self.type[1] == "E":
			return [self.col, self.row]
		return [None, None]
