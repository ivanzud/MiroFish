"""Helpers for resolving OpenAI-compatible LLM environment aliases."""

from __future__ import annotations

import os


def _first_env(*names: str) -> str:
    for name in names:
        value = os.environ.get(name)
        if value not in (None, ""):
            return value
    return ""


def resolve_standard_llm_env() -> tuple[str, str, str]:
    """Resolve the standard LLM configuration aliases used by standalone runners."""
    return (
        _first_env("LLM_API_KEY", "OPENAI_API_KEY"),
        _first_env("LLM_BASE_URL", "OPENAI_BASE_URL", "OPENAI_API_BASE_URL"),
        _first_env("LLM_MODEL_NAME", "OPENAI_MODEL"),
    )


def apply_openai_compat_env(api_key: str, base_url: str) -> None:
    """Populate camel-ai's OpenAI-compatible environment variables."""
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
    if base_url:
        os.environ["OPENAI_API_BASE_URL"] = base_url
