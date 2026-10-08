import pytest

from src.config import load_config
from src.llm import OllamaClient, make_client


def test_config_selects_local_judge_model():
    client = make_client(load_config()["judge"])
    assert isinstance(client, OllamaClient)
    assert client.model == "qwen2.5:3b-instruct"


def test_unknown_provider_rejected():
    with pytest.raises(ValueError):
        make_client({"provider": "nope", "model": "x"})


@pytest.mark.live
def test_live_judge_model_answers():
    client = make_client(load_config()["judge"])
    reply = client.complete("Answer with one word.", "Is the sky blue? yes or no")
    assert reply.text.strip().lower().startswith("yes")
