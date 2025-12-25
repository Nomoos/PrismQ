# Kontrola běhu modulu: PrismQ.T.Review.Title.Readability

## 🎯 Účel modulu
Kontrola čitelnosti a srozumitelnosti titulku. Modul validuje, že titulek je snadno čitelný, srozumitelný, a atraktivní pro target audience.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Review.Title.Readability"
- **Povinné hodnoty:** Story s title fieldem
- **Nepovinné hodnoty:** `--preview`, `--debug` flags
- **Očekávané předpoklady:**
  - Stories prošlé modulem 15 (content editing)
  - Běžící Ollama server nebo readability tools
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories** - dotaz na stav "PrismQ.T.Review.Title.Readability"
2. **Readability analysis:**
   - Length check (ideální 40-60 znaků)
   - Word complexity (jsou slova srozumitelná?)
   - Clarity (je okamžitě jasné, o čem content je?)
   - Intrigue (vyvolává zvědavost?)
   - Avoiding clickbait while staying engaging
3. **Metrics calculation:**
   - Readability score
   - Character count
   - Word count
   - Syllable count per word (pro složitost)
4. **Recommendations:**
   - Návrhy na zkrácení/zjednodušení (pokud potřeba)
5. **Update Story:**
   - Uložení readability metrics
   - State změna na "PrismQ.T.Review.Content.Readability" (modul 17)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story s title readability assessment
- **Formát výstupu:** Databáze (updated Stories), readability reports
- **Vedlejší efekty:** Title quality metrics
- **Chování při chybě:** Flag pro manual review

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 15 - content editing
- Readability tools/AI, databáze

**Výstupní závislosti:**
- Modul 17 (PrismQ.T.Review.Content.Readability)

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Title readability critical for engagement
- Balance between simplicity a intrigue
- Target audience má vliv na acceptable complexity

**Rizika:**
- Over-simplification může ztratit nuance
- Readability scores nejsou perfect metrics

**Doporučení:**
- A/B testing titles pro real engagement data
- Target audience specific readability thresholds
