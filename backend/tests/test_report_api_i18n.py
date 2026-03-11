from __future__ import annotations

import sys
from types import SimpleNamespace
from types import ModuleType

from flask import Flask
from flask.wrappers import Request

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

from app.api import report as report_api
from app.api import report_bp
from app.services.report_agent import ReportStatus


class FakeLogger:
    def __init__(self):
        self.errors = []
        self.debugs = []

    def error(self, message):
        self.errors.append(message)

    def debug(self, message):
        self.debugs.append(message)


def create_report_test_app():
    app = Flask(__name__)
    app.register_blueprint(report_bp, url_prefix="/api/report")
    return app


def test_generate_report_requires_simulation_id_in_english():
    app = create_report_test_app()
    client = app.test_client()

    response = client.post(
        "/api/report/generate",
        json={},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Please provide simulation_id"


def test_generate_status_requires_task_or_simulation_in_english():
    app = create_report_test_app()
    client = app.test_client()

    response = client.post(
        "/api/report/generate/status",
        json={},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Please provide task_id or simulation_id"


def test_generate_status_completed_message_is_localized(monkeypatch):
    app = create_report_test_app()
    client = app.test_client()

    completed_report = SimpleNamespace(
        report_id="report_done",
        status=ReportStatus.COMPLETED,
    )
    monkeypatch.setattr(
        report_api.ReportManager,
        "get_report_by_simulation",
        lambda simulation_id: completed_report,
    )

    response = client.post(
        "/api/report/generate/status",
        json={"simulation_id": "sim_123"},
        headers={"X-Locale": "en"},
    )

    payload = response.get_json()
    assert response.status_code == 200
    assert payload["data"]["message"] == "The report has already been generated"
    assert payload["data"]["already_completed"] is True


def test_generate_report_start_message_is_localized(monkeypatch):
    app = create_report_test_app()
    client = app.test_client()

    report_api.TaskManager()._tasks.clear()

    class ImmediateThread:
        def __init__(self, target=None, args=(), kwargs=None, daemon=None):
            self._target = target
            self._args = args
            self._kwargs = kwargs or {}
            self.daemon = daemon

        def start(self):
            self._target(*self._args, **self._kwargs)

    monkeypatch.setattr(report_api.threading, "Thread", ImmediateThread)
    monkeypatch.setattr(
        report_api.SimulationManager,
        "get_simulation",
        lambda self, simulation_id: SimpleNamespace(
            project_id="proj_123",
            graph_id="graph_123",
        ),
    )
    monkeypatch.setattr(
        report_api.ReportManager,
        "get_report_by_simulation",
        lambda simulation_id: None,
    )
    monkeypatch.setattr(
        report_api.ProjectManager,
        "get_project",
        lambda project_id: SimpleNamespace(
            graph_id="graph_123",
            simulation_requirement="Need a report",
        ),
    )
    monkeypatch.setattr(
        report_api.ReportManager,
        "save_report",
        lambda report: None,
    )
    monkeypatch.setattr(
        report_api.ReportAgent,
        "__init__",
        lambda self, graph_id, simulation_id, simulation_requirement, locale: None,
    )
    monkeypatch.setattr(
        report_api.ReportAgent,
        "generate_report",
        lambda self, progress_callback, report_id: SimpleNamespace(
            report_id=report_id,
            status=ReportStatus.COMPLETED,
            error=None,
        ),
    )

    response = client.post(
        "/api/report/generate",
        json={"simulation_id": "sim_123"},
        headers={"X-Locale": "en"},
    )

    payload = response.get_json()["data"]
    assert response.status_code == 200
    assert payload["status"] == "generating"
    assert payload["message"] == "Report generation has started. Query /api/report/generate/status for progress."
    assert payload["already_generated"] is False


def test_generate_status_translates_task_progress_message(monkeypatch):
    app = create_report_test_app()
    client = app.test_client()

    monkeypatch.setattr(
        report_api.TaskManager,
        "get_task",
        lambda self, task_id: SimpleNamespace(
            to_dict=lambda: {
                "task_id": task_id,
                "status": "processing",
                "progress": 30,
                "message": "[planning] 正在生成报告大纲...",
            }
        ),
    )

    response = client.post(
        "/api/report/generate/status",
        json={"task_id": "task_123"},
        headers={"X-Locale": "en"},
    )

    payload = response.get_json()["data"]
    assert response.status_code == 200
    assert payload["message"] == "[Planning] Generating the report outline..."


def test_generate_status_translates_failed_task_progress_stage(monkeypatch):
    app = create_report_test_app()
    client = app.test_client()

    monkeypatch.setattr(
        report_api.TaskManager,
        "get_task",
        lambda self, task_id: SimpleNamespace(
            to_dict=lambda: {
                "task_id": task_id,
                "status": "failed",
                "progress": -1,
                "message": "[failed] 报告生成失败: boom",
            }
        ),
    )

    response = client.post(
        "/api/report/generate/status",
        json={"task_id": "task_123"},
        headers={"X-Locale": "en"},
    )

    payload = response.get_json()["data"]
    assert response.status_code == 200
    assert payload["message"] == "[Failed] 报告生成失败: boom"


def test_report_progress_message_is_localized(monkeypatch):
    app = create_report_test_app()
    client = app.test_client()

    monkeypatch.setattr(
        report_api.ReportManager,
        "get_progress",
        lambda report_id: {
            "status": "generating",
            "progress": 45,
            "message": "正在生成章节: Key Findings (1/3)",
        },
    )

    response = client.get(
        "/api/report/report_123/progress",
        headers={"X-Locale": "en"},
    )

    payload = response.get_json()["data"]
    assert response.status_code == 200
    assert payload["message"] == "Generating section: Key Findings (1/3)"


def test_missing_report_errors_are_localized(monkeypatch):
    app = create_report_test_app()
    client = app.test_client()

    monkeypatch.setattr(report_api.ReportManager, "get_report", lambda report_id: None)

    response = client.get(
        "/api/report/report_missing",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Report not found: report_missing"


def test_chat_requires_message_in_english(monkeypatch):
    app = create_report_test_app()
    client = app.test_client()

    monkeypatch.setattr(
        report_api.SimulationManager,
        "get_simulation",
        lambda self, simulation_id: SimpleNamespace(project_id="proj_123", graph_id="graph_123"),
    )
    monkeypatch.setattr(
        report_api.ProjectManager,
        "get_project",
        lambda project_id: SimpleNamespace(graph_id="graph_123", simulation_requirement="Need a report"),
    )

    response = client.post(
        "/api/report/chat",
        json={"simulation_id": "sim_123"},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Please provide message"


def test_missing_report_section_error_is_localized(monkeypatch, tmp_path):
    app = create_report_test_app()
    client = app.test_client()

    missing_path = tmp_path / "section_01.md"
    monkeypatch.setattr(
        report_api.ReportManager,
        "_get_section_path",
        lambda report_id, section_index: str(missing_path),
    )

    response = client.get(
        "/api/report/report_123/section/1",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Section not found: section_01.md"


def test_generate_status_exception_logs_english_context(monkeypatch):
    app = create_report_test_app()
    client = app.test_client()
    logger = FakeLogger()

    monkeypatch.setattr(report_api, "logger", logger)

    def boom(self, task_id):
        raise RuntimeError("status exploded")

    monkeypatch.setattr(report_api.TaskManager, "get_task", boom)

    response = client.post(
        "/api/report/generate/status",
        json={"task_id": "task_123"},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "status exploded"
    assert logger.errors == ["Failed to query task status: status exploded"]


def test_get_report_exception_logs_english_context(monkeypatch):
    app = create_report_test_app()
    client = app.test_client()
    logger = FakeLogger()

    monkeypatch.setattr(report_api, "logger", logger)

    def boom(report_id):
        raise RuntimeError("report exploded")

    monkeypatch.setattr(report_api.ReportManager, "get_report", boom)

    response = client.get(
        "/api/report/report_123",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "report exploded"
    assert logger.errors == ["Failed to fetch the report: report exploded"]
    assert logger.debugs


def test_generate_report_request_parse_failure_keeps_english_error_context(monkeypatch):
    app = create_report_test_app()
    client = app.test_client()
    logger = FakeLogger()

    monkeypatch.setattr(report_api, "logger", logger)

    original_get_json = Request.get_json

    def boom(self, *args, **kwargs):
        if self.path == "/api/report/generate":
            raise RuntimeError("bad report json")
        return original_get_json(self, *args, **kwargs)

    monkeypatch.setattr(Request, "get_json", boom)

    response = client.post(
        "/api/report/generate",
        data="{bad json",
        content_type="application/json",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "bad report json"
    assert logger.errors == ["Failed to start report generation: bad report json"]
    assert logger.debugs


def test_report_chat_request_parse_failure_keeps_english_error_context(monkeypatch):
    app = create_report_test_app()
    client = app.test_client()
    logger = FakeLogger()

    monkeypatch.setattr(report_api, "logger", logger)

    original_get_json = Request.get_json

    def boom(self, *args, **kwargs):
        if self.path == "/api/report/chat":
            raise RuntimeError("bad chat json")
        return original_get_json(self, *args, **kwargs)

    monkeypatch.setattr(Request, "get_json", boom)

    response = client.post(
        "/api/report/chat",
        data="{bad json",
        content_type="application/json",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "bad chat json"
    assert logger.errors == ["Report chat failed: bad chat json"]
    assert logger.debugs
