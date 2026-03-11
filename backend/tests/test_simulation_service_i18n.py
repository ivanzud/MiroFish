from __future__ import annotations

import builtins
from types import SimpleNamespace

from flask import Flask

from app.services.simulation_ipc import CommandType, SimulationIPCClient
from app.services.simulation_manager import SimulationManager, SimulationStatus
from app.services.simulation_runner import RunnerStatus, SimulationRunState, SimulationRunner
from app.utils.file_parser import FileParser


def test_file_parser_pdf_dependency_uses_english_request_locale(tmp_path, monkeypatch):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\n")

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "fitz":
            raise ImportError("fitz missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    app = Flask(__name__)
    with app.test_request_context(headers={"X-Locale": "en"}):
        try:
            FileParser.extract_text(str(pdf_path))
        except ImportError as exc:
            assert str(exc) == "Missing PDF parsing dependency PyMuPDF. Install it with `pip install PyMuPDF` first."
        else:
            raise AssertionError("expected ImportError for missing fitz")


def test_simulation_ipc_timeout_uses_english_request_locale(tmp_path):
    app = Flask(__name__)
    client = SimulationIPCClient(str(tmp_path))

    with app.test_request_context(headers={"X-Locale": "en"}):
        try:
            client.send_command(CommandType.CLOSE_ENV, {}, timeout=0.01, poll_interval=0.0)
        except TimeoutError as exc:
            assert str(exc) == "Timed out while waiting for the command response (0.01s)"
        else:
            raise AssertionError("expected TimeoutError when no IPC response arrives")


def test_prepare_simulation_empty_entities_uses_explicit_locale(tmp_path, monkeypatch):
    monkeypatch.setattr(SimulationManager, "SIMULATION_DATA_DIR", str(tmp_path))

    manager = SimulationManager()
    state = manager.create_simulation(
        project_id="project-1",
        graph_id="graph-1",
    )

    monkeypatch.setattr(
        "app.services.simulation_manager.ZepEntityReader",
        lambda: SimpleNamespace(
            filter_defined_entities=lambda **kwargs: SimpleNamespace(
                filtered_count=0,
                entity_types=set(),
                entities=[],
            )
        ),
    )

    result = manager.prepare_simulation(
        simulation_id=state.simulation_id,
        simulation_requirement="predict something",
        document_text="context",
        locale="en",
    )

    assert result.status == SimulationStatus.FAILED
    assert result.error == "No matching entities were found. Check that the graph was built correctly."


def test_stop_simulation_not_running_uses_english_request_locale(monkeypatch):
    app = Flask(__name__)

    monkeypatch.setattr(
        SimulationRunner,
        "get_run_state",
        classmethod(
            lambda cls, simulation_id: SimulationRunState(
                simulation_id=simulation_id,
                runner_status=RunnerStatus.STOPPED,
            )
        ),
    )

    with app.test_request_context(headers={"X-Locale": "en"}):
        try:
            SimulationRunner.stop_simulation("sim-123")
        except ValueError as exc:
            assert str(exc) == "The simulation is not running: sim-123, status=stopped"
        else:
            raise AssertionError("expected ValueError for a stopped simulation")


def test_interview_all_agents_missing_config_uses_english_request_locale(tmp_path, monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(SimulationRunner, "RUN_STATE_DIR", str(tmp_path))
    (tmp_path / "sim-123").mkdir()

    with app.test_request_context(headers={"X-Locale": "en"}):
        try:
            SimulationRunner.interview_all_agents("sim-123", "hello")
        except ValueError as exc:
            assert str(exc) == "The simulation config does not exist yet. Call /prepare first."
        else:
            raise AssertionError("expected ValueError for a missing simulation config")
