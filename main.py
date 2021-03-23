import argparse
from pathlib import Path

import blessed

from music_database import MusicDatabase
from music_player import MusicPlayer


def print_progress_bar(term, percentage):
    term.move_xy(0, term.height - 1)
    print("[", end="")

    num_blocks = int(percentage * term.width)
    print("\N{FULL BLOCK}" * num_blocks, end="")
    print(" " * (term.width - 2 - num_blocks), end="")
    print("]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("music_dir", type=str, help="The directory to play music from")
    args = parser.parse_args()

    music_database = MusicDatabase(args.music_dir)
    term = blessed.Terminal()

    selected_song = 0
    music_player = MusicPlayer()
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        val = ""
        while val.lower() != "q":
            print(term.home + term.clear)
            print(term.center("Choose a song (press q to quit)"))

            if type(val) != str:
                if val.name == "KEY_UP":
                    if selected_song > 0:
                        selected_song -= 1
                elif val.name == "KEY_DOWN":
                    if selected_song < len(music_database.songs) - 1:
                        selected_song += 1

            for index, song in enumerate(music_database.songs):
                if index == selected_song:
                    print(term.underline(song["name"]))
                else:
                    print(song["name"])

            # Play the song after the interface is printed to prevent empty screens
            # while song loads
            if type(val) != str and val.name == "KEY_ENTER":
                playing_song = music_database.songs[selected_song]
                music_player.play(playing_song["path"])

            if music_player.is_playing():
                print("")
                print(term.center(f"Now Playing: {playing_song['name']}"))
                print_progress_bar(term, music_player.get_playing_song_percentage())

            val = term.inkey(timeout=3)