from openai import OpenAI

client = OpenAI("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")

audio_file= open("/Users/mateu/development/projects/hackyeah-project-2k24/src/stuff/speech.mp3", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)
print(transcription.text)