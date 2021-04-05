import vlc


class PlaylistPlayer:
    def __init__(self):
        self.player = vlc.MediaListPlayer()
        # Give the player a default volume of 50, because otherwise it defaults to 0
        # until the first song is played
        self.player.get_media_player().audio_set_volume(50)
        self.player.event_manager().event_attach(
            vlc.EventType.MediaListPlayerNextItemSet, self.next_playlist_item
        )
        self.playlist_index = -1
        self.playlist = []
        self.callbacks = []

    def next_playlist_item(self, *args):
        """A callback that happens when the current playing song finishes"""

        # Update our playlist position
        if self.playlist_index < len(self.playlist) - 1:
            self.playlist_index += 1

        for callback in self.callbacks:
            callback(self.get_current_song())

    def play_playlist_at_index(self, playlist, index):
        self.set_playlist(playlist)
        self.play_at_index(index)

    def set_playlist(self, playlist):
        self.playlist_index = -1
        self.playlist = playlist
        self.pause()

        media_list = vlc.MediaList()
        for song in playlist:
            media_list.add_media(song.path)

        self.player.set_media_list(media_list)

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def play_at_index(self, index):
        if index < 0 or index >= len(self.playlist):
            raise IndexError("Index out of range")
        # Set to one below the index because the callback will immediately be triggered
        # which will increase the index to the correct value
        self.playlist_index = index - 1
        self.player.play_item_at_index(index)

    def get_index(self):
        return self.playlist_index

    def get_current_song(self):
        return self.playlist[self.playlist_index]

    def register_callback(self, callback):
        self.callbacks.append(callback)

    def get_playing_song_length(self):
        return self.player.get_media_player().get_length()

    def get_volume(self):
        return self.player.get_media_player().audio_get_volume()

    def is_playing(self):
        return self.player.is_playing()

    def toggle_playing(self):
        if self.is_playing():
            self.pause()
        else:
            self.play()

    def increase_volume(self):
        new_volume = self.player.get_media_player().audio_get_volume()
        if self.player is not None:
            if new_volume < 100:
                new_volume += 1
            self.player.get_media_player().audio_set_volume(new_volume)
        return new_volume

    def decrease_volume(self):
        new_volume = self.player.get_media_player().audio_get_volume()
        if self.player is not None:
            new_volume -= 1
            self.player.get_media_player().audio_set_volume(new_volume)
        return new_volume
