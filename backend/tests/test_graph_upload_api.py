import importlib
import io
import sys
import types
from pathlib import Path

from flask import Flask


class FakeValidationResult:
    def __init__(self, errors=None):
        self.errors = list(errors or [])
        self.warnings = []
        self.info = []

    @property
    def is_valid(self):
        return not self.errors

    def to_dict(self):
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }


def load_graph_blueprint(monkeypatch):
    for name in (
        "app.api",
        "app.api.graph",
        "app.api.simulation",
        "app.api.report",
        "app.services.graph_builder",
        "app.services.ontology_generator",
    ):
        sys.modules.pop(name, None)

    simulation_stub = types.ModuleType("app.api.simulation")
    report_stub = types.ModuleType("app.api.report")
    graph_builder_stub = types.ModuleType("app.services.graph_builder")
    ontology_stub = types.ModuleType("app.services.ontology_generator")
    zep_cloud_stub = types.ModuleType("zep_cloud")
    zep_cloud_client_stub = types.ModuleType("zep_cloud.client")

    class DummyGraphBuilderService:
        pass

    class DummyOntologyGenerator:
        def __init__(self, *args, **kwargs):
            pass

        def generate(self, *args, **kwargs):
            raise AssertionError("Ontology generation should not run for upload-validation failures")

    graph_builder_stub.GraphBuilderService = DummyGraphBuilderService
    ontology_stub.OntologyGenerator = DummyOntologyGenerator
    zep_cloud_client_stub.Zep = object
    zep_cloud_stub.EpisodeData = object
    zep_cloud_stub.EntityEdgeSourceTarget = object
    zep_cloud_stub.InternalServerError = Exception

    monkeypatch.setitem(sys.modules, "app.api.simulation", simulation_stub)
    monkeypatch.setitem(sys.modules, "app.api.report", report_stub)
    monkeypatch.setitem(sys.modules, "app.services.graph_builder", graph_builder_stub)
    monkeypatch.setitem(sys.modules, "app.services.ontology_generator", ontology_stub)
    monkeypatch.setitem(sys.modules, "zep_cloud", zep_cloud_stub)
    monkeypatch.setitem(sys.modules, "zep_cloud.client", zep_cloud_client_stub)

    api_module = importlib.import_module("app.api")
    graph_module = importlib.import_module("app.api.graph")
    return api_module.graph_bp, graph_module


def create_graph_test_client(monkeypatch, tmp_path):
    graph_bp, graph_module = load_graph_blueprint(monkeypatch)
    monkeypatch.setattr(
        graph_module.ProjectManager,
        "PROJECTS_DIR",
        str(tmp_path / "projects"),
    )
    monkeypatch.setattr(
        graph_module.Config,
        "validate_comprehensive",
        lambda locale="zh": FakeValidationResult(),
    )
    monkeypatch.setattr(
        graph_module.Config,
        "get_config_summary",
        lambda: {
            "llm": {"configured": True},
            "zep": {"configured": True},
        },
    )

    app = Flask(__name__)
    app.register_blueprint(graph_bp, url_prefix="/api/graph")
    return app.test_client(), graph_module


