#!/usr/bin/env python3

from typing import override

import pygame
from pygame.locals import Rect
from pygame_core.application import Application
from pygame_core.color import Green, Red, White
from pygame_core.mouse import Mouse
from pygame_core.panel_manager import PanelManager
from pygame_core.panel_loader import PanelLoader

from core.camera import Camera
from core.debug import Debug
from core.guiobject import GuiObject
from core.image import load_image, scale_surface
from core.music_manager import SoundManager
from enemies import Enemy
from game_state import GameState, TowerConfig
from texts import Text
from tiles import Tile, TILEMAP
from towers import BaseTower, TowerFactory
from wave_manager import WaveManager


class Game(Application):
    """Top-level orchestrator.

    Responsibilities reduced to: wiring subsystems together, handling input,
    and running the render pipeline.  All state lives in GameState; enemy
    spawning logic lives in WaveManager; tower behaviour lives in tower classes.
    """

    # ── construction ──────────────────────────────────────────────────────────

    def __init__(self):
        super().__init__((1440, 900), "TOWER DEFENSE", 165, Mouse(64))

        self.game_state = GameState(start_money=10_000, start_lives=10)
        self.game_state.add_money_listener(self._on_money_changed)
        self.game_state.add_level_listener(self._on_level_changed)

        self.tower_config = TowerConfig(
            prices     = [[70],        [350, 1000, 1750], [500, 1250],  [700, 1600]],
            max_levels = [1,            3,                 2,            2          ],
            ranges     = [[150],       [110, 130, 150],   [90, 110],    [35, 35]   ],
            damages    = [[20],        [40,  50,  70 ],   [80, 120],    [100, 200] ],
            speeds     = [[1000],      [2000, 3000, 4000],[5000, 7000], [4, 2]     ],
        )

        self.camera = Camera(Rect((0, 0), (1152, self.size[1])), 22 * 64, 16 * 64)

        # ── UI object dictionaries (menu / contact / game tabs) ────────────────
        self.panel_manager = PanelManager(starting_tab="main_menu")
        menu = ("menu", "main_menu", "contact")

        loader = PanelLoader(self.panel_manager, self.size)
        loader.load("config/panels.yaml")

        self.panel_manager.add_object("game", "start_pause_button", GuiObject(self.size, (1230, 650), (64, 64), "button/start"))

        _music_tabs = ("main_menu", "contact")
        self._music_button_playing = GuiObject(self.size, (20, 20), (64, 64), "button/pauseMusic")
        self._music_button_paused  = GuiObject(self.size, (20, 20), (64, 64), "button/resumeMusic")

        self.panel_manager.add_object_to_all(_music_tabs, "music_toggle", self._music_button_playing)
        self.panel_manager.add_object("game", "buy_tower_4",    GuiObject(self.size, (1302, 455), (128, 128), "towers/buy_tower4"))
        self.panel_manager.add_object("game", "x2",             GuiObject(self.size, (1310, 650), (64, 64), "button/2x"))

        self.live_texts = [GuiObject(self.size, (1275, 195), (64, 64), "numbers/" + str(i)) for i in range(self.game_state.lives)]
        self.live_text0 = GuiObject(self.size, (1305, 195), (64, 64),  "numbers/0")

        # ── fonts ──────────────────────────────────────────────────────────────
        self.font           = pygame.font.SysFont("ComicSansMs", 40)
        self.dollar_font    = pygame.font.SysFont("ComicSansMs", 30)
        self.fee_font       = pygame.font.SysFont("ComicSansMs", 20)

        # ── game-panel texts ──────────────────────────────────────────────────
        self.money_text  = Text(str(self.game_state.money), self.font,        Green, (self.width - 255, 104))
        self.level_text  = Text("Level 1",                  self.font,        White, (self.width - 215, 2))
        self.dollar_text = Text("$",                         self.dollar_font, Green, (self.width - 60,  110))

        self._fee_text_positions = [(1183, 412), (1326, 412), (1183, 602), (1326, 602)]
        self._create_fee_texts()
        self._check_purchasing_power(self.game_state.money)

        self.fee_text_background = scale_surface(
            self.panel_manager["game"]["money_box"].images[GuiObject.STATE.NORMAL].image, (100, 50)
        )
        self.tower_images = [
            load_image("towers/tower1L1"),
            load_image("towers/tower2L1"),
            load_image("towers/tower3L1"),
            load_image("towers/tower4L1"),
            load_image("towers/tower4L2"),
        ]

        # ── game-object collections ────────────────────────────────────────────
        self.towers:  list[BaseTower] = []
        self.enemies: list[Enemy]     = []
        self.tilemap                  = TILEMAP

        # ── per-frame cursor state ─────────────────────────────────────────────
        self.cursor_col       = None
        self.cursor_row       = None
        self.buying_tower_type = 0
        self.tower_positions: list[tuple] = []

        # ── tile overlay sprites ───────────────────────────────────────────────
        self.block  = load_image("tiles/block")
        self.enable = load_image("tiles/enable")

        # ── wave manager (set after tiles are loaded in run()) ────────────────
        self.wave_manager: WaveManager | None = None
        self.sound_manager = SoundManager("assets/sounds/bg.mp3")

    # ── IGameContext interface (used by enemies / projectiles) ────────────────

    @property
    def speed(self) -> int:
        return self.game_state.speed

    def increase_money(self, amount: int) -> None:
        self.game_state.increase_money(amount)

    # ── lifecycle ─────────────────────────────────────────────────────────────

    def run(self):
        self._create_tiles()
        self._init_wave_manager()
        super().run()

    def _create_tiles(self) -> None:
        self.tiles: list[Tile] = []
        for row_idx, row in enumerate(self.tilemap):
            for col_idx, tile_type in enumerate(row):
                self.tiles.append(Tile(tile_type, col_idx, row_idx))

    def _init_wave_manager(self) -> None:
        spawn_col, spawn_row = None, None
        for tile in self.tiles:
            col, row = tile.get_first_tile()
            if col is not None:
                spawn_col, spawn_row = col, row
                break

        # Original spawn formula: x = col*64 - 32, y = row*64
        self.wave_manager = WaveManager(
            spawn_x=spawn_col * 64 - 32,
            spawn_y=spawn_row * 64,
        )

    # ── event handling ────────────────────────────────────────────────────────

    @override
    def _handle_event(self, event):
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

        if event.type == pygame.MOUSEBUTTONUP:
            if self.panel_manager["main_menu"]["music_toggle"].is_clicked(event, self.mouse.position):
                self._toggle_music()

    def _handle_contact_event(self, event) -> None:
        if self.panel_manager["contact"]["back"].is_clicked(event, self.mouse.position):
            self.panel_manager.current_panel = "main_menu"
        if event.type == pygame.MOUSEBUTTONUP:
            if self.panel_manager["contact"]["music_toggle"].is_clicked(event, self.mouse.position):
                self._toggle_music()

    def _handle_game_event(self, event) -> None:
        self.camera.update_with_mouse(self.mouse.position)

        if self.mouse.position[0] < 1152:
            ox, oy = self.camera.rect.topleft
            self.cursor_col = (self.mouse.position[0] - ox) // 64
            self.cursor_row = (self.mouse.position[1] - oy) // 64

        if self.panel_manager["game"]["menu"].is_clicked(event, self.mouse.position):
            self.panel_manager.current_panel = "main_menu"
            self.game_state.is_started = False
            return

        if event.type == pygame.MOUSEBUTTONUP:
            self._handle_tower_actions(event)
            self._handle_tower_selection()
            self._handle_tower_purchase()

        self._handle_upgrade_planes(event)
        self._handle_start_pause(event)
        self._handle_x2(event)
        self._handle_buy_tower_buttons(event)

    def _handle_tower_actions(self, event) -> None:
        for tower in list(self.towers):
            if self.game_state.selected_tower is tower:
                tower.sell(self.mouse.position, self.game_state, self.towers, self.camera)
                tower.upgrade(self.mouse.position, self.game_state, self.camera)

    def _handle_tower_selection(self) -> None:
        if self.buying_tower_type != 0:
            return
        clicked_tower = None
        for tower in self.towers:
            if self.cursor_col == tower.col and self.cursor_row == tower.row:
                clicked_tower = tower
                break
        if clicked_tower and self.game_state.selected_tower is clicked_tower:
            self.game_state.selected_tower = None
        elif clicked_tower:
            self.game_state.selected_tower = clicked_tower
        else:
            self.game_state.selected_tower = None

    def _handle_tower_purchase(self) -> None:
        if self.mouse.position[0] > 1152 or not self.buying_tower_type:
            return
        if (self.cursor_row, self.cursor_col) in self.block_tiles:
            return
        tower = TowerFactory.create(
            self.buying_tower_type, self.cursor_row, self.cursor_col, self.tower_config
        )
        if tower.get_blocking_position() is None:  # Plane — append to back
            self.towers.append(tower)
        else:                                       # Ground — insert below planes
            self.towers.insert(0, tower)
        self.game_state.decrease_money(tower.buy_price)
        self.buying_tower_type = 0

    def _handle_upgrade_planes(self, event) -> None:
        if (
            self.panel_manager["game"]["upgrade_planes"].is_clicked(event, self.mouse.position)
            and self.game_state.money >= 5000
            and self.game_state.plane_level == 1
        ):
            self.game_state.decrease_money(5000)
            self.panel_manager["game"]["buy_tower_4"] = GuiObject(self.size, (1302, 455), (128, 128), "towers/tower4L2")
            self.game_state.plane_level = 2

    def _handle_start_pause(self, event) -> None:
        start_pause_button = self.panel_manager["game"]["start_pause_button"]
        if not start_pause_button.is_clicked(event, self.mouse.position):
            return
        self.game_state.is_started = not self.game_state.is_started
        icon = "button/pause" if self.game_state.is_started else "button/start"
        self.panel_manager["game"]["start_pause_button"] = GuiObject(self.size, (1230, 650), (64, 64), icon)

    def _handle_x2(self, event) -> None:
        if not self.panel_manager["game"]["x2"].is_clicked(event, self.mouse.position): return

        if self.game_state.speed == 1:
            self.game_state.speed = 2
            self.panel_manager["game"]["x2"] = GuiObject(self.size, (1310, 650), (64, 64), "button/2x2")
        else:
            self.game_state.speed = 1
            self.panel_manager["game"]["x2"] = GuiObject(self.size, (1310, 650), (64, 64), "button/2x")

    def _handle_buy_tower_buttons(self, event) -> None:
        for i in range(4):
            btn = self.panel_manager["game"][f"buy_tower_{i + 1}"]
            if btn.is_clicked(event, self.mouse.position):
                self.buying_tower_type = 0 if self.buying_tower_type == i + 1 else i + 1

    # ── money / UI listeners ──────────────────────────────────────────────────

    def _on_money_changed(self, money: int) -> None:
        self.money_text.set(str(money))
        self._check_purchasing_power(money)

    def _on_level_changed(self, level: int) -> None:
        self.level_text.set("Level " + str(level))

    def _toggle_music(self) -> None:
        self.sound_manager.toggle_paused()
        btn = self._music_button_paused if self.sound_manager.is_paused else self._music_button_playing
        for tab in ("main_menu", "contact"):
            self.panel_manager[tab]["music_toggle"] = btn

    def _create_fee_texts(self) -> None:
        self.fee_texts = [
            Text(str(self.tower_config.prices[i][0]) + " $", self.fee_font, Green, pos)
            for i, pos in enumerate(self._fee_text_positions)
        ]

    def _check_purchasing_power(self, money: int) -> None:
        for i, fee_text in enumerate(self.fee_texts):
            fee_text.set_color(Green if money >= self.tower_config.prices[i][0] else Red)

        if money == 0:
            self.money_text.set_color(Red)
            self.dollar_text.set_color(Red)
        else:
            self.money_text.set_color(Green)
            self.dollar_text.set_color(Green)

    # ── render pipeline ───────────────────────────────────────────────────────

    @override
    def draw(self):
        self.panel_manager.draw(self.window)

        if self.panel_manager.current_panel == "game":
            self._draw_tiles()
            self._draw_towers()
            self._draw_enemies()
            self._draw_game_borders()
            self._draw_game_objects()

            if self.buying_tower_type:
                self._draw_buying_tower()

    def _draw_tiles(self) -> None:
        for tile in self.tiles:
            tile.draw(self.window, self.camera)

    def _draw_game_borders(self) -> None:
        lines = [
            ((1, 0),    (1, 1440),    4),
            ((1151, 0), (1151, 900),  4),
            ((1437, 0), (1437, 900),  4),
            ((0, 1),    (1440, 1),    4),
            ((1150, 65),  (1440, 65),  4),
            ((1150, 200), (1440, 200), 4),
            ((1150, 255), (1438, 255), 4),
            ((1150, 640), (1440, 640), 4),
            ((1150, 720), (1440, 720), 4),
            ((1150, 810), (1440, 810), 4),
            ((0, 897),  (1440, 897),  4),
        ]
        for start, end, width in lines:
            pygame.draw.line(self.window, White, start, end, width)

    def _draw_towers(self) -> None:
        self.tower_positions = []

        for tower in [t for t in self.towers if t.should_remove()]:
            self.towers.remove(tower)

        for tower in self.towers:
            tower.update_and_draw(self.game_state, self.enemies, self.camera, self.window)

            pos = tower.get_blocking_position()
            if pos:
                self.tower_positions.append(pos)

            for bullet in tower.bullets:
                if self.game_state.is_started:
                    bullet.update(self)
                self.camera.draw(self.window, bullet)

    def _draw_enemies(self) -> None:
        if self.wave_manager:
            self.wave_manager.update(self.enemies, self.game_state)

        for enemy in list(self.enemies):
            if enemy.position.x >= self.width - 32:
                self.enemies.remove(enemy)
                self.game_state.lives = max(0, self.game_state.lives - enemy.damage)
                if self.game_state.lives == 0:
                    self.exit()
            elif self.game_state.is_started:
                enemy.move(self.tilemap, self.game_state.speed)
                self.camera.draw(self.window, enemy)
            else:
                self.camera.draw(self.window, enemy)

    def _draw_game_objects(self) -> None:
        lives = self.game_state.lives
        self.live_texts[lives if lives != 10 else 1].draw(self.window)
        if lives == 10:
            self.live_text0.draw(self.window)

        self.level_text.draw(self.window)
        self.money_text.draw(self.window)
        self.dollar_text.draw(self.window)

        for x, y in [(1173, 399), (1316, 399), (1173, 589), (1316, 589)]:
            self.window.blit(self.fee_text_background, (x, y))
        for fee_text in self.fee_texts:
            fee_text.draw(self.window)

    def _draw_buying_tower(self) -> None:
        self.block_tiles: list[tuple] = []
        ox, oy = self.camera.rect.topleft

        for row_idx, row in enumerate(self.tilemap):
            for col_idx, tile in enumerate(row):
                sx = 64 * col_idx + ox
                sy = 64 * row_idx + oy
                buildable = (
                    (tile[0] in ("0", "3"))
                    and (row_idx, col_idx) not in self.tower_positions
                ) or self.buying_tower_type == 4
                if buildable:
                    self.window.blit(self.enable, (sx, sy))
                else:
                    self.window.blit(self.block, (sx, sy))
                    self.block_tiles.append((row_idx, col_idx))

        index = (
            4 if self.buying_tower_type == 4 and self.game_state.plane_level == 2
            else self.buying_tower_type - 1
        )
        mx, my = self.mouse.position
        if mx >= 1152:
            self.window.blit(self.tower_images[index], (mx - 32, my - 32))
        else:
            self.window.blit(self.tower_images[index], (self.cursor_col * 64 + ox, self.cursor_row * 64 + oy))

            draw_range = self.tower_config.ranges[self.buying_tower_type - 1][0]
            surf = pygame.Surface((draw_range * 2, draw_range * 2), pygame.SRCALPHA, 32)
            pygame.draw.circle(surf, (128, 128, 128, 120), (draw_range, draw_range), draw_range, 0)
            blocked = (self.cursor_row, self.cursor_col) in self.block_tiles
            outline_color = (255, 0, 0, 120) if blocked else (0, 200, 0, 120)
            pygame.draw.circle(surf, outline_color, (draw_range, draw_range), draw_range, 5)
            self.window.blit(surf, (
                self.cursor_col * 64 + 32 - draw_range + ox,
                self.cursor_row * 64 + 32 - draw_range + oy,
            ))

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
        debug_font = pygame.font.SysFont("Consolas", 20)
        Debug.draw(self.window, debug_font, debug_info)

    # ── exit ──────────────────────────────────────────────────────────────────

    @override
    def on_exit(self):
        if self.panel_manager.current_panel == "main_menu":
            self.exit()
        elif self.panel_manager.current_panel in ("contact", "game"):
            self.panel_manager.current_panel = "main_menu"
            self.game_state.is_started = False


if __name__ == "__main__":
    game = Game()
    game.run()
