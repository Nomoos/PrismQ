# Výzkumné Otázky - Kompletní Odpovědi

**Dokument Vytvořen**: 2025-11-14  
**Účel**: Odpovědi na klíčové výzkumné otázky o organizaci Research_Layers a best practices

---

## 🎯 Rychlé Shrnutí

Tento dokument odpovídá na klíčové výzkumné otázky:
1. ✅ Python příklady přidány napříč Research_Layers
2. ✅ Strategie virtuálních prostředí pro vrstvy s různými závislostmi
3. ✅ Vzory integrace vrstev a protokolů
4. ✅ Design patterns použitelné v tomto projektu
5. ✅ Identifikované problémy a strategie jejich zmírnění
6. ✅ Úvahy o jazyce (Angličtina/Čeština)
7. ✅ Kompilace best practices
8. ✅ Clean code a PEP standardy průvodce

---

## 1. Python Příklady napříč Research_Layers

### Stav Implementace

Všechny hlavní sekce nyní obsahují praktické Python příklady:

#### **01_Architecture** - Příklady Vrstev
- `examples/layer_separation.py` - Ukazuje správné hranice vrstev
- Demonstrace směru závislostí
- Komunikace mezi vrstvami založená na protokolech

#### **02_Design_Patterns** - Implementace Vzorů
- `examples/solid_single_responsibility.py` - SRP v praxi
- `examples/solid_open_closed.py` - OCP s abstrakcemi
- `examples/solid_dependency_inversion.py` - DIP s dependency injection
- `examples/design_patterns.py` - Strategy, Factory, Observer, Adapter, Repository
- `examples/design_patterns_extended.py` - 🆕 Rozšířené vzory

#### **03_Testing** - Testovací Vzory
- Příklady jednotkových testů
- Testy integrace vrstev
- Vzory mockování

---

## 2. Virtuální Prostředí pro Různé Vrstvy

### Strategie: Virtuální Prostředí Specifická pro Vrstvu

Každá vrstva může mít své vlastní virtuální prostředí se specifickými závislostmi:

```
PrismQ.IdeaInspiration/
├── Source/
│   ├── Audio/
│   │   ├── venv/              # Závislosti specifické pro Audio
│   │   ├── requirements.txt   # pydub, spotify-api, atd.
│   │   └── pyproject.toml
│   ├── Video/
│   │   ├── venv/              # Závislosti specifické pro Video
│   │   ├── requirements.txt   # yt-dlp, opencv, atd.
│   │   └── pyproject.toml
│   └── TaskManager/
│       ├── venv/              # Závislosti API klienta
│       └── requirements.txt   # requests, httpx, atd.
```

### Instalační Skript

```bash
# setup_environments.sh
#!/bin/bash

# Funkce pro nastavení venv pro modul
setup_module_venv() {
    local module_path=$1
    echo "Nastavuji venv pro $module_path"
    
    cd "$module_path"
    py -3.10 -m venv venv
    
    # Aktivace a instalace závislostí
    source venv/Scripts/activate  # Windows: venv\Scripts\activate
    pip install --upgrade pip
    pip install -e .
    deactivate
}

# Nastavení každé vrstvy
setup_module_venv "Source/Audio"
setup_module_venv "Source/Video/YouTube"
setup_module_venv "Classification"
setup_module_venv "Model"
```

### Proč Virtuální Prostředí Specifická pro Vrstvu?

**Výhody:**
- ✅ **Izolace Závislostí**: Zabraňuje konfliktům mezi závislostmi vrstev
- ✅ **Rychlost Vývoje**: Rychlejší instalace pro vývoj jedné vrstvy
- ✅ **Flexibilita Nasazení**: Lze nasadit vrstvy nezávisle
- ✅ **Kontrola Verzí**: Různé vrstvy mohou používat různé verze knihoven
- ✅ **Izolace Testování**: Test jedné vrstvy bez závislostí ostatních

**Úvahy:**
- ⚠️ **Diskový Prostor**: Více venv zabírá více místa (zvladatelné)
- ⚠️ **Složitost Nastavení**: Vyžaduje správu více prostředí
- ⚠️ **Konfigurace IDE**: Potřeba konfigurovat IDE pro každé venv

