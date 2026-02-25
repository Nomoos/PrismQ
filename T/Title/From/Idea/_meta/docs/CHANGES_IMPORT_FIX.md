# Change Summary - Fix IdeaTable Not Available

## Problem

`03_PrismQ.T.Title.From.Idea` failed at startup with:

```
IdeaTable not available - cannot fetch Idea content
```

This happened even though `01_PrismQ.T.Idea.From.User` (Script 01) worked correctly with the same database.

## Root Cause

Two separate issues combined to cause the failure:

### 1. Hard `dotenv` import in `src/config.py`

`src/config.py` imported `python-dotenv` at the module level without a fallback:

```python
# Before — fails if python-dotenv is not installed
from dotenv import load_dotenv, set_key
```

When `python-dotenv` is not yet installed in the virtual environment (e.g. on a fresh `setup_env.bat` run before `requirements.txt` installs finish), this import fails and makes the **entire `src` package unimportable** — including `src.idea.IdeaTable`, which has no dotenv dependency at all.

### 2. Import structure in `title_from_idea_interactive.py` differed from Script 01

The Title script had two **separate** try/except blocks for `IdeaTable` and `Config`, and did not import `setup_idea_table`. Script 01 (`01_PrismQ.T.Idea.From.User`) uses a **single combined block** that imports `Config`, `IdeaTable`, and `setup_idea_table` together.

## Changes Made

### `src/config.py`

Wrapped the `dotenv` import in `try/except ImportError` with no-op fallbacks so `IdeaTable` (and the rest of `src`) remain importable in environments where `python-dotenv` is not installed:

```python
# Before
from dotenv import load_dotenv, set_key

# After
try:
    from dotenv import load_dotenv, set_key
except ImportError:

    def load_dotenv(*args, **kwargs):
        """No-op fallback when python-dotenv is not installed."""
        return False

    def set_key(*args, **kwargs):
        """No-op fallback when python-dotenv is not installed."""
        return (None, None, None)
```

### `T/Title/From/Idea/src/title_from_idea_interactive.py`

Consolidated the two separate import blocks into **one combined block** matching Script 01's pattern exactly, and added `setup_idea_table`:

```python
# Before — two separate blocks, missing setup_idea_table
try:
    from src.idea import IdeaTable
    IDEA_TABLE_AVAILABLE = True
except ImportError:
    IDEA_TABLE_AVAILABLE = False

try:
    from src.config import Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# After — single block, matches 01_PrismQ.T.Idea.From.User exactly
try:
    from src.config import Config
    from src.idea import IdeaTable, setup_idea_table
    IDEA_TABLE_AVAILABLE = True
    CONFIG_AVAILABLE = True
except ImportError:
    IDEA_TABLE_AVAILABLE = False
    CONFIG_AVAILABLE = False
```

Also replaced manual connection setup with `setup_idea_table()`:

```python
# Before
idea_db = IdeaTable(db_path)
idea_db.connect()

# After
idea_db = setup_idea_table(db_path)
```

## Why Script 01 Worked

Script 01 (`T/Idea/From/User/src/idea_creation_interactive.py`) uses the same combined import pattern and `setup_idea_table()`, so it was not affected by either issue.
