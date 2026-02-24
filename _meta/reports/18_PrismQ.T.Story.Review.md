# Kontrola běhu modulu: PrismQ.T.Story.Review

**Účel:** Expert AI review celé Story (title + content) z pohledu content experta — hodnocení kvality, engagement potential a market fit.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Story.Review` s title, content a všemi review metadata (moduly 11-17)
- **Předpoklady:** Stories prošlé všemi technical reviews (moduly 11-17), běžící Ollama server s expert modelem

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Story.Review`
3. [Expert AI holistic review](shared/ollama_ai_integrace.md) — overall quality, engagement, market fit, viral potential, brand alignment
4. SWOT feedback — strengths, weaknesses, opportunities, threats
5. Rating (0-100) a routing: 70+ → polish, <70 → flag/discard
6. [Uložení výsledků](shared/databazova_integrace.md) — update Story: expert review report, state podle score

---

## 📤 Výstup
- **Primární:** Expert review report s rating (0-100) a publishing doporučením
- **DB změny:** Tabulka `Story` — expert review metadata, state: 70+ → `PrismQ.T.Story.Polish`, <70 → flag pro revision
- **Další krok:** Score 70+ → Modul 19 (PrismQ.T.Story.Polish)
