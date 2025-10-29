# Scripts

Utility scripts for PrismQ.IdeaInspiration.Classification.

## Available Scripts

### setup.bat / setup.sh

Sets up the development environment:
- Creates virtual environment
- Installs dependencies
- Installs package in editable mode
- Runs initial tests

**Windows:**
```batch
scripts\setup.bat
```

**Linux/Mac (development only):**
```bash
bash scripts/setup.sh
```

### quickstart.bat / quickstart.sh

Quick start script to run the example:
- Activates virtual environment
- Runs example.py demonstration

**Windows:**
```batch
scripts\quickstart.bat
```

**Linux/Mac (development only):**
```bash
bash scripts/quickstart.sh
```

### test.bat / test.sh

Runs the test suite:
- Activates virtual environment
- Runs pytest with coverage

**Windows:**
```batch
scripts\test.bat
```

**Linux/Mac (development only):**
```bash
bash scripts/test.sh
```

## Manual Setup

If you prefer to set up manually:

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install package with dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run example
python example.py
```

## Platform Notes

- **Windows**: Primary platform, all scripts fully supported
- **Linux/Mac**: Limited support for development purposes only
- Scripts require Python 3.8 or higher
