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
    "config.llm_key_missing": {
        "zh": "LLM_API_KEY / OPENAI_API_KEY 未配置",
        "en": "LLM_API_KEY / OPENAI_API_KEY is not configured",
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
        "zh": "SECRET_KEY 未配置；当前进程正在使用临时随机值，生产环境应显式配置",
        "en": "SECRET_KEY is not configured; a temporary random key is being used for this process, so production deployments should set it explicitly",
    },
    "config.upload_folder_info": {
        "zh": "UPLOAD_FOLDER 尚不存在，将在运行时按需创建: {path}",
        "en": "UPLOAD_FOLDER does not exist yet and will be created on demand at runtime: {path}",
    },
    "config.model_info": {
        "zh": "LLM_MODEL_NAME={model}",
        "en": "LLM_MODEL_NAME={model}",
    },
    "startup.config_error_header": {
        "zh": "配置错误:",
        "en": "Configuration errors:",
    },
    "startup.config_hint": {
        "zh": "请检查 .env 文件中的配置",
        "en": "Check the configuration in the .env file",
    },
    "app.starting": {
        "zh": "MiroFish Backend 启动中...",
        "en": "MiroFish Backend is starting...",
    },
    "app.cleanup_registered": {
        "zh": "已注册模拟进程清理函数",
        "en": "Registered the simulation process cleanup hook",
    },
    "app.request": {
        "zh": "请求: {method} {path}",
        "en": "Request: {method} {path}",
    },
    "app.request_body": {
        "zh": "请求体: {body}",
        "en": "Request body: {body}",
    },
    "app.response": {
        "zh": "响应: {status_code}",
        "en": "Response: {status_code}",
    },
    "app.started": {
        "zh": "MiroFish Backend 启动完成",
        "en": "MiroFish Backend startup completed",
    },
    "retry.sync_failed_final": {
        "zh": "函数 {func_name} 在 {max_retries} 次重试后仍失败: {error}",
        "en": "Function {func_name} still failed after {max_retries} retries: {error}",
    },
    "retry.sync_failed_attempt": {
        "zh": "函数 {func_name} 第 {attempt} 次尝试失败: {error}, {delay:.1f}秒后重试...",
        "en": "Function {func_name} failed on attempt {attempt}: {error}, retrying in {delay:.1f}s...",
    },
    "retry.async_failed_final": {
        "zh": "异步函数 {func_name} 在 {max_retries} 次重试后仍失败: {error}",
        "en": "Async function {func_name} still failed after {max_retries} retries: {error}",
    },
    "retry.async_failed_attempt": {
        "zh": "异步函数 {func_name} 第 {attempt} 次尝试失败: {error}, {delay:.1f}秒后重试...",
        "en": "Async function {func_name} failed on attempt {attempt}: {error}, retrying in {delay:.1f}s...",
    },
    "retry.api_failed_final": {
        "zh": "API调用在 {max_retries} 次重试后仍失败: {error}",
        "en": "API call still failed after {max_retries} retries: {error}",
    },
    "retry.api_failed_attempt": {
        "zh": "API调用第 {attempt} 次尝试失败: {error}, {delay:.1f}秒后重试...",
        "en": "API call failed on attempt {attempt}: {error}, retrying in {delay:.1f}s...",
    },
    "retry.batch_item_failed": {
        "zh": "处理第 {index} 项失败: {error}",
        "en": "Failed to process item {index}: {error}",
    },
    "llm.invalid_json": {
        "zh": "LLM返回的JSON格式无效: {payload}",
        "en": "The LLM returned invalid JSON: {payload}",
    },
    "file.not_found": {
        "zh": "文件不存在: {path}",
        "en": "File not found: {path}",
    },
    "file.unsupported_type": {
        "zh": "不支持的文件格式: {suffix}",
        "en": "Unsupported file format: {suffix}",
    },
    "file.unhandled_type": {
        "zh": "无法处理的文件格式: {suffix}",
        "en": "Unhandled file format: {suffix}",
    },
    "file.pdf_dependency_missing": {
        "zh": "缺少 PDF 解析依赖 PyMuPDF，请先执行 `pip install PyMuPDF`",
        "en": "Missing PDF parsing dependency PyMuPDF. Install it with `pip install PyMuPDF` first.",
    },
    "file.multi_doc_header": {
        "zh": "=== 文档 {index}: {filename} ===",
        "en": "=== Document {index}: {filename} ===",
    },
    "file.multi_doc_failed_header": {
        "zh": "=== 文档 {index}: {filename} (提取失败: {details}) ===",
        "en": "=== Document {index}: {filename} (extraction failed: {details}) ===",
    },
    "task.completed": {
        "zh": "任务完成",
        "en": "Task completed",
    },
    "task.failed": {
        "zh": "任务失败",
        "en": "Task failed",
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
    "graph.document_processing_failed": {
        "zh": "{count} 个文档处理失败，请根据返回的文件错误信息修正后重试",
        "en": "{count} document(s) could not be processed. Fix the reported file issues and retry.",
    },
    "graph.unsupported_file_type": {
        "zh": "文件 {filename} 的格式不受支持。当前仅支持: {extensions}",
        "en": "File {filename} is not supported. Supported formats: {extensions}",
    },
    "graph.document_parse_failed": {
        "zh": "文件 {filename} 解析失败: {details}",
        "en": "Failed to parse file {filename}: {details}",
    },
    "graph.document_empty_after_parse": {
        "zh": "文件 {filename} 未提取到可用文本内容",
        "en": "File {filename} did not yield any usable text",
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
    "graph.zep_auth_failed": {
        "zh": "Zep 认证失败，请检查 ZEP_API_KEY 是否有效并确认其对应当前的 Zep Cloud 项目。",
        "en": "Zep authentication failed. Check that ZEP_API_KEY is valid and belongs to the current Zep Cloud project.",
    },
    "graph.zep_permission_denied": {
        "zh": "Zep 权限不足，请确认当前 API Key 拥有访问目标图谱的权限。",
        "en": "Zep permission denied. Confirm that the current API key can access the target graph.",
    },
    "zep.reader_retry_failed_attempt": {
        "zh": "Zep {operation_name} 第 {attempt} 次尝试失败: {error}, {delay:.1f}秒后重试...",
        "en": "Zep {operation_name} failed on attempt {attempt}: {error}, retrying in {delay:.1f}s...",
    },
    "zep.reader_retry_failed_final": {
        "zh": "Zep {operation_name} 在 {max_retries} 次尝试后仍失败: {error}",
        "en": "Zep {operation_name} still failed after {max_retries} retries: {error}",
    },
    "zep.reader_get_all_nodes_start": {
        "zh": "获取图谱 {graph_id} 的所有节点...",
        "en": "Fetching all nodes for graph {graph_id}...",
    },
    "zep.reader_get_all_nodes_done": {
        "zh": "共获取 {count} 个节点",
        "en": "Fetched {count} node(s) in total",
    },
    "zep.reader_get_all_edges_start": {
        "zh": "获取图谱 {graph_id} 的所有边...",
        "en": "Fetching all edges for graph {graph_id}...",
    },
    "zep.reader_get_all_edges_done": {
        "zh": "共获取 {count} 条边",
        "en": "Fetched {count} edge(s) in total",
    },
    "zep.reader_get_node_edges_failed": {
        "zh": "获取节点 {node_uuid} 的边失败: {error}",
        "en": "Failed to fetch edges for node {node_uuid}: {error}",
    },
    "zep.reader_get_node_edges_operation": {
        "zh": "获取节点边(node={node_uuid})",
        "en": "fetch node edges (node={node_uuid})",
    },
    "zep.reader_get_node_detail_operation": {
        "zh": "获取节点详情(uuid={entity_uuid})",
        "en": "fetch node details (uuid={entity_uuid})",
    },
    "zep.reader_filter_start": {
        "zh": "开始筛选图谱 {graph_id} 的实体...",
        "en": "Starting entity filtering for graph {graph_id}...",
    },
    "zep.reader_filter_deduped": {
        "zh": "实体别名去重完成: 合并了 {count} 个重复实体候选",
        "en": "Duplicate entity alias collapse completed: merged {count} duplicate candidate(s)",
    },
    "zep.reader_filter_done": {
        "zh": "筛选完成: 总节点 {total_count}, 符合条件 {filtered_count}, 实体类型: {entity_types}",
        "en": "Entity filtering completed: total nodes {total_count}, matched {filtered_count}, entity types: {entity_types}",
    },
    "simulation.entity_not_found": {
        "zh": "实体不存在: {entity_uuid}",
        "en": "Entity not found: {entity_uuid}",
    },
    "graph.graph_deleted": {
        "zh": "图谱已删除: {graph_id}",
        "en": "Graph deleted: {graph_id}",
    },
    "graph.build_started": {
        "zh": "图谱构建任务已启动，请通过 /task/{task_id} 查询进度",
        "en": "The graph build task has started. Query /task/{task_id} for progress.",
    },
    "graph.build_task_type": {
        "zh": "构建图谱: {graph_name}",
        "en": "Build graph: {graph_name}",
    },
    "graph.build_service_initializing": {
        "zh": "初始化图谱构建服务...",
        "en": "Initializing the graph build service...",
    },
    "graph.build_chunking": {
        "zh": "文本分块中...",
        "en": "Splitting text into chunks...",
    },
    "graph.build_creating_graph": {
        "zh": "创建Zep图谱...",
        "en": "Creating the Zep graph...",
    },
    "graph.build_setting_ontology": {
        "zh": "设置本体定义...",
        "en": "Setting the ontology...",
    },
    "graph.build_add_batches_start": {
        "zh": "开始添加 {total_chunks} 个文本块...",
        "en": "Starting to add {total_chunks} text chunks...",
    },
    "graph.build_batch_sending": {
        "zh": "发送第 {batch_num}/{total_batches} 批数据 ({chunk_count} 块)...",
        "en": "Sending batch {batch_num}/{total_batches} ({chunk_count} chunk(s))...",
    },
    "graph.build_batch_retry": {
        "zh": "批次 {batch_num} 发送失败，{wait_time:.0f}秒后重试 ({attempt}/{total})...",
        "en": "Batch {batch_num} failed to send, retrying in {wait_time:.0f}s ({attempt}/{total})...",
    },
    "graph.build_waiting_for_zep": {
        "zh": "等待Zep处理数据...",
        "en": "Waiting for Zep to process the data...",
    },
    "graph.build_wait_not_required": {
        "zh": "无需等待（没有 episode）",
        "en": "No waiting required (no episodes)",
    },
    "graph.build_wait_started": {
        "zh": "开始等待 {total_episodes} 个文本块处理...",
        "en": "Waiting for {total_episodes} text chunk(s) to finish processing...",
    },
    "graph.build_wait_partial_timeout": {
        "zh": "部分文本块超时，已完成 {completed_count}/{total_episodes}",
        "en": "Some text chunks timed out, completed {completed_count}/{total_episodes}",
    },
    "graph.build_wait_progress": {
        "zh": "Zep处理中... {completed_count}/{total_episodes} 完成, {pending_count} 待处理 ({elapsed}秒)",
        "en": "Zep processing... {completed_count}/{total_episodes} complete, {pending_count} pending ({elapsed}s)",
    },
    "graph.build_wait_completed": {
        "zh": "处理完成: {completed_count}/{total_episodes}",
        "en": "Processing completed: {completed_count}/{total_episodes}",
    },
    "graph.build_fetching_graph_data": {
        "zh": "获取图谱数据...",
        "en": "Fetching graph data...",
    },
    "graph.build_started_worker": {
        "zh": "开始构建图谱...",
        "en": "Starting graph build...",
    },
    "graph.build_graph_created": {
        "zh": "图谱已创建: {graph_id}",
        "en": "Graph created: {graph_id}",
    },
    "graph.build_ontology_set": {
        "zh": "本体已设置",
        "en": "Ontology configured",
    },
    "graph.build_chunks_split": {
        "zh": "文本已分割为 {total_chunks} 个块",
        "en": "Text split into {total_chunks} chunk(s)",
    },
    "graph.build_fetching_graph_info": {
        "zh": "获取图谱信息...",
        "en": "Fetching graph info...",
    },
    "graph.build_completed": {
        "zh": "图谱构建完成",
        "en": "Graph build completed",
    },
    "graph.build_failed": {
        "zh": "构建失败: {details}",
        "en": "Build failed: {details}",
    },
    "report.simulation_id_required": {
        "zh": "请提供 simulation_id",
        "en": "Please provide simulation_id",
    },
    "report.task_or_simulation_required": {
        "zh": "请提供 task_id 或 simulation_id",
        "en": "Please provide task_id or simulation_id",
    },
    "report.task_not_found": {
        "zh": "任务不存在: {task_id}",
        "en": "Task not found: {task_id}",
    },
    "report.already_exists": {
        "zh": "报告已存在",
        "en": "The report already exists",
    },
    "report.generation_started": {
        "zh": "报告生成任务已启动，请通过 /api/report/generate/status 查询进度",
        "en": "Report generation has started. Query /api/report/generate/status for progress.",
    },
    "report.already_generated": {
        "zh": "报告已生成",
        "en": "The report has already been generated",
    },
    "report.project_not_found": {
        "zh": "项目不存在: {project_id}",
        "en": "Project not found: {project_id}",
    },
    "report.graph_id_required_built": {
        "zh": "缺少图谱ID，请确保已构建图谱",
        "en": "Missing graph_id. Make sure the project graph has been built.",
    },
    "report.graph_id_required": {
        "zh": "缺少图谱ID",
        "en": "Missing graph_id",
    },
    "report.requirement_missing": {
        "zh": "缺少模拟需求描述",
        "en": "Missing simulation requirement",
    },
    "report.generation_failed": {
        "zh": "报告生成失败",
        "en": "Report generation failed",
    },
    "report.error_generation_failed": {
        "zh": "报告生成失败",
        "en": "Report generation failed",
    },
    "report.error_start_generation_failed": {
        "zh": "启动报告生成任务失败",
        "en": "Failed to start report generation",
    },
    "report.error_task_status_failed": {
        "zh": "查询任务状态失败",
        "en": "Failed to query task status",
    },
    "report.error_get_failed": {
        "zh": "获取报告失败",
        "en": "Failed to fetch the report",
    },
    "report.error_list_failed": {
        "zh": "列出报告失败",
        "en": "Failed to list reports",
    },
    "report.error_download_failed": {
        "zh": "下载报告失败",
        "en": "Failed to download the report",
    },
    "report.error_delete_failed": {
        "zh": "删除报告失败",
        "en": "Failed to delete the report",
    },
    "report.error_chat_failed": {
        "zh": "对话失败",
        "en": "Report chat failed",
    },
    "report.error_progress_failed": {
        "zh": "获取报告进度失败",
        "en": "Failed to fetch report progress",
    },
    "report.error_section_list_failed": {
        "zh": "获取章节列表失败",
        "en": "Failed to fetch the section list",
    },
    "report.error_section_content_failed": {
        "zh": "获取章节内容失败",
        "en": "Failed to fetch section content",
    },
    "report.error_status_failed": {
        "zh": "检查报告状态失败",
        "en": "Failed to check report status",
    },
    "report.error_agent_log_failed": {
        "zh": "获取Agent日志失败",
        "en": "Failed to fetch the agent log",
    },
    "report.error_console_log_failed": {
        "zh": "获取控制台日志失败",
        "en": "Failed to fetch the console log",
    },
    "report.error_graph_search_failed": {
        "zh": "图谱搜索失败",
        "en": "Graph search failed",
    },
    "report.error_graph_stats_failed": {
        "zh": "获取图谱统计失败",
        "en": "Failed to fetch graph statistics",
    },
    "report.log_started": {
        "zh": "报告生成任务开始",
        "en": "Report generation task started",
    },
    "report.log_planning_started": {
        "zh": "开始规划报告大纲",
        "en": "Starting report outline planning",
    },
    "report.log_planning_context_loaded": {
        "zh": "获取模拟上下文信息",
        "en": "Loaded simulation context",
    },
    "report.log_planning_completed": {
        "zh": "大纲规划完成",
        "en": "Outline planning completed",
    },
    "report.log_section_started": {
        "zh": "开始生成章节: {section_title}",
        "en": "Starting section generation: {section_title}",
    },
    "report.log_react_iteration": {
        "zh": "ReACT 第{iteration}轮思考",
        "en": "ReACT iteration {iteration}",
    },
    "report.log_tool_call": {
        "zh": "调用工具: {tool_name}",
        "en": "Calling tool: {tool_name}",
    },
    "report.log_tool_result": {
        "zh": "工具 {tool_name} 返回结果",
        "en": "Tool {tool_name} returned a result",
    },
    "report.log_llm_response": {
        "zh": "LLM 响应 (工具调用: {has_tool_calls}, 最终答案: {has_final_answer})",
        "en": "LLM response (tool calls: {has_tool_calls}, final answer: {has_final_answer})",
    },
    "report.log_section_content_completed": {
        "zh": "章节 {section_title} 内容生成完成",
        "en": "Section content generated: {section_title}",
    },
    "report.log_section_completed": {
        "zh": "章节 {section_title} 生成完成",
        "en": "Section generation completed: {section_title}",
    },
    "report.log_completed": {
        "zh": "报告生成完成",
        "en": "Report generation completed",
    },
    "report.log_error": {
        "zh": "发生错误: {error}",
        "en": "Error occurred: {error}",
    },
    "report.not_found": {
        "zh": "报告不存在: {report_id}",
        "en": "Report not found: {report_id}",
    },
    "report.not_available_for_simulation": {
        "zh": "该模拟暂无报告: {simulation_id}",
        "en": "No report exists for simulation: {simulation_id}",
    },
    "report.deleted": {
        "zh": "报告已删除: {report_id}",
        "en": "Report deleted: {report_id}",
    },
    "report.message_required": {
        "zh": "请提供 message",
        "en": "Please provide message",
    },
    "report.progress_not_available": {
        "zh": "报告不存在或进度信息不可用: {report_id}",
        "en": "Report not found or progress data is unavailable: {report_id}",
    },
    "report.section_not_found": {
        "zh": "章节不存在: section_{section_index:02d}.md",
        "en": "Section not found: section_{section_index:02d}.md",
    },
    "report.graph_id_and_query_required": {
        "zh": "请提供 graph_id 和 query",
        "en": "Please provide graph_id and query",
    },
    "report.graph_id_required_for_tools": {
        "zh": "请提供 graph_id",
        "en": "Please provide graph_id",
    },
    "simulation.timeout_invalid_number": {
        "zh": "timeout 必须是大于 0 的数字",
        "en": "timeout must be a number greater than 0",
    },
    "simulation.timeout_invalid_nonpositive": {
        "zh": "timeout 必须大于 0",
        "en": "timeout must be greater than 0",
    },
    "simulation.ipc_timeout": {
        "zh": "等待命令响应超时 ({timeout}秒)",
        "en": "Timed out while waiting for the command response ({timeout}s)",
    },
    "simulation.ipc_command_sent": {
        "zh": "发送IPC命令: {command_type}, command_id={command_id}",
        "en": "Sent IPC command: {command_type}, command_id={command_id}",
    },
    "simulation.ipc_response_received": {
        "zh": "收到IPC响应: command_id={command_id}, status={status}",
        "en": "Received IPC response: command_id={command_id}, status={status}",
    },
    "simulation.ipc_response_parse_failed": {
        "zh": "解析IPC响应失败: {error}",
        "en": "Failed to parse the IPC response: {error}",
    },
    "simulation.ipc_command_file_read_failed": {
        "zh": "读取IPC命令文件失败: {path}, {error}",
        "en": "Failed to read the IPC command file: {path}, {error}",
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
    "simulation.interview_command_sent": {
        "zh": "发送Interview命令: simulation_id={simulation_id}, agent_id={agent_id}, platform={platform}",
        "en": "Sent interview command: simulation_id={simulation_id}, agent_id={agent_id}, platform={platform}",
    },
    "simulation.batch_interview_command_sent": {
        "zh": "发送批量Interview命令: simulation_id={simulation_id}, count={count}, platform={platform}",
        "en": "Sent batch interview command: simulation_id={simulation_id}, count={count}, platform={platform}",
    },
    "simulation.all_interview_command_sent": {
        "zh": "发送全局Interview命令: simulation_id={simulation_id}, agent_count={agent_count}, platform={platform}",
        "en": "Sent global interview command: simulation_id={simulation_id}, agent_count={agent_count}, platform={platform}",
    },
    "simulation.close_env_command_sent": {
        "zh": "发送关闭环境命令: simulation_id={simulation_id}",
        "en": "Sent close-environment command: simulation_id={simulation_id}",
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
    "simulation.project_graph_required": {
        "zh": "项目尚未构建图谱，请先调用 /api/graph/build",
        "en": "The project graph has not been built yet. Call /api/graph/build first.",
    },
    "simulation.project_requirement_required": {
        "zh": "项目缺少模拟需求描述 (simulation_requirement)",
        "en": "The project is missing simulation_requirement",
    },
    "simulation.prepare_dir_missing": {
        "zh": "模拟目录不存在",
        "en": "The simulation directory does not exist",
    },
    "simulation.prepare_missing_files": {
        "zh": "缺少必要文件",
        "en": "Missing required files",
    },
    "simulation.prepare_status_not_ready": {
        "zh": "状态不在已准备列表中或config_generated为false: status={status}, config_generated={config_generated}",
        "en": "The simulation is not in a prepared state or config_generated is false: status={status}, config_generated={config_generated}",
    },
    "simulation.prepare_state_read_failed": {
        "zh": "读取状态文件失败: {details}",
        "en": "Failed to read the simulation state file: {details}",
    },
    "simulation.prepare_already_done": {
        "zh": "已有完成的准备工作，无需重复生成",
        "en": "Preparation already exists and does not need to run again",
    },
    "simulation.prepare_started": {
        "zh": "准备任务已启动，请通过 /api/simulation/prepare/status 查询进度",
        "en": "Preparation has started. Query /api/simulation/prepare/status for progress.",
    },
    "simulation.prepare_exists_short": {
        "zh": "已有完成的准备工作",
        "en": "Preparation already exists",
    },
    "simulation.prepare_not_started": {
        "zh": "尚未开始准备，请调用 /api/simulation/prepare 开始",
        "en": "Preparation has not started yet. Call /api/simulation/prepare first.",
    },
    "simulation.prepare_task_completed_existing": {
        "zh": "任务已完成（准备工作已存在）",
        "en": "The task is already complete because preparation already exists",
    },
    "simulation.prepare_stage_reading": {
        "zh": "读取图谱实体",
        "en": "Reading graph entities",
    },
    "simulation.prepare_stage_generating_profiles": {
        "zh": "生成Agent人设",
        "en": "Generating agent profiles",
    },
    "simulation.prepare_stage_generating_config": {
        "zh": "生成模拟配置",
        "en": "Generating simulation config",
    },
    "simulation.prepare_stage_copying_scripts": {
        "zh": "准备模拟脚本",
        "en": "Preparing simulation scripts",
    },
    "simulation.prepare_initializing": {
        "zh": "开始准备模拟环境...",
        "en": "Preparing the simulation environment...",
    },
    "simulation.prepare_connecting_graph": {
        "zh": "正在连接Zep图谱...",
        "en": "Connecting to the Zep graph...",
    },
    "simulation.prepare_reading_nodes": {
        "zh": "正在读取节点数据...",
        "en": "Reading node data...",
    },
    "simulation.prepare_entities_completed": {
        "zh": "完成，共 {count} 个实体",
        "en": "Completed with {count} entities",
    },
    "simulation.prepare_generation_starting": {
        "zh": "开始生成...",
        "en": "Starting generation...",
    },
    "simulation.prepare_saving_profiles": {
        "zh": "保存Profile文件...",
        "en": "Saving profile files...",
    },
    "simulation.prepare_profiles_completed": {
        "zh": "完成，共 {count} 个Profile",
        "en": "Completed with {count} profiles",
    },
    "simulation.prepare_analyzing_requirement": {
        "zh": "正在分析模拟需求...",
        "en": "Analyzing the simulation requirement...",
    },
    "simulation.prepare_generating_config": {
        "zh": "正在调用LLM生成配置...",
        "en": "Calling the LLM to generate the config...",
    },
    "simulation.prepare_saving_config": {
        "zh": "正在保存配置文件...",
        "en": "Saving the config file...",
    },
    "simulation.prepare_config_completed": {
        "zh": "配置生成完成",
        "en": "Configuration generation completed",
    },
    "simulation.run_instructions_activate_env": {
        "zh": "1. 激活conda环境: conda activate MiroFish",
        "en": "1. Activate the conda environment: conda activate MiroFish",
    },
    "simulation.run_instructions_run_header": {
        "zh": "2. 运行模拟 (脚本位于 {scripts_dir}):",
        "en": "2. Run the simulation (scripts are located in {scripts_dir}):",
    },
    "simulation.run_instructions_twitter": {
        "zh": "   - 单独运行Twitter: python {scripts_dir}/run_twitter_simulation.py --config {config_path}",
        "en": "   - Run Twitter only: python {scripts_dir}/run_twitter_simulation.py --config {config_path}",
    },
    "simulation.run_instructions_reddit": {
        "zh": "   - 单独运行Reddit: python {scripts_dir}/run_reddit_simulation.py --config {config_path}",
        "en": "   - Run Reddit only: python {scripts_dir}/run_reddit_simulation.py --config {config_path}",
    },
    "simulation.run_instructions_parallel": {
        "zh": "   - 并行运行双平台: python {scripts_dir}/run_parallel_simulation.py --config {config_path}",
        "en": "   - Run both platforms in parallel: python {scripts_dir}/run_parallel_simulation.py --config {config_path}",
    },
    "simulation.graph_id_required": {
        "zh": "请提供 graph_id",
        "en": "Please provide graph_id",
    },
    "simulation.no_matching_entities": {
        "zh": "没有找到符合条件的实体",
        "en": "No matching entities were found",
    },
    "simulation.no_matching_entities_build_graph": {
        "zh": "没有找到符合条件的实体，请检查图谱是否正确构建",
        "en": "No matching entities were found. Check that the graph was built correctly.",
    },
    "simulation.interviews_required": {
        "zh": "请提供 interviews（采访列表）",
        "en": "Please provide interviews",
    },
    "simulation.interview_item_agent_required": {
        "zh": "采访列表第{index}项缺少 agent_id",
        "en": "Interview item {index} is missing agent_id",
    },
    "simulation.interview_item_prompt_required": {
        "zh": "采访列表第{index}项缺少 prompt",
        "en": "Interview item {index} is missing prompt",
    },
    "simulation.interview_item_platform_invalid": {
        "zh": "采访列表第{index}项的platform只能是 'twitter' 或 'reddit'",
        "en": "Interview item {index} platform must be 'twitter' or 'reddit'",
    },
    "simulation.env_running": {
        "zh": "环境正在运行，可以接收Interview命令",
        "en": "The environment is running and can accept interview commands",
    },
    "simulation.env_closed": {
        "zh": "环境未运行或已关闭",
        "en": "The environment is not running or has already closed",
    },
    "simulation.env_already_closed": {
        "zh": "环境已经关闭",
        "en": "The environment is already closed",
    },
    "simulation.env_close_sent": {
        "zh": "环境关闭命令已发送",
        "en": "The environment close command was sent",
    },
    "simulation.env_close_timeout": {
        "zh": "环境关闭命令已发送（等待响应超时，环境可能正在关闭）",
        "en": "The environment close command was sent, but waiting for the response timed out and the environment may already be shutting down",
    },
    "simulation.running_force_required": {
        "zh": "模拟正在运行中，请先调用 /stop 接口停止，或使用 force=true 强制重新开始",
        "en": "The simulation is already running. Stop it via /stop first, or use force=true to restart it.",
    },
    "simulation.not_running_status": {
        "zh": "模拟未在运行: {simulation_id}, status={status}",
        "en": "The simulation is not running: {simulation_id}, status={status}",
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
    "simulation.config_no_agents": {
        "zh": "模拟配置中没有Agent: {simulation_id}",
        "en": "The simulation config has no agents: {simulation_id}",
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
    "simulation.run_state_load_failed": {
        "zh": "加载运行状态失败: {error}",
        "en": "Failed to load the run state: {error}",
    },
    "simulation.interview_history_read_failed": {
        "zh": "读取Interview历史失败 ({platform_name}): {error}",
        "en": "Failed to read interview history ({platform_name}): {error}",
    },
    "simulation.already_running": {
        "zh": "模拟已在运行中: {simulation_id}",
        "en": "Simulation is already running: {simulation_id}",
    },
    "simulation.start_config_missing": {
        "zh": "模拟配置不存在，请先调用 /prepare 接口",
        "en": "The simulation config does not exist yet. Call /prepare first.",
    },
    "simulation.rounds_truncated": {
        "zh": "轮数已截断: {original_rounds} -> {total_rounds} (max_rounds={max_rounds})",
        "en": "Rounds truncated: {original_rounds} -> {total_rounds} (max_rounds={max_rounds})",
    },
    "simulation.graph_id_required_for_memory": {
        "zh": "启用图谱记忆更新时必须提供 graph_id",
        "en": "graph_id is required when graph-memory updates are enabled",
    },
    "simulation.graph_memory_enabled": {
        "zh": "已启用图谱记忆更新: simulation_id={simulation_id}, graph_id={graph_id}",
        "en": "Graph-memory updates enabled: simulation_id={simulation_id}, graph_id={graph_id}",
    },
    "simulation.graph_memory_enable_failed": {
        "zh": "创建图谱记忆更新器失败: {details}",
        "en": "Failed to create the graph-memory updater: {details}",
    },
    "simulation.script_path_missing": {
        "zh": "脚本不存在: {script_path}",
        "en": "Script not found: {script_path}",
    },
    "simulation.started": {
        "zh": "模拟启动成功: {simulation_id}, pid={pid}, platform={platform}",
        "en": "Simulation started: {simulation_id}, pid={pid}, platform={platform}",
    },
    "simulation.completed": {
        "zh": "模拟完成: {simulation_id}",
        "en": "Simulation completed: {simulation_id}",
    },
    "simulation.failed": {
        "zh": "模拟失败: {simulation_id}, error={error}",
        "en": "Simulation failed: {simulation_id}, error={error}",
    },
    "simulation.monitor_thread_failed": {
        "zh": "监控线程异常: {simulation_id}, error={error}",
        "en": "Simulation monitor thread failed: {simulation_id}, error={error}",
    },
    "simulation.graph_memory_stopped": {
        "zh": "已停止图谱记忆更新: simulation_id={simulation_id}",
        "en": "Stopped graph-memory updates: simulation_id={simulation_id}",
    },
    "simulation.graph_memory_stop_failed": {
        "zh": "停止图谱记忆更新器失败: {details}",
        "en": "Failed to stop the graph-memory updater: {details}",
    },
    "simulation.platform_completed": {
        "zh": "{platform} 模拟已完成: {simulation_id}, total_rounds={total_rounds}, total_actions={total_actions}",
        "en": "{platform} simulation completed: {simulation_id}, total_rounds={total_rounds}, total_actions={total_actions}",
    },
    "simulation.all_platforms_completed": {
        "zh": "所有平台模拟已完成: {simulation_id}",
        "en": "All platform simulations completed: {simulation_id}",
    },
    "simulation.read_action_log_failed": {
        "zh": "读取动作日志失败: {log_path}, error={error}",
        "en": "Failed to read the action log: {log_path}, error={error}",
    },
    "simulation.terminate_process_tree_windows": {
        "zh": "终止进程树 (Windows): simulation={simulation_id}, pid={pid}",
        "en": "Terminating process tree (Windows): simulation={simulation_id}, pid={pid}",
    },
    "simulation.process_force_kill": {
        "zh": "进程未响应，强制终止: {simulation_id}",
        "en": "Process did not respond and will be force-killed: {simulation_id}",
    },
    "simulation.taskkill_failed_fallback": {
        "zh": "taskkill 失败，尝试 terminate: {details}",
        "en": "taskkill failed, falling back to terminate: {details}",
    },
    "simulation.terminate_process_group_unix": {
        "zh": "终止进程组 (Unix): simulation={simulation_id}, pgid={pgid}",
        "en": "Terminating process group (Unix): simulation={simulation_id}, pgid={pgid}",
    },
    "simulation.process_group_force_kill": {
        "zh": "进程组未响应 SIGTERM，强制终止: {simulation_id}",
        "en": "Process group did not respond to SIGTERM and will be force-killed: {simulation_id}",
    },
    "simulation.terminate_failed": {
        "zh": "终止进程组失败: {simulation_id}, error={error}",
        "en": "Failed to terminate the process group: {simulation_id}, error={error}",
    },
    "simulation.stopped": {
        "zh": "模拟已停止: {simulation_id}",
        "en": "Simulation stopped: {simulation_id}",
    },
    "simulation.process_exit": {
        "zh": "进程退出码: {exit_code}, 错误: {details}",
        "en": "Process exited with code {exit_code}. Error: {details}",
    },
    "simulation.process_exit_huggingface_network": {
        "zh": "模拟运行失败：下载 HuggingFace 模型或资源时出现网络错误。请检查当前机器是否能访问 huggingface.co，并确认代理/VPN 配置后重试。",
        "en": "The simulation run failed while downloading HuggingFace models or assets. Check that this machine can reach huggingface.co, then verify your proxy/VPN settings and retry.",
    },
    "simulation.cleanup_dir_missing": {
        "zh": "模拟目录不存在，无需清理",
        "en": "The simulation directory does not exist and does not need cleanup",
    },
    "simulation.cleanup_delete_failed": {
        "zh": "删除 {target} 失败: {details}",
        "en": "Failed to delete {target}: {details}",
    },
    "simulation.cleanup_completed": {
        "zh": "清理模拟日志完成: {simulation_id}, 删除文件: {cleaned_files}",
        "en": "Simulation log cleanup completed: {simulation_id}, deleted files: {cleaned_files}",
    },
    "simulation.cleanup_all_started": {
        "zh": "正在清理所有模拟进程...",
        "en": "Cleaning up all simulation processes...",
    },
    "simulation.graph_memory_stop_all_failed": {
        "zh": "停止图谱记忆更新器失败: {details}",
        "en": "Failed to stop graph-memory updaters: {details}",
    },
    "simulation.terminating_process": {
        "zh": "终止模拟进程: {simulation_id}, pid={pid}",
        "en": "Terminating simulation process: {simulation_id}, pid={pid}",
    },
    "simulation.state_json_update_attempt": {
        "zh": "尝试更新 state.json: {state_file}",
        "en": "Attempting to update state.json: {state_file}",
    },
    "simulation.state_json_updated": {
        "zh": "已更新 state.json 状态为 stopped: {simulation_id}",
        "en": "Updated state.json status to stopped: {simulation_id}",
    },
    "simulation.state_json_missing": {
        "zh": "state.json 不存在: {state_file}",
        "en": "state.json does not exist: {state_file}",
    },
    "simulation.state_json_update_failed": {
        "zh": "更新 state.json 失败: {simulation_id}, error={error}",
        "en": "Failed to update state.json: {simulation_id}, error={error}",
    },
    "simulation.cleanup_process_failed": {
        "zh": "清理进程失败: {simulation_id}, error={error}",
        "en": "Failed to clean up the process: {simulation_id}, error={error}",
    },
    "simulation.cleanup_all_completed": {
        "zh": "模拟进程清理完成",
        "en": "Simulation process cleanup completed",
    },
    "simulation.stopped_server_shutdown": {
        "zh": "服务器关闭，模拟被终止",
        "en": "The server is shutting down, so the simulation was stopped",
    },
    "simulation.cleanup_signal_received": {
        "zh": "收到信号 {signum}，开始清理...",
        "en": "Received signal {signum}; starting cleanup...",
    },
    "simulation.signal_handler_register_failed": {
        "zh": "无法注册信号处理器（不在主线程），仅使用 atexit",
        "en": "Could not register signal handlers outside the main thread; using atexit only",
    },
    "simulation.posts_db_missing": {
        "zh": "数据库不存在，模拟可能尚未运行",
        "en": "The simulation database does not exist yet. The simulation may not have run for this platform.",
    },
    "simulation.prepare_check_status": {
        "zh": "检测模拟准备状态: {simulation_id}, status={status}, config_generated={config_generated}",
        "en": "Checking simulation prepare state: {simulation_id}, status={status}, config_generated={config_generated}",
    },
    "simulation.prepare_auto_ready": {
        "zh": "自动更新模拟状态: {simulation_id} preparing -> ready",
        "en": "Auto-updated simulation state: {simulation_id} preparing -> ready",
    },
    "simulation.prepare_auto_ready_failed": {
        "zh": "自动更新状态失败: {error}",
        "en": "Failed to auto-update the simulation state: {error}",
    },
    "simulation.prepare_check_ready": {
        "zh": "模拟 {simulation_id} 检测结果: 已准备完成 (status={status}, config_generated={config_generated})",
        "en": "Simulation {simulation_id} prepare check result: ready (status={status}, config_generated={config_generated})",
    },
    "simulation.prepare_check_not_ready": {
        "zh": "模拟 {simulation_id} 检测结果: 未准备完成 (status={status}, config_generated={config_generated})",
        "en": "Simulation {simulation_id} prepare check result: not ready (status={status}, config_generated={config_generated})",
    },
    "simulation.force_stop_running": {
        "zh": "强制模式：停止运行中的模拟 {simulation_id}",
        "en": "Force mode: stopping the running simulation {simulation_id}",
    },
    "simulation.force_stop_warning": {
        "zh": "停止模拟时出现警告: {error}",
        "en": "Stopping the simulation raised a warning: {error}",
    },
    "simulation.force_cleanup_logs": {
        "zh": "强制模式：清理模拟日志 {simulation_id}",
        "en": "Force mode: cleaning simulation logs for {simulation_id}",
    },
    "simulation.force_cleanup_warning": {
        "zh": "清理日志时出现警告: {errors}",
        "en": "Cleaning simulation logs raised a warning: {errors}",
    },
    "simulation.reset_ready_after_prepare": {
        "zh": "模拟 {simulation_id} 准备工作已完成，重置状态为 ready（原状态: {status}）",
        "en": "Simulation {simulation_id} already has prepared assets; resetting state to ready (previous status: {status})",
    },
    "simulation.graph_memory_enable_request": {
        "zh": "启用图谱记忆更新: simulation_id={simulation_id}, graph_id={graph_id}",
        "en": "Enabling graph-memory updates: simulation_id={simulation_id}, graph_id={graph_id}",
    },
    "simulation.created_log": {
        "zh": "创建模拟: {simulation_id}, project={project_id}, graph={graph_id}",
        "en": "Created simulation: {simulation_id}, project={project_id}, graph={graph_id}",
    },
    "simulation.prepare_completed_log": {
        "zh": "模拟准备完成: {simulation_id}, entities={entities}, profiles={profiles}",
        "en": "Simulation preparation completed: {simulation_id}, entities={entities}, profiles={profiles}",
    },
    "simulation.prepare_failed_log": {
        "zh": "模拟准备失败: {simulation_id}, error={error}",
        "en": "Simulation preparation failed: {simulation_id}, error={error}",
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
