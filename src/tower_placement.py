import pygame
from pygame_core.asset_manager import AssetManager
from pygame_core.panel_manager import PanelManager

from core.camera import Camera
from game_state import GameState, TowerConfig
from towers import BaseTower, TowerFactory

GAME_AREA_WIDTH = 1536


class TowerPlacementController:
	def __init__(self, towers: list[BaseTower], tower_config: TowerConfig,
	             assets: AssetManager, game_state: GameState,
	             camera: Camera, panel_manager: PanelManager) -> None:
		self._towers        = towers
		self._tower_config  = tower_config
		self._assets        = assets
		self._game_state    = game_state
		self._camera        = camera
		self._panel_manager = panel_manager

		self.buying_tower_type: int        = 0
		self.cursor_col:        int | None = None
		self.cursor_row:        int | None = None
		self.tower_positions:   list[tuple] = []
		self.block_tiles:       list[tuple] = []

		self._block  = assets.get_image("tile_block")
		self._enable = assets.get_image("tile_enable")
		self._tower_images = [
			assets.get_image("tower_1_lvl1"),
			assets.get_image("tower_2_lvl1"),
			assets.get_image("tower_3_lvl1"),
			assets.get_image("tower_4_lvl1"),
			assets.get_image("tower_4_lvl2"),
		]

	def update_cursor(self, mouse_pos: tuple) -> None:
		if mouse_pos[0] < GAME_AREA_WIDTH:
			ox, oy = self._camera.rect.topleft
			self.cursor_col = (mouse_pos[0] - ox) // 64
			self.cursor_row = (mouse_pos[1] - oy) // 64

	def is_construct_mode(self) -> bool:
		return self.buying_tower_type != 0

	def get_clicked_tower(self) -> BaseTower | None:
		for tower in self._towers:
			if self.cursor_col == tower.col and self.cursor_row == tower.row:
				return tower
		return None

	def handle_event(self, event, mouse_pos: tuple) -> None:
		if event.type == pygame.MOUSEBUTTONUP:
			self._handle_tower_actions(event, mouse_pos)
			self._handle_tower_selection()
			self._handle_tower_purchase(mouse_pos)
		self._handle_buy_tower_buttons(event, mouse_pos)

	def _handle_tower_actions(self, event, mouse_pos: tuple) -> None:
		for tower in self._towers:
			if self._game_state.selected_tower is not tower:
				continue
			tower.sell(mouse_pos, self._game_state, self._towers, self._camera)
			tower.upgrade(mouse_pos, self._game_state, self._camera)

	def _handle_tower_selection(self) -> None:
		if self.is_construct_mode():
			return
		clicked = self.get_clicked_tower()
		if not clicked:
			self._game_state.selected_tower = None
			return
		is_selected = self._game_state.selected_tower is clicked
		self._game_state.selected_tower = None if is_selected else clicked

	def _handle_tower_purchase(self, mouse_pos: tuple) -> None:
		if mouse_pos[0] > GAME_AREA_WIDTH or not self.buying_tower_type:
			return
		if (self.cursor_row, self.cursor_col) in self.block_tiles:
			return
		tower = TowerFactory.create(
			self.buying_tower_type, self.cursor_row, self.cursor_col,
			self._tower_config, self._assets)
		if tower.get_blocking_position() is None:
			self._towers.append(tower)
		else:
			self._towers.insert(0, tower)
		self._game_state.decrease_money(tower.buy_price)
		self.buying_tower_type = 0

	def _handle_buy_tower_buttons(self, event, mouse_pos: tuple) -> None:
		for i in range(4):
			btn = self._panel_manager["game"][f"buy_tower_{i + 1}"]
			if btn.is_clicked(event, mouse_pos):
				self.buying_tower_type = 0 if self.buying_tower_type == i + 1 else i + 1

	def draw(self, surface: pygame.Surface, level: list, mouse_pos: tuple) -> None:
		if not self.buying_tower_type:
			return
		self.block_tiles = []
		ox, oy = self._camera.rect.topleft

		for row_idx, row in enumerate(level):
			for col_idx, tile in enumerate(row):
				sx = 64 * col_idx + ox
				sy = 64 * row_idx + oy
				buildable = (
					(tile[0] in ("0", "3")) and (row_idx, col_idx) not in self.tower_positions
				) or self.buying_tower_type == 4
				if buildable:
					surface.blit(self._enable, (sx, sy))
				else:
					surface.blit(self._block, (sx, sy))
					self.block_tiles.append((row_idx, col_idx))

		index = (
			4 if self.buying_tower_type == 4 and self._game_state.plane_level == 2
			else self.buying_tower_type - 1
		)
		mx, my = mouse_pos
		if mx >= GAME_AREA_WIDTH:
			surface.blit(self._tower_images[index], (mx - 32, my - 32))
		else:
			surface.blit(self._tower_images[index], (self.cursor_col * 64 + ox, self.cursor_row * 64 + oy))
			draw_range = self._tower_config.ranges[self.buying_tower_type - 1][0]
			surf = pygame.Surface((draw_range * 2, draw_range * 2), pygame.SRCALPHA, 32)
			pygame.draw.circle(surf, (128, 128, 128, 120), (draw_range, draw_range), draw_range, 0)
			blocked = (self.cursor_row, self.cursor_col) in self.block_tiles
			outline_color = (255, 0, 0, 120) if blocked else (0, 200, 0, 120)
			pygame.draw.circle(surf, outline_color, (draw_range, draw_range), draw_range, 5)
			surface.blit(surf, (
				self.cursor_col * 64 + 32 - draw_range + ox,
				self.cursor_row * 64 + 32 - draw_range + oy,
			))