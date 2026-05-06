import pygame

from core.guiobject import GuiObject, HoverableGuiObject
from core.text_object import TextObject
from pygame_core.unity.components.transform import Transform


def make_factory(assets):
    def make_gui_object(cfg: dict, parent: Transform) -> GuiObject:
        pos          = cfg["position"]
        size         = tuple(cfg["size"]) if cfg["size"] != "WINDOW" else parent
        asset        = cfg["asset"]
        hover        = cfg.get("hover")
        extra_states = cfg.get("states", {})
        nine_slice   = cfg.get("nine_slice", 0)

        if hover is not None or extra_states:
            obj = HoverableGuiObject(parent=parent, pos=pos, size=size, image_path=asset, hover_image_path=hover, nine_slice=nine_slice)
            for state_key, state_cfg in extra_states.items():
                state_asset = assets.image_path(state_cfg["asset"]) if isinstance(state_cfg["asset"], str) else state_cfg["asset"]
                state_hover = assets.image_path(state_cfg["hover"]) if isinstance(state_cfg.get("hover"), str) else state_cfg.get("hover")
                obj.add_state(state_key, state_asset, state_hover)
            return obj
        return GuiObject(parent=parent, pos=pos, size=size, image_path=asset, nine_slice=nine_slice)
    return make_gui_object


def make_text_factory(assets):
    def make_text_object(cfg: dict, parent: Transform) -> TextObject:
        font_key  = cfg.get("font", "Arial")
        font_size = cfg.get("font_size", 32)
        try:
            font = pygame.font.Font(str(assets.font_path(font_key)), font_size)
        except KeyError:
            font = pygame.font.SysFont(font_key, font_size)
        return TextObject(
            parent,
            cfg["position"],
            cfg["text"],
            font,
            cfg.get("color", [255, 255, 255]),
        )
    return make_text_object