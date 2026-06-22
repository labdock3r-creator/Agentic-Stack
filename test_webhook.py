import requests

# Strzał do lokalnego Webhooka (Zasymulowanie zachowania Hermesa)
url = "http://localhost:8001/run_task"
payload = {
    "task_description": "Wygeneruj skrypt Pythona w folderze D:\\audiobooks-v2 który przeszuka wszystkie katalogi w poszukiwaniu plików audio i przekonwertuje je używając FFMPEG VBR.",
    "priority": "high"
}

print("Wysyłam zadanie do serwera LangGraph...")
response = requests.post(url, json=payload)

print(f"Status HTTP: {response.status_code}")
print(f"Odpowiedź z serwera: {response.json()}")
