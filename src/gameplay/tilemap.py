"""Tiled .tmx loader for the tower-defense game.

Replaces the legacy string-grid `Tilemap` for maps authored in Tiled. The
legacy class still works for hand-coded grids; nothing here touches it.

TMX conventions this loader expects:

- `infinite="0"` in the map header. pytmx 3.32 does not load infinite maps;
  run `python scripts/convert_tmx_to_finite.py <map.tmx>` once after exporting
  from Tiled in infinite mode.
- An object group named `Markers` containing point objects named `"spawn"`
  and `"end"`.
- An object group named `Paths` containing polyline objects, one per path.
- A tile layer named `Road` whose tiles describe the enemy path geometry.
  Buildable tiles are anywhere outside the `Road` layer (and outside towers).
"""

from __future__ import annotations

from pathlib import Path

import pygame
import pytmx
from pygame.math import Vector2
from pytmx.util_pygame import load_pygame


_WAY_LAYER = "Road"
_MARKERS_GROUP = "Markers"
_PATHS_GROUP = "Paths"


class Tilemap:
    """Loads a Tiled .tmx and exposes the surface Game needs."""

    def __init__(self, tmx_path: str | Path) -> None:
        self._tmx = load_pygame(str(tmx_path))
        self.tile_size = self._tmx.tilewidth
        if self._tmx.tilewidth != self._tmx.tileheight:
            raise ValueError("non-square tiles are not supported")

        self.cols: int = self._tmx.width
        self.rows: int = self._tmx.height

        self.waypoints: list[Vector2] = self._load_first_path()
        self._spawn_col, self._spawn_row = self._load_marker("spawn")
        self.buildable_grid: list[list[bool]] = self._compute_buildable()

        self._native_surface: pygame.Surface | None = None
        self._scaled_surface: pygame.Surface | None = None
        self._scaled_factor:  float = 1.0

    # ── loaders ───────────────────────────────────────────────────────────

    def _iter_objects(self, group_name: str):
        for layer in self._tmx.layers:
            if isinstance(layer, pytmx.TiledObjectGroup) and layer.name == group_name:
                yield from layer

    def _load_first_path(self) -> list[Vector2]:
        for obj in self._iter_objects(_PATHS_GROUP):
            points = getattr(obj, "points", None)
            if points:
                return [Vector2(p.x, p.y) for p in points]
        return []

    def _load_marker(self, name: str) -> tuple[int | None, int | None]:
        for obj in self._iter_objects(_MARKERS_GROUP):
            if (obj.name or "").lower() == name.lower():
                col = int(obj.x // self.tile_size)
                row = int(obj.y // self.tile_size)
                return col, row
        return None, None

    def _compute_buildable(self) -> list[list[bool]]:
        grid = [[True for _ in range(self.cols)] for _ in range(self.rows)]
        for layer in self._tmx.layers:
            if not isinstance(layer, pytmx.TiledTileLayer) or layer.name != _WAY_LAYER:
                continue
            for x, y, gid in layer.iter_data():
                if gid != 0 and 0 <= y < self.rows and 0 <= x < self.cols:
                    grid[y][x] = False
        return grid

    # ── public API ────────────────────────────────────────────────────────

    @property
    def map_width(self) -> int:
        return self.cols * self.tile_size

    @property
    def map_height(self) -> int:
        return self.rows * self.tile_size

    def get_spawn_tile(self) -> list[int | None]:
        return [self._spawn_col, self._spawn_row]

    def draw(self, surface: pygame.Surface, camera) -> None:
        if self._native_surface is None:
            self._native_surface = self.pre_render()
        if abs(self._scaled_factor - camera.scale) > 1e-6 or self._scaled_surface is None:
            self._scaled_factor  = camera.scale
            self._scaled_surface = (
                self._native_surface if abs(camera.scale - 1.0) < 1e-6
                else pygame.transform.scale_by(self._native_surface, camera.scale)
            )
        old_clip = surface.get_clip()
        surface.set_clip(camera.rect)
        surface.blit(self._scaled_surface, camera.world_to_screen((0, 0)))
        surface.set_clip(old_clip)

    def pre_render(self) -> pygame.Surface:
        """Render the full map to an offscreen surface (no camera offset)."""
        surf = pygame.Surface((self.map_width, self.map_height))
        ts = self.tile_size
        for layer in self._tmx.visible_layers:
            if not isinstance(layer, pytmx.TiledTileLayer):
                continue
            for x, y, image in layer.tiles():
                if image is not None:
                    surf.blit(image, (x * ts, y * ts))
        return surf