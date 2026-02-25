# Kontrola běhu modulu: PrismQ.T.Content.From.Idea.Title

**Účel:** AI generování strukturovaného obsahu (skript ~300 slov, max 175 s) pro Story na základě titulku a Idea záznamu. Target audience je volitelná — konfiguruje se v `workflow.json`.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`, `Idea`, `Title`)
- **Data:** Story ve stavu `PrismQ.T.Content.From.Idea.Title` s `idea_id` a alespoň jedním záznamem v tabulce `Title`
- **Konfigurace:** `_meta/scripts/04_PrismQ.T.Content.From.Idea.Title/workflow.json` — volitelný target audience (viz níže)
- **Předpoklady:** Story s titulkem z modulu 03, běžící Ollama server, přístup k DB

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení `audience` z `workflow.json` (jednorázově před smyčkou); pokud je `null` nebo soubor chybí → skript běží bez audience kontextu v AI promptu
3. Výběr nejstarší Story ve stavu `PrismQ.T.Content.From.Idea.Title` (FIFO)
4. Načtení Idea textu z tabulky `Idea` (SQL dotaz přes `story.idea_id`)
5. Načtení posledního titulku z tabulky `Title` (`TitleRepository.find_latest_version`)
6. Příprava generování: seed word (náhodně z 504 slov), volitelně audience z konfigurace
7. [AI generování obsahu](shared/ollama_ai_integrace.md) — prompt: title + Idea + seed word (+ audience, pokud nastavena) → strukturovaný skript (hook / deliver / CTA)
8. Validace obsahu (délka ~300 slov / max 175 s, struktura, kvalita)
9. [Uložení výsledků](shared/databazova_integrace.md) — insert `Content` (verze 0), update `Story`: stav → `PrismQ.T.Review.Title.From.Content.Idea`
10. [Continuous loop](shared/continuous_mode.md)

> **Preview mode:** spuštění s `--preview` (nebo přes `Preview.bat`) vygeneruje obsah, ale **neprovede žádné DB zápisy** ani změnu stavu.

---

## ⚙️ Konfigurace audience (`workflow.json`)

Soubor `_meta/scripts/04_PrismQ.T.Content.From.Idea.Title/workflow.json` leží vedle `Run.bat`. Audience je zcela volitelná:

```json
// bez audience — skript běží bez audience kontextu
{ "audience": null }

// s audience — přidáno do AI promptu
{ "audience": { "age_range": "10-25", "gender": "Female", "country": "United States" } }
```

---

## 📤 Výstup
- **Primární:** ContentV1 s textem (~300 slov, hook / deliver / CTA)
- **DB změny:** Tabulka `Content` — nový záznam (verze 0); tabulka `Story` — stav → `PrismQ.T.Review.Title.From.Content.Idea`
- **Další krok:** Modul 05 (PrismQ.T.Review.Title.From.Content.Idea)
