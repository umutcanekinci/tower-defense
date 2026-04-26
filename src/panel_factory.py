from core.guiobject import GuiObject


def make_gui_object(cfg: dict, window_size: tuple) -> GuiObject:
    pos   = cfg["position"]
    size  = tuple(cfg["size"]) if cfg["size"] != "WINDOW" else window_size
    asset = cfg["asset"]              # ImagePath (loader resolve etti)
    hover = cfg.get("hover")          # ImagePath veya None
    return GuiObject(window_size, pos, size, asset, hover)