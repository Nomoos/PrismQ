# PrismQ.IdeaInspiration - Shrnutí Funkcionality

**Centrální systém pro sběr, klasifikaci, hodnocení a zpracování nápadů na obsah pomocí umělé inteligence**

## 📋 Obsah

1. [Přehled systému](#přehled-systému)
2. [Základní moduly](#základní-moduly)
3. [Architektura a datový tok](#architektura-a-datový-tok)
4. [Klíčové funkce](#klíčové-funkce)
5. [Technické specifikace](#technické-specifikace)
6. [Případy použití](#případy-použití)

---

## Přehled systému

PrismQ.IdeaInspiration je komplexní ekosystém nástrojů pro objevování, vyhodnocování a správu nápadů na obsah z různých zdrojů. Tento systém poskytuje AI-powered řešení pro tvorbu krátkého video obsahu optimalizovaného pro platformy jako YouTube Shorts, TikTok a Instagram Reels.

### 🎯 Hlavní účel

Systém poskytuje nástroje pro:
- **Sběr** nápadů z různých zdrojů obsahu (YouTube, Reddit, články, texty písní, trendy atd.)
- **Klasifikaci** obsahu do kategorií a detekci příběhového potenciálu
- **Hodnocení** obsahu na základě engagement metrik a kvalitativních ukazatelů
- **Modelování** unifikovaných datových struktur pro multiplatformní obsah
- **Správu** konfigurace a centralizované zpracování dat

---

## Základní moduly

### 1. 📦 Model
**Účel**: Základní datový model a databázová struktura

#### Klíčové komponenty:
- **IdeaInspiration**: Unifikovaný datový model pro reprezentaci obsahu napříč různými médii (text, video, audio)
- **ContentType**: Enumerace typů obsahu (TEXT, VIDEO, AUDIO, UNKNOWN)
- **Database Setup**: Automatizované skripty pro vytvoření SQLite databáze

#### Datová struktura IdeaInspiration:
```python
- title: str                      # Název/titulek obsahu
- description: str                # Krátký popis nebo shrnutí
- content: str                    # Hlavní textový obsah
- keywords: List[str]             # Seznam relevantních klíčových slov
- source_type: ContentType        # Typ zdroje obsahu
- metadata: Dict[str, str]        # Dodatečná metadata specifická pro zdroj
- source_id: Optional[str]        # Unikátní ID ze zdrojové platformy
- source_url: Optional[str]       # URL k původnímu obsahu
- source_created_by: Optional[str] # Autor/tvůrce obsahu
- source_created_at: Optional[str] # Časové razítko vytvoření
- score: Optional[int]            # Číselné hodnocení (0-100)
- category: Optional[str]         # Primární kategorie
- subcategory_relevance: Dict[str, int]  # Relevance podkategorií
- contextual_category_scores: Dict[str, int]  # Kontextové skóre
```

#### Factory metody:
- `IdeaInspiration.from_text()` - Vytvoření z textového obsahu
- `IdeaInspiration.from_video()` - Vytvoření z videa s titulky
- `IdeaInspiration.from_audio()` - Vytvoření z audia s transkripcí
- `IdeaInspiration.to_dict()` / `from_dict()` - Serializace

### 2. 🎨 Classification
**Účel**: Klasifikace obsahu a detekce příběhů

#### Hlavní funkce:

**Primary Category Classifier**
- Kategorizuje obsah do 8 primárních kategorií optimalizovaných pro krátké video:
  1. **Storytelling** - Příběhy, fikční nebo skutečné (Storytime, POV, zpovědi, AITA, TIFU)
  2. **Entertainment** - Rychlý zábavný obsah (memy, komedie, žerty, fails, reakce)
  3. **Education / Informational** - Vysvětlení, tutoriály, fakta, produktivní tipy
  4. **Lifestyle / Vlog** - Každodenní život, krása, móda, fitness, jídlo, cestování
  5. **Gaming** - Herní klipy, highlights, speedruny, walkthroughs
  6. **Challenges & Trends** - Sociální výzvy, trendové zvuky, AR efekty
  7. **Reviews & Commentary** - Recenze produktů, reakce, komentáře
  8. **Unusable** - Obsah nepoužitelný pro generování příběhů

**Story Detector**
- Binární klasifikátor identifikující obsah založený na příběhu
- Používá váhovanou klíčovou analýzu napříč titulkem, popisem, tagy a titulky
- Poskytuje skóre důvěryhodnosti (0.0-1.0)

**Generalized Text Classifier**
- Unifikovaná klasifikace textu pracující s modelem IdeaInspiration
- Hodnotí více textových polí (title, description, content)
- Integruje kategorizaci a detekci příběhů
- Poskytuje detailní hodnocení na úrovni jednotlivých polí

#### Příklad použití:
```python
from prismq.idea.classification import CategoryClassifier, StoryDetector

classifier = CategoryClassifier()
result = classifier.classify(
    title="My AITA Story - Was I Wrong?",
    description="Let me tell you about what happened yesterday...",
    tags=['storytime', 'aita', 'confession']
)

# Výsledek: kategorie, skóre důvěry, indikátory
```

### 3. 📊 Scoring
**Účel**: Hodnocení kvality a engagement obsahu

#### Typy metrik:

**Engagement metriky:**
- **Basic Score**: Vážené skóre založené na views, likes, komentářích
- **Engagement Rate (ER)**: `(likes + comments + shares + saves) / views × 100%`
- **Watch-Through Rate**: `(průměrný čas sledování / délka videa) × 100%`
- **Conversion Rate (CR)**: `konverze / views × 100%`
- **Relative Performance Index (RPI)**: `(aktuální metrika / mediánová hodnota kanálu) × 100%`
- **Universal Content Score (UCS)**: Kompozitní skóre kombinující ER, Watch-Through a RPI

**AI textové kvalitativní metriky:**
- **Readability Score**: Flesch Reading Ease a Flesch-Kincaid Grade Level
- **Text Structure**: Hodnocení struktury odstavců a vět
- **Length Score**: Optimální délkové rozsahy pro různé typy obsahu
- **Sentiment Analysis**: Detekce pozitivního, negativního nebo neutrálního sentimentu
- **Title Relevance**: Jak dobře titulek odpovídá obsahu
- **Title Quality**: Optimální délka a počet slov pro titulky
- **Description Quality**: Optimální délka a struktura pro popisy

#### Podporované platformy:
- YouTube (view counts, likes, comments)
- Reddit (upvotes, comments, views)
- Generický obsah (vlastní engagement metriky)

#### Batch processing:
```python
from src.scoring import ScoringEngine

engine = ScoringEngine()
score_breakdowns = engine.score_idea_inspiration_batch(ideas)
# Vrací seznam ScoreBreakdown objektů s detailním hodnocením
```

### 4. 🔌 Sources
**Účel**: Sběr obsahu z různých platforem

#### Architektura Single Database:
Všechny zdroje používají jednotnou databázovou architekturu:
- **Centrální databáze**: Všechny IdeaInspiration objekty v jedné databázi
- **source_platform**: Identifikátor zdroje pro filtrování (např. "youtube", "google_trends", "genius")
- **metadata**: Platformně specifická data uložená jako slovník
- **Výhody**: Jednodušší správa, unifikované dotazy, bez duplikace dat

#### Kategorie zdrojů:

**Creative Sources** (Kreativní inspirace)
- ✅ **LyricSnippets**: Texty písní z Genius API
- 🚧 **ScriptBeats**: Narativní struktury
- 🚧 **VisualMoodboard**: Vizuální estetika

**Signal Sources** (Časné indikátory trendů)
- ✅ **GoogleTrends**: Vyhledávací trendy
- 🚧 **NewsApi**: Zpravodajské API
- 🚧 **GoogleNews**: Agregace zpráv
- 🚧 **SocialChallenge**: Virální výzvy
- 🚧 **GeoLocalTrends**: Lokální trendy

**Event Sources** (Plánované a opakující se události)
- ✅ **CalendarHolidays**: Svátky a význačné dny
- 🚧 **SportsHighlights**: Sportovní události
- 🚧 **EntertainmentReleases**: Vydání filmů/hudby

**Content Sources** (Bohaté obsahové zdroje)
- YouTube Shorts, TikTok, Instagram Reels
- Medium články, webové články
- Podcasty (Apple, Spotify)
- Fóra (Reddit, HackerNews)
- Streaming klipy (Kick)

### 5. ⚙️ ConfigLoad
**Účel**: Centralizovaná správa konfigurace

#### Klíčové funkce:
- Automatické vyhledávání a načítání `.env` souborů
- Centralizované ukládání konfigurace v `PrismQ_WD` adresáři
- Interaktivní dotazování na chybějící konfigurační hodnoty
- Komplexní logování s metadaty modulů a systémovými informacemi
- Podpora pro konzolové i souborové logování

#### Použití:
```python
from ConfigLoad import Config, get_module_logger

# Inicializace konfigurace
config = Config()

# Získání hodnot
database_url = config.get("DATABASE_URL", "sqlite:///default.db")

# Získání nebo dotaz na hodnoty
api_key = config.get_or_prompt(
    "API_KEY",
    "Zadejte váš API klíč",
    required=True
)
```

### 6. 💻 Client
**Účel**: Webové rozhraní pro správu a kontrolu

Webový klient poskytuje vizuální rozhraní pro:
- Správu modulů (spouštění, monitorování)
- Prohlížení a filtrování IdeaInspiration objektů
- Sledování zpracování (Classification, Scoring)
- Live logy a monitoring úloh

---

## Architektura a datový tok

### Typický workflow

```
┌─────────────────────────────────────────────────┐
│              PrismQ.IdeaInspiration             │
└─────────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
    ┌───▼───┐    ┌───▼────┐   ┌───▼──────┐
    │Sources│───▶│  Model │◀──│ConfigLoad│
    └───┬───┘    └───┬────┘   └──────────┘
        │            │
        │      ┌─────┴──────┐
        │      │            │
    ┌───▼──────▼─┐   ┌─────▼────────┐
    │Classification│   │   Scoring    │
    └──────┬───────┘   └──────┬───────┘
           │                  │
           └────────┬─────────┘
                    │
              ┌─────▼──────┐
              │   Client   │
              └────────────┘
```

### Krok za krokem:

1. **Sources** → Sběr obsahu z různých platforem
   - YouTube trendy, Reddit posty, texty písní, události, trendy
   
2. **Model** → Transformace do unifikované struktury IdeaInspiration
   - Standardizace datového formátu
   - Ukládání do centrální databáze
   
3. **Classification** → Kategorizace a detekce příběhového potenciálu
   - Přiřazení do 8 primárních kategorií
   - Detekce, zda obsah obsahuje příběh
   - Generování relevančních skóre podkategorií
   
4. **Scoring** → Hodnocení kvality a engagement metrik
   - Výpočet composite score (0-100)
   - Analýza čitelnosti a sentimentu
   - Hodnocení engagement metrik
   
5. **ConfigLoad** → Správa konfigurace napříč všemi moduly
   - Centralizované nastavení
   - Logování a monitoring
   
6. **Client** → Vizualizace a správa pomocí webového rozhraní
   - Dashboard pro monitoring
   - Filtrace a vyhledávání IdeaInspiration objektů
   - Spouštění batch procesů

---

## Klíčové funkce

### 1. Unifikovaný datový model
- Jednotná struktura pro text, video a audio obsah
- Factory metody pro snadné vytváření z různých zdrojů
- Serializace do/z JSON pro ukládání a přenos dat
- Kompatibilita s SQLite databází

### 2. Batch processing
- **Classification**: Zpracování seznamů IdeaInspiration objektů
  ```bash
  python3 Classification/src/cli.py < input.json > output.json
  ```
  
- **Scoring**: Hromadné hodnocení obsahu
  ```bash
  python3 Scoring/src/cli.py < input.json > output.json
  ```

- **Pipeline**: Kombinované zpracování
  ```bash
  python3 generate_data.py | \
    python3 Classification/src/cli.py | \
    python3 Scoring/src/cli.py > results.json
  ```

### 3. Jednotná databázová architektura
- Všechny zdroje ukládají do jedné centrální databáze
- Pole `source_platform` identifikuje původ dat (např. "youtube", "google_trends")
- Platformně specifická metadata uložena ve slovníku `metadata`
- Snadné dotazování napříč zdroji: `db.get_all(source_platform="youtube")`
- Jednodušší správa a údržba bez duplikace dat

### 4. Flexibilní konfigurace
- Automatické vyhledávání PrismQ pracovního adresáře
- Persistentní konfigurace v `.env` souborech
- Interaktivní i neinteraktivní režim (pro CI/CD)
- Centralizované nastavení pro všechny moduly

### 5. Komplexní testování
- Unit testy pro všechny komponenty
- Integrační testy pro end-to-end workflow
- Coverage analýza (>80% pokrytí kódu)
- Automatizované testy v CI/CD pipeline

---

## Technické specifikace

### Cílová platforma

Systém je optimalizován pro:
- **Operační systém**: Windows
- **GPU**: NVIDIA RTX 5090 (Ada Lovelace architektura, 32GB VRAM)
- **CPU**: AMD Ryzen procesor
- **RAM**: 64GB DDR5

### Technologie

- **Jazyk**: Python 3.10+
- **Databáze**: SQLite (.s3db soubory)
- **Web framework**: Flask (pro Client backend)
- **Frontend**: HTML/CSS/JavaScript
- **API**: REST API pro komunikaci mezi moduly
- **Logování**: Python logging s rotací souborů

### Design principy

Systém dodržuje následující principy:

**SOLID principy:**
- **Single Responsibility**: Každá třída má jednu zodpovědnost
- **Open/Closed**: Otevřeno pro rozšíření, uzavřeno pro modifikaci
- **Liskov Substitution**: Podtypy musí být zaměnitelné za své základní typy
- **Interface Segregation**: Používání fokusovaných, minimálních rozhraní
- **Dependency Inversion**: Závislost na abstrakcích, injekce závislostí

**Další principy:**
- **DRY** (Don't Repeat Yourself): Eliminace duplicity kódu
- **KISS** (Keep It Simple): Upřednostňování jednoduchosti před složitostí
- **YAGNI** (You Aren't Gonna Need It): Implementace pouze toho, co je aktuálně potřeba
- **Composition Over Inheritance**: Upřednostňování kompozice objektů před dědičností

---

## Případy použití

### 1. Sběr a analýza trendových videí
```python
# Sběr trendových YouTube Shorts
from sources.youtube import YouTubeTrendingPlugin
from idea_inspiration import IdeaInspiration

plugin = YouTubeTrendingPlugin(config)
shorts = plugin.scrape_by_keyword("true crime", top_n=20)
# Vrací: List[IdeaInspiration]
```

### 2. Klasifikace a hodnocení obsahu
```python
from prismq.idea.classification import TextClassifier
from src.scoring import ScoringEngine

classifier = TextClassifier()
engine = ScoringEngine()

# Klasifikace
enrichments = classifier.enrich_batch(ideas)

# Hodnocení
score_breakdowns = engine.score_idea_inspiration_batch(ideas)

# Aktualizace objektů
for idea, enrichment, breakdown in zip(ideas, enrichments, score_breakdowns):
    idea.category = enrichment.category.value
    idea.score = int(breakdown.overall_score)
    idea.subcategory_relevance = enrichment.subcategory_relevance
```

### 3. Pipeline zpracování přes CLI
```bash
# Kompletní pipeline: sběr → klasifikace → hodnocení
python3 Sources/Creative/LyricSnippets/src/cli.py scrape --query "pop songs" | \
  python3 Classification/src/cli.py | \
  python3 Scoring/src/cli.py > \
  processed_lyrics.json
```

### 4. Vyhledávání inspirace pro tvorbu obsahu
```python
from idea_inspiration_db import IdeaInspirationDatabase

db = IdeaInspirationDatabase("db.s3db")

# Vyhledávání podle klíčových slov
true_crime_ideas = db.filter(keywords=["true_crime"])

# Vyhledávání podle platformy
youtube_ideas = db.filter(metadata_contains={'platform': 'youtube'})

# Kombinované filtry
trending_shorts = db.filter(
    keywords=["mystery"],
    metadata_contains={'platform': 'youtube', 'is_short': 'true'},
    min_score=70,
    days_back=7
)
```

### 5. Monitorování a správa přes webové rozhraní
- Přístup k Client webovému rozhraní
- Prohlížení všech IdeaInspiration objektů
- Filtrace podle kategorie, skóre, data
- Spouštění batch procesů
- Sledování live logů a stavu úloh

---

## Souhrn

PrismQ.IdeaInspiration je komplexní, modulární systém pro:
- ✅ **Sběr** obsahu z více než 30 různých zdrojů
- ✅ **Klasifikaci** do 8 kategorií s detekcí příběhového potenciálu
- ✅ **Hodnocení** pomocí engagement a AI textových metrik
- ✅ **Správu** jednotné databáze inspiračních nápadů
- ✅ **Automatizaci** batch zpracování přes CLI
- ✅ **Vizualizaci** a kontrolu přes webové rozhraní

Systém je navržen pro profesionální tvorbu krátkého video obsahu s důrazem na:
- **Modularitu**: Každý modul lze použít samostatně
- **Rozšiřitelnost**: Snadné přidávání nových zdrojů a funkcí
- **Výkon**: Optimalizováno pro NVIDIA RTX 5090
- **Kvalitu**: Vysoké pokrytí testy, SOLID principy
- **Použitelnost**: CLI i webové rozhraní

---

**Verze dokumentu**: 1.0  
**Datum**: Listopad 2025  
**Součást**: PrismQ Ekosystém - AI-powered platforma pro generování obsahu
