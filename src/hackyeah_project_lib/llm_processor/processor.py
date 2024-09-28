from typing import cast

from openai import OpenAI, models

from hackyeah_project_lib.llm_processor.models import TextPropertiesDetectedByLLM, RefinedTextProperties
from hackyeah_project_lib.llm_processor.prompts import Prompts, TextPropertiesDescriptions


class LLMProcessor:

    def __init__(self):
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

    def get_refined_text_properties(self, text) -> RefinedTextProperties:
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


if __name__ == "__main__":
    resp = LLMProcessor().get_refined_text_properties(
        """W budżecie na 2025 rok przeznaczymy ponad 221,7 mld zł na ochronę. Rekordowy wzrost nakładów na ochronę 
        zdrowia zgodnie z ustawą o blisko 31,7 mld zł, to jest to 0,6%. 0,5 mld zł na realizację programu In Vitro, 
        8,4 mld zł na realizację świadczeń aktywny rodzic, 62,8 mld zł na program Rodzina 800+."""
    )
    print(resp)
    resp = LLMProcessor().get_refined_text_properties(
        """Audytem objęliśmy 96 podmiotów, a łączna kwota badanych środków publicznych to około 100 miliardów złotych.
         W toku działań stwierdziliśmy m.in. niegospodarne i niecelowe wydatkowanie środków publicznych, udzielenie 
         dotacji podmiotów, które nie spełniały kryteriów konkursowych."""
    )
    print(resp)
    resp = LLMProcessor().get_refined_text_properties(
        """W pierwszej połowie lipca przeprowadziliśmy ogólnopolską akcję wzmożonej kontroli przesyłek pocztowych oraz 
        kuriarskich. Funkcjonariusze przeprowadzili kontrolę w 18 punktach w całej Polsce. Wrześniowa zmiana warunków 
        oprocentowania obligacji oszczędnościowych wynika z potrzeby ich dostosowania do bieżących realiów rynkowych."""
    )
    print(resp)
