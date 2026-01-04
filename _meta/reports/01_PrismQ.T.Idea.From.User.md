# Kontrola běhu modulu: PrismQ.T.Idea.From.User

## 🎯 Účel modulu
Vytváření nápadů (Idea objektů) z textového vstupu pomocí AI. Modul slouží jako vstupní bod celého workflow PrismQ - transformuje inspiraci uživatele na strukturované nápady s různými variantami, které lze dále zpracovávat v pipeline.

**Klíčové**: Vstupní text je předán přímo do AI promptu bez jakéhokoliv parsování, extrakce, validace nebo čištění.

---

## 📥 Vstupy (Inputs)
Modul přijímá následující vstupy:

- **Zdroj vstupu:** Uživatel (interaktivní terminálový vstup nebo API volání)
- **Typ dat:** Text (libovolný formát - plain text, JSON, víceřádkový text)
- **Povinné hodnoty:**
  - `input_text` - Textový vstup od uživatele (předán do AI bez úprav)
- **Nepovinné hodnoty:**
  - `count` - počet variant k vygenerování (výchozí: 10)
  - `flavor_name` - specifický flavor (jinak weighted random selection)
- **Očekávané předpoklady:**
  - Běžící Ollama server (localhost:11434)
  - Dostupný AI model (qwen3:32b nebo jiný)
  - Aktivní Python virtual environment
  - Přístup k databázi (POVINNÉ - modul vyžaduje databázové spojení)

---

## ⚙️ Zpracování (Processing)
Průběh zpracování dat v modulu:

1. **Inicializace prostředí:**
   - Kontrola Python instalace
   - Vytvoření/aktivace virtual environment
   - Instalace dependencies (pytest, requests)
   - Spuštění Ollama serveru

2. **Načtení vstupů:**
   - Zobrazení uvítací obrazovky
   - Čtení vstupu od uživatele
   - **Text je předán do AI šablony přesně tak, jak byl zadán** (žádné parsování, extrakce, validace ani čištění)

3. **Výběr flavor variant:**
   - FlavorSelector vybere flavory pomocí weighted random selection
   - Výchozí počet: 10 flavors (stylů obsahu)
   - Flavory definují: typ obsahu, tón, zaměření, cílové publikum
   - 20% šance na dual-flavor kombinaci pro bohatší tematiku

3. **Příprava databáze (POVINNÉ):**
   - Kontrola dostupnosti databázového modulu
   - Získání cesty k databázi (z Config)
   - **Setup databázového spojení JEDNOU při inicializaci** pomocí setup_idea_database()
   - **DŮLEŽITÉ**: PrismQ používá JEDNU sdílenou databázi (db.s3db) pro všechny moduly
   - Spojení je znovu použito napříč všemi vstupy pro lepší výkon
   - Připravené spojení předáno do generátoru
   - **Pokud databázové spojení selže, modul se ukončí s chybou**

4. **Generování variant pomocí AI:**
   - Pro každý vybraný flavor (výchozí: 10x iterace):
     - Načtení flavor definice z konfigurace
     - Sestavení AI promptu: `input_text` + flavor + variation index
     - Odeslání requestu na Ollama API
     - AI generuje odpověď pomocí `idea_improvement.txt` prompt template
     - Odpověď obsahuje 5-sentence paragraph jako kompletní refined idea
     - **Okamžité uložení do databáze**:
       - Přímé volání `db.insert_idea(text=generated_idea, version=1)` na znovu použité spojení
       - Získání idea_id (auto-increment)
     - Vrácení minimálního objektu pro zobrazení:
       - `text`: raw AI výstup
       - `variant_name`: jméno flavoru (nebo kombinace)
       - `idea_id`: ID z databáze

5. **Zobrazení výsledků:**
   - Zobrazení každé varianty s názvem flavoru
   - Přímé zobrazení raw AI textu (bez formátování)
   - Barevný výstup na terminál (ANSI colors)
   - Logování do souboru (v debug režimu)

6. **Shrnutí operace:**
   - Zobrazení počtu uložených variant a jejich ID
   - Zobrazení cesty k databázi

7. **Loop pro další iterace:**
   - Návrat na začátek pro další vstup (databázové spojení zůstává otevřené)
   - Možnost ukončení příkazem "quit"

8. **Ukončení a cleanup:**
   - Uzavření databázového spojení ve finally bloku
   - Čisté ukončení aplikace

9. **Ošetření chybových stavů:**
   - Import errors - graceful degradation, zobrazení chybové zprávy
   - Ollama nedostupný - RuntimeError s instrukcemi (AI je povinné)
   - **Databázové chyby při setup - zobrazení chyby a ukončení (databáze je povinná)**
   - Databázové chyby při save - logování, zobrazení chyby uživateli
   - Ctrl+C handling - čisté ukončení aplikace s uzavřením DB
   - AI generování selhalo - skip varianty, pokračování s dalšími

---

## 📤 Výstupy (Outputs)
Výsledkem běhu modulu je:

- **Primární výstup:**
  - 10 vygenerovaných Idea záznamů v databázi (výchozí počet)
  - Každý záznam obsahuje čistý AI výstup (5-sentence refined idea)
  - **Text je uložen okamžitě po vygenerování, bez intermediate storage**
  
- **Formát výstupu:**
  - Konzolový výstup: Raw AI text s názvem flavoru
  - Databáze: 10 nových záznamů v tabulce `Idea`
    - Pole `text`: Přímý výstup z AI (5 vět, bez formátování)
    - Pole `version`: Vždy 1 pro nové nápady
    - Pole `created_at`: Časová značka vytvoření (auto-generated)
  
