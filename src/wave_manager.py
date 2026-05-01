import pygame

from config_loader import load_wave_compositions
from enemy import Enemy
from game_state import GameState

WAVE_COMPOSITIONS: dict[int, list[tuple[int, int]]] = load_wave_compositions()


class WaveManager:
    """Handles enemy spawning and wave-transition timing."""

    SPAWN_INTERVAL_MS  = 1000
    LEVEL_END_DELAY_MS = 5000

    def __init__(self, spawn_x: int, spawn_y: int) -> None:
        self._spawn_x = spawn_x
        self._spawn_y = spawn_y
        self._count_all_time:    int       = 0
        self._last_spawn_time:   int       = 0
        self._level_finish_time: int | None = None
        self._current_level:     int       = -1
        self._spawn_queue:       list[int] = []  # flattened list of enemy types
        self._queue_index:       int       = 0

    def _build_queue(self, level: int) -> None:
        composition = WAVE_COMPOSITIONS.get(level) or self._composition_for(level)
        self._spawn_queue = [
            enemy_type
            for enemy_type, count in composition
            for _ in range(count)
        ]
        self._queue_index    = 0
        self._level_finish_time = None

    def _composition_for(self, level: int) -> list[tuple[int, int]]:
        extra = level - 10
        return [(3, max(0, 4 - extra)), (4, 10 + extra * 3)]

    def update(self, enemies: list, game_state: GameState) -> None:
        if not game_state.is_started:
            return

        if game_state.level != self._current_level:
            self._current_level = game_state.level
            self._build_queue(game_state.level)

        now = pygame.time.get_ticks()

        if self._queue_index < len(self._spawn_queue):
            if now - self._last_spawn_time >= self.SPAWN_INTERVAL_MS:
                enemy_type = self._spawn_queue[self._queue_index]
                self._queue_index += 1
                self._count_all_time += 1
                enemies.append(Enemy(
                    self._count_all_time,
                    enemy_type,
                    game_state.level,
                    self._spawn_x,
                    self._spawn_y,
                ))
                self._last_spawn_time = now
                if self._queue_index == len(self._spawn_queue):
                    self._level_finish_time = now

        elif (
            self._level_finish_time
            and now - self._level_finish_time >= self.LEVEL_END_DELAY_MS
            and not enemies
        ):
            game_state.advance_level()