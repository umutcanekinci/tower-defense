from typing import Union
import os
import pygame
from pygame_core.asset_path import ImagePath
from pygame_core.image import load_image
from pygame_core.utils import MouseInteractive

from core.image import scale_surface

PathLike = Union[str, ImagePath, os.PathLike]

class ImageObject(MouseInteractive):
	def __init__(self, path: PathLike, pos: tuple[int, int],
	             size: tuple[int, int] = (0, 0)) -> None:
		loaded = load_image(path)
		self.image = scale_surface(loaded, size) if size != (0, 0) else loaded
		self.rect = self.image.get_rect(topleft=pos)

	def draw(self, surface: pygame.Surface) -> None:
		surface.blit(self.image, self.rect)
