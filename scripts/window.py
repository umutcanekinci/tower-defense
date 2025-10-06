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

<<<<<<< HEAD
        self.SetTitle(self.title)
=======
        self.set_title(self.title)
>>>>>>> master

        #-# Setting the Window Center of the Screen #-#
        os.environ['SDL_VIDEO_CENTERED'] = '1'	
		
<<<<<<< HEAD
    def OpenWindow(self):
        if self.fullScreen:
            self.MakeFullScreen()
        else:
            self.MakeMinimizeScreen()


    def SetTitle(self, title):
        pygame.display.set_caption(title)
    def GetWidth(self):
        return self.get_height()
    def GetHeight(self):
        return self.get_width()
    def GetSize(self):
        return self.get_size()
    
    def MakeFullScreen(self):
        pygame.transform.scale(self, self.Scale(self.get_width(), self.get_height(), self.get_width(), self.get_height(), self.fullScreenWidth, self.fullScreenHeight))
        self.fullScreen = True
        self.screen = pygame.display.set_mode(self.fullScreenSize, 0, 32)# 0, 32 or pygame.FULLSCREEN

    def MakeMinimizeScreen(self):
        pygame.transform.scale(self, self.Scale(self.get_width(), self.get_height(), self.get_width(), self.get_height(), self.minimizeWidth, self.minimizeHeight))
        self.fullScreen = False
        self.screen = pygame.display.set_mode(self.minimizeSize, 0, 32)# 0, 32 or pygame.FULLSCREEN

    def Scale(self, oldWidth, oldHeight, resOldWidth, resOldHeight, resNewWidth ,resNewHeight):
=======
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
>>>>>>> master
        scaleWidth = resNewWidth / resOldWidth
        scaleHeight = resNewHeight / resOldHeight
        newWidth = scaleWidth*oldWidth
        newHeight = scaleHeight*oldHeight
        return (newWidth, newHeight)

<<<<<<< HEAD
    def Draw(self):
=======
    def draw(self):
>>>>>>> master
        self.screen.blit(self, (0, 0))
