from dataclasses import dataclass
from pathlib import Path

import yaml

from domain.game_state import TowerConfig, WaveDef

_CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


@dataclass
class EnemyStats:
    hp: int
    speed: float
    kill_money: int
    damage: int
    range: int | None = None             # tanks only
    fire_interval_ms: int | None = None  # tanks only


def load_tower_config() -> TowerConfig:
    with open(_CONFIG_DIR / "towers.yaml") as f:
        data = yaml.safe_load(f)

    towers = sorted(data["towers"], key=lambda t: t["type"])
    return TowerConfig(
        prices       = [t["prices"]    for t in towers],
        max_levels   = [t["max_level"] for t in towers],
        ranges       = [t["ranges"]    for t in towers],
        damages      = [t["damages"]   for t in towers],
        speeds       = [t["speeds"]    for t in towers],
        shoot_sounds = [t.get("shoot_sound") for t in towers],
    )


def load_enemy_stats() -> dict[int, EnemyStats]:
    with open(_CONFIG_DIR / "enemies.yaml") as f:
        data = yaml.safe_load(f)

    return {
        int(k): EnemyStats(
            hp=v["hp"],
            speed=float(v["speed"]),
            kill_money=v["kill_money"],
            damage=v["damage"],
            range=v.get("range"),
            fire_interval_ms=v.get("fire_interval_ms"),
        )
        for k, v in data["enemies"].items()
    }


def load_wave_compositions() -> dict[int, WaveDef]:
    """Parse waves.yaml.

    Each wave entry may be either:
      - a list of {type, count} groups (default spawn interval), or
      - a dict {spawn_interval: <ms>, groups: [{type, count}, ...]}.
    """
    with open(_CONFIG_DIR / "waves.yaml") as f:
        data = yaml.safe_load(f)

    waves: dict[int, WaveDef] = {}
    for wave, entry in data["waves"].items():
        if isinstance(entry, list):
            groups, interval = entry, None
        else:
            groups, interval = entry["groups"], entry.get("spawn_interval")
        waves[int(wave)] = WaveDef(
            groups=[(e["type"], e["count"]) for e in groups],
            spawn_interval_ms=interval,
        )
    return waves