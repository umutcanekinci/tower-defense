import pygame
from pygame.math import Vector2
from game_math import angle_between_points
from game_object import GameObject

class Projectile(GameObject):
	EXPLODE_DISTANCE = 30
	BULLET_SPEED = 1/5

	def __init__(self, target, tower) -> None:
		super().__init__(tower.pos)
		self.load_image("bullets/"+str(tower.type)+"L"+str(tower.level)+".png")
		self.type, self.target, self.tower, self.damage, self.speed = [tower.type, tower.level], target, tower, tower.damage, Vector2(0, -2)

	def update(self, game) -> None:
		if game.enemies == []:
			return self.explode(game)
		
		for enemy in game.enemies:
			if enemy.id == self.target.id:
				self.target = enemy

		self.rotate_to_angle(angle_between_points(self.pos, self.target.pos))

		distance = self.target.pos - self.pos

		if self.is_in_explode_range(distance):
			self.explode(game)
			return

		self.move(distance, game)

	def is_in_explode_range(self, distance: Vector2) -> bool:
		return distance.length() <= self.EXPLODE_DISTANCE

	def explode(self, game) -> None:
		self.tower.bullets.remove(self)
		self.target.decrease_hp(self.damage, game)

	def move(self, distance: Vector2, game) -> None:
		self.velocity = distance.normalize() * self.BULLET_SPEED * game.speed
		self.pos += self.velocity