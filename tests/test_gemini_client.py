from types import SimpleNamespace

import pytest

from docugen.api import gemini_client
from docugen.api.gemini_client import GeminiClient


class _FakeModels:
    def __init__(self) -> None:
        self.calls = []

    def generate_content(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(text="## Generated")


class _FakeClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.models = _FakeModels()


class _FakeGenAI:
    Client = _FakeClient


def test_generate_markdown_calls_sdk(monkeypatch) -> None:
    monkeypatch.setattr(gemini_client, "genai", _FakeGenAI)

    client = GeminiClient(api_key="secret", model="gemini-test")
    result = client.generate_markdown({"summary": {"file_count": 1}}, user_prompt="Focus on usage")

    assert result == "## Generated"
    call = client.client.models.calls[0]
    assert call["model"] == "gemini-test"
    assert "Project metadata (JSON):" in call["contents"]
    assert "Focus on usage" in call["contents"]
    assert call["config"]["system_instruction"]


def test_generate_markdown_raises_when_response_has_no_text(monkeypatch) -> None:
    class EmptyModels:
        def generate_content(self, **kwargs):
            return SimpleNamespace(text="", candidates=[])

    class EmptyClient:
        def __init__(self, api_key: str) -> None:
            self.models = EmptyModels()

    class EmptyGenAI:
        Client = EmptyClient

    monkeypatch.setattr(gemini_client, "genai", EmptyGenAI)

    client = GeminiClient(api_key="secret")
    with pytest.raises(RuntimeError, match="did not include text"):
        client.generate_markdown({"summary": {}})


def test_requires_api_key() -> None:
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        GeminiClient(api_key="")
