import importlib
import json
import sys
import types
from pathlib import Path
from unittest import mock


def _load_simulation_runner_module():
    if "zep_cloud" not in sys.modules:
        zep_cloud = types.ModuleType("zep_cloud")
        zep_cloud_client = types.ModuleType("zep_cloud.client")
        zep_cloud.EpisodeData = type("EpisodeData", (), {})
        zep_cloud.EntityEdgeSourceTarget = type("EntityEdgeSourceTarget", (), {})
        zep_cloud.InternalServerError = type("InternalServerError", (Exception,), {})
        zep_cloud.NotFoundError = type("NotFoundError", (Exception,), {})

        def _make_placeholder(name):
            return type(name, (), {})

        def _missing_attr(name):
            value = _make_placeholder(name)
            setattr(zep_cloud, name, value)
            return value

        zep_cloud.__getattr__ = _missing_attr
        zep_cloud_client.Zep = object
        zep_cloud.client = zep_cloud_client
        sys.modules["zep_cloud"] = zep_cloud
        sys.modules["zep_cloud.client"] = zep_cloud_client

    sys.modules.pop("app.services.simulation_runner", None)
    return importlib.import_module("app.services.simulation_runner")


def _write_actions(path, actions):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for action in actions:
            handle.write(json.dumps(action, ensure_ascii=False) + "\n")


def test_get_all_actions_supports_incremental_windows(tmp_path):
    module = _load_simulation_runner_module()
    runner = module.SimulationRunner
    original_run_state_dir = runner.RUN_STATE_DIR
    runner.RUN_STATE_DIR = str(tmp_path)

    try:
        simulation_dir = tmp_path / "sim-memory"
        _write_actions(
            simulation_dir / "twitter" / "actions.jsonl",
            [
                {
                    "round": 1,
                    "timestamp": "2026-03-11T08:00:00",
                    "agent_id": 1,
                    "agent_name": "Alice",
                    "action_type": "CREATE_POST",
                    "action_args": {"content": "first"},
                    "success": True,
                },
                {
                    "round": 2,
                    "timestamp": "2026-03-11T08:00:02",
                    "agent_id": 1,
                    "agent_name": "Alice",
                    "action_type": "CREATE_POST",
                    "action_args": {"content": "second"},
                    "success": True,
                },
            ],
        )
        _write_actions(
            simulation_dir / "reddit" / "actions.jsonl",
            [
                {
                    "round": 2,
                    "timestamp": "2026-03-11T08:00:01",
                    "agent_id": 7,
                    "agent_name": "Bob",
                    "action_type": "CREATE_COMMENT",
                    "action_args": {"content": "reply"},
                    "success": True,
                }
            ],
        )

        latest_two = runner.get_all_actions("sim-memory", limit=2)
        assert [action.timestamp for action in latest_two] == [
            "2026-03-11T08:00:02",
            "2026-03-11T08:00:01",
        ]

        incremental = runner.get_all_actions(
            "sim-memory",
            since_timestamp="2026-03-11T08:00:01",
        )
        assert [action.timestamp for action in incremental] == [
            "2026-03-11T08:00:02",
            "2026-03-11T08:00:01",
        ]
        assert [action.platform for action in incremental] == ["twitter", "reddit"]
    finally:
        runner.RUN_STATE_DIR = original_run_state_dir


def test_start_simulation_fails_fast_when_optional_runtime_is_missing(tmp_path):
    module = _load_simulation_runner_module()
    runner = module.SimulationRunner
    original_run_state_dir = runner.RUN_STATE_DIR
    original_scripts_dir = runner.SCRIPTS_DIR
    runner.RUN_STATE_DIR = str(tmp_path)
    runner.SCRIPTS_DIR = str(tmp_path)

    simulation_dir = tmp_path / "sim-missing-runtime"
    simulation_dir.mkdir()
    (simulation_dir / "simulation_config.json").write_text(
        json.dumps({"time_config": {"total_simulation_hours": 1, "minutes_per_round": 30}}),
        encoding="utf-8",
    )
    (tmp_path / "run_parallel_simulation.py").write_text("# placeholder", encoding="utf-8")

    try:
        with mock.patch.object(runner, "_simulation_dependencies_available", return_value=False):
            try:
                runner.start_simulation("sim-missing-runtime")
            except RuntimeError as exc:
                assert str(exc) == module.SIMULATION_DEPENDENCY_ERROR
            else:
                raise AssertionError("expected RuntimeError when optional simulation runtime is missing")
    finally:
        runner.RUN_STATE_DIR = original_run_state_dir
        runner.SCRIPTS_DIR = original_scripts_dir


