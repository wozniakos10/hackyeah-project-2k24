import os
from pathlib import Path

import yaml
from pydantic import BaseModel

CURRENT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


class TextPropertiesDescriptions(BaseModel):
    repetitions: str
    list_of_topics: str
    numbers: str
    jargon: str
    passive_voice: str
    complicated_words: str
    complicated_sentences: str
    english_translation: str


class SystemPrompts(BaseModel):
    extract_text_properties: str


class PromptsModel(BaseModel):
    text_properties_descriptions: TextPropertiesDescriptions
    system_prompts: SystemPrompts


with open(CURRENT_DIR.joinpath("prompts.yaml"), "r") as file:
    yaml_data = yaml.safe_load(file)

Prompts = PromptsModel(**yaml_data)
