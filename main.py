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


class ArtistPane(ListPane):
    def __init__(self, term, music_database):
        super().__init__(
            term, list(music_database.get_artists()), 50, 20, "Artist", (0, 2)
        )
        self.music_database = music_database

    def get_current_artist(self):
        return list(self.music_database.get_artists())[self.current_item]


class SongPane(ListPane):
    def __init__(self, term, artist, songs):
        super().__init__(term, songs, 50, 20, "Song", (50, 2))
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