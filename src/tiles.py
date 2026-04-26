from core.game_object import GameObject
from core.image import load_image, scale_surface_by

TILEMAP = [
    ["0",    "0",    "0",    "0",    "0",    "0+B1", "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0+B8", "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0",    "0",    "0",    "0",    "0",    "0",    "0+B2", "0",    "0",    "0+B7", "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0",    "0",    "1R",   "1R",   "1R",   "1D",   "0",    "0",    "1R",   "1R",   "1R",   "1R",   "1R",   "1R",   "1R",   "1R",   "1R",   "1E",   "0",    "0",    "0",    "0"   ],
    ["0",    "0",    "1U",   "0",    "0",    "1D",   "0",    "0",    "1U",   "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0",    "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "2U",   "2L",   "2L",   "2L",   "2L",   "2L",   "2L",   "2L",   "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0",    "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "2U",   "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0+B2", "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "2U",   "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0",    "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "2U",   "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0",    "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "2U",   "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0+B4", "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "2U",   "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0",    "0",    "1U",   "0",    "0",    "2D",   "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "3",    "2U",   "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["1B",   "1R",   "1U",   "0",    "0",    "2R",   "2R",   "2R",   "2R",   "2R",   "2R",   "2R",   "2R",   "2R",   "2R",   "2U",   "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0+B5", "0",    "0",    "0",    "0+B7", "0",    "0",    "0+B1", "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0",    "0+B6", "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0"   ],
    ["0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0",    "0"   ],
]


class Tile(GameObject):
    _TILE_IMAGES = {
        "0": "tiles/grass",
        "1": "tiles/clay",
        "2": "tiles/stone",
        "3": "tiles/sand",
    }

    def __init__(self, tile_type: str, col: int, row: int) -> None:
        super().__init__(self._TILE_IMAGES[tile_type[0]], (col * 64 + 32, row * 64 + 32))
        self.type       = tile_type
        self.row        = row
        self.col        = col
        self.decoration = None

        self.load_image(self._TILE_IMAGES[tile_type[0]])

        if len(tile_type) > 2 and tile_type[1:3] == "+B":
            dec_id          = tile_type[tile_type.index("+B") + 2]
            self.decoration = GameObject("tiles/B" + dec_id, self.position)

    def draw(self, surface, camera) -> None:
        camera.draw(surface, self)
        if self.decoration is not None:
            camera.draw(surface, self.decoration)

    def get_first_tile(self) -> list:
        """Return [col, row] of the enemy spawn tile, or [None, None]."""
        if len(self.type) > 1 and self.type[1] == "B":
            return [self.col, self.row]
        return [None, None]

    def get_last_tile(self) -> list:
        if len(self.type) > 1 and self.type[1] == "E":
            return [self.col, self.row]
        return [None, None]
