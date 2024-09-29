import logging
import os
import uuid
from pathlib import Path

import streamlit as st

from hackyeah_project_lib.config import settings
from hackyeah_project_lib.main_pipeline import MainPipeline
from hackyeah_project_lib.text_processing.llm_processor.processor import LLMProcessor
from hackyeah_project_lib.utils.logger import get_configured_logger

logger = get_configured_logger("app_logger", log_file="logs/app.log", level=logging.DEBUG)


OPENAI_API_KEY = settings.OPENAI_API_KEY
llm = LLMProcessor()
st.set_page_config(layout="wide")
st.title("💬 Chat Ekspert od Manipulacji w Wideo")

if "chat_messages_2" not in st.session_state:
    st.session_state["chat_messages_2"] = [
        {"role": "assistant", "content": "Dodaj plik aby rozpocząć. Przetwarzanie może potrwać do 3 minut."}
    ]

for msg in st.session_state.chat_messages_2:
    st.chat_message(msg["role"]).write(msg["content"])


# Separate File Uploaders for MP4 Files in Columns
cols = st.columns(2)

with cols[0]:
    uploaded_file_1 = st.file_uploader("Wgraj pierwszy plik wideo", type=["mp4", "mpeg4"], key="file_uploader_1")

with cols[1]:
    uploaded_file_2 = st.file_uploader("Wgraj drugi plik wideo", type=["mp4", "mpeg4"], key="file_uploader_2")

if uploaded_file_1 is not None and uploaded_file_2 is not None:
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

        progress_bar = cols[i].progress(0)
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
    if "chat_messages_2" not in st.session_state:
        st.session_state.chat_messages_2 = [
            {"role": "assistant", "content": "Witaj! Zadaj pytanie dotyczące porównania wideo."}
        ]

    for msg in st.session_state.chat_messages_2:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_question := st.chat_input("Zadaj pytanie dotyczące porównania wideo"):
        st.session_state.chat_messages_2.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("Generowanie odpowiedzi..."):
                assistant_response = llm.ask_openai_for_multiple_videos(
                    user_question,
                    pipeline_outputs[0].model_dump(mode="python"),
                    pipeline_outputs[1].model_dump(mode="python"),
                )
                st.markdown(assistant_response)
                st.session_state.chat_messages_2.append({"role": "assistant", "content": assistant_response})
