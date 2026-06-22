from .supervisor import HermesSupervisor

def run_hunter():
    print("[Hunter Task] Inicjalizacja poszukiwania nowych API...")
    # Podłączamy się do naszej zaktualizowanej centrali
    sv = HermesSupervisor(provider="litellm")
    
    # Przekazujemy cel Agentowi HUNTER
    task_description = """
    Jesteś modułem zarządzania kosztami (HUNTER). Przeszukaj najnowsze źródła dla darmowych proxy i darmowych tierów zgodnych z OpenAI (szukaj np. 'OpenRouter free tier list', 'FreeLLMAPI GitHub', 'gpt4free').
    Zbuduj poprawny obiekt JSON z konfiguracją modelu dla LiteLLM. 
    Następnie użyj PythonREPL (PythonREPLTool), aby napisać i wywołać krótki skrypt w 'requests', który wyśle wygenerowany JSON na endpoint Management API naszego routera:
    POST http://host.docker.internal:4000/model/new
    
    Zadbaj o poprawne formatowanie nagłówków autoryzacyjnych (jeśli LiteLLM Master Key został nadany) oraz o zgłoszenie sukcesu do systemu LangGraph po poprawnym dodaniu.
    """
    
    # Odpalamy pełny cykl decyzyjny (Team Composer zdecyduje czy wysłać tylko HUNTERA, ale priority low nakieruje go odpowiednio)
    sv.run_task(task_description, priority="low")

if __name__ == "__main__":
    run_hunter()
