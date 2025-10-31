# Per-Project Virtual Environments

**Issue**: #115  
**Strategy**: Per-Project Isolation (Full Isolation)  
**Status**: ✅ Implemented  
**Date**: 2025-10-31

---

## Overview

PrismQ.IdeaInspiration uses **per-project virtual environments** for full isolation. Each project (Classification, ConfigLoad, Model, Scoring, Sources, Client/Backend) has its own independent Python virtual environment.

This approach was chosen in [Issue #113](../issues/done/113-venv-strategy-decision.md) because:
- Each project will have AI dependencies with different framework versions
- Projects need to evolve independently without version conflicts
- Disk space and switching overhead are acceptable trade-offs for isolation
- Aligns with production best practices

---

## Quick Start

### Initial Setup

**Linux/macOS/WSL:**
```bash
# Create all virtual environments
./_meta/_scripts/setup_all_envs.sh

# Activate a specific project
cd Classification
source venv/bin/activate

# Or use the helper
source _meta/_scripts/activate_env.sh Classification
```

**Windows PowerShell:**
```powershell
# Create all virtual environments
.\_meta\_scripts\setup_all_envs.ps1

# Activate a specific project
cd Classification
.\venv\Scripts\Activate.ps1

# Or use the helper
. _meta\_scripts\activate_env.ps1 Classification
```

---

## Directory Structure

```
PrismQ.IdeaInspiration/
├── _meta/
│   └── _scripts/
│       ├── setup_all_envs.sh        # Create all environments (bash)
│       ├── setup_all_envs.ps1       # Create all environments (PowerShell)
│       ├── update_all_envs.sh       # Update all environments (bash)
│       ├── update_all_envs.ps1      # Update all environments (PowerShell)
│       ├── clean_all_envs.sh        # Remove all environments (bash)
│       ├── clean_all_envs.ps1       # Remove all environments (PowerShell)
│       ├── activate_env.sh          # Helper activation (bash)
│       └── activate_env.ps1         # Helper activation (PowerShell)
├── Classification/
│   ├── venv/                        # Classification environment
│   └── requirements.txt
├── ConfigLoad/
│   ├── venv/                        # ConfigLoad environment
│   └── requirements.txt
├── Model/
│   ├── venv/                        # Model environment
│   └── requirements.txt
├── Scoring/
│   ├── venv/                        # Scoring environment
│   └── requirements.txt
├── Sources/
│   ├── venv/                        # Sources environment
│   └── requirements.txt
└── Client/Backend/
    ├── venv/                        # Client/Backend environment
    └── requirements.txt
```

---

## Management Scripts

### setup_all_envs

Creates virtual environments for all projects.

**Features:**
- Creates `venv/` in each project directory
- Upgrades pip, setuptools, and wheel
- Installs dependencies from `requirements.txt`
- Skips if venv already exists (idempotent)

**Usage:**
```bash
# Linux/macOS/WSL
./_meta/_scripts/setup_all_envs.sh

# Windows PowerShell
.\_meta\_scripts\setup_all_envs.ps1
```

### update_all_envs

Updates all virtual environments with latest dependencies.

**Features:**
- Upgrades pip in each environment
- Upgrades all packages from `requirements.txt`
- Reports failures for troubleshooting

**Usage:**
```bash
# Linux/macOS/WSL
./_meta/_scripts/update_all_envs.sh

# Windows PowerShell
.\_meta\_scripts\update_all_envs.ps1
```

### clean_all_envs

Removes all virtual environments (with confirmation).

**Features:**
- Deletes all `venv/` directories
- Prompts for confirmation before deletion
- Useful for starting fresh

**Usage:**
```bash
# Linux/macOS/WSL
./_meta/_scripts/clean_all_envs.sh

# Windows PowerShell
.\_meta\_scripts\clean_all_envs.ps1
```

### activate_env

Helper script to activate a specific project's environment.

**Usage:**
```bash
# Linux/macOS/WSL
source _meta/_scripts/activate_env.sh <project-name>
source _meta/_scripts/activate_env.sh Classification

# Windows PowerShell
. _meta\_scripts\activate_env.ps1 <project-name>
. _meta\_scripts\activate_env.ps1 Classification
```

**Available projects:**
- Classification
- ConfigLoad
- Model
- Scoring
- Sources
- Client/Backend

---

## Daily Workflows

### Working on a Single Project

```bash
# Navigate to project
cd Classification

# Activate environment
source venv/bin/activate  # Linux/macOS/WSL
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Work on code...
# Run tests...
# Install new packages...

# Deactivate when done
deactivate
```

### Switching Between Projects

```bash
# Method 1: Manual activation
cd Scoring
source venv/bin/activate
# ... work ...
deactivate

cd Classification
source venv/bin/activate
# ... work ...

# Method 2: Using helper script
source _meta/_scripts/activate_env.sh Scoring
# ... work ...
deactivate

source _meta/_scripts/activate_env.sh Classification
# ... work ...
```

### Adding New Dependencies

```bash
# Activate project environment
cd Classification
source venv/bin/activate

# Install new package
pip install transformers

# Update requirements.txt
pip freeze > requirements.txt

# Or manually edit requirements.txt (recommended)
echo "transformers>=4.30.0" >> requirements.txt

# Deactivate
deactivate
```

---

## IDE Integration

### VS Code

Create a **multi-root workspace** for the monorepo:

1. Open VS Code
2. File → Add Folder to Workspace → Select each project folder
3. File → Save Workspace As... → `PrismQ.code-workspace`

**Workspace settings** (`.vscode/settings.json` in each project):

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.testing.pytestEnabled": true
}
```

**Selecting interpreter per project:**
1. Open a file in the project
2. Ctrl+Shift+P → "Python: Select Interpreter"
3. Choose `./venv/bin/python`

### PyCharm

PyCharm has excellent multi-module support:

1. Open `PrismQ.IdeaInspiration` as the root directory
2. For each project:
   - File → Settings → Project → Project Interpreter
   - Click gear icon → Add → Existing Environment
   - Select `<project>/venv/bin/python`
3. Mark each project's `src/` as "Sources Root" (right-click → Mark Directory As)

---

## Automatic Environment Activation with direnv

### Overview

[direnv](https://direnv.net/) automatically loads/unloads environments based on directory. All PrismQ projects now include `.envrc` files for automatic activation.

**✨ Benefits:**
- Activates virtual environment automatically on `cd`
- Deactivates automatically when leaving
- Loads project-specific `.env` variables
- Eliminates manual `source venv/bin/activate`

### Quick Setup

```bash
# 1. Install direnv
sudo apt install direnv  # Ubuntu/Debian
brew install direnv      # macOS

