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


def test_extract_json_payload_with_prefixed_reasoning_text_and_array():
    raw = """Answer:
The best matching items are:
[
  {"name": "Alice"},
  {"name": "Bob"}
]
"""

    assert LLMClient._extract_json_payload(raw) == '[\n  {"name": "Alice"},\n  {"name": "Bob"}\n]'


def test_extract_json_payload_with_bom_and_markdown_array_fence():
    raw = "\ufeff```json\n[\n  1,\n  2,\n  3\n]\n```"

    assert LLMClient._extract_json_payload(raw) == '[\n  1,\n  2,\n  3\n]'


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


def test_chat_retries_with_trimmed_messages_on_context_length_error(monkeypatch):
    create_calls = []

    class FakeBadRequestError(Exception):
        pass

    class FakeCompletions:
        def create(self, **kwargs):
            create_calls.append(kwargs)
            if len(create_calls) == 1:
                raise FakeBadRequestError("context_length exceeded")
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="trimmed response"))]
            )

    class FakeOpenAI:
        def __init__(self, api_key, base_url):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr("app.utils.llm_client.OpenAI", FakeOpenAI)
    monkeypatch.setattr("app.utils.llm_client.BadRequestError", FakeBadRequestError)

    client = LLMClient(api_key="test-key", base_url="https://example.test/v1", model="test-model")
    messages = [{"role": "system", "content": "system"}, {"role": "user", "content": "user"}]
    messages.extend(
        {"role": "assistant" if i % 2 == 0 else "user", "content": f"message-{i}"}
        for i in range(12)
    )

    response = client.chat(messages)

    assert response == "trimmed response"
    assert len(create_calls) == 2
    assert len(create_calls[1]["messages"]) < len(messages)
    assert create_calls[1]["messages"][:2] == messages[:2]


def test_chat_uses_configured_default_max_tokens(monkeypatch):
    create_calls = []

    class FakeCompletions:
        def create(self, **kwargs):
            create_calls.append(kwargs)
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))]
            )

    class FakeOpenAI:
        def __init__(self, api_key, base_url):
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr("app.utils.llm_client.OpenAI", FakeOpenAI)
    monkeypatch.setattr("app.utils.llm_client.Config.LLM_MAX_TOKENS", 1234)

    client = LLMClient(api_key="test-key", base_url="https://example.test/v1", model="test-model")
    client.chat([{"role": "user", "content": "hello"}])

    assert create_calls[0]["max_tokens"] == 1234
