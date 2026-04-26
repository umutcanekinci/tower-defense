from pygame import mixer
import pygame

class SoundManager:
    def __init__(self, path: str, start_on_play: bool=True) -> None:
        self.music_path = path
        self.is_paused = True

        self.ON_MUSIC_END   = pygame.USEREVENT
        mixer.music.set_endevent(self.ON_MUSIC_END)

        if start_on_play:
            self.start_music()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == self.ON_MUSIC_END:
            self.start_music()

    def start_music(self) -> None:
        if not self.is_paused: return

        mixer.music.load(self.music_path)
        mixer.music.play()
        self.is_paused = False

    def toggle_paused(self) -> None:
        if self.is_paused:
            self.resume_music()
        else:
            self.pause_music()

    def resume_music(self) -> None:
        if not self.is_paused: return

        mixer.music.unpause()
        self.is_paused = False

    def pause_music(self) -> None:
        if self.is_paused: return

        mixer.music.pause()
        self.is_paused = True