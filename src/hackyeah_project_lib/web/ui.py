import logging
import os
import uuid
from pathlib import Path

import streamlit as st

from hackyeah_project_lib.config import settings
from hackyeah_project_lib.main_pipeline import MainPipeline
from hackyeah_project_lib.text_processing.llm_processor.processor import LLMProcessor
from hackyeah_project_lib.utils.logger import get_configured_logger
from hackyeah_project_lib.video_processing.gcp import send_message_to_gemini

logger = get_configured_logger("app_logger", log_file="logs/app.log", level=logging.DEBUG)


OPENAI_API_KEY = settings.OPENAI_API_KEY
llm = LLMProcessor()

st.title("💬 Chat Ekspert od Manipulacji w Wideo")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Dodaj plik aby rozpocząć"}]
    st.session_state["file_processed"] = False
    st.session_state["pause_interval"] = None

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# Single File Uploader for MP4 Files
uploaded_file = st.file_uploader(
    "Wgraj plik wideo (MP4, MPEG4)",
    type=["mp4", "mpeg4"],
)

if uploaded_file is not None and not st.session_state["file_processed"]:
    # Process the file
    os.makedirs("temp", exist_ok=True)
    unique_id = uuid.uuid4().hex
    filename, file_extension = os.path.splitext(uploaded_file.name)
    unique_filename = f"{filename}_{unique_id}{file_extension}"

    # Save the uploaded file with the unique filename
    file_path = os.path.join("/tmp", unique_filename)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    progress_bar = st.progress(0)
    if "pipeline_output" not in st.session_state:
        pipeline = MainPipeline(unique_id, progress_bar, logger)
        pipeline_output = pipeline.run(Path(file_path))
        st.session_state["pipeline_output"] = pipeline_output
    else:
        pipeline_output = st.session_state["pipeline_output"]

    st.metric(label="Głośność wideo", value=f"{pipeline_output.audio_volume.volume_interpretation}")

    st.chat_message("assistant").write("TRANSCRIPTION SRT:\n" + pipeline_output.transcription_srt)
    st.chat_message("assistant").write("TRANSCRIPTION:\n" + pipeline_output.transcription)

    # Display video
    st.video(pipeline_output.mp4_path, format="video/mp4")

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
                assistant_response = llm.ask_openai(user_question, pipeline_output.model_dump(mode="python"))
                st.markdown(assistant_response)
                st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})

    # dev
    temporary_s3_file_path = "https://hackyeah-mt.s3.amazonaws.com/videos/HY_2024_film_02.mp4"
    response = send_message_to_gemini(temporary_s3_file_path)
    # dev
