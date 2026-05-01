import pygame
from pygame.math import Vector2
from pygame_core.color import White

from core.game_object import GameObject
from core.guiobject import GuiObject
from game_state import GameState, TowerConfig


class BaseTower(GameObject):
    """Abstract base for all towers.

    Owns the shared upgrade/sell mechanics and exposes properties for stats so
    subclasses never read directly from game — they use TowerConfig (DIP).
    Concrete behaviour (update_and_draw / work) is left to subclasses (OCP/LSP).
    """

    def __init__(self, tower_type: int, row: int, col: int,
                 config: TowerConfig, assets) -> None:
        asset_key = f"tower_{tower_type}_lvl1"  # tower_1_lvl1, tower_2_lvl1, etc.
        super().__init__(
            assets.image_path(asset_key),
            (col * 64 + 32, row * 64 + 32),
        )
        self._assets = assets
        self._price_font = pygame.font.SysFont("ComicSansMs", 15)
        self.tower_type  = tower_type
        self.row         = row
        self.col         = col
        self.level       = 1
        self._config     = config
        self.last_reload_time = 0
        self.bullets: list = []
        self.now: int = 0

    # ── config-derived properties (no direct game coupling) ───────────────────

    @property
    def range(self) -> int:
        return self._config.ranges[self.tower_type - 1][self.level - 1]

    @property
    def damage(self) -> int:
        return self._config.damages[self.tower_type - 1][self.level - 1]

    @property
    def speed(self) -> int:
        return self._config.speeds[self.tower_type - 1][self.level - 1]

    @property
    def max_level(self) -> int:
        return self._config.max_levels[self.tower_type - 1]

    @property
    def sell_price(self) -> int:
        return self._config.prices[self.tower_type - 1][self.level - 1]

    @property
    def upgrade_price(self) -> int:
        return self._config.prices[self.tower_type - 1][self.level]

    @property
    def buy_price(self) -> int:
        return self._config.prices[self.tower_type - 1][0]

    def is_max_level(self) -> bool:
        return self.level >= self.max_level

    # ── shared actions ────────────────────────────────────────────────────────

    def upgrade(self, mouse_pos: tuple, game_state: GameState, camera) -> None:
        if self.is_max_level() or game_state.money < self.upgrade_price:
            return
        ox, oy = camera.rect.topleft
        hit = pygame.Rect(
            self.position.x - 72 + ox,
            self.position.y - self.range - 74 + oy,
            50, 50,
        )
        if not hit.collidepoint(mouse_pos):
            return
        self.level += 1
        game_state.decrease_money(self.upgrade_price)
        game_state.selected_tower = self

    def sell(self, mouse_pos: tuple, game_state: GameState, towers: list, camera) -> None:
        if game_state.selected_tower != self:
            return
        ox, oy = camera.rect.topleft
        hit = pygame.Rect(
            self.position.x + 40 + ox,
            self.position.y - self.range - 54 + oy,
            50, 50,
        )
        if hit.collidepoint(mouse_pos):
            game_state.increase_money(self.sell_price)
            towers.remove(self)

    # ── shared rendering helpers ──────────────────────────────────────────────

    def draw_range(self, surface: pygame.Surface, offset: tuple = (0, 0)) -> None:
        ox, oy = offset
        surf = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA, 32)
        pygame.draw.circle(surf, (128, 128, 128, 120), (int(self.range), int(self.range)), int(self.range), 0)
        pygame.draw.circle(surf, (0, 200, 0, 120),     (int(self.range), int(self.range)), int(self.range), 2)
        surface.blit(surf, (self.position.x - self.range + ox, self.position.y - self.range + oy))

    def draw_selected_ui(self, surface: pygame.Surface, game_state: GameState, camera) -> None:
        ox, oy   = camera.rect.topleft
        draw_pos = self.position + Vector2(ox, oy)

        sell_btn = GuiObject("", draw_pos + Vector2(20, -110), (50, 50),
                             self._assets.image_path("btn_sell"))
        upgrade_btn = GuiObject("", draw_pos + Vector2(-55, -105), (50, 50),
                                self._assets.image_path("btn_upgrade"))
        max_btn = GuiObject("", draw_pos + Vector2(-60, -85), (50, 25),
                            self._assets.image_path("btn_max"))

        sell_text = self._price_font.render(str(self.sell_price) + " $", 2, White)

        if self.is_max_level():
            max_btn.draw(surface)
        else:
            upgrade_text = self._price_font.render(str(self.upgrade_price) + " $", 2, White)
            surface.blit(upgrade_text, draw_pos + Vector2(-50, -60))
            upgrade_btn.draw(surface)

        surface.blit(sell_text, draw_pos + Vector2(30, -60))
        sell_btn.draw(surface)

    # ── polymorphic interface ─────────────────────────────────────────────────

    def should_remove(self) -> bool:
        """Return True when this tower should be removed from the world."""
        return False

    def get_blocking_position(self) -> tuple | None:
        """Grid cell (row, col) that this tower occupies, or None for planes."""
        return (self.row, self.col)

    def update(self, game_state: GameState, enemies: list) -> None:
        raise NotImplementedError

    def draw(self, game_state: GameState, camera, surface: pygame.Surface) -> None:
        raise NotImplementedError

    def work(self, enemies: list, is_started: bool) -> None:
        raise NotImplementedError