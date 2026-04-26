from typing import TYPE_CHECKING

from pygame.math import Vector2

from core.game_object import GameObject
from core.math import angle_between_points
from pygame_core.asset_path import ImagePath

if TYPE_CHECKING:
    from core.protocols import IGameContext


class Projectile(GameObject):
    EXPLODE_DISTANCE = 30
    BULLET_SPEED     = 1 / 5

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

    def _explode(self, ctx: "IGameContext") -> None:
        self.tower.bullets.remove(self)
        self.target.decrease_hp(self.damage, ctx)

    def _move(self, distance: Vector2, speed: int) -> None:
        self._velocity  = distance.normalize() * self.BULLET_SPEED * speed
        self.position  += self._velocity
