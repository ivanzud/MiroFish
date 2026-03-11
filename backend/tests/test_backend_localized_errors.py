from flask import Flask

from app.models.task import TaskManager
from app.utils.file_parser import FileParser
from app.utils.llm_client import LLMClient


def test_llm_client_missing_key_uses_english_request_locale(monkeypatch):
    monkeypatch.setattr("app.utils.llm_client.Config.LLM_API_KEY", "")

    app = Flask(__name__)
    with app.test_request_context(headers={"X-Locale": "en"}):
        try:
            LLMClient()
        except ValueError as exc:
            assert str(exc) == "LLM_API_KEY / OPENAI_API_KEY is not configured"
        else:
            raise AssertionError("expected ValueError when no API key is configured")


def test_llm_client_invalid_json_uses_english_request_locale():
    client = LLMClient.__new__(LLMClient)
    client.chat = lambda *args, **kwargs: "not json"

    app = Flask(__name__)
    with app.test_request_context(headers={"X-Locale": "en"}):
        try:
            client.chat_json([{"role": "user", "content": "hello"}])
        except ValueError as exc:
            assert str(exc) == "The LLM returned invalid JSON: not json"
        else:
            raise AssertionError("expected ValueError for invalid JSON")


def test_file_parser_errors_use_english_request_locale(tmp_path):
    app = Flask(__name__)
    with app.test_request_context(headers={"X-Locale": "en"}):
        missing_path = tmp_path / "missing.txt"
        try:
            FileParser.extract_text(str(missing_path))
        except FileNotFoundError as exc:
            assert str(exc) == f"File not found: {missing_path}"
        else:
            raise AssertionError("expected FileNotFoundError for a missing file")

        unsupported_path = tmp_path / "sample.docx"
        unsupported_path.write_text("hello", encoding="utf-8")
        try:
            FileParser.extract_text(str(unsupported_path))
        except ValueError as exc:
            assert str(exc) == "Unsupported file format: .docx"
        else:
            raise AssertionError("expected ValueError for an unsupported file")


def test_task_manager_complete_and_fail_support_explicit_locale():
    manager = TaskManager()
    manager._tasks.clear()
    task_id = manager.create_task("demo")

    manager.complete_task(task_id, {"ok": True}, locale="en")
    task = manager.get_task(task_id)
    assert task is not None
    assert task.message == "Task completed"

    manager.fail_task(task_id, "boom", locale="en")
    task = manager.get_task(task_id)
    assert task is not None
    assert task.message == "Task failed"
    assert task.error == "boom"
