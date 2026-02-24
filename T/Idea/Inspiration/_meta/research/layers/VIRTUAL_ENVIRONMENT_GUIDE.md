# Virtual Environment Setup Guide

## Strategy: Layer-Specific Virtual Environments

Each major layer/module can have its own virtual environment with isolated dependencies.

## Directory Structure

```
PrismQ.T.Idea.Inspiration/
├── Source/
│   ├── Audio/
│   │   ├── venv/              # Audio-specific dependencies
│   │   ├── requirements.txt
│   │   └── pyproject.toml
│   ├── Video/
│   │   └── YouTube/
│   │       ├── venv/          # Video processing dependencies
│   │       ├── requirements.txt
│   │       └── pyproject.toml
│   └── TaskManager/
│       ├── venv/              # API client dependencies
│       └── pyproject.toml
├── Classification/
│   ├── venv/                  # NLP/ML dependencies
│   └── requirements.txt
├── Model/
│   ├── venv/                  # Minimal dependencies
│   └── requirements.txt
└── Scoring/
    ├── venv/                  # Scoring algorithms
    └── requirements.txt
```

## Why Multiple Virtual Environments?

### Advantages ✅

1. **Dependency Isolation**: Different modules can use different library versions
   - Audio module: `pydub==0.25.1`
   - Video module: `opencv-python==4.8.0`
   - No conflicts!

2. **Faster Development**: Install only what you need
   - Working on Audio? Only install audio dependencies
   - Don't need 5GB of ML libraries for simple changes

3. **Deployment Flexibility**: Deploy modules independently
   - Each module is self-contained
   - Easier Docker containers
   - Microservices-ready

4. **Clearer Dependencies**: Each module's dependencies are explicit
   - Easy to audit
   - Easy to update
   - No hidden transitive dependencies

5. **Testing Isolation**: Test modules independently
   - No interference from other module's dependencies
   - Faster CI/CD pipelines

### Considerations ⚠️

1. **Disk Space**: Multiple venvs use more space
   - Typical venv: 50-500MB
   - 5 modules: 250MB-2.5GB
   - **Solution**: Use `.venv` name and add to `.gitignore`

2. **Setup Time**: Initial setup takes longer
   - **Solution**: Automated setup script (see below)

3. **IDE Configuration**: Need to configure IDE for each venv
   - **Solution**: Modern IDEs (VS Code, PyCharm) handle this well

## Setup Instructions

### Option 1: Automated Setup (Recommended)

Use the setup script:

```bash
# Windows
python setup_all_venvs.py

# Linux/Mac
python3 setup_all_venvs.py
```

### Option 2: Manual Setup

Setup individual module:

```bash
# Navigate to module
cd Source/Audio

# Create virtual environment (Python 3.10 required)
py -3.10 -m venv venv          # Windows
python3.10 -m venv venv         # Linux/Mac

# Activate
venv\Scripts\activate           # Windows
source venv/bin/activate        # Linux/Mac

# Install dependencies
pip install --upgrade pip
pip install -e .

# Deactivate when done
deactivate
```

### Option 3: Using Python Launcher (Windows - Best Practice)

```bash
# Create venv with specific Python version
py -3.10 -m venv venv

# Run module with specific Python
py -3.10 -m pip install -e Source/Audio/

# This allows multiple Python versions coexist
```

## Common Workflows

### Working on Single Module

```bash
# Activate module's venv
cd Source/Audio
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Make changes, run tests
pytest

# Deactivate when done
deactivate
```

### Running Tests Across All Modules

```bash
# Use the test script that activates each venv
python run_all_tests.py
```

### Adding New Dependency

```bash
# Activate module's venv
cd Source/Audio
source venv/bin/activate

# Install new package
pip install new-package

# Update requirements
pip freeze > requirements.txt

# Or update pyproject.toml manually (preferred)
# Then reinstall
pip install -e .

deactivate
```

## IDE Configuration

### VS Code

1. Open workspace/folder
2. Press `Ctrl+Shift+P` → "Python: Select Interpreter"
3. Choose the venv for module you're working on
4. VS Code will auto-detect venvs in subdirectories

Example `.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "Source/Audio/venv/Scripts/python.exe",
    "python.terminal.activateEnvironment": true
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Virtualenv Environment"
4. Point to module's venv directory
5. Can configure multiple interpreters for different modules

## Best Practices

### 1. Always Use Python 3.10

```bash
# Verify Python version before creating venv
python --version
# Should show: Python 3.10.x

# Use py launcher to be explicit (Windows)
py -3.10 --version
```

### 2. Keep Requirements Up to Date

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Update requirements
pip freeze > requirements.txt
```

### 3. Use `pyproject.toml` (Modern Approach)

Prefer `pyproject.toml` over `requirements.txt`:

```toml
[project]
name = "prismq-audio"
version = "0.1.0"
requires-python = ">=3.10,<3.11"
dependencies = [
    "pydantic>=2.0",
    "requests>=2.31",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "black>=23.0",
    "mypy>=1.5",
]
```

### 4. Don't Commit Virtual Environments

Add to `.gitignore`:
```
# Virtual environments
venv/
.venv/
env/
ENV/
```

### 5. Document Module Dependencies

Each module should have clear dependency documentation:

```markdown
# Module: Source/Audio

## Dependencies
- Python 3.10.x
- pydub - Audio processing
- requests - HTTP client
- pydantic - Data validation

## Installation
```bash
pip install -e .
```
```

## Troubleshooting

### Issue: "python not found"

**Solution**: Use `py` launcher (Windows) or `python3` (Linux/Mac)

```bash
# Windows
py -3.10 -m venv venv

# Linux/Mac
python3.10 -m venv venv
```

### Issue: "pip is outdated"

**Solution**: Upgrade pip first

```bash
python -m pip install --upgrade pip
```

### Issue: "Module imports not working"

**Solution**: Install module in editable mode

```bash
pip install -e .
```

### Issue: "Wrong Python version in venv"

**Solution**: Delete venv and recreate with correct version

```bash
# Delete old venv
rm -rf venv  # Linux/Mac
rmdir /s venv  # Windows

# Create with correct version
py -3.10 -m venv venv
```

## Alternative: Monorepo with Single Venv

If multiple venvs are too complex, you can use a single venv:

```bash
# Root level
python -m venv venv
source venv/bin/activate

# Install all modules
pip install -e Source/Audio/
pip install -e Source/Video/YouTube/
pip install -e Classification/
pip install -e Model/
pip install -e Scoring/
```

**Pros**: Simpler setup, one venv to manage  
**Cons**: Potential dependency conflicts, all-or-nothing installs

## Summary

✅ **Recommended**: Multiple venvs for better isolation  
✅ **Python 3.10**: Required for compatibility  
✅ **Use `pyproject.toml`**: Modern dependency management  
✅ **Automate Setup**: Use provided scripts  
✅ **IDE Support**: Configure properly for best experience  

---

**Next Steps**:
1. Run `setup_all_venvs.py` to create all environments
2. Configure your IDE for the module you're working on
3. Read module-specific README for dependencies
4. Start coding!
