# Kontrola běhu modulu: PrismQ.T.Review.Content.From.Title

**Účel:** Finální AI review content proti titulku jako quality gate před detailními reviews (grammar, tone, content quality).

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Review.Content.From.Title` s title a content
- **Předpoklady:** Stories prošlé modulem 07 nebo 09, běžící Ollama server

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Review.Content.From.Title`
3. [AI comprehensive review](shared/ollama_ai_integrace.md) — content-title alignment, celková kvalita, readability, target audience fit, engagement potential
4. Vyhodnocení: pass / conditional pass / fail
5. [Uložení výsledků](shared/databazova_integrace.md) — update Story state
6. [Continuous loop](shared/continuous_mode.md)

---

## 📤 Výstup
- **Primární:** Story s final review assessment — quality gate pro detailed reviews
- **DB změny:** Tabulka `Story` — review metadata, state: Pass → `PrismQ.T.Review.Content.Grammar`, Fail → `PrismQ.T.Content.From.Title.Content.Review`
- **Další krok:** Pass → Modul 11, Fail → Modul 09 (regenerace content)
