# =====================================
#   To-Do List - Decode Labs Project 1
#   Author: Divya Bharti
#   Batch: 2026
#   Intern: Python Programming Intern
# =====================================
#
#  FEATURES:
#   ✔ Priority levels (High / Medium / Low)
#   ✔ 5 task categories
#   ✔ Due-date tracking with overdue detection
#   ✔ Mark tasks complete (keeps history)
#   ✔ Edit existing tasks
#   ✔ Smart search (name + note)
#   ✔ Streak counter — consecutive days with ≥1 completion
#   ✔ Progress bar + full summary dashboard
#   ✔ Persistent JSON storage (survives restarts)
#   ✔ Undo last delete
# =====================================

import json
import os
from datetime import datetime, date, timedelta

SAVE_FILE   = "todo_data.json"

PRIORITIES      = {"1": "🔴 HIGH", "2": "🟡 MEDIUM", "3": "🟢 LOW"}
PRIORITY_ORDER  = {"🔴 HIGH": 0, "🟡 MEDIUM": 1, "🟢 LOW": 2}
CATEGORIES      = {
    "1": "💼 Work",
    "2": "🏠 Personal",
    "3": "📚 Study",
    "4": "🏥 Health",
    "5": "🛒 Shopping",
}
STATUS_DONE    = "✅ Done"
STATUS_PENDING = "⏳ Pending"


# ─────────────────────────── Persistence ──────────────────────────────────────

def _default_store() -> dict:
    return {"tasks": [], "deleted": [], "streaks": {}}


def load_store() -> dict:
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Back-compat: old format stored a plain list
                if isinstance(data, list):
                    return {"tasks": data, "deleted": [], "streaks": {}}
                return data
        except (json.JSONDecodeError, IOError):
            pass
    return _default_store()


def save_store(store: dict) -> None:
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2, ensure_ascii=False)


# ─────────────────────────── Helpers ──────────────────────────────────────────

def _make_id() -> int:
    return int(datetime.now().timestamp() * 1000)


def _today() -> str:
    return date.today().isoformat()


def _progress_bar(done: int, total: int, width: int = 20) -> str:
    pct  = done / total if total else 0
    fill = int(pct * width)
    return "█" * fill + "░" * (width - fill), pct * 100


def _pick_category() -> str:
    print("  Category: " + "  ".join(f"{k}) {v}" for k, v in CATEGORIES.items()))
    ch = input("  Choose (1-5) [default 1]: ").strip() or "1"
    return CATEGORIES.get(ch, "💼 Work")


def _pick_priority() -> str:
    print("  Priority: 1) 🔴 High   2) 🟡 Medium   3) 🟢 Low")
    ch = input("  Choose (1-3) [default 2]: ").strip() or "2"
    return PRIORITIES.get(ch, "🟡 MEDIUM")


def _pick_due() -> str | None:
    raw = input("  Due date (YYYY-MM-DD) or Enter to skip: ").strip()
    if not raw:
        return None
    try:
        datetime.strptime(raw, "%Y-%m-%d")
        return raw
    except ValueError:
        print("  ⚠️  Invalid date — skipped.")
        return None


def _update_streak(store: dict) -> None:
    """Increment or reset the daily completion streak."""
    streaks = store.setdefault("streaks", {})
    today   = _today()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    last = streaks.get("last_completion_date")

    if last == today:
        return                              # already counted today
    elif last == yesterday:
        streaks["count"] = streaks.get("count", 0) + 1
    else:
        streaks["count"] = 1               # reset streak
    streaks["last_completion_date"] = today


# ─────────────────────────── Core Operations ──────────────────────────────────

def add_task(store: dict) -> None:
    print("\n── Add New Task ──────────────────────────────")
    name = input("  Task name: ").strip()
    if not name:
        print("  ⚠️  Task name cannot be empty!")
        return

    priority = _pick_priority()
    category = _pick_category()
    due_date = _pick_due()
    note     = input("  Note (optional): ").strip()

    task = {
        "id":       _make_id(),
        "name":     name,
        "priority": priority,
        "category": category,
        "due_date": due_date,
        "note":     note,
        "status":   STATUS_PENDING,
        "created":  _today(),
        "completed_on": None,
    }
    store["tasks"].append(task)
    save_store(store)
    print(f"  ✅ Added  [{priority}]  {name}" + (f"  📅 Due: {due_date}" if due_date else ""))


