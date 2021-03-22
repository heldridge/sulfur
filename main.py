import argparse
import os

import blessed

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("music_dir", type=str, help="The directory to play music from")
    args = parser.parse_args()

    songs = os.listdir(args.music_dir)

    term = blessed.Terminal()

    selected_song = 0
    playing_song = None
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
                elif val.name == "KEY_ENTER":
                    playing_song = songs[selected_song]

            for index, song in enumerate(songs):
                if index == selected_song:
                    print(term.underline(song))
                else:
                    print(song)

            if playing_song is not None:
                print("")
                print(term.center(f"Now Playing: {playing_song}"))

            val = term.inkey()