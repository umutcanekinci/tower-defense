# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
cd C:\Users\user\PycharmProjects\tower-defense
python __main__.py
```

No tests, no lint config, no build step.

## Architecture

### Entry point → Game class

`__main__.py` creates `Game()` and calls `game.run()`. `Game` (in `src/game.py`) extends `pygame_core.Application` and is the top-level orchestrator: it wires all subsystems in `__init__`, runs a splash screen, then hands control to the `Application` base class loop which calls `update()` / `draw()` / `handle_event()` each frame.

### Subsystems wired by Game

| Object | Class | Responsibility |
|--------|-------|----------------|
| `game_state` | `GameState` | Pure data (money, lives, speed, level, is_started); fires listener callbacks on money/level change |
| `camera` | `Camera` | Edge-scroll camera for the 1536×1080 game area; applies world→screen offset to all drawn entities |
| `assets` | `AssetManager` | Loads all images/sounds from `config/assets.yaml`; accessed via string keys everywhere |
| `panel_manager` | `PanelManager` | Holds named panels ("main_menu", "contact", "game"); switching is `panel_manager.current_panel = "name"` |
| `tilemap` | `Tilemap` | 22×16 tile grid; tiles created lazily in `run()` after splash |
| `wave_manager` | `WaveManager` | Reads `config/waves.yaml`; spawns enemies on a timer; advances `game_state.level` when wave clears |
| `hud` | `GameHUD` | Draws money, lives, level, tower prices; subscribes to `GameState` listeners |
| `tower_controller` | `TowerPlacementController` | Handles buy/place/select/upgrade/sell; shares the `towers` list reference |
| `menu_bg` | `MenuBackground` | Pre-renders tilemap at 2× and slowly pans it behind menu panels |

### Panel / UI system

Panels are defined in `config/panels.yaml` and loaded by `PanelLoaderExt` (in `src/core/panel_loader_ext.py`), which extends the venv `PanelLoader` with **object-level template inheritance** via `object_templates:`.

Two factory types are registered in `game.py`:
- `"object"` (default) → `panel_factory.make_factory(assets)` → creates `GuiObject` or `HoverableGuiObject`
- `"text"` → `panel_factory.make_text_factory()` → creates `TextObject`

YAML keys for image objects: `position`, `size`, `asset`, `hover`, `states`, `nine_slice`, `extends`.  
YAML keys for text objects: `type: text`, `position`, `text`, `font`, `font_size`, `color`.

`nine_slice` uses `core.image.nine_slice_scale()` — `corner` is the corner region size **in source pixels**. Only edges/center are stretched; corners are pixel-perfect.

### Towers

`BaseTower` (abstract) → `GroundTower` (types 1–3) or `PlaneTower` (type 4). `TowerFactory.create()` returns the right subclass. Stats come from `config/towers.yaml` via `TowerConfig` (indexed `[type-1][level-1]`).

- Types 1 & 3: instant-hit `MuzzleFlash` at barrel tips (twin barrels for type 1 and type 3 lvl 2)
- Type 2: homing `Projectile`
- Type 4: cosmetic plane that flies across the map, no attacking

### Projectiles / IGameContext

`Projectile` and `MuzzleFlash` (in `src/projectile.py`) receive an `IGameContext` on `update()`. `Game` satisfies this protocol via `.enemies`, `.speed`, `.map_width`, `.map_height`, and `.increase_money()`. This avoids circular imports — projectiles never import `Game`.

### Rendering order (game panel)

Tilemap → towers + bullets → enemies → border lines → HUD → tower placement overlay (cursor + range ring)

### Config files

| File | Loaded by | Structure |
|------|-----------|-----------|
| `config/assets.yaml` | `AssetManager.load_manifest()` | `{images: {key: {folder, name}}, sounds: {key: {folder, name}}}` |
| `config/towers.yaml` | `config_loader.load_tower_config()` | Produces `TowerConfig` dataclass with `.prices`, `.max_levels`, `.ranges`, `.damages`, `.speeds` |
| `config/enemies.yaml` | `config_loader.load_enemy_stats()` | HP/speed/kill_money/damage per enemy type |
| `config/waves.yaml` | `config_loader.load_wave_compositions()` | `{wave_num: [[enemy_type, count], ...]}` |
| `config/panels.yaml` | `PanelLoaderExt.load()` | Panels + groups + optional `object_templates` |

### Coordinate system

Tile size is 64 px. Map is 22×16 tiles = 1408×1024 px world space. The camera viewport is 1536×1080 (game area) — the full map fits without scrolling. HUD occupies 384 px on the right (x: 1536–1920). All entity positions are world-space center points stored as `pygame.math.Vector2`.

### Adding a new tower type

1. Add stats to `config/towers.yaml`
2. Subclass `BaseTower` (or reuse `GroundTower` if behaviour matches)
3. Register in `TowerFactory.create()`
4. Add assets to `config/assets.yaml` and `assets/images/towers/`
5. Add buy button to `config/panels.yaml` and price display to `GameHUD`