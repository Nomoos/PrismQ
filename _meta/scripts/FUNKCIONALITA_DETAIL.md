# Detailní popis implementovaných modulů - PrismQ Scripts
*Detailed Step-by-Step Module Description*

**Datum:** 2025-12-10  
**Verze:** 1.0

---

## 📋 Formát dokumentace

Každý modul je popsán ve formátu:
- **XX.Y** - Krok Y modulu XX
- **Co se děje** - Technický popis kroku
- **Vstupy** - Co krok potřebuje
- **Výstupy** - Co krok vytvoří
- **Technologie** - Použité nástroje/knihovny

---

# 🎯 Modul 01: PrismQ.T.Idea.From.User

**Účel:** Vytváření nápadů (Idea objektů) z textového vstupu pomocí AI  
**Adresář:** `_meta/scripts/01_PrismQ.T.Idea.From.User/`  
**Python moduly:** `T/Idea/From/User/src/`

---

## 01.1 Start a inicializace prostředí

**Co se děje:**
- Batch skript (`Run.bat` nebo `Preview.bat`) se spustí
- Kontroluje se dostupnost Python
- Vytváří se nebo aktivuje virtual environment (`.venv`)
- Instalují se dependencies z `requirements.txt`
- Spouští se Ollama server (pomocí `common/start_ollama.bat`)

**Vstupy:**
- Žádné (spouští uživatel)

**Výstupy:**
- Aktivní Python virtual environment
- Běžící Ollama server
- Připravené prostředí pro Python skript

**Technologie:**
- Windows Batch scripting
- Python venv
- Ollama (AI model server)

---

## 01.2 Import a setup Python modulu

**Co se děje:**
- Python skript `idea_creation_interactive.py` se spustí
- Importují se moduly:
  - `idea_variants.py` - Generování variant nápadů
  - `ai_generator.py` - AI generátor přes Ollama
  - `flavor_loader.py` - Načítání "flavors" (stylů obsahu)
  - `flavors.py` - Definice stylů
  - Database moduly - Pro ukládání do SQLite
- Nastavují se cesty k modulům (sys.path)
- Kontroluje se dostupnost AI (Ollama)

**Vstupy:**
- Argumenty příkazové řádky (`--preview`, `--debug`)

**Výstupy:**
- Inicializované Python moduly
- Logger (pokud `--debug`)
- Režim běhu (preview vs. production)

**Technologie:**
- Python importy
- argparse (zpracování argumentů)
- logging (logování)

---

## 01.3 Interaktivní prompt a čekání na vstup

**Co se děje:**
- Zobrazí se uvítací header s ASCII art
- Vypíše se informace o režimu (Preview vs. Production)
- Program čeká na uživatelský vstup (multi-line text)
- Uživatel zadá text a potvrdí prázdným řádkem
- Nebo zadá "quit" pro ukončení

**Vstupy:**
- Uživatelský text (libovolný obsah)
- Speciální příkazy: "quit"

**Výstupy:**
- `input_text` - Zachycený vstup
- Log záznamy (v debug režimu)

**Technologie:**
- Python `input()` v loop
- ANSI color codes (barevný terminál)
- Exception handling (Ctrl+C)

---

## 01.4 Parsování vstupního textu

**Co se děje:**
- Funkce `parse_input_text()` analyzuje vstup
- Extrahuje:
  - **Title** - První řádek nebo automaticky generovaný
  - **Description** - Zbytek textu
  - **Metadata** - Případná strukturovaná data (JSON)
- Validuje a čistí text

**Vstupy:**
- `input_text` - Syrový textový vstup

**Výstupy:**
- `title` - Titulek nápadu (string)
- `description` - Popis nápadu (string)
- `metadata` - Dodatečná data (dict nebo None)

**Technologie:**
- Python string manipulace
- JSON parsing (pro metadata)
- Text cleaning a validation

---

## 01.5 Výběr flavors (stylů obsahu)

**Co se děje:**
- `FlavorSelector` vybere 10 flavors (stylů) pro generování variant
- Výběr je **weighted random** - některé flavory mají vyšší pravděpodobnost
- Flavory definují:
  - Typ obsahu (educational, entertaining, inspirational...)
  - Tón (formal, casual, technical...)
  - Zaměření (facts, stories, how-to...)
  - Cílové publikum

**Vstupy:**
- `DEFAULT_IDEA_COUNT` = 10 (počet variant k vytvoření)

**Výstupy:**
- `selected_flavors` - List 10 flavor názvů (strings)

**Technologie:**
- Python random selection s vahami
- Flavor definitions z `flavors.py`

**Příklad flavors:**
```
- Educational_Depth
- Entertaining_Story
- Inspirational_Vision
- Practical_HowTo
- Analytical_Research
... (celkem ~20 definovaných flavors)
```

