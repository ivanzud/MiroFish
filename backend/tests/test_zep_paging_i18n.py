import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

from flask import Flask


fake_zep_cloud = ModuleType("zep_cloud")
fake_zep_client = ModuleType("zep_cloud.client")
fake_zep_client.Zep = object
fake_zep_cloud.client = fake_zep_client
fake_zep_cloud.InternalServerError = RuntimeError
fake_zep_cloud.EpisodeData = object
fake_zep_cloud.EntityEdgeSourceTarget = object
fake_zep_cloud.__getattr__ = lambda name: object
sys.modules.setdefault("zep_cloud", fake_zep_cloud)
sys.modules.setdefault("zep_cloud.client", fake_zep_client)

from app.utils import zep_paging


def test_fetch_page_with_retry_logs_english_messages(monkeypatch):
    app = Flask(__name__)
    warning = Mock()
    error = Mock()
    sleep_calls: list[float] = []
    attempts = {"count": 0}

    def flaky_call():
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("gateway unavailable")
        return ["ok"]

    monkeypatch.setattr(zep_paging.logger, "warning", warning)
    monkeypatch.setattr(zep_paging.logger, "error", error)
    monkeypatch.setattr(zep_paging.time, "sleep", sleep_calls.append)

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = zep_paging._fetch_page_with_retry(
            flaky_call,
            max_retries=3,
            retry_delay=0.5,
            page_description="fetch nodes page 1 (graph=graph-1)",
        )

    assert result == ["ok"]
    assert sleep_calls == [0.5, 1.0]
    assert warning.call_args_list == [
        (
            (
                "Zep fetch nodes page 1 (graph=graph-1) failed on attempt 1: gateway unavailable, retrying in 0.5s...",
            ),
            {},
        ),
        (
            (
                "Zep fetch nodes page 1 (graph=graph-1) failed on attempt 2: gateway unavailable, retrying in 1.0s...",
            ),
            {},
        ),
    ]
    error.assert_not_called()


def test_fetch_page_with_retry_logs_english_final_failure(monkeypatch):
    error = Mock()

    monkeypatch.setattr(zep_paging.logger, "error", error)

    def always_fail():
        raise RuntimeError("still down")

    try:
        zep_paging._fetch_page_with_retry(
            always_fail,
            max_retries=1,
            retry_delay=0.5,
            page_description="fetch edges page 2 (graph=graph-2)",
            locale="en",
        )
    except RuntimeError as exc:
        assert str(exc) == "still down"
    else:
        raise AssertionError("expected RuntimeError")

    error.assert_called_once_with(
        "Zep fetch edges page 2 (graph=graph-2) still failed after 1 attempts: still down"
    )


def test_fetch_all_nodes_localizes_limit_and_missing_uuid_logs(monkeypatch):
    warning = Mock()
    client = SimpleNamespace(
        graph=SimpleNamespace(
            node=SimpleNamespace(
                get_by_graph_id=lambda *_args, **kwargs: [
                    SimpleNamespace(uuid_="node-1"),
                    SimpleNamespace(uuid_="node-2"),
                ]
                if "uuid_cursor" not in kwargs
                else [
                    SimpleNamespace(uuid_="node-3"),
                    SimpleNamespace(name="missing-uuid"),
                ]
            )
        )
    )

    monkeypatch.setattr(zep_paging.logger, "warning", warning)

    nodes = zep_paging.fetch_all_nodes(
        client,
        "graph-3",
        page_size=2,
        max_items=10,
        locale="en",
    )

    assert len(nodes) == 4
    assert warning.call_args_list == [
        (
            (
                "A node is missing the uuid field; stopping pagination after reading 4 nodes",
            ),
            {},
        )
    ]

    warning.reset_mock()

    limited_nodes = zep_paging.fetch_all_nodes(
        client,
        "graph-3",
        page_size=2,
        max_items=2,
        locale="en",
    )

    assert len(limited_nodes) == 2
    warning.assert_called_once_with(
        "Node count reached the limit (2); stopping pagination for graph graph-3"
    )


def test_fetch_all_edges_localizes_missing_uuid_logs(monkeypatch):
    warning = Mock()
    client = SimpleNamespace(
        graph=SimpleNamespace(
            edge=SimpleNamespace(
                get_by_graph_id=lambda *_args, **kwargs: [
                    SimpleNamespace(uuid_="edge-1"),
                    SimpleNamespace(uuid_="edge-2"),
                ]
                if "uuid_cursor" not in kwargs
                else [
                    SimpleNamespace(uuid_="edge-3"),
                    SimpleNamespace(name="missing-uuid"),
                ]
            )
        )
    )

    monkeypatch.setattr(zep_paging.logger, "warning", warning)

    edges = zep_paging.fetch_all_edges(
        client,
        "graph-4",
        page_size=2,
        locale="en",
    )

    assert len(edges) == 4
    warning.assert_called_once_with(
        "An edge is missing the uuid field; stopping pagination after reading 4 edges"
    )
