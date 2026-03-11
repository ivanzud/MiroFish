import importlib
import itertools
import sys
from types import ModuleType, SimpleNamespace

import pytest


@pytest.fixture
def graph_builder_module(monkeypatch):
    zep_cloud = ModuleType("zep_cloud")
    zep_cloud_client = ModuleType("zep_cloud.client")
    zep_cloud_ontology = ModuleType("zep_cloud.external_clients.ontology")

    class FakeEpisodeData:
        def __init__(self, data, type):
            self.data = data
            self.type = type

    class FakeEntityEdgeSourceTarget:
        def __init__(self, source, target):
            self.source = source
            self.target = target

    class FakeInternalServerError(Exception):
        pass

    class FakeZep:
        def __init__(self, api_key):
            self.api_key = api_key

    class FakeEntityModel:
        pass

    class FakeEntityText:
        pass

    class FakeEdgeModel:
        pass

    zep_cloud.EpisodeData = FakeEpisodeData
    zep_cloud.EntityEdgeSourceTarget = FakeEntityEdgeSourceTarget
    zep_cloud.InternalServerError = FakeInternalServerError
    zep_cloud_client.Zep = FakeZep
    zep_cloud_ontology.EntityModel = FakeEntityModel
    zep_cloud_ontology.EntityText = FakeEntityText
    zep_cloud_ontology.EdgeModel = FakeEdgeModel

    monkeypatch.setitem(sys.modules, "zep_cloud", zep_cloud)
    monkeypatch.setitem(sys.modules, "zep_cloud.client", zep_cloud_client)
    monkeypatch.setitem(sys.modules, "zep_cloud.external_clients.ontology", zep_cloud_ontology)
    monkeypatch.delitem(sys.modules, "app.services.graph_builder", raising=False)

    return importlib.import_module("app.services.graph_builder")


def build_service(graph_builder_module):
    service = graph_builder_module.GraphBuilderService.__new__(graph_builder_module.GraphBuilderService)
    service.client = SimpleNamespace(graph=SimpleNamespace())
    service.logger = SimpleNamespace(warning=lambda *args, **kwargs: None)
    service.locale = "zh"
    return service


def test_create_graph_retries_transient_zep_errors(graph_builder_module, monkeypatch):
    service = build_service(graph_builder_module)
    sleep_calls = []
    create_calls = []

    def fake_create(**kwargs):
        create_calls.append(kwargs)
        if len(create_calls) < 3:
            raise RuntimeError("429 Too Many Requests")

    service.client.graph.create = fake_create
    monkeypatch.setattr(graph_builder_module.time, "sleep", sleep_calls.append)

    graph_id = service.create_graph("retry-test", max_retries=3)

    assert graph_id.startswith("mirofish_")
    assert len(create_calls) == 3
    assert sleep_calls == [2.0, 4.0]


def test_create_graph_respects_retry_after_header(graph_builder_module, monkeypatch):
    service = build_service(graph_builder_module)
    sleep_calls = []
    create_calls = []

    class FakeRateLimitError(RuntimeError):
        status_code = 429

        def __init__(self):
            super().__init__("429 Too Many Requests")
            self.headers = {"Retry-After": "7"}

    def fake_create(**kwargs):
        create_calls.append(kwargs)
        if len(create_calls) == 1:
            raise FakeRateLimitError()

    service.client.graph.create = fake_create
    monkeypatch.setattr(graph_builder_module.time, "sleep", sleep_calls.append)

    graph_id = service.create_graph("retry-after", max_retries=3)

    assert graph_id.startswith("mirofish_")
    assert len(create_calls) == 2
    assert sleep_calls == [7.0]


def test_create_graph_respects_retry_after_text_hint(graph_builder_module, monkeypatch):
    service = build_service(graph_builder_module)
    sleep_calls = []
    create_calls = []

    def fake_create(**kwargs):
        create_calls.append(kwargs)
        if len(create_calls) == 1:
            raise RuntimeError("429 Too Many Requests; retry after 9 seconds")

    service.client.graph.create = fake_create
    monkeypatch.setattr(graph_builder_module.time, "sleep", sleep_calls.append)

    graph_id = service.create_graph("retry-after-text", max_retries=3)

    assert graph_id.startswith("mirofish_")
    assert len(create_calls) == 2
    assert sleep_calls == [9.0]