---

## 01.6 Generování variant s AI

**Co se děje:**
- Pro každý vybraný flavor (10x):
  - **01.6.1** `IdeaGenerator.generate_from_flavor()` se zavolá
  - **01.6.2** Načte se flavor definice (prompt template)
  - **01.6.3** Vytvoří se AI prompt kombinující:
    - User input (title + description)
    - Flavor template (styl, tón, zaměření)
    - Variation index (pro unikátnost)
  - **01.6.4** Prompt se pošle na Ollama API
  - **01.6.5** AI (qwen3:32b model) generuje odpověď
  - **01.6.6** Odpověď se parsuje do struktury Idea objektu
  - **01.6.7** Validuje se kvalita výstupu
  - **01.6.8** Vytvoří se Idea objekt (dict) s fieldy:
    - `variant_name` - Název varianty
    - `title` - Vygenerovaný titulek
    - `description` - Rozšířený popis
    - `target_audience` - Cílová skupina
    - `content_type` - Typ obsahu
    - `tone` - Tón
    - `key_points` - Klíčové body (list)
    - `inspiration_source` - Původní vstup
    - `flavor` - Použitý flavor
    - `metadata` - Další data

**Vstupy (pro každou iteraci):**
- `title` - Původní titulek
- `description` - Původní popis
- `flavor_name` - Vybraný flavor
- `variation_index` - Index varianty (0-9)

**Výstupy (pro každou iteraci):**
- `idea` - Idea objekt (dict) s kompletními daty

**Technologie:**
- Ollama HTTP API (POST request)
- JSON strukturování promptů
- AI model: qwen3:32b (32B parametrů)
- Response parsing a validation

**Progress indikace:**
```
[1/10] Generating with flavor: Educational_Depth...
[2/10] Generating with flavor: Entertaining_Story...
...
[10/10] Generating with flavor: Practical_HowTo...
```

---

## 01.7 Zobrazení výsledků

**Co se děje:**
- Pro každou vygenerovanou variantu (10x):
  - Formátuje se do čitelného textu pomocí `format_idea_as_text()`
  - Zobrazí se na terminál s barevným formátováním
  - Loguje se do souboru (v debug režimu)

**Vstupy:**
- `variants` - List 10 Idea objektů

**Výstupy:**
- Konzolový výstup (barevný ASCII)
- Log soubor (pokud debug)

**Technologie:**
- ANSI color codes
- Python string formatting
- File logging

**Formát výstupu:**
```
──────────────────────────────────────────────────
  Variant 1: Educational_Depth_v1
──────────────────────────────────────────────────
  Title: [Vygenerovaný titulek]
  Description: [Rozšířený popis...]
  Target Audience: [Cílová skupina]
  Content Type: [Typ]
  Tone: [Tón]
  Key Points:
    - [Bod 1]
    - [Bod 2]
    ...
```

---

## 01.8 Ukládání do databáze

**Co se děje (pouze v Production režimu, NE v Preview):**
- **01.8.1** Získá se cesta k databázi:
  - Z `Config` objektu (src/config.py)
  - Nebo fallback: `C:/PrismQ/db.s3db`
- **01.8.2** Setup databáze pomocí `setup_idea_database()`
- **01.8.3** Pro každou variantu:
  - Převede se na text pomocí `format_idea_as_text()`
  - Vloží se do tabulky `Idea`:
    - `text` - Formátovaný text varianty
    - `version` - Vždy 1 (nové nápady)
    - `created_at` - Timestamp
  - Získá se `idea_id` (auto-increment)
  - Uloží se do `saved_ids` listu
- **01.8.4** Databáze se zavře
- **01.8.5** Zobrazí se potvrzení s ID

**Vstupy:**
- `variants` - List 10 Idea objektů
- `preview` - Boolean flag (False pro save)

**Výstupy:**
- 10 nových záznamů v tabulce `Idea`
- `saved_ids` - List ID [1, 2, 3, ..., 10]
- Konzolové potvrzení

**Technologie:**
- SQLite database
- Python sqlite3
- Database helper functions

**Database schema:**
```sql
Table: Idea
- id INTEGER PRIMARY KEY AUTOINCREMENT
- text TEXT NOT NULL
- version INTEGER DEFAULT 1
- created_at TIMESTAMP
```

**V Preview režimu:**
- Zobrazí se: "Preview Mode - No Database Save"
- Varianty se NEUKLÁDAJÍ
- Používá se pro testování

---

## 01.9 Loop a další iterace

**Co se děje:**
- Program se vrátí na krok 01.3 (čekání na další vstup)
- Uživatel může:
  - Zadat další text → Opakuje se proces 01.3-01.8
  - Zadat "quit" → Program končí
  - Stisknout Ctrl+C → Program končí s graceful shutdown

