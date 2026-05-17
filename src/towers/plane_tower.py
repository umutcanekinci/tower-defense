import pygame

from util.constants import TILE_SIZE
from domain.game_state import GameState, TowerConfig
from towers.base_tower import BaseTower

MAP_COLS = 22


class PlaneTower(BaseTower):
    REMOVE_X = MAP_COLS * TILE_SIZE

    def __init__(self, tower_type: int, row: int, col: int, config: TowerConfig, assets) -> None:
        super().__init__(tower_type, row, col, config, assets)

    def update(self, game_state: GameState, enemies: list) -> None:
        new_level = game_state.plane_level
        if new_level != self.level:
            self.level = new_level
            self.load(self.assets.image_path(f"tower_{self.tower_type}_lvl{self.level}"))
        if game_state.is_started and self.position.x <= self.REMOVE_X:
            self.position.x += self.speed
            self.rect.center = self.position

    def draw(self, game_state: GameState, camera, surface: pygame.Surface) -> None:
        shadow = self.assets.get_image(f"tower_{self.tower_type}_shadow_lvl{self.level}")
        scaled_shadow = camera.scale_image(shadow)
        shadow_screen = camera.world_to_screen((self.position.x - 20, self.position.y + 20))
        surface.blit(scaled_shadow, shadow_screen)

        if game_state.selected_tower is self:
            self.draw_range(surface, camera)

        camera.draw(surface, self)

    def work(self, enemies: list, is_started: bool) -> None:
        pass  # Planes are purely cosmetic; they do not attack

    def should_remove(self) -> bool:
        return self.position.x > self.REMOVE_X

    def get_blocking_position(self) -> tuple | None:
        return None  # Planes fly over the map and never block a build tile
