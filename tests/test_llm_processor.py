import pytest

from hackyeah_project_lib.text_processing.llm_processor.processor import LLMProcessor
from hackyeah_project_lib.training_data.transcriptions import TrainingData


@pytest.mark.xfail()
@pytest.mark.parametrize(
    "transcription,exp_rep,exp_topic_change",
    [
        (TrainingData.transcriptions[0].transcription, ["środków", "publicznych"], False),
        (TrainingData.transcriptions[1].transcription, [], True),
        (TrainingData.transcriptions[2].transcription, [], True),
    ],
)
def test_llm_processor(
    transcription: str, exp_rep: list[str], exp_topic_change: bool, llm_processor: LLMProcessor
) -> None:
    result = llm_processor.get_refined_text_properties(transcription)

    for rep in exp_rep:
        assert rep in result.repetitions, f"Expected repeated word {rep} not found in llm-detected repetitions"

    print(result.topic_changed_during_conversation)
    assert exp_topic_change == result.topic_changed_during_conversation