**Vstupy:**
- Uživatelský výběr (další text nebo quit)

**Výstupy:**
- Pokračování nebo ukončení programu

**Technologie:**
- Python while loop
- Keyboard interrupt handling

---

## 01.10 Ukončení

**Co se děje:**
- Zobrazí se goodbye message
- Zavřou se všechny otevřené resources
- Python proces končí s exit code 0

**Vstupy:**
- User quit command nebo Ctrl+C

**Výstupy:**
- Čistý shutdown
- Exit code 0 (success)

---

# 📚 Shrnutí Modulu 01

**Celkový flow:**
```
Start → Setup env → Import modules → Interactive prompt → 
Parse input → Select flavors → Generate 10 variants with AI → 
Display results → Save to DB (if not preview) → Loop back or Exit
```

**Klíčové technologie:**
- Windows Batch scripting
- Python 3.x
- Ollama AI (qwen3:32b)
- SQLite database
- ANSI terminal colors
- JSON data structures

**Důležité soubory:**
- `Run.bat` - Production mode launcher
- `Preview.bat` - Test mode launcher
- `idea_creation_interactive.py` - Main script
- `idea_variants.py` - Variant generation logic
- `ai_generator.py` - AI communication
- `flavors.py` - Flavor definitions
- `requirements.txt` - Python dependencies

---

---

# 📖 Modul 02: PrismQ.T.Story.From.Idea

**Účel:** Vytváření Story objektů z Idea objektů  
**Adresář:** `_meta/scripts/02_PrismQ.T.Story.From.Idea/`  
**Python moduly:** `T/Story/From/Idea/src/`

---

## 02.1 Start a inicializace prostředí

**Co se děje:**
- Batch skript (`Run.bat` nebo `Preview.bat`) se spustí
- Stejný proces jako 01.1:
  - Check Python
  - Create/activate venv
  - Install dependencies
  - Start Ollama server

**Vstupy:**
- Žádné

**Výstupy:**
- Připravené Python prostředí
- Běžící Ollama

**Technologie:**
- Windows Batch scripting
- Python venv

---

## 02.2 Import a setup Python modulu

**Co se děje:**
- Python skript `story_from_idea_interactive.py` se spustí
- Importují se moduly:
  - `story_from_idea_service.py` - Hlavní logika
  - `SimpleIdea` - Model pro Idea objekty
  - `SimpleIdeaDatabase` - Database pro Ideas
  - `Story` - Model pro Story objekty
  - `StoryRepository` - Database operations pro Stories
  - Config - Pro database path

**Vstupy:**
- Argumenty: `--preview` (optional)

**Výstupy:**
- Inicializované moduly
- Logger
- Režim (preview vs. production)

**Technologie:**
- Python imports
- Path configuration

---

## 02.3 Připojení k databázi

**Co se děje:**
- **02.3.1** Získá se cesta k databázi (PrismQ DB)
  - Z `Config.get_database_path()`
  - Obsahuje tabulky `Story` a `Idea`
- **02.3.2** Otevře se connection k databázi
- **02.3.3** Nastaví se `row_factory = sqlite3.Row` (pro dict-like rows)
- **02.3.4** Vytvoří se `SimpleIdeaDatabase` instance s touto connection
- **02.3.5** Vytvoří se `StoryFromIdeaService` instance

**Vstupy:**
- Database path z Config

**Výstupy:**
- `db_conn` - SQLite connection (PrismQ DB)
- `idea_db` - SimpleIdeaDatabase instance
- `service` - StoryFromIdeaService instance

**Technologie:**
- Python sqlite3
- Single database connection

**Database struktura:**
```
PrismQ DB (db.s3db):
- Story table (id, idea_id, state, created_at...)
- Idea table (id, text, version, created_at)
```

---

## 02.4 Continuous loop start

**Co se děje:**
- Spustí se **nekonečná smyčka** (while True)
- Program běží **kontinuálně** a zpracovává Ideas automaticky
- Čeká se na Ideas v databázi
- **NE interaktivní** - žádný user input (na rozdíl od modulu 01)

**Vstupy:**
- Žádné

**Výstupy:**
- Běžící continuous loop

**Technologie:**
- Python while True loop

---

## 02.5 Načtení unreferenced Ideas

**Co se děje:**
- **02.5.1** `service.get_unreferenced_idea_ids()` se zavolá
- **02.5.2** Dotaz na Story DB:
  ```sql
  SELECT DISTINCT idea_id FROM Story
  ```
- **02.5.3** Vytvoří se set referenced ID (Ideas, které už mají Stories)
- **02.5.4** Dotaz na Idea DB:
  ```sql
  SELECT id FROM Idea ORDER BY id ASC
  ```
- **02.5.5** Filtrování:
  - Všechny Idea IDs - Referenced IDs = **Unreferenced IDs**
