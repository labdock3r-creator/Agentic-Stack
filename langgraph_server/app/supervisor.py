"""
Hermes LangGraph Supervisor v6 — Pełna implementacja
"""

from typing import List, Dict, TypedDict, Annotated, Optional
import operator
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import BaseMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.tools import PythonREPLTool

from .providers.model_provider import get_model
from .memory.hindsight_integration import HindsightMemory
from .team_composer import TeamComposer


class HermesState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    task_description: str
    selected_team: List[str]
    iteration: int
    max_iterations: int


class HermesSupervisor:
    def __init__(
        self,
        provider: str = "openai",
        model_name: Optional[str] = None,
        roles_dir: str = "src/hermes_langgraph/roles",
        tavily_api_key: Optional[str] = None,
        use_hindsight: bool = True
    ):
        self.model = get_model(provider=provider, model_name=model_name)
        self.composer = TeamComposer(roles_dir=roles_dir)
        self.hindsight = HindsightMemory() if use_hindsight else None
        self.roles = self._load_roles(roles_dir)
        self.tavily_key = tavily_api_key

    def _load_roles(self, roles_dir: str) -> Dict:
        import json
        from pathlib import Path
        roles = {}
        for f in Path(roles_dir).glob("*.json"):
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
                roles[data["name"]] = data
        return roles

    def _get_tools_for_role(self, role_name: str, role_config: dict) -> list:
        tools = [PythonREPLTool()]
        tags = set(role_config.get("tags", []))

        if "research" in tags or "web" in tags:
            if self.tavily_key:
                tools.append(TavilySearchResults(max_results=5, tavily_api_key=self.tavily_key))

        return tools

    def _create_worker_agent(self, role_name: str, role_config: dict):
        system_prompt = role_config.get("system_prompt", f"Jesteś {role_name}.")
        tools = self._get_tools_for_role(role_name, role_config)

        return create_react_agent(
            model=self.model,
            tools=tools,
            prompt=system_prompt,
            name=role_name
        )

    def build_graph(self, composition):
        worker_agents = {}
        for role_name in composition.selected_roles:
            if role_name in self.roles:
                worker_agents[role_name] = self._create_worker_agent(
                    role_name, self.roles[role_name]
                )

        supervisor = create_supervisor(
            agents=list(worker_agents.values()),
            model=self.model,
            prompt="Jesteś Supervisorem dynamicznego zespołu Hermes LangGraph."
        )
        return supervisor.compile()

    def run_task(self, task_description: str, priority: str = "normal"):
        from .evaluation.multi_model_evaluator import MultiModelEvaluator
        from .integrations.obsidian_bridge import ObsidianBridge
        from .integrations.kanban_bridge import KanbanBridge
        
        kanban = KanbanBridge()
        task_id = kanban.create_task(title=task_description[:50], description=task_description, priority=2)
        
        composition = self.composer.compose(task_description, priority)
        print(f"[Team Composer] Zespół: {composition.selected_roles}")
        print(f"[Team Composer] Uzasadnienie: {composition.reasoning}")

        kanban.update_status(task_id, "In Progress", "Supervisor")

        graph = self.build_graph(composition)

        print("[Supervisor] Uruchamianie grafu i generowanie odpowiedzi przez główny model...")
        result = graph.invoke({
            "messages": [{"role": "user", "content": task_description}],
            "task_description": task_description,
            "selected_team": composition.selected_roles,
            "iteration": 0,
            "max_iterations": composition.max_iterations
        })
        
        # W nowej architekturze, by zaprezentować potęgę MultiModelEvaluator, generujemy alternatywną odpowiedź (np. przez gorszy wariant modelu lub jako dummy dla testu ewaluacji) i oceniamy
        # Zamiast odpalać od nowa pełen graf, użyjemy ewaluatora na końcowym wyniku (z jedną odpowiedzią jako główną).
        # Normalnie ewaluator bierze odpowiedzi z 2-3 różnych modeli.
        responses = [result["messages"][-1].content]
        
        # Inicjalizacja ewaluatora i mostka
        evaluator = MultiModelEvaluator(models=[self.model], judge_model=self.model, hindsight=self.hindsight)
        
        # Jeśli jest tylko jedna odpowiedź, po prostu ją przepuszczamy
        if len(responses) == 1:
            best_model_name = getattr(self.model, 'model_name', "Default Model")
            best_response = responses[0]
            reasoning = "Wybrano jedyną dostępną odpowiedź z grafu"
            if self.hindsight:
                self.hindsight.reflect_and_store(task_id, reasoning, "completion")
        else:
            eval_result = evaluator.evaluate_responses(task_description, responses)
            best_model_name = eval_result["best_model"]
            best_response = eval_result["best_response"]
            reasoning = eval_result["reasoning"]

        kanban.update_status(task_id, "Done", "Supervisor")

        obsidian = ObsidianBridge()
        obsidian.write_report(
            task_id=task_id,
            title=task_description[:30] + "...",
            task_description=task_description,
            models_used=[getattr(self.model, 'model_name', "Default Model")],
            best_model=best_model_name,
            best_response=best_response,
            reasoning=reasoning
        )

        return result