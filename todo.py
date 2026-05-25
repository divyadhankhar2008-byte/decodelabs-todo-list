# =====================================
#   To-Do List - Decode Labs Project 1
#   Author: Divya Bharti
#   Batch: 2026
#   Intern: Python Programming Intern
# =====================================

my_tasks = []

def add_task(task):
    """Add a new task to the list."""
    my_tasks.append(task)
    print(f"✅ Task added: {task}")

def view_tasks():
    """Display all tasks in the list."""
    if len(my_tasks) == 0:
        print("📝 No tasks yet! Add some tasks.")
    else:
        print("\n📋 Your To-Do List:")
        for index, task in enumerate(my_tasks, 1):
            print(f"  {index}. {task}")

def delete_task(task_number):
    """Delete a task by its number."""
    if task_number < 1 or task_number > len(my_tasks):
        print("❌ Invalid task number!")
    else:
        removed = my_tasks.pop(task_number - 1)
        print(f"🗑️ Task removed: {removed}")

def main():
    print("=" * 35)
    print("   🐍 Divya's To-Do List App")
    print("      Powered by DecodeLabs")
    print("=" * 35)

    while True:
        print("\nWhat do you want to do?")
        print("1. Add task")
        print("2. View tasks")
        print("3. Delete task")
        print("4. Exit")

        choice = input("\nEnter choice (1/2/3/4): ").strip()

        if choice == "1":
            task = input("Enter task: ").strip()
            if task:
                add_task(task)
            else:
                print("⚠️ Task cannot be empty!")

        elif choice == "2":
            view_tasks()

        elif choice == "3":
            view_tasks()
            if len(my_tasks) > 0:
                try:
                    num = int(input("\nEnter task number to delete: "))
                    delete_task(num)
                except ValueError:
                    print("❌ Please enter a valid number!")

        elif choice == "4":
            print("\n👋 Goodbye! Keep coding! 🌸")
            break

        else:
            print("⚠️ Invalid choice! Please enter 1, 2, 3 or 4.")

if __name__ == "__main__":
    main()
