import importlib.util
from pathlib import Path


def test_config_accepts_openai_api_base_url_alias(monkeypatch):
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.setenv("OPENAI_API_BASE_URL", "https://codex.example.test/v1")

    config_path = Path(__file__).resolve().parents[1] / "app" / "config.py"
    spec = importlib.util.spec_from_file_location("test_config_module", config_path)
    assert spec is not None
    assert spec.loader is not None

    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)

    assert config_module.Config.LLM_BASE_URL == "https://codex.example.test/v1"
