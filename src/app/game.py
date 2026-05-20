from typing import override

import pygame
from pygame import Rect

from pygame_core.application import Application
from pygame_core.asset_manager import AssetManager
from pygame_core.mouse import Mouse
from pygame_core.panel_manager import PanelManager
from pygame_core.panel_loader_ext import PanelLoaderExt

from ui import panel_factory
from util.config_loader import load_tower_config
from rendering.camera import Camera
from util.constants import TILE_SIZE
from util.debug import Debug
from ui.menu_background import MenuBackground
from app.splash_screen import SplashScreen
from pygame_core.unity.game_audio import GameAudio
from gameplay.combat.enemy import Enemy
from ui.game_hud import GameHUD
from domain.game_state import GameState
from pygame_core.unity.components.transform import Transform
from gameplay.tilemap import Tilemap
from gameplay.combat.tower_placement import TowerPlacementController
from towers import BaseTower, GroundTower
from gameplay.combat.wave_manager import WaveManager


class Game(Application):
    """Top-level orchestrator.

    Responsibilities: wiring subsystems, routing input per panel,
    and running the update/draw pipeline.
    """

    # ── construction ──────────────────────────────────────────────────────────

    def __init__(self):
        super().__init__((1920, 1080), "TOWER DEFENSE", 165, Mouse(TILE_SIZE))

        window_transform = Transform((0, 0), self.size)
        self.towers:       list[BaseTower] = []
        self.enemies:      list[Enemy]     = []
        self.wave_manager: WaveManager | None = None

        self.game_state       = GameState(start_money=200, start_lives=10)
        self.assets           = AssetManager()
        self.tower_config     = load_tower_config()
        self.tilemap          = Tilemap("assets/tiled_project/tiled_tilemap.tmx")
        self.camera           = Camera(Rect(0,0, 1500, 1080), self.tilemap.map_width, self.tilemap.map_height, scroll_rect=Rect(0, 0, *self.size))
        self.panel_manager    = PanelManager(starting_tab="main_menu")

        self.load_panels(window_transform)

        self.audio            = GameAudio(str(self.assets.sound_path("bg_music")))
        self.hud              = GameHUD(self.game_state, self.tower_config, self.panel_manager)
        self.tower_controller = TowerPlacementController(self.towers, self.tower_config, self.assets, self.audio, self.game_state, self.camera, self.panel_manager, self.tilemap.buildable_grid, self.tilemap.map_width)

        self.menu_bg = MenuBackground(self.tilemap.pre_render(), self.size)
        self.menu_overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self.menu_overlay.fill((0, 0, 0, 120))
        self.splash = SplashScreen(["assets/images/others/pygame_logo.png"],fade_ms=1500, hold_ms=1000)
        self._init_wave_manager()

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
        if self.panel_manager.current_panel != "game": return
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
        if self.panel_manager.current_panel == "main_menu":
            self._handle_main_menu_event(event)
        elif self.panel_manager.current_panel == "contact":
            self._handle_contact_event(event)
        elif self.panel_manager.current_panel == "game":
            self._handle_game_event(event)
        self.panel_manager.handle_event(event, self.mouse.position)

    def _handle_main_menu_event(self, event) -> None:
        objects = self.panel_manager["main_menu"]
        if objects["play"].is_clicked(event, self.mouse.position):
            self.panel_manager.current_panel = "game"
        elif objects["contact"].is_clicked(event, self.mouse.position):
            self.panel_manager.current_panel = "contact"
        elif objects["exit"].is_clicked(event, self.mouse.position):
            self.on_exit()
        if objects["music_toggle"].is_clicked(event, self.mouse.position):
            self._toggle_music()

    def _handle_contact_event(self, event) -> None:
        panel = self.panel_manager["contact"]
        if panel["back"].is_clicked(event, self.mouse.position):
            self.panel_manager.current_panel = "main_menu"
        if panel["music_toggle"].is_clicked(event, self.mouse.position):
            self._toggle_music()

    def _handle_game_event(self, event) -> None:
        if self.panel_manager["game"]["menu_button"].is_clicked(event, self.mouse.position):
            self.panel_manager.current_panel = "main_menu"
            self.game_state.is_started = False
            return
        self.camera.handle_event(event, self.mouse.position)
        self.tower_controller.handle_event(event, self.mouse.position)
        self._handle_upgrade_plane_button(event)
        self._handle_start_pause(event)
        self._handle_x2(event)

    def _handle_upgrade_plane_button(self, event) -> None:
        panel = self.panel_manager["game"]
        if not panel["upgrade_plane_button"].is_clicked(event, self.mouse.position): return
        if self.game_state.money >= 5000 and self.game_state.plane_level == 1:
            self.game_state.decrease_money(5000)
            panel["buy_tower_4"].set_state("lvl2")
            self.game_state.plane_level = 2

    def _handle_start_pause(self, event) -> None:
        btn = self.panel_manager["game"]["start_pause_button"]
        if not btn.is_clicked(event, self.mouse.position): return
        self.game_state.is_started = not self.game_state.is_started
        btn.set_state("pause" if self.game_state.is_started else None)

    def _handle_x2(self, event) -> None:
        x2 = self.panel_manager["game"]["x2"]
        if not x2.is_clicked(event, self.mouse.position): return
        if self.game_state.speed == 1:
            self.game_state.speed = 2
            x2.set_state("active")
        else:
            self.game_state.speed = 1
            x2.set_state(None)

    def _toggle_music(self) -> None:
        self.audio.toggle_music()
        state = "paused" if self.audio.is_music_paused else None
        for tab in ("main_menu", "contact"):
            self.panel_manager[tab]["music_toggle"].set_state(state)

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

        _draw_tilemap(self)
        _draw_towers(self)
        _draw_enemies(self)
        self.tower_controller.draw(self.window, self.mouse.position)
        self._draw_selected_tower_ui()

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
            self.mouse.info,
            self.camera.info,
            self.panel_manager["main_menu"]["play"].info,
        ]
        Debug.draw(self.window, pygame.font.SysFont("Consolas", 20), debug_info)

    # ── exit ──────────────────────────────────────────────────────────────────

    @override
    def on_exit(self):
        if self.panel_manager.current_panel == "main_menu":
            self.exit()
        elif self.panel_manager.current_panel in ("contact", "game"):
            self.panel_manager.current_panel = "main_menu"
            self.game_state.is_started = False