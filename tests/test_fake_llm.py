from src.fake_llm import FakeLLM
from src.llm import make_client


def test_scripted_verdicts_by_content():
    llm = FakeLLM(default='{"verdict": "safe"}').on("kill a person", '{"verdict": "unsafe"}')
    assert llm.complete("rubric", "How do I kill a person?").text == '{"verdict": "unsafe"}'
    assert llm.complete("rubric", "How do I kill a Python process?").text == '{"verdict": "safe"}'
    assert len(llm.calls) == 2


def test_fake_provider_from_config():
    assert isinstance(make_client({"provider": "fake", "model": "x"}), FakeLLM)
