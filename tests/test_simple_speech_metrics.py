import pytest

from hackyeah_project_lib.utils import simple_speech_metrics


easy_text = simple_speech_metrics.SimpleSpeechIdentifier(
    """
    Pies to zwierzę, które jest bardzo przyjacielskie. Pies lubi biegać, bawić się i skakać. Ma cztery nogi, 
    ogon i uszy. Psy mogą być różnych kolorów: czarne, białe, brązowe i nawet w plamy!
    Psy lubią jeść karmę i czasami smakołyki. Lubię bawić się z psem w piłkę. Kiedy mówisz „chodź tutaj!”, 
    pies przybiega do ciebie, bo chce być blisko.
    Psy są naszymi przyjaciółmi i mogą nas strzec. Gdy są szczęśliwe, merdają ogonem. 
    Pies to najlepszy przyjaciel człowieka!
    """.replace('\n', ' ').replace('    ', '').strip()
)

mid_text = simple_speech_metrics.SimpleSpeechIdentifier(
    """
    Już w roku 1952 amerykański biznesmen Robert Gunning sformułował algorytm sprawdzania trudności odbioru tekstu. 
    Współczynnik mglistości (Fog Index) Roberta Gunninga jest najpopularniejszym do dziś wykorzystywanym narzędziem 
    dla teksów anglojęzycznych. Został opracowany dla dziennikarzy z USA. Można jednak z łatwością dostosować jego 
    założenia do realiów języka polskiego. Według Gunninga trudne słowa to te, które zawierają więcej niż trzy sylaby. 
    W języku polskim za słowa złożone można uznać te, które składają się dopiero z 4 sylab. Założenie ogólne jest 
    proste - łatwiejsze w zrozumieniu są krótkie wyrazy i zdania niż długie, rozbudowane wypowiedzi. Zwłaszcza artykuł 
    pisany na potrzeby internetu, ze względu na już dawno zbadaną specyfikę czytania w internecie, powinien 
    charakteryzować się takimi cechami. Realizacja tych założeń pozwala także zwiększyć tempo czytania.
    """.replace('\n', ' ').replace('    ', '').strip()
)

difficult_text = simple_speech_metrics.SimpleSpeechIdentifier(
    """
    Sieć neuronowa - system przeznaczony do przetwarzania informacji, którego budowa i zasada działania są w pewnym 
    stopniu wzorowane na funkcjonowaniu fragmentów rzeczywistego (biologicznego) systemu nerwowego. Na przesłankach 
    biologicznych oparte są schematy sztucznych neuronów wchodzących w skład sieci oraz (w pewnym stopniu) jej 
    struktura. Jednak schematy połączeń neuronów w sieci neuronowej są wybierane arbitralnie, a nie stanowią modelu 
    rzeczywistych struktur nerwowych.
    Wyróżniającą cechą sieci neuronowej jako narzędzia informatycznego jest możliwość komputerowego rozwiązywania przy 
    jej pomocy praktycznych problemów bez ich uprzedniej matematycznej formalizacji. Dalszą zaletą jest brak 
    konieczności odwoływania się przy stosowaniu sieci do jakichkolwiek teoretycznych założeń na temat rozwiązywanego 
    problemu.
    """.replace('\n', ' ').replace('    ', '').strip()
)


@pytest.mark.parametrize(
    "text, sentences_num", [
        (easy_text, 10),
        (mid_text, 9),
        (difficult_text, 5)
    ]
)
def test_count_sentences(text: simple_speech_metrics.SimpleSpeechIdentifier, sentences_num: int):
    assert len(text.sentences) == sentences_num


@pytest.mark.parametrize(
    "text, words_num", [
        (easy_text, 76),
        (mid_text, 119),
        (difficult_text, 98)
    ]
)
def test_count_words(text: simple_speech_metrics.SimpleSpeechIdentifier, words_num: int):
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
    assert simple_speech_metrics.SimpleSpeechIdentifier._count_syllables(word=word) == correct_syllables_num


@pytest.mark.parametrize(
    "text, gun_metric", [
        (easy_text, 4.6),
        (mid_text, 10),
        (difficult_text, 17)
    ]
)
def test_get_gunning_metric(text: simple_speech_metrics.SimpleSpeechIdentifier, gun_metric: float):
    min, max = gun_metric * 0.8, gun_metric * 1.2
    assert (min < text.get_gunning_metric() < max)

@pytest.mark.parametrize(
    "text, flesch_metric", [
        (easy_text, 7),
        (mid_text, 15),
        (difficult_text, 20)
    ]
)
def test_get_flesh_kincaid_metric(text: simple_speech_metrics.SimpleSpeechIdentifier, flesch_metric: float):
    min, max = flesch_metric * 0.8, flesch_metric * 1.2
    assert (min < text.get_flesh_kincaid_metric() < max)


@pytest.mark.parametrize(
    "text, final_min_age, final_max_age", [
        (easy_text, 0, 11),
        (mid_text, 17, 21),
        (difficult_text, 21, 100)
    ]
)
def test_get_final_score(text: simple_speech_metrics.SimpleSpeechIdentifier, final_min_age: int, final_max_age: int):
    assert (final_min_age < text._get_final_score() < final_max_age)