def _filtered_sorted(tasks: list, filter_status=None, filter_cat=None,
                     sort_by="priority") -> list:
    out = tasks[:]
    if filter_status:
        out = [t for t in out if t["status"] == filter_status]
    if filter_cat:
        out = [t for t in out if t["category"] == filter_cat]

    today = _today()
    if sort_by == "priority":
        out.sort(key=lambda t: (PRIORITY_ORDER.get(t["priority"], 9),
                                t["due_date"] or "9999"))
    elif sort_by == "due_date":
        out.sort(key=lambda t: (t["due_date"] or "9999", PRIORITY_ORDER.get(t["priority"], 9)))
    elif sort_by == "category":
        out.sort(key=lambda t: t["category"])
    elif sort_by == "created":
        out.sort(key=lambda t: t.get("created", ""))
    return out


def view_tasks(store: dict, filter_status=None, filter_cat=None,
               sort_by="priority", heading: str = "📋 Tasks") -> list:
    tasks    = store["tasks"]
    filtered = _filtered_sorted(tasks, filter_status, filter_cat, sort_by)

    if not filtered:
        print("\n  📝 No tasks found.")
        return []

    today = _today()
    print(f"\n  {heading}")
    print(f"  {'─'*66}")
    print(f"  {'#':<4} {'Task':<24} {'Priority':<12} {'Status':<12} Due")
    print(f"  {'─'*66}")
    for i, t in enumerate(filtered, 1):
        due  = t.get("due_date") or "—"
        flag = " ⚠️" if (due != "—" and due < today and t["status"] != STATUS_DONE) else ""
        print(f"  {i:<4} {t['name'][:23]:<24} {t['priority']:<12} {t['status']:<12} {due}{flag}")
        sub = []
        if t.get("note"):
            sub.append(f"📌 {t['note']}")
        sub.append(t["category"])
        if t.get("completed_on"):
            sub.append(f"✔ {t['completed_on']}")
        print(f"       {' | '.join(sub)}")
    print(f"  {'─'*66}")
    all_done = sum(1 for t in tasks if t["status"] == STATUS_DONE)
    bar, pct = _progress_bar(all_done, len(tasks))
    print(f"  Total {len(tasks)} | ✅ {all_done} done | ⏳ {len(tasks)-all_done} pending")
    print(f"  Overall progress: [{bar}] {pct:.0f}%")
    return filtered


def complete_task(store: dict) -> None:
    shown = view_tasks(store, filter_status=STATUS_PENDING, heading="⏳ Pending Tasks")
    if not shown:
        return
    try:
        idx = int(input("\n  Enter # to mark done: ")) - 1
        if not (0 <= idx < len(shown)):
            print("  ❌ Invalid number.")
            return
    except ValueError:
        print("  ❌ Please enter a valid number.")
        return

    # Find in master list by id
    target_id = shown[idx]["id"]
    for t in store["tasks"]:
        if t["id"] == target_id:
            t["status"]       = STATUS_DONE
            t["completed_on"] = _today()
            _update_streak(store)
            save_store(store)
            streak = store.get("streaks", {}).get("count", 1)
            print(f"  🎉 Completed: {t['name']}  |  🔥 Streak: {streak} day(s)!")
            return


def edit_task(store: dict) -> None:
    shown = view_tasks(store, heading="✏️  Edit a Task")
    if not shown:
        return
    try:
        idx = int(input("\n  Enter # to edit: ")) - 1
        if not (0 <= idx < len(shown)):
            print("  ❌ Invalid number.")
            return
    except ValueError:
        print("  ❌ Please enter a valid number.")
        return

    target_id = shown[idx]["id"]
    for t in store["tasks"]:
        if t["id"] == target_id:
            print(f"  Editing: {t['name']}  (press Enter to keep current value)")
            new_name = input(f"  New name [{t['name']}]: ").strip()
            if new_name:
                t["name"] = new_name
            t["priority"] = _pick_priority()
            t["category"] = _pick_category()
            t["due_date"]  = _pick_due() or t["due_date"]
            new_note = input(f"  New note [{t.get('note','—')}]: ").strip()
            if new_note:
                t["note"] = new_note
            save_store(store)
            print(f"  ✅ Task updated: {t['name']}")
            return


def delete_task(store: dict) -> None:
    shown = view_tasks(store, heading="🗑️  Delete a Task")
    if not shown:
        return
    try:
        idx = int(input("\n  Enter # to delete: ")) - 1
        if not (0 <= idx < len(shown)):
            print("  ❌ Invalid number.")
            return
    except ValueError:
        print("  ❌ Please enter a valid number.")
        return

    target_id = shown[idx]["id"]
    for i, t in enumerate(store["tasks"]):
        if t["id"] == target_id:
            removed = store["tasks"].pop(i)
            store["deleted"].append(removed)   # undo buffer
            save_store(store)
            print(f"  🗑️  Deleted: {removed['name']}  (type 'u' in menu to undo)")
            return


