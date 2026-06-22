"""
LangGraph Studio Entry Point — Samodzielny graf do wizualizacji w Studio.
Ten plik nie korzysta z importów względnych (.dot), dzięki czemu CLI może go załadować bezpośrednio.
"""

import os
import sys
import json
from pathlib import Path

# Dodaj katalog app/ do ścieżki Pythona, żeby importy zadziałały bez kontekstu pakietu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langchain_experimental.tools import PythonREPLTool


def _load_roles():
    """Załaduj definicje ról agentów z plików JSON."""
    roles = {}
    roles_dir = Path(__file__).parent / "app" / "roles"
    if roles_dir.exists():
        for f in roles_dir.glob("*.json"):
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
                roles[data["name"]] = data
    return roles


def _build_studio_graph():
    """Zbuduj graf dla LangGraph Studio."""
    
    # Klucz API NVIDIA (ten sam co w kontenerze)
    api_key = os.environ.get(
        "NVIDIA_API_KEY",
        "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"
    )
    
    model = ChatOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
        model="meta/llama-3.3-70b-instruct",
        temperature=0.0,
        timeout=30,
        max_retries=1
    )
    
    roles = _load_roles()
    agents = []
    
    for role_name, role_config in roles.items():
        system_prompt = role_config.get("system_prompt", f"Jesteś {role_name}.")
        agent = create_react_agent(
            model=model,
            tools=[PythonREPLTool()],
            prompt=system_prompt,
            name=role_name
        )
        agents.append(agent)
    
    # Fallback jeśli brak ról
    if not agents:
        agents.append(
            create_react_agent(
                model=model,
                tools=[PythonREPLTool()],
                prompt="Jesteś uniwersalnym asystentem AI.",
                name="Assistant"
            )
        )
    
    supervisor = create_supervisor(
        agents=agents,
        model=model,
        prompt="Jesteś Supervisorem dynamicznego zespołu Hermes LangGraph."
    )
    
    return supervisor.compile()


# Zmienna wymagana przez LangGraph Studio
graph = _build_studio_graph()
