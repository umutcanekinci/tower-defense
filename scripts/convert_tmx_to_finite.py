"""One-shot: convert a Tiled "infinite" TMX into a fixed-size TMX.

pytmx 3.32 raises on infinite maps. Tiled itself can edit either mode, so this
script just normalizes the file once. Re-run any time you re-export from Tiled
in infinite mode.

Usage:
    python scripts/convert_tmx_to_finite.py path/to/map.tmx
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def parse_chunk_csv(text: str) -> list[list[int]]:
    rows = [r for r in (line.strip() for line in text.strip().splitlines()) if r]
    grid = []
    for r in rows:
        grid.append([int(v) for v in r.rstrip(",").split(",")])
    return grid


def convert(tmx_path: Path) -> None:
    tree = ET.parse(tmx_path)
    root = tree.getroot()

    if root.attrib.get("infinite") != "1":
        print(f"{tmx_path.name}: already finite, nothing to do.")
        return

    tile_layers = root.findall("layer")

    # Bounding box across all chunks in all tile layers
    min_x = min_y = None
    max_x = max_y = None
    for layer in tile_layers:
        for chunk in layer.findall("data/chunk"):
            cx = int(chunk.attrib["x"])
            cy = int(chunk.attrib["y"])
            cw = int(chunk.attrib["width"])
            ch = int(chunk.attrib["height"])
            grid = parse_chunk_csv(chunk.text or "")
            if not any(any(v != 0 for v in row) for row in grid):
                continue
            for ry, row in enumerate(grid):
                for rx, v in enumerate(row):
                    if v == 0:
                        continue
                    tx = cx + rx
                    ty = cy + ry
                    if min_x is None or tx < min_x: min_x = tx
                    if min_y is None or ty < min_y: min_y = ty
                    if max_x is None or tx > max_x: max_x = tx
                    if max_y is None or ty > max_y: max_y = ty

    if min_x is None:
        print(f"{tmx_path.name}: empty map, refusing to convert.")
        return

    new_w = max_x - min_x + 1
    new_h = max_y - min_y + 1
    print(f"bbox: ({min_x},{min_y})..({max_x},{max_y})  -> {new_w}x{new_h}")

    # Flatten each tile layer
    for layer in tile_layers:
        flat = [[0] * new_w for _ in range(new_h)]
        for chunk in layer.findall("data/chunk"):
            cx = int(chunk.attrib["x"])
            cy = int(chunk.attrib["y"])
            grid = parse_chunk_csv(chunk.text or "")
            for ry, row in enumerate(grid):
                for rx, v in enumerate(row):
                    if v == 0:
                        continue
                    nx = cx + rx - min_x
                    ny = cy + ry - min_y
                    if 0 <= nx < new_w and 0 <= ny < new_h:
                        flat[ny][nx] = v

        layer.set("width", str(new_w))
        layer.set("height", str(new_h))
        data_el = layer.find("data")
        # remove all chunk children
        for c in list(data_el.findall("chunk")):
            data_el.remove(c)
        csv_lines = [",".join(str(v) for v in row) for row in flat]
        data_el.text = "\n" + ",\n".join(csv_lines) + "\n"

    # Shift object coords. Object x/y are in pixels, so shift by min_x*tw, min_y*th.
    tw = int(root.attrib["tilewidth"])
    th = int(root.attrib["tileheight"])
    dx_px = min_x * tw
    dy_px = min_y * th
    for group in root.findall("objectgroup"):
        for obj in group.findall("object"):
            if "x" in obj.attrib:
                obj.set("x", str(float(obj.attrib["x"]) - dx_px))
            if "y" in obj.attrib:
                obj.set("y", str(float(obj.attrib["y"]) - dy_px))

    # Map-level updates
    root.set("infinite", "0")
    root.set("width", str(new_w))
    root.set("height", str(new_h))

    tree.write(tmx_path, encoding="utf-8", xml_declaration=True)
    print(f"wrote {tmx_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    convert(Path(sys.argv[1]))