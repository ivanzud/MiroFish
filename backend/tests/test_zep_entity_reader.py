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


class _FakeLogger:
    def __init__(self):
        self.messages = []

    def info(self, message, *args):
        self.messages.append(("info", message % args if args else message))

    def warning(self, message, *args):
        self.messages.append(("warning", message % args if args else message))

    def error(self, message, *args):
        self.messages.append(("error", message % args if args else message))


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


def test_filter_defined_entities_localizes_english_diagnostics(monkeypatch):
    reader = _build_reader()
    reader.locale = "en"
    fake_logger = _FakeLogger()
    nodes = [
        {
            "uuid": "node-short",
            "name": "特朗普",
            "labels": ["Entity", "Person"],
            "summary": "Short summary",
            "attributes": {},
        },
        {
            "uuid": "node-long",
            "name": "美国总统特朗普",
            "labels": ["Entity", "Person"],
            "summary": "Longer summary",
            "attributes": {},
        },
    ]
    monkeypatch.setattr("app.services.zep_entity_reader.logger", fake_logger)
    monkeypatch.setattr(reader, "get_all_nodes", lambda graph_id: nodes)
    monkeypatch.setattr(reader, "get_all_edges", lambda graph_id: [])

    result = reader.filter_defined_entities("graph-1", enrich_with_edges=False)

    assert result.filtered_count == 1
    messages = [message for _, message in fake_logger.messages]
    assert messages[0] == "Starting entity filtering for graph graph-1..."
    assert "Duplicate entity alias collapse completed: merged 1 duplicate candidate(s)" in messages
    assert "Entity filtering completed: total nodes 2, matched 1, entity types: {'Person'}" in messages
    assert all("筛选完成" not in message for message in messages)


def test_call_with_retry_localizes_english_retry_logs(monkeypatch):
    reader = _build_reader()
    reader.locale = "en"
    fake_logger = _FakeLogger()
    monkeypatch.setattr("app.services.zep_entity_reader.logger", fake_logger)
    sleep_calls = []
    monkeypatch.setattr("app.services.zep_entity_reader.time.sleep", sleep_calls.append)

    attempts = {"count": 0}

    def flaky():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("gateway unavailable")
        return "ok"

    result = reader._call_with_retry(flaky, "fetch node edges (node=abc12345...)", max_retries=3, initial_delay=0.5)

    assert result == "ok"
    assert sleep_calls == [0.5, 1.0]
    messages = fake_logger.messages
    assert messages == [
        (
            "warning",
            "Zep fetch node edges (node=abc12345...) failed on attempt 1: gateway unavailable, retrying in 0.5s...",
        ),
        (
            "warning",
            "Zep fetch node edges (node=abc12345...) failed on attempt 2: gateway unavailable, retrying in 1.0s...",
        ),
    ]


def test_get_node_edges_localizes_english_failure_message(monkeypatch):
    reader = _build_reader()
    reader.locale = "en"
    fake_logger = _FakeLogger()
    reader.client = SimpleNamespace(
        graph=SimpleNamespace(
            node=SimpleNamespace(
                get_entity_edges=lambda node_uuid: (_ for _ in ()).throw(RuntimeError("forbidden"))
            )
        )
    )
    monkeypatch.setattr("app.services.zep_entity_reader.logger", fake_logger)
    monkeypatch.setattr("app.services.zep_entity_reader.time.sleep", lambda *_: None)

    result = reader.get_node_edges("node-12345678")

    assert result == []
    assert fake_logger.messages[-1] == (
        "warning",
        "Failed to fetch edges for node node-12345678: forbidden",
    )


def test_get_entity_with_context_includes_alias_linked_relations(monkeypatch):
    reader = _build_reader()
    nodes = [
        {
            "uuid": "node-short",
            "name": "特朗普",
            "labels": ["Entity", "Person"],
            "summary": "",
            "attributes": {"source": "short"},
        },
        {
            "uuid": "node-long",
            "name": "美国总统特朗普",
            "labels": ["Entity", "Person"],
            "summary": "更完整的人物摘要。",
            "attributes": {"title": "president"},
        },
        {
            "uuid": "node-biden",
            "name": "拜登",
            "labels": ["Entity", "Person"],
            "summary": "另一个人物。",
            "attributes": {},
        },
    ]
    edges = [
        {
            "uuid": "edge-1",
            "name": "met_with",
            "fact": "美国总统特朗普会见了拜登",
            "source_node_uuid": "node-long",
            "target_node_uuid": "node-biden",
            "attributes": {},
        }
    ]

    reader.client = SimpleNamespace(
        graph=SimpleNamespace(
            node=SimpleNamespace(
                get=lambda uuid_: SimpleNamespace(
                    uuid_=uuid_,
                    name="特朗普",
                    labels=["Entity", "Person"],
                    summary="",
                    attributes={"source": "short"},
                )
            )
        )
    )
    monkeypatch.setattr(reader, "get_all_nodes", lambda graph_id: nodes)
    monkeypatch.setattr(reader, "get_all_edges", lambda graph_id: edges)

    entity = reader.get_entity_with_context("graph-1", "node-short")

    assert entity is not None
    assert entity.name == "美国总统特朗普"
    assert entity.summary == "更完整的人物摘要。"
    assert entity.attributes == {"source": "short", "title": "president"}
    assert entity.related_edges == [
        {
            "direction": "outgoing",
            "edge_name": "met_with",
            "fact": "美国总统特朗普会见了拜登",
            "target_node_uuid": "node-biden",
        }
    ]
    assert entity.related_nodes == [
        {
            "uuid": "node-biden",
            "name": "拜登",
            "labels": ["Entity", "Person"],
            "summary": "另一个人物。",
        }
    ]
