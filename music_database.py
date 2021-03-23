import os
import pathlib


class MusicDatabase:
    def __init__(self, path):
        self.allowed_suffixes = {".flac", ".mp3", ".ogg"}
        self.songs = []
        self.load_songs(path)

    def load_songs(self, path):
        for root, dirs, files in os.walk(path):
            for file in files:
                p = pathlib.Path(os.path.join(root, file))
                if p.suffix in self.allowed_suffixes:
                    self.songs.append({"path": p, "name": file})

    def print_all(self):
        for song in self.songs.values():
            print(song)
