# PrismQ.T.Story.From.Idea

Specializovaný modul pro tvorbu Story objektů z Idea objektů.

## Popis

Tento modul poskytuje funkcionalitu pro vytváření Story objektů z Idea objektů, které ještě nemají reference v Story tabulce.

**Klíčové funkce:**
1. Vybere nejstarší Idea objekt bez referencí ve Story tabulce
2. Vytvoří 10x Story objektů s referencí na Idea (bez Titulku a Scriptu)
3. Story objekty jsou vytvořeny ve stavu `PrismQ.T.Title.From.Idea`

## Pozice ve workflow

```
PrismQ.T.Idea.From.User
       ↓
PrismQ.T.Story.From.Idea (vytvoří pouze Stories) ← Tento modul
       ↓
PrismQ.T.Title.From.Idea (generuje Titulky pro Stories)
```

## Použití

### Hlavní workflow (zpracování nejstarší neodkazované Idea)

```python
from T.Story.From.Idea import StoryFromIdeaService, process_oldest_unreferenced_idea
from T.Idea.Model.src.simple_idea_db import SimpleIdeaDatabase
import sqlite3

# Připojení k databázím
story_conn = sqlite3.connect("prismq.db")
story_conn.row_factory = sqlite3.Row

idea_db = SimpleIdeaDatabase("idea.db")
idea_db.connect()

# Vytvoření služby
service = StoryFromIdeaService(story_conn, idea_db)

# Zpracovat nejstarší neodkazovanou Idea (hlavní workflow)
result = service.process_oldest_unreferenced_idea()
if result:
    print(f"Vytvořeno {result.count} Stories pro Idea {result.idea_id}")
else:
    print("Žádná neodkazovaná Idea nenalezena")

# Nebo použít pomocnou funkci
result = process_oldest_unreferenced_idea(story_conn, idea_db)
```

### Další možnosti použití

```python
# Získat nejstarší neodkazovanou Idea
oldest = service.get_oldest_unreferenced_idea()
if oldest:
    print(f"Nejstarší neodkazovaná Idea: {oldest.id}")

# Získat všechny neodkazované Ideas (seřazené podle stáří)
unreferenced = service.get_unreferenced_ideas()
print(f"Nalezeno {len(unreferenced)} Ideas bez Stories")

# Zpracovat všechny neodkazované Ideas
results = service.process_unreferenced_ideas()
print(f"Vytvořeno Stories pro {len(results)} Ideas")

# Vytvořit Stories pro konkrétní Idea
result = service.create_stories_from_idea(idea_id=1)
if result:
    print(f"Vytvořeno {result.count} Stories")
else:
    print("Idea již má Stories")
```

### Pomocné funkce

```python
from T.Story.From.Idea import (
    create_stories_from_idea,
    get_unreferenced_ideas,
    process_oldest_unreferenced_idea
)

# Zpracovat nejstarší neodkazovanou Idea (hlavní workflow)
result = process_oldest_unreferenced_idea(story_conn, idea_db)

# Získat neodkazované Ideas (seřazené podle stáří)
unreferenced = get_unreferenced_ideas(story_conn, idea_db)

# Vytvořit Stories pro konkrétní Idea
result = create_stories_from_idea(story_conn, idea_db, idea_id=1)
```

## API Reference

### StoryFromIdeaService

Hlavní služba pro vytváření Stories z Ideas.

**Metody:**
- `get_oldest_unreferenced_idea()` - Získá nejstarší Idea bez Story referencí
- `get_unreferenced_ideas()` - Získá všechny Ideas bez Story referencí (seřazené podle stáří)
- `idea_has_stories(idea_id)` - Zkontroluje, zda Idea již má Stories
- `create_stories_from_idea(idea_id, skip_if_exists=True)` - Vytvoří 10 Stories pro Idea
- `process_oldest_unreferenced_idea()` - Zpracuje nejstarší neodkazovanou Idea (hlavní workflow)
- `process_unreferenced_ideas()` - Zpracuje všechny neodkazované Ideas
- `ensure_tables_exist()` - Zajistí existenci Story tabulky

### StoryCreationResult

Výsledek vytváření Stories.

**Atributy:**
- `idea_id: int` - ID zdrojové Idea
- `stories: List[Story]` - Seznam vytvořených Story objektů
- `count: int` - Počet vytvořených Stories

## Struktura modulu

```
T/Story/From/Idea/
├── __init__.py
├── README.md
├── src/
│   ├── __init__.py
│   └── story_from_idea_service.py
└── _meta/
    └── tests/
        ├── __init__.py
        └── test_story_from_idea_service.py
```

## Testy

Spuštění testů:

```bash
pytest T/Story/From/Idea/_meta/tests/ -v
```

## Závislosti

- `T.Database.models.story` - Story model a StoryState enum
- `T.Database.repositories.story_repository` - StoryRepository
- `T.Idea.Model.src.simple_idea` - SimpleIdea model
- `T.Idea.Model.src.simple_idea_db` - SimpleIdeaDatabase
