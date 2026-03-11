"""Helpers for resolving OpenAI-compatible LLM environment aliases."""

from __future__ import annotations

import os

SCRIPT_MESSAGES = {
    "env_loaded": {
        "zh": "已加载环境配置: {path}",
        "en": "Loaded environment configuration: {path}",
    },
    "init": {
        "zh": "初始化...",
        "en": "Initializing...",
    },
    "agent_count": {
        "zh": "  - Agent数量: {count}",
        "en": "  - Agent count: {count}",
    },
    "init_model": {
        "zh": "\n初始化LLM模型...",
        "en": "\nInitializing LLM model...",
    },
    "load_profiles": {
        "zh": "加载Agent Profile...",
        "en": "Loading agent profiles...",
    },
    "profile_missing": {
        "zh": "错误: Profile文件不存在: {path}",
        "en": "Error: profile file does not exist: {path}",
    },
    "config_missing": {
        "zh": "错误: 配置文件不存在: {path}",
        "en": "Error: config file does not exist: {path}",
    },
    "interview_completed": {
        "zh": "  Interview完成: agent_id={agent_id}",
        "en": "  Interview completed: agent_id={agent_id}",
    },
    "interview_platform_completed": {
        "zh": "  Interview完成: agent_id={agent_id}, platform={platform}",
        "en": "  Interview completed: agent_id={agent_id}, platform={platform}",
    },
    "interview_failed": {
        "zh": "  Interview失败: agent_id={agent_id}, error={error}",
        "en": "  Interview failed: agent_id={agent_id}, error={error}",
    },
    "interview_platform_failed": {
        "zh": "  Interview失败: agent_id={agent_id}, platform={platform}, error={error}",
        "en": "  Interview failed: agent_id={agent_id}, platform={platform}, error={error}",
    },
    "multi_platform_interview_completed": {
        "zh": "  Interview完成: agent_id={agent_id}, 成功平台数={success_count}/{platform_count}",
        "en": "  Interview completed: agent_id={agent_id}, successful platforms={success_count}/{platform_count}",
    },
    "multi_platform_interview_failed": {
        "zh": "  Interview失败: agent_id={agent_id}, 所有平台都失败",
        "en": "  Interview failed: agent_id={agent_id}, all platforms failed",
    },
    "batch_interview_completed": {
        "zh": "  批量Interview完成: {count} 个Agent",
        "en": "  Batch interview completed: {count} agents",
    },
    "batch_interview_failed": {
        "zh": "  批量Interview失败: {error}",
        "en": "  Batch interview failed: {error}",
    },
    "twitter_batch_interview_failed": {
        "zh": "  Twitter批量Interview失败: {error}",
        "en": "  Twitter batch interview failed: {error}",
    },
    "reddit_batch_interview_failed": {
        "zh": "  Reddit批量Interview失败: {error}",
        "en": "  Reddit batch interview failed: {error}",
    },
    "unknown_error": {
        "zh": "未知错误",
        "en": "unknown error",
    },
}


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


def script_message(key: str, locale: str = "zh", **params) -> str:
    """Return deterministic localized script/runtime strings."""
    translations = SCRIPT_MESSAGES.get(key)
    if not translations:
        raise KeyError(f"Unknown script message key: {key}")
    template = translations["en"] if locale == "en" else translations["zh"]
    return template.format(**params)
