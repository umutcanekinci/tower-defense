import pygame

def load_image(path):
    if path == None:
        return None
    return pygame.image.load("images/" + path).convert_alpha()

def rotate_image(image, angle):
    return pygame.transform.rotate(image, angle)

def scale_image(image, size):
    return pygame.transform.scale(image, size)