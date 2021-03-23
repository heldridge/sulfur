import os
import pathlib
import time

import mutagen

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame


class NoSongPlayingError(Exception):
    """Used when an operation is called expecting a playing song, but none exists"""

    pass


class MusicPlayer:
    """Handles the logic of loading and playing songs

    Attributes:
        playing_song: The path to the currently playing song
        playing_song_length: The length of the currently playing song in seconds
        playing_song_start_time:
            The unix timestamp of when the current song started playing
    """

    def __init__(self):
        pygame.init()
        self.reset_playing_song()

    def reset_playing_song(self) -> None:
        self.playing_song: pathlib.Path = None
        self.playing_song_length: float = None
        self.playing_song_start_time: float = None

    def play(self, song_path: pathlib.Path):
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play(0)
        self.playing_song = song_path
        mutagen_file = mutagen.File(song_path)

        if mutagen_file is not None:
            self.playing_song_length = mutagen_file.info.length
        else:
            # TODO: don't show progress bar when song length can't be identified
            self.playing_song_length = 999

        self.playing_song_start_time = time.time()

    def is_playing(self) -> bool:
        return pygame.mixer.music.get_busy()

    def get_playing_song_percentage(self) -> float:
        if not pygame.mixer.music.get_busy():
            self.reset_playing_song()
            raise NoSongPlayingError("No song is currently playing")

        return (time.time() - self.playing_song_start_time) / self.playing_song_length
