"""Helpers for resolving OpenAI-compatible LLM environment aliases."""

from __future__ import annotations

import os

SCRIPT_MESSAGES = {
    "missing_dependency": {
        "zh": "错误: 缺少依赖 {dependency}",
        "en": "Error: missing dependency {dependency}",
    },
    "install_simulation_deps_npm": {
        "zh": "请先安装可选仿真依赖: `npm run setup:backend:simulation`",
        "en": "Install the optional simulation dependencies first: `npm run setup:backend:simulation`",
    },
    "install_simulation_deps_uv": {
        "zh": "或在 backend 目录执行: `uv sync --extra simulation`",
        "en": "Or run `uv sync --extra simulation` inside the backend directory",
    },
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
    "agent_lookup_warning": {
        "zh": "  警告: 无法获取Agent {agent_id}: {error}",
        "en": "  Warning: failed to load agent {agent_id}: {error}",
    },
    "no_valid_agents": {
        "zh": "没有有效的Agent",
        "en": "No valid agents were found",
    },
    "no_successful_interviews": {
        "zh": "没有成功的采访",
        "en": "No interviews completed successfully",
    },
    "interview_result_read_failed": {
        "zh": "  读取Interview结果失败: {error}",
        "en": "  Failed to read interview result: {error}",
    },
    "ipc_command_received": {
        "zh": "\n收到IPC命令: {command_type}, id={command_id}",
        "en": "\nReceived IPC command: {command_type}, id={command_id}",
    },
    "close_command_received": {
        "zh": "收到关闭环境命令",
        "en": "Received close-environment command",
    },
    "llm_config": {
        "zh": "LLM配置: model={model}, base_url={base_url}...",
        "en": "LLM config: model={model}, base_url={base_url}...",
    },
    "llm_config_with_label": {
        "zh": "{label} model={model}, base_url={base_url}...",
        "en": "{label} model={model}, base_url={base_url}...",
    },
    "default_base_url": {
        "zh": "默认",
        "en": "default",
    },
    "default_llm_label": {
        "zh": "[通用LLM]",
        "en": "[default LLM]",
    },
    "boost_llm_label": {
        "zh": "[加速LLM]",
        "en": "[boost LLM]",
    },
    "runner_title": {
        "zh": "OASIS {platform}模拟",
        "en": "OASIS {platform} simulation",
    },
    "config_path": {
        "zh": "配置文件: {path}",
        "en": "Config file: {path}",
    },
    "simulation_id": {
        "zh": "模拟ID: {simulation_id}",
        "en": "Simulation ID: {simulation_id}",
    },
    "wait_mode": {
        "zh": "等待命令模式: {state}",
        "en": "Wait-for-command mode: {state}",
    },
    "enabled": {
        "zh": "启用",
        "en": "enabled",
    },
    "disabled": {
        "zh": "禁用",
        "en": "disabled",
    },
    "rounds_truncated": {
        "zh": "\n轮数已截断: {original} -> {current} (max_rounds={max_rounds})",
        "en": "\nRounds truncated: {original} -> {current} (max_rounds={max_rounds})",
    },
    "simulation_params": {
        "zh": "\n模拟参数:",
        "en": "\nSimulation parameters:",
    },
    "total_hours": {
        "zh": "  - 总模拟时长: {hours}小时",
        "en": "  - Total duration: {hours} hours",
    },
    "minutes_per_round": {
        "zh": "  - 每轮时间: {minutes}分钟",
        "en": "  - Minutes per round: {minutes}",
    },
    "total_rounds": {
        "zh": "  - 总轮数: {rounds}",
        "en": "  - Total rounds: {rounds}",
    },
    "max_rounds_limit": {
        "zh": "  - 最大轮数限制: {max_rounds}",
        "en": "  - Max-round limit: {max_rounds}",
    },
    "old_db_removed": {
        "zh": "已删除旧数据库: {path}",
        "en": "Removed previous database: {path}",
    },
    "creating_oasis_env": {
        "zh": "创建OASIS环境...",
        "en": "Creating OASIS environment...",
    },
    "env_initialized": {
        "zh": "环境初始化完成\n",
        "en": "Environment initialization complete\n",
    },
    "initial_events_start": {
        "zh": "执行初始事件 ({count}条初始帖子)...",
        "en": "Applying initial events ({count} initial posts)...",
    },
    "initial_post_warning": {
        "zh": "  警告: 无法为Agent {agent_id}创建初始帖子: {error}",
        "en": "  Warning: failed to create an initial post for agent {agent_id}: {error}",
    },
    "initial_posts_published": {
        "zh": "  已发布 {count} 条初始帖子",
        "en": "  Published {count} initial posts",
    },
    "simulation_loop_start": {
        "zh": "\n开始模拟循环...",
        "en": "\nStarting simulation loop...",
    },
    "simulation_loop_complete": {
        "zh": "\n模拟循环完成!",
        "en": "\nSimulation loop complete!",
    },
    "total_elapsed": {
        "zh": "  - 总耗时: {seconds:.1f}秒",
        "en": "  - Total elapsed: {seconds:.1f}s",
    },
    "database_path": {
        "zh": "  - 数据库: {path}",
        "en": "  - Database: {path}",
    },
    "wait_mode_banner": {
        "zh": "进入等待命令模式 - 环境保持运行",
        "en": "Entering wait-for-command mode: environment stays online",
    },
    "supported_commands": {
        "zh": "支持的命令: interview, batch_interview, close_env",
        "en": "Supported commands: interview, batch_interview, close_env",
    },
    "interrupt_received": {
        "zh": "\n收到中断信号",
        "en": "\nReceived interrupt signal",
    },
    "task_cancelled": {
        "zh": "\n任务被取消",
        "en": "\nTask cancelled",
    },
    "command_processing_failed": {
        "zh": "\n命令处理出错: {error}",
        "en": "\nCommand processing failed: {error}",
    },
    "closing_env": {
        "zh": "\n关闭环境...",
        "en": "\nClosing environment...",
    },
    "env_closed": {
        "zh": "环境已关闭",
        "en": "Environment closed",
    },
    "signal_received": {
        "zh": "\n收到 {signal_name} 信号，正在退出...",
        "en": "\nReceived {signal_name}; shutting down...",
    },
    "force_exit": {
        "zh": "强制退出...",
        "en": "Force exiting...",
    },
    "program_interrupted": {
        "zh": "\n程序被中断",
        "en": "\nProgram interrupted",
    },
    "process_exited": {
        "zh": "模拟进程已退出",
        "en": "Simulation process exited",
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
