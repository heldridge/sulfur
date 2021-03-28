import os
import pathlib
import time
import sys


import mutagen
import vlc


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
        self.player = None

    def play_playlist(self, new_playlist, index):
        media_list = vlc.MediaList()
        for song_path in new_playlist:
            media_list.add_media(song_path)
        self.play(media_list, index)

    def play_next_song(self, *args):
        self.playing_song_index += 1
        if self.playing_song_index < len(self.playlist):
            self.play()

    def play(self, media_list, index):

        self.player = vlc.MediaListPlayer()
        self.player.set_media_list(media_list)
        self.player.play_item_at_index(index)

        self.playing_song_start_time = time.time()

    def is_playing(self) -> bool:
        if self.player is None:
            return False
        return self.player.is_playing()

    def get_playing_song_length(self):
        return self.player.get_media_player().get_length()

    def toggle_playing(self):
        self.player.pause()
