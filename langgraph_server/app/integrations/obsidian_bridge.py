import os
from datetime import datetime

class ObsidianBridge:
    def __init__(self, vault_path: str = "/home/r00t/ObsidianVault"):
        self.vault_path = vault_path
        self.projects_dir = os.path.join(self.vault_path, "Hermes", "Projects")
        
        # Tworzenie struktury folderów jeśli nie istnieje
        if not os.path.exists(self.projects_dir):
            os.makedirs(self.projects_dir, exist_ok=True)

    def write_report(self, task_id: str, title: str, task_description: str, models_used: list, best_model: str, best_response: str, reasoning: str):
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{task_id}_{safe_title}.md".replace(" ", "_")
        filepath = os.path.join(self.projects_dir, filename)

        models_str = ", ".join(models_used)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        content = f"""---
title: "{title}"
task_id: "{task_id}"
date: "{date_str}"
status: "Completed"
models_used: [{models_str}]
best_model: "{best_model}"
tags: [hermes, langgraph, architecture, generated]
---

# Raport z Zadania: {title}
**ID:** {task_id}
**Data wygenerowania:** {date_str}

## Opis zadania:
{task_description}

## Ostateczna decyzja Sędziego:
**Zwycięski model:** `{best_model}`

**Uzasadnienie (Hindsight Reflection):**
> {reasoning}

## Ostateczny Kod / Architektura (Best Response):
```python
{best_response}
```
"""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[Obsidian] Zapisano notatkę w Vault: {filepath}")
        except Exception as e:
            print(f"[Obsidian] Błąd zapisu: {e}")
