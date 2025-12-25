# Kontrola běhu modulu: PrismQ.T.Title.From.Idea

## 🎯 Účel modulu
Generování titulků pro Story objekty na základě původních Ideas. Modul používá AI k vytvoření kvalitních, atraktivních titulků s hodnocením a výběrem nejlepší varianty. Podporuje continuous mode pro automatické zpracování a manuální režim pro jednotlivé Stories.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story s referencí na Idea)
- **Typ dat:** Story objekty ve stavu "PrismQ.T.Title.From.Idea"
- **Povinné hodnoty:**
  - Story záznamy se stavem "PrismQ.T.Title.From.Idea"
  - Platná idea_id reference s existujícím Idea záznamem
  - Text obsah z Idea záznamu
- **Nepovinné hodnoty:**
  - `--preview` flag - režim bez uložení do databáze
  - `--debug` flag - detailní logování
  - `--manual` flag - manuální výběr Stories k zpracování
  - Continuous mode parametr (1ms delay mezi běhy)
- **Očekávané předpoklady:**
  - Story záznamy vytvořené modulem 02
  - Běžící Ollama server (localhost:11434)
  - Dostupný AI model pro generování titulků
  - Aktivní Python virtual environment
  - Přístup k databázi (read + write)

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Inicializace prostředí:**
   - Kontrola Python instalace
   - Vytvoření/aktivace virtual environment
   - Instalace dependencies (requests, pytest)
   - Spuštění Ollama serveru
   - Kontrola dostupnosti AI modelu

2. **Načtení Stories k zpracování:**
   - Připojení k databázi
   - Dotaz na Stories ve stavu "PrismQ.T.Title.From.Idea"
   - Načtení Idea textu pro každou Story (přes idea_id)
   - Filtrování pouze nezpracovaných Stories

3. **Continuous mode vs Manual mode:**
   - **Continuous mode**: Automatické zpracování všech Stories s 1ms delay
   - **Manual mode**: Interaktivní výběr konkrétních Stories

4. **Generování variant titulků (pro každou Story):**
   - Načtení Idea textu z databáze
   - Analýza obsahu Idea pro kontext
   - Volání AI generátoru (OllamaClient)
   - Generování více variant titulků (typicky 5-10)
   - Pro každou variantu:
     - Generování titulku přes AI prompt
     - Parsing odpovědi z AI modelu
     - Vytvoření TitleVariant objektu

5. **Hodnocení a scoring titulků:**
   - Pro každou variantu:
     - TitleScorer hodnotí kvalitu titulku
     - Kritéria hodnocení:
       - Délka (ideální 40-60 znaků)
       - Čitelnost (readability score)
       - Přítomnost klíčových slov
       - Emocionální dopad
       - SEO friendly faktory
     - Výpočet celkového skóre (0-100)
   - Seřazení variant podle skóre

6. **Výběr nejlepšího titulku:**
   - Výběr varianty s nejvyšším skóre
   - Validace vybraného titulku
   - Příprava pro uložení

7. **Update Story objektu:**
   - Nastavení title fieldu na vybraný titulek
   - Změna stavu na "PrismQ.T.Content.From.Idea.Title"
   - Uložení metadata (score, variants count, timestamp)

8. **Uložení do databáze (production režim):**
   - Update Story záznamu v databázi
   - Commit transakce
   - Zalogování úspěšného update

9. **Reportování a statistiky:**
   - Zobrazení vygenerovaného titulku
   - Zobrazení skóre a metrik
   - Progress indikace (X/Y Stories zpracováno)
   - Barevný formátovaný výstup

10. **Loop pro další Stories:**
    - V continuous mode: 1ms delay, pokračování na další Story
    - V manual mode: čekání na další výběr
    - Možnost ukončení

11. **Ošetření chybových stavů:**
    - Žádné Stories k zpracování - informační zpráva
    - Ollama nedostupný - chybová zpráva, ukončení
    - AI generování selhalo - retry mechanismus (3x), pak skip
    - Databázové chyby - rollback, logování
    - Invalid title format - re-generování
    - Ctrl+C handling - čisté ukončení

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:**
  - Story objekty s vygenerovanými titulky
  - Story objekty ve stavu "PrismQ.T.Content.From.Idea.Title"
  - Metadata o generování (skóre, počet variant, timestamp)
  