def test_create_graph_caps_retry_after_delay(graph_builder_module, monkeypatch):
    service = build_service(graph_builder_module)
    sleep_calls = []
    create_calls = []

    class FakeRateLimitError(RuntimeError):
        status_code = 429

        def __init__(self):
            super().__init__("429 Too Many Requests")
            self.headers = {"Retry-After": "600"}

    def fake_create(**kwargs):
        create_calls.append(kwargs)
        if len(create_calls) == 1:
            raise FakeRateLimitError()

    service.client.graph.create = fake_create
    monkeypatch.setattr(graph_builder_module.time, "sleep", sleep_calls.append)

    graph_id = service.create_graph("retry-after-cap", max_retries=3)

    assert graph_id.startswith("mirofish_")
    assert len(create_calls) == 2
    assert sleep_calls == [60.0]


def test_create_graph_does_not_retry_non_transient_errors(graph_builder_module, monkeypatch):
    service = build_service(graph_builder_module)
    sleep_calls = []
    create_calls = []

    def fake_create(**kwargs):
        create_calls.append(kwargs)
        raise ValueError("invalid graph payload")

    service.client.graph.create = fake_create
    monkeypatch.setattr(graph_builder_module.time, "sleep", sleep_calls.append)

    with pytest.raises(ValueError, match="invalid graph payload"):
        service.create_graph("no-retry", max_retries=3)

    assert len(create_calls) == 1
    assert sleep_calls == []


def test_add_text_batches_retries_failed_batch_once(graph_builder_module, monkeypatch):
    service = build_service(graph_builder_module)
    sleep_calls = []
    progress_updates = []
    add_batch_calls = []

    def fake_add_batch(**kwargs):
        add_batch_calls.append(kwargs)
        if len(add_batch_calls) == 1:
            raise RuntimeError("503 Service Unavailable")
        return [SimpleNamespace(uuid_="episode-1"), SimpleNamespace(uuid="episode-2")]

    service.client.graph.add_batch = fake_add_batch
    monkeypatch.setattr(graph_builder_module.time, "sleep", sleep_calls.append)

    episode_ids = service.add_text_batches(
        "graph-1",
        ["chunk-a", "chunk-b"],
        batch_size=2,
        progress_callback=lambda message, progress: progress_updates.append((message, progress)),
    )

    assert episode_ids == ["episode-1", "episode-2"]
    assert len(add_batch_calls) == 2
    assert sleep_calls == [2.0, 1]
    assert any("重试" in message for message, _ in progress_updates)


def test_add_text_batches_uses_english_progress_messages(graph_builder_module, monkeypatch):
    service = build_service(graph_builder_module)
    service.locale = "en"
    progress_updates = []
    sleep_calls = []

    service.client.graph.add_batch = lambda **kwargs: [SimpleNamespace(uuid_="episode-1")]
    monkeypatch.setattr(graph_builder_module.time, "sleep", sleep_calls.append)

    episode_ids = service.add_text_batches(
        "graph-1",
        ["chunk-a", "chunk-b"],
        batch_size=2,
        progress_callback=lambda message, progress: progress_updates.append((message, progress)),
    )

    assert episode_ids == ["episode-1"]
    assert sleep_calls == [1]
    assert progress_updates == [("Sending batch 1/1 (2 chunk(s))...", 1.0)]


