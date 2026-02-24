# Kontrola běhu modulu: PrismQ.T.Review.Content.Content

**Účel:** AI kontrola faktické správnosti, logické konzistence, úplnosti a hodnoty obsahu pro čtenáře.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Review.Content.Content` s content fieldem
- **Předpoklady:** Stories prošlé tone check (modul 12), běžící Ollama server

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Review.Content.Content`
3. [AI content quality analysis](shared/ollama_ai_integrace.md) — faktická správnost, logická konzistence, úplnost, hloubka, relevance k titulku
4. Value assessment — informativnost, splnění promises z titulku
5. Identifikace issues (faktické chyby, zavádějící statements, chybějící informace)
6. [Uložení výsledků](shared/databazova_integrace.md) — update Story: quality report, `state="PrismQ.T.Review.Content.Consistency"`

---

## 📤 Výstup
- **Primární:** Story s content quality assessment
- **DB změny:** Tabulka `Story` — content quality metadata, `state="PrismQ.T.Review.Content.Consistency"`
- **Další krok:** Modul 14 (PrismQ.T.Review.Content.Consistency)
