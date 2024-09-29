import warnings
from typing import Any

import librosa
import numpy as np
from pydantic import BaseModel
from pydub import AudioSegment
from pydub.silence import detect_silence

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


class AudioVolumeModel(BaseModel):
    volume_value: float
    volume_interpretation: str


class AudioVolumeProcessor:
    def __init__(self, path: str):
        self.path = path

    def run(self) -> AudioVolumeModel:
        volume_value, volume_interpretation = self.__get_mp4_volume(self.path)
        return AudioVolumeModel(volume_value=volume_value, volume_interpretation=volume_interpretation)

    @staticmethod
    def __get_mp4_volume(path: str) -> tuple[int, str]:
        y, sr = librosa.load(path)
        rms = np.sqrt(np.mean(y**2))
        db = librosa.amplitude_to_db(rms)

        if db < -42:
            interpretation = "Cicho"
        elif -42 <= db < -30:
            interpretation = "Umiarkowanie"
        else:
            interpretation = "Głośno"

        return db, interpretation


class PauseDetection:
    def __init__(self, path: str) -> None:
        self.path = path
        self.sound = AudioSegment.from_wav(path)
        self.audio_length = len(self.sound)

    def detect_pause(self) -> Any:
        return detect_silence(self.sound, min_silence_len=450, silence_thresh=-65)

    def pause_interval(self) -> dict[str, list[Any]]:
        pause_sum = 0
        silence = self.detect_pause()
        print(silence)
        first_pause_finish = 0
        for elem in silence:
            # skipping first pause (usually ~10sec without action)
            if elem[0] == 0:
                first_pause_finish = elem[1]
                continue
            pause_sum += elem[1] - elem[0]

        return {
            "pause_sum": [pause_sum],
            "pause_percent": [pause_sum / (self.audio_length - first_pause_finish)],
            "amount_of_pauses": [len(silence) - 1],
        }
