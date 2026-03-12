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


def test_simulation_ipc_timeout_uses_explicit_locale_without_request_context(tmp_path):
    client = SimulationIPCClient(str(tmp_path), locale="en")

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


def test_create_simulation_logs_use_english_request_locale(tmp_path, monkeypatch):
    monkeypatch.setattr(SimulationManager, "SIMULATION_DATA_DIR", str(tmp_path))

    info_messages = []
    monkeypatch.setattr(
        "app.services.simulation_manager.logger",
        SimpleNamespace(info=info_messages.append, error=lambda *_: None),
    )

    app = Flask(__name__)
    manager = SimulationManager()

    with app.test_request_context(headers={"X-Locale": "en"}):
        state = manager.create_simulation(
            project_id="project-1",
            graph_id="graph-1",
        )

    assert state.status == SimulationStatus.CREATED
    assert info_messages == [
        f"Created simulation: {state.simulation_id}, project=project-1, graph=graph-1"
    ]


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
            kwargs["progress_callback"](1, 4, "Generating time configuration...")
            kwargs["progress_callback"](2, 4, "Generating event config and hot topics...")
            kwargs["progress_callback"](3, 4, "Generating agent configs (1-2/2)...")
            kwargs["progress_callback"](4, 4, "Generating platform configuration...")
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
    assert "Generating time configuration..." in messages
    assert "Generating event config and hot topics..." in messages
    assert "Generating agent configs (1-2/2)..." in messages
    assert "Generating platform configuration..." in messages
    assert "Saving the config file..." in messages
    assert "Configuration generation completed" in messages

    generating_config_events = [(progress, message) for stage, progress, message, _ in events if stage == "generating_config"]
    assert generating_config_events == [
        (0, "Analyzing the simulation requirement..."),
        (30, "Calling the LLM to generate the config..."),
        (38, "Generating time configuration..."),
        (47, "Generating event config and hot topics..."),
        (56, "Generating agent configs (1-2/2)..."),
        (65, "Generating platform configuration..."),
        (70, "Saving the config file..."),
        (100, "Configuration generation completed"),
    ]


def test_prepare_simulation_logs_success_message_in_english(tmp_path, monkeypatch):
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

    info_messages = []
    monkeypatch.setattr("app.services.simulation_manager.OasisProfileGenerator", FakeProfileGenerator)
    monkeypatch.setattr("app.services.simulation_manager.SimulationConfigGenerator", FakeConfigGenerator)
    monkeypatch.setattr(
        "app.services.simulation_manager.logger",
        SimpleNamespace(info=info_messages.append, error=lambda *_: None),
    )

    manager.prepare_simulation(
        simulation_id=state.simulation_id,
        simulation_requirement="predict something",
        document_text="context",
        locale="en",
    )

    assert info_messages[-1] == (
        f"Simulation preparation completed: {state.simulation_id}, entities=2, profiles=2"
    )


def test_prepare_simulation_logs_failure_message_in_english(tmp_path, monkeypatch):
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
                filtered_count=1,
                entity_types={"Person"},
                entities=[{"id": "a"}],
            )
        ),
    )

    class FailingProfileGenerator:
        def __init__(self, *args, **kwargs):
            pass

        def generate_profiles_from_entities(self, **kwargs):
            raise RuntimeError("profile generation blew up")

    error_messages = []
    monkeypatch.setattr("app.services.simulation_manager.OasisProfileGenerator", FailingProfileGenerator)
    monkeypatch.setattr(
        "app.services.simulation_manager.logger",
        SimpleNamespace(info=lambda *_: None, error=error_messages.append),
    )

    try:
        manager.prepare_simulation(
            simulation_id=state.simulation_id,
            simulation_requirement="predict something",
            document_text="context",
            locale="en",
        )
    except RuntimeError as exc:
        assert str(exc) == "profile generation blew up"
    else:
        raise AssertionError("expected RuntimeError from profile generation")

    assert error_messages[0] == (
        f"Simulation preparation failed: {state.simulation_id}, error=profile generation blew up"
    )


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