# 2. Configure shell (~/.bashrc or ~/.zshrc)
eval "$(direnv hook bash)"

# 3. Reload shell
source ~/.bashrc

# 4. Allow each project (one-time)
cd Classification
direnv allow
```

### Daily Usage

```bash
cd Classification
# ✅ Activated Classification environment (automatic!)

cd ../Scoring  
# ✅ Activated Scoring environment (automatic!)

cd ..
# Environment deactivated (automatic!)
```

**📚 For detailed setup instructions, troubleshooting, and advanced usage, see:**
**[direnv Setup Guide](./DIRENV_SETUP.md)**

### .envrc Files

Each project has a `.envrc` that:
- Activates project's `venv/`
- Loads `.env` file (if it exists)
- Sets `PROJECT_NAME` and `PYTHONPATH`

Example:
```bash
# Classification/.envrc
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

if [ -f ".env" ]; then
    dotenv
fi

export PROJECT_NAME="Classification"
export PYTHONPATH="$(pwd):$PYTHONPATH"
```

**Enable:**
```bash
cd Classification
direnv allow  # One-time, grants permission
```

### Using .env Files

Each project includes a `.env.example` template:

```bash
# Copy and customize
cp .env.example .env
# Edit .env with your values
```

Environment variables from `.env` are automatically loaded by direnv.

**📚 Complete guide:** [DIRENV_SETUP.md](./DIRENV_SETUP.md)

---

## Troubleshooting

### "venv not found" errors

**Problem:** Virtual environment doesn't exist.

**Solution:**
```bash
# Create all environments
./_meta/_scripts/setup_all_envs.sh

# Or create for one project
cd Classification
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Dependency conflicts between projects

**Problem:** Project A needs `package==1.0` but Project B needs `package==2.0`.

**Solution:** This is normal! That's why we use per-project environments. Each project can have different versions. Make sure you're activating the correct environment.

### Disk space concerns

**Expected usage:**
- Lightweight projects (Classification, Model, ConfigLoad, Sources): ~180-250MB each
- Medium projects (Scoring): ~500MB - 2GB (depends on AI dependencies)
- Heavy projects (Client/Backend): ~500MB - 1GB