def create_graph_build_test_client(monkeypatch, tmp_path):
    for name in (
        "app.api",
        "app.api.graph",
        "app.api.simulation",
        "app.api.report",
        "app.services.graph_builder",
        "app.services.ontology_generator",
    ):
        sys.modules.pop(name, None)

    simulation_stub = types.ModuleType("app.api.simulation")
    report_stub = types.ModuleType("app.api.report")
    ontology_stub = types.ModuleType("app.services.ontology_generator")
    zep_cloud_stub = types.ModuleType("zep_cloud")
    zep_cloud_client_stub = types.ModuleType("zep_cloud.client")
    zep_cloud_ontology_stub = types.ModuleType("zep_cloud.external_clients.ontology")

    class DummyOntologyGenerator:
        def __init__(self, *args, **kwargs):
            pass

    class FakeZep:
        def __init__(self, api_key):
            self.api_key = api_key

    zep_cloud_client_stub.Zep = FakeZep
    zep_cloud_stub.EpisodeData = object
    zep_cloud_stub.EntityEdgeSourceTarget = object
    zep_cloud_stub.InternalServerError = Exception
    zep_cloud_ontology_stub.EntityModel = object
    zep_cloud_ontology_stub.EntityText = object
    zep_cloud_ontology_stub.EdgeModel = object
    ontology_stub.OntologyGenerator = DummyOntologyGenerator

    monkeypatch.setitem(sys.modules, "app.api.simulation", simulation_stub)
    monkeypatch.setitem(sys.modules, "app.api.report", report_stub)
    monkeypatch.setitem(sys.modules, "app.services.ontology_generator", ontology_stub)
    monkeypatch.setitem(sys.modules, "zep_cloud", zep_cloud_stub)
    monkeypatch.setitem(sys.modules, "zep_cloud.client", zep_cloud_client_stub)
    monkeypatch.setitem(sys.modules, "zep_cloud.external_clients.ontology", zep_cloud_ontology_stub)

    api_module = importlib.import_module("app.api")
    graph_module = importlib.import_module("app.api.graph")
    monkeypatch.setattr(
        graph_module.ProjectManager,
        "PROJECTS_DIR",
        str(tmp_path / "projects"),
    )
    monkeypatch.setattr(
        graph_module.Config,
        "validate_comprehensive",
        lambda locale="zh": FakeValidationResult(),
    )
    monkeypatch.setattr(
        graph_module.Config,
        "get_config_summary",
        lambda: {
            "llm": {"configured": True},
            "zep": {"configured": True},
        },
    )
    monkeypatch.setattr(graph_module.Config, "ZEP_API_KEY", "zep-test-key")
    monkeypatch.setattr(graph_module.Config, "DEFAULT_CHUNK_SIZE", 500)
    monkeypatch.setattr(graph_module.Config, "DEFAULT_CHUNK_OVERLAP", 50)

    app = Flask(__name__)
    app.register_blueprint(api_module.graph_bp, url_prefix="/api/graph")
    return app.test_client(), graph_module


def test_generate_ontology_returns_file_specific_parse_errors(monkeypatch, tmp_path):
    client, graph_module = create_graph_test_client(monkeypatch, tmp_path)

    def raise_parse_error(_path):
        raise ValueError("mock parse failure")

    monkeypatch.setattr(graph_module.FileParser, "extract_text", raise_parse_error)

    response = client.post(
        "/api/graph/ontology/generate",
        data={
            "simulation_requirement": "predict audience",
            "files": (io.BytesIO(b"hello"), "sample.txt"),
        },
        content_type="multipart/form-data",
    )
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["success"] is False
    assert "1 个文档处理失败" in payload["error"]
    assert payload["data"]["file_errors"] == [
        {
            "filename": "sample.txt",
            "code": "document_parse_failed",
            "message": "文件 sample.txt 解析失败: mock parse failure",
            "details": "mock parse failure",
        }
    ]

    projects_dir = Path(graph_module.ProjectManager.PROJECTS_DIR)
    assert not any(projects_dir.iterdir()) if projects_dir.exists() else True


def test_generate_ontology_reports_unsupported_extensions_in_english(monkeypatch, tmp_path):
    client, graph_module = create_graph_test_client(monkeypatch, tmp_path)

    response = client.post(
        "/api/graph/ontology/generate",
        headers={"X-Locale": "en"},
        data={
            "simulation_requirement": "predict audience",
            "files": (io.BytesIO(b"hello"), "sample.docx"),
        },
        content_type="multipart/form-data",
    )
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["success"] is False
    assert payload["error"] == "1 document(s) could not be processed. Fix the reported file issues and retry."
    assert payload["data"]["file_errors"] == [
        {
            "filename": "sample.docx",
            "code": "unsupported_file_type",
            "message": "File sample.docx is not supported. Supported formats: markdown, md, pdf, txt",
            "supported_extensions": ["markdown", "md", "pdf", "txt"],
        }
    ]


def test_generate_ontology_returns_backend_config_validation_when_env_is_missing(monkeypatch, tmp_path):
    client, graph_module = create_graph_test_client(monkeypatch, tmp_path)
    invalid_validation = FakeValidationResult(
        errors=[
            "LLM_API_KEY / OPENAI_API_KEY is not configured",
            "ZEP_API_KEY is not configured",
        ]
    )
    monkeypatch.setattr(
        graph_module.Config,
        "validate_comprehensive",
        lambda locale="zh": invalid_validation,
    )
    monkeypatch.setattr(
        graph_module.Config,
        "get_config_summary",
        lambda: {
            "llm": {"configured": False},
            "zep": {"configured": False},
        },
    )

    response = client.post(
        "/api/graph/ontology/generate",
        headers={"X-Locale": "en"},
        data={
            "simulation_requirement": "predict audience",
            "files": (io.BytesIO(b"hello"), "sample.txt"),
        },
        content_type="multipart/form-data",
    )
    payload = response.get_json()

    assert response.status_code == 503
    assert payload["success"] is False
    assert "Backend configuration is incomplete:" in payload["error"]
    assert payload["data"]["validation"]["is_valid"] is False
    assert "LLM_API_KEY / OPENAI_API_KEY is not configured" in payload["data"]["validation"]["errors"]
    assert "ZEP_API_KEY is not configured" in payload["data"]["validation"]["errors"]
    assert payload["data"]["summary"]["llm"]["configured"] is False
    assert payload["data"]["summary"]["zep"]["configured"] is False

    projects_dir = Path(graph_module.ProjectManager.PROJECTS_DIR)
    assert not any(projects_dir.iterdir()) if projects_dir.exists() else True


