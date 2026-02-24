# Kontrola běhu modulu: PrismQ.T.Review.Content.Consistency

**Účel:** AI kontrola stylové a strukturální konzistence obsahu (naming, formátování, tense, POV, kapitalizace).

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Review.Content.Consistency` s content fieldem
- **Předpoklady:** Stories prošlé content quality check (modul 13), běžící Ollama server

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Review.Content.Consistency`
3. [AI consistency checks](shared/ollama_ai_integrace.md) — naming, formátování, tense, POV, kapitalizace, number format
4. Internal reference check — cross-references, contradictory information
5. Auto-fix minor issues, flag major ones
6. [Uložení výsledků](shared/databazova_integrace.md) — update Story: consistency report, `state="PrismQ.T.Review.Content.Editing"`

---

## 📤 Výstup
- **Primární:** Story s consistency assessment
- **DB změny:** Tabulka `Story` — consistency metadata, `state="PrismQ.T.Review.Content.Editing"`
- **Další krok:** Modul 15 (PrismQ.T.Review.Content.Editing)