- **02.5.6** Pokud jsou unreferenced Ideas:
  - Vybere se **nejstarší** (nejnižší ID)
  - To je `target_idea_id`
- **02.5.7** Pokud NEJSOU unreferenced Ideas:
  - Čeká se 30 sekund
  - Loop pokračuje (goto 02.5.1)

**Vstupy:**
- Story database (tabulka Story)
- Idea database (tabulka Idea)

**Výstupy:**
- `unreferenced_ids` - Set of Idea IDs bez Stories
- `target_idea_id` - Nejstarší unreferenced Idea ID (int)

**Technologie:**
- SQL queries
- Set operations (difference)

**Logika:**
```python
referenced_ids = {1, 2, 3}  # Ideas s Stories
all_idea_ids = {1, 2, 3, 4, 5}  # Všechny Ideas
unreferenced = {4, 5}  # Ideas BEZ Stories
target = 4  # Nejstarší (nejnižší ID)
```

---

## 02.6 Načtení vybrané Idea

**Co se děje:**
- **02.6.1** `idea_db.get_idea_by_id(target_idea_id)` se zavolá
- **02.6.2** SQL dotaz:
  ```sql
  SELECT * FROM Idea WHERE id = ?
  ```
- **02.6.3** Vytvoří se `SimpleIdea` objekt s daty:
  - `id` - Idea ID (int)
  - `text` - Formátovaný text nápadu
  - `version` - Verze (1)
  - `created_at` - Timestamp

**Vstupy:**
- `target_idea_id` - ID k načtení

**Výstupy:**
- `idea` - SimpleIdea objekt s kompletními daty

**Technologie:**
- SQL query
- Object mapping

---

## 02.7 Vytvoření 10 Story objektů

**Co se děje:**
- Pro i = 0 to 9 (celkem 10x):
  - **02.7.1** Vytvoří se nový `Story` objekt:
    ```python
    story = Story(
        id=None,  # Auto-assign při save
        idea_id=target_idea_id,
        state="PrismQ.T.Title.From.Idea",
        created_at=datetime.now()
    )
    ```
  - **02.7.2** Story obsahuje:
    - `idea_id` - Reference na Idea (integer)
    - `state` - `"PrismQ.T.Title.From.Idea"` (string konstanta)
    - `created_at` - Timestamp
    - `title_id` - NULL (zatím žádný titulek)
    - `content_id` - NULL (zatím žádný obsah)
  - **02.7.3** Story se přidá do `stories` listu

**Vstupy:**
- `target_idea_id` - ID zdrojové Idea
- `NUM_STORIES = 10` - Konstanta (počet Stories na Idea)

**Výstupy:**
- `stories` - List 10 Story objektů (ještě neuložených)

**Technologie:**
- Python object creation
- DateTime handling

**Důležité:**
- Stories jsou **prázdné** - obsahují POUZE referenci na Idea
- NEOBSAHUJÍ žádný text, titulek nebo obsah
- State = TITLE_FROM_IDEA znamená "ready for title generation"

---

## 02.8 Ukládání Stories do databáze

**Co se děje (pouze v Production režimu, NE v Preview):**
- Pro každou Story v `stories` listu:
  - **02.8.1** `story_repo.create(story)` se zavolá
  - **02.8.2** SQL INSERT:
    ```sql
    INSERT INTO Story (idea_id, state, created_at, title_id, content_id)
    VALUES (?, ?, ?, NULL, NULL)
    ```
  - **02.8.3** Získá se `story.id` (auto-increment)
  - **02.8.4** Story objekt se aktualizuje s ID
  - **02.8.5** Loguje se vytvoření

**Vstupy:**
- `stories` - List 10 Story objektů
- `preview` - Boolean flag

**Výstupy:**
- 10 nových záznamů v tabulce `Story`
- Stories mají přidělená ID
- Console log s potvrzením

**Technologie:**
- SQL INSERT statements
- Transaction handling
- Auto-increment IDs

**V Preview režimu:**
- Stories se NEUKLÁDAJÍ
- Pouze se zobrazují na konzoli
- Pro testování logiky

---

## 02.9 Výpočet delay před další iterací

**Co se děje:**
- **02.9.1** Spočítá se počet zbývajících unreferenced Ideas
- **02.9.2** Vypočítá se dynamic delay podle pravidel:
  ```python
  if unreferenced_count >= 100:
      delay = 0.001  # 1ms (rychlé zpracování)
  elif unreferenced_count >= 10:
      delay = 1.0    # 1 sekunda
  elif unreferenced_count >= 1:
      delay = 5.0    # 5 sekund
  else:
      delay = 30.0   # 30 sekund (čekání na nové Ideas)
  ```
- **02.9.3** Zobrazí se info: "Waiting X seconds..."
- **02.9.4** `time.sleep(delay)` se provede

