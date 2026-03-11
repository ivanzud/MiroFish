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
