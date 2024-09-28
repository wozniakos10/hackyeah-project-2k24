from typing import cast

from openai import OpenAI

from hackyeah_project_lib.text_processing.llm_processor.models import RefinedTextProperties, TextPropertiesDetectedByLLM
from hackyeah_project_lib.text_processing.llm_processor.prompts import Prompts


class LLMProcessor:
    def __init__(self) -> None:
        self.openai_client = OpenAI()

    @staticmethod
    def _check_for_common_passive_voice_properties(phrase: str) -> bool:
        """Verify LLM response by common passive voice properties."""
        if "być" in phrase or "zostać" in phrase:
            return True
        for word in phrase.split(" "):
            if word[-2:] in ("to", "no"):
                return True
        return False

    def get_text_properties_with_llm(self, text: str) -> TextPropertiesDetectedByLLM:
        completion = self.openai_client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": Prompts.system_prompts.extract_text_properties},
                {"role": "user", "content": text},
            ],
            response_format=TextPropertiesDetectedByLLM,
            temperature=0.2,
            top_p=0.99,
        )
        return cast(TextPropertiesDetectedByLLM, completion.choices[0].message.parsed)

    def get_refined_text_properties(self, text: str) -> RefinedTextProperties:
        llm_text_properties = self.get_text_properties_with_llm(text)
        return RefinedTextProperties(
            **llm_text_properties.model_dump(mode="python"),
            high_likelihood_repetitions=[rep for rep in llm_text_properties.repetitions if len(rep) > 3],
            low_likelihood_repetitions=[rep for rep in llm_text_properties.repetitions if len(rep) <= 3],
            topic_changed_during_conversation=len(llm_text_properties.list_of_topics) > 1,
            filtered_passive_voice=[
                phrase
                for phrase in llm_text_properties.passive_voice
                if self._check_for_common_passive_voice_properties(phrase)
            ]
        )
