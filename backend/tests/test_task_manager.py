from datetime import datetime, timedelta
from pathlib import Path

import pytest

from app.models.task import TaskManager, TaskStatus


def reset_task_manager_singleton():
    TaskManager._instance = None


@pytest.fixture(autouse=True)
def isolated_task_manager():
    reset_task_manager_singleton()
    yield
    reset_task_manager_singleton()


def test_task_manager_persists_and_reload_tasks(tmp_path, monkeypatch):
    monkeypatch.setattr("app.models.task.Config.UPLOAD_FOLDER", str(tmp_path))

    manager = TaskManager()
    task_id = manager.create_task("graph_build", metadata={"project_id": "proj_123"})
    manager.update_task(
        task_id,
        status=TaskStatus.PROCESSING,
        progress=55,
        message="still running",
        progress_detail={"stage": "ontology"},
    )

    state_path = Path(tmp_path) / "tasks" / "task_state.json"
    assert state_path.exists()

    reset_task_manager_singleton()
    reloaded = TaskManager()
    task = reloaded.get_task(task_id)

    assert task is not None
    assert task.status == TaskStatus.PROCESSING
    assert task.progress == 55
    assert task.message == "still running"
    assert task.metadata == {"project_id": "proj_123"}
    assert task.progress_detail == {"stage": "ontology"}


def test_task_manager_ignores_invalid_persisted_state(tmp_path, monkeypatch):
    monkeypatch.setattr("app.models.task.Config.UPLOAD_FOLDER", str(tmp_path))
    state_path = Path(tmp_path) / "tasks" / "task_state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text("{invalid json", encoding="utf-8")

    manager = TaskManager()

    assert manager.list_tasks() == []


def test_task_manager_cleanup_updates_persisted_state(tmp_path, monkeypatch):
    monkeypatch.setattr("app.models.task.Config.UPLOAD_FOLDER", str(tmp_path))

    manager = TaskManager()
    task_id = manager.create_task("report")
    with manager._task_lock:
        task = manager._tasks[task_id]
        task.status = TaskStatus.COMPLETED
        task.created_at = datetime.now() - timedelta(hours=48)
        task.updated_at = task.created_at
        manager._persist_tasks()

    manager.cleanup_old_tasks(max_age_hours=24)
    assert manager.get_task(task_id) is None

    reset_task_manager_singleton()
    reloaded = TaskManager()
    assert reloaded.get_task(task_id) is None
