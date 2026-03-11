import sys
from types import ModuleType, SimpleNamespace


fake_zep_cloud = ModuleType("zep_cloud")
fake_zep_client = ModuleType("zep_cloud.client")
fake_zep_client.Zep = object
fake_zep_cloud.client = fake_zep_client
fake_zep_cloud.__getattr__ = lambda name: object
sys.modules.setdefault("zep_cloud", fake_zep_cloud)
sys.modules.setdefault("zep_cloud.client", fake_zep_client)

from app.services.zep_entity_reader import ZepEntityReader


def _build_reader():
    reader = ZepEntityReader.__new__(ZepEntityReader)
    reader.client = SimpleNamespace()
    return reader


def test_filter_defined_entities_collapses_title_prefixed_duplicate_people(monkeypatch):
    reader = _build_reader()
    nodes = [
        {
            "uuid": "node-short",
            "name": "特朗普",
            "labels": ["Entity", "Person"],
            "summary": "美国前总统。",
            "attributes": {"source": "short"},
        },
        {
            "uuid": "node-long",
            "name": "美国总统特朗普",
            "labels": ["Entity", "Person"],
            "summary": "在新闻事件中的核心人物，带有更长摘要。",
            "attributes": {"title": "president"},
        },
    ]
    edges = [
        {
            "uuid": "edge-1",
            "name": "mentions",
            "fact": "与选举相关",
            "source_node_uuid": "node-short",
            "target_node_uuid": "node-long",
            "attributes": {},
        }
    ]

    monkeypatch.setattr(reader, "get_all_nodes", lambda graph_id: nodes)
    monkeypatch.setattr(reader, "get_all_edges", lambda graph_id: edges)

    result = reader.filter_defined_entities("graph-1", enrich_with_edges=True)

    assert result.filtered_count == 1
    entity = result.entities[0]
    assert entity.get_entity_type() == "Person"
    assert entity.name == "美国总统特朗普"
    assert entity.summary == "在新闻事件中的核心人物，带有更长摘要。"
    assert entity.attributes == {"source": "short", "title": "president"}
    assert len(entity.related_edges) == 1
    assert any(node["name"] == "美国总统特朗普" for node in entity.related_nodes)


def test_filter_defined_entities_keeps_distinct_people_separate(monkeypatch):
    reader = _build_reader()
    nodes = [
        {
            "uuid": "node-1",
            "name": "特朗普",
            "labels": ["Entity", "Person"],
            "summary": "人物 A",
            "attributes": {},
        },
        {
            "uuid": "node-2",
            "name": "拜登",
            "labels": ["Entity", "Person"],
            "summary": "人物 B",
            "attributes": {},
        },
    ]

    monkeypatch.setattr(reader, "get_all_nodes", lambda graph_id: nodes)
    monkeypatch.setattr(reader, "get_all_edges", lambda graph_id: [])

    result = reader.filter_defined_entities("graph-1", enrich_with_edges=False)

    assert result.filtered_count == 2
    assert [entity.name for entity in result.entities] == ["特朗普", "拜登"]
