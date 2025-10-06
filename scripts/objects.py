<<<<<<< HEAD
### IMPORTING THE PACKAGES ########################################################################################################################################################
import pygame
### OBJECT CLASS ##################################################################################################################################################################
class Object(object):
	def __init__(self, surfaceSize = "", position = ("CENTER", "CENTER"), size =(None, None), ImagePath = None, ImagePath2 = None, extension1 = ".png", extension2 = ".png"):		
		self.X, self.Y, self.Width, self.Height, self.ImagePath, self.ImagePath2, self.surfaceSize, self.extension1, self.extension2 = position[0], position[1], size[0], size[1], ImagePath, ImagePath2, surfaceSize, extension1, extension2
		if self.ImagePath != None:
			self.ImagePath = list(ImagePath)
		if self.ImagePath2 != None:			
			self.ImagePath2 = list(ImagePath2)
		self.Image1 = pygame.transform.scale(pygame.image.load("images/" + ImagePath[0] + "/" + ImagePath[1] + self.extension1).convert_alpha(), (self.Width, self.Height))
		if ImagePath2 != None:
			self.Image2 = pygame.transform.scale(pygame.image.load("images/" + ImagePath2[0] + "/" + ImagePath2[1] + self.extension2).convert_alpha(), (self.Width, self.Height))
		if self.X == "CENTER":
			self.X = (surfaceSize[0] - self.Width) / 2
		if self.Y == "CENTER":
			self.Y = (surfaceSize[1] - self.Height) / 2

	def MouseOnObject(self, MousePosition):
		if MousePosition != None and pygame.Rect(self.X, self.Y, self.Width, self.Height).collidepoint(MousePosition):
			return True
		return False

	def Click(self, Event, MousePosition):
		if self.MouseOnObject(MousePosition) and Event.type == pygame.MOUSEBUTTONUP:
			return True
		return False

	def Draw(self, Window, MousePosition = None):
		self = Object(self.surfaceSize, (self.X, self.Y), (self.Width, self.Height), self.ImagePath, self.ImagePath2, self.extension1, self.extension2)
		if self.MouseOnObject(MousePosition) and self.ImagePath2 != None:
			Window.blit(self.Image2, (self.X, self.Y))		
		else:
			Window.blit(self.Image1, (self.X, self.Y))
### END OF CLASS ##################################################################################################################################################################
=======
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
>>>>>>> master
