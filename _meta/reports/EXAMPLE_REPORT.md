# Kontrola běhu modulu: PrismQ.Example.Module

## 🎯 Účel modulu
Ukázkový modul demonstrující správné použití template. Modul slouží jako referenční příklad pro dokumentaci nových modulů v PrismQ pipeline.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Databáze (tabulka Story ve stavu "PrismQ.Example.Previous")
- **Typ dat:** Story objekty s title a content fieldy
- **Povinné hodnoty:**
  - `story_id` - ID Story objektu k zpracování
  - `content` - Textový obsah Story
  - `title` - Titulek Story
- **Nepovinné hodnoty:**
  - `--preview` flag - režim bez uložení do databáze (pro testování)
  - `--debug` flag - detailní logování operací
  - `--batch-size` - počet Stories zpracovaných v jedné dávce (výchozí: 10)
- **Očekávané předpoklady:**
  - Story objekty vytvořené předchozím modulem
  - Běžící AI server (Ollama na localhost:11434)
  - Dostupný AI model (qwen3:32b)
  - Aktivní Python virtual environment
  - Přístup k databázi (read + write)
  - Dostatečná RAM (min 8GB pro AI model)

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Inicializace prostředí:**
   - Kontrola Python instalace a verze
   - Vytvoření/aktivace virtual environment
   - Instalace dependencies (requests, pytest)
   - Kontrola dostupnosti Ollama serveru
   - Kontrola dostupnosti AI modelu

2. **Načtení nezpracovaných Stories:**
   - Připojení k databázi
   - Dotaz na Stories ve stavu "PrismQ.Example.Previous"
   - Validace dat (kontrola existence title a content)
   - Filtrování pouze platných Stories

3. **Zpracování každé Story:**
   - Pro každou Story (iterace):
     - Načtení title a content z databáze
     - Příprava AI promptu s kontextem
     - Volání AI generátoru přes Ollama API
     - Parsing AI odpovědi
     - Validace výstupu (kontrola formátu, délky)
     - Retry při selhání (max 3 pokusy)

4. **Validace a quality checks:**
   - Kontrola kvality vygenerovaného výstupu
   - Scoring podle definovaných kritérií
   - Threshold check (min. skóre 70/100)
   - Flagování problematických případů

5. **Uložení výsledků (production režim):**
   - Update Story objektu v databázi
   - Změna stavu na "PrismQ.Example.Next"
   - Uložení metadat (skóre, timestamp, verze)
   - Commit transakce

6. **Reportování:**
   - Zobrazení výsledků na konzoli
   - Progress indikace (X/Y Stories zpracováno)
   - Statistiky úspěšnosti
   - Barevný formátovaný výstup

7. **Continuous mode:**
   - Čekání 1ms mezi iteracemi
   - Pokud nejsou Stories k zpracování: čekání 30 sekund a opakování
   - Možnost ukončení Ctrl+C

8. **Cleanup:**
   - Uzavření databázového spojení
   - Cleanup temporary files
   - Čisté ukončení

9. **Ošetření chybových stavů:**
   - Žádné Stories k zpracování - informační zpráva, čekání (continuous mode)
   - Ollama nedostupný - RuntimeError s instrukcemi
   - AI generování selhalo - retry 3x, pak skip Story
   - Databázové chyby - rollback, logování
   - Validace selhala - re-generování nebo skip
   - Ctrl+C handling - čisté ukončení s uzavřením DB

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:**
  - Zpracované Story objekty ve stavu "PrismQ.Example.Next"
  - Stories obsahují nový generated_field s AI výstupem
  - Stories obsahují metadata (skóre, timestamp)
  
- **Formát výstupu:**
  - Konzolový výstup: 
    - Statistiky zpracování (úspěšné/celkové)
    - Preview vygenerovaných dat
    - Barevné formátování (ANSI colors)
  - Databáze (production): 
    - Updated Stories v tabulce `Story`
    - Nový state: "PrismQ.Example.Next"
    - Metadata v JSON fieldu
  - Log soubor (debug): 
    - Detailní log všech operací
    - AI request/response pary
    - Error stack traces
  
