import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

CURRENT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


class TranscriptionModel(BaseModel):
    id: int
    transcription: str


class TrainingDataModel(BaseModel):
    transcriptions: list[TranscriptionModel] = Field(default_factory=list)


with open(CURRENT_DIR.joinpath("transcriptions.yaml"), "r") as file:
    yaml_data = yaml.safe_load(file)

TrainingData = TrainingDataModel(**yaml_data)
