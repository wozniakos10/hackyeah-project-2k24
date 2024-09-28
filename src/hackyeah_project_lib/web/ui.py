import streamlit as st
from openai import OpenAI
from io import BytesIO
import os
from hackyeah_project_lib.config import settings
from hackyeah_project_lib.web.s3 import upload_file

# Initialize OpenAI client
OPENAI_API_KEY = settings.OPENAI_API_KEY
client = OpenAI(api_key=OPENAI_API_KEY)

st.title("💬 Chatbot with Audio Upload")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# File Uploader for MP3 Files
uploaded_file = st.file_uploader("Upload an MP3 file", type=["mp3"])

if uploaded_file is not None:
    # Display audio player
    st.audio(uploaded_file, format="audio/mp3")
    
    # Append user message
    st.session_state.messages.append({"role": "user", "content": "Audio file uploaded."})
    st.chat_message("user").write("Audio file uploaded.")
    
    # Upload to S3
    with st.spinner("Uploading audio to S3..."):
        upload_success = upload_file(uploaded_file, object_name=uploaded_file.name)
    
    if upload_success:
        st.success("File successfully uploaded to S3.")
    else:
        st.error("Failed to upload file to S3.")
    
    # Transcribe audio with a spinner for user feedback
    with st.spinner("Transcribing audio..."):
        try:
            transcription = client.audio.transcriptions.create(
                file=uploaded_file,
                model="whisper-1"
            )
            msg = transcription["text"]
            
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.chat_message("assistant").write(msg)
        except Exception as e:
            st.error(f"An error occurred during transcription: {e}")