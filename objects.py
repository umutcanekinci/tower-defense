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
