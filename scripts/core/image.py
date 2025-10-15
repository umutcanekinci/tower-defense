from email.mime import image
import pygame

def load_image(path, extension=".png"):
    if path == None:
        return None
    return pygame.image.load("images/" + path + extension).convert_alpha()

def rotate_surface(image, angle):
    return pygame.transform.rotate(image, angle)

def scale_surface(image, size):
    return pygame.transform.scale(image, size)

def scale_surface_by(surface: pygame.Surface, factor: tuple[float, float] | float) -> pygame.Surface:
    if isinstance(factor, float) or isinstance(factor, int):
        factor = (factor, factor)

    width  = int(surface.get_width()  * factor[0])
    height = int(surface.get_height() * factor[1])
    return scale_surface(surface, (width, height))
