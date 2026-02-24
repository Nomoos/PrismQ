# Kontrola běhu modulu: PrismQ.T.Title.From.Title.Review.Content

**Účel:** AI regenerace titulku na základě review feedbacku s využitím kontextu z content (max 3 pokusy).

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Title.From.Title.Review.Content` s title, content a review feedback
- **Předpoklady:** Stories s failed title review (z modulu 05 nebo 07), běžící Ollama server

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení původního title, review feedback (issues, suggestions) a content
3. [AI regenerace titulku](shared/ollama_ai_integrace.md) — prompt: původní title + feedback + content → vylepšený titulek
4. Scoring nového titulku (stejná kritéria jako modul 03)
5. [Uložení výsledků](shared/databazova_integrace.md) — update Story: nový `title`, `state="PrismQ.T.Review.Content.From.Title"`, regeneration count
6. [Continuous loop](shared/continuous_mode.md)

---

## 📤 Výstup
- **Primární:** Story s regenerovaným titulkem
- **DB změny:** Tabulka `Story` — nový `title`, `state="PrismQ.T.Review.Content.From.Title"`, regeneration metadata
- **Další krok:** Modul 10 (PrismQ.T.Review.Content.From.Title)
