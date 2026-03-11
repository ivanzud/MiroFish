from __future__ import annotations

from flask import Flask

from app.api import simulation_bp


def create_simulation_test_app():
    app = Flask(__name__)
    app.register_blueprint(simulation_bp, url_prefix="/api/simulation")
    return app


def test_entities_requires_zep_key_in_english(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr("app.api.simulation.Config.ZEP_API_KEY", "")

    response = client.get(
        "/api/simulation/entities/graph_123",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "ZEP_API_KEY is not configured"


def test_entity_detail_missing_entity_is_localized(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr("app.api.simulation.Config.ZEP_API_KEY", "zep-key")

    class FakeReader:
        def get_entity_with_context(self, graph_id, entity_uuid):
            assert graph_id == "graph_123"
            assert entity_uuid == "entity_404"
            return None

    monkeypatch.setattr("app.api.simulation.ZepEntityReader", FakeReader)

    response = client.get(
        "/api/simulation/entities/graph_123/entity_404",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Entity not found: entity_404"


def test_entities_by_type_requires_zep_key_in_english(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr("app.api.simulation.Config.ZEP_API_KEY", "")

    response = client.get(
        "/api/simulation/entities/graph_123/by-type/Person",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "ZEP_API_KEY is not configured"
