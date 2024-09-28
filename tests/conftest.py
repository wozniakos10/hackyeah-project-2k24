import pytest

from hackyeah_project_lib.text_processing.llm_processor.processor import LLMProcessor


@pytest.fixture(scope="module")
def llm_processor() -> LLMProcessor:
    return LLMProcessor()
