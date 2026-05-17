from typing import override
import pygame
from pygame.math import Vector2

from core.game_object.image_object import ImageObject, PathLike
from pygame_core.asset_path import ImagePath
from pygame_core.unity.components.sprite_renderer2d import SpriteRenderer2D


class RotateableObject(ImageObject):
	def __init__(self, image_path: ImagePath, pos: Vector2):
		self.position = Vector2(pos)  # must precede super() — ImageObject.__init__ triggers self.load(), which reads self.position
		super().__init__(image_path, pos)
		self.rect.center = pos
		self.rotated_image = None
		self.is_rotated = False

	@override
	def load(self, path: PathLike, size: tuple[int, int] = (0, 0), nine_slice: int = 0) -> None:
		super().load(path, size, nine_slice)
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