import sys
import json
from types import SimpleNamespace
from types import ModuleType

fake_zep_cloud = ModuleType("zep_cloud")
fake_zep_client = ModuleType("zep_cloud.client")
fake_zep_client.Zep = object
fake_zep_cloud.client = fake_zep_client
fake_zep_cloud.__getattr__ = lambda name: object
sys.modules.setdefault("zep_cloud", fake_zep_cloud)
sys.modules.setdefault("zep_cloud.client", fake_zep_client)

from app.services.oasis_profile_generator import OasisAgentProfile, OasisProfileGenerator
from app.services.graph_builder import GraphBuilderService
from app.services import simulation_config_generator as simulation_config_generator_module
from app.services.simulation_config_generator import SimulationConfigGenerator
from app.services.zep_entity_reader import ZepEntityReader
from app.services.zep_graph_memory_updater import AgentActivity, ZepGraphMemoryUpdater
from app.services.zep_tools import ZepToolsService


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


def test_oasis_profile_generator_english_rule_based_group_profile_uses_english_country():
    generator = OasisProfileGenerator.__new__(OasisProfileGenerator)
    generator.locale = "en"

    profile = generator._generate_profile_rule_based(
        entity_name="Example University",
        entity_type="University",
        entity_summary="A research university.",
        entity_attributes={},
    )

    assert profile["country"] == "China"


def test_oasis_profile_generator_save_profiles_defaults_country_by_locale(tmp_path):
    generator = OasisProfileGenerator.__new__(OasisProfileGenerator)
    generator.locale = "en"
    output_path = tmp_path / "profiles.json"

    generator.save_profiles(
        [
            OasisAgentProfile(
                user_id=1,
                name="Alice",
                user_name="alice",
                bio="Bio",
                persona="Persona",
                karma=1000,
                created_at="2026-03-11",
                age=30,
                gender="female",
                mbti="INTJ",
                country=None,
                profession="Engineer",
                interested_topics=["Games"],
            )
        ],
        str(output_path),
        platform="reddit",
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload[0]["country"] == "China"


def test_oasis_profile_generator_default_country_tolerates_uninitialized_locale():
    generator = OasisProfileGenerator.__new__(OasisProfileGenerator)

    assert generator._default_country() == "中国"


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


def test_simulation_config_generator_logs_english_time_config_adjustments(monkeypatch):
    messages = []
    fake_logger = SimpleNamespace(warning=messages.append)
    monkeypatch.setattr(simulation_config_generator_module, "logger", fake_logger)

    generator = SimulationConfigGenerator.__new__(SimulationConfigGenerator)
    generator.locale = "en"

    parsed = generator._parse_time_config(
        {
            "agents_per_hour_min": 10,
            "agents_per_hour_max": 11,
        },
        num_entities=4,
    )

    assert parsed.agents_per_hour_min == 1
    assert parsed.agents_per_hour_max == 2
    assert messages == [
        "agents_per_hour_min (10) exceeded the total agent count (4); adjusted automatically",
        "agents_per_hour_max (11) exceeded the total agent count (4); adjusted automatically",
    ]


def test_simulation_config_generator_logs_english_min_ge_max_adjustment(monkeypatch):
    messages = []
    fake_logger = SimpleNamespace(warning=messages.append)
    monkeypatch.setattr(simulation_config_generator_module, "logger", fake_logger)

    generator = SimulationConfigGenerator.__new__(SimulationConfigGenerator)
    generator.locale = "en"

    parsed = generator._parse_time_config(
        {
            "agents_per_hour_min": 4,
            "agents_per_hour_max": 4,
        },
        num_entities=10,
    )

    assert parsed.agents_per_hour_min == 2
    assert parsed.agents_per_hour_max == 4
    assert messages == [
        "agents_per_hour_min was >= max; adjusted to 2",
    ]


def test_simulation_config_generator_logs_english_initial_post_assignment(monkeypatch):
    info_messages = []
    warning_messages = []
    fake_logger = SimpleNamespace(
        info=info_messages.append,
        warning=warning_messages.append,
    )
    monkeypatch.setattr(simulation_config_generator_module, "logger", fake_logger)

    generator = SimulationConfigGenerator.__new__(SimulationConfigGenerator)
    generator.locale = "en"

    event_config = generator._parse_event_config(
        {
            "initial_posts": [
                {"content": "Official update", "poster_type": "Official"},
                {"content": "Unexpected voice", "poster_type": "Alien"},
            ]
        }
    )
    agent_configs = [
        SimpleNamespace(agent_id=7, entity_type="University", influence_weight=3.0),
        SimpleNamespace(agent_id=4, entity_type="Student", influence_weight=1.0),
    ]

    updated = generator._assign_initial_post_agents(event_config, agent_configs)

    assert [post["poster_agent_id"] for post in updated.initial_posts] == [7, 7]
    assert warning_messages == [
        "No matching agent found for poster_type 'alien'; using the highest-influence agent"
    ]
    assert info_messages == [
        "Initial post assignment: poster_type='official' -> agent_id=7",
        "Initial post assignment: poster_type='alien' -> agent_id=7",
    ]


def test_zep_services_missing_key_support_english_request_locale(monkeypatch):
    monkeypatch.setattr("app.services.graph_builder.Config.ZEP_API_KEY", "")
    monkeypatch.setattr("app.services.zep_entity_reader.Config.ZEP_API_KEY", "")
    monkeypatch.setattr("app.services.zep_graph_memory_updater.Config.ZEP_API_KEY", "")
    monkeypatch.setattr("app.services.zep_tools.Config.ZEP_API_KEY", "")

    from flask import Flask

    app = Flask(__name__)
    with app.test_request_context(headers={"X-Locale": "en"}):
        constructors = (
            (GraphBuilderService, (), {}),
            (ZepEntityReader, (), {}),
            (ZepGraphMemoryUpdater, ("graph_123",), {}),
            (ZepToolsService, (), {}),
        )
        for service_type, args, kwargs in constructors:
            try:
                service_type(*args, **kwargs)
            except ValueError as exc:
                assert str(exc) == "ZEP_API_KEY is not configured"
            else:
                raise AssertionError(f"expected ValueError for {service_type.__name__}")


def test_agent_activity_episode_text_respects_english_locale():
    activity = AgentActivity(
        platform="twitter",
        agent_id=1,
        agent_name="Alice",
        action_type="QUOTE_POST",
        action_args={
            "original_author_name": "Bob",
            "original_content": "Launch day is tomorrow",
            "quote_content": "I agree",
        },
        round_num=1,
        timestamp="2026-03-11T12:00:00",
        locale="en",
    )

    assert (
        activity.to_episode_text()
        == 'Alice: quoted Bob\'s post "Launch day is tomorrow", adding: "I agree"'
    )
