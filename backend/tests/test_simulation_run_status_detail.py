from __future__ import annotations

from app.api import simulation as simulation_api
from app.services.simulation_runner import AgentAction, RunnerStatus, SimulationRunState

from test_simulation_api_i18n import create_simulation_test_app


def test_run_status_detail_caps_recent_actions(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    run_state = SimulationRunState(
        simulation_id="sim_123",
        runner_status=RunnerStatus.RUNNING,
        current_round=3,
        total_rounds=12,
    )

    all_actions = [
        AgentAction(
            round_num=3,
            timestamp="2026-03-11T14:00:00",
            platform="twitter",
            agent_id=1,
            agent_name="Alice",
            action_type="CREATE_POST",
        )
    ]
    recent_actions = [
        AgentAction(
            round_num=3,
            timestamp=f"2026-03-11T14:00:{index:02d}",
            platform="reddit",
            agent_id=index,
            agent_name=f"Agent {index}",
            action_type="CREATE_COMMENT",
        )
        for index in range(250)
    ]

    monkeypatch.setattr(simulation_api.SimulationRunner, "get_run_state", lambda simulation_id: run_state)
    monkeypatch.setattr(simulation_api.SimulationRunner, "get_all_actions", lambda **kwargs: all_actions)
    monkeypatch.setattr(simulation_api.SimulationRunner, "get_actions", lambda **kwargs: recent_actions[: kwargs["limit"]])

    response = client.get("/api/simulation/sim_123/run-status/detail")

    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["returned_actions_count"] == 1
    assert len(payload["all_actions"]) == 1
    assert len(payload["recent_actions"]) == simulation_api.RUN_STATUS_DETAIL_RECENT_ACTIONS_LIMIT


def test_run_status_detail_exposes_waiting_diagnostics(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    run_state = SimulationRunState(
        simulation_id="sim_waiting",
        runner_status=RunnerStatus.RUNNING,
        current_round=0,
        total_rounds=12,
        process_pid=31337,
    )

    monkeypatch.setattr(simulation_api.SimulationRunner, "get_run_state", lambda simulation_id: run_state)
    monkeypatch.setattr(simulation_api.SimulationRunner, "get_all_actions", lambda **kwargs: [])
    monkeypatch.setattr(simulation_api.SimulationRunner, "get_actions", lambda **kwargs: [])
    monkeypatch.setattr(simulation_api.SimulationRunner, "_process_pid_is_alive", lambda process_pid: True)
    monkeypatch.setattr(
        simulation_api.SimulationRunner,
        "get_simulation_log_tail",
        lambda simulation_id: "booting simulation runtime\nloading agents",
    )

    response = client.get("/api/simulation/sim_waiting/run-status/detail")

    assert response.status_code == 200
    payload = response.get_json()["data"]
    diagnostics = payload["waiting_diagnostics"]
    assert diagnostics["waiting_for_actions"] is True
    assert diagnostics["process_alive"] is True
    assert diagnostics["process_pid"] == 31337
    assert diagnostics["latest_action_timestamp"] is None
    assert diagnostics["simulation_log_tail"] == "booting simulation runtime\nloading agents"
