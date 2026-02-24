# Kontrola běhu modulu: PrismQ.T.Review.Content.Editing

**Účel:** Finální AI editační průchod obsahu — optimalizace formulací, odstraňění zbytečností, příprava pro publikaci.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Review.Content.Editing` s content fieldem
- **Předpoklady:** Stories prošlé consistency check (modul 14), běžící Ollama server

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Review.Content.Editing`
3. [AI editorial improvements](shared/ollama_ai_integrace.md) — clarity, conciseness, flow, word choice, redundancy removal, passive→active voice
4. Optimization — sentence length variety, paragraph breaks, hook strength, conclusion strength
5. Final polish — filler words removal, tighten weak sections
6. [Uložení výsledků](shared/databazova_integrace.md) — update Story: edited content, `state="PrismQ.T.Review.Title.Readability"`

---

## 📤 Výstup
- **Primární:** Story s polished, publication-ready content
- **DB změny:** Tabulka `Story` — updated content, editing metadata, `state="PrismQ.T.Review.Title.Readability"`
- **Další krok:** Modul 16 (PrismQ.T.Review.Title.Readability)
