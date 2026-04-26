import pygame

from core.game_object import GameObject
from core.image import load_image
from core.math import angle_between_delta
from game_state import GameState, TowerConfig
from projectile import Projectile
from pygame_core.asset_path import ImagePath
from towers.base_tower import BaseTower


class GroundTower(BaseTower):
    """Stationary tower that aims at the nearest enemy and fires projectiles.

    Covers tower types 1, 2, and 3 — all share the same behavioural contract so
    Liskov substitution holds: a GroundTower can replace any other GroundTower
    without callers noticing.
    """

    def __init__(self, tower_type: int, row: int, col: int, config: TowerConfig, assets) -> None:
        super().__init__(tower_type, row, col, config, assets)
        self.platform = GameObject(
            str(ImagePath("tower" + str(tower_type) + "platform1", folder="towers")),
            self.position,
        )

    def update_and_draw(self, game_state: GameState, enemies: list, camera, surface: pygame.Surface) -> None:
        self.now = pygame.time.get_ticks()

        # Type-2 towers show a reload animation: swap to the "charging" sprite
        # between shots, then back to idle once the cooldown is almost done.
        if self.tower_type == 2:
            self.image = load_image("towers/tower" + str(self.tower_type) + "L" + str(self.level) + "_")
            if self.now - self.last_reload_time > self.speed - 1000:
                self.image = load_image("towers/tower" + str(self.tower_type) + "L" + str(self.level))

        cam_offset = camera.rect.topleft
        camera.draw(surface, self.platform)

        if game_state.selected_tower is self:
            self.draw_range(surface, cam_offset)
            self.draw_selected_ui(surface, game_state, camera)

        self.work(enemies, game_state.is_started)
        camera.draw(surface, self)

    def work(self, enemies: list, is_started: bool) -> None:
        if not is_started or not enemies:
            return

        distances       = [enemy.position - self.position for enemy in enemies]
        lengths         = [d.length() for d in distances]
        nearest_dist    = min(lengths)
        nearest_idx     = lengths.index(nearest_dist)

        if nearest_dist > self.range:
            return

        self.rotate_to_angle(angle_between_delta(distances[nearest_idx]))

        if self._is_attack_ready():
            self._shoot(enemies[nearest_idx])

    # ── private ───────────────────────────────────────────────────────────────

    def _is_attack_ready(self) -> bool:
        self.now = pygame.time.get_ticks()
        return self.now - self.last_reload_time > self.speed

    def _shoot(self, target) -> None:
        self.bullets.append(Projectile(target, self))
        self.last_reload_time = self.now
