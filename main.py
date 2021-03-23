import argparse
import os
from pathlib import Path
import time

import blessed

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame


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

    pygame.init()

    music_dir = Path(args.music_dir)
    songs = [song for song in music_dir.iterdir() if not song.is_dir()]

    term = blessed.Terminal()

    selected_song = 0
    playing_song = None
    playing_song_length = None
    playing_song_start_time = None
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
                    if selected_song < len(songs) - 1:
                        selected_song += 1

            for index, song in enumerate(songs):
                if index == selected_song:
                    print(term.underline(song.name))
                else:
                    print(song.name)

            # Play the song after the interface is printed to prevent empty screens
            # while song loads
            if type(val) != str and val.name == "KEY_ENTER":
                playing_song = songs[selected_song]
                pygame.mixer.music.load(playing_song)
                pygame.mixer.music.play(0)

                playing_song_length = pygame.mixer.Sound(playing_song).get_length()
                playing_song_start_time = time.time()

            if playing_song is not None and pygame.mixer.music.get_busy():
                print("")
                print(term.center(f"Now Playing: {playing_song.name}"))
                print_progress_bar(
                    term, (time.time() - playing_song_start_time) / playing_song_length
                )

            val = term.inkey(timeout=3)