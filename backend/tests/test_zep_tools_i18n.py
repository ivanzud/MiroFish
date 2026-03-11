from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType

from flask import Flask

fake_zep_cloud = ModuleType("zep_cloud")
fake_zep_client = ModuleType("zep_cloud.client")
fake_zep_client.Zep = object
fake_zep_cloud.client = fake_zep_client
fake_zep_cloud.__getattr__ = lambda name: object
sys.modules.setdefault("zep_cloud", fake_zep_cloud)
sys.modules.setdefault("zep_cloud.client", fake_zep_client)

from app.services import zep_tools as zep_tools_module
from app.services.zep_tools import (
    AgentInterview,
    EdgeInfo,
    InsightForgeResult,
    NodeInfo,
    PanoramaResult,
    SearchResult,
    ZepToolsService,
)


def _make_service() -> ZepToolsService:
    return ZepToolsService.__new__(ZepToolsService)


class FakeLogger:
    def __init__(self) -> None:
        self.messages = []

    def debug(self, message):
        self.messages.append(("debug", str(message)))

    def info(self, message):
        self.messages.append(("info", str(message)))

    def warning(self, message):
        self.messages.append(("warning", str(message)))

    def error(self, message):
        self.messages.append(("error", str(message)))


def test_interview_agents_localizes_missing_profiles_summary_in_english():
    app = Flask(__name__)
    service = _make_service()
    service._load_agent_profiles = lambda simulation_id: []

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.interview_agents("sim_123", "Understand the reaction")

    assert result.summary == "No interviewable agent profiles were found"