- **Vedlejší efekty:**
  - Vytvoření virtual environment (.venv) pokud neexistuje
  - Instalace Python packages
  - Spuštění Ollama serveru (pokud nebyl spuštěn)
  - AI model cache warming
  - Log soubory v debug režimu
  - Temporary files v /tmp
  - Statistiky v databázi
  
- **Chování při chybě:**
  - Ollama error: RuntimeError, ukončení celého běhu
  - AI generování selhalo: Retry 3x, pak skip Story a pokračování
  - Databázová chyba: Rollback transakce, logování, ukončení
  - Validace selhala: Re-generování (max 3x), pak skip
  - Partial failure: Commitované Stories zůstávají, nezpracované zůstanou ve frontě
  - Network error: Retry s exponential backoff (max 5 pokusů)

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Modul XX (PrismQ.Example.Previous) - vytváří Stories připravené k zpracování
- Ollama server (AI model hosting) - **POVINNÉ**
- AI model (qwen3:32b) - pro generování obsahu
- SQLite databáze s tabulkou Story
- Python 3.12+ s virtual environment
- Hlavní moduly:
  - `Example/src/example_service.py` - Servisní logika
  - `Example/src/example_interactive.py` - Interaktivní rozhraní
  - `Example/src/ai_generator.py` - AI integrace
  - `Model/Database/repositories/story_repository.py` - Story repository
  - `src/config.py` - Konfigurace

**Výstupní závislosti:**
- Modul YY (PrismQ.Example.Next) - čte Stories ve stavu "PrismQ.Example.Next"
- Tabulka `Story` v databázi - obsahuje zpracované Stories
- Log files - pro monitoring a debugging

**Dokumentace (nepovinné):**
- README.md - Navigace a quick start
- _meta/docs/EXAMPLE_MODULE.md - Detailní dokumentace
- _meta/docs/AI_INTEGRATION.md - AI setup

---

## 📝 Poznámky / Rizika

**Klíčové změny v aktuální verzi:**
- **Verze 2.0**: Přechod na continuous mode jako výchozí
- **Verze 1.5**: Přidána validace s quality scoring
- **Verze 1.0**: Počáteční implementace

**Poznámky:**
- Modul podporuje continuous mode pro automatické zpracování nových Stories
- Preview režim je klíčový pro testování bez ovlivnění databáze
- AI model lze změnit v konfiguraci (AIConfig)
- Modul používá retry mechanismus pro handling dočasných chyb
- Quality scoring zajišťuje minimální kvalitu výstupu
- **VAROVÁNÍ**: Vždy použijte preview režim při testování nových prompt šablon
- Databázové spojení je reusable pro lepší výkon
- Modul loguje do souboru v debug režimu pro troubleshooting

**Rizika:**
- **AI nedostupnost**: Pokud Ollama není spuštěn, modul vyhodí RuntimeError (žádný fallback)
- **Kvalita AI výstupu**: AI může generovat nekvalitní data - částečně ošetřeno scoring
- **Performance**: Generování může být pomalé (~5-10s per Story pro 30B model)
- **Memory consumption**: Continuous mode může konzumovat hodně RAM při dlouhých bězích
- **API rate limiting**: Ollama může být zahlcen při batch processing velkého objemu
- **Databázová konkurence**: SQLite write locking může způsobit timeouts při parallel běhu
- **Determinismus**: AI výstup není deterministický - stejná Story může generovat různé výsledky
- **Dlouhé čekací doby**: Batch zpracování může trvat hodiny pro tisíce Stories

**Doporučení:**
- Monitorovat dostupnost Ollama serveru před spuštěním long-running jobs
- Používat preview režim pro testování nových funkcí a prompt šablon
- Pravidelně zálohovat databázi před velkými batch operacemi
- Implementovat monitoring a alerting pro continuous mode
- Zvážit použití menšího AI modelu pro faster processing (trade-off quality)
- Přidat progress bar nebo webhook notifikace pro dlouhé běhy
- Regular review AI výstupů pro quality assurance
- Implementovat circuit breaker pro repeated AI failures
- Use batch processing s limitováním paměti pro velmi velké datasety
- Consider caching frequently seen patterns (reduces AI calls)

---

*Příklad vytvořen: 2026-01-02 pro demonstraci template*
