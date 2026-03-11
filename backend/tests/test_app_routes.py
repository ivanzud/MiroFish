import sys
import types

from flask import Blueprint

from app import create_app


def test_root_and_health_endpoints_expose_backend_status(monkeypatch):
    api_module = types.ModuleType("app.api")
    services_module = types.ModuleType("app.services")
    simulation_runner_module = types.ModuleType("app.services.simulation_runner")

    api_module.graph_bp = Blueprint("graph", __name__)
    api_module.simulation_bp = Blueprint("simulation", __name__)
    api_module.report_bp = Blueprint("report", __name__)

    class FakeSimulationRunner:
        @staticmethod
        def register_cleanup():
            return None

    simulation_runner_module.SimulationRunner = FakeSimulationRunner
    services_module.simulation_runner = simulation_runner_module

    monkeypatch.setitem(sys.modules, "app.api", api_module)
    monkeypatch.setitem(sys.modules, "app.services", services_module)
    monkeypatch.setitem(sys.modules, "app.services.simulation_runner", simulation_runner_module)

    app = create_app()
    client = app.test_client()

    for path in ("/", "/health", "/healthz"):
        response = client.get(path)
        payload = response.get_json()

        assert response.status_code == 200
        assert payload["status"] == "ok"
        assert payload["service"] == "MiroFish Backend"
        assert payload["api_prefixes"] == [
            "/api/graph",
            "/api/simulation",
            "/api/report",
        ]
        assert payload["health_endpoint"] == "/health"


def test_api_cors_uses_env_backed_origin_list(monkeypatch):
    api_module = types.ModuleType("app.api")
    services_module = types.ModuleType("app.services")
    simulation_runner_module = types.ModuleType("app.services.simulation_runner")

    graph_bp = Blueprint("graph", __name__)
    api_module.graph_bp = graph_bp
    api_module.simulation_bp = Blueprint("simulation", __name__)
    api_module.report_bp = Blueprint("report", __name__)

    @graph_bp.route("/ping")
    def ping():
        return {"ok": True}

    class FakeSimulationRunner:
        @staticmethod
        def register_cleanup():
            return None

    simulation_runner_module.SimulationRunner = FakeSimulationRunner
    services_module.simulation_runner = simulation_runner_module

    monkeypatch.setitem(sys.modules, "app.api", api_module)
    monkeypatch.setitem(sys.modules, "app.services", services_module)
    monkeypatch.setitem(sys.modules, "app.services.simulation_runner", simulation_runner_module)

    class TestConfig:
        DEBUG = False
        JSON_AS_ASCII = False

        @staticmethod
        def get_cors_resources():
            return {
                "origins": ["https://app.example.test"],
                "methods": ["GET", "POST"],
                "allow_headers": ["Content-Type", "X-Locale"],
            }

    app = create_app(config_class=TestConfig)
    client = app.test_client()

    allowed = client.get("/api/graph/ping", headers={"Origin": "https://app.example.test"})
    blocked = client.get("/api/graph/ping", headers={"Origin": "https://other.example.test"})

    assert allowed.status_code == 200
    assert allowed.headers["Access-Control-Allow-Origin"] == "https://app.example.test"
    assert blocked.status_code == 200
    assert "Access-Control-Allow-Origin" not in blocked.headers
