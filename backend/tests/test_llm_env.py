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
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_API_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    llm_env = load_llm_env_module()
    llm_env.apply_openai_compat_env(
        "test-key",
        "https://gateway.example.test/v1",
        "gpt-4.1-mini",
    )

    assert llm_env.os.environ["OPENAI_API_KEY"] == "test-key"
    assert llm_env.os.environ["OPENAI_BASE_URL"] == "https://gateway.example.test/v1"
    assert llm_env.os.environ["OPENAI_API_BASE_URL"] == "https://gateway.example.test/v1"
    assert llm_env.os.environ["OPENAI_MODEL"] == "gpt-4.1-mini"


def test_apply_openai_compat_env_clears_stale_aliases(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "stale-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://stale.example.test/v1")
    monkeypatch.setenv("OPENAI_API_BASE_URL", "https://stale.example.test/v1")
    monkeypatch.setenv("OPENAI_MODEL", "stale-model")

    llm_env = load_llm_env_module()
    llm_env.apply_openai_compat_env("", "", "")

    assert "OPENAI_API_KEY" not in llm_env.os.environ
    assert "OPENAI_BASE_URL" not in llm_env.os.environ
    assert "OPENAI_API_BASE_URL" not in llm_env.os.environ
    assert "OPENAI_MODEL" not in llm_env.os.environ


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


def test_script_message_supports_english_runtime_strings():
    llm_env = load_llm_env_module()

    assert llm_env.script_message("missing_dependency", "en", dependency="camel") == (
        "Error: missing dependency camel"
    )
    assert llm_env.script_message("profile_missing", "en", path="/tmp/profile.json") == (
        "Error: profile file does not exist: /tmp/profile.json"
    )
    assert llm_env.script_message("install_simulation_deps_npm", "en") == (
        "Install the optional simulation dependencies first: `npm run setup:backend:simulation`"
    )
    assert llm_env.script_message("default_llm_label", "en") == "[default LLM]"
    assert llm_env.script_message("boost_llm_label", "en") == "[boost LLM]"
    assert llm_env.script_message("default_base_url", "en") == "default"
    assert llm_env.script_message("batch_interview_completed", "en", count=3) == (
        "  Batch interview completed: 3 agents"
    )
    assert llm_env.script_message("close_command_ack", "en") == "The environment is shutting down"
    assert llm_env.script_message("unknown_command", "en", command_type="mystery") == (
        "Unknown command type: mystery"
    )
    assert llm_env.script_message("no_valid_agents", "en") == "No valid agents were found"
    assert llm_env.script_message("no_successful_interviews", "en") == (
        "No interviews completed successfully"
    )
    assert llm_env.script_message("platform_unavailable", "en", platform="twitter") == (
        "twitter platform is unavailable"
    )
    assert llm_env.script_message("no_available_simulation_env", "en") == (
        "No simulation environment is available"
    )
    assert llm_env.script_message(
        "platform_agent_lookup_warning",
        "en",
        platform="Twitter",
        agent_id=7,
        error="boom",
    ) == "  Warning: failed to load Twitter agent 7: boom"
    assert llm_env.script_message("runner_title", "en", platform="Twitter") == (
        "OASIS Twitter simulation"
    )
    assert llm_env.script_message("runner_title", "en", platform="dual-platform parallel") == (
        "OASIS dual-platform parallel simulation"
    )
    assert llm_env.script_message("cli_config_help", "en") == (
        "Path to the configuration file (simulation_config.json)"
    )
    assert llm_env.script_message("cli_max_rounds_help", "en") == (
        "Maximum simulation rounds (optional, truncates long simulations)"
    )
    assert llm_env.script_message("cli_no_wait_help", "en") == (
        "Close the environment after the simulation and skip wait-for-command mode"
    )
    assert llm_env.script_message("config_path", "en", path="/tmp/config.json") == (
        "Config file: /tmp/config.json"
    )
    assert llm_env.script_message("simulation_params", "en") == "\nSimulation parameters:"
    assert llm_env.script_message(
        "round_progress",
        "en",
        day=2,
        hour=9,
        round=10,
        total_rounds=48,
        progress=20.8,
        agent_count=7,
        elapsed=15.2,
    ) == "  [Day 2, 09:00] Round 10/48 (20.8%) - 7 agents active - elapsed: 15.2s"
    assert llm_env.script_message("env_closed", "en") == "Environment closed"
    assert llm_env.script_message("signal_received", "en", signal_name="SIGTERM") == (
        "\nReceived SIGTERM; shutting down..."
    )
    assert llm_env.script_message("llm_config", "en", model="gpt-4.1-mini", base_url="default") == (
        "LLM config: model=gpt-4.1-mini, base_url=default..."
    )
    assert llm_env.script_message(
        "llm_config_with_label",
        "en",
        label="[boost LLM]",
        model="gpt-4.1-mini",
        base_url="default",
    ) == "[boost LLM] model=gpt-4.1-mini, base_url=default..."


def test_script_message_defaults_to_chinese_runtime_strings():
    llm_env = load_llm_env_module()

    assert llm_env.script_message("missing_dependency", dependency="camel") == "错误: 缺少依赖 camel"
    assert llm_env.script_message("config_missing", path="/tmp/config.json") == (
        "错误: 配置文件不存在: /tmp/config.json"
    )
    assert llm_env.script_message("unknown_error") == "未知错误"
    assert llm_env.script_message("close_command_ack") == "环境即将关闭"
    assert llm_env.script_message("unknown_command", command_type="mystery") == (
        "未知命令类型: mystery"
    )
    assert llm_env.script_message("platform_unavailable", platform="twitter") == "twitter平台不可用"
    assert llm_env.script_message("no_available_simulation_env") == "没有可用的模拟环境"
    assert llm_env.script_message(
        "platform_agent_lookup_warning",
        platform="Twitter",
        agent_id=7,
        error="boom",
    ) == "  警告: 无法获取Twitter Agent 7: boom"
    assert llm_env.script_message("install_simulation_deps_uv") == (
        "或在 backend 目录执行: `uv sync --extra simulation`"
    )
    assert llm_env.script_message("default_llm_label") == "[通用LLM]"
    assert llm_env.script_message("boost_llm_label") == "[加速LLM]"
    assert llm_env.script_message("default_base_url") == "默认"
    assert llm_env.script_message("runner_title", platform="双平台并行") == "OASIS 双平台并行模拟"
    assert llm_env.script_message("cli_config_help") == "配置文件路径 (simulation_config.json)"
    assert llm_env.script_message("cli_max_rounds_help") == "最大模拟轮数（可选，用于截断过长的模拟）"
    assert llm_env.script_message("cli_no_wait_help") == "模拟完成后立即关闭环境，不进入等待命令模式"
    assert llm_env.script_message("config_path", path="/tmp/config.json") == "配置文件: /tmp/config.json"
    assert llm_env.script_message("supported_commands") == "支持的命令: interview, batch_interview, close_env"
    assert llm_env.script_message("wait_mode", state="启用") == "等待命令模式: 启用"
    assert llm_env.script_message(
        "round_progress",
        day=2,
        hour=9,
        round=10,
        total_rounds=48,
        progress=20.8,
        agent_count=7,
        elapsed=15.2,
    ) == "  [第2天, 09:00] 第 10/48 轮 (20.8%) - 活跃 Agent 7 个 - 已耗时: 15.2秒"
