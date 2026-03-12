import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace


def load_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "print_config_status.py"
    module_name = "test_print_config_status_module"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validation_payload(*, is_valid: bool, errors: list[str] | None = None) -> SimpleNamespace:
    errors = errors or []
    return SimpleNamespace(
        is_valid=is_valid,
        to_dict=lambda: {
            "is_valid": is_valid,
            "errors": errors,
            "warnings": [],
            "info": [],
            "error_count": len(errors),
            "warning_count": 0,
        },
    )


def test_build_payload_matches_backend_config_status_shape(monkeypatch):
    module = load_module()
    fake_validation = _validation_payload(is_valid=True)
    seen = {}

    def validate(locale="zh"):
        seen["locale"] = locale
        return fake_validation

    monkeypatch.setattr(
        module,
        "Config",
        SimpleNamespace(
            validate_comprehensive=validate,
            get_config_summary=lambda: {
                "llm": {
                    "backend_mode": "openai_compatible",
                    "sources": {"api_key_env": "OPENAI_API_KEY"},
                }
            },
        ),
    )

    payload = module.build_payload("en")

    assert seen["locale"] == "en"
    assert payload == {
        "success": True,
        "data": {
            "validation": fake_validation.to_dict(),
            "summary": {
                "llm": {
                    "backend_mode": "openai_compatible",
                    "sources": {"api_key_env": "OPENAI_API_KEY"},
                }
            },
        },
    }


def test_load_config_class_avoids_importing_flask_app_package():
    original_app = sys.modules.pop("app", None)
    try:
        module = load_module()

        assert module.Config.__module__ == "_mirofish_script_app.config"
        assert "app" not in sys.modules
    finally:
        if original_app is not None:
            sys.modules["app"] = original_app


def test_main_returns_nonzero_when_config_is_invalid(monkeypatch, capsys):
    module = load_module()
    fake_validation = _validation_payload(
        is_valid=False,
        errors=["LLM_API_KEY / OPENAI_API_KEY is not configured"],
    )

    monkeypatch.setattr(
        module,
        "Config",
        SimpleNamespace(
            validate_comprehensive=lambda locale="zh": fake_validation,
            get_config_summary=lambda: {"llm": {"configured": False}},
        ),
    )

    exit_code = module.main(["--locale", "en", "--compact"])
    captured = capsys.readouterr()

    assert exit_code == 1
    payload = json.loads(captured.out)
    assert payload["success"] is False
    assert payload["data"]["validation"]["errors"] == [
        "LLM_API_KEY / OPENAI_API_KEY is not configured"
    ]


def test_print_config_status_script_accepts_openai_aliases_end_to_end():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "print_config_status.py"
    env = {
        **os.environ,
        "LLM_API_KEY": "",
        "LLM_BASE_URL": "",
        "LLM_MODEL_NAME": "",
        "OPENAI_API_KEY": "codex-test-key",
        "OPENAI_BASE_URL": "",
        "OPENAI_API_BASE_URL": "https://codex.example.test/v1",
        "OPENAI_MODEL": "gpt-4.1-mini",
        "ZEP_API_KEY": "zep-test-key",
    }

    result = subprocess.run(
        [sys.executable, str(script_path), "--locale", "en", "--compact"],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert payload["data"]["summary"]["llm"] == {
        "backend_mode": "openai_compatible",
        "base_url": "https://codex.example.test/v1",
        "model": "gpt-4.1-mini",
        "max_tokens": 4096,
        "configured": True,
        "sources": {
            "api_key_env": "OPENAI_API_KEY",
            "base_url_env": "OPENAI_API_BASE_URL",
            "model_env": "OPENAI_MODEL",
            "base_url_conflict": None,
            "uses_project_aliases": False,
            "uses_openai_aliases": True,
        },
    }
    assert payload["data"]["summary"]["capabilities"] == {
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
