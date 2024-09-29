import logging
import os
import uuid
from pathlib import Path
from random import randint

import streamlit as st
from annotated_text import annotated_text

from hackyeah_project_lib.main_pipeline import MainPipeline
from hackyeah_project_lib.text_processing.llm_processor.processor import LLMProcessor
from hackyeah_project_lib.utils.logger import get_configured_logger
from hackyeah_project_lib.web.utils.gauge_widget import gauge

logger = get_configured_logger("app_logger", log_file="logs/app.log", level=logging.DEBUG)

st.set_page_config(layout="wide")
left_col, right_col = st.columns(2)


def reset_app() -> None:
    st.session_state.clear()


with left_col:
    st.title("💬 Chat Ekspert od Manipulacji w Wideo")

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Single File Uploader for MP4 Files
    uploaded_file = st.file_uploader(
        "Wgraj plik wideo (MP4, MPEG4)", type=["mp4", "mpeg4"], on_change=lambda: reset_app()
    )

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if uploaded_file is None:
        st.session_state.messages.append(
            {"role": "assistant", "content": "Dodaj plik aby rozpocząć. Przetwarzanie może potrwać do 2 minut."}
        )
    else:
        if "pipeline_output" not in st.session_state:
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
            pipeline = MainPipeline(unique_id, progress_bar, logger)
            pipeline_output = pipeline.run(Path(file_path))
            st.session_state["pipeline_output"] = pipeline_output
        else:
            pipeline_output = st.session_state["pipeline_output"]

        st.session_state["messages"] = []
        llm = LLMProcessor()
        st.video(pipeline_output.mp4_path, format="video/mp4")

        # Chat interface
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = [
                {"role": "assistant", "content": "Witaj! Zadaj pytanie dotyczące manipulacji w wideo."}
            ]

        messages = st.container(height=500)
        for msg in st.session_state.chat_messages:
            with messages.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if user_question := st.chat_input("Zadaj pytanie dotyczące manipulacji w wideo"):
            st.session_state.chat_messages.append({"role": "user", "content": user_question})
            with messages.chat_message("user"):
                st.markdown(user_question)

            with messages.chat_message("assistant"):
                with st.spinner("Generowanie odpowiedzi..."):
                    assistant_response = llm.ask_openai(user_question, pipeline_output.model_dump(mode="python"))
                    st.markdown(assistant_response)
                    st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})


with right_col:
    if "pipeline_output" in st.session_state:
        # Audio volume gauge display
        volume_gauge_value = {"Cicho": 0.25, "Umiarkowanie": 0.5, "Głośno": 0.75}[
            pipeline_output.audio_volume.volume_interpretation
        ]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                label="Sugerowany wiek odbiorcy tekstu",
                value=pipeline_output.simple_speech_metrics.suggested_text_recipient_age,
            )
            st.write(f"{pipeline_output.simple_speech_metrics.suggested_text_recipient_interpretation}.")
        with col2:
            st.metric(
                label="Liczba zidentyfikowanych osób",
                value=pipeline_output.people_count.number_of_persons,
            )
            st.write(pipeline_output.people_count.description)
        with col3:
            gauge(
                pipeline_output.audio_volume.volume_value,
                gTitle=pipeline_output.audio_volume.volume_interpretation,
                gcLow="#FF9400",
                gcMid="#1B8720",
                gcHigh="#FF9400",
                gSize="FULL",
                sFix=" dB",
                grLow=-42,
                grMid=-30,
                arBot=-76,
                arTop=12,
            )
        st.caption(
            "Sugerowany wiek odbiorcy oszacowano na podstawie średniej ważonej metryk Gunninga-Foga i Flescha-Kincaida."
        )

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                label="Przerwy w mówieniu",
                value="Tak" if not pipeline_output.audio_pauses.raw_score else "Nie",
            )
            st.write(pipeline_output.audio_pauses.interpretation)

            st.divider()
            st.metric(
                label="Zmiana tematu",
                value="Tak" if pipeline_output.llm_analysis.topic_changed_during_conversation else "Nie",
            )
            if pipeline_output.llm_analysis.topic_changed_during_conversation:
                st.write("W danym nagraniu tematy wypowiedzi zmieniali się następująco:")
                for topic in pipeline_output.llm_analysis.list_of_topics:
                    st.write(f"> :red[_{topic}_]")
            else:
                st.write("W danym nagraniu nie wykryliśmy zmiany tematu wypowiedzi. Temat wideo, to: ")
                st.write(f"> :green[_{pipeline_output.llm_analysis.list_of_topics[0]}_]")

        with col2:
            st.write(f"> :blue[_Mimika: {pipeline_output.video_processing.face_mimic}_]")
            st.write(f"> :blue[_Ton wypowiedzi: {pipeline_output.video_processing.speech_tone}_]")
            st.write(f"> :blue[_Gestykulacja: {pipeline_output.video_processing.gesticulation}_]")
            st.write(f"> :blue[_Emocje: {pipeline_output.video_processing.emotions}_]")
            st.write(f"> :blue[_Mowa nienawiści: {pipeline_output.video_processing.hate_speech}_]")
            st.write(f"> :blue[_Rozbieżności: {pipeline_output.video_processing.discrepancies}_]")

        st.divider()
        tab_jcn, tab_rep, tab_passive, tab_questions = st.tabs(
            ["Liczby, żargon i skomplikowane słowa", "Powtórzenia", "Liczba bierna", "Pytania do wypowiedzi"]
        )
        with tab_jcn:
            annotated_text(*pipeline_output.llm_analysis.annotated_text_jcn)
        with tab_rep:
            annotated_text(*pipeline_output.llm_analysis.annotated_text_repetitions)
        with tab_passive:
            annotated_text(*pipeline_output.llm_analysis.annotated_text_passive_voice)
        with tab_questions:
            for i in range(3):
                question = getattr(pipeline_output.questions_generated, f"question_{randint(1, 10)}")
                st.write(f"> _{question}_")
