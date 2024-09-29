import os
from typing import cast

from moviepy.editor import VideoFileClip


class VideoConverter:
    def __init__(self, path: str) -> None:
        self.mp4_path = path
        self.file_size_mb = self.__get_mp4_size(self.mp4_path)
        self.duration = self.__get_mp4_duration(self.mp4_path)

    @staticmethod
    def __get_mp4_size(path: str) -> float:
        file_size = os.path.getsize(path)  # Odczyt rozmiaru pliku w bajtach
        file_size_mb = file_size / (1024 * 1024)  # Konwersja na MB
        return file_size_mb

    @staticmethod
    def __get_mp4_duration(path: str) -> float:
        video = VideoFileClip(path)
        duration_seconds = video.duration  # Długość nagrania w sekundach
        return cast(float, duration_seconds)

    def mp4_to_mp3(self, path_to_mp3: str) -> None:
        # Konwersja MP4 do MP3
        video = VideoFileClip(self.mp4_path)
        video.audio.write_audiofile(path_to_mp3)

    def mp4_to_wav(self, path_to_wav: str) -> None:
        """Konwersja MP4 do WAV"""
        video = VideoFileClip(self.mp4_path)
        video.audio.write_audiofile(path_to_wav, codec="pcm_s16le")
        print(f"Konwersja MP4 do WAV zakończona: {path_to_wav}")


# Usage:
# mp4_path = (
#     "/Users/dtomal/Documents/hackyeah-project-2k24/wetransfer_hackyeah-2024-breakwordtraps_2024-09-28_0449/"
#     "HY_2024_film_15.mp4"
# )
# converter = VideoConverter(mp4_path)
# print(f"Rozmiar pliku: {converter.file_size_mb:.2f} MB")
# print(f"Długość nagrania: {converter.duration:.2f} sekund")
# converter.mp4tomp3('file.mp3')
