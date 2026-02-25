# Kontrola běhu modulu: PrismQ.T.Title.From.Idea

**Účel:** AI generování titulků pro Story objekty s dvoustupňovým hodnocením kvality (rule-based + AI scoring 0-100) a výběrem nejlepší varianty.

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story` + `Idea`)
- **Data:** Story objekty ve stavu `PrismQ.T.Title.From.Idea`, Idea text pro kontext
- **Předpoklady:** Story záznamy z modulu 02, běžící Ollama server, přístup k DB

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Title.From.Idea` + Idea text z tabulky `Idea`
3. [AI generování variant titulků](shared/ollama_ai_integrace.md) — 10 variant na Story, každá s náhodnou temperature 0.6–0.8 pro kreativní rozmanitost
4. Rule-based scoring každého titulku (TitleScorer: délka — ideál 40-60 znaků → 0.95, dobrá 35-65 → 0.90, krátké → 0.80, přijatelné 66-69 → 0.82, příliš dlouhé 70+ → 0.75)
5. AI scoring každého titulku pomocí `title_scoring.txt` šablony (temperature=0.1): čitelnost, klíčová slova, emocionální dopad, SEO, literární kvalita → výsledek 0-100 normalizovaný na 0.0–1.0
6. Kombinované skóre = 50 % rule-based + 50 % AI skóre; seřazení variant od nejvyššího
7. Výběr varianty s nejvyšším kombinovaným skóre s ohledem na podobnost k titulkům sourozeneckých Stories (Jaccard similarity, threshold 0.7)
8. [Uložení výsledků](shared/databazova_integrace.md) — nový záznam v tabulce `Title` (story_id, version=0, text), update Story: `state="PrismQ.T.Content.From.Idea.Title"`
9. [Continuous loop](shared/continuous_mode.md)

---

## 📤 Výstup
- **Primární:** Story objekty s vygenerovanými titulky a kombinovaným skóre (rule-based + AI)
- **DB změny:** Tabulka `Title` — `story_id`, `version=0`, `text`; Tabulka `Story` — `state="PrismQ.T.Content.From.Idea.Title"`
- **Další krok:** Modul 04 (PrismQ.T.Content.From.Idea.Title)
