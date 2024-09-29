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

    @staticmethod
    def _word_in_list(word: str, words_list: list[str]) -> bool:
        return (
            len(word) > 3
            and any(word in element or element in word for element in words_list)
            or len(word) <= 3
            and word in words_list
        )

    def get_refined_text_properties(self, text: str) -> RefinedTextProperties:
        llm_text_properties = self.get_text_properties_with_llm(text)
        filtered_passive_voice = [
            phrase
            for phrase in llm_text_properties.passive_voice
            if self._check_for_common_passive_voice_properties(phrase)
        ]
        annotated_text: list[str | tuple[str, str]] = []
        for word in text.split(" "):
            if self._word_in_list(word, llm_text_properties.repetitions):
                annotated_text.append((word, "powtórzenie"))
            elif self._word_in_list(word, llm_text_properties.jargon):
                annotated_text.append((word, "żargon"))
            elif self._word_in_list(word, llm_text_properties.complicated_words):
                annotated_text.append((word, "skomplikowane"))
            elif any(word in element or element in word for element in llm_text_properties.numbers):
                annotated_text.append((word, "liczba"))
            elif self._word_in_list(
                word, [passive_word for sentence in filtered_passive_voice for passive_word in sentence.split(" ")]
            ):
                annotated_text.append((word, "liczba bierna"))
            else:
                annotated_text.append(word)
        annotated_text = [f"{word} " if isinstance(word, str) else (f"{word[0]} ", word[1]) for word in annotated_text]

        return RefinedTextProperties(
            **llm_text_properties.model_dump(mode="python"),
            high_likelihood_repetitions=[rep for rep in llm_text_properties.repetitions if len(rep) > 3],
            low_likelihood_repetitions=[rep for rep in llm_text_properties.repetitions if len(rep) <= 3],
            topic_changed_during_conversation=len(llm_text_properties.list_of_topics) > 1,
            filtered_passive_voice=filtered_passive_voice,
            annotated_text=annotated_text,
        )

    def ask_openai(self, question: str, json_data: dict[str, Any]) -> str:
        # Połącz pytanie użytkownika z danymi o manipulacjach
        content = (
            f"Użytkownik zapytał: '{question}'. Oto dane dotyczące manipulacji w wideo:\n{json_data}\nOpisz manipulacje"
            " wideo na podstawie tego pytania."
        )

        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Jesteś ekspertem od analizy manipulacji w wideo. Korzystając z dostarczonych informacji"
                        " JSONodpowiedz użytkownikowi na zadane pytanie dotyczące manipulacji w udostępionym przez"
                        " niego video. Możesz korzystać tylko z dostarczonychprzez nas danych. Nie możesz odpowiedzieć"
                        " na pytanie nie dotyczące manipulacji video! Jeśli użytkownik zada pytanie niezwiązane z"
                        " tematem, powiedz mu ze nie mozesz odpowiedziec na to pytanie."
                    ),
                },
                {"role": "user", "content": content},
            ],
        )

        return cast(str, response.choices[0].message.content)
