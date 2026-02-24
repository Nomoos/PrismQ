# Kontrola běhu modulu: PrismQ.T.Review.Title.From.Content

**Účel:** Finální AI review titulku proti obsahu bez závislosti na Idea, zaměřený na title-content match, atraktivitu a SEO.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Review.Title.From.Content` s title a content
- **Předpoklady:** Stories prošlé content review (modul 06), běžící Ollama server

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Review.Title.From.Content`
3. [AI title-content review](shared/ollama_ai_integrace.md) — title-content match, atraktivita, SEO a clickability
4. Vyhodnocení: pass/fail
5. [Uložení výsledků](shared/databazova_integrace.md) — update Story state
6. [Continuous loop](shared/continuous_mode.md)

---

## 📤 Výstup
- **Primární:** Title review report
- **DB změny:** Tabulka `Story` — review metadata, state: Pass → `PrismQ.T.Review.Content.From.Title`, Fail → `PrismQ.T.Title.From.Title.Review.Content`
- **Další krok:** Pass → Modul 10, Fail → Modul 08 (regenerace titulku)
