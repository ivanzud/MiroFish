import json
import sys
from types import ModuleType

fake_zep_cloud = ModuleType("zep_cloud")
fake_zep_client = ModuleType("zep_cloud.client")
fake_zep_client.Zep = object
fake_zep_cloud.client = fake_zep_client
fake_zep_cloud.__getattr__ = lambda name: object
sys.modules.setdefault("zep_cloud", fake_zep_cloud)
sys.modules.setdefault("zep_cloud.client", fake_zep_client)

from app.services.report_agent import ReportAgent
from app.services.report_agent import ReportManager
from app.services.report_agent import ReportOutline
from app.services.report_agent import ReportSection
from app.services.report_agent import ReportStatus


class FakeLLM:
    def __init__(self):
        self.messages = None
        self.temperature = None

    def chat_json(self, messages, temperature):
        self.messages = messages
        self.temperature = temperature
        return {
            "title": "游戏受众分析与预测",
            "summary": "核心玩家更偏向剧情驱动和策略投入并重的受众组合。",
            "sections": [
                {"title": "潜在人群画像"},
                {"title": "传播与留存风险"},
            ],
        }


class AbstractTitleLLM(FakeLLM):
    def chat_json(self, messages, temperature):
        self.messages = messages
        self.temperature = temperature
        return {
            "title": "未来受众群体生态的静默与解体：一项基于模拟的预测报告",
            "summary": "核心玩家更偏向剧情驱动和策略投入并重的受众组合。",
            "sections": [
                {"title": "潜在人群画像"},
                {"title": "传播与留存风险"},
            ],
        }


class FailingLLM(FakeLLM):
    def chat_json(self, messages, temperature):
        raise RuntimeError("provider offline")


class EmptySectionLLM(FakeLLM):
    def chat_json(self, messages, temperature):
        self.messages = messages
        self.temperature = temperature
        return {
            "title": "游戏受众分析与预测",
            "summary": "核心玩家更偏向剧情驱动和策略投入并重的受众组合。",
            "sections": [
                {"title": "潜在人群画像"},
            ],
        }

    def chat(self, messages, temperature, max_tokens, response_format=None):
        self.messages = messages
        self.temperature = temperature
        return None


class SequenceSectionLLM(FakeLLM):
    def __init__(self, responses):
        super().__init__()
        self.responses = list(responses)
        self.calls = []

    def chat(self, messages, temperature, max_tokens, response_format=None):
        snapshot = [{"role": item["role"], "content": item["content"]} for item in messages]
        self.calls.append(snapshot)
        self.messages = snapshot
        self.temperature = temperature
        if not self.responses:
            raise AssertionError("SequenceSectionLLM ran out of scripted responses")
        return self.responses.pop(0)


class FakeZepTools:
    def get_simulation_context(self, graph_id, simulation_requirement):
        return {
            "graph_statistics": {
                "total_nodes": 12,
                "total_edges": 21,
                "entity_types": {"玩家": 8, "媒体": 4},
            },
            "total_entities": 12,
            "related_facts": [
                {"fact": "剧情向玩家更关注世界观完整度"},
                {"fact": "策略向玩家更在意长期成长反馈"},
            ],
        }


def test_plan_outline_sends_readability_constraints_in_prompt():
    llm = FakeLLM()
    agent = ReportAgent(
        graph_id="graph-test",
        simulation_id="sim-test",
        simulation_requirement="预测这个游戏的受众群体会是什么样",
        llm_client=llm,
        zep_tools=FakeZepTools(),
    )

    outline = agent.plan_outline()

    assert outline.title == "游戏受众分析与预测"
    assert [section.title for section in outline.sections] == ["潜在人群画像", "传播与留存风险"]
    assert llm.temperature == 0.3
    assert llm.messages is not None

    system_prompt = llm.messages[0]["content"]
    user_prompt = llm.messages[1]["content"]

    assert "标题与摘要要求" in system_prompt
    assert "标题要简洁、直白、可读" in system_prompt
    assert "禁止使用与用户问题脱节的抽象比喻或夸张措辞" in system_prompt
    assert "报告标题必须让普通用户直接看懂" in user_prompt
    assert "如果模拟需求是在预测某个产品、方案、游戏、事件或人群，就在标题里明确点出该对象" in user_prompt


def test_plan_outline_falls_back_from_abstract_title_to_requirement_subject():
    llm = AbstractTitleLLM()
    agent = ReportAgent(
        graph_id="graph-test",
        simulation_id="sim-test",
        simulation_requirement="预测这个游戏的受众群体会是什么样",
        llm_client=llm,
        zep_tools=FakeZepTools(),
    )

    outline = agent.plan_outline()

    assert outline.title == "游戏受众群体分析报告"


