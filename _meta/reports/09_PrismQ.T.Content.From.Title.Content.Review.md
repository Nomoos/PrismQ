# Kontrola běhu modulu: PrismQ.T.Content.From.Title.Content.Review

**Účel:** AI regenerace obsahu na základě review feedbacku se zachováním fungujících částí (max 3 pokusy).

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Content.From.Title.Content.Review` s title, content a review feedback
- **Předpoklady:** Stories s failed content review (z modulu 06), běžící Ollama server

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Analýza review feedback — extrakce issues, identifikace oblastí pro vylepšení
3. [AI regenerace content](shared/ollama_ai_integrace.md) — prompt: původní content + feedback + title → vylepšený obsah
4. Validace nového content (~300 slov, max 175s, intro/body/conclusion)
5. [Uložení výsledků](shared/databazova_integrace.md) — update Story: nový content, `state="PrismQ.T.Review.Content.From.Title"`
6. [Continuous loop](shared/continuous_mode.md)

---

## 📤 Výstup
- **Primární:** Story s regenerovaným obsahem
- **DB změny:** Tabulka `Story` — nový content, `state="PrismQ.T.Review.Content.From.Title"`, regeneration metadata
- **Další krok:** Modul 10 (PrismQ.T.Review.Content.From.Title)
