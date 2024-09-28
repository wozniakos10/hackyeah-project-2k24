import os
from typing import Any

from moviepy.editor import AudioFileClip, VideoFileClip


class VideoConverter:
    def __init__(self, path: str) -> None:
        self.mp4_path = path
        self.file_size_mb = self.__get_mp4_size(self.mp4_path)
        self.duration = self.__get_mp4_duration(self.mp4_path)

    def __get_mp4_size(self, path: str) -> float:
        file_size = os.path.getsize(path)  # Odczyt rozmiaru pliku w bajtach
        file_size_mb = file_size / (1024 * 1024)  # Konwersja na MB
        return file_size_mb

    def __get_mp4_duration(self, path: str) -> Any:
        video = VideoFileClip(path)
        duration_seconds = video.duration  # Długość nagrania w sekundach
        return duration_seconds

    def mp4tomp3(self, path_to_mp3: str) -> None:
        # Konwersja MP4 do MP3
        video = VideoFileClip(self.mp4_path)
        video.audio.write_audiofile(path_to_mp3)

    def mp4towav(self, path_to_wav: str) -> None:
        """Konwersja MP4 do WAV"""
        video = VideoFileClip(self.mp4_path)
        video.audio.write_audiofile(path_to_wav, codec="pcm_s16le")
        print(f"Konwersja MP4 do WAV zakończona: {path_to_wav}")

    def mp3towav(self, mp3_path: str, path_to_wav: str) -> None:
        """Konwersja MP3 do WAV"""
        audio = AudioFileClip(mp3_path)
        audio.write_audiofile(path_to_wav, codec="pcm_s16le")
        print(f"Konwersja MP3 do WAV zakończona: {path_to_wav}")


if __name__ == "__main__":
    mp4_path = "path_to_file"
    converter = VideoConverter(mp4_path)
    print(f"Rozmiar pliku: {converter.file_size_mb:.2f} MB")
    print(f"Długość nagrania: {converter.duration:.2f} sekund")
    converter.mp4towav("file.wav")
