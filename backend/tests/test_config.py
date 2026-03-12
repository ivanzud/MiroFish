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


def test_config_accepts_openai_base_url_alias(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_BASE_URL", raising=False)
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    config_module = load_config_module()

    assert config_module.Config.LLM_BASE_URL == "https://api.openai.com/v1"


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
    monkeypatch.setenv("INTERVIEW_BATCH_TIMEOUT_SECONDS", "0")
    monkeypatch.setenv("REPORT_AGENT_TEMPERATURE", "9")

    config_module = load_config_module()
    result = config_module.Config.validate_comprehensive()

    assert result.is_valid is False
    assert any("OPENAI_API_BASE_URL" in error for error in result.errors)
    assert "OASIS_DEFAULT_MAX_ROUNDS 必须是合法数字，当前值: not-a-number" in result.errors
    assert "INTERVIEW_BATCH_TIMEOUT_SECONDS 必须 >= 1，当前值: 0" in result.errors
    assert "REPORT_AGENT_TEMPERATURE 必须 <= 2，当前值: 9" in result.errors


def test_validate_comprehensive_reports_debug_warning_and_safe_summary(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("ZEP_API_KEY", "zep-key")
    monkeypatch.setenv("FLASK_DEBUG", "True")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    config_module = load_config_module()
    result = config_module.Config.validate_comprehensive()
    summary = config_module.Config.get_config_summary()

    assert any("DEBUG" in warning for warning in result.warnings)
    assert any("SECRET_KEY" in warning for warning in result.warnings)
    assert summary["llm"]["configured"] is True
    assert summary["zep"]["configured"] is True
    assert summary["cors"]["allowed_origins"] == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    assert summary["simulation"]["interview_timeouts"]["single_seconds"] == 120.0
    assert summary["security"]["secret_key_source"] == "generated"
    assert "test-key" not in str(summary)
    assert "zep-key" not in str(summary)
    assert "mirofish-secret-key" not in config_module.Config.SECRET_KEY
    assert config_module.validate_on_startup() is True


def test_config_defaults_to_debug_off_and_uses_explicit_secret_key(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "configured-secret")
    monkeypatch.delenv("FLASK_DEBUG", raising=False)

    config_module = load_config_module()

    assert config_module.Config.DEBUG is False
    assert config_module.Config.SECRET_KEY == "configured-secret"
    assert config_module.Config.SECRET_KEY_IS_GENERATED is False
    assert config_module.Config.get_config_summary()["security"]["secret_key_source"] == "env"


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


def test_config_parses_cors_csv_environment_variables(monkeypatch):
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "https://app.example.test, https://admin.example.test",
    )
    monkeypatch.setenv("CORS_ALLOW_METHODS", "GET,POST")
    monkeypatch.setenv("CORS_ALLOW_HEADERS", "Content-Type, X-Locale")

    config_module = load_config_module()

    assert config_module.Config.CORS_ALLOWED_ORIGINS == [
        "https://app.example.test",
        "https://admin.example.test",
    ]
    assert config_module.Config.CORS_ALLOW_METHODS == ["GET", "POST"]
    assert config_module.Config.CORS_ALLOW_HEADERS == ["Content-Type", "X-Locale"]
    assert config_module.Config.get_cors_resources() == {
        "origins": [
            "https://app.example.test",
            "https://admin.example.test",
        ],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "X-Locale"],
    }


def test_config_defaults_cors_to_local_dev_origins(monkeypatch):
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)

    config_module = load_config_module()

    assert config_module.Config.CORS_ALLOWED_ORIGINS == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    assert "*" not in config_module.Config.CORS_ALLOWED_ORIGINS


def test_config_summary_reports_openai_compatible_alias_sources(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL_NAME", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "codex-key")
    monkeypatch.setenv("OPENAI_API_BASE_URL", "https://codex.example.test/v1")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")
    monkeypatch.setenv("ZEP_API_KEY", "zep-key")

    config_module = load_config_module()
    summary = config_module.Config.get_config_summary()

    assert summary["llm"]["backend_mode"] == "openai_compatible"
    assert summary["llm"]["sources"] == {
        "api_key_env": "OPENAI_API_KEY",
        "base_url_env": "OPENAI_API_BASE_URL",
        "model_env": "OPENAI_MODEL",
        "base_url_conflict": None,
        "uses_project_aliases": False,
        "uses_openai_aliases": True,
    }
    assert summary["capabilities"] == {
        "direct_llm": {
            "ready": True,
        },
        "graph_build": {
            "ready": True,
            "requires_zep": True,
        },
        "graph_report_tools": {
            "ready": True,
            "requires_zep": True,
        },
        "existing_simulation_interaction": {
            "ready": True,
            "requires_existing_simulation": True,
        },
    }


def test_config_summary_reports_openai_base_url_source(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL_NAME", raising=False)
    monkeypatch.delenv("OPENAI_API_BASE_URL", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "codex-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")
    monkeypatch.setenv("ZEP_API_KEY", "zep-key")

    config_module = load_config_module()
    summary = config_module.Config.get_config_summary()

    assert summary["llm"]["backend_mode"] == "openai_compatible"
    assert summary["llm"]["sources"] == {
        "api_key_env": "OPENAI_API_KEY",
        "base_url_env": "OPENAI_BASE_URL",
        "model_env": "OPENAI_MODEL",
        "base_url_conflict": None,
        "uses_project_aliases": False,
        "uses_openai_aliases": True,
    }


def test_config_warns_when_openai_base_url_aliases_conflict(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "codex-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    monkeypatch.setenv("OPENAI_API_BASE_URL", "https://codex-gateway.example.test/v1")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")
    monkeypatch.setenv("ZEP_API_KEY", "zep-key")

    config_module = load_config_module()
    result = config_module.Config.validate_comprehensive(locale="en")
    summary = config_module.Config.get_config_summary()

    assert result.is_valid is True
    assert "OPENAI_BASE_URL / OPENAI_API_BASE_URL" in result.warnings[0]
    assert "OPENAI_BASE_URL=https://api.openai.com/v1 will take precedence" in result.warnings[0]
    assert summary["llm"]["base_url"] == "https://api.openai.com/v1"
    assert summary["llm"]["sources"]["base_url_env"] == "OPENAI_BASE_URL"
    assert summary["llm"]["sources"]["base_url_conflict"] == {
        "has_conflict": True,
        "selected_env": "OPENAI_BASE_URL",
        "selected_value": "https://api.openai.com/v1",
        "configured_envs": [
            {"name": "OPENAI_BASE_URL", "value": "https://api.openai.com/v1"},
            {"name": "OPENAI_API_BASE_URL", "value": "https://codex-gateway.example.test/v1"},
        ],
    }


def test_config_summary_exposes_non_zep_capability_boundaries(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL_NAME", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "codex-key")
    monkeypatch.setenv("OPENAI_API_BASE_URL", "https://codex.example.test/v1")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")
    monkeypatch.delenv("ZEP_API_KEY", raising=False)

    config_module = load_config_module()
    summary = config_module.Config.get_config_summary()

    assert summary["capabilities"] == {
        "direct_llm": {
            "ready": True,
        },
        "graph_build": {
            "ready": False,
            "requires_zep": True,
        },
        "graph_report_tools": {
            "ready": False,
            "requires_zep": True,
        },
        "existing_simulation_interaction": {
            "ready": True,
            "requires_existing_simulation": True,
        },
    }
