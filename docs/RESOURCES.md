# Szacowane Zasoby dla Agentic Stack

Architektura zakłada użycie lokalnych maszyn i chmurowego dostępu do potężnych modeli LLM, dzięki czemu kontenery pozostają niezwykle lekkie.

## 1. Hermes (Centrum Dowodzenia)
Główny agent odpowiedzialny za interfejs Kanban oraz integracje czatowe (Telegram, Discord, Email).

- **Środowisko:** Docker lub bezpośrednio WSL
- **RAM:** 200 MB - 500 MB
- **CPU:** Minimalne użycie (głównie nasłuch I/O, webhooki)
- **Rola LLM:** Routing intencji (np. model os-core-smart) - zużycie ułamków centów na zapytanie (lub darmowe via openrouter).

## 2. LangGraph Server (Wieloagentowa Fabryka)
Dedykowany kontener zajmujący się tylko i wyłącznie skomplikowanymi zadaniami generatywnymi i analitycznymi w tle.

- **Środowisko:** Kontener Docker z wystawionym portem 8000 (FastAPI/LangServe)
- **RAM:** 500 MB - 1 GB (w zależności od rozmiaru drzewa myślowego / pamięci kontekstu uruchomionych grafów)
- **CPU:** Niskie, sporadyczne piki przy parsowaniu logiki czy ewaluacji
- **Rola LLM:** "Ciężkie Myślenie". Korzystamy z chmury NVIDIA NIM API.
  - **Modele:** `meta/llama-3.3-70b-instruct` (główny architekt i sędzia), ew. DeepSeek (jako koder-asystent).
  - **Zależność sprzetowa:** Kontener łączy się z chmurą Nvidii, stąd lokalny komputer nie wymaga posiadania karty graficznej GPU VRAM, o ile zapewnione są klucze NVAPI.

## Dlaczego nie lokalne LLM?
Dzięki zewnętrznym potokom NVIDIA API, Twój stos uniknie zajmowania kilkudziesięciu Gigabajtów pamięci graficznej (co byłoby wymagane np. dla modeli 70B), zachowując tym samym lekkość i prędkość całego rozwiązania, a komputer PC nie odczuje spadków wydajności podczas długotrwałego renderowania kodu.
