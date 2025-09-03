import os
import shutil
import tempfile
from pathlib import Path


def test_create_and_transition_task():
    tmp = tempfile.mkdtemp()
    try:
        os.environ["COLLAB_ROOT"] = tmp
        # Lazy import after setting env so BASE points to tmp
        import importlib

        collab = importlib.import_module("mcp.kyros_collab_server")
        # seed minimal state files
        (Path(tmp) / "collaboration/state").mkdir(parents=True, exist_ok=True)
        (Path(tmp) / "collaboration/state/tasks.json").write_text(
            '{\n "version": 1, "tasks": []\n}'
        )
        # create
        res = collab.create_task({"title": "Test Task", "labels": ["backend"]})
        assert "id" in res
        tid = res["id"]
        # transition
        ok = collab.transition_task({"id": tid, "new_status": "in_progress"})
        assert ok["ok"] is True
        # suggest
        sug = collab.suggest_assignee({"labels": ["backend"]})
        assert "assignee" in sug
    finally:
        shutil.rmtree(tmp)


def test_lease_acquire_release():
    tmp = tempfile.mkdtemp()
    try:
        os.environ["COLLAB_ROOT"] = tmp
        import importlib

        mod = importlib.import_module("mcp.kyros_collab_server")
        (Path(tmp) / "collaboration/state").mkdir(parents=True, exist_ok=True)
        (Path(tmp) / "collaboration/state/locks.json").write_text(
            '{\n "version": 1, "locks": []\n}'
        )
        res = mod.rpc_acquire_lease(
            {
                "path": "frontend/playwright.config.js",
                "owner": "codex-cli-1",
                "purpose": "task-xyz",
            }
        )
        assert "lock_id" in res
        lid = res["lock_id"]
        ok = mod.rpc_release_lease({"lock_id": lid, "owner": "codex-cli-1"})
        assert ok["ok"] is True
    finally:
        shutil.rmtree(tmp)
