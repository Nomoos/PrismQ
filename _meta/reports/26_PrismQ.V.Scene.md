# Kontrola běhu modulu: PrismQ.V.Scene

**Účel:** AI plánování video scén z obsahu — rozdělení na logické scény (5-10 pro 120s video) s visual concepts a timing.

---

## 📥 Vstup
- **Zdroj:** Databáze (published Stories s text content)
- **Data:** Published Story text, target video duration (120s)
- **Předpoklady:** Published content z modulu 20, AI pro scene analysis, přístup k DB

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Content analysis — parse struktura (intro/body/conclusion), extrakce klíčových konceptů a visual keywords
3. [AI scene breakdown](shared/ollama_ai_integrace.md) — rozdělení na 5-10 scén, duration per scéna, transitions
4. Visual concept generation — pro každou scénu: visual description, mood/tone, color palette, image suggestions
5. Scene script — narration text per scéna, on-screen text, transitions, timing
6. [Uložení výsledků](shared/databazova_integrace.md) — uložení scene plan (JSON), update Story: `state="PrismQ.V.Keyframe"`

---

## 📤 Výstup
- **Primární:** Scene plan s visual concepts a timing (structured JSON)
- **DB změny:** Tabulka `Story` — scene plan data, `state="PrismQ.V.Keyframe"`
- **Další krok:** Modul 27 (PrismQ.V.Keyframe)
