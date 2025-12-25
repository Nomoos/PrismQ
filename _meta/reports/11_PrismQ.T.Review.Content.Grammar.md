# Kontrola běhu modulu: PrismQ.T.Review.Content.Grammar

## 🎯 Účel modulu
Detailní gramatická kontrola obsahu. Modul provádí důkladnou analýzu gramatiky, pravopisu, interpunkce a syntaxe vygenerovaného content pomocí AI nebo specializovaných nástrojů.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Review.Content.Grammar"
- **Povinné hodnoty:** Story s content fieldem
- **Nepovinné hodnoty:** `--preview`, `--debug` flags
- **Očekávané předpoklady:**
  - Stories prošlé modulem 10
  - Běžící Ollama server nebo grammar checking služby
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Načtení Stories** - dotaz na stav "PrismQ.T.Review.Content.Grammar"
2. **Grammar check:**
   - Kontrola pravopisu (spelling errors)
   - Kontrola gramatiky (subject-verb agreement, tense usage, atd.)
   - Kontrola interpunkce (commas, periods, quotes)
   - Kontrola syntaxe (sentence structure)
   - Identifikace typos
3. **Generování correction suggestions:**
   - Pro každý nalezený problém:
     - Popis chyby
     - Umístění v textu
     - Návrh opravy
     - Severity (critical, warning, suggestion)
4. **Auto-correction (optional):**
   - Automatické opravy trivial errors
   - Flagování non-trivial errors pro manual review
5. **Update Story:**
   - Uložení grammar review results
   - State změna na "PrismQ.T.Review.Content.Tone" (modul 12)

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:** Story s grammar review report a případnými corrections
- **Formát výstupu:** Databáze (updated Stories), grammar reports
- **Vedlejší efekty:** Grammar quality metrics, correction logs
- **Chování při chybě:** Skip nebo manual review request

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 10 - předchozí review
- Grammar checking tool/AI, databáze

**Výstupní závislosti:**
- Modul 12 (PrismQ.T.Review.Content.Tone)

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Může použít AI (LLM) nebo specializované grammar tools (LanguageTool, Grammarly API)
- Auto-correction pouze pro jednoznačné chyby
- Complex grammar issues vyžadují human judgment

**Rizika:**
- False positives (správné použití označené jako chyba)
- Missed errors (zejména context-dependent grammar)
- Over-correction (ztráta autenticity stylu)

**Doporučení:**
- Kombinovat multiple grammar checkers pro lepší coverage
- Human review pro flagged complex issues
- Learning from corrections pro zlepšení AI prompts
