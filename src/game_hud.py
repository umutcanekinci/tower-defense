import pygame
from pygame_core.asset_manager import AssetManager
from pygame_core.color import Green, Red, White
from pygame_core.panel_manager import PanelManager

from core.guiobject import GuiObject
from core.image import scale_surface
from game_state import GameState, TowerConfig
from text import Text


class GameHUD:
	def __init__(self, assets: AssetManager, window_size: tuple,
	             game_state: GameState, tower_config: TowerConfig,
	             panel_manager: PanelManager) -> None:
		self._game_state = game_state
		self._tower_config = tower_config
		width = window_size[0]

		font        = pygame.font.SysFont("ComicSansMs", 50)
		dollar_font = pygame.font.SysFont("ComicSansMs", 37)
		fee_font    = pygame.font.SysFont("ComicSansMs", 25)

		self.live_texts = [
			GuiObject(window_size, (1700, 234), (80, 80), assets.image_path(f"digit_{i}"))
			for i in range(game_state.lives)
		]
		self.live_text0 = GuiObject(window_size, (1740, 234), (80, 80), assets.image_path("digit_0"))

		self.money_text  = Text(str(game_state.money), font,        Green, (width - 340, 125))
		self.level_text  = Text("Level 1",             font,        White, (width - 287, 2))
		self.dollar_text = Text("$",                   dollar_font, Green, (width - 80,  132))

		_fee_positions = [(1577, 494), (1768, 494), (1577, 722), (1768, 722)]
		self.fee_texts = [
			Text(str(tower_config.prices[i][0]) + " $", fee_font, Green, pos)
			for i, pos in enumerate(_fee_positions)
		]
		self.fee_text_background = scale_surface(
			panel_manager["game"]["money_box"].images[None].image, (133, 60)
		)

		game_state.add_money_listener(self._on_money_changed)
		game_state.add_level_listener(self._on_level_changed)
		self._check_purchasing_power(game_state.money)

	def _on_money_changed(self, money: int) -> None:
		self.money_text.set(str(money))
		self._check_purchasing_power(money)

	def _on_level_changed(self, level: int) -> None:
		self.level_text.set("Level " + str(level))

	def _check_purchasing_power(self, money: int) -> None:
		for i, fee_text in enumerate(self.fee_texts):
			fee_text.set_color(Green if money >= self._tower_config.prices[i][0] else Red)
		color = Red if money == 0 else Green
		self.money_text.set_color(color)
		self.dollar_text.set_color(color)

	def draw(self, surface: pygame.Surface) -> None:
		lives = self._game_state.lives
		self.live_texts[lives if lives != 10 else 1].draw(surface)
		if lives == 10:
			self.live_text0.draw(surface)
		self.level_text.draw(surface)
		self.money_text.draw(surface)
		self.dollar_text.draw(surface)
		for x, y in [(1564, 479), (1755, 479), (1564, 707), (1755, 707)]:
			surface.blit(self.fee_text_background, (x, y))
		for fee_text in self.fee_texts:
			fee_text.draw(surface)