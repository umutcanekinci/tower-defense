import pygame

class Text(object):
    def __init__(self, text, font : pygame.font.SysFont, color, position) -> None:
        self.text, self.font, self.color = text, font, color
        self.position = (self.x, self.y) = position
<<<<<<< HEAD
        self.UpdateTextObject()
    
    def ChangeText(self, text):
        self.text = text
        self.UpdateTextObject()

    def ChangeColor(self, color):
        self.color = color
        self.UpdateTextObject()

    def UpdateTextObject(self):
        self.textObject = self.font.render(self.text, 2, self.color)

    def Draw(self, surface: pygame.Surface):
=======
        self.update_object()
    
    def set(self, text):
        self.text = text
        self.update_object()

    def set_color(self, color):
        self.color = color
        self.update_object()

    def update_object(self):
        self.textObject = self.font.render(self.text, 2, self.color)

    def draw(self, surface: pygame.Surface):
>>>>>>> master
        surface.blit(self.textObject, self.position)