**Vstupy:**
- `unreferenced_count` - Počet zbývajících Ideas

**Výstupy:**
- `delay` - Čas k čekání (float seconds)
- Pauza v běhu

**Technologie:**
- Python time.sleep()
- Dynamic calculation

**Účel delay:**
- Mnoho Ideas → Rychlé zpracování (1ms)
- Málo Ideas → Pomalejší (nechat čas na nové Ideas)
- Žádné Ideas → Dlouhá pauza (čekat na vytvoření)

---

## 02.10 Loop pokračuje

**Co se děje:**
- Po delay se loop vrátí na krok 02.5
- Proces se opakuje:
  - Načtou se unreferenced Ideas
  - Vybere se nejstarší
  - Vytvoří se 10 Stories
  - Uloží se (nebo ne, pokud preview)
  - Počká se dynamic delay
  - Loop pokračuje
- **Nekonečný cyklus** - běží, dokud není ukončen (Ctrl+C)

**Vstupy:**
- Žádné (automatické)

**Výstupy:**
- Kontinuální zpracování

**Technologie:**
- While True loop

---

## 02.11 Ukončení

**Co se děje:**
- User stiskne Ctrl+C
- Zachytí se KeyboardInterrupt
- Zobrazí se "Shutting down..."
- Zavřou se database connections:
  - `story_conn.close()`
  - `idea_db.close()`
- Program končí s exit code 0

**Vstupy:**
- Keyboard interrupt (Ctrl+C)

**Výstupy:**
- Čistý shutdown
- Zavřené connections
- Exit code 0

---

# 📚 Shrnutí Modulu 02

**Celkový flow:**
```
Start → Setup env → Import modules → Connect to DBs →
LOOP: Load unreferenced Ideas → Select oldest → Create 10 Stories →
Save to DB (if not preview) → Dynamic delay → LOOP
```

**Klíčové rozdíly od Modulu 01:**
- ❌ **NE interaktivní** - žádný user input
- ✅ **Continuous mode** - běží automaticky
- ✅ **Dynamic delays** - přizpůsobuje se množství dat
- ✅ **Dvě databáze** - Story DB + Idea DB
- ✅ **Prázdné Stories** - POUZE reference na Idea

**Důležité konstanty:**
- `NUM_STORIES = 10` - Počet Stories na Idea
- `StoryState.TITLE_FROM_IDEA` - State pro nové Stories

**Workflow pozice:**
```
Idea Creation (01) → Story From Idea (02) → Title From Idea (03)
                     ^^^^^^^^^^^^^^^^^^^^
                     Tento modul
```

---

---

# 🏷️ Modul 03: PrismQ.T.Title.From.Idea

**Účel:** Generování Title objektů pro Stories pomocí AI  
**Adresář:** `_meta/scripts/03_PrismQ.T.Title.From.Idea/`  
**Python moduly:** `T/Title/From/Idea/src/`

---

## 03.1 Start a inicializace prostředí

**Co se děje:**
- Batch skript (`Run.bat`, `Preview.bat` nebo `Manual.bat`) se spustí
- Stejný proces jako 01.1 a 02.1:
  - Check Python
  - Create/activate venv
  - Install dependencies
  - Start Ollama server (s modelem qwen3:32b)

**Vstupy:**
- Optional: `--db <path>` - Cesta k databázi

**Výstupy:**
- Připravené Python prostředí
- Běžící Ollama s qwen3:32b modelem

**Technologie:**
- Windows Batch scripting
- Python venv
- Ollama (qwen3:32b model - větší než 14b v modulu 01)

**Tři režimy:**
- `Run.bat` - Continuous mode (default)
- `Preview.bat` - Preview mode (no save)
- `Manual.bat` - Interactive mode (manual input)

---

## 03.2 Import a setup Python modulu

**Co se děje:**
- Python skript `title_from_idea_interactive.py` se spustí
- Importují se moduly:
  - `story_title_service.py` - Hlavní service layer
  - `ai_title_generator.py` - AI generování titulků
  - `title_generator.py` - Title generation logic
  - `title_scorer.py` - Hodnocení kvality titulků
  - `title_variant.py` - Datový model pro Title variant
  - `ollama_client.py` - Ollama API wrapper
  - Database models (Story, Title)
  - Repositories (StoryRepository, TitleRepository)

**Vstupy:**
- Argumenty: `--preview`, `--interactive`, `--db <path>`

**Výstupy:**
- Inicializované moduly
- Service instance
- Režim běhu

**Technologie:**
- Python imports
- Service layer pattern
- Repository pattern

---

## 03.3 Připojení k databázi

**Co se děje:**
- **03.3.1** Získá se database path:
  - Z CLI argumentu `--db` (pokud zadán)
  - Nebo z `Config.get_database_path()`
