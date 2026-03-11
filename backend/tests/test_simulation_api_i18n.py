from __future__ import annotations

import sys
from types import ModuleType

from flask import Flask

fake_zep_cloud = ModuleType("zep_cloud")
fake_zep_client = ModuleType("zep_cloud.client")
fake_zep_ontology = ModuleType("zep_cloud.external_clients.ontology")
fake_zep_cloud.client = fake_zep_client
fake_zep_cloud.__getattr__ = lambda name: object


class FakeZep:
    def __init__(self, *args, **kwargs):
        pass


fake_zep_client.Zep = FakeZep
fake_zep_ontology.EntityModel = object
fake_zep_ontology.EntityText = object
fake_zep_ontology.EdgeModel = object
sys.modules.setdefault("zep_cloud", fake_zep_cloud)
sys.modules.setdefault("zep_cloud.client", fake_zep_client)
sys.modules.setdefault("zep_cloud.external_clients.ontology", fake_zep_ontology)

from app.api import simulation_bp
from app.api import simulation as simulation_api


def create_simulation_test_app():
    app = Flask(__name__)
    app.register_blueprint(simulation_bp, url_prefix="/api/simulation")
    return app


def test_entities_requires_zep_key_in_english(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.Config, "ZEP_API_KEY", "")

    response = client.get(
        "/api/simulation/entities/graph_123",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "ZEP_API_KEY is not configured"


def test_entity_detail_missing_entity_is_localized(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.Config, "ZEP_API_KEY", "zep-key")

    class FakeReader:
        def get_entity_with_context(self, graph_id, entity_uuid):
            assert graph_id == "graph_123"
            assert entity_uuid == "entity_404"
            return None

    monkeypatch.setattr(simulation_api, "ZepEntityReader", FakeReader)

    response = client.get(
        "/api/simulation/entities/graph_123/entity_404",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Entity not found: entity_404"


def test_entities_by_type_requires_zep_key_in_english(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.Config, "ZEP_API_KEY", "")

    response = client.get(
        "/api/simulation/entities/graph_123/by-type/Person",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "ZEP_API_KEY is not configured"


def test_generate_profiles_requires_graph_id_in_english():
    app = create_simulation_test_app()
    client = app.test_client()

    response = client.post(
        "/api/simulation/generate-profiles",
        json={},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Please provide graph_id"


def test_prepare_status_not_started_is_localized(tmp_path, monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.Config, "OASIS_SIMULATION_DATA_DIR", str(tmp_path))

    response = client.post(
        "/api/simulation/prepare/status",
        json={"simulation_id": "sim_123"},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["status"] == "not_started"
    assert payload["message"] == "Preparation has not started yet. Call /api/simulation/prepare first."


def test_batch_interview_validation_is_localized(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.Config, "INTERVIEW_BATCH_TIMEOUT_SECONDS", 300)

    response = client.post(
        "/api/simulation/interview/batch",
        json={"simulation_id": "sim_123", "interviews": [{}]},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Interview item 1 is missing agent_id"


def test_env_status_message_is_localized(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.SimulationRunner, "check_env_alive", lambda simulation_id: True)
    monkeypatch.setattr(
        simulation_api.SimulationRunner,
        "get_env_status_detail",
        lambda simulation_id: {"twitter_available": True, "reddit_available": False},
    )

    response = client.post(
        "/api/simulation/env-status",
        json={"simulation_id": "sim_123"},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["message"] == "The environment is running and can accept interview commands"


def test_close_env_passes_locale_and_returns_localized_message(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    def fake_close(simulation_id, timeout, locale=None):
        assert simulation_id == "sim_123"
        assert timeout == 30
        assert locale == "en"
        return {"success": True, "message": "The environment is already closed"}

    monkeypatch.setattr(simulation_api.SimulationRunner, "close_simulation_env", fake_close)

    response = client.post(
        "/api/simulation/close-env",
        json={"simulation_id": "sim_123"},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["message"] == "The environment is already closed"
