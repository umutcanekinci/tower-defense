import pygame

class Text(object):
    def __init__(self, text, font : pygame.font.SysFont, color, position) -> None:
        self._text, self._font, self._color = text, font, color
        self.position = (self.x, self.y) = position
        self.update_object()
    
    def set(self, text):
        self._text = text
        self.update_object()

    def set_color(self, color):
        self._color = color
        self.update_object()

    def update_object(self):
        self._text_object = self._font.render(self._text, 2, self._color)

    def draw(self, surface: pygame.Surface):
        surface.blit(self._text_object, self.position)