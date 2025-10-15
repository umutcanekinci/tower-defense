import pygame

class Mouse:
    def __init__(self, tile_size=None) -> None:
        self.pos = (0, 0)
        self.tile_size = tile_size

        if self.tile_size:
            self.tile_pos = (0, 0)

    def update(self) -> None:
        self.pos = pygame.mouse.get_pos()

        if self.tile_size:
            self.tile_pos = (self.pos[0] // self.tile_size, self.pos[1] // self.tile_size)

    def get_info(self):
        return "Mouse Info:", {
            "pos": self.pos,
            "tile_pos": self.tile_pos if self.tile_size else None
        }