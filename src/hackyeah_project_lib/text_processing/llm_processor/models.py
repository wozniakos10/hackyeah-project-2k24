from pydantic import BaseModel, Field

from hackyeah_project_lib.text_processing.llm_processor.prompts import Prompts


class TextPropertiesDetectedByLLM(BaseModel):
    repetitions: list[str] = Field(description=Prompts.text_properties_descriptions.repetitions, default_factory=list)
    list_of_topics: list[str] = Field(
        description=Prompts.text_properties_descriptions.list_of_topics, default_factory=list
    )
    numbers: list[int] = Field(description=Prompts.text_properties_descriptions.numbers, default_factory=list)
    jargon: list[str] = Field(description=Prompts.text_properties_descriptions.jargon, default_factory=list)
    passive_voice: list[str] = Field(
        description=Prompts.text_properties_descriptions.passive_voice, default_factory=list
    )
    complicated_words: list[str] = Field(
        description=Prompts.text_properties_descriptions.complicated_words, default_factory=list
    )
    complicated_sentences: list[str] = Field(
        description=Prompts.text_properties_descriptions.complicated_sentences, default_factory=list
    )


class RefinedTextProperties(TextPropertiesDetectedByLLM):
    high_likelihood_repetitions: list[str]
    low_likelihood_repetitions: list[str]
    topic_changed_during_conversation: bool
    filtered_passive_voice: list[str]


class TextQuestionByLLm(BaseModel):
    question_1: str = Field(description="Gene", default_factory=str)
    question_2: str = Field(description=Prompts.question_generates_prompt.question_prompt, default_factory=str)
    question_3: str = Field(description=Prompts.question_generates_prompt.question_prompt, default_factory=str)
    question_4: str = Field(description=Prompts.question_generates_prompt.question_prompt, default_factory=str)
    question_5: str = Field(description=Prompts.question_generates_prompt.question_prompt, default_factory=str)
    question_6: str = Field(description=Prompts.question_generates_prompt.question_prompt, default_factory=str)
    question_7: str = Field(description=Prompts.question_generates_prompt.question_prompt, default_factory=str)
    question_8: str = Field(description=Prompts.question_generates_prompt.question_prompt, default_factory=str)
    question_9: str = Field(description=Prompts.question_generates_prompt.question_prompt, default_factory=str)
    question_10: str = Field(description=Prompts.question_generates_prompt.question_prompt, default_factory=str)
