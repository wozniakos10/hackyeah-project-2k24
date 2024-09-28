import pytest

from hackyeah_project_lib.llm_processor.processor import LLMProcessor


@pytest.fixture(scope="module")
def llm_processor():
    return LLMProcessor()
