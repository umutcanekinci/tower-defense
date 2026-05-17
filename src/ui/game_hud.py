import pygame
from pygame_core.asset_manager import AssetManager
from pygame_core.panel_manager import PanelManager

from pygame_core.unity.state_object import StateObject
from domain.game_state import GameState, TowerConfig
from pygame_core.unity.components.transform import Transform


class GameHUD:
	def __init__(self, assets: AssetManager, window_transform: Transform,
	             game_state: GameState, tower_config: TowerConfig,
	             panel_manager: PanelManager) -> None:
		self._game_state = game_state
		self._tower_config = tower_config

		self.live_texts = [
			StateObject(window_transform, (1700, 234), (80, 80), assets.image_path(f"digit_{i}"))
			for i in range(game_state.lives)
		]
		self.live_text0 = StateObject(window_transform, (1740, 234), (80, 80), assets.image_path("digit_0"))

		self.money_text  = panel_manager["game"]["money_text"]
		self.money_text.set_text(str(game_state.money))
		self.level_text  = panel_manager["game"]["level_text"]
		self.dollar_text = panel_manager["game"]["dollar_text"]

		self.fee_texts = [panel_manager["game"][f"fee_text_{i + 1}"] for i in range(4)]
		for i, fee_text in enumerate(self.fee_texts):
			fee_text.set_text(f"{tower_config.prices[i][0]} $")

		game_state.add_money_listener(self._on_money_changed)
		game_state.add_level_listener(self._on_level_changed)
		self._check_purchasing_power(game_state.money)

	def _on_money_changed(self, money: int) -> None:
		self.money_text.set_text(str(money))
		self._check_purchasing_power(money)

	def _on_level_changed(self, level: int) -> None:
		self.level_text.set_text("Level " + str(level))

	def _check_purchasing_power(self, money: int) -> None:
		for i, fee_text in enumerate(self.fee_texts):
			fee_text.set_color("green" if money >= self._tower_config.prices[i][0] else "red")
		color = "red" if money == 0 else "green"
		self.money_text.set_color(color)
		self.dollar_text.set_color(color)

	def draw(self, surface: pygame.Surface) -> None:
		lives = self._game_state.lives
		self.live_texts[lives if lives != 10 else 1].draw(surface)
		if lives == 10:
			self.live_text0.draw(surface)
		for fee_text in self.fee_texts:
			fee_text.draw(surface)