# Wytyczne i Pomysły dla Groka (Rozbudowa)

Poniżej znajdują się kluczowe propozycje do przedstawienia Grokowi w ramach burzy mózgów i planowania kolejnych integracji naszego stosu.

## 1. Rozbudowa API LangGraph Server
**Do Groka:** *Stworzyliśmy wyizolowany serwer LangGraph z użyciem FastAPI. Jakie endpointy sugerujesz dodać, by najlepiej połączyć go z Hermesem? Obecnie mamy `/run_task` przyjmujące tekst i zwracające sukces/porażkę. Czy powinniśmy dodać `/status` by Hermes wiedział w jakim procencie LangGraph ukończył iterację zespołu?*

## 2. Dynamiczne Przypisywanie Zespołów
**Do Groka:** *Obecnie `HermesSupervisor` w LangGraph ma stałe role (Architect, Coder, Reviewer). Czy masz pomysł, jak dynamicznie w locie (tzw. Dynamic Agent Generation) generować specjalistyczne prompty z bazy profilów Hermesa i wrzucać je do potoku LangGraph w zależności od zlecenia (np. generowanie agenta "Audiobook Expert" specjalnie dla danego zapytania)?*

## 3. Komunikacja Webhook <-> Telegram
**Do Groka:** *Hermes działa jako bot Telegramowy. Kiedy LangGraph zaczyna pracę, zajmuje to np. 5 minut. Jak optymalnie ustawić strumieniowanie wiadomości (Websockets / SSE) z LangGraph do Hermesa, by Hermes co minutę informował użytkownika na Telegramie np. "Llama 3.3 właśnie testuje kod FFMPEG..."?*

## 4. Ochrona Pętli i Bezpieczeństwo Kosztów (Guardrails)
**Do Groka:** *Korzystamy z kluczy NVIDIA NIM (`meta/llama-3.3-70b-instruct`). Co się stanie, gdy graf wpadnie w nieskończoną pętlę generowania złego kodu i ewaluacji? Proszę o zaimplementowanie mechanizmu "Max Tokens Limit" lub ostrego przerwania w `evaluatorze` na wypadek, gdy Sędzia 3 razy odrzuci kod.*
