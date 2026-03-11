from __future__ import annotations

from types import SimpleNamespace

from flask import Flask

from app.api import report_bp
from app.services.report_agent import ReportStatus


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
        "app.api.report.ReportManager.get_report_by_simulation",
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


def test_missing_report_errors_are_localized(monkeypatch):
    app = create_report_test_app()
    client = app.test_client()

    monkeypatch.setattr("app.api.report.ReportManager.get_report", lambda report_id: None)

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
        "app.api.report.SimulationManager.get_simulation",
        lambda self, simulation_id: SimpleNamespace(project_id="proj_123", graph_id="graph_123"),
    )
    monkeypatch.setattr(
        "app.api.report.ProjectManager.get_project",
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
        "app.api.report.ReportManager._get_section_path",
        lambda report_id, section_index: str(missing_path),
    )

    response = client.get(
        "/api/report/report_123/section/1",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Section not found: section_01.md"
