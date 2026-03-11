from __future__ import annotations

import sys
from types import ModuleType

from flask import Flask

fake_zep_cloud = ModuleType("zep_cloud")
fake_zep_client = ModuleType("zep_cloud.client")
fake_zep_client.Zep = object
fake_zep_cloud.client = fake_zep_client
fake_zep_cloud.__getattr__ = lambda name: object
sys.modules.setdefault("zep_cloud", fake_zep_cloud)
sys.modules.setdefault("zep_cloud.client", fake_zep_client)

from app.services import zep_tools as zep_tools_module
from app.services.zep_tools import ZepToolsService


def _make_service() -> ZepToolsService:
    return ZepToolsService.__new__(ZepToolsService)


def test_interview_agents_localizes_missing_profiles_summary_in_english():
    app = Flask(__name__)
    service = _make_service()
    service._load_agent_profiles = lambda simulation_id: []

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.interview_agents("sim_123", "Understand the reaction")

    assert result.summary == "No interviewable agent profiles were found"


def test_interview_agents_localizes_english_placeholders_and_text(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    service._load_agent_profiles = lambda simulation_id: [
        {
            "username": "alice",
            "realname": "Alice",
            "profession": "Analyst",
            "bio": "Tracks policy sentiment shifts.",
        }
    ]
    service._select_agents_for_interview = lambda **kwargs: (
        [service._load_agent_profiles("sim_123")[0]],
        [0],
        "Selected for domain relevance.",
    )
    service._generate_interview_questions = lambda **kwargs: ["What changed after the announcement?"]
    service._generate_interview_summary = lambda **kwargs: "The reaction was mixed but informed."

    monkeypatch.setattr(
        "app.services.simulation_runner.SimulationRunner.interview_agents_batch",
        lambda **kwargs: {
            "success": True,
            "interviews_count": 1,
            "result": {
                "results": {
                    "twitter_0": {"response": "People became more cautious after the update."},
                    "reddit_0": {"response": ""},
                }
            },
        },
    )

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.interview_agents("sim_123", "Understand the reaction")

    assert result.interviews[0].response == (
        "[Twitter answer]\n"
        "People became more cautious after the update.\n\n"
        "[Reddit answer]\n"
        "(no reply received from this platform)"
    )

    rendered = result.to_text()
    assert "## In-Depth Interview Report" in rendered
    assert "**Interview topic:** Understand the reaction" in rendered
    assert "_Bio: Tracks policy sentiment shifts._" in rendered
    assert "**Key quotes:**" in rendered or result.interviews[0].key_quotes == []


def test_interview_agents_localizes_api_failure_summary_in_english(monkeypatch):
    app = Flask(__name__)
    service = _make_service()
    service._load_agent_profiles = lambda simulation_id: [{"username": "alice", "bio": ""}]
    service._select_agents_for_interview = lambda **kwargs: ([{"username": "alice", "bio": ""}], [0], "")
    service._generate_interview_questions = lambda **kwargs: ["What happened?"]

    monkeypatch.setattr(
        "app.services.simulation_runner.SimulationRunner.interview_agents_batch",
        lambda **kwargs: {"success": False, "error": "env offline"},
    )

    with app.test_request_context(headers={"X-Locale": "en"}):
        result = service.interview_agents("sim_123", "Understand the reaction")

    assert (
        result.summary
        == "Interview API call failed: env offline. Check the OASIS simulation environment status."
    )
