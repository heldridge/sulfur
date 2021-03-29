from collections import defaultdict
import os
import pathlib

import mutagen


class Song:
    def __init__(self, title, path, track_number):
        self.title = title
        self.path = path
        self.track_number = track_number


class MusicDatabase:
    def __init__(self, path):
        self.allowed_suffixes = {".flac", ".mp3", ".ogg", ".wav"}
        self.artist_tags = {"ARTIST", "TPE1"}
        self.album_tags = {"TALB", "ALBUM"}
        self.title_tags = {"TITLE", "TIT2"}
        self.track_number_tags = {"TRCK", "TRACKNUMBER"}

        self.songs = []
        self.artist_map = defaultdict(lambda: defaultdict(list))
        self.load_songs(path)

    def load_songs(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                p = pathlib.Path(os.path.join(root, file))
                if p.suffix in self.allowed_suffixes:
                    mutagen_file = mutagen.File(p)
                    if mutagen_file is None:
                        # Don't add files we can't understand to the database
                        continue

                    song_artist = "Unknown"
                    for tag in self.artist_tags:
                        if tag in mutagen_file.tags:
                            artist = mutagen_file.tags[tag]
                            if isinstance(artist, list):
                                artist = artist[0]
                            song_artist = str(artist)
                            break

                    song_album = "<Unknown>"
                    for tag in self.album_tags:
                        if tag in mutagen_file.tags:
                            album = mutagen_file.tags[tag]
                            if isinstance(album, list):
                                album = album[0]
                            song_album = str(album)
                            break

                    song_title = "<Unknown>"
                    for title_tag in self.title_tags:
                        if title_tag in mutagen_file.tags:
                            title = mutagen_file.tags[title_tag]
                            if isinstance(title, list):
                                title = title[0]
                            song_title = str(title)
                            break

                    track_number = 0
                    for track_number_tag in self.track_number_tags:
                        if track_number_tag in mutagen_file.tags:
                            track_number = mutagen_file.tags[track_number_tag]
                            if isinstance(track_number, list):
                                track_number = track_number[0]
                            if isinstance(track_number, mutagen.id3.TRCK):
                                track_number = track_number.__pos__()

                            track_number = int(str(track_number))
                            break

                    self.artist_map[song_artist][song_album].append(
                        Song(song_title, p, track_number)
                    )

                    self.songs.append({"path": p, "name": file})

    def print_all(self):
        for song in self.songs.values():
            print(song)

    def get_albums(self, artist):
        return sorted(self.artist_map[artist])

    def get_artists(self):
        return sorted(self.artist_map.keys())