---

## 3. Vzory Integrace Vrstev

### Strategie Integrace: Hranice Založené na Protokolech

Použití Python Protokolů (PEP 544) k definování kontraktů mezi vrstvami:

```python
from typing import Protocol, List
from dataclasses import dataclass

# Doménový model (vrstva Model)
@dataclass
class IdeaInspiration:
    id: str
    title: str
    source: str

# Protokol definuje kontrakt (žádná implementace)
class IdeaRepository(Protocol):
    """Kontrakt repository pro persistence vrstvu."""
    
    def save(self, idea: IdeaInspiration) -> str: ...
    def get_by_id(self, id: str) -> IdeaInspiration: ...
    def list_all(self) -> List[IdeaInspiration]: ...

# Vyšší vrstva závisí na protokolu, ne na implementaci
class IdeaService:
    """Servisní vrstva orchestruje business logiku."""
    
    def __init__(self, repository: IdeaRepository):
        # Závisí na abstrakci, ne na konkrétní třídě
        self._repository = repository
```

### Komunikační Vzory

**1. Přímá Dependency Injection (Preferováno)**
```python
# Propojení aplikace
db_repository = SqliteIdeaRepository("database.db")
service = IdeaService(repository=db_repository)
```

**2. Factory Pattern**
```python
class RepositoryFactory:
    @staticmethod
    def create(db_type: str) -> IdeaRepository:
        if db_type == "sqlite":
            return SqliteIdeaRepository()
        elif db_type == "postgres":
            return PostgresIdeaRepository()
```

---

## 4. Design Patterns pro PrismQ

### Použitelné Design Patterns

#### **1. Strategy Pattern** ⭐⭐⭐⭐⭐
**Případ Použití**: Různé content source scrapers (YouTube, TikTok, Reddit)

```python
class ContentScrapingStrategy(Protocol):
    def scrape(self, url: str) -> List[IdeaInspiration]: ...

class YouTubeScrapingStrategy:
    def scrape(self, url: str) -> List[IdeaInspiration]:
        # YouTube-specifické scrapování
        pass

class ContentScraper:
    def __init__(self, strategy: ContentScrapingStrategy):
        self.strategy = strategy
```

#### **2. Factory Pattern** ⭐⭐⭐⭐⭐
**Případ Použití**: Vytváření workerů podle typu úkolu

```python
class WorkerFactory:
    _registry = {}
    
    @classmethod
    def register(cls, task_type: str, worker_class):
        cls._registry[task_type] = worker_class
    
    @classmethod
    def create(cls, task_type: str) -> Worker:
        worker_class = cls._registry.get(task_type)
        if not worker_class:
            raise ValueError(f"Neznámý typ úkolu: {task_type}")
        return worker_class()
```

#### **3. Repository Pattern** ⭐⭐⭐⭐⭐
**Případ Použití**: Abstrakce přístupu k datům (již použito v projektu)

#### **4. Observer Pattern** ⭐⭐⭐⭐
**Případ Použití**: Notifikace dokončení úkolů, sledování průběhu

#### **5. Adapter Pattern** ⭐⭐⭐⭐
**Případ Použití**: Adaptace third-party API na interní rozhraní

#### **6. Template Method Pattern** ⭐⭐⭐
**Případ Použití**: Základní worker s přizpůsobitelnými kroky

#### **7. Singleton Pattern** ⭐⭐
**Případ Použití**: Configuration loader, databázová spojení (používat střídmě)

---

## 5. Identifikované Problémy a Zmírnění Rizik

### Problém 1: Peklo Závislostí mezi Vrstvami
**Riziko**: Konfliktní závislosti mezi vrstvami (např. různé verze ML knihoven)

**Zmírnění**:
- ✅ Použití virtuálních prostředí specifických pro vrstvu
- ✅ Připnutí závislostí s rozsahy verzí v `pyproject.toml`
- ✅ Použití kontroly závislostí (pip-audit, safety)
- ✅ Pravidelné aktualizace závislostí kontrolovaným způsobem

