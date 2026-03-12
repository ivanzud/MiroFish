from flask import Flask

from app.config import Config
from app.utils.error_handler import error_response, handle_api_exception


class FakeLogger:
    def __init__(self):
        self.errors = []
        self.debugs = []

    def error(self, message):
        self.errors.append(message)

    def debug(self, message):
        self.debugs.append(message)


def test_error_response_hides_traceback_when_debug_disabled(monkeypatch):
    monkeypatch.setattr(Config, "DEBUG", False)
    app = Flask(__name__)

    with app.app_context():
        try:
            raise RuntimeError("boom")
        except RuntimeError as error:
            response, status_code = error_response("boom", original_error=error)

    assert status_code == 500
    assert response.get_json() == {"success": False, "error": "boom"}


def test_error_response_includes_traceback_when_debug_enabled(monkeypatch):
    monkeypatch.setattr(Config, "DEBUG", True)
    app = Flask(__name__)

    with app.app_context():
        try:
            raise RuntimeError("boom")
        except RuntimeError as error:
            response, status_code = error_response("boom", original_error=error)

    payload = response.get_json()

    assert status_code == 500
    assert payload["success"] is False
    assert payload["error"] == "boom"
    assert "traceback" in payload
    assert "RuntimeError: boom" in payload["traceback"]


def test_handle_api_exception_logs_and_returns_standard_payload(monkeypatch):
    monkeypatch.setattr(Config, "DEBUG", False)
    app = Flask(__name__)
    logger = FakeLogger()

    with app.app_context():
        try:
            raise ValueError("bad input")
        except ValueError as error:
            response, status_code = handle_api_exception(logger, error, "测试上下文")

    assert status_code == 500
    assert response.get_json() == {"success": False, "error": "bad input"}
    assert logger.errors == ["测试上下文: bad input"]
    assert logger.debugs