def undo_delete(store: dict) -> None:
    if not store.get("deleted"):
        print("  ℹ️  Nothing to undo.")
        return
    restored = store["deleted"].pop()
    store["tasks"].append(restored)
    save_store(store)
    print(f"  ↩️  Restored: {restored['name']}")


def search_tasks(store: dict) -> None:
    kw = input("  Search keyword: ").strip().lower()
    if not kw:
        return
    results = [t for t in store["tasks"]
               if kw in t["name"].lower() or kw in (t.get("note") or "").lower()
               or kw in t["category"].lower()]
    if results:
        # Wrap in temp store for display
        view_tasks({"tasks": results, "deleted": [], "streaks": {}},
                   heading=f"🔍 Results for '{kw}'")
    else:
        print(f"  🔍 No tasks found matching '{kw}'.")


def show_summary(store: dict) -> None:
    tasks = store["tasks"]
    total = len(tasks)
    done  = sum(1 for t in tasks if t["status"] == STATUS_DONE)
    today = _today()
    overdue = sum(
        1 for t in tasks
        if t.get("due_date") and t["due_date"] < today and t["status"] != STATUS_DONE
    )
    due_today = sum(
        1 for t in tasks
        if t.get("due_date") == today and t["status"] == STATUS_PENDING
    )

    bar, pct = _progress_bar(done, total)
    streak    = store.get("streaks", {}).get("count", 0)

    print("\n  ╔══════════════════════════════════╗")
    print("  ║       📊  Task Dashboard         ║")
    print("  ╠══════════════════════════════════╣")
    print(f"  ║  Total       : {total:<18}║")
    print(f"  ║  ✅ Done     : {done:<18}║")
    print(f"  ║  ⏳ Pending  : {total - done:<18}║")
    print(f"  ║  ⚠️  Overdue  : {overdue:<18}║")
    print(f"  ║  📅 Due Today: {due_today:<18}║")
    print(f"  ║  🔥 Streak   : {streak} day(s){'':<11}║")
    print("  ╠══════════════════════════════════╣")
    print(f"  ║  [{bar}] {pct:>4.0f}%  ║")
    print("  ╠══════════════════════════════════╣")

    # By priority
    pri_counts = {}
    for t in tasks:
        pri_counts[t["priority"]] = pri_counts.get(t["priority"], 0) + 1
    for pri in ["🔴 HIGH", "🟡 MEDIUM", "🟢 LOW"]:
        cnt = pri_counts.get(pri, 0)
        if cnt:
            print(f"  ║  {pri:<12}: {cnt:<20}║")

    # Top category
    cat_counts = {}
    for t in tasks:
        cat_counts[t["category"]] = cat_counts.get(t["category"], 0) + 1
    if cat_counts:
        top_cat = max(cat_counts, key=cat_counts.get)
        print(f"  ║  Top category: {top_cat[:18]:<18}║")
    print("  ╚══════════════════════════════════╝")


# ─────────────────────────── Main ─────────────────────────────────────────────

def main() -> None:
    store = load_store()

    # Greet with streak info if available
    streak = store.get("streaks", {}).get("count", 0)
    print("=" * 44)
    print("   🐍 Divya's Smart To-Do List App")
    print("      Powered by DecodeLabs | 2026")
    if streak:
        print(f"      🔥 Current Streak: {streak} day(s)!")
    print("=" * 44)

    MENU = {
        "1": ("➕  Add task",                   lambda: add_task(store)),
        "2": ("📋  View all tasks",              lambda: view_tasks(store)),
        "3": ("🔼  View by priority",            lambda: view_tasks(store, sort_by="priority",
                                                                    heading="🔼 By Priority")),
        "4": ("📅  View by due date",            lambda: view_tasks(store, sort_by="due_date",
                                                                    heading="📅 By Due Date")),
        "5": ("✅  Mark task as done",           lambda: complete_task(store)),
        "6": ("✏️   Edit task",                   lambda: edit_task(store)),
        "7": ("🗑️   Delete task",                 lambda: delete_task(store)),
        "8": ("↩️   Undo last delete",            lambda: undo_delete(store)),
        "9": ("🔎  Search tasks",                lambda: search_tasks(store)),
        "0": ("📊  Summary dashboard",           lambda: show_summary(store)),
        "x": ("🚪  Exit",                        None),
    }

    while True:
        print("\n── Menu ────────────────────────────────────")
        for key, (label, _) in MENU.items():
            print(f"  {key}.  {label}")
        print("────────────────────────────────────────────")
        choice = input("  Enter choice: ").strip().lower()

        if choice == "x":
            print("\n  👋 Goodbye, Divya! Keep crushing it! 🌸🚀")
            break
        elif choice in MENU:
            _, action = MENU[choice]
            action()
        else:
            print("  ⚠️  Invalid choice.")


if __name__ == "__main__":
    main()