### Problém 2: Porušení Hranic Vrstev
**Riziko**: Vyšší vrstvy přímo přistupují k implementacím nižších vrstev

**Zmírnění**:
- ✅ Použití Python Protokolů k definování kontraktů
- ✅ Dependency Inversion Principle (závislost na abstrakcích)
- ✅ Kontrolní seznam code review pro porušení vrstev
- ✅ Nástroje statické analýzy (mypy se strict módem)

### Problém 3: Složitost Testování s Více Venv
**Riziko**: Obtížné spuštění testů napříč všemi vrstvami

**Zmírnění**:
- ✅ Hlavní testovací skript, který aktivuje každé venv
- ✅ CI/CD pipeline automaticky zpracovává nastavení venv
- ✅ Mock externí závislosti v jednotkových testech
- ✅ Integrační testy běží v samostatné fázi

---

## 6. Jazykové Úvahy (Angličtina/Čeština)

### Současný Přístup: Angličtina Primární, Čeština Volitelná

**Rozhodnutí**: Použití angličtiny jako primárního jazyka dokumentace

**Zdůvodnění**:
- ✅ **Mezinárodní Spolupráce**: Angličtina umožňuje globální přispěvatele
- ✅ **Technické Zdroje**: Většina technických zdrojů v angličtině
- ✅ **Kódové Standardy**: PEP 8, SOLID, atd. referencovány v angličtině
- ✅ **Dokumentace Knihoven**: Závislosti dokumentovány v angličtině
- ✅ **Kariérní Růst**: Psaní technické angličtiny je cenná dovednost

### Podpora Českého Jazyka

**Kde je Čeština Vhodná**:
- ✅ Týmové schůzky a diskuse (pokud je tým český)
- ✅ Interní poznámky a brainstorming
- ✅ Uživatelská dokumentace (pokud jsou uživatelé čeští)

**Kde je Angličtina Vyžadována**:
- ✅ Kód (proměnné, funkce, třídy, komentáře)
- ✅ Technická dokumentace
- ✅ Architecture Decision Records (ADR)
- ✅ API dokumentace
- ✅ Git commit zprávy

### Best Practice: Kód a Komentáře v Angličtině

```python
# ✅ DOBŘE: Anglický kód a komentáře
class VideoProcessor:
    """Process video content for idea extraction."""
    
    def extract_ideas(self, video_url: str) -> List[IdeaInspiration]:
        """Extract idea inspirations from video."""
        pass

# ❌ ŠPATNĚ: Smíšená čeština/angličtina
class VideoProcesor:
    """Zpracování video obsahu pro extrakci nápadů."""
    
    def extrahuj_napady(self, video_url: str) -> List[IdeaInspiration]:
        """Extrahuje nápady z videa."""
        pass
```

---

## 7. Kompilace Best Practices

### Python Best Practices (PEP 8 + Rozšíření)

#### **1. Konvence Pojmenování**

```python
# ✅ DOBŘE: Jasná, popisná jména
class YouTubeVideoScraper:
    MAX_RETRY_ATTEMPTS = 3
    
    def __init__(self, api_key: str):
        self._api_key = api_key  # Soukromý atribut
    
    def fetch_video_metadata(self, video_id: str) -> VideoMetadata:
        pass
```

#### **2. Type Hints (PEP 484)**

```python
from typing import List, Optional, Dict, Any

# ✅ DOBŘE: Kompletní type hints
def process_videos(
    video_ids: List[str],
    options: Optional[Dict[str, Any]] = None
) -> List[IdeaInspiration]:
    """Zpracování více videí a vrácení nápadů."""
    pass
```

#### **3. Docstrings (PEP 257 + Google Style)**

```python
# ✅ DOBŘE: Kompletní docstring
def calculate_relevance_score(
    title: str,
    description: str,
    categories: List[str]
) -> float:
    """Vypočítat skóre relevance pro obsah.
    
    Analyzuje titulek, popis a kategorie pro výpočet
    skóre relevance mezi 0.0 a 1.0.
    
    Args:
        title: Titulek obsahu (povinný, neprázdný)
        description: Popis obsahu (může být prázdný)
        categories: Seznam tagů kategorií
    
    Returns:
        Skóre relevance mezi 0.0 (nerelevantní) a 1.0 (vysoce relevantní)
    
    Raises:
        ValueError: Pokud je titulek prázdný nebo seznam kategorií prázdný
    """
    pass
```

