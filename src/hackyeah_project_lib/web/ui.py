import logging
import os
import uuid  # Import the uuid module
from typing import Any

import streamlit as st

from hackyeah_project_lib.audio_processing.audio_converter import AudioConverter
from hackyeah_project_lib.audio_processing.audio_features import AudioFeatures, PauseDetection
from hackyeah_project_lib.audio_processing.transcription import transcribe_audio
from hackyeah_project_lib.audio_processing.transcription_srt import transcribe_audio_srt
from hackyeah_project_lib.audio_processing.xgboost_pause_detection.xgboost_class import XGBoostClass
from hackyeah_project_lib.config import settings
from hackyeah_project_lib.utils.logger import get_configured_logger
from hackyeah_project_lib.utils.s3 import S3

logger = get_configured_logger("app_logger", log_file="logs/app.log", level=logging.DEBUG)


def pause_extractor(file_path: str) -> dict[str, list[Any]]:
    wav_file_name = os.path.join("temp", f"{filename}_{unique_id}.wav")
    audio_conv = AudioConverter(path=file_path)
    audio_conv.mp3towav(path_to_wav=wav_file_name)
    pause = PauseDetection(path=wav_file_name)
    st.write("Pause detection:")
    pause_interval = pause.pause_interval()
    st.write(pause_interval)
    return pause_interval


def pause_model_output_parser(score: int) -> None:
    if score == 0:
        st.write("W powyższym nagraniu występują za długie pauzy lub przerywniki.")
    else:
        st.write("W powyższym nagraniu nie wykryliśmy zbyt długich pauz lub przerywników.")


OPENAI_API_KEY = settings.OPENAI_API_KEY
s3_class = S3()

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

    if not s3_class.upload_file(file_name=file_path, object_name=f"app/{unique_id}/{filename}{file_extension}"):
        st.warning("There was a problem with uploading the file to s3...")

    st.write("# Analiza audio:")

    # Podziel na dwie kolumny
    col1, col2 = st.columns(2)

    # Kolumna 1: Analiza pauzy lub przerywnika
    with col1:
        st.write("### Detekcja pauz:")
        pause_interval = pause_extractor(file_path)

        model = XGBoostClass(
            model_path="src/hackyeah_project_lib/audio_processing/xgboost_pause_detection/xgboost_model.pkl",
            scaler_path="src/hackyeah_project_lib/audio_processing/xgboost_pause_detection/scaler.pkl",
        )
        score = model.predict(pause_interval)
        pause_model_output_parser(score)

    # Kolumna 2: Rozpoznanie głośności audio
    with col2:
        st.write("### Analiza głośności audio:")
        audio_feat = AudioFeatures(path=file_path)
        interpretation = audio_feat.volume_interpretation
        st.metric(label="Głośność wideo", value=f"{interpretation}")

    # Odtwarzanie pliku audio
    st.audio(file_path, format="audio/mp3")
    st.session_state.messages.append({"role": "user", "content": "Audio file uploaded."})
    st.chat_message("user").write("Audio file uploaded.")

    # Transkrypcja
    transcription_srt = transcribe_audio_srt(file_path)  # transkrypcja audio SRT
    st.chat_message("assistant").write("TRANSCRIPTION SRT:\n" + transcription_srt)

    transcription = transcribe_audio(file_path)  # transkrypcja audio
    st.chat_message("assistant").write("TRANSCRIPTION:\n" + transcription)
