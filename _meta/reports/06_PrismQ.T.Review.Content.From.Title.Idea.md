# Kontrola běhu modulu: PrismQ.T.Review.Content.From.Title.Idea

**Účel:** AI review obsahu proti titulku a původní Idea pro validaci kvality, relevance a konzistence content.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Review.Content.From.Title.Idea` s title, content a idea_id
- **Předpoklady:** Stories prošlé title review (modul 05), běžící Ollama server

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Review.Content.From.Title.Idea`
3. [AI content review](shared/ollama_ai_integrace.md) — relevance k titulku, konzistence s Idea, kvalita a struktura
4. Vyhodnocení: pass/fail rozhodnutí
5. [Uložení výsledků](shared/databazova_integrace.md) — update Story state
6. [Continuous loop](shared/continuous_mode.md)

---

## 📤 Výstup
- **Primární:** Content review report s hodnocením
- **DB změny:** Tabulka `Story` — review metadata, state: Pass → `PrismQ.T.Review.Title.From.Content`, Fail → `PrismQ.T.Content.From.Title.Content.Review`
- **Další krok:** Pass → Modul 07, Fail → Modul 09 (regenerace content)
