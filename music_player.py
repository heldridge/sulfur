import os
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame


class NoSongPlayingError(Exception):
    pass


class MusicPlayer:
    def __init__(self):
        pygame.init()
        self.reset_playing_song()

    def reset_playing_song(self):
        self.playing_song = None
        self.playing_song_length = None
        self.playing_song_start_time = None

    def play(self, song_path):
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(0)
        self.playing_song = song_path
        self.playing_song_length = pygame.mixer.Sound(song_path).get_length()
        self.playing_song_start_time = time.time()

    def is_playing(self):
        return pygame.mixer.music.get_busy()

    def get_playing_song_percentage(self):

        if not pygame.mixer.music.get_busy():
            self.reset_playing_song()
            raise NoSongPlayingError("No song is currently playing")

        return (time.time() - self.playing_song_start_time) / self.playing_song_length
