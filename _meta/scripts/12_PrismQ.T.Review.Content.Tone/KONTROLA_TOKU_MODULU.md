# Kontrola běhu modulu: PrismQ.T.Review.Content.Tone

## 🎯 Účel modulu
Kontrola tónu a stylu obsahu. Modul validuje, že tón content je konzistentní, vhodný pro target audience, a alignovaný s brand voice/style guidelines.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Review.Content.Tone"
- **Povinné hodnoty:** Story s content fieldem, target audience info
- **Nepovinné hodnoty:** `--preview`, `--debug` flags, brand voice guidelines
- **Očekávané předpoklady:**
  - Stories prošlé modulem 11 (grammar check)
  - Běžící Ollama server
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories** - dotaz na stav "PrismQ.T.Review.Content.Tone"
2. **Tone analysis:**
   - Analýza overall tone (formal, casual, professional, friendly, atd.)
   - Kontrola tone consistency (není-li chaotické střídání tónů)
   - Validace proti target audience (je tón vhodný pro věk 13-23, ženy, USA?)
   - Sentiment analysis (pozitivní, negativní, neutrální)
   - Voice consistency (první/druhá/třetí osoba)
3. **Brand voice alignment check:**
   - Porovnání s brand voice guidelines (pokud existují)
   - Identifikace tone deviations
4. **Recommendations:**
   - Návrhy na tone adjustments
   - Specific sections s tone issues
5. **Update Story:**
   - Uložení tone review results
   - State změna na "PrismQ.T.Review.Content.Content" (modul 13)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story s tone analysis report
- **Formát výstupu:** Databáze (updated Stories), tone reports
- **Vedlejší efekty:** Tone quality metrics, consistency tracking
- **Chování při chybě:** Flag pro manual review

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 11 - grammar check
- Ollama server, databáze

**Výstupní závislosti:**
- Modul 13 (PrismQ.T.Review.Content.Content)

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Tone je subjektivní - vyžaduje clear guidelines
- Target audience má velký vliv na acceptable tone
- Brand voice guidelines mohou být specifické

**Rizika:**
- Subjektivita v tone assessment
- Cultural differences v tone perception
- Over-policing může ztratit authenticity

**Doporučení:**
- Clear tone guidelines pro každou audience segment
- Human sampling pro calibraci
- A/B testing různých tónů
