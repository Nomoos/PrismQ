# Kontrola běhu modulu: PrismQ.T.Review.Content.Editing

## 🎯 Účel modulu
Finální editační průchod obsahu. Modul provádí poslední editorial review, optimalizuje formulace, zkracuje zbytečnosti, a zajišťuje, že content je ready for publication.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Review.Content.Editing"
- **Povinné hodnoty:** Story s content fieldem
- **Nepovinné hodnoty:** `--preview`, `--debug` flags
- **Očekávané předpoklady:**
  - Stories prošlé modulem 14 (consistency check)
  - Běžící Ollama server
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories** - dotaz na stav "PrismQ.T.Review.Content.Editing"
2. **Editorial improvements:**
   - **Clarity**: Nejasné formulace → clearer expressions
   - **Conciseness**: Verbose text → concise text
   - **Flow**: Awkward transitions → smooth transitions
   - **Word choice**: Weak words → stronger, more precise words
   - **Redundancy removal**: Repetitive content → streamlined
   - **Engagement**: Passive voice → active voice (kde vhodné)
3. **Optimization:**
   - Sentence length variety (mix short/long)
   - Paragraph breaks pro readability
   - Hook strength (první věta engaging?)
   - Conclusion strength (memorable ending?)
4. **Final polish:**
   - Remove filler words
   - Tighten weak sections
   - Enhance key points
5. **Update Story:**
   - Apply editorial improvements
   - Uložení editing report
   - State změna na "PrismQ.T.Review.Title.Readability" (modul 16)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story s polished, publication-ready content
- **Formát výstupu:** Databáze (updated Stories with edited content)
- **Vedlejší efekty:** Editing metrics, improvement logs
- **Chování při chybě:** Manual editorial review request

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 14 - consistency check
- Ollama server, databáze

**Výstupní závislosti:**
- Modul 16 (PrismQ.T.Review.Title.Readability)

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Editorial changes mohou být substantial
- Balance mezi improvement a original voice
- Last chance pro major content changes před publishing pipeline

**Rizika:**
- Over-editing může ztratit original voice
- Subjektivita v "better" word choices
- Time-consuming pokud many changes needed

**Doporučení:**
- Track before/after metrics (readability scores, engagement)
- Human editorial review sampling
- A/B testing edited vs original content
- Learning from high-performing edits