- **03.3.2** Otevře se connection k PrismQ DB
- **03.3.3** Nastaví se `row_factory = sqlite3.Row`
- **03.3.4** Ověří se existence tabulek:
  - `Story` table
  - `Title` table
- **03.3.5** Vytvoří se `StoryTitleService` instance

**Vstupy:**
- Database path (z CLI nebo Config)

**Výstupy:**
- `conn` - SQLite connection
- `service` - StoryTitleService instance

**Technologie:**
- Python sqlite3
- Single database (na rozdíl od modulu 02)

**Database tabulky:**
```
Story:
- id INTEGER PRIMARY KEY
- idea_id TEXT
- state TEXT
- title_id TEXT (NULL initially)
- content_id TEXT (NULL)
- created_at TIMESTAMP

Title:
- id TEXT PRIMARY KEY (UUID)
- story_id INTEGER (FK to Story)
- text TEXT
- version INTEGER
- score REAL (quality score)
- created_at TIMESTAMP
```

---

## 03.4 Continuous mode loop (výchozí režim)

**Co se děje:**
- Spustí se **nekonečná smyčka** (while True)
- Program běží **kontinuálně** jako modul 02
- Čeká se na Stories ready for title generation
- **Delay = 1ms** mezi iteracemi (velmi rychlé)

**Vstupy:**
- Žádné

**Výstupy:**
- Běžící continuous loop

**Technologie:**
- Python while True loop
- Fixed 1ms delay

---

## 03.5 Načtení Stories ready for titles

**Co se děje:**
- **03.5.1** `service.get_stories_ready_for_titles()` se zavolá
- **03.5.2** SQL dotaz:
  ```sql
  SELECT * FROM Story 
  WHERE state = 'PrismQ.T.Title.From.Idea' 
    AND title_id IS NULL
  ORDER BY created_at ASC
  LIMIT 1
  ```
- **03.5.3** Vybere se **nejstarší** Story bez titulku
- **03.5.4** Pokud žádná Story není ready:
  - Čeká se 1ms
  - Loop pokračuje (goto 03.5.1)
- **03.5.5** Pokud je Story ready:
  - Načte se kompletní Story objekt
  - To je `target_story`

**Vstupy:**
- Story database

**Výstupy:**
- `target_story` - Story objekt ready for title (nebo None)

**Technologie:**
- SQL query s JOIN
- State filtering

**Kritéria pro "ready for title":**
- State = `"PrismQ.T.Title.From.Idea"`
- `title_id IS NULL` (nemá ještě titulek)

---

## 03.6 Načtení zdrojové Idea

**Co se děje:**
- **03.6.1** Z `target_story` se získá `idea_id` (integer)
- **03.6.2** Idea se načte z Idea tabulky (stejná databáze)
  - SQL: `SELECT * FROM Idea WHERE id = ?`
- **03.6.3** Získá se `idea_text` - kompletní text Idea objektu
- **03.6.4** Text se použije přímo pro AI generování (žádný parsing)

**Vstupy:**
- `target_story.idea_id` - Reference na Idea (integer)

**Výstupy:**
- `idea_text` - Text zdrojové Idea (použit přímo pro AI prompt)

**Technologie:**
- SQL query
- Text retrieval (bez parsování)

---

## 03.7 Generování Title variant pomocí AI

**Co se děje:**
- **03.7.1** `AITitleGenerator` instance se vytvoří
- **03.7.2** Pro i = 0 to 9 (celkem 10 variant):
  - **03.7.2.1** Vytvoří se AI prompt:
    ```
    Generate a compelling title for this content:
    
    Idea: [idea_text]
    Target Audience: [audience]
    Content Type: [type]
    Tone: [tone]
    
    Generate variant #{i+1}
    ```
  - **03.7.2.2** Prompt se pošle na Ollama API
    - Model: qwen3:32b (větší model pro lepší titulky)
    - Temperature: 0.8 (kreativita)
    - Max tokens: 100
  - **03.7.2.3** AI vygeneruje title text
  - **03.7.2.4** Title se validuje:
    - Délka: 10-100 znaků
    - Formát: Single line
    - Jazyk: Match s Idea
  - **03.7.2.5** Vytvoří se `TitleVariant` objekt:
    ```python
    variant = TitleVariant(
        text=generated_text,
        variant_index=i,
        idea_id=idea_id,
        metadata={...}
    )
    ```
  - **03.7.2.6** Title se ohodnotí pomocí `TitleScorer`:
    - Readability score (0-100)
    - Engagement score (0-100)
    - SEO score (0-100)
    - Overall score (průměr)
  - **03.7.2.7** Variant s score se přidá do `variants` listu

**Vstupy:**
- `idea_text` - Text zdrojové Idea
- `idea_metadata` - Metadata z Idea
- `NUM_VARIANTS = 10` - Počet variant

