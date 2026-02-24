# Ollama AI integrace

Společný vzor pro moduly využívající AI:

- **Server:** Ollama na `localhost:11434`
- **Model:** Získán globálně přes `get_local_ai_model()` (např. Qwen3:30b)
- **Temperature:** Náhodná mezi definovanými limity (globální konfigurace)
- **Timeout:** 120 sekund
- **Bez AI:** Modul vyhodí `RuntimeError` (žádný fallback)
