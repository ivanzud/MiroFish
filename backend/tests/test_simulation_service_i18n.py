from __future__ import annotations

import builtins
import csv
import json
from types import SimpleNamespace

from flask import Flask

from app.services import simulation_ipc as simulation_ipc_module
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


def test_simulation_ipc_logs_english_timeout_diagnostics(tmp_path, monkeypatch):
    app = Flask(__name__)
    fake_logger = SimpleNamespace(info=lambda *_: None, warning=lambda *_: None, error_messages=[])

    def _capture_error(message):
        fake_logger.error_messages.append(message)

    fake_logger.error = _capture_error
    monkeypatch.setattr(simulation_ipc_module, "logger", fake_logger)

    with app.test_request_context(headers={"X-Locale": "en"}):
        client = SimulationIPCClient(str(tmp_path))
        try:
            client.send_command(CommandType.CLOSE_ENV, {}, timeout=0.01, poll_interval=0.0)
        except TimeoutError:
            pass
        else:
            raise AssertionError("expected TimeoutError when no IPC response arrives")

    assert fake_logger.error_messages[-1] == "Timed out while waiting for the command response (0.01s)"


def test_simulation_ipc_logs_english_send_and_receive_messages(tmp_path, monkeypatch):
    app = Flask(__name__)

    class FakeLogger:
        def __init__(self):
            self.info_messages = []

        def info(self, message):
            self.info_messages.append(message)

        def warning(self, message):
            raise AssertionError(f"did not expect warning log: {message}")

        def error(self, message):
            raise AssertionError(f"did not expect error log: {message}")

    fake_logger = FakeLogger()
    monkeypatch.setattr(simulation_ipc_module, "logger", fake_logger)
    monkeypatch.setattr(simulation_ipc_module.uuid, "uuid4", lambda: "fixed-command-id")

    original_sleep = simulation_ipc_module.time.sleep

    def _write_response(_seconds):
        response_file = tmp_path / "ipc_responses" / "fixed-command-id.json"
        response_file.parent.mkdir(parents=True, exist_ok=True)
        response_file.write_text(
            json.dumps(
                {
                    "command_id": "fixed-command-id",
                    "status": "completed",
                    "result": {"ok": True},
                    "timestamp": "2026-03-11T18:00:00",
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        monkeypatch.setattr(simulation_ipc_module.time, "sleep", original_sleep)

    with app.test_request_context(headers={"X-Locale": "en"}):
        monkeypatch.setattr(simulation_ipc_module.time, "sleep", _write_response)
        client = SimulationIPCClient(str(tmp_path))
        response = client.send_command(CommandType.CLOSE_ENV, {}, timeout=0.1, poll_interval=0.01)

    assert response.status.value == "completed"
    assert fake_logger.info_messages == [
        "Sent IPC command: close_env, command_id=fixed-command-id",
        "Received IPC response: command_id=fixed-command-id, status=completed",
    ]


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


def test_prepare_simulation_progress_messages_use_explicit_locale(tmp_path, monkeypatch):
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
                filtered_count=2,
                entity_types={"Person"},
                entities=[{"id": "a"}, {"id": "b"}],
            )
        ),
    )

    class FakeProfileGenerator:
        def __init__(self, *args, **kwargs):
            pass

        def generate_profiles_from_entities(self, entities, progress_callback, **kwargs):
            progress_callback(1, 2, "Profile 1")
            progress_callback(2, 2, "Profile 2")
            return [{"name": "A"}, {"name": "B"}]

        def save_profiles(self, **kwargs):
            return None

    class FakeConfig:
        generation_reasoning = "done"

        def to_json(self):
            return "{}"

    class FakeConfigGenerator:
        def __init__(self, *args, **kwargs):
            pass

        def generate_config(self, **kwargs):
            return FakeConfig()

    monkeypatch.setattr("app.services.simulation_manager.OasisProfileGenerator", FakeProfileGenerator)
    monkeypatch.setattr("app.services.simulation_manager.SimulationConfigGenerator", FakeConfigGenerator)

    events = []

    manager.prepare_simulation(
        simulation_id=state.simulation_id,
        simulation_requirement="predict something",
        document_text="context",
        locale="en",
        progress_callback=lambda stage, progress, message, **kwargs: events.append((stage, progress, message, kwargs)),
    )

    messages = [message for _, _, message, _ in events]
    assert "Connecting to the Zep graph..." in messages
    assert "Reading node data..." in messages
    assert "Completed with 2 entities" in messages
    assert "Starting generation..." in messages
    assert "Saving profile files..." in messages
    assert "Completed with 2 profiles" in messages
    assert "Analyzing the simulation requirement..." in messages
    assert "Calling the LLM to generate the config..." in messages
    assert "Saving the config file..." in messages
    assert "Configuration generation completed" in messages


def test_get_profiles_falls_back_to_enabled_twitter_platform_and_reads_csv(tmp_path, monkeypatch):
    monkeypatch.setattr(SimulationManager, "SIMULATION_DATA_DIR", str(tmp_path))

    manager = SimulationManager()
    state = manager.create_simulation(
        project_id="project-1",
        graph_id="graph-1",
        enable_twitter=True,
        enable_reddit=False,
    )

    sim_dir = tmp_path / state.simulation_id
    with (sim_dir / "twitter_profiles.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["username", "platform", "bio"])
        writer.writeheader()
        writer.writerow({"username": "tw-user", "platform": "twitter", "bio": "Tracks breaking news"})

    profiles = manager.get_profiles(state.simulation_id, platform="reddit")

    assert profiles == [
        {
            "username": "tw-user",
            "platform": "twitter",
            "bio": "Tracks breaking news",
        }
    ]


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