def test_simulation_runner_interview_logs_use_english_request_locale(tmp_path, monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(SimulationRunner, "RUN_STATE_DIR", str(tmp_path))
    (tmp_path / "sim-123").mkdir()

    class FakeIPCClient:
        def __init__(self, sim_dir):
            assert sim_dir == str(tmp_path / "sim-123")

        def check_env_alive(self):
            return True

        def send_interview(self, **kwargs):
            return SimpleNamespace(
                status=SimpleNamespace(value="completed"),
                result={"ok": True},
                timestamp="2026-03-11T18:35:00Z",
            )

    info_messages = []
    monkeypatch.setattr("app.services.simulation_runner.SimulationIPCClient", FakeIPCClient)
    monkeypatch.setattr("app.services.simulation_runner.logger", SimpleNamespace(info=info_messages.append))

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = SimulationRunner.interview_agent("sim-123", 7, "hello", platform="twitter")

    assert result["success"] is True
    assert info_messages == [
        "Sent interview command: simulation_id=sim-123, agent_id=7, platform=twitter"
    ]


def test_simulation_runner_batch_and_global_logs_use_english_request_locale(tmp_path, monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(SimulationRunner, "RUN_STATE_DIR", str(tmp_path))
    sim_dir = tmp_path / "sim-123"
    sim_dir.mkdir()
    (sim_dir / "simulation_config.json").write_text(
        json.dumps({"agent_configs": [{"agent_id": 3}, {"agent_id": 9}]}, ensure_ascii=False),
        encoding="utf-8",
    )

    class FakeIPCClient:
        def __init__(self, current_sim_dir):
            assert current_sim_dir == str(sim_dir)

        def check_env_alive(self):
            return True

        def send_batch_interview(self, **kwargs):
            return SimpleNamespace(
                status=SimpleNamespace(value="completed"),
                result={"ok": True},
                timestamp="2026-03-11T18:35:00Z",
            )

    info_messages = []
    monkeypatch.setattr("app.services.simulation_runner.SimulationIPCClient", FakeIPCClient)
    monkeypatch.setattr("app.services.simulation_runner.logger", SimpleNamespace(info=info_messages.append))

    with app.test_request_context(headers={"X-Locale": "en"}):
        batch_result = SimulationRunner.interview_agents_batch(
            "sim-123",
            interviews=[{"agent_id": 1, "prompt": "a"}, {"agent_id": 2, "prompt": "b"}],
            platform="reddit",
        )
        global_result = SimulationRunner.interview_all_agents("sim-123", "hello", platform="twitter")

    assert batch_result["success"] is True
    assert global_result["success"] is True
    assert info_messages == [
        "Sent batch interview command: simulation_id=sim-123, count=2, platform=reddit",
        "Sent global interview command: simulation_id=sim-123, agent_count=2, platform=twitter",
        "Sent batch interview command: simulation_id=sim-123, count=2, platform=twitter",
    ]


def test_simulation_runner_close_env_log_uses_explicit_locale(tmp_path, monkeypatch):
    monkeypatch.setattr(SimulationRunner, "RUN_STATE_DIR", str(tmp_path))
    (tmp_path / "sim-123").mkdir()

    class FakeIPCClient:
        def __init__(self, sim_dir):
            assert sim_dir == str(tmp_path / "sim-123")

        def check_env_alive(self):
            return True

        def send_close_env(self, **kwargs):
            return SimpleNamespace(
                status=SimpleNamespace(value="completed"),
                result={"ok": True},
                timestamp="2026-03-11T18:35:00Z",
            )

    info_messages = []
    monkeypatch.setattr("app.services.simulation_runner.SimulationIPCClient", FakeIPCClient)
    monkeypatch.setattr("app.services.simulation_runner.logger", SimpleNamespace(info=info_messages.append))

    result = SimulationRunner.close_simulation_env("sim-123", locale="en")

    assert result["success"] is True
    assert info_messages == [
        "Sent close-environment command: simulation_id=sim-123"
    ]


def test_get_run_state_logs_english_load_failure(tmp_path, monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(SimulationRunner, "RUN_STATE_DIR", str(tmp_path))
    sim_dir = tmp_path / "sim-123"
    sim_dir.mkdir()
    (sim_dir / "run_state.json").write_text("{not-json", encoding="utf-8")
    SimulationRunner._run_states.pop("sim-123", None)

    error_messages = []
    monkeypatch.setattr("app.services.simulation_runner.logger", SimpleNamespace(error=error_messages.append))

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = SimulationRunner.get_run_state("sim-123")

    assert result is None
    assert error_messages == [
        "Failed to load the run state: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)"
    ]


def test_get_interview_history_logs_english_read_failure(tmp_path, monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(SimulationRunner, "RUN_STATE_DIR", str(tmp_path))
    sim_dir = tmp_path / "sim-123" / "twitter"
    sim_dir.mkdir(parents=True)
    (tmp_path / "sim-123" / "twitter_simulation.db").write_bytes(b"")

    error_messages = []
    monkeypatch.setattr(
        "app.services.simulation_runner.logger",
        SimpleNamespace(error=error_messages.append),
    )

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = SimulationRunner.get_interview_history("sim-123", platform="twitter", limit=5)

    assert result == []
    assert error_messages == [
        "Failed to read interview history (twitter): no such table: trace"
    ]
