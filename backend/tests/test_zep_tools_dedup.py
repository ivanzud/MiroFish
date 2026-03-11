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

from app.services.zep_tools import NodeInfo, SearchResult, ZepToolsService


def _make_service() -> ZepToolsService:
    return ZepToolsService.__new__(ZepToolsService)


def test_get_entities_by_type_collapses_obvious_alias_duplicates():
    service = _make_service()
    service.get_all_nodes = lambda graph_id: [
        NodeInfo(
            uuid="node-short",
            name="特朗普",
            labels=["Entity", "PublicFigure"],
            summary="",
            attributes={},
            locale="en",
        ),
        NodeInfo(
            uuid="node-long",
            name="美国总统特朗普",
            labels=["Entity", "PublicFigure"],
            summary="Former president and recurring political actor.",
            attributes={"country": "US"},
            locale="en",
        ),
        NodeInfo(
            uuid="node-biden",
            name="拜登",
            labels=["Entity", "PublicFigure"],
            summary="",
            attributes={},
            locale="en",
        ),
    ]

    result = service.get_entities_by_type("graph-1", "PublicFigure")

    assert [node.name for node in result] == ["特朗普", "拜登"]
    assert result[0].summary == "Former president and recurring political actor."
    assert result[0].attributes == {"country": "US"}


def test_panorama_search_reports_deduplicated_entity_count():
    app = Flask(__name__)
    service = _make_service()
    service.get_all_nodes = lambda graph_id: [
        NodeInfo(
            uuid="node-short",
            name="特朗普",
            labels=["Entity", "PublicFigure"],
            summary="",
            attributes={},
            locale="en",
        ),
        NodeInfo(
            uuid="node-long",
            name="美国总统特朗普",
            labels=["Entity", "PublicFigure"],
            summary="Former president and recurring political actor.",
            attributes={"country": "US"},
            locale="en",
        ),
    ]
    service.get_all_edges = lambda graph_id, include_temporal=True: []
    service._locale = lambda: "en"

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.panorama_search("graph-1", "trump")

    assert result.total_nodes == 1
    assert [node.name for node in result.all_nodes] == ["特朗普"]
    assert result.to_text().count("**特朗普**") == 1


def test_insight_forge_collapses_duplicate_aliases_in_entities_and_relationships():
    app = Flask(__name__)
    service = _make_service()
    service._locale = lambda: "en"
    service._generate_sub_queries = lambda **kwargs: ["trump reaction"]
    service.search_graph = lambda **kwargs: SearchResult(
        facts=[
            "特朗普 criticized the proposal.",
            "美国总统特朗普 met with advisers at the White House.",
        ],
        edges=[
            {
                "source_node_uuid": "node-short",
                "target_node_uuid": "node-wh",
                "name": "MENTIONS",
            },
            {
                "source_node_uuid": "node-long",
                "target_node_uuid": "node-wh",
                "name": "MENTIONS",
            },
        ],
        nodes=[],
        query=str(kwargs.get("query", "")),
        total_count=2,
        locale="en",
    )
    node_lookup = {
        "node-short": NodeInfo(
            uuid="node-short",
            name="特朗普",
            labels=["Entity", "PublicFigure"],
            summary="",
            attributes={},
            locale="en",
        ),
        "node-long": NodeInfo(
            uuid="node-long",
            name="美国总统特朗普",
            labels=["Entity", "PublicFigure"],
            summary="Former president and recurring political actor.",
            attributes={"country": "US"},
            locale="en",
        ),
        "node-wh": NodeInfo(
            uuid="node-wh",
            name="白宫",
            labels=["Entity", "Organization"],
            summary="Executive residence and workplace.",
            attributes={},
            locale="en",
        ),
    }
    service.get_node_detail = lambda uuid: node_lookup[uuid]

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.insight_forge("graph-1", "How did Trump react?", "Political crisis")

    assert result.total_entities == 2
    assert [entity["name"] for entity in result.entity_insights] == ["白宫", "特朗普"]
    assert "特朗普 criticized the proposal." in result.entity_insights[1]["related_facts"]
    assert "美国总统特朗普 met with advisers at the White House." in result.entity_insights[1]["related_facts"]
    assert result.total_relationships == 1
    assert result.relationship_chains == ["特朗普 --[MENTIONS]--> 白宫"]
