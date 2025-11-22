# Postup pro Manuální Testování YouTube Scraping
# Manual Testing Procedure for YouTube Scraping

**Poslední aktualizace / Last Updated**: 2025-11-03  
**Modul / Module**: PrismQ.T.Idea.Inspiration.Sources.Content.Shorts.YouTube  
**Účel / Purpose**: Komplexní návod pro manuální testování YouTube scraping funkcionality krok za krokem

> 💡 **Pro rychlou referenci / For quick reference**: Viz [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)

---

## 📋 Obsah / Table of Contents

1. [Příprava Testovacího Prostředí / Test Environment Setup](#1-příprava-testovacího-prostředí--test-environment-setup)
2. [Základní Test - Channel Scraping](#2-základní-test---channel-scraping)
3. [Test - Trending Scraping](#3-test---trending-scraping)
4. [Test - Keyword Search](#4-test---keyword-search)
5. [Ověření Dat v Databázi / Database Verification](#5-ověření-dat-v-databázi--database-verification)
6. [Test Zpracování na IdeaInspiration Formát](#6-test-zpracování-na-ideainspiration-formát)
7. [Pokročilé Testovací Scénáře / Advanced Test Scenarios](#7-pokročilé-testovací-scénáře--advanced-test-scenarios)
8. [Řešení Problémů / Troubleshooting](#8-řešení-problémů--troubleshooting)
9. [Čistění a Reset / Cleanup and Reset](#9-čistění-a-reset--cleanup-and-reset)

---

## 1. Příprava Testovacího Prostředí / Test Environment Setup

### Krok 1.1: Přejít do Adresáře Modulu
**Navigate to Module Directory**

```bash
cd /cesta/k/PrismQ.T.Idea.Inspiration/Sources/Content/Shorts/YouTube
# Windows příklad:
# cd C:\Projects\PrismQ.T.Idea.Inspiration\Sources\Content\Shorts\YouTube
```

### Krok 1.2: Vytvořit Virtuální Prostředí (Doporučeno)
**Create Virtual Environment (Recommended)**

```bash
# Linux/macOS/WSL
python3 -m venv venv
source venv/bin/activate

# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows CMD
python -m venv venv
venv\Scripts\activate.bat
```

### Krok 1.3: Instalace Závislostí
**Install Dependencies**

```bash
pip install -r requirements.txt
```

**Očekávaný výstup / Expected output:**
```
Successfully installed click-8.3.0 google-api-python-client-2.186.0 
python-dotenv-1.2.1 yt-dlp-2025.10.22 sqlite-utils-3.38 ...
```

### Krok 1.4: Vytvoření Testovací Konfigurace
**Create Test Configuration**

```bash
# Zkopírovat testovací konfigurační soubor
# Copy test configuration file
cp .env.test.example .env.test
```

**Kontrola obsahu / Verify contents:**
```bash
cat .env.test  # Linux/macOS/WSL
type .env.test  # Windows CMD
```

**Očekávaný obsah / Expected contents:**
```bash
WORKING_DIRECTORY=
DATABASE_URL=sqlite:///test_db.s3db
YOUTUBE_CHANNEL_URL=https://www.youtube.com/@SnappyStories_1
YOUTUBE_API_KEY=  # Není potřeba pro channel scraping / Not needed for channel scraping
```

### Krok 1.5: Ověření Instalace
**Verify Installation**

```bash
python -m src.cli --version
python -m src.cli --help
```

**Očekávaný výstup / Expected output:**
```
PrismQ YouTube Shorts Source - Gather idea inspirations from YouTube Shorts.

Commands:
  clear            Clear all ideas from the database.
  list             List collected ideas.
  process          Process unprocessed YouTube Shorts records...
  scrape-channel   Scrape ideas from a specific YouTube channel's Shorts...
  scrape-keyword   Scrape ideas from YouTube by keyword search...
  scrape-trending  Scrape ideas from YouTube trending Shorts...
  stats            Show statistics about collected ideas.
```

✅ **Checkpoint:** Pokud vidíte seznam příkazů, instalace je úspěšná!  
✅ **Checkpoint:** If you see the command list, installation is successful!

---

## 2. Základní Test - Channel Scraping

### Krok 2.1: Spuštění Prvního Scrape
**Run First Scrape**

```bash
python -m src.cli scrape-channel --env-file .env.test --top 5
```

**Parametry / Parameters:**
- `--env-file .env.test` - použít testovací konfiguraci / use test configuration
- `--top 5` - stáhnout pouze 5 shorts (rychlé testování) / download only 5 shorts (quick test)

### Krok 2.2: Sledování Průběhu
**Monitor Progress**

**Očekávaný výstup / Expected output:**
```
Scraping YouTube channel: https://www.youtube.com/@SnappyStories_1
Maximum shorts to scrape: 5

[INFO] Fetching channel videos...
[INFO] Found 100+ videos in channel
[INFO] Filtering for Shorts (duration ≤180s, vertical format)...
[INFO] Found 50 qualifying Shorts

Processing Shorts:
  [1/5] Extracting metadata for: FpSdooOrmsU
    ✓ Title: "Amazing Story Title"
    ✓ Duration: 58s
    ✓ Views: 125,430
    ✓ Likes: 8,234
    ✓ Format: vertical (1080x1920)
    ✓ Subtitles: extracted
    
  [2/5] Extracting metadata for: ...
  ...
  [5/5] Extracting metadata for: ...

Scraping complete!
Total shorts found: 50
Total shorts processed: 5
Total shorts saved: 5
Database: ./test_db.s3db
```

### Krok 2.3: Kontrola Co se Stahuje
**Verify What's Being Downloaded**

**Klíčové informace k ověření / Key information to verify:**
- ✅ **Video ID** - jedinečný identifikátor YouTube / unique YouTube identifier
- ✅ **Title** - název videa / video title
- ✅ **Duration** - musí být ≤180s (omezení pro Shorts) / must be ≤180s (Shorts limit)
- ✅ **View Count** - počet zhlédnutí / view count
- ✅ **Like Count** - počet "to se mi líbí" / like count
- ✅ **Comment Count** - počet komentářů / comment count
- ✅ **Format** - vertikální (výška > šířka) / vertical (height > width)
- ✅ **Upload Date** - datum nahrání / upload date
- ✅ **Subtitles** - titulky (pokud jsou k dispozici) / subtitles (if available)

### Krok 2.4: Rychlý Přehled Výsledků
**Quick Results Overview**

```bash
python -m src.cli stats --env-file .env.test
```

**Očekávaný výstup / Expected output:**
```
Database Statistics
===================
Database: ./test_db.s3db
Total ideas: 5
Sources:
  - YouTube_Channel: 5 ideas

Recent ideas (last 5):
1. "Amazing Story Title" (FpSdooOrmsU) - Score: 85.3
2. "Another Great Story" (...) - Score: 72.1
...
```

✅ **Checkpoint:** Máte 5 shorts v databázi? Test úspěšný!  
✅ **Checkpoint:** Do you have 5 shorts in database? Test successful!

---

## 3. Test - Trending Scraping

### Krok 3.1: Scrape Trending Shorts
**Scrape Trending Shorts**

```bash
python -m src.cli scrape-trending --env-file .env.test --top 10
```

**Co tento příkaz dělá / What this command does:**
- Stahuje trendy YouTube Shorts z trending stránky / Downloads trending YouTube Shorts from trending page
- Nevyžaduje API klíč / Does not require API key
- Najde virální obsah / Discovers viral content

### Krok 3.2: Ověření Trending Dat
**Verify Trending Data**

```bash
python -m src.cli list --env-file .env.test
```

**Očekávaný výstup / Expected output:**
```
Ideas from database:
====================

1. [YouTube_Trending] "Viral Short Title"
   ID: abc123xyz
   Views: 2,500,000
   Likes: 150,000
   Score: 92.5
   Date: 2025-11-01

2. [YouTube_Channel] "Amazing Story Title"
   ID: FpSdooOrmsU
   Views: 125,430
   Likes: 8,234
   Score: 85.3
   Date: 2025-10-28

...
Total: 15 ideas
```

✅ **Checkpoint:** Vidíte mix YouTube_Channel a YouTube_Trending zdrojů?  
✅ **Checkpoint:** Do you see a mix of YouTube_Channel and YouTube_Trending sources?

---

## 4. Test - Keyword Search

### Krok 4.1: Vyhledávání Podle Klíčových Slov
**Search by Keywords**

```bash
python -m src.cli scrape-keyword --env-file .env.test --keyword "startup ideas" --top 8
```

**Parametry / Parameters:**
- `--keyword "startup ideas"` - hledané klíčové slovo / search keyword
- `--top 8` - maximální počet výsledků / maximum results

### Krok 4.2: Test s Různými Klíčovými Slovy
**Test with Different Keywords**

```bash
# České klíčové slovo / Czech keyword
python -m src.cli scrape-keyword --env-file .env.test --keyword "podnikatelské nápady" --top 5

# Obecné téma / General topic
python -m src.cli scrape-keyword --env-file .env.test --keyword "life hacks" --top 5

# Specifické téma / Specific topic
python -m src.cli scrape-keyword --env-file .env.test --keyword "AI tips" --top 5
```

### Krok 4.3: Kontrola Výsledků Vyhledávání
**Verify Search Results**

```bash
python -m src.cli stats --env-file .env.test
```

**Očekávaný výstup / Expected output:**
```
Database Statistics
===================
Total ideas: 33
Sources:
  - YouTube_Channel: 5 ideas
  - YouTube_Trending: 10 ideas
  - YouTube_Keyword: 18 ideas
```

✅ **Checkpoint:** Vidíte všechny tři typy zdrojů? Test úspěšný!  
✅ **Checkpoint:** Do you see all three source types? Test successful!

---

## 5. Ověření Dat v Databázi / Database Verification

### Krok 5.1: Zobrazení Seznamu Všech Nápadů
**Display List of All Ideas**

```bash
python -m src.cli list --env-file .env.test
```

### Krok 5.2: Přímý Přístup k Databázi (Pokročilé)
**Direct Database Access (Advanced)**

```bash
# Instalace sqlite3 (pokud není nainstalováno)
# Install sqlite3 (if not installed)

# Linux/macOS/WSL - použijte interaktivní shell
# Linux/macOS/WSL - use interactive shell
sqlite3 test_db.s3db

# Nebo zkontrolujte data pomocí Python skriptu
# Or check data using Python script (see below)
```

**SQLite příkazy k testování (v sqlite3 shell) / SQLite commands to test (in sqlite3 shell):**
```sql
-- Zobrazit strukturu tabulky / Show table structure
.schema ideas

-- Počet záznamů / Count records
SELECT COUNT(*) FROM ideas;

-- Top 5 nápadů podle skóre / Top 5 ideas by score
SELECT source, source_id, title, score FROM ideas ORDER BY score DESC LIMIT 5;

-- Seskupení podle zdroje / Group by source
SELECT source, COUNT(*) as count FROM ideas GROUP BY source;

-- Exit
.quit
```

### Krok 5.3: Ověření Metadat
**Verify Metadata**

**Použití Python pro kontrolu dat / Using Python to check data:**

Můžete vytvořit jednoduchý Python skript pro inspekci databáze:

```python
# Uložit jako check_db.py / Save as check_db.py
import sqlite3
import json
import sys
from pathlib import Path

db_path = 'test_db.s3db'

# Check if database exists
if not Path(db_path).exists():
    print(f"Error: Database file '{db_path}' not found!")
    print("Run a scrape command first to create the database.")
    sys.exit(1)

try:
    conn = sqlite3.connect(db_path)
    # Use Row factory for better column access
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Zobrazit strukturu / Display structure
    cursor.execute('PRAGMA table_info(ideas)')
    columns = cursor.fetchall()
    print("Database columns:")
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")

    # Získat jeden záznam / Get one record
    cursor.execute('SELECT * FROM ideas LIMIT 1')
    row = cursor.fetchone()
    if row:
        print("\nSample record found!")
        print(f"Source: {row['source']}")
        print(f"Source ID: {row['source_id']}")
        print(f"Title: {row['title']}")
        print(f"Score: {row['score']}")
    else:
        print("\nNo records in database yet.")

    # Zkontrolovat score_dictionary (JSON)
    cursor.execute('SELECT score_dictionary FROM ideas WHERE score_dictionary IS NOT NULL LIMIT 1')
    result = cursor.fetchone()
    if result and result['score_dictionary']:
        score_dict = json.loads(result['score_dictionary'])
        print("\nScore Dictionary keys:")
        for key in score_dict.keys():
            print(f"  - {key}: {score_dict[key]}")

except sqlite3.Error as e:
    print(f"Database error: {e}")
    sys.exit(1)
finally:
    if conn:
        conn.close()
```

**Spustit skript / Run script:**
```bash
python check_db.py
```

**Očekávaná pole v score_dictionary / Expected fields in score_dictionary:**
```json
{
  "view_count": 125430,
  "like_count": 8234,
  "comment_count": 342,
  "engagement_rate": 6.84,
  "likes_per_view": 0.0656,
  "comments_per_view": 0.0027,
  "views_per_day": 8362.0,
  "upload_age_days": 15,
  "duration_seconds": 58,
  "quality_score": 85.3
}
```

✅ **Checkpoint:** Všechna očekávaná pole jsou přítomna a mají hodnoty?  
✅ **Checkpoint:** Are all expected fields present with values?

---

## 6. Test Zpracování na IdeaInspiration Formát

### Krok 6.1: Zpracování do Centrální Databáze
**Process to Central Database**

```bash
python -m src.cli process --env-file .env.test
```

**Co tento příkaz dělá / What this command does:**
- Transformuje YouTube metadata na standardní IdeaInspiration formát / Transforms YouTube metadata to standard IdeaInspiration format
- Ukládá do centrální databáze (Model modul) / Saves to central database (Model module)
- Přidává klasifikační značky / Adds classification tags

**Očekávaný výstup / Expected output:**
```
Processing YouTube Shorts to IdeaInspiration format...
Database: ./test_db.s3db

Found 33 YouTube Shorts records
Processing...
  [1/33] Processing: "Amazing Story Title"
    ✓ Transformed to IdeaInspiration
    ✓ Category: Content/Shorts
    ✓ Tags: storytelling, viral, engaging
    ✓ Saved to central DB
  ...
  [33/33] Processing: ...

Processing complete!
Total processed: 33
Total saved to central DB: 33
```

### Krok 6.2: Ověření v Centrální Databázi
**Verify in Central Database**

**Poznámka / Note:** Cesta k centrální databázi je spravována Model modulem (PrismQ.T.Idea.Inspiration.Model). Centrální databáze ukládá všechny IdeaInspiration záznamy ze všech zdrojů.

**Note:** The central database path is managed by the Model module (PrismQ.T.Idea.Inspiration.Model). The central database stores all IdeaInspiration records from all sources.

```bash
# ✅ DOPORUČENÝ ZPŮSOB / RECOMMENDED METHOD:
# Zkontrolovat výstup process příkazu, který zobrazí cestu
# Check process command output, which displays the path
python -m src.cli process --env-file .env.test

# Výstup ukáže cestu typu / Output will show path like:
# "Saving to central database: /full/path/to/PrismQ.T.Idea.Inspiration/Model/idea_inspiration.db"
# Tuto cestu pak použijte pro SQL dotazy / Use this path for SQL queries
```

**Tip:** Cestu ke centrální databázi vždy zkontrolujte z výstupu `process` příkazu místo předpokládání struktury adresářů.

**Tip:** Always check the central database path from the `process` command output instead of assuming directory structure.

✅ **Checkpoint:** Jsou data úspěšně zpracována do centrální databáze?  
✅ **Checkpoint:** Is data successfully processed to central database?

---

## 7. Pokročilé Testovací Scénáře / Advanced Test Scenarios

### Scénář 7.1: Test Deduplikace
**Test Deduplication**

```bash
# Spustit stejný scrape dvakrát / Run same scrape twice
python -m src.cli scrape-channel --env-file .env.test --top 5
python -m src.cli scrape-channel --env-file .env.test --top 5

# Zkontrolovat počet / Check count
python -m src.cli stats --env-file .env.test
```

**Očekávaný výsledek / Expected result:**
- Počet záznamů by měl zůstat stejný (ne zdvojnásobený) / Record count should remain the same (not doubled)
- Duplicitní záznamy jsou ignorovány / Duplicate records are ignored

### Scénář 7.2: Test s Různými Kanály
**Test with Different Channels**

```bash
# Test s jiným kanálem / Test with different channel
python -m src.cli scrape-channel --channel "@TechTips" --top 3 --env-file .env.test

python -m src.cli scrape-channel --channel "https://www.youtube.com/@LifeHacks101" --top 3 --env-file .env.test
```

### Scénář 7.3: Test Velkého Objemu Dat
**Test Large Data Volume**

```bash
# Varování: Toto může trvat 5-10 minut
# Warning: This may take 5-10 minutes
python -m src.cli scrape-channel --env-file .env.test --top 50
```

**Co sledovat / What to monitor:**
- Rychlost zpracování (videa/minutu) / Processing speed (videos/minute)
- Chybová hlášení / Error messages
- Využití paměti / Memory usage

### Scénář 7.4: Test Titulků a Metadat
**Test Subtitles and Metadata**

```bash
# Scrape s explicitním logováním / Scrape with explicit logging
python -m src.cli scrape-channel --channel "@SnappyStories_1" --top 3 --env-file .env.test 2>&1 | tee scrape_log.txt
```

**Kontrola logu / Check log:**
```bash
# Hledat subtitles v logu / Search for subtitles in log
grep -i "subtitle" scrape_log.txt  # Linux/macOS/WSL
findstr /i "subtitle" scrape_log.txt  # Windows
```

### Scénář 7.5: Test Různých Formátů URL
**Test Different URL Formats**

```bash
# Všechny tyto formáty by měly fungovat / All these formats should work
python -m src.cli scrape-channel --channel "@SnappyStories_1" --top 2 --env-file .env.test

python -m src.cli scrape-channel --channel "SnappyStories_1" --top 2 --env-file .env.test

python -m src.cli scrape-channel --channel "https://www.youtube.com/@SnappyStories_1" --top 2 --env-file .env.test

python -m src.cli scrape-channel --channel "https://www.youtube.com/@SnappyStories_1/shorts" --top 2 --env-file .env.test
```

**Očekávaný výsledek / Expected result:**
- Všechny formáty by měly fungovat identicky / All formats should work identically
- URL je normalizováno interně / URL is normalized internally

---

## 8. Řešení Problémů / Troubleshooting

### Problém 8.1: "No module named 'dotenv'"

**Řešení / Solution:**
```bash
pip install python-dotenv
```

### Problém 8.2: "yt-dlp command not found"

**Řešení / Solution:**
```bash
pip install --upgrade yt-dlp

# Ověření / Verify
yt-dlp --version
```

### Problém 8.3: "No Shorts found"

**Možné příčiny a řešení / Possible causes and solutions:**

1. **Kanál nemá Shorts / Channel has no Shorts**
   ```bash
   # Vyzkoušet testovací kanál / Try test channel
   python -m src.cli scrape-channel --channel "@SnappyStories_1" --top 5 --env-file .env.test
   ```

2. **Problém s připojením k internetu / Internet connection issue**
   ```bash
   # Test připojení / Test connection
   ping youtube.com
   curl -I https://www.youtube.com
   ```

3. **yt-dlp je zastaralý / yt-dlp is outdated**
   ```bash
   pip install --upgrade yt-dlp
   ```

### Problém 8.4: "Database locked"

**Řešení / Solution:**
```bash
# Zavřít všechny aplikace používající databázi / Close all apps using database
# Nebo smazat lock soubor / Or delete lock file
rm test_db.s3db-journal  # Linux/macOS/WSL
del test_db.s3db-journal  # Windows
```

### Problém 8.5: Timeout při stahování

**Řešení / Solution:**
```bash
# Snížit počet shorts / Reduce number of shorts
python -m src.cli scrape-channel --channel "@SnappyStories_1" --top 3 --env-file .env.test

# Zkontrolovat rychlost internetu / Check internet speed
# Zkusit znovu později / Try again later
```

### Problém 8.6: "Permission denied" při zápisu do databáze

**Řešení / Solution:**
```bash
# Linux/macOS/WSL - opravit oprávnění / Fix permissions
chmod 664 test_db.s3db

# Windows - spustit jako administrátor / Run as administrator
# Nebo zkontrolovat antivirový software / Or check antivirus software
```

### Problém 8.7: Nesprávné metriky nebo skóre

**Diagnostika / Diagnosis:**

Vytvořte diagnostický skript pro kontrolu dat:

```python
# Uložit jako diagnose_metrics.py / Save as diagnose_metrics.py
import sqlite3

conn = sqlite3.connect('test_db.s3db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Zkontrolovat raw data / Check raw data
cursor.execute('SELECT source_id, title, score, score_dictionary FROM ideas LIMIT 1')
row = cursor.fetchone()
if row:
    print(f"Source ID: {row['source_id']}")
    print(f"Title: {row['title']}")
    print(f"Score: {row['score']}")
    print(f"Score Dictionary: {row['score_dictionary']}")

conn.close()
```

**Spustit diagnostiku / Run diagnosis:**
```bash
python diagnose_metrics.py
```

**Řešení / Solution:**
- Ověřte, že score_dictionary obsahuje platná data / Verify score_dictionary contains valid data
- Re-scrape problematické video / Re-scrape problematic video
- Zkontrolujte logs pro chyby při extrakci metadat / Check logs for metadata extraction errors

---

## 9. Čistění a Reset / Cleanup and Reset

### Krok 9.1: Vymazání Všech Dat z Testovací Databáze
**Clear All Data from Test Database**

```bash
python -m src.cli clear --env-file .env.test
```

**Očekávaný výstup / Expected output:**
```
Warning: This will delete all ideas from the database!
Database: ./test_db.s3db
Are you sure? [y/N]: y

Clearing database...
Deleted 33 ideas
Database cleared successfully!
```

### Krok 9.2: Kompletní Reset
**Complete Reset**

```bash
# Smazat databázový soubor / Delete database file
rm test_db.s3db  # Linux/macOS/WSL
del test_db.s3db  # Windows

# Smazat testovací konfiguraci / Delete test configuration
rm .env.test  # Linux/macOS/WSL
del .env.test  # Windows

# Vytvořit znovu / Recreate
cp .env.test.example .env.test
```

### Krok 9.3: Deaktivace Virtuálního Prostředí
**Deactivate Virtual Environment**

```bash
deactivate
```

---

## 📊 Kontrolní Seznam Testů / Test Checklist

Po dokončení všech testů, ověřte následující:

**Základní Funkčnost / Basic Functionality:**
- [ ] Instalace závislostí úspěšná / Dependencies installed successfully
- [ ] CLI příkazy fungují / CLI commands work
- [ ] Channel scraping funguje / Channel scraping works
- [ ] Trending scraping funguje / Trending scraping works
- [ ] Keyword search funguje / Keyword search works

**Extrakce Dat / Data Extraction:**
- [ ] Metadata jsou kompletní (title, description, views, likes, comments) / Metadata is complete
- [ ] Titulky jsou extrahovány (pokud jsou dostupné) / Subtitles are extracted (when available)
- [ ] Engagement metriky jsou správně vypočítány / Engagement metrics calculated correctly
- [ ] Filtrování na Shorts (≤180s, vertikální) funguje / Filtering for Shorts (≤180s, vertical) works

**Úložiště Dat / Data Storage:**
- [ ] Data jsou uložena do SQLite databáze / Data saved to SQLite database
- [ ] Deduplikace funguje (žádné duplicity) / Deduplication works (no duplicates)
- [ ] score_dictionary je validní JSON / score_dictionary is valid JSON
- [ ] Všechna pole mají správný datový typ / All fields have correct data types

**Zpracování / Processing:**
- [ ] Transformace na IdeaInspiration formát funguje / Transform to IdeaInspiration format works
- [ ] Uložení do centrální databáze funguje / Save to central database works
- [ ] Kategorie a tagy jsou přiřazeny / Categories and tags are assigned

**Chybové Stavy / Error Handling:**
- [ ] Korektní zpracování neexistujícího kanálu / Proper handling of non-existent channel
- [ ] Timeout handling funguje / Timeout handling works
- [ ] Network errors jsou zachyceny / Network errors are caught
- [ ] Logování chyb je srozumitelné / Error logging is clear

---

## 🎯 Doporučené Testovací Kanály / Recommended Test Channels

| Kanál / Channel | URL | Účel / Purpose |
|-----------------|-----|----------------|
| **SnappyStories_1** | `@SnappyStories_1` | Oficiální testovací kanál / Official test channel |
| **Mr Beast Shorts** | `@MrBeast` | Velký kanál s mnoha Shorts / Large channel with many Shorts |
| **Kurzgesagt** | `@kurzgesagt` | Vzdělávací obsah / Educational content |
| **Daily Dose of Internet** | `@DailyDoseOfInternet` | Virální kratká videa / Viral short videos |

---

## 📝 Poznámky k Testování / Testing Notes

### Výkonnost / Performance
- **Rychlost scraping**: ~10-15 sekund per Short (včetně metadata a titulků) / ~10-15 seconds per Short (including metadata and subtitles)
- **Doporučený batch size**: 5-20 Shorts pro testování, 50-100 pro produkci / 5-20 Shorts for testing, 50-100 for production
- **Využití paměti**: ~50-100 MB pro typický scrape / ~50-100 MB for typical scrape

### Limity / Limitations
- **YouTube rate limiting**: yt-dlp respektuje rate limity / yt-dlp respects rate limits
- **Network timeouts**: 60 sekund per video / 60 seconds per video
- **Shorts definition**: max 180s, vertikální formát (výška > šířka) / max 180s, vertical format (height > width)

### Nejlepší Postupy / Best Practices
1. **Začněte malými testy** (--top 5) před velkými scrapes / Start with small tests (--top 5) before large scrapes
2. **Použijte .env.test** pro testování, .env pro produkci / Use .env.test for testing, .env for production
3. **Pravidelně čistěte testovací databázi** / Regularly clean test database
4. **Sledujte logy** pro chyby a varování / Monitor logs for errors and warnings
5. **Backup databáze** před velkými operacemi / Backup database before large operations

---

## 🆘 Podpora / Support

Pokud narazíte na problémy:  
If you encounter issues:

1. **Zkontrolujte sekci [Řešení Problémů](#8-řešení-problémů--troubleshooting)**  
   Check the [Troubleshooting](#8-řešení-problémů--troubleshooting) section

2. **Přečtěte si dokumentaci:**
   - [TESTING_GUIDE.md](./TESTING_GUIDE.md) - Automatizované testování / Automated testing
   - [SCRAPING_BEST_PRACTICES.md](./SCRAPING_BEST_PRACTICES.md) - Osvědčené postupy / Best practices
   - [README.md](../../README.md) - Obecný přehled / General overview

3. **Zkontrolujte logs a error messages**

4. **Nahlaste issue** na GitHub s:
   - Příkaz který jste spustili / Command you ran
   - Kompletní error message
   - Verze Python a yt-dlp
   - Operační systém

---

**Konec dokumentu / End of document**

**Verze / Version**: 1.0.0  
**Autor / Author**: PrismQ Team  
**Licence / License**: Proprietary - All Rights Reserved
