import importlib.util
import sys
from pathlib import Path

import pytest


def load_run_module():
    run_path = Path(__file__).resolve().parents[1] / "run.py"
    module_name = "test_run_module"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, run_path)
    assert spec is not None
    assert spec.loader is not None

    run_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_module)
    return run_module


def test_main_prints_english_startup_validation_output(monkeypatch, capsys):
    monkeypatch.setenv("MIROFISH_LOCALE", "en")
    run_module = load_run_module()
    monkeypatch.setattr(run_module.Config, "validate", lambda locale="zh": ["LLM_API_KEY is not configured"])

    with pytest.raises(SystemExit) as exc:
        run_module.main()

    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert captured.out == (
        "Configuration errors:\n"
        "  - LLM_API_KEY is not configured\n"
        "\n"
        "Check the configuration in the .env file\n"
    )


def test_main_defaults_to_chinese_startup_validation_output(monkeypatch, capsys):
    monkeypatch.delenv("MIROFISH_LOCALE", raising=False)
    run_module = load_run_module()
    monkeypatch.setattr(run_module.Config, "validate", lambda locale="zh": ["LLM_API_KEY 未配置"])

    with pytest.raises(SystemExit) as exc:
        run_module.main()

    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert captured.out == "配置错误:\n  - LLM_API_KEY 未配置\n\n请检查 .env 文件中的配置\n"
