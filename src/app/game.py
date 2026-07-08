from pathlib import Path
from typing import override

import pygame
import yaml
from pygame import Rect

from app.game_events import GameEventsMixin
from app.game_save import GameSaveMixin
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
from ui import hp_bar
from ui.menu_background import MenuBackground
from pygame_core.splash_screen import SplashScreen
from pygame_core.save_store import SaveStore
from pygame_core.ecs.game_audio import GameAudio
from gameplay.combat.enemy import Enemy
from ui.game_hud import GameHUD
from domain.game_state import GameState
from pygame_core.ecs.components.transform import Transform
from gameplay.tilemap import Tilemap
from gameplay.combat.tower_placement import TowerPlacementController
from towers import BaseTower, GroundTower
from gameplay.combat.wave_manager import WaveManager

WINDOW_MODE_LABELS = {
    "fullscreen": "FULLSCREEN",
    "borderless": "BORDERLESS",
    "windowed":   "WINDOWED",
}


class Game(GameEventsMixin, GameSaveMixin, Application):
    """Top-level orchestrator.

    Responsibilities: wiring subsystems, routing input per panel,
    and running the update/draw pipeline.
    """

    # ── construction ──────────────────────────────────────────────────────────

    def __init__(self):
        # Guards on_canvas_resized() firing while Application.__init__ (called
        # below) sets up the very first display mode -- game_area/camera/
        # panel_manager don't exist yet at that point. Flipped True once the
        # rest of this constructor has finished building them.
        self._construction_complete = False

        self.settings = yaml.safe_load(Path("config/settings.yaml").read_text())
        window   = self.settings["window"]
        gameplay = self.settings["gameplay"]
        splash   = self.settings["splash"]
        camera   = self.settings["camera"]
        audio    = self.settings["audio"]
        self._default_audio_settings = dict(audio)  # kept for "reset to defaults"

        self.settings_store = SaveStore("settings")
        saved_settings = self.settings_store.load()
        audio["music_volume"] = saved_settings.get("music_volume", audio["music_volume"])
        audio["sfx_volume"]   = saved_settings.get("sfx_volume", audio["sfx_volume"])

        self.save_store      = SaveStore("save")
        self._starting_money = gameplay["starting_money"]
        self._starting_lives = gameplay["starting_lives"]
        # panels.yaml's positions/sizes/font sizes are authored for this
        # resolution; _load_panel_layout() shrinks (never grows) UI chrome
        # by the same factor the canvas falls short of it, so buttons/panels
        # stay fully on-screen at smaller windows instead of overflowing.
        self._authored_ui_size = tuple(window["size"])

        super().__init__(tuple(window["size"]), window["title"], window["fps"], Mouse(TILE_SIZE))
        self._restore_window_mode(saved_settings)

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
        self.audio.set_music_volume(audio["music_volume"])
        self.audio.set_sfx_volume(audio["sfx_volume"])
        self.hud              = GameHUD(self.game_state, self.tower_config, self.panel_manager)
        self.tower_controller = TowerPlacementController(self.towers, self.tower_config, self.assets, self.audio, self.game_state, self.camera, self.panel_manager, self.tilemap.buildable_grid, self.tilemap.map_width, self.game_area)

        # Cached (not cheap -- iterates every tile): reused by _reflow_panels()
        # to rebuild menu_bg at the new size without re-rendering the tilemap.
        self._tilemap_surface = self.tilemap.pre_render()
        self.menu_bg = MenuBackground(self._tilemap_surface, self.size)
        self.menu_overlay = pygame.Surface(self.size, pygame.SRCALPHA)
        self.menu_overlay.fill((0, 0, 0, 120))
        self.splash = SplashScreen([self.assets.image_path("pygame_logo")], fade_ms=splash["fade_ms"], hold_ms=splash["hold_ms"])
        self._init_wave_manager()

        self.click_sound_path = self.assets.sound_path("click")
        self.handlers = {
            "main_menu": self._handle_main_menu_event,
            "play_menu": self._handle_play_menu_event,
            "contact":   self._handle_contact_event,
            "settings":  self._handle_settings_event,
            "game":      self._handle_game_event,
        }
        self._bind_settings_ui()
        self._build_menu_controllers()
        self._construction_complete = True

    def _bind_settings_ui(self) -> None:
        """(Re-)applies live audio/window state to the settings panel's
        sliders and labels -- needed both at startup and after a canvas
        resize rebuilds those objects from scratch."""
        self._refresh_window_size_label()
        self._refresh_window_mode_label()
        settings_panel = self.panel_manager["settings"]
        settings_panel["sfx_volume_slider"].set_value(self.audio.sfx_volume())
        settings_panel["sfx_volume_slider"].on_change = self._on_sfx_volume_changed
        settings_panel["music_volume_slider"].set_value(self.audio.music_volume())
        settings_panel["music_volume_slider"].on_change = self._on_music_volume_changed
        self._refresh_sfx_volume_label()
        self._refresh_music_volume_label()

    def _build_menu_controllers(self) -> None:
        """(Re-)builds the keyboard-nav controllers from the current panel
        objects -- they hold direct button references, so a canvas resize
        (which rebuilds those objects) must rebuild these too."""
        main_menu_buttons = [self.panel_manager["main_menu"][n] for n in ("play", "contact", "settings", "exit")]
        play_menu_buttons = [self.panel_manager["play_menu"][n] for n in ("new_game", "continue_game", "back")]
        self.menu_controllers = {
            "main_menu": MenuController(
                main_menu_buttons,
                self.audio,
                self.assets.sound_path("switch_up"),
                self.assets.sound_path("switch_down"),
            ),
            "play_menu": MenuController(
                play_menu_buttons,
                self.audio,
                self.assets.sound_path("switch_up"),
                self.assets.sound_path("switch_down"),
            ),
        }

    def load_panels(self, window_transform) -> None:
        self.assets.load_manifest("config/assets.yaml")
        missing = self.assets.validate()
        if missing:
            raise RuntimeError("Missing assets:\n" + "\n".join(missing))
        self._load_panel_layout(window_transform)

    def _load_panel_layout(self, window_transform) -> None:
        """The YAML-parsing half of load_panels(), split out so a canvas
        resize can re-run just this part (positions/sizes depend on the
        window_transform passed in) without re-parsing config/assets.yaml."""
        loader = PanelLoaderExt(self.panel_manager, window_transform, self.assets)
        loader.authored_size = self._authored_ui_size
        loader.scale = min(
            1.0,
            window_transform.width  / self._authored_ui_size[0],
            window_transform.height / self._authored_ui_size[1],
        )
        loader.register("object", panel_factory.make_factory(self.assets), default=True)
        loader.register("text", panel_factory.make_text_factory(self.assets))
        loader.register("animated", panel_factory.make_animated_factory(self.assets))
        loader.register("slider", panel_factory.make_slider_factory(self.assets))
        loader.load("config/panels.yaml")

    def _refresh_window_size_label(self) -> None:
        w, h = self.resolution
        self.panel_manager["settings"]["window_size_value_text"].set_text(f"{w}x{h}")

    def _refresh_window_mode_label(self) -> None:
        self.panel_manager["settings"]["window_mode_value_text"].set_text(WINDOW_MODE_LABELS[self._window_mode])

    def _refresh_sfx_volume_label(self) -> None:
        self.panel_manager["settings"]["sfx_volume_value_text"].set_text(f"{round(self.audio.sfx_volume() * 100)}%")

    def _refresh_music_volume_label(self) -> None:
        self.panel_manager["settings"]["music_volume_value_text"].set_text(f"{round(self.audio.music_volume() * 100)}%")

    # ── settings persistence ─────────────────────────────────────────────────

    def _restore_window_mode(self, saved_settings: dict) -> None:
        """Applies a saved window mode/size on top of Application.__init__'s
        default (always exclusive fullscreen). set_resolution() only resizes
        immediately if already windowed (mode and resolution are independent
        settings) -- called here while still in the just-constructed default
        fullscreen, it just remembers the size for whichever mode is applied
        next, below."""
        if "window_size" in saved_settings:
            self.set_resolution(tuple(saved_settings["window_size"]))
        mode = saved_settings.get("window_mode", "fullscreen")
        mode_methods = {"fullscreen": self.full_screen, "borderless": self.borderless_full_screen, "windowed": self.minimize}
        mode_methods.get(mode, self.full_screen)()

    def _save_settings(self) -> None:
        self.settings_store.save({
            "window_mode":  self._window_mode,
            "window_size":  list(self.resolution),
            "sfx_volume":   self.audio.sfx_volume(),
            "music_volume": self.audio.music_volume(),
        })

    def _reset_settings(self) -> None:
        """Restores window mode/size and both volumes to config/settings.yaml's
        shipped defaults (not merely the values from the last save), then
        persists immediately -- Reset is a deliberate action, not a live drag,
        so it shouldn't wait for the player to also press Back."""
        self.clear_resolution_override()
        self.full_screen()
        self.audio.set_sfx_volume(self._default_audio_settings["sfx_volume"])
        self.audio.set_music_volume(self._default_audio_settings["music_volume"])

        settings_panel = self.panel_manager["settings"]
        settings_panel["sfx_volume_slider"].set_value(self.audio.sfx_volume())
        settings_panel["music_volume_slider"].set_value(self.audio.music_volume())
        self._refresh_window_size_label()
        self._refresh_window_mode_label()
        self._refresh_sfx_volume_label()
        self._refresh_music_volume_label()
        self._save_settings()

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
        # SplashScreen runs its own loop with direct pygame.display.update()
        # calls, bypassing Application._present()'s scale step -- draw it
        # straight onto the real display surface rather than the offscreen
        # logical canvas, or it would never actually reach the screen.
        self.splash.run(self.display_surface, self.clock, self._fps)
        super().run()

    def _init_wave_manager(self) -> None:
        if not self.tilemap.waypoints:
            raise RuntimeError("TMX has no Paths/polyline; enemies have nowhere to go")
        self.wave_manager = WaveManager(self.tilemap.waypoints, self.assets)

    # ── canvas resize ────────────────────────────────────────────────────────

    @override
    def on_canvas_resized(self, new_size: tuple[int, int]) -> None:
        if not self._construction_complete:
            return  # Application.__init__ is still setting up the first display mode
        self._reflow_camera(new_size)
        self._reflow_panels(new_size)

    def _reflow_camera(self, new_size: tuple[int, int]) -> None:
        """game_area IS camera.rect (same Rect object, shared by reference
        with TowerPlacementController too) -- mutating it in place propagates
        everywhere it's already shared, no reassignment needed."""
        w, h = new_size
        self.game_area.update(0, 0, w, h)
        self.camera.scroll_rect.update(0, 0, w, h)
        self.camera._clamp_offset()

    def _reflow_panels(self, new_size: tuple[int, int]) -> None:
        """Rebuilds every panel object against the new canvas size, reusing
        the existing panel_manager (add_object() overwrites by name, so
        stale objects are simply replaced) rather than replacing it -- that
        keeps TowerPlacementController's stored panel_manager reference
        valid. GameHUD is re-bound rather than reconstructed so its
        already-registered GameState listeners aren't duplicated (GameState
        has no listener-removal mechanism)."""
        self._load_panel_layout(Transform((0, 0), new_size))
        self.hud.rebind_panel(self.panel_manager)
        self._bind_settings_ui()
        self._build_menu_controllers()
        self._sync_game_ui()
        self.menu_bg = MenuBackground(self._tilemap_surface, new_size)
        self.menu_overlay = pygame.Surface(new_size, pygame.SRCALPHA)
        self.menu_overlay.fill((0, 0, 0, 120))

    # ── update ────────────────────────────────────────────────────────────────

    @override
    def update(self) -> None:
        self.panel_manager.update()
        if self.panel_manager.current_panel in ("main_menu", "play_menu", "contact", "settings"):
            self.menu_bg.update()
        if self.panel_manager.current_panel == "settings":
            self._refresh_window_mode_label()  # picks up F11-triggered mode changes
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
                    self.save_store.delete()  # a lost run isn't continuable
                    self.exit()
                continue
            if not self.game_state.is_started:
                continue
            enemy.move(self.game_state.speed)
            if hasattr(enemy, "update_combat"):
                enemy.update_combat(self)
                for bullet in list(enemy.bullets):
                    bullet.update(self)

    # ── event handling ────────────────────────────────────────────────────────

    @override
    def handle_event(self, event):
        self.panel_manager.handle_event(event, self.mouse.position)
        if controller := self.menu_controllers.get(self.panel_manager.current_panel):
            controller.handle_event(event, self.mouse.position)
        if handler := self.handlers.get(self.panel_manager.current_panel):
            handler(event)
        panel = self.panel_manager[self.panel_manager.current_panel]
        if self._activate(panel["music_toggle_button"], event):
            self._toggle_music()

    # ── render pipeline ───────────────────────────────────────────────────────

    @override
    def draw(self):
        self.window.fill((0, 0, 0))
        if self.panel_manager.current_panel == "game":
            self._draw_game()
        elif self.panel_manager.current_panel in ("main_menu", "play_menu", "contact", "settings"):
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
                hp_bar.draw(self.window, self.camera, tower.position, tower.hp, tower.maxHP,
                            force=tower is self.game_state.selected_tower)

        def _draw_enemies(self) -> None:
            for enemy in self.enemies:
                self.camera.draw(self.window, enemy)
                if hasattr(enemy, "draw_muzzle"):
                    enemy.draw_muzzle(self.window, self.camera)
                    for bullet in enemy.bullets:
                        self.camera.draw(self.window, bullet)
                hp_bar.draw(self.window, self.camera, enemy.position, enemy.hp, enemy.maxHP)

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
        panel = self.panel_manager.current_panel
        if panel == "main_menu":
            self.exit()
        elif panel in ("play_menu", "contact", "settings", "game"):
            if panel == "settings":
                self._save_settings()
            elif panel == "game":
                self.game_state.is_started = False
                self._save_game()
            self.panel_manager.current_panel = "main_menu"

    @override
    def exit(self) -> None:
        self._save_settings()
        super().exit()