- **Architektura uložení:**
  - **Reusable DB connection**: Databázové spojení nastaveno JEDNOU při inicializaci
  - **Direct save**: AI generuje → okamžité uložení do DB → vrácení minimálních dat pro display
  - **Single shared database**: PrismQ používá JEDNU databázi (db.s3db) pro všechny moduly
  - Žádné intermediate dictionary s metadaty
  - Databázové spojení znovu použito napříč všemi variantami a vstupy
  - Každá varianta je uložena ihned po vygenerování
  - Spojení uzavřeno při ukončení v finally bloku
  
- **Vedlejší efekty:**
  - Vytvoření virtual environment (.venv)
  - Instalace Python packages
  - Spuštění Ollama serveru (pokud nebyl spuštěn)
  - Vytvoření databázového souboru (pokud neexistuje)
  
- **Chování při chybě:**
  - Import error: Zobrazení chybové zprávy, ukončení
  - Ollama chyba: RuntimeError s návodem na instalaci/spuštění (AI je povinné)
  - **Databázová chyba při setup: Zobrazení chyby, ukončení (databáze je povinná)**
  - Databázová chyba při save: RuntimeError, varianta je přeskočena
  - AI generování selhalo: Skip problematické varianty, pokračování s ostatními

---

## 🔗 Vazby a závislosti

**Vstupní závislosti:**
- Ollama server (AI model hosting) - **POVINNÉ**
- AI model (qwen3:32b výchozí, konfigurovatelný)
- SQLite databáze (persistence v production režimu)
- Python 3.12+
- Hlavní moduly:
  - `T/Idea/From/User/src/idea_variants.py` - IdeaGenerator, FlavorSelector
  - `T/Idea/From/User/src/ai_generator.py` - AIIdeaGenerator
  - `T/Idea/From/User/src/flavor_loader.py` - FlavorLoader
  - `T/Idea/From/User/src/flavors.py` - Flavor utility functions
  - `T/Idea/From/User/src/idea_creation_interactive.py` - Interaktivní CLI
  - `T/Idea/Model/src/simple_idea_db.py` - Databázové operace
  - `src/config.py` - Konfigurace

**Výstupní závislosti:**
- Modul 02 (PrismQ.T.Story.From.Idea) - čte vytvořené Ideas z databáze
- Tabulka `Idea` v databázi - source of truth pro další moduly

**Dokumentace:**
- README.md - Navigace a quick start
- _meta/docs/AI_INTEGRATION_README.md - Detailní AI setup
- _meta/docs/HOW_IT_WORKS.md - Technická dokumentace (CZ)
- _meta/docs/FLAVOR_SYSTEM.md - Flavor systém
- _meta/docs/CUSTOM_PROMPTS.md - Prompt templating

---

## 📝 Poznámky / Rizika

**Klíčové změny v aktuální verzi:**
- **Vstupní text bez parsování**: Text jde přímo do AI promptu
- **Žádné legacy parametry**: Pouze `input_text` (ne title/description)
- **AI je povinné**: Žádný fallback mode - RuntimeError pokud Ollama není dostupný
- **Databáze je povinná**: Modul se ukončí s chybou pokud databáze není dostupná
- **Jeden režim**: Odstraněn preview mode - pouze continuous mode s databázovým ukládáním
- **Direct save architektura**: AI generuje → okamžitě uloží do DB → vrátí minimální data pro display
- **Reusable DB connection**: Spojení nastaveno JEDNOU při inicializaci, znovu použito pro všechny operace
- **Single shared database**: PrismQ používá JEDNU databázi (db.s3db) pro VŠECHNY moduly
- **Žádné intermediate storage**: Eliminovány dictionary objekty s metadaty
- **Databázové spojení v generátoru**: DB připojení předáno do `generate_from_flavor()`
- **Dual-flavor support**: 20% šance na kombinaci dvou flavors
- **SOLID architektura**: Externalised configuration, service-oriented design

**Poznámky:**
- Modul podporuje batch processing přes `T/Idea/Batch/src/`
- **VAROVÁNÍ**: Nikdy nevytvářejte vícenásobné databáze nebo oddělené DB soubory
- Direct save znamená okamžité uložení po AI generování (žádné čekání na batch)
- Flavors jsou weighted - některé se objevují častěji (optimalizace pro cílové publikum)
- AI model může být změněn v konfiguraci (AIConfig)
- README.md je nyní pouze navigace - detaily v _meta/docs/
- Databáze ukládá pouze čistý text z AI - žádné JSON objekty, struktury nebo formátování
- **Databázové spojení je POVINNÉ** - modul nelze spustit bez přístupu k databázi

**Rizika:**
- **AI nedostupnost**: Pokud Ollama server není spuštěn nebo model není nainstalován, modul vyhodí RuntimeError (žádný fallback)
- **Databáze nedostupná**: Pokud databázové spojení nelze vytvořit, modul se ukončí s chybou (žádný fallback)
- **Kvalita AI výstupu**: AI může generovat nekvalitní data - částečně ošetřeno minimální délkou (20 znaků)
- **Databázová korrupce**: Současný zápis více instancí může způsobit problémy (SQLite je single-writer)
- **Memory consumption**: Generování 10 variant může být náročné na paměť při velkých modelech
- **API rate limiting**: Ollama může být zahlcen při batch processing
- **Dlouhé čekací doby**: Generování 10 variant může trvat několik minut (30B parameter model)

**Doporučení:**
- Monitorovat dostupnost Ollama serveru před spuštěním
- Zajistit dostupnost databázového spojení před spuštěním
- Pravidelně zálohovat databázi
- Zvážit implementaci retry mechanismu pro AI volání
- Implementovat progress bar pro lepší UX
- Číst aktuální dokumentaci v _meta/docs/ pro detaily
