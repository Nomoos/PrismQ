# Scripts

Utility scripts for PrismQ.IdeaInspiration.Classification.

## Why PowerShell?

For Windows users, **PowerShell scripts (.ps1) are recommended** over batch scripts (.bat) because:

1. **Better Error Handling**: PowerShell provides structured error handling with try/catch blocks
2. **Colored Output**: Enhanced readability with color-coded status messages
3. **Modern Windows Standard**: PowerShell is the modern scripting standard for Windows
4. **AI Assistant Friendly**: Better structured syntax for GitHub Copilot and ChatGPT to understand and modify
5. **More Powerful**: Advanced features like object manipulation and better string handling

### Enabling PowerShell Scripts

If you get an error about script execution being disabled, run this once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

This allows locally created scripts to run while still protecting against untrusted remote scripts.

## Available Scripts

### setup.ps1 / setup.bat / setup.sh

Sets up the development environment:
- Creates virtual environment
- Installs dependencies
- Installs package in editable mode
- Runs initial tests

**Windows (PowerShell - Recommended):**
```powershell
.\scripts\setup.ps1
```

**Windows (Batch - Legacy):**
```batch
scripts\setup.bat
```

**Linux/Mac (development only):**
```bash
bash scripts/setup.sh
```

### quickstart.ps1 / quickstart.bat / quickstart.sh

Quick start script to run the example:
- Activates virtual environment
- Runs example.py demonstration

**Windows (PowerShell - Recommended):**
```powershell
.\scripts\quickstart.ps1
```

**Windows (Batch - Legacy):**
```batch
scripts\quickstart.bat
```

**Linux/Mac (development only):**
```bash
bash scripts/quickstart.sh
```

### test.ps1 / test.bat / test.sh

Runs the test suite:
- Activates virtual environment
- Runs pytest with coverage

**Windows (PowerShell - Recommended):**
```powershell
.\scripts\test.ps1
```

**Windows (Batch - Legacy):**
```batch
scripts\test.bat
```

**Linux/Mac (development only):**
```bash
bash scripts/test.sh
```

### docs.ps1 / docs.bat

Builds documentation with Sphinx:
- Activates virtual environment
- Installs Sphinx if needed
- Builds HTML documentation

**Windows (PowerShell - Recommended):**
```powershell
.\scripts\docs.ps1
```

**Windows (Batch - Legacy):**
```batch
scripts\docs.bat
```

### lint.ps1 / lint.bat

Runs code quality checks:
- Activates virtual environment
- Runs Flake8 (PEP 8 linting)
- Runs MyPy (type checking)

**Windows (PowerShell - Recommended):**
```powershell
.\scripts\lint.ps1
```

**Windows (Batch - Legacy):**
```batch
scripts\lint.bat
```

### format.ps1 / format.bat

Formats code with Black:
- Activates virtual environment
- Runs Black code formatter (PEP 8)

**Windows (PowerShell - Recommended):**
```powershell
.\scripts\format.ps1
```

**Windows (Batch - Legacy):**
```batch
scripts\format.bat
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
