from langfuse.openai import openai
from hackyeah_project_lib.config import settings

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def transcribe_audio(file_path: str):
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
        )
        return transcript.text
