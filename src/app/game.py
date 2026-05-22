from pathlib import Path
from typing import override

import pygame
import yaml
from pygame import Rect

from app.game_events import GameEventsMixin
from pygame_core.application import Application
from pygame_core.asset_manager import AssetManager
from pygame_core.ui_widgets.menu_controller import MenuController
from pygame_core.mouse import Mouse
from pygame_core.panel_manager import PanelManager
from pygame_core.panel_loader_ext import PanelLoaderExt

from pygame_core import panel_factory
from util.config_loader import load_tower_config
from pygame_core.camera import Camera
from util.constants import TILE_SIZE
from pygame_core.debug import Debug
from ui.menu_background import MenuBackground
from pygame_core.splash_screen import SplashScreen
from pygame_core.ecs.game_audio import GameAudio
from gameplay.combat.enemy import Enemy
from ui.game_hud import GameHUD
from domain.game_state import GameState
from pygame_core.ecs.components.transform import Transform
from gameplay.tilemap import Tilemap
from gameplay.combat.tower_placement import TowerPlacementController
from towers import BaseTower, GroundTower
from gameplay.combat.wave_manager import WaveManager


class Game(GameEventsMixin, Application):
    """Top-level orchestrator.

    Responsibilities: wiring subsystems, routing input per panel,
    and running the update/draw pipeline.
    """

    # ── construction ──────────────────────────────────────────────────────────

    def __init__(self):
        self.settings = yaml.safe_load(Path("config/settings.yaml").read_text())
        window   = self.settings["window"]
        gameplay = self.settings["gameplay"]
        splash   = self.settings["splash"]
        camera   = self.settings["camera"]

        super().__init__(tuple(window["size"]), window["title"], window["fps"], Mouse(TILE_SIZE))

        window_transform = Transform((0, 0), self.size)
        self.towers:       list[BaseTower] = []
        self.enemies:      list[Enemy]     = []
        self.wave_manager: WaveManager | None = None

        self.game_area        = Rect(*gameplay["game_area"])
        self.game_state       = GameState(start_money=gameplay["starting_money"], start_lives=gameplay["starting_lives"])
        self.assets           = AssetManager()
        self.tower_config     = load_tower_config()
        self.tilemap          = Tilemap("assets/tiled_project/tiled_tilemap.tmx")
        self.camera           = Camera(
            self.game_area,
            self.tilemap.map_width, self.tilemap.map_height,
            scroll_rect=Rect(0, 0, *self.size),
            edge_scroll_zone=camera["edge_scroll_zone"],
            speed=camera["speed"],
            zoom_step=camera["zoom_step"],
            zoom_min=camera["zoom_min"],
            zoom_max=camera["zoom_max"],
        )
        self.panel_manager    = PanelManager(starting_tab="main_menu")

        self.load_panels(window_transform)

        self.audio            = GameAudio(str(self.assets.sound_path("bg_music")))
        self.hud              = GameHUD(self.game_state, self.tower_config, self.panel_manager)
        self.tower_controller = TowerPlacementController(self.towers, self.tower_config, self.assets, self.audio, self.game_state, self.camera, self.panel_manager, self.tilemap.buildable_grid, self.tilemap.map_width, self.game_area)

        self.menu_bg = MenuBackground(self.tilemap.pre_render(), self.size)
        self.menu_overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self.menu_overlay.fill((0, 0, 0, 120))
        self.splash = SplashScreen([self.assets.image_path("pygame_logo")], fade_ms=splash["fade_ms"], hold_ms=splash["hold_ms"])
        self._init_wave_manager()

        self.handlers = {
            "main_menu": self._handle_main_menu_event,
            "contact":   self._handle_contact_event,
            "game":      self._handle_game_event,
        }
        main_menu_buttons = [self.panel_manager["main_menu"][n] for n in ("play", "contact", "exit")]
        self.menu_controllers = {
            "main_menu": MenuController(main_menu_buttons, self.audio),
        }

    def load_panels(self, window_transform) -> None:
        self.assets.load_manifest("config/assets.yaml")
        missing = self.assets.validate()
        if missing:
            raise RuntimeError("Missing assets:\n" + "\n".join(missing))

        loader = PanelLoaderExt(self.panel_manager, window_transform, self.assets)
        loader.register("object", panel_factory.make_factory(self.assets), default=True)
        loader.register("text", panel_factory.make_text_factory(self.assets))
        loader.register("animated", panel_factory.make_animated_factory(self.assets))
        loader.load("config/panels.yaml")

    # ── IGameContext interface ────────────────────────────────────────────────

    @property
    def speed(self) -> int:
        return self.game_state.speed

    @property
    def map_width(self) -> int:
        return self.tilemap.map_width

    @property
    def map_height(self) -> int:
        return self.tilemap.map_height

    def increase_money(self, amount: int) -> None:
        self.game_state.increase_money(amount)

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def run(self):
        self.splash.run(self.window, self.clock, self._fps)
        super().run()

    def _init_wave_manager(self) -> None:
        if not self.tilemap.waypoints:
            raise RuntimeError("TMX has no Paths/polyline; enemies have nowhere to go")
        self.wave_manager = WaveManager(self.tilemap.waypoints, self.assets)

    # ── update ────────────────────────────────────────────────────────────────

    @override
    def update(self) -> None:
        self.panel_manager.update()
        if self.panel_manager.current_panel in ("main_menu", "contact"):
            self.menu_bg.update()
        if self.panel_manager.current_panel == "game":
            self._update_game()

    def _update_game(self) -> None:
        self.camera.update_with_mouse(self.mouse.position)
        self.mouse.update()
        self.tower_controller.update_cursor(self.mouse.position)
        self._update_towers()
        self._update_enemies()

    def _update_towers(self) -> None:
        self.towers[:] = [t for t in self.towers if not t.should_remove()]
        self.tower_controller.tower_positions = []
        for tower in self.towers:
            tower.update(self.game_state, self.enemies)
            pos = tower.get_blocking_position()
            if pos:
                self.tower_controller.tower_positions.append(pos)
            for bullet in tower.bullets:
                if self.game_state.is_started:
                    bullet.update(self)

    def _update_enemies(self) -> None:
        if self.wave_manager:
            self.wave_manager.update(self.enemies, self.game_state)
        for enemy in self.enemies:
            if enemy.reached_end():
                self.enemies.remove(enemy)
                self.game_state.decrease_lives(enemy.damage)
                if self.game_state.lives == 0:
                    self.exit()
            elif self.game_state.is_started:
                enemy.move(self.game_state.speed)

    # ── event handling ────────────────────────────────────────────────────────

    @override
    def handle_event(self, event):
        self.panel_manager.handle_event(event, self.mouse.position)
        if controller := self.menu_controllers.get(self.panel_manager.current_panel):
            controller.handle_event(event, self.mouse.position)
        if handler := self.handlers.get(self.panel_manager.current_panel):
            handler(event)
        panel = self.panel_manager[self.panel_manager.current_panel]
        if panel["music_toggle_button"].is_clicked(event, self.mouse.position):
            self._toggle_music()

    # ── render pipeline ───────────────────────────────────────────────────────

    @override
    def draw(self):
        self.window.fill((0, 0, 0))
        if self.panel_manager.current_panel == "game":
            self._draw_game()
        elif self.panel_manager.current_panel in ("main_menu", "contact"):
            self.menu_bg.draw(self.window)
            self.window.blit(self.menu_overlay, (0, 0))
        self.panel_manager.draw(self.window)
        if self.panel_manager.current_panel == "game":
            self.tower_controller.draw_shortcuts(self.window)

    def _draw_game(self) -> None:
        def _draw_tilemap(self) -> None:
            self.tilemap.draw(self.window, self.camera)

        def _draw_towers(self) -> None:
            for tower in self.towers:
                tower.draw(self.game_state, self.camera, self.window)
                for bullet in tower.bullets:
                    self.camera.draw(self.window, bullet)

        def _draw_enemies(self) -> None:
            for enemy in self.enemies:
                self.camera.draw(self.window, enemy)

        old_clip = self.window.get_clip()
        self.window.set_clip(self.game_area)
        _draw_tilemap(self)
        _draw_towers(self)
        _draw_enemies(self)
        self.tower_controller.draw(self.window, self.mouse.position)
        self._draw_selected_tower_ui()
        self.window.set_clip(old_clip)

    def _draw_selected_tower_ui(self) -> None:
        selected = self.game_state.selected_tower
        if selected is None or selected not in self.towers:
            return
        if isinstance(selected, GroundTower):
            selected.draw_selected_ui(self.window, self.game_state, self.camera)


    # ── debug ─────────────────────────────────────────────────────────────────

    @override
    def draw_debug(self):
        if not self._is_in_debug_mode: return

        debug_info = [
            self.mouse.get_info(),
            self.camera.info(),
            self.panel_manager["main_menu"]["play"].get_info,
        ]
        Debug.draw(self.window, pygame.font.SysFont("Consolas", 20), debug_info)

    # ── exit ──────────────────────────────────────────────────────────────────

    @override
    def on_exit_request(self):
        if self.panel_manager.current_panel == "main_menu":
            self.exit()
        elif self.panel_manager.current_panel in ("contact", "game"):
            self.panel_manager.current_panel = "main_menu"
            self.game_state.is_started = False