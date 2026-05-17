from typing import Union
import os
import pygame
from pygame_core.asset_path import ImagePath
from pygame_core.image import load_image
from pygame_core.unity.gameobject import GameObject
from pygame_core.unity.components.sprite_renderer2d import SpriteRenderer2D
from pygame_core.utils import MouseInteractive

PathLike = Union[str, ImagePath, os.PathLike]

class ImageObject(GameObject, MouseInteractive):
	def __init__(self, path: PathLike, pos: tuple[int, int],
	             size: tuple[int, int] = (0, 0),
				 nine_slice: int = 0) -> None:
		super().__init__()

		self.add_component(SpriteRenderer2D)
		self.load(path, size, nine_slice)
		self.rect.topleft = pos

	def load(self, path: PathLike, size: tuple[int, int] = (0, 0), nine_slice: int = 0) -> None:
		image = load_image(path, size, nine_slice)
		self.get_component(SpriteRenderer2D).set_image(image)
		self.rect.size = image.get_size()
