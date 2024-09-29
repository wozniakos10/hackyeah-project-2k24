import tempfile
from typing import cast

import ffmpeg
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


def transcribe_audio_srt(mp3_path: str, video_path: str) -> str:
    with open(mp3_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(file=audio_file, model="whisper-1", response_format="srt")
        # save transcript to file
        with open("transcription.srt", "w") as file:
            file.write(transcript)
        # video path is mp4 file so as output file name add _with_subtitles to the end
        output_video = video_path.replace(".mp4", "_with_subtitles.mp4")
        add_subtitles_to_video(video_path, "transcription.srt", output_video)
        return cast(str, transcript)


def add_subtitles_to_video(input_video: str, subtitles_file: str, output_video: str) -> None:
    """
    Adds subtitles to the video file using ffmpeg.

    :param input_video: Path to the input video file.
    :param subtitles_file: Path to the SRT file.
    :param output_video: Path to the output video file with subtitles.
    """
    (ffmpeg.input(input_video).output(output_video, vf=f"subtitles={subtitles_file}").run())


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
