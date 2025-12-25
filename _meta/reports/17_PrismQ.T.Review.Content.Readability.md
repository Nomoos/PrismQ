# Kontrola běhu modulu: PrismQ.T.Review.Content.Readability

## 🎯 Účel modulu
Kontrola čitelnosti a srozumitelnosti obsahu. Modul validuje, že content je snadno čitelný pro target audience, má vhodnou reading level, a dobrou strukturu pro rychlé skenování.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Review.Content.Readability"
- **Povinné hodnoty:** Story s content fieldem
- **Nepovinné hodnoty:** `--preview`, `--debug` flags, target reading level
- **Očekávané předpoklady:**
  - Stories prošlé modulem 16 (title readability)
  - Běžící readability analysis tools
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories** - dotaz na stav "PrismQ.T.Review.Content.Readability"
2. **Comprehensive readability analysis:**
   - **Flesch Reading Ease**: 0-100 score
   - **Flesch-Kincaid Grade Level**: US grade level
   - **Sentence length distribution**: Mix of short/medium/long
   - **Paragraph length**: Not too long, scannable
   - **Word complexity**: Syllables per word average
   - **Passive voice percentage**: Should be low
   - **Transition words**: Presence of connectors
   - **Heading usage**: Proper use of subheadings (pokud applicable)
3. **Target audience fit:**
   - Validace proti target age group (13-23)
   - Appropriate vocabulary level
   - Cultural relevance
4. **Scannability assessment:**
   - Can reader quickly grasp main points?
   - Are key points highlighted/emphasized?
   - Visual flow (paragraph breaks, lists)
5. **Recommendations:**
   - Specific improvements pro readability
   - Sentence/paragraph restructuring suggestions
6. **Update Story:**
   - Uložení comprehensive readability metrics
   - State změna na "PrismQ.T.Story.Review" (modul 18)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story s comprehensive readability assessment
- **Formát výstupu:** Databáze (updated Stories), detailed readability reports
- **Vedlejší efekty:** Readability metrics, improvement suggestions
- **Chování při chybě:** Flag pro editorial review

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 16 - title readability
- Readability analysis tools (Flesch, etc.), databáze

**Výstupní závislosti:**
- Modul 18 (PrismQ.T.Story.Review) - expert GPT review

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Multiple readability metrics poskytují comprehensive view
- Target audience (13-23, ženy, USA) vyžaduje specific reading level
- Readability != quality, ale významně ovlivňuje engagement
- Last technical review před expert human-like review

**Rizika:**
- Over-optimization pro readability může zjednodušit obsah příliš
- Readability metrics nejsou universal (kulturní rozdíly)
- Balance mezi readability a depth může být challenging

**Doporučení:**
- Set target readability ranges per content type
- Monitor actual reader engagement vs readability scores
- Allow higher complexity pro educational content
- A/B testing různých readability levels
- Human review sampling pro quality assurance
