"""Minimal backend i18n helpers for deterministic API messages."""

from __future__ import annotations

from flask import has_request_context, request


DEFAULT_LOCALE = "zh"

TRANSLATIONS = {
    "api.backend_config_incomplete": {
        "zh": "后端配置不完整: {details}",
        "en": "Backend configuration is incomplete: {details}",
    },
    "config.key_missing": {
        "zh": "{name} 未配置",
        "en": "{name} is not configured",
    },
    "config.url_invalid_scheme": {
        "zh": "{name} 必须使用 http/https: {value}",
        "en": "{name} must use http/https: {value}",
    },
    "config.url_missing_host": {
        "zh": "{name} 缺少主机名: {value}",
        "en": "{name} is missing a hostname: {value}",
    },
    "config.numeric_invalid": {
        "zh": "{name} 必须是合法数字，当前值: {value}",
        "en": "{name} must be a valid number, current value: {value}",
    },
    "config.numeric_min": {
        "zh": "{name} 必须 >= {minimum}，当前值: {value}",
        "en": "{name} must be >= {minimum}, current value: {value}",
    },
    "config.numeric_max": {
        "zh": "{name} 必须 <= {maximum}，当前值: {value}",
        "en": "{name} must be <= {maximum}, current value: {value}",
    },
    "config.debug_warning": {
        "zh": "FLASK_DEBUG=True; 不建议在生产环境启用 DEBUG",
        "en": "FLASK_DEBUG=True; DEBUG should not be enabled in production",
    },
    "config.secret_key_warning": {
        "zh": "SECRET_KEY 使用默认值；生产环境应覆盖",
        "en": "SECRET_KEY is using the default value; override it in production",
    },
    "config.upload_folder_info": {
        "zh": "UPLOAD_FOLDER 尚不存在，将在运行时按需创建: {path}",
        "en": "UPLOAD_FOLDER does not exist yet and will be created on demand at runtime: {path}",
    },
    "config.model_info": {
        "zh": "LLM_MODEL_NAME={model}",
        "en": "LLM_MODEL_NAME={model}",
    },
    "graph.project_not_found": {
        "zh": "项目不存在: {project_id}",
        "en": "Project not found: {project_id}",
    },
    "graph.project_delete_failed": {
        "zh": "项目不存在或删除失败: {project_id}",
        "en": "Project not found or could not be deleted: {project_id}",
    },
    "graph.project_deleted": {
        "zh": "项目已删除: {project_id}",
        "en": "Project deleted: {project_id}",
    },
    "graph.project_reset": {
        "zh": "项目已重置: {project_id}",
        "en": "Project reset: {project_id}",
    },
    "graph.simulation_requirement_required": {
        "zh": "请提供模拟需求描述 (simulation_requirement)",
        "en": "Please provide simulation_requirement",
    },
    "graph.upload_files_required": {
        "zh": "请至少上传一个文档文件",
        "en": "Please upload at least one document file",
    },
    "graph.no_processed_documents": {
        "zh": "没有成功处理任何文档，请检查文件格式",
        "en": "No documents were processed successfully. Check the file format.",
    },
    "graph.config_error": {
        "zh": "配置错误: {details}",
        "en": "Configuration error: {details}",
    },
    "graph.project_id_required": {
        "zh": "请提供 project_id",
        "en": "Please provide project_id",
    },
    "graph.ontology_required": {
        "zh": "项目尚未生成本体，请先调用 /ontology/generate",
        "en": "The project ontology has not been generated yet. Call /ontology/generate first.",
    },
    "graph.build_in_progress": {
        "zh": "图谱正在构建中，请勿重复提交。如需强制重建，请添加 force: true",
        "en": "The graph is already building. Do not submit again unless you set force: true.",
    },
    "graph.extracted_text_missing": {
        "zh": "未找到提取的文本内容",
        "en": "No extracted text content was found",
    },
    "graph.ontology_missing": {
        "zh": "未找到本体定义",
        "en": "No ontology definition was found",
    },
    "graph.task_not_found": {
        "zh": "任务不存在: {task_id}",
        "en": "Task not found: {task_id}",
    },
    "graph.zep_key_missing": {
        "zh": "ZEP_API_KEY未配置",
        "en": "ZEP_API_KEY is not configured",
    },
    "graph.graph_deleted": {
        "zh": "图谱已删除: {graph_id}",
        "en": "Graph deleted: {graph_id}",
    },
    "simulation.timeout_invalid_number": {
        "zh": "timeout 必须是大于 0 的数字",
        "en": "timeout must be a number greater than 0",
    },
    "simulation.timeout_invalid_nonpositive": {
        "zh": "timeout 必须大于 0",
        "en": "timeout must be greater than 0",
    },
    "simulation.simulation_id_required": {
        "zh": "请提供 simulation_id",
        "en": "Please provide simulation_id",
    },
    "simulation.agent_id_required": {
        "zh": "请提供 agent_id",
        "en": "Please provide agent_id",
    },
    "simulation.prompt_required": {
        "zh": "请提供 prompt（采访问题）",
        "en": "Please provide prompt (interview question)",
    },
    "simulation.platform_invalid": {
        "zh": "platform 参数只能是 'twitter' 或 'reddit'",
        "en": "platform must be 'twitter' or 'reddit'",
    },
    "simulation.environment_not_alive": {
        "zh": "模拟环境未运行或已关闭。请确保模拟已完成并进入等待命令模式。",
        "en": "The simulation environment is not running or has already closed. Make sure the simulation completed and is in wait-for-commands mode.",
    },
    "simulation.interview_timeout": {
        "zh": "等待Interview响应超时: {details}",
        "en": "Timed out while waiting for the interview response: {details}",
    },
    "simulation.batch_interview_timeout": {
        "zh": "等待批量Interview响应超时: {details}",
        "en": "Timed out while waiting for the batch interview response: {details}",
    },
    "simulation.all_interview_timeout": {
        "zh": "等待全局Interview响应超时: {details}",
        "en": "Timed out while waiting for the global interview response: {details}",
    },
    "simulation.max_rounds_positive": {
        "zh": "max_rounds 必须是正整数",
        "en": "max_rounds must be a positive integer",
    },
    "simulation.max_rounds_integer": {
        "zh": "max_rounds 必须是有效的整数",
        "en": "max_rounds must be a valid integer",
    },
    "simulation.invalid_platform_type": {
        "zh": "无效的平台类型: {platform}，可选: twitter/reddit/parallel",
        "en": "Invalid platform type: {platform}. Expected twitter/reddit/parallel",
    },
    "simulation.not_found": {
        "zh": "模拟不存在: {simulation_id}",
        "en": "Simulation not found: {simulation_id}",
    },
    "simulation.running_force_required": {
        "zh": "模拟正在运行中，请先调用 /stop 接口停止，或使用 force=true 强制重新开始",
        "en": "The simulation is already running. Stop it via /stop first, or use force=true to restart it.",
    },
    "simulation.not_ready": {
        "zh": "模拟未准备好，当前状态: {status}，请先调用 /prepare 接口",
        "en": "The simulation is not ready yet. Current status: {status}. Call /prepare first.",
    },
    "simulation.graph_memory_requires_graph": {
        "zh": "启用图谱记忆更新需要有效的 graph_id，请确保项目已构建图谱",
        "en": "Enabling graph-memory updates requires a valid graph_id. Make sure the project graph has been built.",
    },
    "simulation.config_missing_prepare": {
        "zh": "模拟配置不存在，请先调用 /prepare 接口",
        "en": "The simulation config does not exist yet. Call /prepare first.",
    },
    "simulation.config_file_missing_prepare": {
        "zh": "配置文件不存在，请先调用 /prepare 接口",
        "en": "The config file does not exist yet. Call /prepare first.",
    },
    "simulation.script_unknown": {
        "zh": "未知脚本: {script_name}，可选: {allowed}",
        "en": "Unknown script: {script_name}. Allowed values: {allowed}",
    },
    "simulation.script_missing": {
        "zh": "脚本文件不存在: {script_name}",
        "en": "Script file not found: {script_name}",
    },
    "simulation.runner_dependency_error": {
        "zh": "当前后端未安装可选的 OASIS 仿真运行时依赖。请先执行 `npm run setup:backend:simulation`，或在 backend 目录执行 `uv sync --extra simulation`。",
        "en": "The optional OASIS simulation runtime dependencies are not installed. Run `npm run setup:backend:simulation`, or `uv sync --extra simulation` inside the backend directory first.",
    },
    "simulation.already_running": {
        "zh": "模拟已在运行中: {simulation_id}",
        "en": "Simulation is already running: {simulation_id}",
    },
    "simulation.start_config_missing": {
        "zh": "模拟配置不存在，请先调用 /prepare 接口",
        "en": "The simulation config does not exist yet. Call /prepare first.",
    },
    "simulation.graph_id_required_for_memory": {
        "zh": "启用图谱记忆更新时必须提供 graph_id",
        "en": "graph_id is required when graph-memory updates are enabled",
    },
    "simulation.script_path_missing": {
        "zh": "脚本不存在: {script_path}",
        "en": "Script not found: {script_path}",
    },
    "simulation.process_exit": {
        "zh": "进程退出码: {exit_code}, 错误: {details}",
        "en": "Process exited with code {exit_code}. Error: {details}",
    },
}


def get_locale(preferred: str | None = None) -> str:
    """Resolve the current locale from an explicit value or the request header."""
    if preferred in {"zh", "en"}:
        return preferred
    if has_request_context():
        header = (request.headers.get("X-Locale") or "").strip().lower()
        if header.startswith("en"):
            return "en"
    return DEFAULT_LOCALE


def tr(key: str, locale: str | None = None, **params) -> str:
    """Translate a known backend message key."""
    resolved_locale = get_locale(locale)
    template = TRANSLATIONS.get(key, {}).get(resolved_locale)
    if template is None:
        template = TRANSLATIONS.get(key, {}).get(DEFAULT_LOCALE, key)
    return template.format(**params)
