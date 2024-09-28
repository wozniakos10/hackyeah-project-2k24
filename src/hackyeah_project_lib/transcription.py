import openai
from typing import cast
from hackyeah_project_lib.config import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def transcribe_audio(file_path: str) -> str:
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
        )
        return cast(str, transcript.text)
