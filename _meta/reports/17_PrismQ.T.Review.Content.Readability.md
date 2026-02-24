# Kontrola běhu modulu: PrismQ.T.Review.Content.Readability

**Účel:** Komplexní kontrola čitelnosti obsahu pomocí Flesch metrik, scannability a audience fit pro cílovou skupinu (13-23, ženy, USA).

---

## 📥 Vstup
- **Zdroj:** Databáze (tabulka `Story`)
- **Data:** Story ve stavu `PrismQ.T.Review.Content.Readability` s content fieldem
- **Předpoklady:** Stories prošlé title readability (modul 16), readability analysis tools

---

## ⚙️ Zpracování
1. [Inicializace](shared/inicializace_prostredi.md)
2. Načtení Stories ve stavu `PrismQ.T.Review.Content.Readability`
3. Readability analysis — Flesch Reading Ease (0-100), Flesch-Kincaid Grade Level, sentence/paragraph length, passive voice %, transition words
4. Target audience fit — vocabulary level pro věk 13-23, cultural relevance
5. Scannability assessment — key points visibility, visual flow, paragraph breaks
6. [Uložení výsledků](shared/databazova_integrace.md) — update Story: readability metrics, `state="PrismQ.T.Story.Review"`

---

## 📤 Výstup
- **Primární:** Story s comprehensive readability assessment
- **DB změny:** Tabulka `Story` — readability metrics (Flesch, grade level, passive voice %), `state="PrismQ.T.Story.Review"`
- **Další krok:** Modul 18 (PrismQ.T.Story.Review)
