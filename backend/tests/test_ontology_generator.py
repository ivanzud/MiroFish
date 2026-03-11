import importlib.util
import sys
import types
from pathlib import Path


def load_ontology_generator():
    backend_root = Path(__file__).resolve().parents[1]
    app_root = backend_root / "app"
    services_root = app_root / "services"
    module_path = services_root / "ontology_generator.py"

    app_module = sys.modules.setdefault("app", types.ModuleType("app"))
    app_module.__path__ = [str(app_root)]

    services_module = sys.modules.setdefault("app.services", types.ModuleType("app.services"))
    services_module.__path__ = [str(services_root)]

    spec = importlib.util.spec_from_file_location("app.services.ontology_generator", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


OntologyGenerator = load_ontology_generator().OntologyGenerator


class FakeLLM:
    def __init__(self):
        self.messages = None

    def chat_json(self, messages, temperature, max_tokens):
        self.messages = messages
        return {
            "entity_types": [
                {"name": "Player", "description": "Game player", "attributes": [], "examples": []},
                {"name": "Studio", "description": "Game studio", "attributes": [], "examples": []},
                {"name": "Analyst", "description": "Market analyst", "attributes": [], "examples": []},
                {"name": "Streamer", "description": "Content creator", "attributes": [], "examples": []},
                {"name": "Journalist", "description": "Reporter", "attributes": [], "examples": []},
                {"name": "Publisher", "description": "Publisher", "attributes": [], "examples": []},
                {"name": "Community", "description": "Fan community", "attributes": [], "examples": []},
                {"name": "Platform", "description": "Distribution platform", "attributes": [], "examples": []},
                {"name": "Person", "description": "Fallback person", "attributes": [], "examples": []},
                {"name": "Organization", "description": "Fallback org", "attributes": [], "examples": []},
            ],
            "edge_types": [],
            "analysis_summary": "English summary",
        }


def test_validate_and_process_normalizes_string_and_invalid_ontology_items():
    generator = OntologyGenerator(llm_client=object())

    result = generator._validate_and_process(
        {
            "entity_types": [
                "PersonLike",
                {
                    "name": "Analyst",
                    "description": "x" * 120,
                },
                123,
            ],
            "edge_types": [
                "RELATES_TO",
                {
                    "name": "MENTIONS",
                    "description": "y" * 120,
                },
                None,
            ],
        }
    )

    assert result["entity_types"][0] == {
        "name": "PersonLike",
        "description": "Entity type: PersonLike",
        "attributes": [],
        "examples": [],
    }
    assert result["entity_types"][1]["name"] == "Analyst"
    assert result["entity_types"][1]["attributes"] == []
    assert result["entity_types"][1]["examples"] == []
    assert result["entity_types"][1]["description"].endswith("...")
    assert len(result["entity_types"][1]["description"]) == 100
    assert {entity["name"] for entity in result["entity_types"]} >= {
        "Person",
        "Organization",
    }

    assert result["edge_types"] == [
        {
            "name": "RELATES_TO",
            "description": "Relationship type: RELATES_TO",
            "source_targets": [],
            "attributes": [],
        },
        {
            "name": "MENTIONS",
            "description": ("y" * 97) + "...",
            "source_targets": [],
            "attributes": [],
        },
    ]


def test_generate_requests_english_analysis_summary_when_locale_is_en():
    llm = FakeLLM()
    generator = OntologyGenerator(llm_client=llm, locale="en")

    result = generator.generate(
        document_texts=["Game design notes"],
        simulation_requirement="Predict the target audience for this game",
    )

    assert result["analysis_summary"] == "English summary"
    assert llm.messages is not None
    assert "Brief analysis summary of the text content (English)" in llm.messages[0]["content"]
