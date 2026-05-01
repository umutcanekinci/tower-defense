from typing import TYPE_CHECKING

import pygame
from pygame.math import Vector2

from core.game_object import GameObject
from core.math import angle_between_points
from pygame_core.asset_path import ImagePath

if TYPE_CHECKING:
    from core.protocols import IGameContext


class Projectile(GameObject):
    EXPLODE_DISTANCE = 30
    BULLET_SPEED     = 1 / 2

    def __init__(self, target, tower) -> None:
        super().__init__(
            ImagePath(str(tower.tower_type) + "L" + str(tower.level), folder="bullets"),
            tower.position,
        )
        self.tower_type = tower.tower_type
        self.target     = target
        self.tower      = tower
        self.damage     = tower.damage
        self._velocity  = Vector2(0, 0)

    def update(self, ctx: "IGameContext") -> None:
        if self._is_out_of_bounds(ctx):
            self._remove()
            return

        if not ctx.enemies:
            self._explode(ctx)
            return

        # Re-find target by id in case the list was rebuilt
        for enemy in ctx.enemies:
            if enemy.id == self.target.id:
                self.target = enemy
                break

        self.rotate_to_angle(angle_between_points(self.position, self.target.position))

        distance = self.target.position - self.position
        if distance.length() <= self.EXPLODE_DISTANCE:
            self._explode(ctx)
            return

        self._move(distance, ctx.speed)

    def _is_out_of_bounds(self, ctx: "IGameContext") -> bool:
        return (
            self.position.x < 0 or self.position.x > ctx.map_width
            or self.position.y < 0 or self.position.y > ctx.map_height
        )

    def _remove(self) -> None:
        if self in self.tower.bullets:
            self.tower.bullets.remove(self)

    def _explode(self, ctx: "IGameContext") -> None:
        self._remove()
        self.target.decrease_hp(self.damage, ctx)

    def _move(self, distance: Vector2, speed: int) -> None:
        self._velocity  = distance.normalize() * self.BULLET_SPEED * speed
        self.position  += self._velocity
        self.rect.center = self.position


class MuzzleFlash(GameObject):
    """Instant-hit effect for tower types 1 and 3.

    Positioned at the barrel tip (pos). Deals damage on the first update tick
    if deals_damage=True (set False for the second barrel of a twin-gun tower).
    Removes itself after FLASH_DURATION_MS.
    """
    FLASH_DURATION_MS = 120

    def __init__(self, target, tower, pos: Vector2, deals_damage: bool = True) -> None:
        super().__init__(
            ImagePath(str(tower.tower_type) + "L" + str(tower.level), folder="bullets"),
            pos,
        )
        self.tower         = tower
        self.target        = target
        self.damage        = tower.damage
        self._created_at   = pygame.time.get_ticks()
        self._damage_dealt = not deals_damage
        self.rotate_to_angle(angle_between_points(pos, target.position))

    def update(self, ctx: "IGameContext") -> None:
        if not self._damage_dealt:
            for enemy in ctx.enemies:
                if enemy.id == self.target.id:
                    self.target = enemy
                    break
            if self.target in ctx.enemies:
                self.target.decrease_hp(self.damage, ctx)
            self._damage_dealt = True

        if pygame.time.get_ticks() - self._created_at > self.FLASH_DURATION_MS:
            if self in self.tower.bullets:
                self.tower.bullets.remove(self)