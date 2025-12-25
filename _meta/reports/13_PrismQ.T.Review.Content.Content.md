# Kontrola běhu modulu: PrismQ.T.Review.Content.Content

## 🎯 Účel modulu
Kontrola faktické správnosti a kvality obsahu. Modul validuje, že content obsahuje přesné informace, není zavádějící, a poskytuje hodnotu pro čtenáře.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Review.Content.Content"
- **Povinné hodnoty:** Story s content fieldem
- **Nepovinné hodnoty:** `--preview`, `--debug` flags, fact-checking resources
- **Očekávané předpoklady:**
  - Stories prošlé modulem 12 (tone check)
  - Běžící Ollama server
  - Přístup k fact-checking APIs (optional)
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories** - dotaz na stav "PrismQ.T.Review.Content.Content"
2. **Content quality analysis:**
   - Faktická správnost (fact-checking claims)
   - Logická konzistence (contradictions, logical fallacies)
   - Completeness (jsou všechny důležité body pokryty?)
   - Depth (je obsah dostatečně detailní?)
   - Accuracy (přesnost informací)
   - Relevance (je obsah relevantní k titulku?)
3. **Value assessment:**
   - Poskytuje content value čtenáři?
   - Je obsah informativní/educational/entertaining?
   - Splňuje content své promises (z titulku)?
4. **Issue identification:**
   - Faktické chyby
   - Zavádějící statements
   - Missing critical information
   - Irrelevant tangents
5. **Update Story:**
   - Uložení content quality report
   - State změna na "PrismQ.T.Review.Content.Consistency" (modul 14)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story s content quality assessment
- **Formát výstupu:** Databáze (updated Stories), quality reports
- **Vedlejší efekty:** Quality metrics, fact-check logs
- **Chování při chybě:** Flag pro manual fact-checking

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 12 - tone check
- Ollama server, fact-checking APIs (optional), databáze

**Výstupní závislosti:**
- Modul 14 (PrismQ.T.Review.Content.Consistency)

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Fact-checking může vyžadovat external resources
- AI může mít outdated information (training data cutoff)
- Content value je částečně subjektivní

**Rizika:**
- Missed factual errors (AI hallucinations)
- False positives (correct info flagged jako wrong)
- Inability to verify všechny claims

**Doporučení:**
- Human fact-checking pro critical claims
- Integration s fact-checking APIs
- Citation requirements pro factual claims
- Regular update AI knowledge base
