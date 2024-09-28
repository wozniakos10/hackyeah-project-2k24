import nltk
import pandas as pd
from nltk.tokenize import RegexpTokenizer

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("cmudict")


class SimpleSpeechIdentifier:
    def __init__(self, text: str):
        self.raw_text = text
        self.sentences = nltk.sent_tokenize(self.raw_text, language="polish")
        self._tokenizer = RegexpTokenizer(r"\w+")  # tokenizer that excludes punctuation
        self.words = self._tokenizer.tokenize(self.raw_text)
        self.scores_df = pd.DataFrame(
            {
                "min_age": [0, 11, 13, 17, 21],
                "max_age": [11, 13, 17, 21, 100],
                "notes": [
                    "Bardzo łatwy do przeczytania. Łatwo zrozumiały dla przeciętnego 11-letniego ucznia.",
                    "Dosyć łatwy do przeczytania. Polski konwersacyjny dla turystów.",
                    "Prosty polski. Zrozumiały dla uczniów w wieku 13-15 lat.",
                    "Dosyć trudny do przeczytania. Zawiera wiele złożonych słów",
                    "Bardzo trudny do przeczytania. Najlepiej zrozumiały dla absolwentów uniwersytetu.",
                ],
            }
        )

    @staticmethod
    def _count_syllables(word: str) -> int:
        vowels = "aeiouyąęó"
        count = 0
        on_vowel = False

        for letter in word.lower():
            if letter in vowels:
                if not on_vowel:
                    count += 1
                on_vowel = True
            else:
                on_vowel = False

        return count

    def get_gunning_metric(self) -> float:
        complex_word_syll_num = 4  # word is complex if contains >= X syllables
        complex_words = [word for word in self.words if self._count_syllables(word) >= complex_word_syll_num]

        # calculate Gunning Fog index
        return 0.4 * (len(self.words) / len(self.sentences) + 100 * (len(complex_words) / len(self.words)))

    def get_flesh_kincaid_metric(self) -> float:
        syllable_count = sum(self._count_syllables(word) for word in self.words)

        # flesch calculation
        return (0.39 * len(self.words) / len(self.sentences)) + (11.8 * syllable_count / len(self.words)) - 15.59

    def _get_final_score(self, gun_w: float = 0.7, fk_w: float = 0.3) -> float:
        if gun_w + fk_w != 1:
            raise ValueError("Incorrect weight coefficient")

        # calculate metrics and convert them to avg age of recipient
        gunning_age = self.get_gunning_metric() + 5
        flesch_age = self.get_flesh_kincaid_metric() + 6

        final_metric = gunning_age * gun_w + flesch_age * fk_w  # weighted sum

        return final_metric

    def output_msg(self) -> str:
        final_score = self._get_final_score()
        print(f"{final_score=}")

        # find correct row from table
        row = self.scores_df[
            (self.scores_df["min_age"] <= final_score) & (self.scores_df["max_age"] > final_score)
        ].iloc[0]

        return str(row["notes"])

    def __repr__(self) -> str:
        return (
            f"{self.get_gunning_metric()=} ; {self.get_flesh_kincaid_metric()=} ; "
            f"{self._get_final_score()=} ; {self.output_msg()=}"
        )

    def __str__(self) -> str:
        return f"{self.get_gunning_metric()=} ; {self.get_flesh_kincaid_metric()=}"
