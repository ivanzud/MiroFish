import importlib
import json
import sys
import types


def _load_simulation_runner_module():
    if "zep_cloud" not in sys.modules:
        zep_cloud = types.ModuleType("zep_cloud")
        zep_cloud_client = types.ModuleType("zep_cloud.client")
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
