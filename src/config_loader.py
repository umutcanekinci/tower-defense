from pathlib import Path

import yaml

from game_state import TowerConfig

_CONFIG_DIR = Path(__file__).parent.parent / "config"


def load_tower_config() -> TowerConfig:
    with open(_CONFIG_DIR / "towers.yaml") as f:
        data = yaml.safe_load(f)

    towers = sorted(data["towers"], key=lambda t: t["type"])
    return TowerConfig(
        prices     = [t["prices"]    for t in towers],
        max_levels = [t["max_level"] for t in towers],
        ranges     = [t["ranges"]    for t in towers],
        damages    = [t["damages"]   for t in towers],
        speeds     = [t["speeds"]    for t in towers],
    )


def load_enemy_stats() -> dict[int, tuple[int, float, int, int]]:
    with open(_CONFIG_DIR / "enemies.yaml") as f:
        data = yaml.safe_load(f)

    return {
        int(k): (v["hp"], float(v["speed"]), v["kill_money"], v["damage"])
        for k, v in data["enemies"].items()
    }


def load_wave_compositions() -> dict[int, list[tuple[int, int]]]:
    with open(_CONFIG_DIR / "waves.yaml") as f:
        data = yaml.safe_load(f)

    return {
        int(wave): [(e["type"], e["count"]) for e in groups]
        for wave, groups in data["waves"].items()
    }