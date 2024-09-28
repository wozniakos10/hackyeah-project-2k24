from openai import OpenAI

client = OpenAI(api_key="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")

audio_file= open("/Users/mateu/development/projects/hackyeah-project-2k24/src/stuff/speech.mp3", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)
print(transcription.text)

# output to :
# W budżecie na 2025 rok przeznaczymy ponad 221,7 mld zł na ochronę. Rekordowy wzrost nakładów na ochronę zdrowia zgodnie z ustawą o blisko 31,7 mld zł, to jest to 0,6%. 0,5 mld zł na realizację programu In Vitro, 8,4 mld zł na realizację świadczeń aktywny rodzic, 62,8 mld zł na program Rodzina 800+.