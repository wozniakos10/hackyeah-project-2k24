from typing import Any, cast

from dotenv import load_dotenv
from openai import OpenAI

from hackyeah_project_lib.text_processing.llm_processor.models import (
    RefinedTextProperties,
    TextPropertiesDetectedByLLM,
    TextQuestionByLLm,
)
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

    @staticmethod
    def _add_word_spaces(annotated_text: list[str | tuple[str, str]]) -> list[str | tuple[str, str]]:
        return [f"{word} " if isinstance(word, str) else (f"{word[0]} ", word[1]) for word in annotated_text]

    @staticmethod
    def _combine_same_types(annotated_text: list[str | tuple[str, str]]) -> list[str | tuple[str, str]]:
        new_annotated_text: list[str | tuple[str, str]] = []
        for word in annotated_text:
            if not new_annotated_text:
                new_annotated_text.append(word)
                continue

            last_element = new_annotated_text[-1]
            last_type = None if isinstance(last_element, str) else last_element[1]

            if isinstance(word, str) and last_type is None:
                # Both the current word and the last element are strings; concatenate them.
                new_annotated_text[-1] += word  # type: ignore
            elif isinstance(word, tuple) and last_type == word[1]:
                # Both the current word and the last element are tuples with the same type; combine them.
                new_annotated_text[-1] = (last_element[0] + word[0], word[1])
            else:
                # Different types; append the current word as a new element.
                new_annotated_text.append(word)
        return new_annotated_text

    def get_refined_text_properties(self, text: str) -> RefinedTextProperties:
        llm_text_properties = self.get_text_properties_with_llm(text)
        filtered_passive_voice = [
            phrase
            for phrase in llm_text_properties.passive_voice
            if self._check_for_common_passive_voice_properties(phrase)
        ]
        annotated_text_jcn: list[str | tuple[str, str]] = []
        annotated_text_repetitions: list[str | tuple[str, str]] = []
        annotated_text_passive_voice: list[str | tuple[str, str]] = []
        for word in text.split(" "):
            if self._word_in_list(word, llm_text_properties.jargon):
                annotated_text_jcn.append((word, "żargon"))
            elif self._word_in_list(word, llm_text_properties.complicated_words):
                annotated_text_jcn.append((word, "skomplikowane"))
            elif any(word in element or element in word for element in llm_text_properties.numbers):
                annotated_text_jcn.append((word, "liczba"))
            else:
                annotated_text_jcn.append(word)

            if self._word_in_list(word, llm_text_properties.repetitions):
                annotated_text_repetitions.append((word, "powtórzenie"))
            else:
                annotated_text_repetitions.append(word)

            if self._word_in_list(
                word, [passive_word for sentence in filtered_passive_voice for passive_word in sentence.split(" ")]
            ):
                annotated_text_passive_voice.append((word, "liczba bierna"))
            else:
                annotated_text_passive_voice.append(word)

        annotated_text_jcn = self._combine_same_types(self._add_word_spaces(annotated_text_jcn))
        annotated_text_repetitions = self._combine_same_types(self._add_word_spaces(annotated_text_repetitions))
        annotated_text_passive_voice = self._combine_same_types(self._add_word_spaces(annotated_text_passive_voice))

        return RefinedTextProperties(
            **llm_text_properties.model_dump(mode="python"),
            high_likelihood_repetitions=[rep for rep in llm_text_properties.repetitions if len(rep) > 3],
            low_likelihood_repetitions=[rep for rep in llm_text_properties.repetitions if len(rep) <= 3],
            topic_changed_during_conversation=len(llm_text_properties.list_of_topics) > 1,
            filtered_passive_voice=filtered_passive_voice,
            annotated_text_jcn=annotated_text_jcn,
            annotated_text_repetitions=annotated_text_repetitions,
            annotated_text_passive_voice=annotated_text_passive_voice,
        )

    def get_10_question(self, text: str) -> TextQuestionByLLm:
        completion = self.openai_client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": Prompts.system_prompts.question_prompt},
                {"role": "user", "content": text},
            ],
            response_format=TextQuestionByLLm,
            temperature=0.2,
            top_p=0.99,
        )
        questions = cast(TextQuestionByLLm, completion.choices[0].message.parsed)
        return TextQuestionByLLm(**questions.model_dump(mode="python"))

    def get_key_words(self, text: str) -> Any:
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": Prompts.system_prompts.extract_text_properties},
                {"role": "user", "content": text},
            ],
            temperature=0.2,
            top_p=0.99,
        )
        return response.choices[0].message.content

    # Funkcja wysyłająca pytanie do OpenAI
    def ask_openai(self, question: str, json_data: dict[str, Any]) -> str:
        # Połącz pytanie użytkownika z danymi o manipulacjach
        content = (
            f"Użytkownik zapytał: '{question}'. Oto dane dotyczące manipulacji w wideo:\n{json_data}\n"
            "Opisz manipulacje wideo na podstawie tego pytania."
        )

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Jesteś ekspertem od analizy manipulacji w wideo. Korzystając z dostarczonych informacji JSON"
                        " odpowiedz użytkownikowi na zadane pytanie dotyczące manipulacji w udostępnionym przez niego"
                        " video. Możesz korzystać tylko z dostarczonych przez nas danych. Nie możesz odpowiedzieć na"
                        " pytanie nie dotyczące manipulacji video! Jeśli użytkownik zada pytanie nie związane z"
                        " tematem, powiedz mu ze nie możesz odpowiedzieć na to pytanie. W żadnym bądź razie nie podawaj"
                        " 'surowych' pól z JSONa, który otrzymałeś. W przypadku pytań o dokładne pola, odpowiadaj w"
                        " sposób bardziej ogólny, tak aby użytkownik nie mógł zrozumieć dokładnie co ty widziałeś"
                        " wcześniej.  "
                    ),
                },
                {"role": "user", "content": content},
            ],
        )

        return cast(str, response.choices[0].message.content)

    def ask_openai_for_multiple_videos(
        self, question: str, json_data_1: dict[str, Any], json_data_2: dict[str, Any]
    ) -> str:
        # Połącz pytanie użytkownika z danymi o manipulacjach
        content = (
            f"Użytkownik zapytał: '{question}'. Oto dane dotyczące wideo numer 1:\n{json_data_1}\nOto dane dotyczące"
            f" wideo numer 2:\n{json_data_2}\nPorównaj te dwa wideo na podstawie tego pytania."
        )

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Jesteś ekspertem od analizy manipulacji w wideo. Korzystając z dostarczonych informacji"
                        " JSON odpowiedz użytkownikowi na zadane pytanie dotyczące porównania wideo. Możesz korzystać"
                        " tylko z dostarczonych przez nas danych. Jeśli użytkownik zada pytanie niezwiązane z tematem,"
                        " powiedz mu ze nie możesz odpowiedzieć na to pytanie. W żadnym bądź razie nie podawaj"
                        " 'surowych' pól z JSONa, który otrzymałeś. W przypadku pytań o dokładne pola, odpowiadaj w"
                        " sposób bardziej ogólny, tak aby użytkownik nie mógł zrozumieć dokładnie co ty widziałeś"
                        " wcześniej.  "
                    ),
                },
                {"role": "user", "content": content},
            ],
        )

        return cast(str, response.choices[0].message.content)
