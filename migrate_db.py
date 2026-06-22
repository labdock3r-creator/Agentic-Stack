import sqlite3

db_path = "/home/r00t/.hermes/kanban.db"
with sqlite3.connect(db_path) as conn:
    conn.execute("UPDATE tasks SET status = 'in_progress' WHERE status = 'In Progress'")
    conn.execute("UPDATE tasks SET status = 'todo' WHERE status = 'Backlog'")
    conn.execute("UPDATE tasks SET status = 'done' WHERE status = 'Done'")
    conn.commit()
print("Baza zaktualizowana.")
