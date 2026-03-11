import importlib
import io
import sys
import types
from pathlib import Path

from flask import Flask


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

    class DummyGraphBuilderService:
        pass

    class DummyOntologyGenerator:
        def __init__(self, *args, **kwargs):
            pass

        def generate(self, *args, **kwargs):
            raise AssertionError("Ontology generation should not run for upload-validation failures")

    graph_builder_stub.GraphBuilderService = DummyGraphBuilderService
    ontology_stub.OntologyGenerator = DummyOntologyGenerator

    monkeypatch.setitem(sys.modules, "app.api.simulation", simulation_stub)
    monkeypatch.setitem(sys.modules, "app.api.report", report_stub)
    monkeypatch.setitem(sys.modules, "app.services.graph_builder", graph_builder_stub)
    monkeypatch.setitem(sys.modules, "app.services.ontology_generator", ontology_stub)

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

    app = Flask(__name__)
    app.register_blueprint(graph_bp, url_prefix="/api/graph")
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