def test_get_backend_config_status_reports_openai_compatible_alias_sources(monkeypatch, tmp_path):
    client, graph_module = create_graph_test_client(monkeypatch, tmp_path)
    validation = FakeValidationResult()
    monkeypatch.setattr(
        graph_module.Config,
        "validate_comprehensive",
        lambda locale="zh": validation,
    )
    monkeypatch.setattr(
        graph_module.Config,
        "get_config_summary",
        lambda: {
            "llm": {
                "backend_mode": "openai_compatible",
                "configured": True,
                "base_url": "https://api.openai.com/v1",
                "model": "gpt-4.1-mini",
                "sources": {
                    "api_key_env": "OPENAI_API_KEY",
                    "base_url_env": "OPENAI_API_BASE_URL",
                    "model_env": "OPENAI_MODEL",
                    "uses_project_aliases": False,
                    "uses_openai_aliases": True,
                },
            },
            "zep": {"configured": True},
        },
    )

    response = client.get("/api/graph/config/status", headers={"X-Locale": "en"})
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["data"]["validation"]["is_valid"] is True
    assert payload["data"]["summary"]["llm"]["backend_mode"] == "openai_compatible"
    assert payload["data"]["summary"]["llm"]["sources"] == {
        "api_key_env": "OPENAI_API_KEY",
        "base_url_env": "OPENAI_API_BASE_URL",
        "model_env": "OPENAI_MODEL",
        "uses_project_aliases": False,
        "uses_openai_aliases": True,
    }


def test_build_graph_task_persists_sanitized_zep_auth_error(monkeypatch, tmp_path):
    client, graph_module = create_graph_build_test_client(monkeypatch, tmp_path)

    graph_module.TaskManager()._tasks.clear()

    class ImmediateThread:
        def __init__(self, target=None, args=(), kwargs=None, daemon=None):
            self._target = target
            self._args = args
            self._kwargs = kwargs or {}
            self.daemon = daemon

        def start(self):
            self._target(*self._args, **self._kwargs)

    auth_traceback = """Traceback (most recent call last):
  File "/app/backend/.venv/lib/python3.11/site-packages/zep_cloud/graph/raw_client.py", line 713, in create
    _response_json = _response.json()
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
401 unauthorized
"""

    monkeypatch.setattr(graph_module.threading, "Thread", ImmediateThread)
    monkeypatch.setattr(graph_module.TextProcessor, "split_text", lambda text, chunk_size, overlap: ["chunk-1"])
    monkeypatch.setattr(
        graph_module.GraphBuilderService,
        "create_graph",
        lambda self, name: (_ for _ in ()).throw(RuntimeError(auth_traceback)),
    )

    project = graph_module.ProjectManager.create_project("Auth failure test")
    project.status = graph_module.ProjectStatus.ONTOLOGY_GENERATED
    project.ontology = {
        "entity_types": [{"name": "Person", "attributes": []}],
        "edge_types": [],
    }
    graph_module.ProjectManager.save_project(project)
    graph_module.ProjectManager.save_extracted_text(project.project_id, "test text")

    response = client.post(
        "/api/graph/build",
        json={"project_id": project.project_id, "graph_name": "Auth failure graph"},
    )
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is True

    task_id = payload["data"]["task_id"]
    task_response = client.get(f"/api/graph/task/{task_id}")
    task_payload = task_response.get_json()
    persisted_project = graph_module.ProjectManager.get_project(project.project_id)

    assert task_response.status_code == 200
    assert task_payload["data"]["status"] == "failed"
    assert "ZEP_API_KEY" in task_payload["data"]["error"]
    assert "Traceback" not in task_payload["data"]["error"]
    assert "构建失败:" in task_payload["data"]["message"]

    assert persisted_project.status == graph_module.ProjectStatus.FAILED
    assert "ZEP_API_KEY" in persisted_project.error
    assert "Traceback" not in persisted_project.error
