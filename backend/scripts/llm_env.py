"""Helpers for resolving OpenAI-compatible LLM environment aliases."""

from __future__ import annotations

import os


def _first_env(*names: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value not in (None, ""):
            return value
    return ""


def resolve_standard_model_name() -> str:
    """Resolve the standard model-name aliases used by OpenAI-compatible setups."""
    return _first_env("LLM_MODEL_NAME", "OPENAI_MODEL")


def resolve_standard_llm_env() -> tuple[str, str, str]:
    """Resolve the standard LLM configuration aliases used by standalone runners."""
    return (
        _first_env("LLM_API_KEY", "OPENAI_API_KEY"),
        _first_env("LLM_BASE_URL", "OPENAI_BASE_URL", "OPENAI_API_BASE_URL"),
        resolve_standard_model_name(),
    )


def _set_or_clear_env(name: str, value: str) -> None:
    if value:
        os.environ[name] = value
        return
    os.environ.pop(name, None)


def apply_openai_compat_env(api_key: str, base_url: str, model_name: str = "") -> None:
    """Populate a deterministic OpenAI-compatible environment snapshot."""
    _set_or_clear_env("OPENAI_API_KEY", api_key)
    _set_or_clear_env("OPENAI_BASE_URL", base_url)
    _set_or_clear_env("OPENAI_API_BASE_URL", base_url)
    _set_or_clear_env("OPENAI_MODEL", model_name)


def missing_api_key_message(locale: str = "zh") -> str:
    """Return a consistent missing-key message for OpenAI-compatible env aliases."""
    if locale == "en":
        return (
            "Missing API key configuration. Set LLM_API_KEY or OPENAI_API_KEY "
            "in the project root .env file."
        )
    return "缺少 API Key 配置，请在项目根目录 .env 文件中设置 LLM_API_KEY 或 OPENAI_API_KEY"
