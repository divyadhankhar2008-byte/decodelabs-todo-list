# 🐍 To-Do List App — Project 1

> **DecodeLabs Industrial Training Kit | Batch 2026**
> **Author: Divya Bharti | Python Programming Intern**

---

## 📌 Project Overview

A command-line Python To-Do List application that allows users to **add**, **view**, and **delete** tasks interactively through a menu-driven interface. This project demonstrates core Python concepts including functions, lists, loops, and input validation.

---

## 🎯 Key Concepts Demonstrated

| Concept | Implementation |
|---|---|
| **Lists** | `my_tasks = []` stores all tasks dynamically |
| **Functions** | `add_task()`, `view_tasks()`, `delete_task()` — modular design |
| **enumerate()** | Displays tasks with numbered index |
| **While Loop** | Keeps the menu running until user exits |
| **Input Validation** | Guards against empty tasks, invalid numbers, and wrong menu choices |
| **Defensive Coding** | `try / except ValueError` on delete input |

---

## 🚀 How to Run

### Prerequisites
- Python 3.x installed

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/divyabharti/decodelabs-todo-list.git

# 2. Navigate into the folder
cd decodelabs-todo-list

# 3. Run the script
python todo.py
```

---

## 🖥️ Sample Output

```
===================================
   🐍 Divya's To-Do List App
      Powered by DecodeLabs
===================================

What do you want to do?
1. Add task
2. View tasks
3. Delete task
4. Exit

Enter choice (1/2/3/4): 1
Enter task: Complete Python project
✅ Task added: Complete Python project

Enter choice (1/2/3/4): 1
Enter task: Read documentation
✅ Task added: Read documentation

Enter choice (1/2/3/4): 2

📋 Your To-Do List:
  1. Complete Python project
  2. Read documentation

Enter choice (1/2/3/4): 3

📋 Your To-Do List:
  1. Complete Python project
  2. Read documentation

Enter task number to delete: 1
🗑️ Task removed: Complete Python project

Enter choice (1/2/3/4): 4

👋 Goodbye! Keep coding! 🌸
```

---

## ⚙️ Features

- ✅ **Add Task** — Append any task to your list (empty input rejected)
- 📋 **View Tasks** — Display all tasks in a numbered list
- 🗑️ **Delete Task** — Remove a task by its number with bounds checking
- 👋 **Exit** — Graceful shutdown with a goodbye message
- ⚠️ **Input Guards** — Handles invalid menu choices, empty tasks, and non-numeric input

---

## 📁 Project Structure

```
decodelabs-todo-list/
│
├── todo.py      # Main application script
└── README.md    # Project documentation
```

---

## 🏢 About DecodeLabs

**DecodeLabs** is an industrial training platform based in Greater Lucknow, India, focused on building real-world Python and backend development skills.

- 🌐 [www.decodelabs.tech](http://www.decodelabs.tech)
- 📧 decodelabs.tech@gmail.com
- 📞 +91 89330 06408

---

*Built with 💻 by Divya Bharti as part of the DecodeLabs Python Programming Industrial Training — Batch 2026*
