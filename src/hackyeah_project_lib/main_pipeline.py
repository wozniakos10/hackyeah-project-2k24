import json
import logging
from pathlib import Path

import streamlit as st
from pydantic import BaseModel

from hackyeah_project_lib.audio_processing.audio_converter import AudioConverter
from hackyeah_project_lib.audio_processing.audio_features import AudioVolumeModel, AudioVolumeProcessor, PauseDetection
from hackyeah_project_lib.audio_processing.transcription import transcribe_audio
from hackyeah_project_lib.audio_processing.transcription_srt import transcribe_audio_srt
from hackyeah_project_lib.audio_processing.xgboost_pause_detection import XGBoostClassifier, XGBoostPauseClassifierModel
from hackyeah_project_lib.text_processing.llm_processor.models import RefinedTextProperties, TextQuestionByLLm
from hackyeah_project_lib.text_processing.llm_processor.processor import LLMProcessor
from hackyeah_project_lib.text_processing.speech_metrics import SimpleSpeechMetricsProcessor, SpeechMetricsModel
from hackyeah_project_lib.utils.logger import get_configured_logger
from hackyeah_project_lib.utils.s3 import S3
from hackyeah_project_lib.video_processing import count_people_on_video
from hackyeah_project_lib.video_processing.count_people_on_video import PeopleCountModel
from hackyeah_project_lib.video_processing.gcp import send_message_to_gemini
from hackyeah_project_lib.video_processing.models import VideoProcessingResponse
from hackyeah_project_lib.video_processing.reduce_mp4_size import compress_video
from hackyeah_project_lib.video_processing.video_to_audio import VideoConverter


class PipelineResponseModel(BaseModel):
    s3_bucket_path: str
    mp4_path: str
    mp3_path: str
    wav_path: str
    people_count: PeopleCountModel
    audio_volume: AudioVolumeModel
    audio_pauses: XGBoostPauseClassifierModel
    transcription_srt: str
    transcription: str
    key_words_phrases: str
    questions_generated: TextQuestionByLLm
    llm_analysis: RefinedTextProperties
    simple_speech_metrics: SpeechMetricsModel
    video_processing: VideoProcessingResponse


class MainPipelineException(Exception):
    pass


class MainPipeline:
    steps_percentage = {
        0: 0,
        1: 5,
        2: 20,
        3: 25,
        4: 30,
        5: 40,
        6: 45,
        7: 50,
        8: 65,
        9: 70,
        10: 75,
        11: 80,
        12: 90,
        13: 100,
    }
    step_counter: int = 0

    def __init__(
        self,
        unique_id: str,
        progress_bar: st.delta_generator.DeltaGenerator | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.unique_id = unique_id
        if logger is None:
            logger = get_configured_logger("pipeline_logger", log_file="logs/app.log", level=logging.DEBUG)
        self.logger = logger
        if progress_bar is None:
            progress_bar = st.delta_generator.DeltaGenerator(root_container=None)
        self.progress_bar = progress_bar
        self.s3_class = S3()

    def describe_step(self, desc: str) -> None:
        self.step_counter += 1
        desc = f"Krok {self.step_counter}: {desc}"
        if self.progress_bar is not None:
            self.progress_bar.progress(self.steps_percentage[self.step_counter], text=desc)
        self.logger.debug(desc)

    def run(self, input_video_path: Path) -> PipelineResponseModel:
        self.step_counter = 0
        self.progress_bar.progress(self.steps_percentage[self.step_counter])

        # Step 1: Compress video
        self.describe_step(desc="Kompresja wideo...")
        compressed_video_path = f"/tmp/{input_video_path.stem}_compressed{input_video_path.suffix}"
        compress_video(video_full_path=input_video_path, output_file_name=compressed_video_path)

        # Step 2: Convert video to MP3 and WAV
        self.describe_step(desc="Konwersja wideo na MP3 i WAV...")
        mp3_path = f"/tmp/{input_video_path.stem}_audio.mp3"
        wav_path = f"/tmp/{input_video_path.stem}_audio.wav"
        VideoConverter(path=compressed_video_path).mp4_to_mp3(path_to_mp3=mp3_path)
        AudioConverter(path=mp3_path).mp3_to_wav(path_to_wav=wav_path)

        # Step 3: Upload file to S3
        self.describe_step(desc="Przesyłanie pliku do chmury...")
        s3_object_name = f"app/{self.unique_id}/{input_video_path.name}"
        if not self.s3_class.upload_file(file_name=input_video_path.as_posix(), object_name=s3_object_name):
            raise MainPipelineException("Error while uploading file to S3.")
        s3_file_url = self.s3_class.get_file_url(object_name=s3_object_name)

        # Step 4: Count number of people
        self.describe_step(desc="Zliczanie ludzie na wideo...")
        people_count = count_people_on_video.num_people(
            *count_people_on_video.analyze_video(input_video_path.as_posix())
        )

        # Step 5: Audio volume analysis
        self.describe_step(desc="Analiza głośności audio...")
        audio_volume = AudioVolumeProcessor(path=input_video_path.as_posix()).run()

        # Step 6: Pause detection
        self.describe_step(desc="Detekcja pauz...")
        pause_interval_info = PauseDetection(path=wav_path).pause_interval()
        xgboost_classifier = XGBoostClassifier()
        audio_pauses = xgboost_classifier.format_output(xgboost_classifier.predict(pause_interval_info))

        # Step 7: Speech to text transcription (SRT)
        self.describe_step(desc="Transkrypcja mowy na tekst (SRT)...")
        transcription_srt = transcribe_audio_srt(mp3_path)

        # Step 8: Speech to text transcription (normal)
        self.describe_step(desc="Transkrypcja mowy na tekst (normal)...")
        transcription = transcribe_audio(mp3_path)

        # Step 9: Transcription summarization
        self.describe_step(desc="Podsumowanie tekstu po transkrypcji...")

        key_words_phrases = LLMProcessor().get_key_words(transcription)

        # Step 10: Question generation
        self.describe_step(desc="Tworzenie pytan do tekstu...")

        questions_generated = LLMProcessor().get_10_question(transcription)

        # Step 11: LLM metrics
        self.describe_step(desc="Analiza wyodrębnionego tekstu...")
        llm_analysis_result = LLMProcessor().get_refined_text_properties(transcription)

        # Step 12: Calculate speech metrics
        self.describe_step(desc="Obliczenie metryk zrozumiałości tekstu...")
        simple_speech_metrics = SimpleSpeechMetricsProcessor(transcription).get_all_metrics()

        # Step 13: Video processing
        self.describe_step(desc="Przetwarzanie wideo...")
        video_processing = send_message_to_gemini(file_url=s3_file_url)

        value = PipelineResponseModel(
            s3_bucket_path=s3_object_name,
            mp4_path=input_video_path.as_posix(),
            mp3_path=mp3_path,
            wav_path=wav_path,
            people_count=people_count,
            audio_volume=audio_volume,
            audio_pauses=audio_pauses,
            transcription_srt=transcription_srt,
            transcription=transcription,
            key_words_phrases=key_words_phrases,
            questions_generated=questions_generated,
            llm_analysis=llm_analysis_result,
            simple_speech_metrics=simple_speech_metrics,
            video_processing=video_processing,
        )
        self.logger.info(f"Formatted output: {json.dumps(value.model_dump(mode='python'),indent=2)}")
        return value
