import os
import uuid  # Import the uuid module

import streamlit as st
from langfuse.openai import openai

from hackyeah_project_lib.config import settings
from hackyeah_project_lib.transcription import transcribe_audio
from hackyeah_project_lib.transcription_srt import transcribe_audio_srt

OPENAI_API_KEY = settings.OPENAI_API_KEY

result = openai.langfuse_auth_check()
st.title("💬 chatuj tutaj")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Dodaj plik aby rozpocząć"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# File Uploader for MP3 Files
uploaded_file = st.file_uploader("Upload file", type=["mp3", "mp4"])

if uploaded_file is not None:
    # Ensure the 'temp' directory exists
    os.makedirs("temp", exist_ok=True)

    # Generate a unique filename using UUID
    unique_id = uuid.uuid4().hex
    filename, file_extension = os.path.splitext(uploaded_file.name)
    unique_filename = f"{filename}_{unique_id}{file_extension}"

    # Save the uploaded file with the unique filename
    file_path = os.path.join("temp", unique_filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.audio(file_path, format="audio/mp3")
    st.session_state.messages.append({"role": "user", "content": "Audio file uploaded."})
    st.chat_message("user").write("Audio file uploaded.")

    transcription = transcribe_audio_srt(file_path)  # transkrypcja audio
    st.chat_message("assistant").write("TRANSCRIPTION SRT:" + transcription)

    transcription = transcribe_audio(file_path)  # transkrypcja audio
    st.chat_message("assistant").write("TRANSCRIPTION:" + transcription)