def test_plan_outline_requests_english_output_when_locale_is_en():
    llm = FakeLLM()
    agent = ReportAgent(
        graph_id="graph-test",
        simulation_id="sim-test",
        simulation_requirement="Predict the likely audience for this game",
        locale="en",
        llm_client=llm,
        zep_tools=FakeZepTools(),
    )

    agent.plan_outline()

    assert llm.messages is not None
    user_prompt = llm.messages[1]["content"]

    assert "Return the report title, summary, and section titles/descriptions in English." in user_prompt
    assert "Keep wording concrete, readable, and directly aligned with the simulation requirement." in user_prompt


def test_plan_outline_english_progress_messages_are_localized():
    llm = FakeLLM()
    agent = ReportAgent(
        graph_id="graph-test",
        simulation_id="sim-test",
        simulation_requirement="Predict the likely audience for this game",
        locale="en",
        llm_client=llm,
        zep_tools=FakeZepTools(),
    )

    progress_updates = []
    agent.plan_outline(progress_callback=lambda stage, progress, message: progress_updates.append((stage, progress, message)))

    assert progress_updates == [
        ("planning", 0, "Analyzing the simulation requirement..."),
        ("planning", 30, "Generating the report outline..."),
        ("planning", 80, "Parsing the outline structure..."),
        ("planning", 100, "Outline planning completed"),
    ]


def test_plan_outline_english_fallback_outline_is_localized():
    agent = ReportAgent(
        graph_id="graph-test",
        simulation_id="sim-test",
        simulation_requirement="Predict the likely audience for this game",
        locale="en",
        llm_client=FailingLLM(),
        zep_tools=FakeZepTools(),
    )

    outline = agent.plan_outline()

    assert outline.title == "Forecast Report"
    assert outline.summary == "Trend and risk analysis based on the simulation forecast."
    assert [section.title for section in outline.sections] == [
        "Forecast scenarios and key findings",
        "Audience behavior analysis",
        "Trend outlook and risk signals",
    ]


def test_execute_tool_english_errors_are_localized():
    agent = ReportAgent(
        graph_id="graph-test",
        simulation_id="sim-test",
        simulation_requirement="Predict the likely audience for this game",
        locale="en",
        llm_client=FakeLLM(),
        zep_tools=FakeZepTools(),
    )

    unknown = agent._execute_tool("not_a_tool", {})
    assert unknown == "Unknown tool: not_a_tool. Use one of: insight_forge, panorama_search, quick_search"

    class BrokenTools(FakeZepTools):
        def quick_search(self, graph_id, query, limit):
            raise RuntimeError("search backend unavailable")

    failing_agent = ReportAgent(
        graph_id="graph-test",
        simulation_id="sim-test",
        simulation_requirement="Predict the likely audience for this game",
        locale="en",
        llm_client=FakeLLM(),
        zep_tools=BrokenTools(),
    )

    assert failing_agent._execute_tool("quick_search", {"query": "audience", "limit": 3}) == (
        "Tool execution failed: search backend unavailable"
    )


def test_generate_report_survives_empty_llm_section_responses(tmp_path, monkeypatch):
    monkeypatch.setattr(ReportManager, "REPORTS_DIR", str(tmp_path / "reports"))

    agent = ReportAgent(
        graph_id="graph-test",
        simulation_id="sim-test",
        simulation_requirement="预测这个游戏的受众群体会是什么样",
        llm_client=EmptySectionLLM(),
        zep_tools=FakeZepTools(),
    )

    report = agent.generate_report(report_id="report_empty_llm")

    assert report.status == ReportStatus.COMPLETED
    assert "本章节生成失败：LLM 返回空响应，请稍后重试" in report.markdown_content

    saved_progress = ReportManager.get_progress("report_empty_llm")
    assert saved_progress is not None
    assert saved_progress["status"] == "completed"
    assert saved_progress["progress"] == 100


