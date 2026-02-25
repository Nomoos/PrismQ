# Kontrola běhu modulu: PrismQ.T.Review.Title.From.Content.Idea

**Účel:** AI review titulku proti vygenerovanému obsahu a původní Idea pro validaci konzistence title-content-idea triády.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story` + `Idea`)
- **Data:** Story ve stavu `PrismQ.T.Review.Title.From.Content.Idea` s title, content a idea_id
- **Předpoklady:** Story s title (modul 03) a content (modul 04), běžící Ollama server

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories s title, content a Idea textem
3. [AI review](shared/ollama_ai_integrace.md) — hodnocení relevance titulku k obsahu, konzistence s Idea, identifikace nesrovnalostí
4. Vyhodnocení: rating (0-100), issues, suggestions, rozhodnutí (pass/fail)
5. [Uložení výsledků](shared/databazova_integrace.md) — update Story state podle výsledku
6. [Continuous loop](shared/continuous_mode.md)

---

## 📤 Výstup
- **Primární:** Review report s rating a feedback
- **DB změny:** Tabulka `Review` — nový záznam s textem a skóre; tabulka `Story` — state: Pass → `PrismQ.T.Review.Content.From.Title.Idea`, Fail → `PrismQ.T.Title.From.Title.Review.Content`
- **Další krok:** Pass → Modul 06, Fail → Modul 08 (regenerace titulku)
