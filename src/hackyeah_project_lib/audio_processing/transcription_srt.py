import tempfile
from typing import cast

import openai
import webvtt
from pydantic import BaseModel

from hackyeah_project_lib.config import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


class CaptionVTTModel(BaseModel):
    text: str
    start_time: str
    end_time: str


class TranscriptionVTTModel(BaseModel):
    captions: list[CaptionVTTModel]


def transcribe_audio_srt(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(file=audio_file, model="whisper-1", response_format="srt")
        print(type(transcript))
        return cast(str, transcript)


def srt_to_webvtt_format(srt_string: str) -> TranscriptionVTTModel:
    # Create a NamedTemporaryFile and ensure it is deleted after usage
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", suffix=".srt") as tp:
        # Write string data to the temporary file
        tp.write(srt_string)
        tp.flush()

        # Read and convert the SRT file to VTT using webvtt
        vtt = webvtt.from_srt(tp.name)
        transcription_vtt = TranscriptionVTTModel(
            captions=[
                CaptionVTTModel(text=caption.text, start_time=caption.start, end_time=caption.end) for caption in vtt
            ]
        )
        return transcription_vtt
