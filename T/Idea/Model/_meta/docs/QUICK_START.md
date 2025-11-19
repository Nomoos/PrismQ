# Quick Start Guide

Get started with PrismQ.Idea.Model in 5 minutes.

## Installation

```bash
cd Idea/Model
pip install -e .
```

## Database Setup

**Linux/macOS:**
```bash
./setup_db.sh
```

**Windows (PowerShell):**
```powershell
.\setup_db.ps1
```

**Windows (Command Prompt):**
```cmd
setup_db.bat
```

## Basic Usage

### Create a Standalone Idea

```python
from idea import Idea, ContentGenre, IdeaStatus

idea = Idea(
    title="Python Tutorial Series",
    concept="Teaching Python fundamentals through projects",
    synopsis="A beginner-friendly Python course",
    target_platforms=["youtube", "medium"],
    target_formats=["text", "video"],
    genre=ContentGenre.EDUCATIONAL,
    keywords=["python", "programming", "tutorial"],
    outline="1. Setup\n2. Variables\n3. Functions",
    skeleton="Intro → Theory → Practice → Challenge"
)

print(idea)
```

### Create from IdeaInspiration Sources

```python
# Fuse multiple inspirations into one idea
idea = Idea.from_inspirations(
    inspirations=[insp1, insp2, insp3],
    title="Digital Detective Stories",
    concept="Using tech to solve internet mysteries",
    target_platforms=["youtube", "spotify", "medium"],
    target_formats=["text", "audio", "video"],
    genre=ContentGenre.TRUE_CRIME
)

print(f"Created from {len(idea.inspiration_ids)} inspirations")
```

### Save to Database

```python
from idea_db import IdeaDatabase

db = IdeaDatabase("idea.db")
db.connect()

idea_id = db.insert_idea(idea.to_dict())
print(f"Saved with ID: {idea_id}")

db.close()
```

### Version Management

```python
# Create new version
v2 = idea.create_new_version(
    concept="Enhanced concept",
    status=IdeaStatus.VALIDATED
)

print(f"Version: {v2.version}")  # Version: 2
```

## Next Steps

- **[Field Reference](FIELDS.md)** - Complete field documentation
- **[Database Guide](DATABASE.md)** - Database operations
- **[AI Generation](AI_GENERATION.md)** - Using AI-ready fields
- **[Multi-Format](MULTI_FORMAT.md)** - Universal content generation
- **[Examples](../examples/example_usage.py)** - More code examples
