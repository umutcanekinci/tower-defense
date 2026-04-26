import enum
from typing import TYPE_CHECKING

from core.image import rotate_surface
from core.game_object import GameObject
from pygame_core.asset_path import ImagePath

if TYPE_CHECKING:
    from core.protocols import IGameContext


class Enemy(GameObject):
    class Direction(enum.Enum):
        Right = "R"
        Up    = "U"
        Left  = "L"
        Down  = "D"
        Back  = "B"
        Enter = "E"

    def __init__(self, id: int, level: int, x: int, y: int) -> None:
        super().__init__(ImagePath("E1", folder="enemy"), (x + 32, y + 32))
        self.id          = id
        self.is_walking  = True
        self.direction   = self.Direction.Right
        self._calculate_stats(level)

    def _calculate_stats(self, level: int) -> None:
        self.maxHP     = 10 * ((level // 10) + 1) ** 2
        self.hp        = self.maxHP
        self.killMoney = ((level // 5) + 1) * 1
        self.damage    = (level // 25) + 1
        self.mov_speed = 1

    def destroy(self, ctx: "IGameContext") -> None:
        if self in ctx.enemies:
            ctx.enemies.remove(self)

    def decrease_hp(self, damage: int, ctx: "IGameContext") -> None:
        if self not in ctx.enemies:
            return
        self.hp -= damage
        if self.hp <= 0:
            self.destroy(ctx)
            ctx.increase_money(self.killMoney)

    def get_column(self) -> int:
        return (self.position.x // 64) + 1

    def get_row(self) -> int:
        return (self.position.y // 64) + 1

    def move(self, tilemap: list, game_speed: int) -> None:
        self.row_number = 0
        self._rotate(tilemap)

        if self.direction == self.Direction.Right:
            self.position.x += self.mov_speed * game_speed
        elif self.direction == self.Direction.Up:
            self.position.y -= self.mov_speed * game_speed
        elif self.direction == self.Direction.Left:
            self.position.x -= self.mov_speed * game_speed
        elif self.direction == self.Direction.Down:
            self.position.y += self.mov_speed * game_speed
        elif self.direction in (self.Direction.Back, self.Direction.Enter):
            self.position.x -= self.mov_speed * game_speed

        self.rect.center = self.position

    def _rotate(self, tilemap: list) -> None:
        for row in tilemap:
            self.row_number   += 1
            self.column_number = 0
            for cell in row:
                self.column_number += 1
                if not (
                    len(cell) >= 2
                    and self.column_number == self.get_column()
                    and self.row_number    == self.get_row()
                    and (self.position.x - 32) % 64 == 0
                    and (self.position.y - 32) % 64 == 0
                ):
                    continue

                new_dir = cell[1]
                if new_dir == "R":
                    if self.direction == self.Direction.Up:
                        self.image = rotate_surface(self.image, -90)
                    elif self.direction == self.Direction.Down:
                        self.image = rotate_surface(self.image, +90)
                    self.direction = self.Direction.Right
                elif new_dir == "U":
                    if self.direction == self.Direction.Right:
                        self.image = rotate_surface(self.image, +90)
                    elif self.direction == self.Direction.Left:
                        self.image = rotate_surface(self.image, -90)
                    self.direction = self.Direction.Up
                elif new_dir == "L":
                    if self.direction == self.Direction.Up:
                        self.image = rotate_surface(self.image, +90)
                    elif self.direction == self.Direction.Down:
                        self.image = rotate_surface(self.image, -90)
                    self.direction = self.Direction.Left
                elif new_dir == "D":
                    if self.direction == self.Direction.Right:
                        self.image = rotate_surface(self.image, -90)
                    elif self.direction == self.Direction.Left:
                        self.image = rotate_surface(self.image, +90)
                    self.direction = self.Direction.Down