**Výstupy:**
- `variants` - List 10 TitleVariant objektů s scores

**Technologie:**
- Ollama HTTP API
- qwen3:32b AI model (32B parametrů!)
- Title scoring algorithms
- Validation logic

**Progress indikace:**
```
[1/10] Generating title variant 1...
[2/10] Generating title variant 2...
...
[10/10] Generating title variant 10...
```

---

## 03.8 Výběr nejlepšího titulku

**Co se děje:**
- **03.8.1** Všechny varianty se seřadí podle `overall_score` (descending)
- **03.8.2** Vybere se varianta s nejvyšším score
- **03.8.3** To je `best_variant`

**Vstupy:**
- `variants` - List 10 TitleVariant objektů se scores

**Výstupy:**
- `best_variant` - TitleVariant s nejvyšším score

**Technologie:**
- Python sorting
- Score comparison

**Příklad scores:**
```
Variant 1: overall_score = 87.3
Variant 2: overall_score = 92.1  ← Best
Variant 3: overall_score = 85.7
...
```

---

## 03.9 Vytvoření Title objektu

**Co se děje:**
- **03.9.1** Vytvoří se nový `Title` objekt:
  ```python
  title = Title(
      id=generate_uuid(),  # Unique UUID
      story_id=target_story.id,
      text=best_variant.text,
      version=0,  # První verze (v0)
      score=best_variant.overall_score,
      created_at=datetime.now(),
      metadata={
          'variant_index': best_variant.variant_index,
          'readability_score': best_variant.readability_score,
          'engagement_score': best_variant.engagement_score,
          'seo_score': best_variant.seo_score,
          'all_variants': [v.text for v in variants]  # Pro porovnání
      }
  )
  ```

**Vstupy:**
- `best_variant` - Vybraný TitleVariant
- `target_story` - Story pro kterou je Title

**Výstupy:**
- `title` - Title objekt ready for save

**Technologie:**
- UUID generation
- Object creation
- Metadata embedding

**Důležité:**
- `version = 0` - První verze titulku (v0)
- Metadata obsahují **všechny varianty** pro pozdější analýzu

---

## 03.10 Ukládání Title do databáze

**Co se děje (pouze v Production režimu, NE v Preview):**
- **03.10.1** `title_repo.create(title)` se zavolá
- **03.10.2** SQL INSERT:
  ```sql
  INSERT INTO Title (id, story_id, text, version, score, created_at, metadata)
  VALUES (?, ?, ?, ?, ?, ?, ?)
  ```
- **03.10.3** Title se uloží s UUID jako PRIMARY KEY
- **03.10.4** Story se aktualizuje:
  ```sql
  UPDATE Story 
  SET title_id = ?, 
      state = 'PrismQ.T.Script.From.Title.Idea'  -- Next stage!
  WHERE id = ?
  ```
- **03.10.5** Loguje se vytvoření

**Vstupy:**
- `title` - Title objekt
- `target_story` - Story k aktualizaci
- `preview` - Boolean flag

**Výstupy:**
- 1 nový záznam v tabulce `Title`
- 1 aktualizovaný záznam v tabulce `Story`
  - `title_id` se nastaví
  - `state` se změní na next stage
- Console log

**Technologie:**
- SQL INSERT + UPDATE
- UUID as PRIMARY KEY
- State transition

**State transition:**
```
Before: Story.state = "PrismQ.T.Title.From.Idea"
After:  Story.state = "PrismQ.T.Script.From.Title.Idea"
                       ↑
                       Ready for Stage 04 (Script generation)
```

**V Preview režimu:**
- Title se NEULOŽÍ
- Story se NEAKTUALIZUJE
- Pouze zobrazení na konzoli

---

## 03.11 Zobrazení výsledků

**Co se děje:**
- Zobrazí se info o vytvořeném titulku:
  ```
  ✓ Created Title for Story ID: 123
  
  Selected Title (v0):
    Text: [Nejlepší vygenerovaný titulek]
    Score: 92.1/100
    
  Breakdown:
    Readability: 89/100
    Engagement: 95/100
    SEO: 92/100
  
  Alternative Variants (not used):
    1. [Varianta 1] - Score: 87.3
    2. [Varianta 3] - Score: 85.7
    ...
  ```

**Vstupy:**
- `title` - Vytvořený Title objekt
- `variants` - Všechny varianty

**Výstupy:**
- Console output
- Log soubor

**Technologie:**
- ANSI colors
- Formatted output

---

## 03.12 Loop delay a pokračování