def test_generate_section_localizes_english_react_loop_messages(monkeypatch):
    llm = SequenceSectionLLM([
        '<tool_call>{"name":"quick_search","parameters":{"query":"audience","limit":1}}</tool_call>',
        "Final Answer: Too early",
        '<tool_call>{"name":"panorama_search","parameters":{"query":"audience","include_expired":true}}</tool_call>',
        '<tool_call>{"name":"insight_forge","parameters":{"query":"audience"}}</tool_call>',
        "Final Answer: Final English section body",
    ])
    agent = ReportAgent(
        graph_id="graph-test",
        simulation_id="sim-test",
        simulation_requirement="Predict the likely audience for this game",
        locale="en",
        llm_client=llm,
        zep_tools=FakeZepTools(),
    )
    outline = ReportOutline(
        title="Forecast Report",
        summary="Audience forecast",
        sections=[ReportSection(title="Audience Outlook")],
    )
    progress_updates = []
    observed_contexts = []

    def fake_execute_tool(tool_name, parameters, report_context=None):
        observed_contexts.append((tool_name, report_context))
        return f"{tool_name} evidence"

    monkeypatch.setattr(agent, "_execute_tool", fake_execute_tool)

    content = agent._generate_section_react(
        outline.sections[0],
        outline,
        [],
        progress_callback=lambda stage, progress, message: progress_updates.append((stage, progress, message)),
        section_index=1,
    )

    assert content == "Final English section body"
    assert progress_updates[0] == ("generating", 0, "Deep retrieval and drafting in progress (0/5)")
    assert "(This is the first section)" in llm.calls[0][1]["content"]
    assert observed_contexts[0] == (
        "quick_search",
        "Section title: Audience Outlook\nSimulation requirement: Predict the likely audience for this game",
    )

    observation_prompt = llm.calls[1][-1]["content"]
    assert "Observation:" in observation_prompt
    assert "Tool quick_search returned" in observation_prompt
    assert "Tool calls used: 1/5" in observation_prompt

    insufficient_tools_prompt = llm.calls[2][-1]["content"]
    assert insufficient_tools_prompt.startswith("Notice: you have only used 1 tool calls; at least 3 are required.")
    assert "Please call another tool to gather more simulation evidence before outputting Final Answer." in insufficient_tools_prompt
    assert "Tip: you have not used these tools yet:" in insufficient_tools_prompt


def test_generate_section_localizes_english_empty_response_retry_and_fallback():
    llm = SequenceSectionLLM([None, None, None, None, None, None])
    agent = ReportAgent(
        graph_id="graph-test",
        simulation_id="sim-test",
        simulation_requirement="Predict the likely audience for this game",
        locale="en",
        llm_client=llm,
        zep_tools=FakeZepTools(),
    )
    outline = ReportOutline(
        title="Forecast Report",
        summary="Audience forecast",
        sections=[ReportSection(title="Audience Outlook")],
    )

    content = agent._generate_section_react(outline.sections[0], outline, [], section_index=1)

    assert content == "(This section could not be generated because the LLM returned an empty response. Please try again later.)"
    assert llm.calls[1][-2]["content"] == "(The response was empty)"
    assert llm.calls[1][-1]["content"] == "Please continue generating the content."


def test_generate_report_localizes_persisted_agent_log_messages_in_english(tmp_path, monkeypatch):
    monkeypatch.setattr(ReportManager, "REPORTS_DIR", str(tmp_path / "reports"))
    monkeypatch.setattr("app.services.report_agent.Config.UPLOAD_FOLDER", str(tmp_path))

    agent = ReportAgent(
        graph_id="graph-test",
        simulation_id="sim-test",
        simulation_requirement="Predict the likely audience for this game",
        locale="en",
        llm_client=EmptySectionLLM(),
        zep_tools=FakeZepTools(),
    )

    report = agent.generate_report(report_id="report_en_logs")

    assert report.status == ReportStatus.COMPLETED

    assert agent.report_logger is not None
    log_path = agent.report_logger.log_file_path
    entries = [
        json.loads(line)
        for line in open(log_path, encoding="utf-8").read().splitlines()
        if line.strip()
    ]
    messages = [entry["details"].get("message") for entry in entries]

    assert "Report generation task started" in messages
    assert "Starting report outline planning" in messages
    assert "Outline planning completed" in messages
    assert "Starting section generation: 潜在人群画像" in messages
    assert "Section generation completed: 潜在人群画像" in messages
    assert "Report generation completed" in messages


def test_generate_report_localizes_console_log_messages_in_english(tmp_path, monkeypatch):
    monkeypatch.setattr(ReportManager, "REPORTS_DIR", str(tmp_path / "reports"))
    monkeypatch.setattr("app.services.report_agent.Config.UPLOAD_FOLDER", str(tmp_path))

    agent = ReportAgent(
        graph_id="graph-test",
        simulation_id="sim-test",
        simulation_requirement="Predict the likely audience for this game",
        locale="en",
        llm_client=EmptySectionLLM(),
        zep_tools=FakeZepTools(),
    )

    report = agent.generate_report(report_id="report_en_console")

    assert report.status == ReportStatus.COMPLETED

    console_log_path = tmp_path / "reports" / "report_en_console" / "console_log.txt"
    console_output = console_log_path.read_text(encoding="utf-8")

    assert "Starting report outline planning..." in console_output
    assert "Outline planning completed: 1 sections" in console_output
    assert "Generating section with ReACT: 潜在人群画像" in console_output
    assert "Section saved: report_en_console/section_01.md" in console_output
    assert "Full report assembled: report_en_console" in console_output
    assert "Report generation completed: report_en_console" in console_output
