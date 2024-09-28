#%%
import os
import librosa
import numpy as np
import warnings


warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
class AudioFeatures:
    def __init__(self, path):
        self.path = path
        self.volume = self.__get_mp4_volume(self.path)[0]
        self.volume_interpretation = self.__get_mp4_volume(self.path)[1]

    def __get_mp4_volume(self, path):
        y, sr = librosa.load(path)
        rms = np.sqrt(np.mean(y ** 2))
        db = librosa.amplitude_to_db(rms)

        if db < -42:
            interpretation = "Cicho"
        elif -42 <= db < -30:
            interpretation = "Umiarkowanie"
        else:
            interpretation = "Głośno"

        return db, interpretation
## usage:
##af = AudioFeatures('/Users/dtomal/Documents/hackyeah-project-2k24/data_mp4/HY_2024_film_03.mp4')
#print(af.volume)
#print(af.volume_interpretation)
