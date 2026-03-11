import importlib.util
import sys
from pathlib import Path


def load_config_module():
    config_path = Path(__file__).resolve().parents[1] / "app" / "config.py"
    module_name = "test_config_module"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, config_path)
    assert spec is not None
    assert spec.loader is not None

    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    return config_module


def test_config_accepts_openai_api_base_url_alias(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.setenv("OPENAI_API_BASE_URL", "https://codex.example.test/v1")

    config_module = load_config_module()

    assert config_module.Config.LLM_BASE_URL == "https://codex.example.test/v1"


def test_validate_returns_structured_errors_for_missing_keys(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ZEP_API_KEY", raising=False)

    config_module = load_config_module()

    errors = config_module.Config.validate()

    assert isinstance(errors, list)
    assert "LLM_API_KEY / OPENAI_API_KEY 未配置" in errors
    assert "ZEP_API_KEY 未配置" in errors


def test_validate_comprehensive_detects_invalid_url_and_numeric_values(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("ZEP_API_KEY", "zep-key")
    monkeypatch.setenv("OPENAI_API_BASE_URL", "ftp://example.test")
    monkeypatch.setenv("OASIS_DEFAULT_MAX_ROUNDS", "not-a-number")
    monkeypatch.setenv("REPORT_AGENT_TEMPERATURE", "9")

    config_module = load_config_module()
    result = config_module.Config.validate_comprehensive()

    assert result.is_valid is False
    assert any("OPENAI_API_BASE_URL" in error for error in result.errors)
    assert "OASIS_DEFAULT_MAX_ROUNDS 必须是合法数字，当前值: not-a-number" in result.errors
    assert "REPORT_AGENT_TEMPERATURE 必须 <= 2，当前值: 9" in result.errors


def test_validate_comprehensive_reports_debug_warning_and_safe_summary(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("ZEP_API_KEY", "zep-key")
    monkeypatch.setenv("FLASK_DEBUG", "True")

    config_module = load_config_module()
    result = config_module.Config.validate_comprehensive()
    summary = config_module.Config.get_config_summary()

    assert any("DEBUG" in warning for warning in result.warnings)
    assert summary["llm"]["configured"] is True
    assert summary["zep"]["configured"] is True
    assert "api_key" not in str(summary).lower()
    assert config_module.validate_on_startup() is True


def test_validate_comprehensive_can_render_english_messages(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ZEP_API_KEY", raising=False)
    monkeypatch.setenv("OASIS_DEFAULT_MAX_ROUNDS", "bad-value")

    config_module = load_config_module()
    result = config_module.Config.validate_comprehensive(locale="en")

    assert "LLM_API_KEY / OPENAI_API_KEY is not configured" in result.errors
    assert "ZEP_API_KEY is not configured" in result.errors
    assert "OASIS_DEFAULT_MAX_ROUNDS must be a valid number, current value: bad-value" in result.errors
