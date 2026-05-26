# 🐍 Smart To-Do List App — Project 1

> **DecodeLabs Industrial Training Kit | Batch 2026**
> Author: Divya Bharti | Python Programming Intern

---

## 📌 Project Overview

A feature-rich, command-line Python To-Do List application that goes far beyond basic task management. Built as Project 1 of the DecodeLabs Python Programming Industrial Training Kit, this app demonstrates mastery of core Python concepts while delivering a genuinely useful productivity tool.

Users can **add, view, edit, complete, delete, search, and analyse** tasks through an intuitive menu-driven interface — with all data surviving restarts via JSON persistence.

---

## ✨ Features

| Feature | Description |
|---|---|
| ➕ Add Tasks | Name, priority, category, due date, and optional notes |
| 🔴🟡🟢 Priority Levels | High / Medium / Low with smart sort order |
| 🗂️ 5 Categories | Work, Personal, Study, Health, Shopping |
| 📅 Due Date Tracking | Overdue detection with ⚠️ warning flags |
| ✅ Mark Complete | Preserves completion date in history |
| ✏️ Edit Tasks | Update any field on existing tasks |
| 🗑️ Delete + Undo | Delete tasks with single-step undo recovery |
| 🔎 Smart Search | Searches task name, notes, and category |
| 🔥 Streak Counter | Tracks consecutive days with ≥1 completion |
| 📊 Dashboard | Progress bar, overdue count, due-today count, priority breakdown |
| 💾 JSON Persistence | All data saved to `todo_data.json` — survives restarts |
| 🔄 Sort Options | Sort by priority, due date, category, or created date |

---

## 🎯 Key Concepts Demonstrated

| Concept | Implementation |
|---|---|
| Lists & Dicts | `store["tasks"]` — dynamic task storage with rich metadata |
| Functions | Fully modular: `add_task()`, `view_tasks()`, `edit_task()`, etc. |
| `enumerate()` | Numbered task display in all views |
| While Loop | Menu keeps running until user exits with `x` |
| Input Validation | Guards empty names, invalid numbers, bad dates |
| Defensive Coding | `try / except ValueError` on all numeric inputs |
| File I/O | `json.load()` / `json.dump()` for persistent storage |
| `datetime` module | Due date parsing, overdue detection, streak logic |
| Backward Compatibility | Handles old plain-list format gracefully on load |

---

## 🏗️ Architecture

The project follows a clean **Input → Process → Output** scaffold:

```
Phase 1 — Load        : Read JSON store or initialise defaults
Phase 2 — Menu Loop   : Display menu, capture choice, dispatch action
Phase 3 — Action      : Mutate store in memory
Phase 4 — Persist     : Write updated store back to JSON
Phase 5 — Feedback    : Print result to user
```

---

## 🚀 How to Run

### Prerequisites
- Python **3.10+** (uses `str | None` type hints)
- No external libraries — uses stdlib only (`json`, `os`, `datetime`)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/divyadhankhar2008-byte/decodelabs-todo-list.git

# 2. Navigate into the folder
cd decodelabs-todo-list

# 3. Run the script
python todo.py
```

---

## 🖥️ Sample Output

```
============================================
   🐍 Divya's Smart To-Do List App
      Powered by DecodeLabs | 2026
      🔥 Current Streak: 3 day(s)!
============================================

── Menu ────────────────────────────────────
  1.  ➕  Add task
  2.  📋  View all tasks
  3.  🔼  View by priority
  4.  📅  View by due date
  5.  ✅  Mark task as done
  6.  ✏️   Edit task
  7.  🗑️   Delete task
  8.  ↩️   Undo last delete
  9.  🔎  Search tasks
  0.  📊  Summary dashboard
  x.  🚪  Exit
────────────────────────────────────────────
```

```
  ╔══════════════════════════════════╗
  ║       📊  Task Dashboard         ║
  ╠══════════════════════════════════╣
  ║  Total       : 8                 ║
  ║  ✅ Done     : 5                 ║
  ║  ⏳ Pending  : 3                 ║
  ║  ⚠️  Overdue  : 1                 ║
  ║  📅 Due Today: 2                 ║
  ║  🔥 Streak   : 3 day(s)          ║
  ╠══════════════════════════════════╣
  ║  [████████████████░░░░] 62%      ║
  ╚══════════════════════════════════╝
```

---

## 📁 File Structure

```
decodelabs-todo-list/
├── todo.py           # Main application
├── todo_data.json    # Auto-generated on first run (gitignored)
└── README.md
```

---

## 💡 What I Learned

By building this project I practised:

- **Modular design** — every action is an isolated function
- **State management** — a single `store` dict passed through all functions
- **Data persistence** — reading and writing structured JSON
- **UX thinking** — progress bars, streak counters, and overdue warnings make the CLI feel polished
- **Defensive programming** — every user input is validated before use

---

## 👩‍💻 Author

**Divya Bharti**
Python Programming Intern | DecodeLabs Batch 2026
