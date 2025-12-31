# Kontrola běhu modulu: PrismQ.T.Review.Title.From.Content.Idea

## 🎯 Účel modulu
Review titulku proti vygenerovanému obsahu a původnímu nápadu. Modul validuje, zda titulek odpovídá obsahu skriptu a original Idea, poskytuje feedback a hodnocení konzistence mezi všemi třemi elementy.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story s title, content a idea_id)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Review.Title.From.Content.Idea"
- **Povinné hodnoty:**
  - Story s title fieldem (z modulu 03)
  - Story s content fieldem (z modulu 04)
  - Platná idea_id reference s Idea textem
- **Nepovinné hodnoty:**
  - `--preview` flag - režim bez uložení
  - `--debug` flag - detailní logování
- **Očekávané předpoklady:**
  - Story s vygenerovaným titulkem a obsahem
  - Běžící Ollama server
  - Dostupný AI model pro review
  - Přístup k databázi

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Inicializace a setup:**
   - Aktivace virtual environment
   - Instalace dependencies
   - Spuštění Ollama serveru

2. **Načtení Stories k review:**
   - Dotaz na Stories ve stavu "PrismQ.T.Review.Title.From.Content.Idea"
   - Načtení title, content a idea textu pro každou Story

3. **AI-powered review proces:**
   - Sestavení review promptu kombinující:
     - Original Idea text (kontext a záměr)
     - Vygenerovaný Content (co bylo napsáno)
     - Titulek (co má být reviewed)
   - Požadavky na AI:
     - Hodnocení relevance titulku k obsahu
     - Kontrola konzistence s původním nápadem
     - Identifikace nesrovnalostí
     - Návrhy na zlepšení

4. **Vyhodnocení review:**
   - Parsing AI odpovědi
   - Extrakce:
     - Rating score (0-100)
     - List problémů/issues
     - List doporučení/suggestions
     - Celkové hodnocení (pass/fail/conditional)

5. **Update Story se review výsledky:**
   - Uložení review metadata
   - Změna stavu podle výsledku:
     - Pass → "PrismQ.T.Review.Content.From.Title.Idea" (modul 06)
     - Fail → "PrismQ.T.Title.From.Title.Review.Content" (modul 08 - regenerace titulku)

6. **Reportování:**
   - Zobrazení review výsledků
   - Rating score a issues
   - Rozhodnutí (pass/fail)

7. **Loop pro další Stories:**
   - V continuous mode: čekání 1ms mezi iteracemi, pokud není žádná Story, čekání 30 sekund a opakování dotazu
   - Možnost ukončení

8. **Ošetření chyb:**
   - Žádné Stories k zpracování - informační zpráva, čekání 30 sekund a opakování (continuous mode)
   - AI nedostupný - error message, ukončení
   - Review parsing failed - retry, pak skip
   - DB errors - rollback, logování

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:**
  - Story objekty s review metadaty
  - Stories ve stavu podle review výsledku (pass/fail)
  - Review report s rating a feedback
  
- **Formát výstupu:**
  - Konzolový výstup: Review results, rating, issues
  - Databáze: Updated Story záznamy (review metadata, state)
  - Log soubor: Kompletní review details
  
- **Vedlejší efekty:**
  - Review metrics shromážděné pro analytics
  - Log soubory
  
- **Chování při chybě:**
  - AI error: Error message, ukončení
  - Review failed: Story přesunuta do regeneration state
  - DB error: Rollback, logování

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 04 (PrismQ.T.Content.From.Idea.Title) - vytváří Content
- Modul 03 (PrismQ.T.Title.From.Idea) - vytváří Title
- Modul 01 (PrismQ.T.Idea.From.User) - source Idea
- Ollama server, AI model, databáze

**Výstupní závislosti:**
- Modul 06 (PrismQ.T.Review.Content.From.Title.Idea) - pokud pass
- Modul 08 (PrismQ.T.Title.From.Title.Review.Content) - pokud fail (regenerace titulku)

---

## 📝 Poznámky / Rizika

**Poznámky:**
- První review krok v multi-stage review procesu
- Validuje konzistenci title-content-idea triády
- AI poskytuje strukturované hodnocení s konkrétními issues

**Rizika:**
- **Subjektivita**: AI review může být subjektivní
- **False positives**: Dobrý titulek může být označen jako špatný
- **False negatives**: Špatný titulek může projít
- **Performance**: Review je pomalý (AI volání)

**Doporučení:**
- Human review sampling pro quality assurance
- Implementovat appeal proces pro false positives
- A/B testing různých review prompt strategií
- Tracking review accuracy over time
