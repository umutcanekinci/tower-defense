import pygame

from enemies import Enemy
from game_state import GameState


class WaveManager:
    """Handles enemy spawning and level-transition timing.

    Extracted from the monolithic Game class to satisfy SRP: the only job of
    this class is to know *when* and *where* to spawn enemies and when to
    advance to the next level.
    """

    SPAWN_INTERVAL_MS  = 1000
    LEVEL_END_DELAY_MS = 5000

    def __init__(self, spawn_x: int, spawn_y: int) -> None:
        self._spawn_x = spawn_x
        self._spawn_y = spawn_y
        self._count_this_level: int       = 0
        self._count_all_time:   int       = 0
        self._last_spawn_time:  int       = 0
        self._level_finish_time: int | None = None

    def update(self, enemies: list, game_state: GameState) -> None:
        if not game_state.is_started:
            return

        now   = pygame.time.get_ticks()
        total = game_state.level * 10

        if self._count_this_level < total:
            if self._count_this_level == total - 1:
                self._level_finish_time = now
            if now - self._last_spawn_time > self.SPAWN_INTERVAL_MS:
                self._count_this_level += 1
                self._count_all_time   += 1
                enemies.append(Enemy(
                    self._count_all_time,
                    game_state.level,
                    self._spawn_x,
                    self._spawn_y,
                ))
                self._last_spawn_time = now

        elif self._level_finish_time and now - self._level_finish_time > self.LEVEL_END_DELAY_MS:
            game_state.advance_level()
            self._count_this_level  = 0
            self._level_finish_time = None