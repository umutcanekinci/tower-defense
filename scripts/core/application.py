import pygame
import sys
from pygame import mixer
import os
from core.mouse import Mouse

class Application():
    def __init__(self, size: tuple[int, int], title: str, fps: int) -> None:
        self.fps = fps
        self.is_in_debug_mode = False
        self.mouse_pos = (0, 0)
        self.is_running = True
        self.mouse = Mouse(64)
        pygame.init()
        mixer.init()
        self.set_title(title)
        self.fetch_screen_dimensions(size)
        self.full_screen()
        self.center_window()
        self.clock = pygame.time.Clock()

    def center_window(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'

    def fetch_screen_dimensions(self, size: tuple[int, int]):
        self.infoObject = pygame.display.Info()
        self.full_screen_size = self.fullScreenWidth, self.fullScreenHeight = self.infoObject.current_w, self.infoObject.current_h
        self.minimized_size = self.minimizeWidth, self.minimizeHeight = size
        self.scale = self.fullScreenWidth / self.minimizeWidth, self.fullScreenHeight / self.minimizeHeight

    def set_title(self, title):
        self.title = title
        pygame.display.set_caption(title)

    def minimize(self):
        self.size = self.width, self.height = self.minimized_size
        self.window = pygame.display.set_mode(self.size)

    def full_screen(self):
        self.size = self.width, self.height = self.full_screen_size
        self.window = pygame.display.set_mode(self.size, pygame.FULLSCREEN) # 0, 32 or pygame.FULLSCREEN
  
    def run(self) -> None:
        while self.is_running:
            self.clock.tick(self.fps)
            self.mouse.update()
            self._handle_events()
            self.update()
            self.draw()
            self.draw_debug()
            pygame.display.update()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            self.handle_events(event)

    #region Override these methods in subclasses (Abstract Methods)

    def handle_events(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.on_exit()
            elif event.key == pygame.K_F1:
                    self.is_in_debug_mode = not self.is_in_debug_mode
            elif event.key == pygame.K_F11:
                    self.full_screen() if self.size == self.minimized_size else self.minimize()
            elif event.type == pygame.QUIT:
                self.on_exit()

    def update(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def draw_debug(self) -> None:
        pass

    def on_exit(self) -> None:
        self.exit()

    #endregion

    def exit(self) -> None:
        self.is_running = False
        pygame.quit()
        sys.exit()