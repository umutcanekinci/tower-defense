import pygame
from pygame import Rect

from core.camera import Camera

SCROLL_SPEED = 0.7   # px per frame


class MenuBackground:
    """Pre-renders the tilemap at 2× and slowly pans through it as a menu backdrop."""

    _SCALE = 2

    def __init__(self, tilemap, map_cols: int, map_rows: int, viewport: tuple[int, int]) -> None:
        mw = map_cols * 64
        mh = map_rows * 64
        vw, vh = viewport

        # Render all tiles into an off-screen surface at 1×
        src = pygame.Surface((mw, mh))
        null_cam = Camera(Rect(0, 0, mw, mh))
        for tile in tilemap.tiles:
            tile.draw(src, null_cam)

        bg_w = mw * self._SCALE
        bg_h = mh * self._SCALE
        self._bg    = pygame.transform.smoothscale(src, (bg_w, bg_h))
        self._max_x = float(max(0, bg_w - vw))
        self._max_y = float(max(0, bg_h - vh))
        self._vw = vw
        self._vh = vh
        self._x  = 0.0
        self._y  = 0.0
        self._dx = SCROLL_SPEED
        self._dy = SCROLL_SPEED

    def update(self) -> None:
        self._x += self._dx
        self._y += self._dy
        if self._x >= self._max_x or self._x <= 0:
            self._dx = -self._dx
            self._x  = max(0.0, min(self._max_x, self._x))
        if self._y >= self._max_y or self._y <= 0:
            self._dy = -self._dy
            self._y  = max(0.0, min(self._max_y, self._y))

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self._bg, (0, 0),
                     (int(self._x), int(self._y), self._vw, self._vh))