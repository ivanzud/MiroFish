import importlib.util
import sys
from pathlib import Path


def load_llm_env_module():
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "llm_env.py"
    module_name = "test_llm_env_module"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resolve_standard_llm_env_accepts_openai_api_base_url(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "codex-key")
    monkeypatch.setenv("OPENAI_API_BASE_URL", "https://codex.example.test/v1")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4.1-mini")

    llm_env = load_llm_env_module()

    assert llm_env.resolve_standard_llm_env() == (
        "codex-key",
        "https://codex.example.test/v1",
        "gpt-4.1-mini",
    )


def test_resolve_standard_model_name_accepts_openai_model(monkeypatch):
    monkeypatch.delenv("LLM_MODEL_NAME", raising=False)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")

    llm_env = load_llm_env_module()

    assert llm_env.resolve_standard_model_name() == "gpt-5-mini"


def test_apply_openai_compat_env_sets_expected_aliases(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_BASE_URL", raising=False)

    llm_env = load_llm_env_module()
    llm_env.apply_openai_compat_env("test-key", "https://gateway.example.test/v1")

    assert llm_env.os.environ["OPENAI_API_KEY"] == "test-key"
    assert llm_env.os.environ["OPENAI_API_BASE_URL"] == "https://gateway.example.test/v1"


def test_missing_api_key_message_mentions_openai_alias(monkeypatch):
    llm_env = load_llm_env_module()

    assert llm_env.missing_api_key_message() == (
        "缺少 API Key 配置，请在项目根目录 .env 文件中设置 LLM_API_KEY 或 OPENAI_API_KEY"
    )


def test_missing_api_key_message_supports_english(monkeypatch):
    llm_env = load_llm_env_module()

    assert llm_env.missing_api_key_message("en") == (
        "Missing API key configuration. Set LLM_API_KEY or OPENAI_API_KEY "
        "in the project root .env file."
    )
