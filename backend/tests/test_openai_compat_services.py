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
    generator.client = SimpleNamespace(chat=SimpleNamespace(completions=FakeCompletions()))

    result = generator._request_json_completion(
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.6,
    )

    assert result["content"] == '{"time_config": {"total_simulation_hours": 12}}'
    assert "response_format" in create_calls[0]
    assert "response_format" not in create_calls[1]
