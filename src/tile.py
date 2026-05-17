from core.constants import TILE_SIZE, HALF_TILE
from core.rotateable_object import RotateableObject


class Tile(RotateableObject):
    _TILE_KEYS = {
        "0": "tile_grass",
        "1": "tile_clay",
        "2": "tile_stone",
        "3": "tile_sand",
    }

    def __init__(self, tile_type: str, col: int, row: int, assets) -> None:
        base_image = assets.image_path(self._TILE_KEYS[tile_type[0]])
        super().__init__(base_image, (col * TILE_SIZE + HALF_TILE, row * TILE_SIZE + HALF_TILE))

        self.type = tile_type
        self.row = row
        self.col = col
        self.decoration = None

        if len(tile_type) > 2 and tile_type[1:3] == "+B":
            dec_id = tile_type[tile_type.index("+B") + 2]
            dec_path = assets.image_path(f"tile_decoration_{dec_id}")
            self.decoration = RotateableObject(dec_path, self.position)

    def draw(self, surface, camera) -> None:
        camera.draw(surface, self)
        if self.decoration is not None:
            camera.draw(surface, self.decoration)

    def is_enemy_spawn_tile(self) -> bool:
        """Checks if the tile is an enemy spawn tile (type "1E") and returns its coordinates if true."""

        return len(self.type) > 1 and self.type[1] == "B"

    def get_last_tile(self) -> list:
        if len(self.type) > 1 and self.type[1] == "E":
            return [self.col, self.row]
        return [None, None]
