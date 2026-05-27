"""
Tests for todo-1.py  (imported as module `todo`)
Covers: persistence, helpers, add_task, view_tasks, complete_task,
        edit_task, delete_task, undo_delete, search_tasks, show_summary
"""

import json
import pytest
from datetime import date, timedelta
from unittest.mock import patch
import importlib.util, pathlib, sys


# ── Module loader fixture ───────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def todo_mod():
    """Load todo-1.py once per test session as module `todo`."""
    spec = importlib.util.spec_from_file_location(
        "todo",
        pathlib.Path(__file__).parent / "todo-1.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(autouse=True)
def patch_save_file(todo_mod, tmp_path, monkeypatch):
    """Redirect SAVE_FILE to a temp path so no real files are touched."""
    monkeypatch.setattr(todo_mod, "SAVE_FILE", str(tmp_path / "todo_data.json"))


# ── Shared helpers ──────────────────────────────────────────────────────────────

def _store(tasks=None, deleted=None, streaks=None):
    return {
        "tasks":   tasks   or [],
        "deleted": deleted or [],
        "streaks": streaks or {},
    }


def _task(name="Test Task", priority="🟡 MEDIUM", category="💼 Work",
          due_date=None, note="", status=None, task_id=1,
          created=None, completed_on=None):
    from datetime import date as _date
    return {
        "id":           task_id,
        "name":         name,
        "priority":     priority,
        "category":     category,
        "due_date":     due_date,
        "note":         note,
        "status":       status or "⏳ Pending",
        "created":      created or _date.today().isoformat(),
        "completed_on": completed_on,
    }


# ══════════════════════════════════════════════════════════════════════════════
# Persistence
# ══════════════════════════════════════════════════════════════════════════════

class TestLoadStore:
    def test_returns_defaults_when_no_file(self, todo_mod):
        store = todo_mod.load_store()
        assert store == {"tasks": [], "deleted": [], "streaks": {}}

    def test_loads_existing_store(self, todo_mod, tmp_path, monkeypatch):
        path = tmp_path / "todo_data.json"
        payload = {"tasks": [{"id": 99}], "deleted": [], "streaks": {"count": 3}}
        path.write_text(json.dumps(payload))
        monkeypatch.setattr(todo_mod, "SAVE_FILE", str(path))
        store = todo_mod.load_store()
        assert store["tasks"][0]["id"] == 99
        assert store["streaks"]["count"] == 3

    def test_back_compat_plain_list(self, todo_mod, tmp_path, monkeypatch):
        """Old format: JSON root was a plain list of tasks."""
        path = tmp_path / "todo_data.json"
        path.write_text(json.dumps([{"id": 1, "name": "Old task"}]))
        monkeypatch.setattr(todo_mod, "SAVE_FILE", str(path))
        store = todo_mod.load_store()
        assert isinstance(store, dict)
        assert store["tasks"][0]["name"] == "Old task"

    def test_returns_defaults_on_corrupt_file(self, todo_mod, tmp_path, monkeypatch):
        path = tmp_path / "todo_data.json"
        path.write_text("BROKEN{{{")
        monkeypatch.setattr(todo_mod, "SAVE_FILE", str(path))
        store = todo_mod.load_store()
        assert store["tasks"] == []


class TestSaveStore:
    def test_writes_and_reloads(self, todo_mod):
        store = _store(tasks=[_task()])
        todo_mod.save_store(store)
        loaded = todo_mod.load_store()
        assert loaded["tasks"][0]["name"] == "Test Task"


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

class TestProgressBar:
    def test_full_bar(self, todo_mod):
        bar, pct = todo_mod._progress_bar(10, 10)
        assert pct == 100.0
        assert "░" not in bar

    def test_empty_bar(self, todo_mod):
        bar, pct = todo_mod._progress_bar(0, 10)
        assert pct == 0.0
        assert "█" not in bar

    def test_zero_total_no_division_error(self, todo_mod):
        bar, pct = todo_mod._progress_bar(0, 0)
        assert pct == 0.0

    def test_half_bar(self, todo_mod):
        bar, pct = todo_mod._progress_bar(5, 10)
        assert pct == pytest.approx(50.0)


class TestUpdateStreak:
    def test_first_completion_sets_streak_to_one(self, todo_mod):
        store = _store()
        todo_mod._update_streak(store)
        assert store["streaks"]["count"] == 1

    def test_consecutive_day_increments_streak(self, todo_mod):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        store = _store(streaks={"count": 4, "last_completion_date": yesterday})
        todo_mod._update_streak(store)
        assert store["streaks"]["count"] == 5

    def test_gap_resets_streak(self, todo_mod):
        store = _store(streaks={"count": 10, "last_completion_date": "2020-01-01"})
        todo_mod._update_streak(store)
        assert store["streaks"]["count"] == 1

    def test_same_day_does_not_double_count(self, todo_mod):
        today = date.today().isoformat()
        store = _store(streaks={"count": 3, "last_completion_date": today})
        todo_mod._update_streak(store)
        assert store["streaks"]["count"] == 3


# ══════════════════════════════════════════════════════════════════════════════
# add_task
# ══════════════════════════════════════════════════════════════════════════════

class TestAddTask:
    def _add(self, todo_mod, inputs):
        store = _store()
        with patch("builtins.input", side_effect=inputs), patch("builtins.print"):
            todo_mod.add_task(store)
        return store

    def test_adds_valid_task(self, todo_mod):
        store = self._add(todo_mod, ["Buy milk", "2", "1", "", "grocery run"])
        assert len(store["tasks"]) == 1
        assert store["tasks"][0]["name"] == "Buy milk"

    def test_empty_name_rejected(self, todo_mod):
        store = self._add(todo_mod, ["", "", "", "", ""])
        assert len(store["tasks"]) == 0

    def test_default_priority_medium(self, todo_mod):
        store = self._add(todo_mod, ["Task A", "", "1", "", ""])
        assert store["tasks"][0]["priority"] == "🟡 MEDIUM"

    def test_default_category_work(self, todo_mod):
        store = self._add(todo_mod, ["Task B", "1", "", "", ""])
        assert store["tasks"][0]["category"] == "💼 Work"

    def test_valid_due_date_stored(self, todo_mod):
        store = self._add(todo_mod, ["Task C", "1", "1", "2030-12-31", ""])
        assert store["tasks"][0]["due_date"] == "2030-12-31"

    def test_invalid_due_date_skipped(self, todo_mod):
        store = self._add(todo_mod, ["Task D", "1", "1", "not-a-date", ""])
        assert store["tasks"][0]["due_date"] is None

    def test_status_is_pending_on_creation(self, todo_mod):
        store = self._add(todo_mod, ["Task E", "1", "1", "", ""])
        assert store["tasks"][0]["status"] == "⏳ Pending"

    def test_created_date_is_today(self, todo_mod):
        store = self._add(todo_mod, ["Task F", "1", "1", "", ""])
        assert store["tasks"][0]["created"] == date.today().isoformat()


# ══════════════════════════════════════════════════════════════════════════════
# view_tasks / _filtered_sorted
# ══════════════════════════════════════════════════════════════════════════════

class TestViewTasks:
    def test_no_tasks_message(self, todo_mod, capsys):
        todo_mod.view_tasks(_store())
        assert "No tasks" in capsys.readouterr().out

    def test_shows_task_names(self, todo_mod, capsys):
        store = _store(tasks=[_task("Read book"), _task("Write code", task_id=2)])
        todo_mod.view_tasks(store)
        out = capsys.readouterr().out
        assert "Read book" in out
        assert "Write code" in out

    def test_filter_status_pending(self, todo_mod, capsys):
        done_task = _task("Done one", task_id=1, status="✅ Done")
        pending_task = _task("Pending one", task_id=2)
        store = _store(tasks=[done_task, pending_task])
        todo_mod.view_tasks(store, filter_status="⏳ Pending")
        out = capsys.readouterr().out
        assert "Pending one" in out
        assert "Done one" not in out

    def test_filter_status_done(self, todo_mod, capsys):
        done_task = _task("Completed", task_id=1, status="✅ Done")
        pending_task = _task("Still pending", task_id=2)
        store = _store(tasks=[done_task, pending_task])
        todo_mod.view_tasks(store, filter_status="✅ Done")
        out = capsys.readouterr().out
        assert "Completed" in out
        assert "Still pending" not in out

    def test_overdue_flag_shown(self, todo_mod, capsys):
        overdue_task = _task("Overdue", task_id=1, due_date="2020-01-01")
        store = _store(tasks=[overdue_task])
        todo_mod.view_tasks(store)
        out = capsys.readouterr().out
        assert "⚠️" in out

    def test_progress_bar_shown(self, todo_mod, capsys):
        store = _store(tasks=[_task()])
        todo_mod.view_tasks(store)
        out = capsys.readouterr().out
        assert "%" in out

    def test_sort_by_priority(self, todo_mod):
        high = _task("High priority", priority="🔴 HIGH", task_id=1)
        low  = _task("Low priority",  priority="🟢 LOW",  task_id=2)
        store = _store(tasks=[low, high])
        result = todo_mod._filtered_sorted(store["tasks"], sort_by="priority")
        assert result[0]["priority"] == "🔴 HIGH"

    def test_sort_by_due_date(self, todo_mod):
        early = _task("Early", due_date="2025-01-01", task_id=1)
        late  = _task("Late",  due_date="2026-06-01", task_id=2)
        store = _store(tasks=[late, early])
        result = todo_mod._filtered_sorted(store["tasks"], sort_by="due_date")
        assert result[0]["due_date"] == "2025-01-01"


# ══════════════════════════════════════════════════════════════════════════════
# complete_task
# ══════════════════════════════════════════════════════════════════════════════

class TestCompleteTask:
    def test_marks_task_done(self, todo_mod):
        store = _store(tasks=[_task(task_id=1)])
        with patch("builtins.input", side_effect=["1"]), patch("builtins.print"):
            todo_mod.complete_task(store)
        assert store["tasks"][0]["status"] == "✅ Done"

    def test_sets_completed_on_today(self, todo_mod):
        store = _store(tasks=[_task(task_id=1)])
        with patch("builtins.input", side_effect=["1"]), patch("builtins.print"):
            todo_mod.complete_task(store)
        assert store["tasks"][0]["completed_on"] == date.today().isoformat()

    def test_increments_streak(self, todo_mod):
        store = _store(tasks=[_task(task_id=1)])
        with patch("builtins.input", side_effect=["1"]), patch("builtins.print"):
            todo_mod.complete_task(store)
        assert store["streaks"].get("count", 0) >= 1

    def test_invalid_index_does_not_change_status(self, todo_mod, capsys):
        store = _store(tasks=[_task(task_id=1)])
        with patch("builtins.input", side_effect=["99"]):
            todo_mod.complete_task(store)
        assert store["tasks"][0]["status"] == "⏳ Pending"

    def test_non_numeric_input_handled(self, todo_mod):
        store = _store(tasks=[_task(task_id=1)])
        with patch("builtins.input", side_effect=["abc"]), patch("builtins.print"):
            todo_mod.complete_task(store)
        assert store["tasks"][0]["status"] == "⏳ Pending"

    def test_no_pending_tasks_returns_early(self, todo_mod):
        done = _task(status="✅ Done", task_id=1)
        store = _store(tasks=[done])
        with patch("builtins.input", side_effect=[]):
            todo_mod.complete_task(store)  # should not raise


# ══════════════════════════════════════════════════════════════════════════════
# edit_task
# ══════════════════════════════════════════════════════════════════════════════

class TestEditTask:
    def test_updates_task_name(self, todo_mod):
        store = _store(tasks=[_task("Old Name", task_id=1)])
        inputs = ["1", "New Name", "1", "1", "", ""]
        with patch("builtins.input", side_effect=inputs), patch("builtins.print"):
            todo_mod.edit_task(store)
        assert store["tasks"][0]["name"] == "New Name"

    def test_keeps_old_name_on_empty_input(self, todo_mod):
        store = _store(tasks=[_task("Keep Me", task_id=1)])
        inputs = ["1", "", "2", "2", "", ""]
        with patch("builtins.input", side_effect=inputs), patch("builtins.print"):
            todo_mod.edit_task(store)
        assert store["tasks"][0]["name"] == "Keep Me"

    def test_invalid_index_does_not_change_task(self, todo_mod):
        store = _store(tasks=[_task("Unchanged", task_id=1)])
        with patch("builtins.input", side_effect=["99"]), patch("builtins.print"):
            todo_mod.edit_task(store)
        assert store["tasks"][0]["name"] == "Unchanged"


# ══════════════════════════════════════════════════════════════════════════════
# delete_task
# ══════════════════════════════════════════════════════════════════════════════

class TestDeleteTask:
    def test_removes_task_from_list(self, todo_mod):
        store = _store(tasks=[_task("Remove me", task_id=1)])
        with patch("builtins.input", side_effect=["1"]), patch("builtins.print"):
            todo_mod.delete_task(store)
        assert len(store["tasks"]) == 0

    def test_moved_to_deleted_buffer(self, todo_mod):
        store = _store(tasks=[_task("Buffered", task_id=1)])
        with patch("builtins.input", side_effect=["1"]), patch("builtins.print"):
            todo_mod.delete_task(store)
        assert store["deleted"][0]["name"] == "Buffered"

    def test_invalid_index_does_not_remove(self, todo_mod):
        store = _store(tasks=[_task(task_id=1)])
        with patch("builtins.input", side_effect=["99"]), patch("builtins.print"):
            todo_mod.delete_task(store)
        assert len(store["tasks"]) == 1

    def test_non_numeric_input_handled(self, todo_mod):
        store = _store(tasks=[_task(task_id=1)])
        with patch("builtins.input", side_effect=["xyz"]), patch("builtins.print"):
            todo_mod.delete_task(store)
        assert len(store["tasks"]) == 1


# ══════════════════════════════════════════════════════════════════════════════
# undo_delete
# ══════════════════════════════════════════════════════════════════════════════

class TestUndoDelete:
    def test_restores_last_deleted_task(self, todo_mod):
        store = _store(deleted=[_task("Restored", task_id=1)])
        with patch("builtins.print"):
            todo_mod.undo_delete(store)
        assert store["tasks"][0]["name"] == "Restored"
        assert len(store["deleted"]) == 0

    def test_nothing_to_undo_message(self, todo_mod, capsys):
        store = _store()
        todo_mod.undo_delete(store)
        assert "Nothing" in capsys.readouterr().out

    def test_multiple_undos_restore_lifo_order(self, todo_mod):
        store = _store(deleted=[
            _task("First deleted", task_id=1),
            _task("Last deleted",  task_id=2),
        ])
        with patch("builtins.print"):
            todo_mod.undo_delete(store)
        assert store["tasks"][0]["name"] == "Last deleted"


# ══════════════════════════════════════════════════════════════════════════════
# search_tasks
# ══════════════════════════════════════════════════════════════════════════════

class TestSearchTasks:
    def test_finds_by_name(self, todo_mod, capsys):
        store = _store(tasks=[_task("Buy apples", task_id=1),
                               _task("Walk dog",  task_id=2)])
        with patch("builtins.input", return_value="apples"):
            todo_mod.search_tasks(store)
        out = capsys.readouterr().out
        assert "Buy apples" in out
        assert "Walk dog" not in out

    def test_finds_by_note(self, todo_mod, capsys):
        store = _store(tasks=[_task("Task X", note="urgent meeting", task_id=1)])
        with patch("builtins.input", return_value="urgent"):
            todo_mod.search_tasks(store)
        assert "Task X" in capsys.readouterr().out

    def test_finds_by_category(self, todo_mod, capsys):
        store = _store(tasks=[_task("Health task", category="🏥 Health", task_id=1),
                               _task("Work task",   category="💼 Work",   task_id=2)])
        with patch("builtins.input", return_value="health"):
            todo_mod.search_tasks(store)
        out = capsys.readouterr().out
        assert "Health task" in out

    def test_no_results_message(self, todo_mod, capsys):
        store = _store(tasks=[_task("Nothing here", task_id=1)])
        with patch("builtins.input", return_value="xyz123"):
            todo_mod.search_tasks(store)
        assert "No tasks found" in capsys.readouterr().out

    def test_case_insensitive_search(self, todo_mod, capsys):
        store = _store(tasks=[_task("Buy MILK", task_id=1)])
        with patch("builtins.input", return_value="milk"):
            todo_mod.search_tasks(store)
        assert "Buy MILK" in capsys.readouterr().out

    def test_empty_keyword_returns_without_results(self, todo_mod, capsys):
        store = _store(tasks=[_task(task_id=1)])
        with patch("builtins.input", return_value=""):
            todo_mod.search_tasks(store)
        # Should not crash and not show results header
        out = capsys.readouterr().out
        assert "Results" not in out


# ══════════════════════════════════════════════════════════════════════════════
# show_summary
# ══════════════════════════════════════════════════════════════════════════════

class TestShowSummary:
    def test_shows_total_count(self, todo_mod, capsys):
        store = _store(tasks=[_task(task_id=1), _task(task_id=2)])
        todo_mod.show_summary(store)
        assert "2" in capsys.readouterr().out

    def test_shows_done_and_pending(self, todo_mod, capsys):
        store = _store(tasks=[
            _task(task_id=1, status="✅ Done"),
            _task(task_id=2),
        ])
        todo_mod.show_summary(store)
        out = capsys.readouterr().out
        assert "Done" in out
        assert "Pending" in out

    def test_shows_overdue_count(self, todo_mod, capsys):
        overdue = _task("Late", task_id=1, due_date="2020-01-01")
        store = _store(tasks=[overdue])
        todo_mod.show_summary(store)
        out = capsys.readouterr().out
        assert "Overdue" in out

    def test_shows_streak(self, todo_mod, capsys):
        store = _store(tasks=[_task()], streaks={"count": 7})
        todo_mod.show_summary(store)
        assert "7" in capsys.readouterr().out

    def test_empty_store_no_crash(self, todo_mod):
        store = _store()
        todo_mod.show_summary(store)   # should not raise

    def test_shows_top_category(self, todo_mod, capsys):
        tasks = [
            _task("T1", category="📚 Study", task_id=1),
            _task("T2", category="📚 Study", task_id=2),
            _task("T3", category="💼 Work",  task_id=3),
        ]
        store = _store(tasks=tasks)
        todo_mod.show_summary(store)
        assert "Study" in capsys.readouterr().out
