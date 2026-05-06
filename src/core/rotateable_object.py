from typing import override
import pygame
from pygame.math import Vector2
from core.image import load_image
from core.guiobject import ImageObject
from pygame_core.unity.components.sprite_renderer2d import SpriteRenderer2D


class RotateableObject(ImageObject):
	def __init__(self, image_path: str, pos: Vector2):
		ImageObject.__init__(self, image_path, pos)
		self.is_rotated = False
		self.position = Vector2(pos)
		self.rect.center = pos

	def load_image(self, image_path: str) -> None:
		self.image = load_image(image_path)
		self.rect.size =  self.image.get_size()
		self.rect.center = self.position
		self.is_rotated = False

	def rotate_to_angle(self, angle: float) -> None:
		self.rotated_image = pygame.transform.rotate(self.get_component(SpriteRenderer2D).image, -angle - 90)
		self.rect.size =  self.rotated_image.get_size()
		self.rect.center = self.position
		self.is_rotated = True

	@override
	def draw(self, surface: pygame.Surface) -> None:
		surface.blit(self.rotated_image if self.is_rotated else self.image, self.rect)