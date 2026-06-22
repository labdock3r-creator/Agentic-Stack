"""
Team Composer v6
"""

from dataclasses import dataclass
from typing import List
from pathlib import Path
import json

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None


@dataclass
class TeamComposition:
    task_id: str
    task_description: str
    selected_roles: List[str]
    reasoning: str
    priority: str = "normal"
    max_iterations: int = 3
    use_swarm_handoff: bool = False


class TeamComposer:
    def __init__(self, roles_dir: str = "src/hermes_langgraph/roles"):
        self.roles_dir = Path(roles_dir)
        self.available_roles = self._load_roles()

    def _load_roles(self):
        roles = {}
        for f in self.roles_dir.glob("*.json"):
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
                roles[data["name"]] = data
        return roles

    def compose(self, task_description: str, priority: str = "normal") -> TeamComposition:
        task_lower = task_description.lower()
        selected = ["ARCHI"]

        if any(kw in task_lower for kw in ["web", "ui", "frontend", "interface"]):
            selected.append("FRONT")
        if any(kw in task_lower for kw in ["implement", "code", "backend", "api"]):
            selected.append("FORGE")
        if any(kw in task_lower for kw in ["test", "security", "audit", "review"]):
            selected.append("SENTINEL")
        if any(kw in task_lower for kw in ["docker", "deploy", "devops"]):
            selected.append("HELIX")
        if any(kw in task_lower for kw in ["research", "trend", "analiz"]):
            selected.append("RESEARCH_AGENT")

        return TeamComposition(
            task_id=f"task-{hash(task_description) % 100000}",
            task_description=task_description,
            selected_roles=list(dict.fromkeys(selected)),
            reasoning="Regułowa analiza zadania",
            priority=priority,
            use_swarm_handoff=len(selected) >= 3 and priority == "high"
        )