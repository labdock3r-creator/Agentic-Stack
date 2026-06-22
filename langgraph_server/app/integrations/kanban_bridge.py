"""
Kanban Bridge v6 — Integracja z Hermes Kanban Board
"""

from typing import Optional
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

import sqlite3
import time
import uuid

class KanbanBridge:
    def __init__(self, db_path="/home/r00t/.hermes/kanban.db"):
        self.db_path = db_path
        # Upewniamy się że tabela istnieje i ew. logujemy
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1 FROM tasks LIMIT 1")
        except Exception as e:
            print(f"[KanbanBridge] Błąd połączenia z bazą: {e}")

    def create_task(self, title: str, description: str, priority: int = 2):
        task_id = f"TASK-{str(uuid.uuid4())[:8].upper()}"
        created_at = int(time.time())
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO tasks (id, title, body, status, priority, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (task_id, title, description, "todo", priority, created_at)
                )
            print(f"[Kanban] Task created in DB: {task_id}")
        except Exception as e:
            print(f"[KanbanBridge] Błąd przy dodawaniu zadania: {e}")
        return task_id

    def update_status(self, task_id: str, phase: str, agent: str, notes: str = ""):
        # W prawdziwym Hermesie kolumna to status (np. 'In Progress', 'Done', 'Backlog') i assignee
        status_map = {
            "Architektura (ARCHI)": "in_progress",
            "Review (FORGE)": "in_progress",
            "Zakończone (DONE)": "done"
        }
        status_val = status_map.get(phase, phase)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE tasks SET status = ?, assignee = ? WHERE id = ?",
                    (status_val, agent, task_id)
                )
            print(f"[Kanban] Aktualizacja statusu {task_id} -> {status_val} przez {agent}")
        except Exception as e:
            print(f"[KanbanBridge] Błąd przy aktualizacji statusu: {e}")

    def add_reflection(self, task_id: str, reflection: str):
        print(f"[Kanban] Reflection dla {task_id}: {reflection[:80]}...")
        # Wrzucenie reflection jako note wymagałoby aktualizacji `body` lub oddzielnej tabeli. W uproszczeniu wrzucamy jako append do body
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT body FROM tasks WHERE id = ?", (task_id,))
                row = cursor.fetchone()
                if row:
                    new_body = str(row[0]) + f"\n\n--- Hindsight Reflection ---\n{reflection}"
                    conn.execute("UPDATE tasks SET body = ? WHERE id = ?", (new_body, task_id))
        except Exception as e:
            pass