from collections import defaultdict
import os
import pathlib

import mutagen


class MusicDatabase:
    def __init__(self, path):
        self.allowed_suffixes = {".flac", ".mp3", ".ogg", ".wav"}
        self.artist_tags = {"ARTIST", "TPE1"}
        self.songs = []
        self.artist_map = defaultdict(list)
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

                    self.artist_map[song_artist].append(
                        {
                            "path": p,
                            "info": mutagen_file.info,
                        }
                    )

                    self.songs.append({"path": p, "name": file})

    def print_all(self):
        for song in self.songs.values():
            print(song)