def test_wait_for_episodes_uses_english_progress_messages(graph_builder_module, monkeypatch):
    service = build_service(graph_builder_module)
    service.locale = "en"
    progress_updates = []
    episode_state = {"episode-1": False}
    time_values = itertools.repeat(100.0)

    def fake_get(*, uuid_):
        processed = episode_state[uuid_]
        episode_state[uuid_] = True
        return SimpleNamespace(processed=processed)

    service.client.graph.episode = SimpleNamespace(get=fake_get)
    monkeypatch.setattr(graph_builder_module.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(graph_builder_module.time, "time", lambda: next(time_values))

    service._wait_for_episodes(
        ["episode-1"],
        progress_callback=lambda message, progress: progress_updates.append((message, progress)),
    )

    assert progress_updates == [
        ("Waiting for 1 text chunk(s) to finish processing...", 0),
        ("Zep processing... 0/1 complete, 1 pending (0s)", 0.0),
        ("Zep processing... 1/1 complete, 0 pending (0s)", 1.0),
        ("Processing completed: 1/1", 1.0),
    ]


def test_wait_for_episodes_without_entries_uses_english_progress_message(graph_builder_module):
    service = build_service(graph_builder_module)
    service.locale = "en"
    progress_updates = []

    service._wait_for_episodes(
        [],
        progress_callback=lambda message, progress: progress_updates.append((message, progress)),
    )

    assert progress_updates == [("No waiting required (no episodes)", 1.0)]


def test_set_ontology_accepts_string_attribute_definitions(graph_builder_module):
    service = build_service(graph_builder_module)
    captured = {}

    def fake_set_ontology(**kwargs):
        captured.update(kwargs)

    service.client.graph.set_ontology = fake_set_ontology

    service.set_ontology(
        "graph-1",
        {
            "entity_types": [
                {
                    "name": "Person",
                    "description": "Person entity",
                    "attributes": ["full_name", {"name": "role", "description": "Role"}],
                }
            ],
            "edge_types": [
                {
                    "name": "knows",
                    "description": "Knows edge",
                    "attributes": ["since", {"name": "context", "description": "Context"}],
                    "source_targets": [{"source": "Person", "target": "Person"}],
                }
            ],
        },
    )

    entities = captured["entities"]
    edges = captured["edges"]

    assert "Person" in entities
    assert entities["Person"].__annotations__["full_name"] is not None
    assert entities["Person"].__annotations__["role"] is not None

    edge_model, source_targets = edges["KNOWS"]
    assert edge_model.__name__ == "Knows"
    assert edge_model.__annotations__["since"] is not None
    assert edge_model.__annotations__["context"] is not None
    assert len(source_targets) == 1
    assert source_targets[0].source == "Person"
    assert source_targets[0].target == "Person"


def test_set_ontology_normalizes_entity_and_edge_type_names(graph_builder_module):
    service = build_service(graph_builder_module)
    captured = {}

    def fake_set_ontology(**kwargs):
        captured.update(kwargs)

    service.client.graph.set_ontology = fake_set_ontology

    service.set_ontology(
        "graph-1",
        {
            "entity_types": [
                {
                    "name": "university_student",
                    "description": "Student entity",
                    "attributes": [{"name": "major", "description": "Major"}],
                },
                {
                    "name": "ResearchLab",
                    "description": "Lab entity",
                    "attributes": [{"name": "focus_area", "description": "Focus"}],
                },
            ],
            "edge_types": [
                {
                    "name": "WorksFor",
                    "description": "Employment edge",
                    "attributes": [{"name": "start_date", "description": "Start"}],
                    "source_targets": [
                        {"source": "university_student", "target": "ResearchLab"}
                    ],
                }
            ],
        },
    )

    entities = captured["entities"]
    edges = captured["edges"]

    assert "UniversityStudent" in entities
    assert "ResearchLab" in entities
    assert entities["UniversityStudent"].__annotations__["major"] is not None
    assert entities["ResearchLab"].__annotations__["focus_area"] is not None

    edge_model, source_targets = edges["WORKS_FOR"]
    assert edge_model.__name__ == "WorksFor"
    assert edge_model.__annotations__["start_date"] is not None
    assert len(source_targets) == 1
    assert source_targets[0].source == "UniversityStudent"
    assert source_targets[0].target == "ResearchLab"


def test_get_graph_data_collapses_obvious_alias_duplicates_and_remaps_edges(graph_builder_module, monkeypatch):
    service = build_service(graph_builder_module)

    nodes = [
        SimpleNamespace(
            uuid_="node-short",
            name="特朗普",
            labels=["Entity", "人物"],
            summary="Short summary",
            attributes={"role": "candidate"},
            created_at="2026-01-01T00:00:00Z",
        ),
        SimpleNamespace(
            uuid_="node-long",
            name="美国总统特朗普",
            labels=["Entity", "人物"],
            summary="Longer summary with more context",
            attributes={"title": "President"},
            created_at="2026-01-02T00:00:00Z",
        ),
        SimpleNamespace(
            uuid_="node-other",
            name="白宫",
            labels=["Entity", "机构"],
            summary="",
            attributes={},
            created_at=None,
        ),
    ]
    edges = [
        SimpleNamespace(
            uuid_="edge-1",
            name="VISITS",
            fact="特朗普访问白宫",
            source_node_uuid="node-short",
            target_node_uuid="node-other",
            attributes={},
            created_at=None,
            valid_at=None,
            invalid_at=None,
            expired_at=None,
            episodes=[],
        ),
        SimpleNamespace(
            uuid_="edge-2",
            name="VISITS",
            fact="特朗普访问白宫",
            source_node_uuid="node-long",
            target_node_uuid="node-other",
            attributes={},
            created_at=None,
            valid_at=None,
            invalid_at=None,
            expired_at=None,
            episodes=[],
        ),
    ]

    monkeypatch.setattr(graph_builder_module, "fetch_all_nodes", lambda client, graph_id: nodes)
    monkeypatch.setattr(graph_builder_module, "fetch_all_edges", lambda client, graph_id: edges)

    result = service.get_graph_data("graph-1")

    assert result["node_count"] == 2
    assert result["edge_count"] == 1

    merged_trump = next(node for node in result["nodes"] if node["uuid"] == "node-short")
    assert merged_trump["name"] == "特朗普"
    assert merged_trump["alias_names"] == ["特朗普", "美国总统特朗普"]
    assert merged_trump["merged_node_uuids"] == ["node-short", "node-long"]
    assert merged_trump["attributes"] == {"title": "President", "role": "candidate"}
    assert merged_trump["summary"] == "Longer summary with more context"

    merged_edge = result["edges"][0]
    assert merged_edge["source_node_uuid"] == "node-short"
    assert merged_edge["source_node_name"] == "特朗普"
    assert merged_edge["target_node_uuid"] == "node-other"


def test_get_graph_data_keeps_distinct_nodes_separate(graph_builder_module, monkeypatch):
    service = build_service(graph_builder_module)

    nodes = [
        SimpleNamespace(
            uuid_="node-1",
            name="特朗普",
            labels=["Entity", "人物"],
            summary="",
            attributes={},
            created_at=None,
        ),
        SimpleNamespace(
            uuid_="node-2",
            name="特朗普大厦",
            labels=["Entity", "机构"],
            summary="",
            attributes={},
            created_at=None,
        ),
    ]

    monkeypatch.setattr(graph_builder_module, "fetch_all_nodes", lambda client, graph_id: nodes)
    monkeypatch.setattr(graph_builder_module, "fetch_all_edges", lambda client, graph_id: [])

    result = service.get_graph_data("graph-2")

    assert result["node_count"] == 2
    assert sorted(node["uuid"] for node in result["nodes"]) == ["node-1", "node-2"]


def test_format_user_facing_error_maps_zep_auth_failures(graph_builder_module):
    service = build_service(graph_builder_module)

    class FakeUnauthorizedError(Exception):
        status_code = 401

    error = FakeUnauthorizedError("401 unauthorized")

    assert "ZEP_API_KEY" in service.format_user_facing_error(error)


def test_format_user_facing_error_maps_embedded_traceback_auth_failures(graph_builder_module):
    service = build_service(graph_builder_module)

    error = RuntimeError(
        """Traceback (most recent call last):
  File "/app/backend/.venv/lib/python3.11/site-packages/zep_cloud/graph/raw_client.py", line 713, in create
    _response_json = _response.json()
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
401 unauthorized
"""
    )

    assert "ZEP_API_KEY" in service.format_user_facing_error(error)


def test_format_user_facing_error_keeps_generic_message(graph_builder_module):
    service = build_service(graph_builder_module)

    error = RuntimeError("invalid graph payload")

    assert service.format_user_facing_error(error) == "invalid graph payload"


def test_format_user_facing_error_strips_traceback_noise_from_generic_errors(graph_builder_module):
    service = build_service(graph_builder_module)

    error = RuntimeError(
        """Traceback (most recent call last):
  File "/app/backend/app/services/graph_builder.py", line 42, in create_graph
    raise RuntimeError("provider temporarily unavailable")
RuntimeError: provider temporarily unavailable
"""
    )

    assert service.format_user_facing_error(error) == "RuntimeError: provider temporarily unavailable"
