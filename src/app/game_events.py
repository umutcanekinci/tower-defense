import pygame


def _activate_on_click_or_space(button, event, mouse_position) -> bool:
    if button.is_clicked(event, mouse_position):
        return True
    if event.type == pygame.KEYUP and event.key in (pygame.K_SPACE, pygame.K_RETURN) and getattr(button, "focused", False):
        return True
    return False


class GameEventsMixin:
    """Per-panel input dispatch for Game.

    Game owns a `self.handlers` dict mapping panel name → handler; the base
    `handle_event` looks up the current panel and routes to the matching
    method on this mixin. Each handler reads from `self.panel_manager`
    and mutates game state via the surrounding Game.
    """

    def _handle_main_menu_event(self, event) -> None:
        panel = self.panel_manager["main_menu"]
        if _activate_on_click_or_space(panel["play"], event, self.mouse.position):
            self.panel_manager.current_panel = "game"
        elif _activate_on_click_or_space(panel["contact"], event, self.mouse.position):
            self.panel_manager.current_panel = "contact"
        elif _activate_on_click_or_space(panel["exit"], event, self.mouse.position):
            self.on_exit_request()

    def _handle_contact_event(self, event) -> None:
        panel = self.panel_manager["contact"]
        if panel["back"].is_clicked(event, self.mouse.position):
            self.panel_manager.current_panel = "main_menu"

    def _handle_game_event(self, event) -> None:
        panel = self.panel_manager["game"]
        if panel["menu_button"].is_clicked(event, self.mouse.position):
            self.panel_manager.current_panel = "main_menu"
            self.game_state.is_started = False
            return
        self.camera.handle_event(event, self.mouse.position)
        self.tower_controller.handle_event(event, self.mouse.position)
        self._handle_upgrade_plane_button(event)
        self._handle_start_pause(event)
        self._handle_speed_toggle(event)

    def _handle_upgrade_plane_button(self, event) -> None:
        panel = self.panel_manager["game"]
        if not panel["upgrade_plane_button"].is_clicked(event, self.mouse.position):
            return
        if self.game_state.money >= 5000 and self.game_state.plane_level == 1:
            self.game_state.decrease_money(5000)
            panel["buy_tower_4"].set_state("lvl2")
            panel["upgrade_plane_button"].set_state("purchased")
            self.game_state.plane_level = 2

    def _handle_start_pause(self, event) -> None:
        panel = self.panel_manager["game"]
        if not panel["start_pause_button"].is_clicked(event, self.mouse.position):
            return
        self.game_state.is_started = not self.game_state.is_started
        panel["start_pause_button_icon"].set_state("pause" if self.game_state.is_started else None)

    def _handle_speed_toggle(self, event) -> None:
        panel = self.panel_manager["game"]
        button = panel["speed_toggle_button"]
        if not button.is_clicked(event, self.mouse.position):
            return
        next_speed, next_state = {1: (2, "x2_active"), 2: (4, "x4_active")}.get(
            self.game_state.speed, (1, None)
        )
        self.game_state.speed = next_speed
        button.set_state(next_state)

    def _toggle_music(self) -> None:
        self.audio.toggle_music()
        state = "paused" if self.audio.is_music_paused else None
        for tab in self.panel_manager.keys():
            self.panel_manager[tab]["music_toggle_icon"].set_state(state)