def test_start_simulation_can_render_english_dependency_error(tmp_path):
    module = _load_simulation_runner_module()
    runner = module.SimulationRunner
    original_run_state_dir = runner.RUN_STATE_DIR
    original_scripts_dir = runner.SCRIPTS_DIR
    runner.RUN_STATE_DIR = str(tmp_path)
    runner.SCRIPTS_DIR = str(tmp_path)

    simulation_dir = tmp_path / "sim-missing-runtime-en"
    simulation_dir.mkdir()
    (simulation_dir / "simulation_config.json").write_text(
        json.dumps({"time_config": {"total_simulation_hours": 1, "minutes_per_round": 30}}),
        encoding="utf-8",
    )
    (tmp_path / "run_parallel_simulation.py").write_text("# placeholder", encoding="utf-8")

    try:
        with mock.patch.object(runner, "_simulation_dependencies_available", return_value=False):
            try:
                runner.start_simulation("sim-missing-runtime-en", locale="en")
            except RuntimeError as exc:
                assert (
                    str(exc)
                    == "The optional OASIS simulation runtime dependencies are not installed. Run `npm run setup:backend:simulation`, or `uv sync --extra simulation` inside the backend directory first."
                )
            else:
                raise AssertionError("expected RuntimeError when optional simulation runtime is missing")
    finally:
        runner.RUN_STATE_DIR = original_run_state_dir
        runner.SCRIPTS_DIR = original_scripts_dir


def test_start_simulation_passes_locale_to_runner_process(tmp_path):
    module = _load_simulation_runner_module()
    runner = module.SimulationRunner
    original_run_state_dir = runner.RUN_STATE_DIR
    original_scripts_dir = runner.SCRIPTS_DIR
    original_processes = runner._processes.copy()
    original_threads = runner._monitor_threads.copy()
    original_stdout_files = runner._stdout_files.copy()
    original_stderr_files = runner._stderr_files.copy()
    runner.RUN_STATE_DIR = str(tmp_path)
    runner.SCRIPTS_DIR = str(tmp_path)

    simulation_dir = tmp_path / "sim-locale"
    simulation_dir.mkdir()
    (simulation_dir / "simulation_config.json").write_text(
        json.dumps({"time_config": {"total_simulation_hours": 1, "minutes_per_round": 30}}),
        encoding="utf-8",
    )
    (tmp_path / "run_parallel_simulation.py").write_text("# placeholder", encoding="utf-8")

    popen_calls = {}

    class FakeProcess:
        pid = 4242

        def poll(self):
            return None

    class FakeThread:
        def __init__(self, target=None, args=None, daemon=None):
            self.target = target
            self.args = args
            self.daemon = daemon

        def start(self):
            return None

    def fake_popen(cmd, cwd, stdout, stderr, text, encoding, bufsize, env, start_new_session):
        popen_calls["env"] = env
        return FakeProcess()

    try:
        with mock.patch.object(runner, "_simulation_dependencies_available", return_value=True):
            with mock.patch.object(module.subprocess, "Popen", side_effect=fake_popen):
                with mock.patch.object(module.threading, "Thread", FakeThread):
                    state = runner.start_simulation("sim-locale", locale="en")

        assert state.locale == "en"
        assert popen_calls["env"]["MIROFISH_LOCALE"] == "en"
    finally:
        for handle in runner._stdout_files.values():
            try:
                handle.close()
            except Exception:
                pass
        runner.RUN_STATE_DIR = original_run_state_dir
        runner.SCRIPTS_DIR = original_scripts_dir
        runner._processes = original_processes
        runner._monitor_threads = original_threads
        runner._stdout_files = original_stdout_files
        runner._stderr_files = original_stderr_files


