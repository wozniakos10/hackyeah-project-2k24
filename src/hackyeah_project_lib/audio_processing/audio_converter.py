import logging

from moviepy.editor import AudioFileClip

from hackyeah_project_lib.utils.logger import get_configured_logger
from hackyeah_project_lib.video_processing.video_to_audio import VideoConverter

logger = get_configured_logger("app_logger", log_file="logs/app.log", level=logging.DEBUG)


class AudioConverter:
    def __init__(self, path: str) -> None:
        self.mp3_path = path

    def mp3_to_wav(self, path_to_wav: str) -> bool:
        """Konwersja MP3 do WAV"""
        try:
            audio = AudioFileClip(self.mp3_path)
            audio.write_audiofile(path_to_wav, codec="pcm_s16le")
            print(f"Konwersja MP3 do WAV zakończona: {path_to_wav}")
        except Exception as e:
            logger.error(f"There was error: {e}")
            return False
        return True


if __name__ == "__main__":
    mp4_path = "path_to_file"
    converter = VideoConverter(mp4_path)
    print(f"Rozmiar pliku: {converter.file_size_mb:.2f} MB")
    print(f"Długość nagrania: {converter.duration:.2f} sekund")
    converter.mp4_to_wav("file.wav")
