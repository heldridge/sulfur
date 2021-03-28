import argparse

import urwid

from music_database import MusicDatabase
from music_player import MusicPlayer


class CustomButton(urwid.Button):
    button_left = urwid.Text("")
    button_right = urwid.Text("")


class CustomProgressBar(urwid.ProgressBar):
    def get_text(self):
        return ""


class Display:
    def __init__(self, music_dir):
        self.music_database = MusicDatabase(music_dir)
        self.music_player = MusicPlayer()

        artists = []
        for artist in self.music_database.get_artists():
            button = CustomButton(artist)
            urwid.connect_signal(button, "click", self.set_current_artist, artist)
            artists.append(button)

        self.artist_pane = urwid.LineBox(
            urwid.ListBox(urwid.SimpleFocusListWalker(artists)), title="Artist"
        )

        # Songs Pane
        self.song_list_walker = urwid.SimpleFocusListWalker([])
        self.song_list = urwid.ListBox(self.song_list_walker)
        self.song_pane = urwid.LineBox(self.song_list, title="Song")

        # Progress Bar
        progress_bar = urwid.Filler(
            CustomProgressBar("pg normal", "pg complete", 0, 5), "bottom"
        )

        # Layout
        self.panes = urwid.Columns([self.artist_pane, self.song_pane])
        self.top = urwid.Pile([("weight", 25, self.panes), progress_bar])

    def update_progress_bar(self, loop, user_data):
        if self.music_player.is_playing():
            self.progress_bar.set_completion(self.music_player.get_played_time())
        loop.set_alarm_in(0.2, self.update_progress_bar)

    def set_current_artist(self, button, new_artist):
        self.song_list_walker.clear()

        for song in self.music_database.artist_map[new_artist]:
            button = CustomButton(song.title)
            urwid.connect_signal(button, "click", self.play_song, song.path)
            self.song_list_walker.append(button)
        self.song_list_walker.set_focus(0)

    def handle_input(self, key):
        if key in ("q", "Q"):
            raise urwid.ExitMainLoop()
        if key in ("p", "P"):
            self.music_player.toggle_playing()

    def play_song(self, button, song_path):
        self.music_player.play(song_path)

        self.progress_bar = CustomProgressBar(
            "pg normal",
            "pg complete",
            0,
            self.music_player.get_playing_song_length(),
        )

        self.top.contents[1] = (
            urwid.Filler(
                self.progress_bar,
                "bottom",
            ),
            self.top.options(),
        )

    def run(self):
        palette = [
            ("pg complete", "light gray", "light gray"),
        ]
        self.loop = urwid.MainLoop(
            self.top, palette=palette, unhandled_input=self.handle_input
        )
        self.loop.set_alarm_in(0.2, self.update_progress_bar)
        self.loop.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("music_dir", type=str, help="The directory to play music from")
    args = parser.parse_args()

    display = Display(args.music_dir)
    display.run()
