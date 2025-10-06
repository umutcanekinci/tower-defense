import pygame
from image import load_image, scale_image

class GUI_Object(object):
	def __init__(self, surface_size = "", pos = ("CENTER", "CENTER"), size =(None, None), image_path = None, image_path2 = None, extension1 = ".png", extension2 = ".png") -> None:
		self.width, self.height, self.image_path, self.image_path2, self.surfaceSize, self.extension1, self.extension2 = size[0], size[1], image_path, image_path2, surface_size, extension1, extension2
		self.x = (surface_size[0] - self.width) / 2 if pos[0] == "CENTER" else pos[0]
		self.y = (surface_size[1] - self.height) / 2 if pos[1] == "CENTER" else pos[1]
		
		if self.image_path != None:
			self.image_path = list(image_path)

		if self.image_path2 != None:
			self.image_path2 = list(image_path2)

		self.image1 = scale_image(load_image(self.image_path[0] + "/" + self.image_path[1] + self.extension1), (self.width, self.height))

		if self.image_path2 != None:
			self.image2 = scale_image(load_image(self.image_path2[0] + "/" + self.image_path2[1] + self.extension2), (self.width, self.height))

	def is_mouse_on(self, mouse_pos) -> bool:
		return mouse_pos != None and pygame.Rect(self.x, self.y, self.width, self.height).collidepoint(mouse_pos)

	def is_mouse_click(self, event, mouse_pos) -> bool:
		return self.is_mouse_on(mouse_pos) and event.type == pygame.MOUSEBUTTONUP

	def draw(self, window, mouse_pos = None) -> None:
		image = self.image2 if self.is_mouse_on(mouse_pos) and self.image_path2 != None else self.image1
		window.blit(image, (self.x, self.y))
