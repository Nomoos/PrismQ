# Kontrola běhu modulu: PrismQ.T.Title.From.Idea

**Účel:** AI generování titulků pro Story objekty s hodnocením kvality (scoring 0-100) a výběrem nejlepší varianty.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story` + `Idea`)
- **Data:** Story objekty ve stavu `PrismQ.T.Title.From.Idea`, Idea text pro kontext
- **Předpoklady:** Story záznamy z modulu 02, běžící Ollama server, přístup k DB

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Title.From.Idea` + Idea text
3. [AI generování variant titulků](shared/ollama_ai_integrace.md) — 5-10 variant na Story
4. Scoring titulků (TitleScorer: délka 40-60 znaků, čitelnost, klíčová slova, emocionální dopad, SEO)
5. Výběr varianty s nejvyšším skóre
6. [Uložení výsledků](shared/databazova_integrace.md) — update Story: `title`, `state="PrismQ.T.Content.From.Idea.Title"`
7. [Continuous loop](shared/continuous_mode.md)

---

## 📤 Výstup
- **Primární:** Story objekty s vygenerovanými titulky a skóre
- **DB změny:** Tabulka `Story` — `title`, `state="PrismQ.T.Content.From.Idea.Title"`, metadata (score, variants count)
- **Další krok:** Modul 04 (PrismQ.T.Content.From.Idea.Title)