---

## 8. Clean Code Principy

### Základní Principy z "Clean Code" od Robert C. Martin

#### **1. Smysluplná Jména**

```python
# ✅ DOBŘE: Odhaluje záměr
def get_active_youtube_videos_from_last_week() -> List[Video]:
    pass

# ❌ ŠPATNĚ: Nejasné zkratky
def get_act_yt_vids_lst_wk():
    pass
```

#### **2. Funkce By Měly Dělat Jednu Věc**

```python
# ✅ DOBŘE: Jediná odpovědnost
def extract_video_id(url: str) -> str:
    """Extrahovat video ID z YouTube URL."""
    pass

def validate_video_id(video_id: str) -> bool:
    """Validovat formát video ID."""
    pass
```

#### **3. DRY (Don't Repeat Yourself)**

```python
# ✅ DOBŘE: Extrahovat společnou logiku
def format_timestamp(dt: datetime) -> str:
    """Formátovat datetime na ISO string."""
    return dt.isoformat()

def save_video(video: Video):
    video.created_at = format_timestamp(datetime.now())
    # Použití helperu

def save_channel(channel: Channel):
    channel.created_at = format_timestamp(datetime.now())
    # Opětovné použití stejného helperu
```

---

## 9. PEP Standardy Rychlý Přehled

### Klíčové PEP pro Tento Projekt

#### **PEP 8 - Style Guide pro Python Kód**

**Klíčové Body**:
- Odsazení: 4 mezery (žádné tabulátory)
- Délka řádku: 79-88 znaků (88 pro Black formatter)
- Importy: seskupené (stdlib, third-party, local)
- Pojmenování: `snake_case` pro funkce/proměnné, `PascalCase` pro třídy

#### **PEP 484 - Type Hints**

```python
from typing import List, Dict, Optional, Union

def process_videos(
    video_ids: List[str],
    options: Optional[Dict[str, str]] = None
) -> Union[List[IdeaInspiration], None]:
    """Zpracování více videí."""
    pass
```

#### **PEP 544 - Protokoly (Structural Subtyping)**

```python
from typing import Protocol

class Drawable(Protocol):
    """Protokol pro kreslitelné objekty."""
    
    def draw(self) -> None:
        """Nakreslit objekt."""
        ...

# Jakákoli třída s metodou draw() je Drawable
class Circle:
    def draw(self) -> None:
        print("Kreslím kruh")

# Žádné explicitní dědění není potřeba!
def render(obj: Drawable) -> None:
    obj.draw()
```

---

## 10. Shrnutí a Rychlé Akce

### ✅ Dokončeno

1. **Python Příklady**: Přidány napříč Research_Layers
2. **Strategie Virtuálních Prostředí**: Dokumentováno a implementováno
3. **Integrace Vrstev**: Vzory založené na protokolech dokumentovány
4. **Design Patterns**: Identifikovány a implementovány použitelné vzory
5. **Problémy**: Identifikovány a zmírněny
6. **Jazyk**: Potvrzena angličtina jako primární (správný přístup)
7. **Best Practices**: Sestaven komplexní průvodce
8. **Clean Code**: Zdokumentovány principy s příklady
9. **PEP Standardy**: Vytvořen rychlý přehled

### 🎯 Rychlé Odkazy

- **SOLID Příklady**: `02_Design_Patterns/examples/`
- **Testovací Vzory**: `03_Testing/examples/`
- **Architektura Vrstev**: `01_Architecture/examples/`
- **Worker Šablony**: `05_Templates/`
- **Rychlý Přehled**: `QUICK_REFERENCE.md`

---

**Poslední Aktualizace**: 2025-11-14  
**Spravuje**: PrismQ Architecture Team  
**Další Revize**: Čtvrtletně

---