def test_search_graph_localizes_fallback_logs_in_english(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    service.MAX_RETRIES = 1
    service.RETRY_DELAY = 0

    class FakeGraphAPI:
        def search(self, **kwargs):
            raise RuntimeError("search unavailable")

    class FakeClient:
        graph = FakeGraphAPI()

    fake_logger = FakeLogger()
    service.client = FakeClient()
    service.get_all_edges = lambda graph_id: [
        EdgeInfo(
            uuid="edge-1",
            name="influences",
            fact="Alice influences Bob",
            source_node_uuid="node-1",
            target_node_uuid="node-2",
            locale="en",
        )
    ]
    service.get_all_nodes = lambda graph_id: []
    monkeypatch.setattr(zep_tools_module, "logger", fake_logger)

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.search_graph("graph-1", "Alice")

    assert result.total_count == 1
    assert any("Graph search: graph_id=graph-1" in message for _, message in fake_logger.messages)
    assert any("falling back to local search" in message for _, message in fake_logger.messages)
    assert any("Local search completed: found 1 relevant facts" in message for _, message in fake_logger.messages)
    assert all("图谱搜索" not in message for _, message in fake_logger.messages)


def test_graph_introspection_logs_are_localized_in_english(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    fake_logger = FakeLogger()

    class FakeNode:
        def __init__(self, uuid_, name):
            self.uuid_ = uuid_
            self.name = name
            self.labels = ["Entity", "Analyst"]
            self.summary = "Tracks sentiment shifts."
            self.attributes = {}

    class FakeEdge:
        def __init__(self):
            self.uuid_ = "edge-1"
            self.name = "influences"
            self.fact = "Alice influences Bob"
            self.source_node_uuid = "node-1"
            self.target_node_uuid = "node-2"
            self.created_at = None
            self.valid_at = None
            self.invalid_at = None
            self.expired_at = None

    class FakeNodeAPI:
        @staticmethod
        def get(uuid_):
            return FakeNode(uuid_, "Alice")

    class FakeGraphAPI:
        node = FakeNodeAPI()

    class FakeClient:
        graph = FakeGraphAPI()

    service.client = FakeClient()
    monkeypatch.setattr(zep_tools_module, "logger", fake_logger)
    monkeypatch.setattr(zep_tools_module, "fetch_all_nodes", lambda client, graph_id: [FakeNode("node-1", "Alice")])
    monkeypatch.setattr(zep_tools_module, "fetch_all_edges", lambda client, graph_id: [FakeEdge()])

    with app.test_request_context(headers={"X-Locale": "en"}):
        nodes = service.get_all_nodes("graph-1")
        edges = service.get_all_edges("graph-1")
        detail = service.get_node_detail("node-1")
        related_edges = service.get_node_edges("graph-1", "node-1")
        stats = service.get_graph_statistics("graph-1")

    assert len(nodes) == 1
    assert len(edges) == 1
    assert detail is not None
    assert len(related_edges) == 1
    assert stats["total_nodes"] == 1
    assert any("Fetching all nodes for graph graph-1..." in message for _, message in fake_logger.messages)
    assert any("Fetched 1 nodes" in message for _, message in fake_logger.messages)
    assert any("Fetching node details: node-1..." in message for _, message in fake_logger.messages)
    assert any("Fetching edges related to node node-1..." in message for _, message in fake_logger.messages)
    assert any("Found 1 edges related to the node" in message for _, message in fake_logger.messages)
    assert any("Fetching graph statistics for graph-1..." in message for _, message in fake_logger.messages)
    assert all("获取图谱" not in message for _, message in fake_logger.messages)
    assert all("获取节点" not in message for _, message in fake_logger.messages)


def test_panorama_quicksearch_and_insightforge_logs_are_localized_in_english(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    fake_logger = FakeLogger()

    monkeypatch.setattr(zep_tools_module, "logger", fake_logger)
    service.search_graph = lambda **kwargs: SearchResult(
        facts=["Alice influences Bob"],
        edges=[
            {
                "name": "influences",
                "fact": "Alice influences Bob",
                "source_node_uuid": "node-1",
                "target_node_uuid": "node-2",
            }
        ],
        nodes=[],
        query=kwargs["query"],
        total_count=1,
        locale="en",
    )
    service.get_all_nodes = lambda graph_id: [
        NodeInfo(
            uuid="node-1",
            name="Alice",
            labels=["Entity", "Analyst"],
            summary="Tracks sentiment shifts.",
            attributes={},
            locale="en",
        ),
        NodeInfo(
            uuid="node-2",
            name="Bob",
            labels=["Entity", "Citizen"],
            summary="Responds to policy changes.",
            attributes={},
            locale="en",
        ),
    ]
    service.get_all_edges = lambda graph_id, include_temporal=True: [
        EdgeInfo(
            uuid="edge-1",
            name="influences",
            fact="Alice influences Bob",
            source_node_uuid="node-1",
            target_node_uuid="node-2",
            source_node_name="Alice",
            target_node_name="Bob",
            locale="en",
        )
    ]
    service._generate_sub_queries = lambda **kwargs: ["Who influenced the discussion?"]
    service.get_node_detail = lambda uuid, graph_id=None: NodeInfo(
        uuid=uuid,
        name="Alice" if uuid == "node-1" else "Bob",
        labels=["Entity", "Analyst" if uuid == "node-1" else "Citizen"],
        summary="Context",
        attributes={},
        locale="en",
    )

    with app.test_request_context(headers={"X-Locale": "en"}):
        quick = service.quick_search("graph-1", "Alice")
        panorama = service.panorama_search("graph-1", "Alice")
        insight = service.insight_forge("graph-1", "Who influenced the discussion?", "Track policy sentiment")

    assert quick.total_count == 1
    assert panorama.active_count == 1
    assert insight.total_facts == 1
    assert any("QuickSearch: Alice..." in message for _, message in fake_logger.messages)
    assert any("QuickSearch completed: 1 results" in message for _, message in fake_logger.messages)
    assert any("PanoramaSearch overview: Alice..." in message for _, message in fake_logger.messages)
    assert any("PanoramaSearch completed: 1 active facts, 0 historical facts" in message for _, message in fake_logger.messages)
    assert any("InsightForge deep analysis: Who influenced the discussion?..." in message for _, message in fake_logger.messages)
    assert any("Generated 1 sub-queries" in message for _, message in fake_logger.messages)
    assert any("InsightForge completed: 1 facts, 2 entities, 1 relationships" in message for _, message in fake_logger.messages)
    assert all("深度洞察检索" not in message for _, message in fake_logger.messages)
    assert all("条有效" not in message for _, message in fake_logger.messages)


def test_interview_agents_localizes_missing_profile_logs_in_english(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    service._load_agent_profiles = lambda simulation_id: []
    fake_logger = FakeLogger()
    monkeypatch.setattr(zep_tools_module, "logger", fake_logger)

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.interview_agents("sim_123", "Understand the reaction")

    assert result.summary == "No interviewable agent profiles were found"
    assert any("InterviewAgents deep interview (live API)" in message for _, message in fake_logger.messages)
    assert any("No agent profile files were found for simulation sim_123" in message for _, message in fake_logger.messages)
    assert all("未找到模拟" not in message for _, message in fake_logger.messages)


def test_interview_agents_localizes_english_placeholders_and_text(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    service._load_agent_profiles = lambda simulation_id: [
        {
            "username": "alice",
            "realname": "Alice",
            "profession": "Analyst",
            "bio": "Tracks policy sentiment shifts.",
        }
    ]
    service._select_agents_for_interview = lambda **kwargs: (
        [service._load_agent_profiles("sim_123")[0]],
        [0],
        "Selected for domain relevance.",
    )
    service._generate_interview_questions = lambda **kwargs: ["What changed after the announcement?"]
    service._generate_interview_summary = lambda **kwargs: "The reaction was mixed but informed."

    monkeypatch.setattr(
        "app.services.simulation_runner.SimulationRunner.interview_agents_batch",
        lambda **kwargs: {
            "success": True,
            "interviews_count": 1,
            "result": {
                "results": {
                    "twitter_0": {"response": "People became more cautious after the update."},
                    "reddit_0": {"response": ""},
                }
            },
        },
    )

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.interview_agents("sim_123", "Understand the reaction")

    assert result.interviews[0].response == (
        "[Twitter answer]\n"
        "People became more cautious after the update.\n\n"
        "[Reddit answer]\n"
        "(no reply received from this platform)"
    )
    assert result.interviews[0].key_quotes == [
        "People became more cautious after the update."
    ]

    rendered = result.to_text()
    assert "## In-Depth Interview Report" in rendered
    assert "**Interview topic:** Understand the reaction" in rendered
    assert "_Bio: Tracks policy sentiment shifts._" in rendered
    assert '**Key quotes:**' in rendered
    assert '> "People became more cautious after the update."' in rendered


def test_interview_agents_localizes_api_failure_summary_in_english(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    service._load_agent_profiles = lambda simulation_id: [{"username": "alice", "bio": ""}]
    service._select_agents_for_interview = lambda **kwargs: ([{"username": "alice", "bio": ""}], [0], "")
    service._generate_interview_questions = lambda **kwargs: ["What happened?"]

    monkeypatch.setattr(
        "app.services.simulation_runner.SimulationRunner.interview_agents_batch",
        lambda **kwargs: {"success": False, "error": "env offline"},
    )

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.interview_agents("sim_123", "Understand the reaction")

    assert (
        result.summary
        == "Interview API call failed: env offline. Check the OASIS simulation environment status."
    )


def test_interview_agents_localizes_live_api_prompt_prefix_in_english(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    service._load_agent_profiles = lambda simulation_id: [{"username": "alice", "bio": ""}]
    service._select_agents_for_interview = lambda **kwargs: ([{"username": "alice", "bio": ""}], [0], "")
    service._generate_interview_questions = lambda **kwargs: ["What happened?"]
    captured = {}
    monkeypatch.setattr(zep_tools_module.Config, "INTERVIEW_BATCH_TIMEOUT_SECONDS", 321.0)

    def fake_batch(**kwargs):
        captured["prompt"] = kwargs["interviews"][0]["prompt"]
        captured["timeout"] = kwargs["timeout"]
        return {
            "success": True,
            "interviews_count": 1,
            "result": {"results": {"twitter_0": {"response": "It changed quickly."}, "reddit_0": {"response": ""}}},
        }

    monkeypatch.setattr(
        "app.services.simulation_runner.SimulationRunner.interview_agents_batch",
        fake_batch,
    )

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.interview_agents("sim_123", "Understand the reaction")

    assert result.summary
    assert captured["prompt"].startswith("You are being interviewed.")
    assert "Response requirements:" in captured["prompt"]
    assert "\"Question X:\"" in captured["prompt"]
    assert "What happened?" in captured["prompt"]
    assert captured["timeout"] == 321.0


def test_tool_result_renderers_localize_deterministic_wrappers_in_english():
    search = SearchResult(
        facts=["Alice joined the discussion."],
        edges=[],
        nodes=[],
        query="Alice sentiment",
        total_count=1,
        locale="en",
    )
    assert "Search query: Alice sentiment" in search.to_text()
    assert "### Relevant facts:" in search.to_text()

    node = NodeInfo(
        uuid="node-1",
        name="Alice",
        labels=["Entity", "Analyst"],
        summary="Tracks sentiment shifts.",
        attributes={},
        alias_names=["Alice", "Alice Chen"],
        locale="en",
    )
    assert (
        node.to_text()
        == "Entity: Alice (Type: Analyst)\n"
        "Summary: Tracks sentiment shifts.\n"
        "Aliases: Alice, Alice Chen"
    )

    edge = EdgeInfo(
        uuid="edge-1",
        name="influences",
        fact="Alice influences Bob",
        source_node_uuid="node-1",
        target_node_uuid="node-2",
        source_node_name="Alice",
        target_node_name="Bob",
        valid_at="2026-03-01",
        invalid_at=None,
        expired_at="2026-03-10",
        locale="en",
    )
    rendered_edge = edge.to_text(include_temporal=True)
    assert "Relationship: Alice --[influences]--> Bob" in rendered_edge
    assert "Fact: Alice influences Bob" in rendered_edge
    assert "Validity: 2026-03-01 - present" in rendered_edge
    assert "(expired: 2026-03-10)" in rendered_edge

    insight = InsightForgeResult(
        query="Who shaped the narrative?",
        simulation_requirement="Track policy sentiment",
        sub_queries=["Who posted first?"],
        semantic_facts=["Alice posted first."],
        entity_insights=[
            {
                "name": "Alice",
                "type": "Analyst",
                "summary": "Tracks sentiment shifts.",
                "related_facts": ["Alice posted first."],
            }
        ],
        relationship_chains=["Alice --[influences]--> Bob"],
        total_facts=1,
        total_entities=1,
        total_relationships=1,
        locale="en",
    )
    rendered_insight = insight.to_text()
    assert "## Future prediction deep analysis" in rendered_insight
    assert "### Analysis sub-questions" in rendered_insight
    assert "### [Key facts] (quote these original statements in the report)" in rendered_insight
    assert "### [Core entities]" in rendered_insight
    assert "Summary: \"Tracks sentiment shifts.\"" in rendered_insight
    assert "Related facts: 1" in rendered_insight
    assert "### [Relationship chains]" in rendered_insight

    panorama = PanoramaResult(
        query="Alice sentiment",
        all_nodes=[node],
        active_facts=["Alice joined the discussion."],
        historical_facts=["[2026-02-01 - 2026-02-10] Alice ignored the topic."],
        total_nodes=1,
        total_edges=1,
        active_count=1,
        historical_count=1,
        locale="en",
    )
    rendered_panorama = panorama.to_text()
    assert "## Panorama search results (future overview)" in rendered_panorama
    assert "### Statistics" in rendered_panorama
    assert "### [Current active facts] (original simulation output)" in rendered_panorama
    assert "### [Historical/expired facts] (change timeline record)" in rendered_panorama
    assert "### [Entities involved]" in rendered_panorama


def test_panorama_search_localizes_missing_historical_timestamps_in_english():
    app = Flask(__name__)
    service = _make_service()
    service._locale = lambda: "en"
    service.get_all_nodes = lambda graph_id: [
        NodeInfo(
            uuid="node-1",
            name="Alice",
            labels=["Entity", "Analyst"],
            summary="Tracks sentiment shifts.",
            attributes={},
            locale="en",
        )
    ]
    service.get_all_edges = lambda graph_id, include_temporal=True: [
        EdgeInfo(
            uuid="edge-1",
            name="influences",
            fact="Alice ignored the topic.",
            source_node_uuid="node-1",
            target_node_uuid="node-2",
            source_node_name="Alice",
            target_node_name="Bob",
            valid_at=None,
            invalid_at=None,
            expired_at="2026-03-10",
            locale="en",
        )
    ]

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.panorama_search("graph-1", "Alice")

    assert result.historical_facts == ["[Unknown - 2026-03-10] Alice ignored the topic."]
    assert "未知" not in result.to_text()


def test_insight_forge_localizes_default_entity_type_in_english():
    app = Flask(__name__)
    service = _make_service()
    service._locale = lambda: "en"
    service._generate_sub_queries = lambda **kwargs: ["Who shaped the narrative?"]
    service.search_graph = lambda **kwargs: SearchResult(
        facts=["Alice posted first."],
        edges=[
            {
                "source_node_uuid": "node-1",
                "target_node_uuid": "node-2",
                "name": "influences",
            }
        ],
        nodes=[],
        query=str(kwargs.get("query", "")),
        total_count=1,
        locale="en",
    )
    service.get_node_detail = lambda uuid, graph_id=None: NodeInfo(
        uuid=uuid,
        name="Alice" if uuid == "node-1" else "Bob",
        labels=["Entity"],
        summary="Context",
        attributes={},
        locale="en",
    )

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.insight_forge("graph-1", "Who shaped the narrative?", "Track policy sentiment")

    assert result.entity_insights[0]["type"] == "Entity"
    assert "实体" not in result.to_text()


def test_select_agents_for_interview_localizes_prompts_fallback_reasoning_and_logs_in_english(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    captured = {}
    fake_logger = FakeLogger()

    class FakeLLM:
        def chat_json(self, messages, temperature):
            captured["messages"] = messages
            raise RuntimeError("planner unavailable")

    service._llm_client = FakeLLM()
    profiles = [{"username": "alice", "bio": "", "interested_topics": []}]
    monkeypatch.setattr(zep_tools_module, "logger", fake_logger)

    with app.test_request_context(headers={"X-Locale": "en"}):
        selected, indices, reasoning = service._select_agents_for_interview(
            profiles=profiles,
            interview_requirement="Understand the reaction",
            simulation_requirement="",
            max_agents=1,
        )

    assert selected == profiles
    assert indices == [0]
    assert reasoning == "Used the default selection strategy"
    assert "You are an expert interview planner." in captured["messages"][0]["content"]
    assert "Write the `reasoning` field in natural English" in captured["messages"][0]["content"]
    assert "Simulation background:\nNot provided" in captured["messages"][1]["content"]
    assert '"profession": "Unknown"' in captured["messages"][1]["content"]
    assert any(
        "LLM agent selection failed; using the default selection: planner unavailable" in message
        for _, message in fake_logger.messages
    )


def test_generate_interview_questions_localizes_prompts_fallbacks_and_logs_in_english(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    captured = {}
    fake_logger = FakeLogger()

    class FakeLLM:
        def chat_json(self, messages, temperature):
            captured["messages"] = messages
            raise RuntimeError("question generator unavailable")

    service._llm_client = FakeLLM()
    monkeypatch.setattr(zep_tools_module, "logger", fake_logger)

    with app.test_request_context(headers={"X-Locale": "en"}):
        questions = service._generate_interview_questions(
            interview_requirement="the reaction",
            simulation_requirement="",
            selected_agents=[{"profession": None}],
        )

    assert questions == [
        "What is your perspective on the reaction?",
        "How does this affect you or the group you represent?",
        "What should be changed or improved in response?",
    ]
    assert "You are a professional interviewer." in captured["messages"][0]["content"]
    assert "Write every question in natural English" in captured["messages"][0]["content"]
    assert "Simulation background: Not provided" in captured["messages"][1]["content"]
    assert "Interviewee roles: Unknown" in captured["messages"][1]["content"]
    assert any(
        "Failed to generate interview questions: question generator unavailable" in message
        for _, message in fake_logger.messages
    )


def test_generate_sub_queries_localizes_prompts_and_fallbacks_in_english(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    captured = {}
    fake_logger = FakeLogger()

    class FakeLLM:
        def chat_json(self, messages, temperature):
            captured["messages"] = messages
            raise RuntimeError("sub-query planner unavailable")

    service._llm_client = FakeLLM()
    monkeypatch.setattr(zep_tools_module, "logger", fake_logger)

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service._generate_sub_queries(
            query="How will the narrative change?",
            simulation_requirement="Track public reaction over two weeks",
            report_context="Recent posts show rising skepticism.",
            max_queries=4,
        )

    assert result == [
        "How will the narrative change?",
        "Who are the main actors related to How will the narrative change?",
        "What are the causes and impacts of How will the narrative change?",
        "How is How will the narrative change likely to evolve?",
    ]
    assert "You are an expert question analyst." in captured["messages"][0]["content"]
    assert "Write every sub-question in natural English" in captured["messages"][0]["content"]
    assert "Simulation background:\nTrack public reaction over two weeks" in captured["messages"][1]["content"]
    assert "Report context:\nRecent posts show rising skepticism." in captured["messages"][1]["content"]
    assert "Break the following question into 4 focused sub-questions" in captured["messages"][1]["content"]
    assert "返回JSON格式" not in captured["messages"][0]["content"]
    assert any(
        "Failed to generate sub-queries: sub-query planner unavailable" in message
        for _, message in fake_logger.messages
    )


def test_generate_interview_summary_localizes_empty_fallback_copy_and_logs_in_english(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    fake_logger = FakeLogger()

    with app.test_request_context(headers={"X-Locale": "en"}):
        assert service._generate_interview_summary([], "Understand the reaction") == "No interviews were completed"

    class FakeLLM:
        def chat(self, messages, temperature, max_tokens):
            raise RuntimeError("summary generator unavailable")

    service._llm_client = FakeLLM()
    monkeypatch.setattr(zep_tools_module, "logger", fake_logger)
    interviews = [
        AgentInterview(
            agent_name="Alice",
            agent_role="Analyst",
            agent_bio="Tracks sentiment shifts.",
            question="What changed?",
            response="People became more cautious after the update.",
            locale="en",
        )
    ]

    with app.test_request_context(headers={"X-Locale": "en"}):
        summary = service._generate_interview_summary(interviews, "Understand the reaction")

    assert summary == "Interviewed 1 participants, including: Alice"
    assert any(
        "Failed to generate the interview summary: summary generator unavailable" in message
        for _, message in fake_logger.messages
    )


def test_load_agent_profiles_localizes_twitter_csv_unknown_profession_in_english():
    app = Flask(__name__)
    service = _make_service()
    simulation_id = "sim_csv_en"
    sim_dir = Path(__file__).resolve().parents[1] / "uploads" / "simulations" / simulation_id
    sim_dir.mkdir(parents=True)
    try:
        (sim_dir / "twitter_profiles.csv").write_text(
            "name,username,description,user_char\nAlice,alice,Tracks sentiment shifts.,Detailed persona\n",
            encoding="utf-8",
        )

        with app.test_request_context(headers={"X-Locale": "en"}):
            profiles = service._load_agent_profiles(simulation_id)

        assert profiles[0]["profession"] == "Unknown"
    finally:
        csv_path = sim_dir / "twitter_profiles.csv"
        if csv_path.exists():
            csv_path.unlink()
        if sim_dir.exists():
            sim_dir.rmdir()


def test_generate_interview_summary_uses_english_wrappers_in_english_mode():
    app = Flask(__name__)
    service = _make_service()
    captured = {}

    class FakeLLM:
        def chat(self, messages, temperature, max_tokens):
            captured["messages"] = messages
            return "Summary complete."

    service._llm_client = FakeLLM()
    interviews = [
        AgentInterview(
            agent_name="Alice",
            agent_role="Unknown",
            agent_bio="Tracks sentiment shifts.",
            question="What changed?",
            response="People became more cautious after the update.",
            locale="en",
        )
    ]

    with app.test_request_context(headers={"X-Locale": "en"}):
        summary = service._generate_interview_summary(interviews, "Understand the reaction")

    assert summary == "Summary complete."
    assert "Write the summary entirely in natural English" in captured["messages"][0]["content"]
    assert "translate it into fluent English before quoting or summarizing it" in captured["messages"][0]["content"]
    assert "Use standard English quotation marks when quoting interviewees directly" in captured["messages"][0]["content"]
    assert "[Alice (Unknown)]" in captured["messages"][1]["content"]
    assert "【Alice（Unknown）】" not in captured["messages"][1]["content"]