- **Formát výstupu:**
  - Konzolový výstup: 
    - Vygenerované titulky s skóre
    - Progress indikace
    - Statistiky zpracování
  - Databáze (production): 
    - Updated záznamy v tabulce `Story` (title field, state field)
  - Log soubor (debug): 
    - Detailní log AI volání
    - Všechny vygenerované varianty
    - Scoring metriky
  
- **Vedlejší efekty:**
  - Vytvoření virtual environment (.venv)
  - Instalace Python packages
  - Spuštění Ollama serveru
  - AI model cache (Ollama)
  - Log soubory v debug režimu
  - Progress tracking v DB
  
- **Chování při chybě:**
  - Ollama error: Chybová zpráva, ukončení celého běhu
  - AI generování selhalo: Retry 3x, pak skip Story, pokračování s další
  - Databázová chyba: Rollback, logování, ukončení nebo pokračování (podle severity)
  - Invalid title: Re-generování (max 3 pokusy), pak použití fallback titulku
  - Partial failure: Zpracované Stories se commitnou, nezpracované zůstanou ve frontě

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul 02 (PrismQ.T.Story.From.Idea) - vytváří Stories připravené k zpracování
- Modul 01 (PrismQ.T.Idea.Creation) - source Idea textu
- Ollama server (AI model hosting)
- AI model pro generování titulků (např. qwen3:30b)
- SQLite databáze s tabulkami Story a Idea
- Python 3.x + virtual environment
- Moduly:
  - `T/Title/From/Idea/src/title_from_idea_interactive.py` - Hlavní aplikace
  - `T/Title/From/Idea/src/story_title_service.py` - Servisní logika
  - `T/Title/From/Idea/src/ai_title_generator.py` - AI generování
  - `T/Title/From/Idea/src/title_generator.py` - Generátor titulků
  - `T/Title/From/Idea/src/title_scorer.py` - Hodnocení kvality
  - `T/Title/From/Idea/src/title_variant.py` - Datové modely
  - `T/Title/From/Idea/src/ollama_client.py` - Ollama integrace
  - `T/Title/From/Idea/src/prompt_loader.py` - Načítání promptů
  - `Model/Database/repositories/story_repository.py` - Story repository

**Výstupní závislosti:**
- Modul 04 (PrismQ.T.Content.From.Idea.Title) - čte Stories s titulky
- Tabulka `Story` v databázi - obsahuje Stories s vygenerovanými titulky

---

## 📝 Poznámky / Rizika

**Poznámky:**
- Modul podporuje tři režimy běhu: continuous, manual, preview
- Continuous mode běží s 1ms delay pro vysokou propustnost
- Title scoring je komplexní - kombinuje délku, čitelnost, SEO, emocionální dopad
- Modul cachuje AI prompts pro rychlejší běhy
- Manual.bat umožňuje interaktivní zpracování jednotlivých Stories
- Modul je nejvíce CPU-intensive v celém pipeline (AI generování)

**Rizika:**
- **AI nedostupnost**: Pokud Ollama není spuštěn, celý běh selže
- **Kvalita titulků**: AI může generovat nevhodné nebo nekvalitní titulky (částečně ošetřeno scoring)
- **Performance**: Generování titulků je pomalé (30B model, ~5-10s per title)
- **Memory consumption**: Continuous mode může konzumovat hodně paměti při dlouhých bězích
- **Rate limiting**: Ollama může být zahlcen v continuous mode
- **Databázové zámky**: SQLite write locking může způsobit timeouts v continuous mode
- **Determinismus**: AI výstup není deterministický, stejná Idea může generovat různé titulky
- **Title length variance**: Některé titulky mohou být příliš dlouhé nebo krátké (ošetřeno scoring)

**Doporučení:**
- Monitorovat Ollama server před spuštěním continuous mode
- Implementovat rate limiting pro AI volání
- Přidat circuit breaker pro AI selhání
- Implementovat title caching pro stejné Ideas
- Zvážit paralelní zpracování s worker pool
- Přidat webhook notifikace pro completion
- Implementovat quality threshold - odmítnout titulky pod min. skóre
- Pravidelně review AI-generované titulky pro quality assurance