def test_start_simulation_passes_locale_to_graph_memory_updater(tmp_path):
    module = _load_simulation_runner_module()
    runner = module.SimulationRunner
    original_run_state_dir = runner.RUN_STATE_DIR
    original_scripts_dir = runner.SCRIPTS_DIR
    original_processes = runner._processes.copy()
    original_threads = runner._monitor_threads.copy()
    original_stdout_files = runner._stdout_files.copy()
    original_stderr_files = runner._stderr_files.copy()
    original_graph_memory_enabled = runner._graph_memory_enabled.copy()
    runner.RUN_STATE_DIR = str(tmp_path)
    runner.SCRIPTS_DIR = str(tmp_path)

    simulation_dir = tmp_path / "sim-graph-memory-locale"
    simulation_dir.mkdir()
    (simulation_dir / "simulation_config.json").write_text(
        json.dumps({"time_config": {"total_simulation_hours": 1, "minutes_per_round": 30}}),
        encoding="utf-8",
    )
    (tmp_path / "run_parallel_simulation.py").write_text("# placeholder", encoding="utf-8")

    class FakeProcess:
        pid = 4343

        def poll(self):
            return None

    class FakeThread:
        def __init__(self, target=None, args=None, daemon=None):
            self.target = target
            self.args = args
            self.daemon = daemon

        def start(self):
            return None

    updater_calls = {}

    def fake_popen(cmd, cwd, stdout, stderr, text, encoding, bufsize, env, start_new_session):
        return FakeProcess()

    def fake_create_updater(simulation_id, graph_id, locale="zh"):
        updater_calls["simulation_id"] = simulation_id
        updater_calls["graph_id"] = graph_id
        updater_calls["locale"] = locale
        return object()

    try:
        with mock.patch.object(runner, "_simulation_dependencies_available", return_value=True):
            with mock.patch.object(module.subprocess, "Popen", side_effect=fake_popen):
                with mock.patch.object(module.threading, "Thread", FakeThread):
                    with mock.patch.object(module.ZepGraphMemoryManager, "create_updater", side_effect=fake_create_updater):
                        state = runner.start_simulation(
                            "sim-graph-memory-locale",
                            locale="en",
                            enable_graph_memory_update=True,
                            graph_id="graph_123",
                        )

        assert state.locale == "en"
        assert updater_calls == {
            "simulation_id": "sim-graph-memory-locale",
            "graph_id": "graph_123",
            "locale": "en",
        }
    finally:
        for handle in runner._stdout_files.values():
            try:
                handle.close()
            except Exception:
                pass
        runner.RUN_STATE_DIR = original_run_state_dir
        runner.SCRIPTS_DIR = original_scripts_dir
        runner._processes = original_processes
        runner._monitor_threads = original_threads
        runner._stdout_files = original_stdout_files
        runner._stderr_files = original_stderr_files
        runner._graph_memory_enabled = original_graph_memory_enabled


def test_simulation_runtime_manifests_do_not_depend_on_camel_oasis():
    backend_dir = Path(__file__).resolve().parents[1]
    pyproject = (backend_dir / "pyproject.toml").read_text(encoding="utf-8")
    requirements = (backend_dir / "requirements-simulation.txt").read_text(encoding="utf-8")

    assert "camel-oasis" not in pyproject
    assert "camel-oasis" not in requirements
    assert "unstructured" not in requirements
    assert (backend_dir / "oasis" / "__init__.py").exists()


def test_format_process_exit_error_classifies_huggingface_network_failures():
    module = _load_simulation_runner_module()
    runner = module.SimulationRunner

    error = runner._format_process_exit_error(
        exit_code=1,
        details=(
            "requests.exceptions.ProxyError: HTTPSConnectionPool(host='huggingface.co', port=443): "
            "Max retries exceeded while calling hf_hub_download for sentence-transformers/all-MiniLM-L6-v2"
        ),
    )

    assert "HuggingFace" in error
    assert "huggingface.co" in error


def test_format_process_exit_error_localizes_huggingface_network_failures_in_english():
    module = _load_simulation_runner_module()
    runner = module.SimulationRunner

    error = runner._format_process_exit_error(
        exit_code=1,
        details=(
            "urllib3.exceptions.ConnectTimeoutError: HTTPSConnectionPool(host='huggingface.co', port=443) "
            "timed out while loading transformers model"
        ),
        locale="en",
    )

    assert (
        error
        == "The simulation run failed while downloading HuggingFace models or assets. "
        "Check that this machine can reach huggingface.co, then verify your proxy/VPN settings and retry."
    )


def test_format_process_exit_error_keeps_generic_message_for_other_failures():
    module = _load_simulation_runner_module()
    runner = module.SimulationRunner

    error = runner._format_process_exit_error(
        exit_code=2,
        details="ValueError: invalid simulation config",
        locale="en",
    )

    assert error == "Process exited with code 2. Error: ValueError: invalid simulation config"
