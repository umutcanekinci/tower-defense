from dataclasses import dataclass
from typing import Callable


@dataclass
class TowerConfig:
    """All per-type, per-level tower data.

    prices[type-1][level-1] doubles as the sell value at that level and as
    the buy/upgrade cost to *reach* that level (same index scheme used by the
    original code throughout).
    """
    prices:     list[list[int]]
    max_levels: list[int]
    ranges:     list[list[int]]
    damages:    list[list[int]]
    speeds:     list[list[int]]


class GameState:
    """Pure game state — no pygame, no rendering, no game-object lists."""

    def __init__(self, start_money: int, start_lives: int) -> None:
        self.money:          int  = start_money
        self.lives:          int  = start_lives
        self.level:          int  = 1
        self.speed:          int  = 1
        self.is_started:     bool = False
        self.selected_tower        = None
        self.plane_level:    int  = 1

        self._money_cbs: list[Callable[[int], None]] = []
        self._level_cbs: list[Callable[[int], None]] = []

    # ── listeners ────────────────────────────────────────────────────────────

    def add_money_listener(self, cb: Callable[[int], None]) -> None:
        self._money_cbs.append(cb)

    def add_level_listener(self, cb: Callable[[int], None]) -> None:
        self._level_cbs.append(cb)

    # ── mutations ─────────────────────────────────────────────────────────────

    def increase_money(self, amount: int) -> None:
        self.money += amount
        for cb in self._money_cbs:
            cb(self.money)

    def decrease_money(self, amount: int) -> None:
        self.money -= amount
        for cb in self._money_cbs:
            cb(self.money)

    def advance_level(self) -> None:
        self.level += 1
        for cb in self._level_cbs:
            cb(self.level)