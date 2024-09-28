import nltk
from nltk.tokenize import RegexpTokenizer

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('cmudict')


class Text:
    def __init__(self, text: str):
        self.raw_text = text
        self.sentences = nltk.sent_tokenize(self.raw_text, language='polish')
        self._tokenizer = RegexpTokenizer(r'\w+')  # tokenizer that excludes punctuation
        self.words = self._tokenizer.tokenize(self.raw_text)
        # self.words = nltk.word_tokenize(self.raw_text, language='polish')

    def _count_syllables(self, word: str) -> int:
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
        COMPLEX_WORD_SYLL_NUM = 4  # word is complex if contains >= X syllables
        complex_words = [word for word in self.words if self._count_syllables(word) >= COMPLEX_WORD_SYLL_NUM]

        # calculate Gunning Fog index
        return 0.4 * (len(self.words) / len(self.sentences) + 100 * (len(complex_words) / len(self.words)))

    def get_lix_metric(self):
        COMPLEX_WORD_CHAR_NUM = 7
        complex_words = [word for word in self.words if self._count_syllables(word) >= COMPLEX_WORD_CHAR_NUM]

        # calculate Lesbarhets index
        return (len(self.words) / len(self.sentences) + 100 * (len(complex_words) / len(self.words)))

    def get_flesh_metric(self) -> float:
        """
        Score 	      School level (US)  Notes
        100.00–90.00  5th grade 	     Very easy to read. Easily understood by an average 11-year-old student.
        90.0–80.0 	  6th grade 	     Easy to read. Conversational English for consumers.
        80.0–70.0 	  7th grade 	     Fairly easy to read.
        70.0–60.0 	  8th & 9th grade    Plain English. Easily understood by 13- to 15-year-old students.
        60.0–50.0 	  10 - 12th grade    Fairly difficult to read.
        50.0–30.0 	  College 	         Difficult to read.
        30.0–10.0 	  College graduates  Very difficult to read. Best understood by university graduates.
        10.0–0.0 	  Professional 	     Extremely difficult to read. Best understood by university graduates.
        :return: score from table above
        """
        syllable_count = sum(self._count_syllables(word) for word in self.words)

        # flesch calculation
        return 206.835 - (1.015 * len(self.words) / len(self.sentences)) - (84.6 * syllable_count / len(self.words))

    def get_kincaid_grade(self):
        syllable_count = sum(self._count_syllables(word) for word in self.words)

        # kincaid calculation
        return (0.39 * len(self.words) / len(self.sentences)) + (11.8 * syllable_count / len(self.words)) - 15.59

    # def get_final_metric(self, gun_w: float = 0.4, lix_w: float = 0.4, fle_w: float = 0.1, kin_w: float = 0.1) -> float:
    #     if gun_w + lix_w + fle_w + kin_w != 1:
    #         raise ValueError('Incorrect weight coefficient')
    #
    #     gunning_w = g_to_f_weight
    #     flesch_w = 1 - gunning_w
    #
    #     final_metric = (gunning_w * self.get_gunning_metric() + flesch_w * self.get_flesh_metric()) / 2
    #     return final_metric

    def __str__(self):
        return f'{self.get_gunning_metric()=} ; {self.get_flesh_metric()=} ; {self.get_kincaid_grade()=}'


# text1 = Text(
#     """
#     Już w roku 1952 amerykański biznesmen Robert Gunning sformułował algorytm sprawdzania trudności odbioru tekstu.
#     Współczynnik mglistości (Fog Index) Roberta Gunninga jest najpopularniejszym do dziś wykorzystywanym narzędziem
#     dla teksów anglojęzycznych. Został opracowany dla dziennikarzy z USA. Można jednak z łatwością dostosować jego
#     założenia do realiów języka polskiego. Według Gunninga trudne słowa to te, które zawierają więcej niż trzy sylaby.
#     W języku polskim za słowa złożone można uznać te, które składają się dopiero z 4 sylab. Założenie ogólne jest
#     proste - łatwiejsze w zrozumieniu są krótkie wyrazy i zdania niż długie, rozbudowane wypowiedzi. Zwłaszcza artykuł
#     pisany na potrzeby internetu, ze względu na już dawno zbadaną specyfikę czytania w internecie, powinien
#     charakteryzować się takimi cechami. Realizacja tych założeń pozwala także zwiększyć tempo czytania.
#     """
# )
# print(text1.get_kincaid_grade())
#
# c = 0
# for word in text1.words:
#     print(f'{word}: {text1._count_syllables(word)}')
#     c += text1._count_syllables(word)
#
# print('final count', c)
#
# print(text1)
