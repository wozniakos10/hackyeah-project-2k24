from openai import OpenAI
from hackyeah_project_lib.config import settings

client = OpenAI(settings.OPENAI_API_KEY)

audio_file= open("/Users/mateu/development/projects/hackyeah-project-2k24/src/stuff/speech.mp3", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)
print(transcription.text)