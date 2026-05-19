import pygame

from pygame_core.unity.components.transform import Transform
from pygame_core.utils import Centerable


class TextObject(Centerable):
    """A GUI-compatible text label loaded from panel YAML.

    Implements the same minimal interface as GuiObject (draw / handle_event /
    is_clicked / set_state) so PanelManager can treat it uniformly.
    """

    def __init__(
        self,
        parent: Transform,
        pos,
        text: str,
        font: pygame.font.Font,
        color
    ) -> None:
        self._parent = parent
        self._pos_spec = pos
        self._font = font
        self._text = text
        self._color = self._parse_color(color)
        self._render()

    def set_text(self, text: str) -> None:
        if text == self._text:
            return
        self._text = text
        self._render()

    def set_color(self, color) -> None:
        new_color = self._parse_color(color)
        if new_color == self._color:
            return
        self._color = new_color
        self._render()

    def _render(self) -> None:
        self._surface = self._font.render(self._text, True, self._color)
        text_size = self._surface.get_size()
        local_pos = self.resolve_pos(self._pos_spec, self._parent.size, text_size)
        self._pos = (local_pos[0] + self._parent.x, local_pos[1] + self._parent.y)

    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self._surface, self._pos)

    @staticmethod
    def _parse_color(color) -> tuple:
        if isinstance(color, (list, tuple)):
            return tuple(color)
        return tuple(pygame.Color(str(color)))