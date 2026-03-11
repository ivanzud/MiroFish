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
