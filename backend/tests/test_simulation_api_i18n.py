from __future__ import annotations

import sys
from types import ModuleType

from flask import Flask

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

from app.api import simulation_bp
from app.api import simulation as simulation_api
from app.services.simulation_manager import SimulationState, SimulationStatus


def create_simulation_test_app():
    app = Flask(__name__)
    app.register_blueprint(simulation_bp, url_prefix="/api/simulation")
    return app


def test_entities_requires_zep_key_in_english(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.Config, "ZEP_API_KEY", "")

    response = client.get(
        "/api/simulation/entities/graph_123",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "ZEP_API_KEY is not configured"


def test_entity_detail_missing_entity_is_localized(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.Config, "ZEP_API_KEY", "zep-key")

    class FakeReader:
        def get_entity_with_context(self, graph_id, entity_uuid):
            assert graph_id == "graph_123"
            assert entity_uuid == "entity_404"
            return None

    monkeypatch.setattr(simulation_api, "ZepEntityReader", FakeReader)

    response = client.get(
        "/api/simulation/entities/graph_123/entity_404",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Entity not found: entity_404"


def test_entities_by_type_requires_zep_key_in_english(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.Config, "ZEP_API_KEY", "")

    response = client.get(
        "/api/simulation/entities/graph_123/by-type/Person",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "ZEP_API_KEY is not configured"


def test_generate_profiles_requires_graph_id_in_english():
    app = create_simulation_test_app()
    client = app.test_client()

    response = client.post(
        "/api/simulation/generate-profiles",
        json={},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Please provide graph_id"


def test_start_requires_simulation_id_in_english():
    app = create_simulation_test_app()
    client = app.test_client()

    response = client.post(
        "/api/simulation/start",
        json={},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Please provide simulation_id"


def test_stop_requires_simulation_id_in_english():
    app = create_simulation_test_app()
    client = app.test_client()

    response = client.post(
        "/api/simulation/stop",
        json={},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Please provide simulation_id"


def test_prepare_status_not_started_is_localized(tmp_path, monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.Config, "OASIS_SIMULATION_DATA_DIR", str(tmp_path))

    response = client.post(
        "/api/simulation/prepare/status",
        json={"simulation_id": "sim_123"},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["status"] == "not_started"
    assert payload["message"] == "Preparation has not started yet. Call /api/simulation/prepare first."


def test_prepare_status_translates_task_progress_payload(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    class FakeTask:
        def to_dict(self):
            return {
                "task_id": "task_123",
                "status": "processing",
                "progress": 35,
                "message": "[1/4] 读取图谱实体: 正在连接Zep图谱...",
                "progress_detail": {
                    "current_stage": "reading",
                    "current_stage_name": "读取图谱实体",
                    "item_description": "正在连接Zep图谱...",
                },
            }

    monkeypatch.setattr(
        "app.models.task.TaskManager.get_task",
        lambda self, task_id: FakeTask(),
    )

    response = client.post(
        "/api/simulation/prepare/status",
        json={"task_id": "task_123"},
        headers={"X-Locale": "en"},
    )

    payload = response.get_json()["data"]
    assert response.status_code == 200
    assert payload["message"] == "[1/4] Reading graph entities: Connecting to the Zep graph..."
    assert payload["progress_detail"]["current_stage_name"] == "Reading graph entities"
    assert payload["progress_detail"]["item_description"] == "Connecting to the Zep graph..."


def test_prepare_requires_existing_simulation_in_english(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.SimulationManager, "get_simulation", lambda self, simulation_id: None)

    response = client.post(
        "/api/simulation/prepare",
        json={"simulation_id": "sim_missing"},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 404
    assert response.get_json()["error"] == "Simulation not found: sim_missing"


def test_batch_interview_validation_is_localized(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.Config, "INTERVIEW_BATCH_TIMEOUT_SECONDS", 300)

    response = client.post(
        "/api/simulation/interview/batch",
        json={"simulation_id": "sim_123", "interviews": [{}]},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Interview item 1 is missing agent_id"


def test_env_status_message_is_localized(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(simulation_api.SimulationRunner, "check_env_alive", lambda simulation_id: True)
    monkeypatch.setattr(
        simulation_api.SimulationRunner,
        "get_env_status_detail",
        lambda simulation_id: {"twitter_available": True, "reddit_available": False},
    )

    response = client.post(
        "/api/simulation/env-status",
        json={"simulation_id": "sim_123"},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["message"] == "The environment is running and can accept interview commands"


def test_close_env_passes_locale_and_returns_localized_message(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    def fake_close(simulation_id, timeout, locale=None):
        assert simulation_id == "sim_123"
        assert timeout == 30
        assert locale == "en"
        return {"success": True, "message": "The environment is already closed"}

    monkeypatch.setattr(simulation_api.SimulationRunner, "close_simulation_env", fake_close)

    response = client.post(
        "/api/simulation/close-env",
        json={"simulation_id": "sim_123"},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["message"] == "The environment is already closed"


def test_interview_endpoint_uses_english_prompt_prefix(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    captured = {}

    monkeypatch.setattr(simulation_api.SimulationRunner, "check_env_alive", lambda simulation_id: True)

    def fake_interview_agent(simulation_id, agent_id, prompt, platform, timeout):
        captured.update(
            simulation_id=simulation_id,
            agent_id=agent_id,
            prompt=prompt,
            platform=platform,
            timeout=timeout,
        )
        return {"success": True, "response": "ok"}

    monkeypatch.setattr(simulation_api.SimulationRunner, "interview_agent", fake_interview_agent)

    response = client.post(
        "/api/simulation/interview",
        json={"simulation_id": "sim_123", "agent_id": 7, "prompt": "What changed?", "platform": "twitter"},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 200
    assert captured["prompt"].startswith(simulation_api.INTERVIEW_PROMPT_PREFIXES["en"])
    assert captured["prompt"].endswith("What changed?")


def test_batch_interview_endpoint_uses_english_prompt_prefix(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    captured = {}

    monkeypatch.setattr(simulation_api.Config, "INTERVIEW_BATCH_TIMEOUT_SECONDS", 300)
    monkeypatch.setattr(simulation_api.SimulationRunner, "check_env_alive", lambda simulation_id: True)

    def fake_interview_agents_batch(simulation_id, interviews, platform, timeout):
        captured.update(
            simulation_id=simulation_id,
            interviews=interviews,
            platform=platform,
            timeout=timeout,
        )
        return {"success": True, "results": {}}

    monkeypatch.setattr(simulation_api.SimulationRunner, "interview_agents_batch", fake_interview_agents_batch)

    response = client.post(
        "/api/simulation/interview/batch",
        json={
            "simulation_id": "sim_123",
            "interviews": [{"agent_id": 1, "prompt": "How are people reacting?"}],
        },
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 200
    assert captured["interviews"][0]["prompt"].startswith(simulation_api.INTERVIEW_PROMPT_PREFIXES["en"])
    assert captured["interviews"][0]["prompt"].endswith("How are people reacting?")


def test_interview_all_endpoint_uses_english_prompt_prefix(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    captured = {}

    monkeypatch.setattr(simulation_api.Config, "INTERVIEW_ALL_TIMEOUT_SECONDS", 300)
    monkeypatch.setattr(simulation_api.SimulationRunner, "check_env_alive", lambda simulation_id: True)

    def fake_interview_all_agents(simulation_id, prompt, platform, timeout):
        captured.update(
            simulation_id=simulation_id,
            prompt=prompt,
            platform=platform,
            timeout=timeout,
        )
        return {"success": True, "results": {}}

    monkeypatch.setattr(simulation_api.SimulationRunner, "interview_all_agents", fake_interview_all_agents)

    response = client.post(
        "/api/simulation/interview/all",
        json={"simulation_id": "sim_123", "prompt": "Summarize the mood."},
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 200
    assert captured["prompt"].startswith(simulation_api.INTERVIEW_PROMPT_PREFIXES["en"])
    assert captured["prompt"].endswith("Summarize the mood.")


def test_run_status_exception_logs_english_context(monkeypatch):
    app = create_simulation_test_app()
    client = app.test_client()

    class FakeLogger:
        def __init__(self):
            self.errors = []
            self.debugs = []

        def error(self, message):
            self.errors.append(message)

        def debug(self, message):
            self.debugs.append(message)

    logger = FakeLogger()
    monkeypatch.setattr(simulation_api, "logger", logger)

    def boom(simulation_id):
        raise RuntimeError("runner exploded")

    monkeypatch.setattr(simulation_api.SimulationRunner, "get_run_state", boom)

    response = client.get(
        "/api/simulation/sim_123/run-status",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 500
    assert response.get_json()["error"] == "runner exploded"
    assert logger.errors == ["Failed to get run status: runner exploded"]
    assert logger.debugs


def test_posts_missing_database_message_is_localized(monkeypatch, tmp_path):
    app = create_simulation_test_app()
    client = app.test_client()

    uploads_root = tmp_path / "uploads"
    simulations_root = uploads_root / "simulations"
    simulations_root.mkdir(parents=True)

    monkeypatch.setattr(simulation_api.os.path, "dirname", lambda _path: str(uploads_root / "placeholder"))

    response = client.get(
        "/api/simulation/sim_123/posts?platform=twitter",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 200
    payload = response.get_json()["data"]
    assert payload["count"] == 0
    assert payload["posts"] == []
    assert payload["message"] == (
        "The simulation database does not exist yet. "
        "The simulation may not have run for this platform."
    )


def test_ready_simulation_run_instructions_are_localized(monkeypatch, tmp_path):
    app = create_simulation_test_app()
    client = app.test_client()

    monkeypatch.setattr(
        simulation_api.SimulationManager,
        "SIMULATION_DATA_DIR",
        str(tmp_path),
    )

    ready_state = SimulationState(
        simulation_id="sim_ready",
        project_id="proj_123",
        graph_id="graph_123",
        status=SimulationStatus.READY,
    )

    monkeypatch.setattr(
        simulation_api.SimulationManager,
        "get_simulation",
        lambda self, simulation_id: ready_state,
    )

    response = client.get(
        "/api/simulation/sim_ready",
        headers={"X-Locale": "en"},
    )

    assert response.status_code == 200
    instructions = response.get_json()["data"]["run_instructions"]
    assert instructions["commands"]["parallel"].endswith(
        "run_parallel_simulation.py --config "
        f"{tmp_path}/sim_ready/simulation_config.json"
    )
    assert instructions["instructions"] == (
        "1. Activate the conda environment: conda activate MiroFish\n"
        f"2. Run the simulation (scripts are located in {instructions['scripts_dir']}):\n"
        f"   - Run Twitter only: python {instructions['scripts_dir']}/run_twitter_simulation.py --config {tmp_path}/sim_ready/simulation_config.json\n"
        f"   - Run Reddit only: python {instructions['scripts_dir']}/run_reddit_simulation.py --config {tmp_path}/sim_ready/simulation_config.json\n"
        f"   - Run both platforms in parallel: python {instructions['scripts_dir']}/run_parallel_simulation.py --config {tmp_path}/sim_ready/simulation_config.json"
    )
