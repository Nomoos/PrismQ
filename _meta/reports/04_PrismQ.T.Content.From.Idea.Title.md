# Kontrola běhu modulu: PrismQ.T.Content.From.Idea.Title

**Účel:** AI generování strukturovaného skriptu (~300 slov, max 175s) pro Story na základě titulku, Idea a target audience (13-23, ženy, USA).

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story` + `Idea`)
- **Data:** Story ve stavu `PrismQ.T.Content.From.Idea.Title` s `title` a `idea_id`
- **Předpoklady:** Story s titulkem z modulu 03, běžící Ollama server, přístup k DB

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories + Idea text pro kontext
3. Příprava generování: target audience (věk 13-23, ženy, USA), seed word (z 504 slov)
4. [AI generování obsahu](shared/ollama_ai_integrace.md) — prompt: title + Idea + audience + seed word → strukturovaný skript (intro/body/conclusion)
5. Validace obsahu (délka ~300 slov / max 175s, struktura, kvalita)
6. [Uložení výsledků](shared/databazova_integrace.md) — insert Content, update Story: `content_id`, `state="PrismQ.T.Review.Title.From.Content.Idea"`
7. [Continuous loop](shared/continuous_mode.md)

---

## 📤 Výstup
- **Primární:** ContentV1 s introduction, body, conclusion (~300 slov)
- **DB změny:** Tabulka `Content` — nový záznam; tabulka `Story` — `content_id`, `state="PrismQ.T.Review.Title.From.Content.Idea"`
- **Další krok:** Modul 05 (PrismQ.T.Review.Title.From.Content.Idea)
