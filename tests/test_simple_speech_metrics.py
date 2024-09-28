import pytest

from hackyeah_project_lib.utils import simple_speech_metrics


text1 = simple_speech_metrics.Text(
    """
    To jest przykładowy tekst, który chcemy ocenić pod kątem trudności czytania.
    Zawiera on kilka złożonych słów, aby sprawdzić działanie współczynnika.
    """
)

text2 = simple_speech_metrics.Text(
    """
    Już w roku 1952 amerykański biznesmen Robert Gunning sformułował algorytm sprawdzania trudności odbioru tekstu. 
    Współczynnik mglistości (Fog Index) Roberta Gunninga jest najpopularniejszym do dziś wykorzystywanym narzędziem 
    dla teksów anglojęzycznych. Został opracowany dla dziennikarzy z USA. Można jednak z łatwością dostosować jego 
    założenia do realiów języka polskiego. Według Gunninga trudne słowa to te, które zawierają więcej niż trzy sylaby. 
    W języku polskim za słowa złożone można uznać te, które składają się dopiero z 4 sylab. Założenie ogólne jest 
    proste - łatwiejsze w zrozumieniu są krótkie wyrazy i zdania niż długie, rozbudowane wypowiedzi. Zwłaszcza artykuł 
    pisany na potrzeby internetu, ze względu na już dawno zbadaną specyfikę czytania w internecie, powinien 
    charakteryzować się takimi cechami. Realizacja tych założeń pozwala także zwiększyć tempo czytania.
    """
)


@pytest.mark.parametrize(
    "text, sentences_num", [
        (text1, 2),
        (text2, 9),
    ]
)
def test_count_sentences(text: simple_speech_metrics.Text, sentences_num: int):
    assert len(text.sentences) == sentences_num


@pytest.mark.parametrize(
    "text, words_num", [
        (text1, 20),
        (text2, 119),
    ]
)
def test_count_words(text: simple_speech_metrics.Text, words_num: int):
    assert len(text.words) == words_num


@pytest.mark.parametrize(
    "word, correct_syllables_num", [
        ("przykładowy", 4),
        ("tekst", 1),
        ("złożonych", 3),
        ("współczynnika", 4),
        ("internetu", 4),
        ("rowie", 2)
    ]
)
def test_count_syllables(word: str, correct_syllables_num: int):
    assert text1._count_syllables(word=word) == correct_syllables_num


@pytest.mark.parametrize(
    "text, gun_metric", [
        (text1, 4),
        (text2, 8.65),
    ]
)
def test_gunning_metric(text: simple_speech_metrics.Text, gun_metric: float):
    min, max = gun_metric * 0.85, gun_metric * 1.15
    assert (min < text.get_gunning_metric() < max)

@pytest.mark.parametrize(
    "text, flesch_metric", [
        (text1, 78.25),
        (text2, 34.88),
    ]
)
def test_flesch_metric(text: simple_speech_metrics.Text, flesch_metric: float):
    min, max = flesch_metric * 0.85, flesch_metric * 1.15
    assert (min < text.get_flesh_metric() < max)
