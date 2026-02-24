# Kontrola běhu modulu: PrismQ.T.Review.Title.Readability

**Účel:** AI kontrola čitelnosti a srozumitelnosti titulku — délka, složitost slov, clarity a intrigue pro target audience.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Review.Title.Readability` s title fieldem
- **Předpoklady:** Stories prošlé content editing (modul 15), běžící Ollama server nebo readability tools

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Review.Title.Readability`
3. [AI readability analysis](shared/ollama_ai_integrace.md) — délka (ideál 40-60 znaků), word complexity, clarity, intrigue, clickbait detection
4. Metrics calculation — readability score, character count, word count, syllable count
5. [Uložení výsledků](shared/databazova_integrace.md) — update Story: readability metrics, `state="PrismQ.T.Review.Content.Readability"`

---

## 📤 Výstup
- **Primární:** Story s title readability assessment a metriky
- **DB změny:** Tabulka `Story` — title readability metrics, `state="PrismQ.T.Review.Content.Readability"`
- **Další krok:** Modul 17 (PrismQ.T.Review.Content.Readability)
