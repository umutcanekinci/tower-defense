from pygame.math import Vector2
from image import load_image
import pygame

class GameObject():
	def __init__(self, pos: Vector2):
		self.pos = Vector2(pos)
		self.is_rotated = False

	def load_image(self, path: str) -> None:
		self.image = load_image(path)
		self.rect = self.image.get_rect(center = self.pos)

	def rotate_to_angle(self, angle: float) -> None:
		self.rotated_image = pygame.transform.rotate(self.image, -angle - 90)
		self.rect = self.rotated_image.get_rect(center = self.pos)
		self.is_rotated = True

	def draw(self, surface: pygame.Surface) -> None:
		surface.blit(self.rotated_image if self.is_rotated else self.image, self.rect)