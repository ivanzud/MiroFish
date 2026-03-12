import importlib.util
import sys
from pathlib import Path


def load_parallel_simulation_module(monkeypatch, locale="en"):
    scripts_dir = Path(__file__).resolve().parents[1] / "scripts"
    module_path = scripts_dir / "run_parallel_simulation.py"
    module_name = "test_run_parallel_simulation_module"

    monkeypatch.setenv("MIROFISH_LOCALE", locale)
    monkeypatch.syspath_prepend(str(scripts_dir))
    sys.modules.pop(module_name, None)

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fetch_new_actions_from_db_localizes_read_failures(monkeypatch, tmp_path, capsys):
    module = load_parallel_simulation_module(monkeypatch, locale="en")
    broken_db = tmp_path / "broken.db"
    broken_db.write_text("not a sqlite database", encoding="utf-8")

    actions, last_rowid = module.fetch_new_actions_from_db(str(broken_db), 0, {})

    assert actions == []
    assert last_rowid == 0
    assert "Failed to read database actions:" in capsys.readouterr().out


def test_enrich_action_context_localizes_failures(monkeypatch, capsys):
    module = load_parallel_simulation_module(monkeypatch, locale="en")

    class FailingCursor:
        def execute(self, *_args, **_kwargs):
            raise RuntimeError("boom")

    module._enrich_action_context(
        FailingCursor(),
        "FOLLOW",
        {"follow_id": 1},
        {},
    )

    assert "Failed to enrich action context: boom" in capsys.readouterr().out
