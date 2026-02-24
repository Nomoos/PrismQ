# Kontrola běhu modulu: PrismQ.T.Review.Content.Tone

**Účel:** AI kontrola tónu a stylu obsahu pro validaci vhodnosti pro cílové publikum (13-23, ženy, USA) a brand voice.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Review.Content.Tone` s content fieldem a target audience info
- **Předpoklady:** Stories prošlé grammar check (modul 11), běžící Ollama server

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Review.Content.Tone`
3. [AI tone analysis](shared/ollama_ai_integrace.md) — overall tone, konzistence, validace pro audience (13-23, ženy, USA), sentiment, voice (POV)
4. Brand voice alignment check
5. [Uložení výsledků](shared/databazova_integrace.md) — update Story: tone report, `state="PrismQ.T.Review.Content.Content"`

---

## 📤 Výstup
- **Primární:** Story s tone analysis report
- **DB změny:** Tabulka `Story` — tone review metadata, `state="PrismQ.T.Review.Content.Content"`
- **Další krok:** Modul 13 (PrismQ.T.Review.Content.Content)
