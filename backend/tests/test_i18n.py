from flask import Flask

from app.i18n import get_locale, tr


def test_get_locale_defaults_to_zh_without_request():
    assert get_locale() == "zh"


def test_get_locale_reads_request_header():
    app = Flask(__name__)

    with app.test_request_context(headers={"X-Locale": "en"}):
        assert get_locale() == "en"
        assert tr("graph.project_not_found", project_id="proj_123") == "Project not found: proj_123"
        assert (
            tr("simulation.runner_dependency_error")
            == "The optional OASIS simulation runtime dependencies are not installed. Run `npm run setup:backend:simulation`, or `uv sync --extra simulation` inside the backend directory first."
        )