**Total: ~2-6GB for all 6 environments**

**To reclaim space:**
```bash
# Remove unused environments
./_meta/_scripts/clean_all_envs.sh

# Recreate only what you need
cd Classification
python3 -m venv venv
```

### Slow environment creation

**Problem:** Creating environments takes too long.

**Optimizations:**
- Pip uses a wheel cache (reuses downloads across environments)
- First setup is slowest; subsequent setups are faster
- Consider using `pip install --no-cache-dir` if you have bandwidth but limited disk

### Wrong environment activated

**Problem:** Installed packages in wrong environment.

**Solution:**
```bash
# Check which environment is active
which python  # Linux/macOS
where python  # Windows

# Should show: /path/to/PrismQ.IdeaInspiration/<project>/venv/bin/python

# If wrong, deactivate and activate correct one
deactivate
cd <correct-project>
source venv/bin/activate
```

---

## Best Practices

### 1. Always Activate Before Installing

```bash
# ✅ Correct
cd Classification
source venv/bin/activate
pip install new-package

# ❌ Wrong (installs to system/wrong environment)
cd Classification
pip install new-package
```

### 2. Use requirements.txt

```bash
# ✅ Correct: Maintain requirements.txt manually
# requirements.txt
pytest>=7.0.0
transformers>=4.30.0,<5.0.0

# ❌ Avoid: Using pip freeze (includes transitive dependencies)
pip freeze > requirements.txt  # Creates bloated file
```

### 3. Keep Environments Clean

```bash
# Periodically recreate environments to remove unused packages
./_meta/_scripts/clean_all_envs.sh
./_meta/_scripts/setup_all_envs.sh
```

### 4. Document Project-Specific Dependencies

Add comments to `requirements.txt`:

```txt
# Core dependencies
python-dotenv>=1.0.0

# AI/ML dependencies (GPU-accelerated for RTX 5090)
torch>=2.0.0  # CUDA 12.1 compatible
transformers>=4.30.0  # For BERT models

# Development dependencies
pytest>=7.0.0
black>=23.0.0
```

---

## Migration from Other Strategies

### From Shared Environment

If you were using a single monorepo-wide environment:

```bash
# 1. Deactivate current environment
deactivate

# 2. Create per-project environments
./_meta/_scripts/setup_all_envs.sh

# 3. Verify each project's requirements.txt is accurate

# 4. Remove old shared environment (optional)
rm -rf venv/  # At repository root
```

### From No Environment

If you were using system Python:

```bash
# 1. Create all environments
./_meta/_scripts/setup_all_envs.sh

# 2. For each project, create requirements.txt with current dependencies
cd Classification
source venv/bin/activate
pip list --format=freeze > requirements.txt

# 3. Review and clean up requirements.txt (remove unnecessary packages)
```

---

## Advantages

✅ **Full Isolation**: Projects can use different package versions  
✅ **Clean Dependencies**: Each env only has what that project needs  
✅ **Independent Updates**: Upgrade one project without affecting others  
✅ **Conflict-Free**: No version conflicts between projects  
✅ **Flexibility**: Easy to add projects with unique requirements  
✅ **AI-Ready**: Each project can use different AI frameworks/versions  
✅ **Production-Like**: Mimics deployment isolation

---

## Known Limitations

⚠️ **Disk Space**: ~2-6GB total (acceptable per user constraints)  
⚠️ **Setup Time**: 5-10 minutes to create all environments  
⚠️ **Manual Switching**: Must remember to activate correct environment (mitigated by direnv)  
⚠️ **Duplication**: Common packages installed multiple times (acceptable trade-off)

---

## Success Metrics

- **Disk Space**: < 6GB for all 6 environments ✅
- **Setup Time**: < 10 minutes for all environments ✅
- **Isolation**: Zero cross-contamination between environments ✅
- **Developer Satisfaction**: Easy to work with after initial setup ✅

---

## Related Documentation

- [Issue #113: Virtual Environment Strategy Decision](../issues/done/113-venv-strategy-decision.md)
- [Issue #115: Implementation Plan](../issues/new/Infrastructure_DevOps/115-implement-per-project-venv.md)
- [SOLID Principles](./SOLID_PRINCIPLES.md)
- [Contributing Guide](./CONTRIBUTING.md)

---

## Support

If you encounter issues not covered here:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Review [Issue #115](../issues/new/Infrastructure_DevOps/115-implement-per-project-venv.md)
3. Open a new issue with the `infrastructure` label
