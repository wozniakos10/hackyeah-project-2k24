from typing import Any, cast

from dotenv import load_dotenv
from openai import OpenAI

from hackyeah_project_lib.text_processing.llm_processor.models import RefinedTextProperties, TextPropertiesDetectedByLLM
from hackyeah_project_lib.text_processing.llm_processor.prompts import Prompts


class LLMProcessor:
    def __init__(self) -> None:
        load_dotenv()
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
            ],
        )

    # Funkcja wysyłająca pytanie do OpenAI
    def ask_openai(self, question: str, json_data: dict[str, Any]) -> str:
        # Połącz pytanie użytkownika z danymi o manipulacjach
        content = (
            f"Użytkownik zapytał: '{question}'. Oto dane dotyczące manipulacji w wideo:\n{json_data}\n"
            f"Opisz manipulacje wideo na podstawie tego pytania."
        )

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Jesteś ekspertem od analizy manipulacji w wideo. Korzystając z dostarczonych "
                    "informacji JSON odpowiedz użytkownikowi na zadane pytanie dotyczące manipulacji w "
                    "udostępionym przez niego video. Możesz korzystać tylko z dostarczonych przez nas danych. "
                    "Nie możesz odpowiedzieć na pytanie nie dotyczące manipulacji video! Jeśli użytkownik zada "
                    "pytanie nie związane z tematem, powiedz mu ze nie mozesz odpowiedziec na to pytanie.",
                },
                {"role": "user", "content": content},
            ],
        )

        return cast(str, response.choices[0].message.content)
