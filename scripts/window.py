import pygame
import os

class Window(pygame.Surface):
    def __init__(self, size, title, fullScreen=False):
        super().__init__(size)

        ###- Properties -###
        self.infoObject = pygame.display.Info()
        self.fullScreenSize = self.fullScreenWidth, self.fullScreenHeight = self.infoObject.current_w, self.infoObject.current_h
        self.minimizeSize = self.minimizeWidth, self.minimizeHeight = size
        self.fullScreen = fullScreen
        self.title = title

        self.set_title(self.title)

        #-# Setting the Window Center of the Screen #-#
        os.environ['SDL_VIDEO_CENTERED'] = '1'	
		
    def open(self):
        self.full_screen() if self.fullScreen else self.minimize()

    def set_title(self, title):
        pygame.display.set_caption(title)

    def full_screen(self):
        pygame.transform.scale(self, self.scale(self.get_width(), self.get_height(), self.get_width(), self.get_height(), self.fullScreenWidth, self.fullScreenHeight))
        self.fullScreen = True
        self.screen = pygame.display.set_mode(self.fullScreenSize, 0, 32)# 0, 32 or pygame.FULLSCREEN

    def minimize(self):
        pygame.transform.scale(self, self.scale(self.get_width(), self.get_height(), self.get_width(), self.get_height(), self.minimizeWidth, self.minimizeHeight))
        self.fullScreen = False
        self.screen = pygame.display.set_mode(self.minimizeSize, 0, 32)# 0, 32 or pygame.FULLSCREEN

    def scale(self, oldWidth, oldHeight, resOldWidth, resOldHeight, resNewWidth ,resNewHeight):
        scaleWidth = resNewWidth / resOldWidth
        scaleHeight = resNewHeight / resOldHeight
        newWidth = scaleWidth*oldWidth
        newHeight = scaleHeight*oldHeight
        return (newWidth, newHeight)

    def draw(self):
        self.screen.blit(self, (0, 0))
