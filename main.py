import argparse
import time

import urwid

from music_database import MusicDatabase
from playlist_player import PlaylistPlayer


class CustomButton(urwid.Button):
    button_left = urwid.Text("")
    button_right = urwid.Text("")


class CustomProgressBar(urwid.ProgressBar):
    def get_text(self):
        return ""


class NoSpaceListBox(urwid.ListBox):
    def keypress(self, size, key):
        if key in {" "}:
            # Deliberately ignore presses of the spacebar
            return key
        return super().keypress(size, key)


class Display:
    def __init__(self, music_dir):
        self.music_database = MusicDatabase(music_dir)
        self.playlist_player = PlaylistPlayer()
        self.playlist_player.register_callback(self.next_playlist_item)

        artists = []
        for artist in self.music_database.get_artists():
            button = CustomButton(artist)
            urwid.connect_signal(
                button, "click", self.set_current_artist, user_args=[artist]
            )
            artists.append(button)

        self.artist_pane = urwid.LineBox(
            NoSpaceListBox(urwid.SimpleFocusListWalker(artists)), title="Artist"
        )

        # Albums Pane
        self.album_list_walker = urwid.SimpleFocusListWalker([])
        self.album_list = NoSpaceListBox(self.album_list_walker)
        self.album_pane = urwid.LineBox(self.album_list, title="Album")

        # Songs Pane
        self.song_list_walker = urwid.SimpleFocusListWalker([])
        self.song_list = NoSpaceListBox(self.song_list_walker)
        self.song_pane = urwid.LineBox(self.song_list, title="Song")

        # Progress Bar
        progress_bar = urwid.Filler(
            CustomProgressBar("pg normal", "pg complete", 0, 5), "bottom"
        )

        self.now_playing = urwid.Text("", "center")

        self.volume_bar = CustomProgressBar(
            "pg normal", "pg complete", self.playlist_player.get_volume(), 100
        )

        volume = urwid.Columns(
            [
                ("weight", 0, urwid.Filler(urwid.Text("["), "middle")),
                urwid.Filler(self.volume_bar, "middle"),
                ("weight", 0, urwid.Filler(urwid.Text("]"), "middle")),
            ]
        )

        pre_progress_bar = urwid.Columns(
            [
                urwid.Pile(
                    [
                        urwid.Filler(urwid.Text("Volume", "center"), "middle"),
                        # urwid.Filler(self.volume_bar, "middle"),
                        volume,
                    ]
                ),
                ("weight", 10, urwid.Filler(self.now_playing, "bottom")),
                urwid.Filler(urwid.Text(""), "bottom"),
            ]
        )
        # Layout
        self.panes = urwid.Columns([self.artist_pane, self.album_pane, self.song_pane])
        self.top = urwid.Pile(
            [
                ("weight", 25, self.panes),
                # urwid.Filler(self.now_playing, "bottom"),
                pre_progress_bar,
                progress_bar,
            ]
        )

    def update_volume(self, *args):
        self.volume_bar.set_completion(self.playlist_player.get_volume())

    def update_progress_bar(self, loop, user_data):
        if self.playlist_player.is_playing():
            self.progress_bar.set_completion(
                self.playlist_player.player.get_media_player().get_time()
            )
        loop.set_alarm_in(0.2, self.update_progress_bar)

    def set_current_artist(self, new_artist, button):
        self.song_list_walker.clear()
        self.album_list_walker.clear()
        for album in self.music_database.get_albums(new_artist):
            button = CustomButton(album)
            urwid.connect_signal(
                button, "click", self.set_current_album, user_args=[new_artist, album]
            )
            self.album_list_walker.append(button)
        self.album_list_walker.set_focus(0)
        # Move focus to album pane
        self.panes.set_focus(1)

        self.current_artist = new_artist

    def set_current_album(self, new_artist, new_album, button):
        self.song_list_walker.clear()

        for index, song in enumerate(
            self.music_database.artist_map[new_artist][new_album]
        ):
            button = CustomButton(str(song.title))
            urwid.connect_signal(
                button,
                "click",
                self.play_songs_at_index,
                user_args=[new_artist, new_album, index],
            )
            self.song_list_walker.append(button)
        self.song_list_walker.set_focus(0)
        # Move focus to song pane
        self.panes.set_focus(2)

        self.current_album = new_album

    def handle_input(self, key):
        if key in ("q", "Q"):
            raise urwid.ExitMainLoop()
        elif key in ("p", "P", " "):
            self.playlist_player.toggle_playing()
        elif key in ("=", "+"):
            self.playlist_player.increase_volume()
            self.update_volume()
        elif key in ("-", "_"):
            self.playlist_player.decrease_volume()
            self.update_volume()

    def next_playlist_item(self, song):
        self.now_playing.set_text(song.title)

    def play_songs_at_index(self, artist, album, index, button):
        self.playlist_player.play_playlist_at_index(
            self.music_database.artist_map[artist][album], index
        )

        while self.playlist_player.get_playing_song_length() == 0:
            # Wait for the song length attribute to exist
            time.sleep(0.1)

        self.progress_bar = CustomProgressBar(
            "pg normal",
            "pg complete",
            0,
            self.playlist_player.get_playing_song_length(),
        )

        self.top.contents[2] = (
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
