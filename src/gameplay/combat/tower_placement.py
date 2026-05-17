import pygame
from pygame_core.asset_manager import AssetManager
from pygame_core.panel_manager import PanelManager

from rendering.camera import Camera
from util.constants import TILE_SIZE, HALF_TILE
from domain.game_state import GameState, TowerConfig
from towers import BaseTower, TowerFactory

GAME_AREA_WIDTH = 1536


class TowerPlacementController:
	def __init__(self, towers: list[BaseTower], tower_config: TowerConfig,
	             assets: AssetManager, game_state: GameState,
	             camera: Camera, panel_manager: PanelManager,
	             buildable_grid: list[list[bool]]) -> None:
		self._towers         = towers
		self._tower_config   = tower_config
		self._assets         = assets
		self._game_state     = game_state
		self._camera         = camera
		self._panel_manager  = panel_manager
		self._buildable_grid = buildable_grid

		self.buying_tower_type: int        = 0
		self.cursor_col:        int | None = None
		self.cursor_row:        int | None = None
		self.tower_positions:   list[tuple] = []

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
			world = self._camera.screen_to_world(mouse_pos)
			self.cursor_col = int(world.x // TILE_SIZE)
			self.cursor_row = int(world.y // TILE_SIZE)

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
		if not self._is_placeable(self.cursor_row, self.cursor_col):
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

	def draw(self, surface: pygame.Surface, mouse_pos: tuple) -> None:
		if not self.buying_tower_type:
			return
		self._draw_grid_overlay(surface)
		self._draw_cursor_preview(surface, mouse_pos)

	def _is_placeable(self, row: int | None, col: int | None) -> bool:
		if self.buying_tower_type == 4:
			return True
		if row is None or col is None:
			return False
		if not (0 <= row < len(self._buildable_grid) and 0 <= col < len(self._buildable_grid[0])):
			return False
		if not self._buildable_grid[row][col]:
			return False
		return (row, col) not in self.tower_positions

	def _draw_grid_overlay(self, surface: pygame.Surface) -> None:
		scaled_enable = self._camera.scale_image(self._enable)
		scaled_block  = self._camera.scale_image(self._block)
		for row_idx, row in enumerate(self._buildable_grid):
			for col_idx in range(len(row)):
				screen = self._camera.world_to_screen((col_idx * TILE_SIZE, row_idx * TILE_SIZE))
				tile = scaled_enable if self._is_placeable(row_idx, col_idx) else scaled_block
				surface.blit(tile, screen)

	def _draw_cursor_preview(self, surface: pygame.Surface, mouse_pos: tuple) -> None:
		index = (
			4 if self.buying_tower_type == 4 and self._game_state.plane_level == 2
			else self.buying_tower_type - 1
		)
		mx, my = mouse_pos
		if mx >= GAME_AREA_WIDTH:
			surface.blit(self._tower_images[index], (mx - HALF_TILE, my - HALF_TILE))
			return

		scaled_tower = self._camera.scale_image(self._tower_images[index])
		cell_top_left = self._camera.world_to_screen(
			(self.cursor_col * TILE_SIZE, self.cursor_row * TILE_SIZE))
		surface.blit(scaled_tower, cell_top_left)

		world_range  = self._tower_config.ranges[self.buying_tower_type - 1][0]
		scaled_range = int(world_range * self._camera.scale)
		center = self._camera.world_to_screen(
			(self.cursor_col * TILE_SIZE + HALF_TILE,
			 self.cursor_row * TILE_SIZE + HALF_TILE))
		blocked = not self._is_placeable(self.cursor_row, self.cursor_col)
		self._blit_range_ring(surface, center, scaled_range, blocked)

	@staticmethod
	def _blit_range_ring(surface: pygame.Surface, center, radius: int, blocked: bool) -> None:
		if radius <= 0:
			return
		surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
		pygame.draw.circle(surf, (128, 128, 128, 120), (radius, radius), radius, 0)
		outline = (255, 0, 0, 120) if blocked else (0, 200, 0, 120)
		pygame.draw.circle(surf, outline, (radius, radius), radius, 5)
		surface.blit(surf, (center.x - radius, center.y - radius))