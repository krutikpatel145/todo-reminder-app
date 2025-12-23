# todo_app.py - A simple CLI todo list with reminders because who doesn't need a nudge sometimes?
# Author: Alex (just a dev who hates forgetting stuff)
# Date: Dec 2025 - Yeah, it's basic but it works for me.

import json
import datetime
import os
from typing import List, Dict, Optional

# File to store tasks
TASKS_FILE = 'tasks.json'

class Task:
    def __init__(self, description: str, due_date: str = None, reminder_days: int = 0):
        self.id = None  # Will be set later
        self.description = description
        self.due_date = due_date  # Format: YYYY-MM-DD
        self.reminder_days = reminder_days  # Days before due to remind
        self.completed = False
        self.created = datetime.datetime.now().isoformat()

    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'due_date': self.due_date,
            'reminder_days': self.reminder_days,
            'completed': self.completed,
            'created': self.created
        }

    @classmethod
    def from_dict(cls, data: Dict):
        task = cls(data['description'], data['due_date'], data['reminder_days'])
        task.id = data['id']
        task.completed = data['completed']
        task.created = data['created']
        return task

class TodoManager:
    def __init__(self):
        self.tasks: List[Task] = []
        self.load_tasks()

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(t) for t in data]
                print(f"Loaded {len(self.tasks)} tasks from file. Good to go!")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Oops, couldn't load tasks: {e}. Starting fresh.")
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        data = [t.to_dict() for t in self.tasks]
        with open(TASKS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        # print("Saved tasks. You're welcome.")

    def add_task(self, description: str, due_date: Optional[str] = None, reminder_days: int = 0):
        task = Task(description, due_date, reminder_days)
        # Simple ID: len + 1
        task.id = len(self.tasks) + 1
        self.tasks.append(task)
        self.save_tasks()
        print(f"Added task '{description}' with ID {task.id}. Nice one!")

    def list_tasks(self, show_completed: bool = False):
        if not self.tasks:
            print("No tasks yet. Add some!")
            return

        active = [t for t in self.tasks if not t.completed] if not show_completed else self.tasks
        if not active:
            print("All done! Or nothing to show.")
            return

        print("\n--- Your Tasks ---")
        for task in active:
            status = "✓" if task.completed else "○"
            due = f" (due {task.due_date})" if task.due_date else ""
            reminder = f" (remind in {task.reminder_days} days)" if task.reminder_days else ""
            print(f"{status} [{task.id}] {task.description}{due}{reminder}")

    def complete_task(self, task_id: int):
        for task in self.tasks:
            if task.id == task_id:
                task.completed = True
                self.save_tasks()
                print(f"Marked task {task_id} as done. Progress!")
                return
        print(f"Task {task_id} not found. Check your list?")

    def delete_task(self, task_id: int):
        self.tasks = [t for t in self.tasks if t.id != task_id]
        # Renumber IDs because why not keep it simple
        for i, task in enumerate(self.tasks, 1):
            task.id = i
        self.save_tasks()
        print(f"Deleted task {task_id}. Gone forever.")

    def check_reminders(self):
        now = datetime.datetime.now()
        reminders = []
        for task in self.tasks:
            if task.due_date and not task.completed:
                try:
                    due = datetime.datetime.strptime(task.due_date, '%Y-%m-%d').date()
                    remind_date = due - datetime.timedelta(days=task.reminder_days)
                    if now.date() >= remind_date:
                        reminders.append(task)
                except ValueError:
                    print(f"Bad date format for task {task.id}: {task.due_date}. Skipping.")

        if reminders:
            print("\n🚨 Reminders! Don't forget:")
            for task in reminders:
                print(f"  - {task.description} (due {task.due_date})")
        else:
            print("No reminders today. Relax.")

def main():
    manager = TodoManager()
    print("Welcome to TodoReminder! Type 'help' for commands.")

    while True:
        try:
            cmd = input("\n> ").strip().lower()
            parts = cmd.split()

            if not parts:
                continue

            action = parts[0]

            if action == 'quit' or action == 'q':
                print("Bye! Don't forget your tasks.")
                break

            elif action == 'add' or action == 'a':
                if len(parts) < 2:
                    print("Usage: add 'description' [due YYYY-MM-DD] [remind N days]")
                    continue
                desc = ' '.join(parts[1:])  # Simple, grab rest as desc
                # Parse optional due and remind
                due = None
                remind = 0
                # Hacky parse: look for date pattern or number at end
                full_desc = ' '.join(parts[1:])
                if ' ' in full_desc:
                    last_two = full_desc.split()[-2:]
                    if len(last_two) == 2 and last_two[0] == 'due' and '-' in last_two[1]:
                        due = last_two[1]
                        desc = full_desc.replace(f"due {due}", "").strip()
                    elif len(parts) >= 3 and parts[-1].isdigit():
                        remind = int(parts[-1])
                        desc = ' '.join(parts[1:-1])
                        if len(parts) >= 4 and parts[-2] == 'due' and '-' in parts[-3]:
                            due = parts[-3]
                            desc = ' '.join(parts[1:-2])
                manager.add_task(desc, due, remind)

            elif action == 'list' or action == 'l':
                show_all = len(parts) > 1 and parts[1] == 'all'
                manager.list_tasks(show_all)

            elif action == 'complete' or action == 'c':
                if len(parts) < 2:
                    print("Usage: complete ID")
                    continue
                try:
                    tid = int(parts[1])
                    manager.complete_task(tid)
                except ValueError:
                    print("ID must be a number.")

            elif action == 'delete' or action == 'd':
                if len(parts) < 2:
                    print("Usage: delete ID")
                    continue
                try:
                    tid = int(parts[1])
                    manager.delete_task(tid)
                except ValueError:
                    print("ID must be a number.")

            elif action == 'remind' or action == 'r':
                manager.check_reminders()

            elif action == 'help' or action == 'h':
                print("""
Commands:
  add 'Buy milk due 2025-12-25 remind 1'  - Add task (due optional YYYY-MM-DD, remind optional days before)
  list [all]                               - List tasks (all shows completed too)
  complete ID / c ID                       - Mark done
  delete ID / d ID                         - Remove task
  remind / r                               - Check reminders now
  quit / q                                 - Exit
                """)

            else:
                print("Unknown command. Try 'help'.")

        except KeyboardInterrupt:
            print("\n\nExiting gracefully.")
            break
        except Exception as e:
            print(f"Something went wrong: {e}. Keep going!")

if __name__ == '__main__':
    main()
