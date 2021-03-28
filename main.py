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

        print(self.music_database.artist_map)

        artists = []
        for artist in self.music_database.get_artists():
            button = CustomButton(artist)
            urwid.connect_signal(
                button, "click", self.set_current_artist, user_args=[artist]
            )
            artists.append(button)

        self.artist_pane = urwid.LineBox(
            urwid.ListBox(urwid.SimpleFocusListWalker(artists)), title="Artist"
        )

        # Albums Pane
        self.album_list_walker = urwid.SimpleFocusListWalker([])
        self.album_list = urwid.ListBox(self.album_list_walker)
        self.album_pane = urwid.LineBox(self.album_list, title="Album")

        # Songs Pane
        self.song_list_walker = urwid.SimpleFocusListWalker([])
        self.song_list = urwid.ListBox(self.song_list_walker)
        self.song_pane = urwid.LineBox(self.song_list, title="Song")

        # Progress Bar
        progress_bar = urwid.Filler(
            CustomProgressBar("pg normal", "pg complete", 0, 5), "bottom"
        )

        # Layout
        self.panes = urwid.Columns([self.artist_pane, self.album_pane, self.song_pane])
        self.top = urwid.Pile([("weight", 25, self.panes), progress_bar])

    def update_progress_bar(self, loop, user_data):
        if self.music_player.is_playing():
            self.progress_bar.set_completion(self.music_player.get_played_time())
        loop.set_alarm_in(0.2, self.update_progress_bar)

    def set_current_artist(self, new_artist, button):
        self.album_list_walker.clear()
        for album in self.music_database.artist_map[new_artist].keys():
            button = CustomButton(album)
            urwid.connect_signal(
                button, "click", self.set_current_album, user_args=[new_artist, album]
            )
            self.album_list_walker.append(button)
        self.album_list_walker.set_focus(0)
        # Move focus to album pane
        self.panes.set_focus(1)

    def set_current_album(self, new_artist, new_album, button):
        self.song_list_walker.clear()

        for song in self.music_database.artist_map[new_artist][new_album]:
            button = CustomButton(str(song.title))
            urwid.connect_signal(button, "click", self.play_song, user_args=[song.path])
            self.song_list_walker.append(button)
        self.song_list_walker.set_focus(0)
        # Move focus to song pane
        self.panes.set_focus(2)

    def handle_input(self, key):
        if key in ("q", "Q"):
            raise urwid.ExitMainLoop()
        if key in ("p", "P"):
            self.music_player.toggle_playing()

    def play_song(self, song_path, button):
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
