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
