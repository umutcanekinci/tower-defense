import pygame

from core.image import load_image
from game_state import GameState, TowerConfig
from towers.base_tower import BaseTower


class PlaneTower(BaseTower):
    """Plane that flies across the map — does not shoot or occupy a tile.

    Because planes have a completely different lifecycle from ground towers, they
    are a separate class rather than a conditional branch inside Tower.  This
    removes all the `if self.is_plane()` guards that broke Liskov substitution
    in the original design.
    """

    REMOVE_X = 1125

    def __init__(self, tower_type: int, row: int, col: int, config: TowerConfig) -> None:
        super().__init__(tower_type, row, col, config)

    def update_and_draw(self, game_state: GameState, enemies: list, camera, surface: pygame.Surface) -> None:
        self.level = game_state.plane_level
        ox, oy    = camera.rect.topleft
        shadow    = load_image("towers/tower" + str(self.tower_type) + "shadow" + str(self.level))

        if game_state.is_started and self.position.x <= self.REMOVE_X:
            self.position.x += self.speed

        surface.blit(shadow, (self.position.x - 20 + ox, self.position.y + 20 + oy))

        if game_state.selected_tower is self:
            self.draw_range(surface, camera.rect.topleft)

        camera.draw(surface, self)

    def work(self, enemies: list, is_started: bool) -> None:
        pass  # Planes are purely cosmetic; they do not attack

    def should_remove(self) -> bool:
        return self.position.x > self.REMOVE_X

    def get_blocking_position(self) -> tuple | None:
        return None  # Planes fly over the map and never block a build tile
