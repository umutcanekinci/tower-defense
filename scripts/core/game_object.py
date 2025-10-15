from typing import override
from pygame.math import Vector2
from core.image import load_image
import pygame
from core.gui_object import ImageObject

class GameObject(ImageObject):
	def __init__(self, image_path: str, pos: Vector2):
		super().__init__(image_path, pos)
		self.is_rotated = False
		self.pos = Vector2(pos)
		self.rect.center = self.pos

	def load_image(self, image_path: str) -> None:
		self.image = load_image(image_path)
		self.rect = self.image.get_rect(center = self.pos)
		self.is_rotated = False

	def rotate_to_angle(self, angle: float) -> None:
		self.rotated_image = pygame.transform.rotate(self.image, -angle - 90)
		self.rect = self.rotated_image.get_rect(center = self.pos)
		self.is_rotated = True

	@override
	def draw(self, surface: pygame.Surface) -> None:
		surface.blit(self.rotated_image if self.is_rotated else self.image, self.rect)