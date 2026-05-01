from typing import override

import pygame
from pygame.locals import Rect
from pygame_core.application import Application
from pygame_core.asset_manager import AssetManager
from pygame_core.color import White
from pygame_core.mouse import Mouse
from pygame_core.panel_manager import PanelManager
from pygame_core.panel_loader_ext import PanelLoaderExt

import panel_factory
from config_loader import load_tower_config
from core.camera import Camera
from core.debug import Debug
from core.menu_background import MenuBackground
from core.music_manager import SoundManager
from core.splash_screen import SplashScreen
from enemy import Enemy
from game_hud import GameHUD
from game_state import GameState
from tile import TILEMAP, Tilemap
from tower_placement import TowerPlacementController
from towers import BaseTower
from wave_manager import WaveManager


class Game(Application):
    """Top-level orchestrator.

    Responsibilities: wiring subsystems, routing input per panel,
    and running the update/draw pipeline.
    """

    # ── construction ──────────────────────────────────────────────────────────

    def __init__(self):
        super().__init__((1920, 1080), "TOWER DEFENSE", 165, Mouse(64))

        self.game_state   = GameState(start_money=10_000, start_lives=10)
        self.tower_config = load_tower_config()
        self.camera       = Camera(Rect((0, 0), (1536, self.size[1])), 22 * 64, 16 * 64)

        self.assets = AssetManager()
        self.assets.load_manifest("config/assets.yaml")
        missing = self.assets.validate()
        if missing:
            raise RuntimeError("Missing assets:\n" + "\n".join(missing))

        self.panel_manager = PanelManager(starting_tab="main_menu")
        loader = PanelLoaderExt(self.panel_manager, self.size, self.assets)
        loader.register("object", panel_factory.make_factory(self.assets), default=True)
        loader.register("text",   panel_factory.make_text_factory(self.assets))
        loader.load("config/panels.yaml")

        self.towers:       list[BaseTower] = []
        self.enemies:      list[Enemy]     = []
        self.level         = TILEMAP
        self.tilemap       = Tilemap(TILEMAP, self.assets)
        self.wave_manager: WaveManager | None = None
        self.sound_manager = SoundManager(str(self.assets.sound_path("bg_music")))

        self.hud = GameHUD(self.assets, self.size, self.game_state, self.tower_config, self.panel_manager)

        self.tower_controller = TowerPlacementController(
            self.towers, self.tower_config, self.assets, self.game_state,
            self.camera, self.panel_manager)

    # ── IGameContext interface ────────────────────────────────────────────────

    @property
    def speed(self) -> int:
        return self.game_state.speed

    @property
    def map_width(self) -> int:
        return len(self.level[0]) * 64

    @property
    def map_height(self) -> int:
        return len(self.level) * 64

    def increase_money(self, amount: int) -> None:
        self.game_state.increase_money(amount)

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def run(self):
        SplashScreen(
            ["assets/images/others/pygame_logo.png", "assets/images/others/kenney_logo.png"],
            fade_ms=1500, hold_ms=1000,
        ).run(self.window, self.clock, self._fps)
        self.tilemap.create_tiles()
        self._init_wave_manager()
        self.menu_bg = MenuBackground(
            self.tilemap, len(self.level[0]), len(self.level), self.size)
        self.menu_overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self.menu_overlay.fill((0, 0, 0, 120))
        super().run()

    def _init_wave_manager(self) -> None:
        spawn_col, spawn_row = self.tilemap.get_spawn_tile()
        assert spawn_col is not None and spawn_row is not None, "No spawn tile found in level data"
        self.wave_manager = WaveManager(spawn_x=spawn_col * 64 - 32, spawn_y=spawn_row * 64)

    # ── update ────────────────────────────────────────────────────────────────

    @override
    def update(self) -> None:
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
            if enemy.position.x >= self.map_width - 32:
                self.enemies.remove(enemy)
                self.game_state.lives = max(0, self.game_state.lives - enemy.damage)
                if self.game_state.lives == 0:
                    self.exit()
            elif self.game_state.is_started:
                enemy.move(self.level, self.game_state.speed)

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
        self.sound_manager.handle_event(event)

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
        if self.panel_manager["game"]["menu"].is_clicked(event, self.mouse.position):
            self.panel_manager.current_panel = "main_menu"
            self.game_state.is_started = False
            return
        self.tower_controller.handle_event(event, self.mouse.position)
        self._handle_upgrade_planes(event)
        self._handle_start_pause(event)
        self._handle_x2(event)

    def _handle_upgrade_planes(self, event) -> None:
        panel = self.panel_manager["game"]
        if not panel["upgrade_planes"].is_clicked(event, self.mouse.position): return
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
        self.sound_manager.toggle_paused()
        state = "paused" if self.sound_manager.is_paused else None
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

    def _draw_game(self) -> None:
        self.tilemap.draw(self.window, self.camera)
        self._draw_towers()
        self._draw_enemies()
        self._draw_game_borders()
        self.hud.draw(self.window)
        self.tower_controller.draw(self.window, self.level, self.mouse.position)

    def _draw_game_borders(self) -> None:
        lines = [
            ((1,    0),    (1,    1080), 4),
            ((1535, 0),    (1535, 1080), 4),
            ((1916, 0),    (1916, 1080), 4),
            ((0,    1),    (1920, 1),    4),
            ((1534, 78),   (1920, 78),   4),
            ((1534, 240),  (1920, 240),  4),
            ((1534, 306),  (1917, 306),  4),
            ((1534, 768),  (1920, 768),  4),
            ((1534, 864),  (1920, 864),  4),
            ((1534, 972),  (1920, 972),  4),
            ((0,    1076), (1920, 1076), 4),
        ]
        for start, end, width in lines:
            pygame.draw.line(self.window, White, start, end, width)

    def _draw_towers(self) -> None:
        for tower in self.towers:
            tower.draw(self.game_state, self.camera, self.window)
            for bullet in tower.bullets:
                self.camera.draw(self.window, bullet)

    def _draw_enemies(self) -> None:
        for enemy in self.enemies:
            self.camera.draw(self.window, enemy)

    # ── debug ─────────────────────────────────────────────────────────────────

    @override
    def draw_debug(self):
        if not self._is_in_debug_mode:
            return
        debug_info = [
            self.mouse.get_info(),
            self.camera.get_info(),
            self.panel_manager["main_menu"]["play"].get_info(),
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