from typing import cast

import openai

from hackyeah_project_lib.config import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def transcribe_audio_srt(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(file=audio_file, model="whisper-1", response_format="srt")
        print(type(transcript))
        return cast(str, transcript)


# ANOTHER APPROACH:
# from datetime import timedelta
# import os
# import whisper

# def transcribe_audio(path):
#     model = whisper.load_model("base") # Change this to your desired model
#     print("Whisper model loaded.")
#     transcribe = model.transcribe(audio=path)
#     segments = transcribe['segments']

#     for segment in segments:
#         startTime = str(0)+str(timedelta(seconds=int(segment['start'])))+',000'
#         endTime = str(0)+str(timedelta(seconds=int(segment['end'])))+',000'
#         text = segment['text']
#         segmentId = segment['id']+1
#         segment = f"{segmentId}\n{startTime} --> {endTime}\n{text[1:] if text[0] is ' ' else text}\n\n"

#         srtFilename = os.path.join("SrtFiles", f"VIDEO_FILENAME.srt")
#         with open(srtFilename, 'a', encoding='utf-8') as srtFile:
#             srtFile.write(segment)

#     return srtFilename
