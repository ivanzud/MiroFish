import sys
from types import SimpleNamespace
from types import ModuleType

fake_zep_cloud = ModuleType("zep_cloud")
fake_zep_client = ModuleType("zep_cloud.client")
fake_zep_client.Zep = object
fake_zep_cloud.client = fake_zep_client
fake_zep_cloud.__getattr__ = lambda name: object
sys.modules.setdefault("zep_cloud", fake_zep_cloud)
sys.modules.setdefault("zep_cloud.client", fake_zep_client)

from app.services.oasis_profile_generator import OasisProfileGenerator
from app.services.simulation_config_generator import SimulationConfigGenerator


def _make_response(content, finish_reason="stop"):
    return SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content=content),
                finish_reason=finish_reason,
            )
        ]
    )


def test_oasis_profile_generator_retries_without_response_format_on_unsupported_json_mode():
    create_calls = []

    class FakeCompletions:
        def create(self, **kwargs):
            create_calls.append(kwargs)
            if "response_format" in kwargs:
                raise RuntimeError("response_format json_object unsupported")
            return _make_response('Answer:\n{"bio":"Test bio","persona":"Test persona"}')

    generator = OasisProfileGenerator.__new__(OasisProfileGenerator)
    generator.model_name = "test-model"
    generator.client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

    result = generator._request_json_completion(
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.5,
    )

    assert result["content"] == '{"bio":"Test bio","persona":"Test persona"}'
    assert "response_format" in create_calls[0]
    assert "response_format" not in create_calls[1]


def test_simulation_config_generator_retries_without_response_format_on_unsupported_json_mode():
    create_calls = []

    class FakeCompletions:
        def create(self, **kwargs):
            create_calls.append(kwargs)
            if "response_format" in kwargs:
                raise RuntimeError("invalid parameter: response_format")
            return _make_response('```json\n{"time_config": {"total_simulation_hours": 12}}\n```')

    generator = SimulationConfigGenerator.__new__(SimulationConfigGenerator)
    generator.model_name = "test-model"
    generator.locale = "zh"
    generator.client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

    result = generator._request_json_completion(
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.6,
    )

    assert result["content"] == '{"time_config": {"total_simulation_hours": 12}}'
    assert "response_format" in create_calls[0]
    assert "response_format" not in create_calls[1]


def test_oasis_profile_generator_missing_api_key_mentions_openai_alias(monkeypatch):
    monkeypatch.setattr("app.services.oasis_profile_generator.Config.LLM_API_KEY", "")

    try:
        OasisProfileGenerator()
    except ValueError as exc:
        assert str(exc) == "LLM_API_KEY / OPENAI_API_KEY 未配置"
    else:
        raise AssertionError("expected ValueError when no API key is configured")


def test_oasis_profile_generator_english_prompts_switch_user_facing_language():
    generator = OasisProfileGenerator.__new__(OasisProfileGenerator)
    generator.locale = "en"

    system_prompt = generator._get_system_prompt(is_individual=True)
    user_prompt = generator._build_individual_persona_prompt(
        entity_name="Alice",
        entity_type="Player",
        entity_summary="A strategy-game enthusiast.",
        entity_attributes={"region": "US"},
        context="Forum comments and profile notes.",
    )

    assert "Write all user-facing text fields in English." in system_prompt
    assert "Use English for all user-facing fields except gender values" in user_prompt
    assert "country name in English" in user_prompt


def test_simulation_config_generator_missing_api_key_mentions_openai_alias(monkeypatch):
    monkeypatch.setattr("app.services.simulation_config_generator.Config.LLM_API_KEY", "")

    try:
        SimulationConfigGenerator()
    except ValueError as exc:
        assert str(exc) == "LLM_API_KEY / OPENAI_API_KEY 未配置"
    else:
        raise AssertionError("expected ValueError when no API key is configured")


def test_simulation_config_generator_missing_api_key_english_message(monkeypatch):
    monkeypatch.setattr("app.services.simulation_config_generator.Config.LLM_API_KEY", "")

    try:
        SimulationConfigGenerator(locale="en")
    except ValueError as exc:
        assert str(exc) == "LLM_API_KEY / OPENAI_API_KEY is not configured"
    else:
        raise AssertionError("expected ValueError when no API key is configured")


def test_simulation_config_generator_english_prompts_switch_user_facing_language():
    generator = SimulationConfigGenerator.__new__(SimulationConfigGenerator)
    generator.locale = "en"
    generator.TIME_CONFIG_CONTEXT_LENGTH = 10000
    generator.EVENT_CONFIG_CONTEXT_LENGTH = 8000
    generator.AGENT_SUMMARY_LENGTH = 300

    time_prompt, time_system = generator._build_time_config_prompt("## Simulation Requirement\nLaunch a new game.", 12)
    event_prompt, event_system = generator._build_event_config_prompt(
        context="## Simulation Requirement\nLaunch a new game.",
        simulation_requirement="Predict the target audience for a new strategy game.",
        type_info="- Student: Alice, Bob",
    )
    agent_prompt, agent_system = generator._build_agent_config_prompt(
        entity_list=[{"agent_id": 0, "entity_name": "Alice", "entity_type": "Student", "summary": "Strategy gamer"}],
        simulation_requirement="Predict the target audience for a new strategy game.",
    )

    assert "Generate a time-configuration JSON for this social simulation." in time_prompt
    assert "Return strict JSON only." in time_system
    assert "Generate the event configuration JSON for this simulation." in event_prompt
    assert "poster_type must match one of the available entity types exactly" in event_system
    assert "Generate social-media activity configurations for each entity below." in agent_prompt
    assert "social-media behavior analyst" in agent_system
