"""
Hindsight Integration v6
"""

from typing import Optional
from datetime import datetime

import os
import json
from typing import Optional
from datetime import datetime

class HindsightMemory:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.storage_file = "/home/r00t/.hermes/hindsight_reflections.json"
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def reflect_and_store(self, task_id: str, reflection: str, phase: str = None):
        entry = {
            "task_id": task_id, 
            "reflection": reflection, 
            "phase": phase, 
            "time": datetime.now().isoformat()
        }
        
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            data.append(entry)
            with open(self.storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"[Hindsight] Zapisano reflection dla zadania {task_id}")
        except Exception as e:
            print(f"[Hindsight] Błąd zapisu: {e}")