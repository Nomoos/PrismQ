# Issue #118: Implement direnv for Automatic Environment Activation

**Type**: Enhancement  
**Priority**: Medium  
**Status**: New  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 3-5 days  
**Dependencies**: One of #114, #115, #116, or #117 (whichever venv strategy is chosen)  
**Related Issues**: #113, #114, #115, #116, #117

---

## Description

Implement direnv to automatically activate the correct virtual environment when entering a project directory, and deactivate it when leaving. This dramatically improves developer experience by eliminating manual environment activation.

## Problem Statement

Without automation, developers must:
1. Remember which environment to activate for each project
2. Manually activate with `source venv/bin/activate`
3. Manually deactivate when switching projects
4. Risk running code in the wrong environment

This leads to errors, frustration, and wasted time.

## Solution: direnv

[direnv](https://direnv.net/) is a shell extension that loads/unloads environment variables based on the current directory. It can:
- Auto-activate virtual environments when entering directories
- Auto-deactivate when leaving directories
- Load project-specific .env files
- Set project-specific environment variables

## Implementation Overview

Set up direnv for all PrismQ.IdeaInspiration projects, adapting the configuration based on the chosen virtual environment strategy (#113).

## Architecture (varies by strategy)

### For Per-Project Strategy (#115)
```
Classification/
├── venv/
├── .envrc          # Activates ./venv
└── .env            # Project variables (optional)

ConfigLoad/
├── venv/
├── .envrc          # Activates ./venv
└── .env
```

### For Grouped Strategy (#116)
```
Classification/
├── .envrc          # Activates ../.venv-core
└── .env

Scoring/
├── .envrc          # Activates ../.venv-ml
└── .env

Client/Backend/
├── .envrc          # Activates ../.venv-web
└── .env
```

### For Shared Strategy (#114)
```
.envrc              # At repo root, activates ./.venv
Classification/
└── .env            # Optional project-specific vars
```

## Tasks

### direnv Installation
- [ ] Create installation guide for Windows
  - Git Bash compatibility
  - PowerShell compatibility
  - WSL compatibility
- [ ] Create installation guide for Linux/macOS
- [ ] Document shell configuration (bash, zsh, fish)
- [ ] Test on target platform (Windows)

### .envrc Template Creation
- [ ] Create .envrc template for per-project strategy
- [ ] Create .envrc template for grouped strategy
- [ ] Create .envrc template for shared strategy
- [ ] Create .envrc template for layered strategy
- [ ] Include .env file loading in templates
- [ ] Add helpful comments to templates

### .envrc Deployment
- [ ] Generate .envrc for each project based on strategy
- [ ] Test auto-activation in each project
- [ ] Test auto-deactivation when leaving
- [ ] Verify nested directory behavior
- [ ] Test rapid directory switching

### .env File Support
- [ ] Create .env.example for each project
- [ ] Document environment variables per project
- [ ] Ensure .env is gitignored
- [ ] Test .env loading with direnv

### Security
- [ ] Document .envrc security model
- [ ] Explain `direnv allow` requirement
- [ ] Create .envrc whitelist/review process
- [ ] Add security warnings to documentation

### IDE Integration
- [ ] Test VS Code with direnv extension
- [ ] Document PyCharm direnv integration
- [ ] Test GitHub Copilot with direnv
- [ ] Verify language servers see activated environment

### Windows-Specific Work
- [ ] Test direnv with Git Bash
- [ ] Test direnv with WSL
- [ ] Test direnv with PowerShell (if supported)
- [ ] Document Windows-specific setup steps
- [ ] Create fallback for unsupported shells

### Documentation
- [ ] Create `_meta/docs/DIRENV_SETUP.md`
  - Installation instructions (OS-specific)
  - Shell configuration
  - How .envrc works
  - Security best practices
  - Troubleshooting
- [ ] Create quick start guide
- [ ] Add to main README.md
- [ ] Create video tutorial (optional)

## .envrc Templates

### Template 1: Per-Project Environment
```bash
# .envrc for projects with local venv/
# Auto-activates virtual environment when entering directory

# Activate local venv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    # Windows Git Bash
    source venv/Scripts/activate
else
    echo "⚠️  Virtual environment not found. Run setup script."
fi

# Load project environment variables
if [ -f ".env" ]; then
    dotenv
fi

# Set project-specific variables
export PROJECT_NAME="Classification"  # Update per project
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo "✅ Activated $PROJECT_NAME environment"
```

### Template 2: Grouped Environment
```bash
# .envrc for projects using grouped environments
# Auto-activates the appropriate group environment

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo ..)"

# Determine which group environment to use
GROUP_ENV="core"  # Options: core, ml, web

if [ -f "$REPO_ROOT/.venv-$GROUP_ENV/bin/activate" ]; then
    source "$REPO_ROOT/.venv-$GROUP_ENV/bin/activate"
elif [ -f "$REPO_ROOT/.venv-$GROUP_ENV/Scripts/activate" ]; then
    # Windows Git Bash
    source "$REPO_ROOT/.venv-$GROUP_ENV/Scripts/activate"
else
    echo "⚠️  Group environment not found: .venv-$GROUP_ENV"
    echo "Run: _meta/_scripts/setup_grouped_envs.sh"
fi

# Load project environment variables
if [ -f ".env" ]; then
    dotenv
fi

# Set project-specific variables
export PROJECT_GROUP="$GROUP_ENV"
export PROJECT_NAME="Classification"  # Update per project
export PYTHONPATH="$(pwd):$PYTHONPATH"

echo "✅ Activated $PROJECT_NAME ($GROUP_ENV environment)"
```

### Template 3: Shared Environment (repo root)
```bash
# .envrc for shared environment (place at repo root)
# Auto-activates when entering any project in the monorepo

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    # Windows Git Bash
    source .venv/Scripts/activate
else
    echo "⚠️  Shared virtual environment not found"
    echo "Run: _meta/_scripts/create_shared_env.sh"
fi

echo "✅ Activated PrismQ.IdeaInspiration shared environment"
```

## .env.example Templates

### Classification/.env.example
```bash
# Classification Module Environment Variables

# Logging
LOG_LEVEL=INFO
LOG_FILE=classification.log

# Model paths (if local models are used)
# MODEL_PATH=/path/to/model

# Development
PYTHONPATH=.
DEBUG=false
```

### Scoring/.env.example
```bash
# Scoring Module Environment Variables

# API Keys (for future integrations)
# OPENAI_API_KEY=your_key_here

# GPU Settings
CUDA_VISIBLE_DEVICES=0
TORCH_HOME=/path/to/torch/cache

# Logging
LOG_LEVEL=INFO
LOG_FILE=scoring.log

# Development
PYTHONPATH=.
DEBUG=false
```

## Installation Guide Outline

### Windows Installation
```bash
# Using Scoop (recommended)
scoop install direnv

# Or using Chocolatey
choco install direnv

# Configure for Git Bash (~/.bashrc)
eval "$(direnv hook bash)"

# Configure for PowerShell (if supported)
# May require workarounds or alternatives
```

### Linux/macOS Installation
```bash
# Ubuntu/Debian
sudo apt install direnv

# macOS
brew install direnv

# Configure for Bash (~/.bashrc)
eval "$(direnv hook bash)"

# Configure for Zsh (~/.zshrc)
eval "$(direnv hook zsh)"
```

## Usage Workflow

1. **Initial Setup**:
   ```bash
   cd PrismQ.IdeaInspiration
   # .envrc files already created by setup scripts
   
   # Allow each .envrc (one-time per project)
   cd Classification
   direnv allow
   
   cd ../ConfigLoad
   direnv allow
   # Repeat for all projects
   ```

2. **Daily Usage**:
   ```bash
   cd PrismQ.IdeaInspiration/Classification
   # ✅ Activated Classification environment
   # (happens automatically!)
   
   python classify.py  # Uses Classification venv
   
   cd ../Scoring
   # ✅ Activated Scoring environment
   # (automatically switched!)
   
   python score.py  # Uses Scoring venv
   ```

## Acceptance Criteria

- [ ] direnv installed and configured on development machine
- [ ] .envrc files created for all projects
- [ ] Auto-activation works when entering directories
- [ ] Auto-deactivation works when leaving directories
- [ ] .env files loaded correctly
- [ ] Works on Windows (Git Bash/WSL)
- [ ] Works with VS Code
- [ ] GitHub Copilot sees activated environment
- [ ] Documentation complete and tested
- [ ] Security best practices documented

## Benefits

1. **Zero Manual Activation**: Never type `source venv/bin/activate` again
2. **Automatic Deactivation**: Environment cleaned up when leaving
3. **Correct Context**: Always in the right environment for the project
4. **Reduced Errors**: Can't accidentally run code in wrong environment
5. **Environment Variables**: Automatic .env loading
6. **IDE Integration**: Tools always use correct interpreter

## Challenges on Windows

- **Git Bash**: Generally works well
- **WSL**: Works natively like Linux
- **PowerShell**: Limited support, may need workarounds
- **CMD**: Not supported

**Recommended**: Use Git Bash or WSL on Windows for best experience

## Success Metrics

- **Manual Activations**: 0 (down from 10-20 per day)
- **Wrong Environment Errors**: 0 (down from occasional)
- **Setup Time**: < 30 minutes for all projects
- **Developer Satisfaction**: High (automatic > manual)

## References

- [direnv official site](https://direnv.net/)
- [direnv GitHub](https://github.com/direnv/direnv)
- [Hynek Schlawack's direnv guide](https://hynek.me/articles/python-virtualenv-redux/)
- [direnv for Python projects](https://direnv.net/man/direnv-stdlib.1.html)

---

**Note**: Implement after #113 decision and the chosen venv strategy (#114, #115, #116, or #117) is complete
