# Kontrola běhu modulu: PrismQ.T.Story.From.Idea

**Účel:** Vytváření Story záznamů z nezpracovaných Idea objektů jako vstupní bod pro content pipeline (10 Stories na Idea).

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Idea`)
- **Data:** Idea dicts (`id`, `text`, `version`, `created_at`) — Ideas bez reference v tabulce `Story`
- **Předpoklady:** Existující Idea záznamy (modul 01), přístup k DB (read + write)

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení nezpracovaných Ideas (bez Story referencí)
3. Pro každou Idea: vytvoření 10 Story objektů s `idea_id` referencí a `state="PrismQ.T.Title.From.Idea"`
4. [Uložení výsledků](shared/databazova_integrace.md) — insert do tabulky `Story`, commit transakce
5. [Continuous loop](shared/continuous_mode.md) — čekání 30s pokud žádné nové Ideas

---

## 📤 Výstup
- **Primární:** 10 Story záznamů na každou zpracovanou Idea
- **DB změny:** Tabulka `Story` — `idea_id`, `state="PrismQ.T.Title.From.Idea"`, `created_at`
- **Další krok:** Modul 03 (PrismQ.T.Title.From.Idea)
