import enum
from core.image import rotate_surface
from core.game_object import GameObject

class Enemy(GameObject):
	class Direction(enum.Enum):
		Right = "R"
		Up = "U"
		Left = "L"
		Down = "D"
		Back = "B"
		Enter = "E"

	def __init__(self, id, level, x, y):
		super().__init__("enemy/E1", (x + 32, y + 32))
		self.id = id
		self.is_walking = True	
		self.direction = self.Direction.Right
		self.calculate_stats(level)

	def calculate_stats(self, level):
		self.maxHP = 10 * ((level // 10) + 1)**2  
		self.hp = self.maxHP
		self.killMoney = ((level // 5) + 1)*1
		self.damage = (level // 25) + 1
		#self.MovSpeed = 1 + level*0.02
		self.mov_speed = 1

	def destroy(self, game):
		if self in game.enemies:
			game.enemies.remove(self)

	def decrease_hp(self, damage, game):
		if self in game.enemies:
			self.hp -= damage

			if self.hp <= 0:
				self.destroy(game)
				game.increase_money(self.killMoney)

	def get_column(self):
		return (self.pos.x // 64) + 1

	def get_row(self):
		return (self.pos.y // 64) + 1

	def move(self, map, game_speed):
		self.row_number = 0
		self.rotate(map)

		#-# Move Enemy #-#
		if self.direction == self.Direction.Right:
			self.pos.x += self.mov_speed * game_speed
		elif self.direction == self.Direction.Up:
			self.pos.y -= self.mov_speed * game_speed
		elif self.direction == self.Direction.Left:
			self.pos.x -= self.mov_speed * game_speed
		elif self.direction == self.Direction.Down:
			self.pos.y += self.mov_speed * game_speed
		elif self.direction == self.Direction.Back or self.direction == self.Direction.Enter:
			self.pos.x -= self.mov_speed * game_speed
		self.rect.center = self.pos

	def rotate(self, map):
		for row in map:
			self.row_number += 1
			self.column_number = 0
			for column in row:
				self.column_number += 1
				if(len(column) >= 2 and self.column_number == self.get_column() and self.row_number == self.get_row() and (self.pos.x - 32) % 64 == 0 and (self.pos.y - 32) % 64 == 0): 		
					if(column[1] == "R"):
						if(self.direction == self.Direction.Up):
							self.image = rotate_surface(self.image, -90)
						if(self.direction == self.Direction.Down):
							self.image = rotate_surface(self.image, +90)
						self.direction = self.Direction.Right
					elif(column[1] == "U"):
						if(self.direction == self.Direction.Right):
							self.image = rotate_surface(self.image, +90)
						if(self.direction == self.Direction.Left):
							self.image = rotate_surface(self.image, -90)
						self.direction = self.Direction.Up
					elif(column[1] == "L"):
						if(self.direction == self.Direction.Up):
							self.image = rotate_surface(self.image, +90)
						if(self.direction == self.Direction.Down):
							self.image = rotate_surface(self.image, -90)
						self.direction = self.Direction.Left
					elif(column[1] == "D"):
						if(self.direction == self.Direction.Right):
							self.image = rotate_surface(self.image, -90)
						if(self.direction == self.Direction.Left):
							self.image = rotate_surface(self.image, +90)
						self.direction = self.Direction.Down

