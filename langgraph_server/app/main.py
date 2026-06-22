from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
from .supervisor import HermesSupervisor
import datetime

app = FastAPI(title="LangGraph Server API", version="1.0")

# Prosta struktura do trzymania logów w pamięci
recent_tasks: List[dict] = []

html_template = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangGraph Factory Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: #e0e0e0; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: auto; }
        h1 { color: #00ffcc; text-align: center; }
        .card { background-color: #1e1e1e; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .task { border-left: 4px solid #00ffcc; padding-left: 10px; margin-bottom: 15px; }
        .time { font-size: 0.8em; color: #888; }
        .btn { background-color: #00ffcc; color: #121212; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-weight: bold; }
        .btn:hover { background-color: #00ccaa; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚙️ LangGraph Factory Dashboard</h1>
        <div class="card">
            <h2>Status Serwera: <span style="color: #00ffcc;">Online</span></h2>
            <p>Ten kontener nasłuchuje na polecenia z Hermesa i wykonuje je w tle korzystając z modeli NVIDIA NIM.</p>
            <button class="btn" onclick="location.reload()">Odśwież Logi</button>
        </div>
        <div class="card">
            <h2>Ostatnie Zlecenia:</h2>
            <div id="logs">
                {logs_html}
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def read_root():
    logs_html = ""
    if not recent_tasks:
        logs_html = "<p>Brak aktywnych zleceń. Czekam na webhooki z Hermesa...</p>"
    else:
        for t in reversed(recent_tasks[-10:]):
            logs_html += f"<div class='task'><div class='time'>{t['time']} | Priorytet: {t['priority']}</div><div>{t['desc']}</div></div>"
    return html_template.replace("{logs_html}", logs_html)


class TaskRequest(BaseModel):
    task_description: str
    priority: str = "normal"

@app.post("/run_task")
async def run_task_endpoint(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Endpoint pozwalający zewnętrznym aplikacjom (np. Hermes) zlecić wykonanie złożonego zadania.
    Zadanie wykonywane jest asynchronicznie, by nie blokować połączenia.
    """
    def execute_graph():
        print(f"Rozpoczęto generowanie grafu dla: {request.task_description}")
        supervisor = HermesSupervisor(
            provider="nvidia",
            model_name="meta/llama-3.3-70b-instruct",
            use_hindsight=True
        )
        supervisor.run_task(task_description=request.task_description, priority=request.priority)

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    recent_tasks.append({
        "time": now_str,
        "priority": request.priority,
        "desc": request.task_description
    })
    
    background_tasks.add_task(execute_graph)
    return {"status": "accepted", "message": "Zadanie wysłane do LangGraph Server. Procesowanie w tle."}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
