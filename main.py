import argparse
import math
from pathlib import Path

import blessed

from music_database import MusicDatabase
from music_player import MusicPlayer


def print_progress_bar(term, percentage):
    term.move_xy(0, term.height - 1)
    print("[", end="")

    num_blocks = math.ceil(percentage * term.width)
    print("\N{FULL BLOCK}" * num_blocks, end="")
    print(" " * (term.width - 2 - num_blocks), end="")
    print("]")


class ArtistPane:
    def __init__(self, term, music_database):
        self.term = term
        self.current_artist = 0
        self.music_database = music_database

    def render(self):
        for index, artist in enumerate(music_database.get_artists()):
            if index == self.current_artist:
                print(term.underline(artist))
            else:
                print(artist)

    def process_keystroke(self, val):
        if val.name == "KEY_UP":
            if self.current_artist > 0:
                self.current_artist -= 1
        elif val.name == "KEY_DOWN":
            if self.current_artist < len(music_database.get_artists()) - 1:
                self.current_artist += 1

    def get_current_artist(self):
        return list(self.music_database.get_artists())[self.current_artist]


class SongPane:
    def __init__(self, term, artist, songs):
        self.term = term
        self.artist = artist
        self.songs = songs
        self.current_song = 0

    def set_songs(self, songs):
        self.songs = songs
        self.current_song = 0

    def render(self):
        for index, song in enumerate(self.songs):
            if index == self.current_song:
                print(term.underline(song.title))
            else:
                print(song.title)

    def process_keystroke(self, val):
        if val.name == "KEY_UP":
            if self.current_song > 0:
                self.current_song -= 1
        elif val.name == "KEY_DOWN":
            if self.current_song < len(self.songs) - 1:
                self.current_song += 1

    def get_current_song(self):
        return self.songs[self.current_song]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("music_dir", type=str, help="The directory to play music from")
    args = parser.parse_args()

    music_database = MusicDatabase(args.music_dir)
    term = blessed.Terminal()

    selected_song = 0
    music_player = MusicPlayer()

    artist_pane = ArtistPane(term, music_database)
    song_pane = SongPane(
        term,
        artist_pane.get_current_artist(),
        music_database.artist_map[artist_pane.get_current_artist()],
    )
    active_pane = "artist"
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        val = None
        while val is None or val.lower() != "q":
            print(term.home + term.clear)
            print(term.center("Choose a song (press q to quit)"))

            if val is not None:
                if val.lower() == "a":
                    active_pane = "artist"
                elif val.lower() == "s":
                    active_pane = "song"
                else:
                    if active_pane == "artist":
                        artist_pane.process_keystroke(val)
                    elif active_pane == "song":
                        song_pane.process_keystroke(val)

            artist_pane.render()
            print("")
            song_pane.render()
            print("")
            print(active_pane)

            if val is not None and val.name == "KEY_ENTER":
                if active_pane == "artist":
                    if artist_pane.get_current_artist() != song_pane.artist:
                        song_pane = SongPane(
                            term,
                            artist_pane.get_current_artist(),
                            music_database.artist_map[artist_pane.get_current_artist()],
                        )
                if active_pane == "song":
                    playing_song = song_pane.get_current_song()
                    music_player.play(playing_song.path)

            if music_player.is_playing():
                print("")
                print(term.center(f"Now Playing: {playing_song.title}"))
                print_progress_bar(term, music_player.get_playing_song_percentage())

            val = term.inkey(0.1)