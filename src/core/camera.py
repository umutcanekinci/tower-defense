import pygame
from core.image import scale_surface_by

EDGE_SCROLL_ZONE = 30  # pixels from edge to start scrolling
CAMERA_SPEED = 10      # pixels per frame

class Camera():
    def __init__(self, rect, map_width=None, map_height=None):
        self.rect = rect
        self.scale = 1
        self.min_x = -(map_width - rect.width) if map_width and map_width > rect.width else 0
        self.min_y = -(map_height - rect.height) if map_height and map_height > rect.height else 0

    def draw(self, surface, entity):
        image = entity.rotated_image if getattr(entity, 'is_rotated', False) else entity.image
        scaled_image = scale_surface_by(image, self.scale)
        scaled_rect = scaled_image.get_rect(center=entity.rect.center)
        surface.blit(scaled_image, self.apply_position(scaled_rect))

    def apply_position(self, rect):
        return rect.move(self.rect.topleft)

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

        x = max(self.min_x, min(0, x))
        y = max(self.min_y, min(0, y))

        self.rect.topleft = (x, y)

    def get_info(self):
        return "Camera Info:", {
            "rect": self.rect,
            "scale": self.scale
        }