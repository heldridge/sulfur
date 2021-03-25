import argparse
import math
from pathlib import Path

import blessed

from list_pane import ListPane
from music_database import MusicDatabase
from music_player import MusicPlayer


def print_progress_bar(term, percentage):
    num_blocks = math.ceil(percentage * term.width)
    print(
        term.move_xy(0, term.height - 1)
        + "["
        + "\N{FULL BLOCK}" * num_blocks
        + " " * (term.width - 2 - num_blocks)
        + "]",
    )


class ArtistPane:
    def __init__(self, term, music_database):
        self.term = term
        self.current_artist = 0
        self.music_database = music_database

    def render(self, active):
        for index, artist in enumerate(music_database.get_artists()):
            if active and index == self.current_artist:
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


class SongPaneOld:
    def __init__(self, term, artist, songs):
        self.term = term
        self.artist = artist
        self.songs = songs
        self.current_song = 0
        self.height = 15

        self.songs_offset = 0

    def set_songs(self, songs):
        self.songs = songs
        self.current_song = 0

    def render(self, active):
        for index, song in enumerate(self.songs[self.songs_offset :]):
            song_string = song.title
            if active and index == self.current_song - self.songs_offset:
                song_string = term.underline(song.title)

            print(term.move_xy(50, index + 2) + song_string)
            if index >= self.height:
                print(term.move_xy(50, index + 3) + "...")
                break

    def process_keystroke(self, val):
        if val.name == "KEY_UP":
            if self.current_song > 0:
                self.current_song -= 1

            if self.songs_offset > 0:
                self.songs_offset -= 1
        elif val.name == "KEY_DOWN":
            if self.current_song < len(self.songs) - 1:
                self.current_song += 1

            if self.songs_offset + self.height < len(self.songs):
                self.songs_offset += 1

    def get_current_song(self):
        return self.songs[self.current_song]


class SongPane(ListPane):
    def __init__(self, term, artist, songs):
        super().__init__(term, songs, 50, 20, (50, 2))
        self.artist = artist

    def get_item_string(self, item):
        return item.title

    def get_current_song(self):
        return self.items[self.current_item]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("music_dir", type=str, help="The directory to play music from")
    args = parser.parse_args()

    music_database = MusicDatabase(args.music_dir)
    term = blessed.Terminal()

    random_artists = [
        "Alison Krauss and Union Station",
        "Daft Punk",
        "The Black Keys",
        "Tony Bennett",
        "Alice In Chains",
        "Pink Floyd",
        "Nelly Furtado",
        "Gregg Allman",
    ]

    # list_pane = ListPane(term, random_artists, 40, 6)

    # with term.fullscreen(), term.cbreak(), term.hidden_cursor():
    #     val = None
    #     while val is None or val.lower() != "q":
    #         print(term.home + term.clear)
    #         if val is not None:
    #             list_pane.process_keystroke(val)
    #         list_pane.render()

    #         val = term.inkey(100)

    selected_song = 0
    music_player = MusicPlayer()

    artist_pane = ArtistPane(term, music_database)
    song_pane = SongPane(
        term,
        "",
        [],
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

            artist_pane.render(active_pane == "artist")
            print("")
            song_pane.render(active_pane == "song")
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
            else:
                print(term.move_y(term.height) + "")

            val = term.inkey(0.2)