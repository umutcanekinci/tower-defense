from typing import Union
import os
import enum
import pygame
from pygame_core.asset_path import ImagePath
from pygame_core.utils import Centerable
from core.image_object import ImageObject

PathLike = Union[str, ImagePath, os.PathLike]

class GuiObject(Centerable):
	class STATE(enum.Enum):
		NORMAL = 0
		OVER = 1

	def __init__(self, surface_size: tuple[int, int] = (0, 0),
	             pos=("CENTER", "CENTER"),
	             size=(None, None),
	             image_path: PathLike = None,
	             image_path2: PathLike = None) -> None:
		self.state = self.STATE.NORMAL
		self.images = {}
		self.image_path = image_path
		pos = self.resolve_pos(pos, surface_size, size)

		if image_path is not None:
			self.images[self.STATE.NORMAL] = ImageObject(image_path, pos, size)
		self.images[self.STATE.OVER] = (
			ImageObject(image_path2, pos, size)
			if image_path2 is not None
			else self.images[self.STATE.NORMAL]
		)
		
	def is_mouse_over(self, mouse_pos) -> bool:
		return self.images[self.state].is_mouse_over(mouse_pos)
	
	def is_clicked(self, event, mouse_pos) -> bool:
		return self.images[self.state].is_clicked(event, mouse_pos)

	def handle_event(self, event, mouse_pos: tuple) -> None:
		self.state = self.STATE.OVER if self.images[self.state].is_mouse_over(mouse_pos) else self.STATE.NORMAL

	def draw(self, surface: pygame.Surface) -> None:
		self.images[self.state].draw(surface)

	def get_info(self) -> tuple:
		return "GUI Object Info:", {
			"state": self.state.name,
			"pos": self.images[self.state].rect.topleft,
			"size": self.images[self.state].rect.size
		}
