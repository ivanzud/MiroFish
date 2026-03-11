import sys
import types

from flask import Blueprint

import app as app_module
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


class _FakeLogger:
    def __init__(self):
        self.info_messages = []
        self.debug_messages = []

    def info(self, message, *args, **kwargs):
        self.info_messages.append(message)

    def debug(self, message, *args, **kwargs):
        self.debug_messages.append(message)


def _install_fake_app_modules(monkeypatch):
    api_module = types.ModuleType("app.api")
    services_module = types.ModuleType("app.services")
    simulation_runner_module = types.ModuleType("app.services.simulation_runner")

    graph_bp = Blueprint("graph", __name__)
    api_module.graph_bp = graph_bp
    api_module.simulation_bp = Blueprint("simulation", __name__)
    api_module.report_bp = Blueprint("report", __name__)

    @graph_bp.route("/ping", methods=["POST"])
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


def test_create_app_localizes_startup_logs_from_env(monkeypatch):
    _install_fake_app_modules(monkeypatch)
    startup_logger = _FakeLogger()
    request_logger = _FakeLogger()

    monkeypatch.setenv("MIROFISH_LOCALE", "en")
    monkeypatch.setattr(app_module, "setup_logger", lambda name="mirofish": startup_logger)
    monkeypatch.setattr(app_module, "get_logger", lambda name="mirofish": request_logger)

    create_app()

    assert "MiroFish Backend is starting..." in startup_logger.info_messages
    assert "Registered the simulation process cleanup hook" in startup_logger.info_messages
    assert "MiroFish Backend startup completed" in startup_logger.info_messages


def test_request_logging_uses_request_locale(monkeypatch):
    _install_fake_app_modules(monkeypatch)
    startup_logger = _FakeLogger()
    request_logger = _FakeLogger()

    monkeypatch.setattr(app_module, "setup_logger", lambda name="mirofish": startup_logger)
    monkeypatch.setattr(app_module, "get_logger", lambda name="mirofish": request_logger)

    app = create_app()
    client = app.test_client()

    response = client.post(
        "/api/graph/ping",
        headers={"X-Locale": "en", "Content-Type": "application/json"},
        json={"hello": "world"},
    )

    assert response.status_code == 200
    assert "Request: POST /api/graph/ping" in request_logger.debug_messages
    assert "Request body: {'hello': 'world'}" in request_logger.debug_messages
    assert "Response: 200" in request_logger.debug_messages
