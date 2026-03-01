# Workflow Script Pattern

**Canonical pattern for all continuous workflow runner scripts in `T/*/src/`**

Every workflow Python script that processes Story objects from the database must follow this pattern exactly. The sections below explain each part and why it is required.

---

## 1. Path Setup

```python
SCRIPT_DIR = Path(__file__).parent.absolute()   # .../T/<Module>/src
MODULE_ROOT = SCRIPT_DIR.parent                 # .../T/<Module>
# Adjust the number of .parent calls below to reach T/ from MODULE_ROOT.
# Example for T/Review/Title/From/Idea/Content (5 levels deep):
#   T_ROOT = MODULE_ROOT.parent.parent.parent.parent.parent
# Example for T/Content/From/Idea/Title (4 levels deep):
#   T_ROOT = MODULE_ROOT.parent.parent.parent.parent
T_ROOT = MODULE_ROOT.parent.parent...           # .../T  (adjust depth)
REPO_ROOT = T_ROOT.parent                       # repo root

sys.path.insert(0, str(SCRIPT_DIR))             # local service/helper imports
sys.path.insert(0, str(REPO_ROOT))              # REPO_ROOT/src/ (Config, shared tables)
```

Both `SCRIPT_DIR` **and** `REPO_ROOT` must be inserted before any imports. The number of `.parent` hops to reach `T_ROOT` varies with the module depth—add a comment showing the resolved path so it is easy to verify.

---

## 2. Config Import (must come first)

```python
# Import Config before service (service modifies sys.path and may shadow REPO_ROOT/src)
try:
    from src.config import Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
```

> **Why first?**  
> Service files (e.g. `*_service.py`) insert `T/` at `sys.path[0]` during import. This makes Python find `T/src/` (the T foundation package, which has no `config.py`) before `REPO_ROOT/src/`. Importing `Config` before the service ensures the correct module is found while `REPO_ROOT/src/` is still unobscured.

---

## 3. Service Import (after Config)

```python
try:
    from <module_name>_service import <ServiceClass>
    # Concrete example: from review_title_service import ReviewTitleService
    SERVICE_AVAILABLE = True
except ImportError as e:
    SERVICE_AVAILABLE = False
    IMPORT_ERROR = str(e)
```

Keep the two `try/except` blocks **separate**. Never merge Config and the service into one block.

---

## 4. Database Path in `main()`

```python
def main() -> int:
    ...
    db_path = "C:/PrismQ/db.s3db"  # fallback default
    if CONFIG_AVAILABLE:
        try:
            config = Config()
            db_path = config.database_path
        except Exception:
            pass

    print_info(f"Database: {db_path}")

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        print_success("Connected to database")
    except Exception as e:
        print_error(f"Failed to connect to database: {e}")
        return 1
```

Use `Config().database_path` (instance attribute). `Config.get_database_path()` does not exist.

---

## 5. Environment Setup (venv)

Each module manages its own virtual environment. Environment setup is **individual** per module but follows the same tooling:

- **Windows**: `_meta/scripts/Run.bat` calls the shared helper  
  `<REPO_ROOT>/_meta/scripts/common/setup_env.bat "<MODULE_DIR>"`
- **Linux/macOS**: `_meta/scripts/setup_env.sh` (source it to activate)

The shared `setup_env.bat` / `setup_env.sh`:
- Creates `.venv/` inside the module directory if it does not exist
- Installs dependencies from `requirements.txt` when changed
- Activates the virtual environment before running the workflow script

The workflow Python script itself does **not** handle venv activation — that is the responsibility of the launcher script.

---

## Quick Checklist for New Scripts

- [ ] `sys.path.insert(0, str(SCRIPT_DIR))` — local imports
- [ ] `sys.path.insert(0, str(REPO_ROOT))` — shared `src/`
- [ ] `Config` imported in its **own** `try/except` **before** the service import
- [ ] `CONFIG_AVAILABLE` flag set
- [ ] Service imported in a **separate** `try/except` after Config
- [ ] `SERVICE_AVAILABLE` and `IMPORT_ERROR` flags set
- [ ] `db_path` resolved via `Config().database_path` inside `main()`, with fallback
- [ ] Launcher script (`Run.bat` / `setup_env.sh`) calls common `setup_env` helper

---

## Example: Minimal Script Skeleton

```python
#!/usr/bin/env python3
"""Continuous Workflow Runner for PrismQ.T.<Module>

Usage:
    python <module>_workflow.py           # Run continuously
    python <module>_workflow.py --preview # Preview mode (no DB save)

Press Ctrl+C to stop.
"""

import logging
import sqlite3
import sys
import time
from pathlib import Path
from typing import Optional

# Setup paths
SCRIPT_DIR = Path(__file__).parent.absolute()   # .../T/<Module>/src
MODULE_ROOT = SCRIPT_DIR.parent                 # .../T/<Module>
# Adjust the number of .parent calls to reach T/ from MODULE_ROOT.
# Example for T/Review/Title/From/Idea/Content (5 levels deep):
#   T_ROOT = MODULE_ROOT.parent.parent.parent.parent.parent
T_ROOT = MODULE_ROOT.parent.parent              # .../T  (adjust depth)
REPO_ROOT = T_ROOT.parent                       # repo root

sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(REPO_ROOT))

# Import Config before service (service modifies sys.path and may shadow REPO_ROOT/src)
try:
    from src.config import Config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from <module>_service import <ServiceClass>
    # Concrete example: from review_title_service import ReviewTitleService
    SERVICE_AVAILABLE = True
except ImportError as e:
    SERVICE_AVAILABLE = False
    IMPORT_ERROR = str(e)


def main() -> int:
    if not SERVICE_AVAILABLE:
        print(f"✗ Service module not available: {IMPORT_ERROR}")
        return 1

    db_path = "C:/PrismQ/db.s3db"
    if CONFIG_AVAILABLE:
        try:
            config = Config()
            db_path = config.database_path
        except Exception:
            pass

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        return 1

    # ... processing loop ...

    return 0


if __name__ == "__main__":
    sys.exit(main())
```
