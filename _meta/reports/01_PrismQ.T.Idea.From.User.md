# Kontrola běhu modulu: PrismQ.T.Idea.From.User

**Účel:** Generování strukturovaných Idea záznamů z uživatelského textového vstupu pomocí AI s flavor variantami (weighted random selection, 40% dual-flavor).

---

## 📥 Vstup
- **Zdroj:** Terminálový vstup (uživatel)
- **Data:** Text (`input_text`), předán do AI bez parsování/validace
- **Předpoklady:** Běžící Ollama server, aktivní DB spojení

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení vstupu od uživatele (raw text bez úprav)
3. Výběr flavor variant (FlavorSelector, výchozí 10, weighted random, 40% dual-flavor)
4. [AI generování variant](shared/ollama_ai_integrace.md) — pro každý flavor: `idea_improvement.txt` prompt → 5-sentence refined idea
5. [Uložení výsledků](shared/databazova_integrace.md) — `db.insert_idea(text, version=1)` okamžitě po každé variantě
6. [Continuous loop](shared/continuous_mode.md) — další vstup nebo ukončení příkazem "quit"

---

## 📤 Výstup
- **Primární:** 10 Idea záznamů v DB (čistý AI text, 5 vět)
- **DB změny:** Tabulka `Idea` — pole `text`, `version=1`, `created_at` (auto)
- **Další krok:** Modul 02 (PrismQ.T.Story.From.Idea)
