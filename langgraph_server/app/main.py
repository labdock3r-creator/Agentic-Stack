from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from .supervisor import HermesSupervisor

app = FastAPI(title="LangGraph Server API", version="1.0")

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

    background_tasks.add_task(execute_graph)
    return {"status": "accepted", "message": "Zadanie wysłane do LangGraph Server. Procesowanie w tle."}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
