import enum
from sre_parse import State
import pygame
from core.image import load_image, scale_surface

class ImageObject():
	def __init__(self, path: str, pos: tuple[int, int], size: tuple[int, int] = (None, None), extension: str = ".png") -> None:
		self.image = scale_surface(load_image(path, extension), size) if size != (None, None) else load_image(path, extension)
		self.rect = self.image.get_rect(topleft = pos)

	def is_mouse_on(self, mouse_pos) -> bool:		
		return mouse_pos != None and self.rect.collidepoint(mouse_pos)

	def is_clicked(self, event, mouse_pos) -> bool:
		return self.is_mouse_on(mouse_pos) and event.type == pygame.MOUSEBUTTONUP

	def draw(self, surface: pygame.Surface) -> None:
		surface.blit(self.image, self.rect)

class GUI_Object(object):
	class STATE(enum.Enum):
		NORMAL = 0
		OVER = 1

	def __init__(self, surface_size = "", pos = ("CENTER", "CENTER"), size =(None, None), image_path = None, image_path2 = None, extension1 = ".png", extension2 = ".png") -> None:	
		self.state = self.STATE.NORMAL
		self.images = {}

		x = (surface_size[0] - size[0]) / 2 if pos[0] == "CENTER" else pos[0]
		y = (surface_size[1] - size[1]) / 2 if pos[1] == "CENTER" else pos[1]

		if image_path != None:
			self.images[self.STATE.NORMAL] = ImageObject(image_path, (x, y), size, extension1)
		self.images[self.STATE.OVER] = ImageObject(image_path2, (x, y), size, extension2) if image_path2 != None else self.images[self.STATE.NORMAL]

	def is_mouse_on(self, mouse_pos) -> bool:
		return self.images[self.state].is_mouse_on(mouse_pos)
	
	def is_clicked(self, event, mouse_pos) -> bool:
		return self.images[self.state].is_clicked(event, mouse_pos)

	def update(self, mouse_pos: tuple) -> None:
		self.state = self.STATE.OVER if self.images[self.state].is_mouse_on(mouse_pos) else self.STATE.NORMAL

	def draw(self, surface: pygame.Surface) -> None:
		self.images[self.state].draw(surface)

	def get_info(self) -> tuple:
		return "GUI Object Info:", {
			"state": self.state.name,
			"pos": self.images[self.state].rect.topleft,
			"size": self.images[self.state].rect.size
		}
