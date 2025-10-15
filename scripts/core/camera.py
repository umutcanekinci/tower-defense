import pygame
from core.image import scale_surface_by

EDGE_SCROLL_ZONE = 30  # pixels from edge to start scrolling
CAMERA_SPEED = 10      # pixels per frame

class Camera():
    def __init__(self, rect):
        self.rect = rect
        self.scale = 1

    def draw(self, surface, entity):
        scaled_image, scaled_rect = self.apply_scale_and_position(entity)
        surface.blit(scaled_image, scaled_rect)

    def apply_scale_and_position(self, entity):
        scaled_image = self.apply_scale(entity)
        scaled_rect = scaled_image.get_rect(center=entity.rect.center)
        return scaled_image, self.apply_position(scaled_rect)

    def apply_position(self, rect):
        return rect.move(self.rect.topleft)

    def apply_scale(self, entity):
        return scale_surface_by(entity.image, self.scale)

    def update(self, target=None):
        # Optionally keep this for centering on a target
        pass

    def update_with_mouse(self, mouse_pos):
        mx, my = mouse_pos
        x, y = self.rect.topleft

        # Move right
        if mx > self.rect.width - EDGE_SCROLL_ZONE:
            x -= CAMERA_SPEED
        # Move left
        if mx < EDGE_SCROLL_ZONE:
            x += CAMERA_SPEED
        # Move down
        if my > self.rect.height - EDGE_SCROLL_ZONE:
            y -= CAMERA_SPEED
        # Move up
        if my < EDGE_SCROLL_ZONE:
            y += CAMERA_SPEED

        # Clamp camera position
        # x = min(0, x)
        # y = min(0, y)
        # x = max(-(self.width - screen_width), x)
        # y = max(-(self.height - screen_height), y)

        self.rect.topleft = (x, y)

    def get_info(self):
        return "Camera Info:", {
            "rect": self.rect,
            "scale": self.scale
        }