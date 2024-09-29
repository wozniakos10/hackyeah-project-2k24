import logging
import os
import uuid
from typing import Any

import streamlit as st

from hackyeah_project_lib.audio_processing.audio_converter import AudioConverter
from hackyeah_project_lib.audio_processing.audio_features import AudioVolumeProcessor, PauseDetection
from hackyeah_project_lib.audio_processing.transcription import transcribe_audio
from hackyeah_project_lib.audio_processing.transcription_srt import transcribe_audio_srt
from hackyeah_project_lib.audio_processing.xgboost_pause_detection.xgboost_class import XGBoostClassifier
from hackyeah_project_lib.config import settings
from hackyeah_project_lib.text_processing.llm_processor.processor import LLMProcessor
from hackyeah_project_lib.utils.logger import get_configured_logger
from hackyeah_project_lib.utils.s3 import S3
from hackyeah_project_lib.video_processing.reduce_mp4_size import compress_video
from hackyeah_project_lib.video_processing.video_to_audio import VideoConverter
from hackyeah_project_lib.video_processing.gcp import send_message_to_gemini

logger = get_configured_logger("app_logger", log_file="logs/app.log", level=logging.DEBUG)


def pause_extractor(file_path: str) -> dict[str, list[Any]]:
    wav_file_name = os.path.join("temp", f"{os.path.basename(file_path)}_{uuid.uuid4().hex}.wav")
    audio_conv = AudioConverter(path=file_path)
    audio_conv.mp3_to_wav(path_to_wav=wav_file_name)
    pause = PauseDetection(path=wav_file_name)
    pause_interval = pause.pause_interval()
    return pause_interval


def pause_model_output_parser(score: int) -> str:
    if score == 0:
        return "W powyższym nagraniu występują za długie pauzy lub przerywniki."
    else:
        return "W powyższym nagraniu nie wykryliśmy zbyt długich pauz lub przerywników."


OPENAI_API_KEY = settings.OPENAI_API_KEY
s3_class = S3()
llm = LLMProcessor()

st.title("💬 Chat Ekspert od Manipulacji w Wideo")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Dodaj plik aby rozpocząć"}]
    st.session_state["file_processed"] = False
    st.session_state["pause_interval"] = None

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

uploaded_file = st.file_uploader("Upload file", type="mp4")
# Single File Uploader for MP4 Files
uploaded_file = st.file_uploader("Wgraj plik wideo (MP4, MPEG4)", type=["mp4", "mpeg4"])

if uploaded_file is not None and not st.session_state["file_processed"]:
    # Process the file
    os.makedirs("temp", exist_ok=True)
    unique_id = uuid.uuid4().hex
    filename, file_extension = os.path.splitext(uploaded_file.name)
    unique_filename = f"{filename}_{unique_id}{file_extension}"

    # Save the uploaded file with the unique filename
    file_path = os.path.join("/tmp", unique_filename)
    file_path = os.path.join("temp", unique_filename)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    progress_bar = st.progress(0)
    status_text = st.empty()

    # Compress video
    status_text.text("Kompresja wideo...")
    compressed_video_path = os.path.join("temp", f"{filename}_{unique_id}_compressed{file_extension}")
    compress_video(video_full_path=file_path, output_file_name=compressed_video_path)
    progress_bar.progress(20)

    # Convert video to MP3
    status_text.text("Konwersja wideo na MP3...")
    mp3_path = os.path.join("temp", f"{filename}_{unique_id}.mp3")
    video_converter = VideoConverter(path=compressed_video_path)
    video_converter.mp4_to_mp3(path_to_mp3=mp3_path)
    progress_bar.progress(40)  # Update progress

    # Upload file to S3
    status_text.text("Przesyłanie pliku na S3...")
    if not s3_class.upload_file(file_name=file_path, object_name=f"app/{unique_id}/{filename}{file_extension}"):
        st.warning("There was a problem with uploading the file to s3...")
    progress_bar.progress(60)

    st.write("# Analiza audio:")

    # Pause detection
    status_text.text("Detekcja pauz...")
    pause_interval = pause_extractor(mp3_path)
    progress_bar.progress(70)

    model = XGBoostClassifier()
    score = model.predict(pause_interval)
    pause_model_output_parser(score)

    # Step 5: Audio volume analysis

    st.write("### Analiza głośności audio:")
    status_text.text("Analiza głośności audio...")
    interpretation = AudioVolumeProcessor(path=file_path).run().volume_interpretation
    st.metric(label="Głośność wideo", value=f"{interpretation}")
    progress_bar.progress(80)  # Update progress

    # Transcription
    status_text.text("Transkrypcja audio (SRT)...")
    transcription_srt = transcribe_audio_srt(mp3_path)
    progress_bar.progress(90)

    status_text.text("Transkrypcja audio...")
    transcription = transcribe_audio(mp3_path)
    progress_bar.progress(100)

    # Completion
    status_text.text("Proces zakończony.")

    # Save results to session state
    st.session_state["file_processed"] = True
    st.session_state["pause_interval"] = pause_interval
    st.session_state["pause_result"] = pause_result
    st.session_state["volume_interpretation"] = interpretation
    st.session_state["transcription_srt"] = transcription_srt
    st.session_state["transcription"] = transcription
    st.session_state["video_path"] = file_path

if st.session_state["file_processed"]:
    # Display results
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Detekcja pauz:")
        st.write(st.session_state["pause_result"])
    with col2:
        st.write("### Analiza głośności audio:")
        st.metric(label="Głośność wideo", value=st.session_state["volume_interpretation"])

    st.chat_message("assistant").write("TRANSCRIPTION SRT:\n" + st.session_state["transcription_srt"])
    st.chat_message("assistant").write("TRANSCRIPTION:\n" + st.session_state["transcription"])

    # Display video
    st.video(st.session_state["video_path"], format="video/mp4")

    # Chat interface
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Witaj! Zadaj pytanie dotyczące manipulacji w wideo."}
        ]

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_question := st.chat_input("Zadaj pytanie dotyczące manipulacji w wideo"):
        st.session_state.chat_messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Generowanie odpowiedzi..."):
                assistant_response = llm.ask_openai(user_question, st.session_state["pause_interval"])
                st.markdown(assistant_response)
                st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})

    #dev
    temporary_s3_file_path = "https://hackyeah-mt.s3.amazonaws.com/videos/HY_2024_film_02.mp4"
    response = send_message_to_gemini(temporary_s3_file_path)
    #dev
