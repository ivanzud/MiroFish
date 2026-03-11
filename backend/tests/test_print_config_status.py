import importlib.util
import json
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
