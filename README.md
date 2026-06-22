# 🧠 Agentic-Stack

**Dual-Stack AI Architecture**: Hermes (Command Center) + LangGraph (Agent Factory)

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)](https://docker.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2.6-green)](https://langchain-ai.github.io/langgraph/)
[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-NIM-76B900)](https://build.nvidia.com)

---

## 📋 Opis Projektu

Agentic-Stack to wieloagentowy system AI oparty na architekturze Dual-Stack:

- **Hermes** — interfejs użytkownika (TUI/Telegram/Discord/Email), tablica Kanban, routing zadań
- **LangGraph Server** — bezgłowy kontener Docker z fabryką agentów AI (Supervisor → ARCHI + FORGE), ewaluatorami i pamięcią retrospektywną (Hindsight)

Użytkownik komunikuje się wyłącznie z Hermesem. Hermes automatycznie deleguje ciężkie zadania do kontenera LangGraph przez wewnętrzne Webhooki (REST API).

## 🏗️ Architektura

```
┌──────────────────────────────────────────────────┐
│                   UŻYTKOWNIK                     │
│          (Telegram / Discord / TUI)              │
└─────────────────────┬────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────┐
│              HERMES (Command Center)             │
│  • Kanban Board (SQLite)                         │
│  • Profile Router / Decomposer                   │
│  • Komunikacja wieloplatformowa                  │
│  • Port: 9119 (Kanban UI)                        │
└─────────────────────┬────────────────────────────┘
                      │ POST /run_task (Webhook)
                      ▼
┌──────────────────────────────────────────────────┐
│         LANGGRAPH SERVER (Docker Container)      │
│  • FastAPI + Uvicorn                             │
│  • Supervisor → Agenci (ARCHI, FORGE)            │
│  • Multi-Model Evaluator (NVIDIA NIM)            │
│  • Hindsight Memory                              │
│  • Obsidian Bridge (raporty .md)                 │
│  • Kanban Bridge (statusy → SQLite)              │
│  • Port: 8001 (Dashboard) / 2024 (Studio)        │
└──────────────────────────────────────────────────┘
```

## 🚀 Szybki Start

### Wymagania
- Docker + Docker Compose
- WSL 2 (Ubuntu) na Windows
- Node.js ≥ 18 (do LangGraph Studio)
- Klucz API NVIDIA NIM ([build.nvidia.com](https://build.nvidia.com))

### 1. Sklonuj repozytorium
```bash
git clone https://github.com/labdock3r-creator/Agentic-Stack.git
cd Agentic-Stack
```

### 2. Skonfiguruj zmienne środowiskowe
```bash
cp .env.example .env
# Edytuj .env i wpisz swoje klucze API
```

### 3. Uruchom kontener LangGraph
```bash
docker compose up -d --build
```

### 4. Sprawdź, czy działa
Otwórz w przeglądarce: **http://localhost:8001**
Powinien pojawić się LangGraph Factory Dashboard.

### 5. (Opcjonalnie) Uruchom LangGraph Studio
```bash
cd langgraph_server
npx @langchain/langgraph-cli dev --host 0.0.0.0 --port 2024
```
Studio UI: **https://smith.langchain.com/studio/?baseUrl=http://localhost:2024**

## 📁 Struktura Projektu

```
Agentic-Stack/
├── .env                          # Klucze API (NVIDIA, LangSmith)
├── .gitignore                    # Wykluczenia Git
├── docker-compose.yml            # Definicja kontenera LangGraph
├── migrate_db.py                 # Skrypt migracji bazy Kanban
├── test_webhook.py               # Test Webhooka (symulacja Hermesa)
│
├── docs/
│   ├── ARCHITECTURE.md           # Szczegółowa architektura Dual-Stack
│   ├── GROK_INTEGRATION.md       # Instrukcja integracji z Grok/xAI
│   └── RESOURCES.md              # Lista zasobów i linków
│
└── langgraph_server/
    ├── Dockerfile                # Obraz Python 3.11-slim
    ├── requirements.txt          # Zależności pip
    ├── langgraph.json            # Konfiguracja LangGraph Studio
    ├── studio_graph.py           # Punkt wejścia dla Studio (samodzielny)
    │
    └── app/
        ├── main.py               # FastAPI: Dashboard HTML + /run_task endpoint
        ├── supervisor.py         # HermesSupervisor: orkiestracja agentów
        ├── team_composer.py      # Dynamiczny dobór zespołu agentów
        ├── roles/                # Definicje ról agentów (JSON)
        │   ├── ARCHI.json        # Agent Architekt
        │   └── FORGE.json        # Agent Programista
        ├── providers/
        │   └── model_provider.py # Router modeli LLM (NVIDIA, Anthropic, xAI)
        ├── evaluation/
        │   └── multi_model_evaluator.py  # Ewaluator wielo-modelowy
        ├── integrations/
        │   ├── kanban_bridge.py  # Most do bazy Kanban Hermesa (SQLite)
        │   └── obsidian_bridge.py # Most do Obsidian Vault (.md)
        └── memory/
            └── hindsight_integration.py  # Pamięć retrospektywna (Hindsight)
```

## 🖥️ Dostępne Interfejsy

| Panel | Adres | Opis |
|---|---|---|
| **Kanban Board (Hermes)** | `http://localhost:9119/kanban` | Tablica zadań Todo / In Progress / Done |
| **LangGraph Dashboard** | `http://localhost:8001` | Mroczny panel z logami webhooków |
| **LangGraph Studio** | `https://smith.langchain.com/studio/?baseUrl=http://localhost:2024` | Wizualizacja grafów i kroków AI |
| **API Docs (Swagger)** | `http://localhost:2024/docs` | Dokumentacja REST API Studio |

## 🔧 Zmienne Środowiskowe (.env)

| Zmienna | Opis |
|---|---|
| `NVIDIA_API_KEY` | Klucz API do NVIDIA NIM (Llama 3.3, DeepSeek) |
| `LANGSMITH_API_KEY` | Klucz API LangSmith (do Studio) |
| `LANGCHAIN_TRACING_V2` | Włącz tracing LangChain (`true`) |
| `OBSIDIAN_VAULT_PATH` | Ścieżka montowania Obsidian Vault |
| `SQLITE_DB_PATH` | Ścieżka do bazy danych Kanban Hermesa |

## 📄 Licencja

MIT License — Możesz dowolnie używać, modyfikować i dystrybuować.
