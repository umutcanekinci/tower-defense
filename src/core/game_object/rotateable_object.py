from typing import override
import pygame
from pygame.math import Vector2

from core.game_object.image_object import ImageObject, PathLike
from core.math import angle_between_delta
from pygame_core.asset_path import ImagePath
from pygame_core.unity.components.sprite_renderer2d import SpriteRenderer2D

# Angle (atan2 / screen-coord convention) the sprite's "forward" points in its source PNG.
FACE_RIGHT = 0
FACE_DOWN  = 90
FACE_LEFT  = 180
FACE_UP    = -90


class RotateableObject(ImageObject):
	def __init__(self, image_path: ImagePath, pos: Vector2, sprite_orientation: float = FACE_RIGHT):
		self.position = Vector2(pos)  # must precede super() — ImageObject.__init__ triggers self.load(), which reads self.position
		super().__init__(image_path, pos)
		self.rect.center = pos
		self.rotated_image = None
		self.is_rotated = False
		self.sprite_orientation = sprite_orientation

	@override
	def load(self, path: PathLike, size: tuple[int, int] = (0, 0), nine_slice: int = 0) -> None:
		super().load(path, size, nine_slice)
		self.rect.center = self.position
		self.is_rotated = False

	def rotate_to_delta(self, delta: Vector2) -> None:
		if delta.length_squared() == 0: return

		self.rotate_to_angle(angle_between_delta(delta))

	def rotate_to_angle(self, angle: float) -> None:
		rotation = self.sprite_orientation - angle
		self.rotated_image = pygame.transform.rotate(self.get_component(SpriteRenderer2D).image, rotation)
		self.rect.size =  self.rotated_image.get_size()
		self.rect.center = self.position
		self.is_rotated = True

	@override
	def draw(self, surface: pygame.Surface) -> None:
		surface.blit(self.rotated_image if self.is_rotated else self.image, self.rect)