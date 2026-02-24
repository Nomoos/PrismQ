# Kontrola běhu modulu: PrismQ.T.Story.Polish

**Účel:** Finální polish a SEO optimalizace Story před publikováním — aplikace expert review suggestions, metadata příprava.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Story.Polish` s title, content a expert review feedback (modul 18)
- **Předpoklady:** Stories prošlé expert review (modul 18), běžící Ollama server

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Story.Polish`
3. [AI final polish](shared/ollama_ai_integrace.md) — aplikace expert suggestions, wording improvements, emotional hooks, flow optimization
4. SEO optimization — keyword density, meta description, title SEO, OpenGraph tags, Schema.org markup
5. Format optimization — heading hierarchy (H1-H3), paragraph breaks, emphasis
6. Metadata příprava — publication date, categories/tags, author attribution
7. [Uložení výsledků](shared/databazova_integrace.md) — update Story: polished content, SEO metadata, `state="PrismQ.T.Publishing"`

---

## 📤 Výstup
- **Primární:** Fully polished, publication-ready Story s SEO metadata
- **DB změny:** Tabulka `Story` — polished content, SEO metadata, `state="PrismQ.T.Publishing"`
- **Další krok:** Modul 20 (PrismQ.T.Publishing)