**Co se děje:**
- **03.12.1** `time.sleep(0.001)` - 1ms delay
- **03.12.2** Loop se vrátí na krok 03.5
- **03.12.3** Proces se opakuje:
  - Načte se další Story ready for title
  - Vygenerují se Title varianty
  - Vybere se nejlepší
  - Vytvoří se Title
  - Uloží se (nebo ne, pokud preview)
  - 1ms pauza
  - Loop pokračuje

**Vstupy:**
- Žádné (automatické)

**Výstupy:**
- Kontinuální zpracování

**Technologie:**
- While True loop
- Fixed 1ms delay

**Rychlost zpracování:**
- 1ms delay = velmi rychlé
- Může zpracovat ~1000 Stories/sekunda (teoreticky)
- V praxi omezeno AI generation time (~5-10s per title)

---

## 03.13 Alternativní režimy

### Manual/Interactive Mode (Manual.bat)

**Co se děje:**
- Stejný flow jako Modul 01
- User zadává text ručně
- Generují se titulky pro zadaný text
- Zobrazí se všechny varianty
- User vidí scores
- Neukládá se do DB automaticky

### Preview Mode (Preview.bat)

**Co se děje:**
- Stejný flow jako Continuous mode
- ALE: Titles se NEUKLÁDAJÍ do DB
- Stories se NEAKTUALIZUJÍ
- Pouze testování a ladění

---

## 03.14 Ukončení

**Co se děje:**
- User stiskne Ctrl+C
- Zachytí se KeyboardInterrupt
- Zobrazí se "Shutting down..."
- Zavře se database connection
- Vypne se Ollama client
- Program končí s exit code 0

**Vstupy:**
- Keyboard interrupt (Ctrl+C)

**Výstupy:**
- Čistý shutdown
- Exit code 0

---

# 📚 Shrnutí Modulu 03

**Celkový flow:**
```
Start → Setup env → Import modules → Connect to DB →
LOOP: Load Story ready for title → Load source Idea →
Generate 10 Title variants with AI → Score all variants →
Select best variant → Create Title object → Save to DB →
Update Story state → 1ms delay → LOOP
```

**Klíčové vlastnosti:**
- ✅ **AI-powered** - Používá qwen3:32b model (největší)
- ✅ **Continuous mode** - Běží automaticky
- ✅ **Title scoring** - Hodnotí kvalitu titulků
- ✅ **Multiple variants** - Generuje 10 variant, vybírá nejlepší
- ✅ **State transition** - Posouvá Story do next stage
- ✅ **UUID keys** - Title má UUID primary key

**Důležité konstanty:**
- `NUM_VARIANTS = 10` - Počet variant na Story
- `version = 0` - První verze titulku
- Model: `qwen3:32b` - Větší než v modulech 01-02

**Workflow pozice:**
```
Idea Creation (01) → Story From Idea (02) → Title From Idea (03) → Script Generation (04)
                                             ^^^^^^^^^^^^^^^^^^^^
                                             Tento modul
```

**Output:**
- Title v0 pro každou Story
- Story state = "PrismQ.T.Script.From.Title.Idea" (ready for Stage 04)

---

# 🎓 Celkové shrnutí modulů 01-03

## Workflow chain:

```
01. Idea Creation
    ↓ Creates: Idea objects (10 variants)
    ↓ Storage: Idea table
    
02. Story From Idea
    ↓ Creates: Story objects (10 per Idea)
    ↓ Storage: Story table
    ↓ State: TITLE_FROM_IDEA
    
03. Title From Idea
    ↓ Creates: Title objects (1 per Story, v0)
    ↓ Storage: Title table
    ↓ Updates: Story.title_id + Story.state
    ↓ New State: SCRIPT_FROM_TITLE_IDEA
    
04. Script From Title Idea
    ↓ NOT IMPLEMENTED YET
    ↓ Would create: Script objects
    
... (stages 05-30)
```

## Společné vzory:

1. **Batch script setup** - Všechny moduly
2. **Virtual environment** - Všechny moduly
3. **Ollama AI** - Moduly 01, 03 (02 ne)
4. **SQLite database** - Všechny moduly
5. **Preview mode** - Všechny moduly
6. **Continuous loops** - Moduly 02, 03 (01 interaktivní)

## Klíčové rozdíly:

| Aspekt | Modul 01 | Modul 02 | Modul 03 |
|--------|----------|----------|----------|
| Input | Interaktivní user text | Auto (Ideas z DB) | Auto (Stories z DB) |
| AI Model | qwen3:32b | Žádné | qwen3:32b |
| Output Count | 10 Ideas | 10 Stories per Idea | 1 Title per Story (10 variants) |
| Loop Type | Interactive | Continuous | Continuous |
| Delay | Žádný (čeká na user) | Dynamic (1-30s) | Fixed (1ms) |
| Scoring | Ne | Ne | Ano (Title scoring) |

---

*Dokumentace pokračuje...*
*Další moduly (04-30) budou popsány po jejich implementaci.*
