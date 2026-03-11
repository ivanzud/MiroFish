from __future__ import annotations

import sys
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
    EdgeInfo,
    InsightForgeResult,
    NodeInfo,
    PanoramaResult,
    SearchResult,
    ZepToolsService,
)


def _make_service() -> ZepToolsService:
    return ZepToolsService.__new__(ZepToolsService)


def test_interview_agents_localizes_missing_profiles_summary_in_english():
    app = Flask(__name__)
    service = _make_service()
    service._load_agent_profiles = lambda simulation_id: []

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.interview_agents("sim_123", "Understand the reaction")

    assert result.summary == "No interviewable agent profiles were found"


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

    rendered = result.to_text()
    assert "## In-Depth Interview Report" in rendered
    assert "**Interview topic:** Understand the reaction" in rendered
    assert "_Bio: Tracks policy sentiment shifts._" in rendered
    assert "**Key quotes:**" in rendered or result.interviews[0].key_quotes == []


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
        locale="en",
    )
    assert node.to_text() == "Entity: Alice (Type: Analyst)\nSummary: Tracks sentiment shifts."

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
