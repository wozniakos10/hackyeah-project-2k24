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


# Separate File Uploaders for MP4 Files in Columns
col1, col2 = st.columns(2)

with col1:
    uploaded_file_1 = st.file_uploader(
        "Wgraj pierwszy plik wideo",
        type=["mp4", "mpeg4"],
        key="file_uploader_1"
    )

with col2:
    uploaded_file_2 = st.file_uploader(
        "Wgraj drugi plik wideo",
        type=["mp4", "mpeg4"],
        key="file_uploader_2"
    )

if uploaded_file_1 is not None and uploaded_file_2 is not None and not st.session_state["file_processed"]:
    # Process the files
    os.makedirs("temp", exist_ok=True)
    file_paths = []
    pipeline_outputs_names = ["pipeline_output_1", "pipeline_output_2"]
    pipeline_outputs = []
    for i, uploaded_file in enumerate([uploaded_file_1, uploaded_file_2]):
        unique_id = uuid.uuid4().hex
        filename, file_extension = os.path.splitext(uploaded_file.name)
        unique_filename = f"{filename}_{unique_id}{file_extension}"

        # Save the uploaded file with the unique filename
        file_path = os.path.join("/tmp", unique_filename)
        file_paths.append(file_path)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        progress_bar = st.progress(0)
        if pipeline_outputs_names[i] not in st.session_state:
            pipeline = MainPipeline(unique_id, progress_bar, logger)
            pipeline_outputs.append(pipeline.run(Path(file_path)))
            st.session_state[pipeline_outputs_names[i]] = pipeline_outputs[i]
        else:
            pipeline_outputs.append(st.session_state[pipeline_outputs_names[i]])


    # Comparison logic (example: comparing transcriptions)
    if pipeline_outputs[0].transcription == pipeline_outputs[1].transcription:
        comparison_result = "Transkrypcje są identyczne."
    else:
        comparison_result = "Transkrypcje różnią się."

    # st.chat_message("assistant").write("Wynik porównania: " + comparison_result)

    # Chat interface
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Witaj! Zadaj pytanie dotyczące porównania wideo."}
        ]

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_question := st.chat_input("Zadaj pytanie dotyczące porównania wideo"):
        st.session_state.chat_messages.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Generowanie odpowiedzi..."):
                assistant_response = llm.ask_openai_for_multiple_videos(user_question,
                    pipeline_outputs[0].model_dump(mode="python"),
                    pipeline_outputs[1].model_dump(mode="python")
                )
                st.markdown(assistant_response)
                st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})