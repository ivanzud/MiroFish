from types import SimpleNamespace

from app.utils.llm_client import LLMClient


def test_extract_json_payload_from_markdown_fence():
    raw = """```json
{"a": 1, "b": [2, 3]}
```"""

    assert LLMClient._extract_json_payload(raw) == '{"a": 1, "b": [2, 3]}'


def test_extract_json_payload_with_prefixed_reasoning_text():
    raw = """分析如下：
<think>先思考</think>
最终答案：
{"entity_types": [], "edge_types": []}
"""

    assert LLMClient._extract_json_payload(raw) == '{"entity_types": [], "edge_types": []}'


def test_chat_returns_empty_string_when_content_is_none(monkeypatch):
    create_calls = []

    class FakeCompletions:
        def create(self, **kwargs):
            create_calls.append(kwargs)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=None))]
            )

    class FakeOpenAI:
        def __init__(self, api_key, base_url):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr("app.utils.llm_client.OpenAI", FakeOpenAI)

    client = LLMClient(api_key="test-key", base_url="https://example.test/v1", model="test-model")
    response = client.chat([{"role": "user", "content": "hello"}], response_format={"type": "json_object"})

    assert response == ""
    assert create_calls[0]["response_format"] == {"type": "json_object"}


def test_chat_json_omits_response_format_for_compatibility(monkeypatch):
    create_calls = []

    class FakeCompletions:
        def create(self, **kwargs):
            create_calls.append(kwargs)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content='{"ok": true}'))]
            )

    class FakeOpenAI:
        def __init__(self, api_key, base_url):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr("app.utils.llm_client.OpenAI", FakeOpenAI)

    client = LLMClient(api_key="test-key", base_url="https://example.test/v1", model="test-model")
    response = client.chat_json([{"role": "user", "content": "hello"}])

    assert response == {"ok": True}
    assert "response_format" not in create_calls[0]
