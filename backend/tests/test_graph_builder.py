import importlib
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

    edge_model, source_targets = edges["knows"]
    assert edge_model.__annotations__["since"] is not None
    assert edge_model.__annotations__["context"] is not None
    assert len(source_targets) == 1
    assert source_targets[0].source == "Person"
    assert source_targets[0].target == "Person"


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
