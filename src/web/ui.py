import streamlit as st
from openai import OpenAI
import os
from hackyeah_project_lib.config import settings

OPENAI_API_KEY = settings.OPENAI_API_KEY

st.title("💬 Hackyeah Chatbot with Audio Upload")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# File Uploader for MP3 Files
uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3"])

if uploaded_file is not None:
    # Ensure the 'temp' directory exists
    os.makedirs("temp", exist_ok=True)
    
    # Save the uploaded MP3 file to a temporary location
    file_path = os.path.join("temp", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.audio(file_path, format="audio/mp3")

    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Append user message
    st.session_state.messages.append({"role": "user", "content": "Audio file uploaded."})
    st.chat_message("user").write("Audio file uploaded.")

    # Process the audio file with OpenAI's Whisper
    try:
        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(file=audio_file, model="whisper-1")
        msg = response["text"]
        
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)
    except Exception as e:
        st.error(f"An error occurred during transcription: {e}")