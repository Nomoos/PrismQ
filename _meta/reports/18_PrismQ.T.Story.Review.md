# Kontrola běhu modulu: PrismQ.T.Story.Review

## 🎯 Účel modulu
Expert GPT review celé Story. Modul poskytuje high-level human-like review celého příběhu (title + content) z pohledu content experta, hodnotí overall quality, engagement potential a market fit.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Story.Review"
- **Povinné hodnoty:**
  - Story s title a content fieldy
  - Všechna předchozí review metadata
- **Nepovinné hodnoty:** `--preview`, `--debug` flags
- **Očekávané předpoklady:**
  - Stories prošlé všemi technical reviews (moduly 11-17)
  - Běžící Ollama server s expert model
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories** - dotaz na stav "PrismQ.T.Story.Review"
2. **Expert-level holistic review:**
   - **Overall quality assessment**: Je Story professional quality?
   - **Engagement evaluation**: Bude Story engaging pro audience?
   - **Market fit analysis**: Je Story vhodná pro target market?
   - **Competitive analysis**: Jak se Story srovnává s competitors?
   - **Value proposition**: Poskytuje Story unique value?
   - **Viral potential**: Má Story potential pro sharing?
   - **Brand alignment**: Fits brand image a values?
3. **Detailed feedback:**
   - Strengths (co funguje dobře)
   - Weaknesses (co by mohlo být lepší)
   - Opportunities (jak story maximize)
   - Threats (potenciální problémy)
4. **Rating a recommendations:**
   - Overall score (0-100)
   - Publikační doporučení (publish as-is, minor edits, major revision)
   - Specific improvement suggestions
   - Priority ranking improvements
5. **Decision routing:**
   - High score (90+) → "PrismQ.T.Story.Polish" (modul 19)
   - Medium score (70-89) → "PrismQ.T.Story.Polish" with notes
   - Low score (<70) → Flag pro major revision nebo discard
6. **Update Story:**
   - Uložení expert review report
   - State změna podle score

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story s expert review assessment a publishing recommendation
- **Formát výstupu:** Databáze (updated Stories), comprehensive review reports
- **Vedlejší efekty:** 
  - Quality gate metrics
  - Market fit analysis data
  - Publishing decision logs
- **Chování při chybě:** Human expert review fallback

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 17 - content readability (poslední technical review)
- Všechny předchozí review metadata (11-17)
- Expert-level AI model (např. GPT-4, Claude 3)
- Databáze

**Výstupní závislosti:**
- Modul 19 (PrismQ.T.Story.Polish) - pokud pass
- Manual review queue - pokud fail

---

## 📝 Poznámky / Rizika

**Poznámky:**
- První "human-like" review po technical checks
- Poskytuje high-level strategic feedback
- Critical quality gate před publishing pipeline
- Expert model může být expensive (GPT-4 API calls)
- Review je comprehensive - hodnotí Story jako celek
- Může identifikovat issues missed v technical reviews

**Rizika:**
- **Subjektivita**: Expert review je inherently subjektivní
- **Cost**: Expert AI models jsou expensive
- **Inconsistency**: Různé review runs mohou dát různé results
- **False negatives**: Good stories mohou být rejected
- **False positives**: Mediocre stories mohou projít
- **Market trends**: Review kritéria mohou být outdated

**Doporučení:**
- Human sampling pro calibraci expert AI
- Track correlation mezi expert scores a actual performance
- Regular update review criteria based on market feedback
- Implement appeal process pro rejected stories
- A/B testing published stories across score ranges
- Monitor engagement metrics vs expert predictions
- Consider ensemble review (multiple expert models)
- Human final approval pro borderline cases
