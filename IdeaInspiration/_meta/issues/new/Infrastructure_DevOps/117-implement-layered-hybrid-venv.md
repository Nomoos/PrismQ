# Issue #117: Implement Hybrid Layered Virtual Environment Strategy

**Type**: Implementation  
**Priority**: Medium  
**Status**: New  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 2-3 weeks  
**Dependencies**: #113 (if this strategy is chosen)  
**Related Issues**: #113, #114, #115, #116

---

## Description

Implement a hybrid layered virtual environment strategy using pip-tools to share a common base of development dependencies while allowing project-specific runtime dependencies. This is the most complex but potentially most efficient approach.

This issue should be implemented if Strategy 4 (Layered Hybrid) is chosen in #113.

## Implementation Overview

Use pip-tools to create a layered dependency system:
- **Base layer**: Common development tools (pytest, black, mypy, ruff)
- **Project layers**: Project-specific runtime dependencies
- Each project has its own venv but shares versions for common packages

## Architecture

```
PrismQ.IdeaInspiration/
├── _meta/
│   ├── requirements/
│   │   ├── base.in                    # Base dev dependencies (input)
│   │   ├── base.txt                   # Compiled base (locked)
│   │   ├── classification.in          # Classification specific
│   │   ├── classification.txt         # Compiled (with base)
│   │   ├── configload.in              # ConfigLoad specific
│   │   ├── configload.txt
│   │   ├── model.in
│   │   ├── model.txt
│   │   ├── scoring.in                 # Scoring specific
│   │   ├── scoring.txt
│   │   ├── sources.in
│   │   ├── sources.txt
│   │   ├── web.in                     # Web specific
│   │   └── web.txt
│   └── _scripts/
│       ├── compile_requirements.sh    # pip-compile all .in files
│       ├── setup_layered_envs.sh      # Create all venvs
│       ├── update_layered_envs.sh     # Update all venvs
│       └── sync_requirements.sh       # pip-sync to match compiled
├── Classification/
│   ├── venv/                          # Has base + classification deps
│   └── .envrc
├── ConfigLoad/
│   ├── venv/                          # Has base + configload deps
│   └── .envrc
├── Model/
│   ├── venv/                          # Has base + model deps
│   └── .envrc
├── Scoring/
│   ├── venv/                          # Has base + scoring deps
│   └── .envrc
├── Sources/
│   ├── venv/                          # Has base + sources deps
│   └── .envrc
└── Client/Backend/
    ├── venv/                          # Has base + web deps
    └── .envrc
```

## Dependency Layer Design

### Base Layer (base.in)
```
# Common development dependencies across all projects
# These will be installed in every project's venv

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.1  # For async tests

# Code Quality
black>=23.0.0
ruff>=0.1.0
mypy>=1.0.0
flake8>=6.0.0

# Common utilities
python-dotenv>=1.0.0
```

### Project Layers (example: classification.in)
```
# Classification-specific dependencies
-c base.txt  # Constrain to base versions

# No additional runtime dependencies
# Classification uses only stdlib
```

### Project Layers (example: scoring.in)
```
# Scoring-specific dependencies
-c base.txt  # Constrain to base versions

# Current runtime dependencies
# (ML deps commented for future)

# Future ML dependencies
# torch>=2.0.0
# transformers>=4.30.0
# sentence-transformers>=2.2.0
# numpy>=1.24.0
```

### Project Layers (example: web.in)
```
# Web Client Backend dependencies
-c base.txt  # Constrain to base versions

# Web framework
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Utilities
aiofiles>=23.2.1
sse-starlette>=2.0.0
httpx>=0.26.0
```

## Tasks

### pip-tools Setup
- [ ] Install pip-tools in base environment or globally
- [ ] Document pip-tools workflow
- [ ] Create Makefile for common pip-tools commands (optional)

### Requirements File Creation
- [ ] Create `_meta/requirements/base.in`
  - Common dev dependencies
  - Testing tools
  - Code quality tools
  - Shared utilities
- [ ] Create `_meta/requirements/classification.in`
- [ ] Create `_meta/requirements/configload.in`
- [ ] Create `_meta/requirements/model.in`
- [ ] Create `_meta/requirements/scoring.in`
- [ ] Create `_meta/requirements/sources.in`
- [ ] Create `_meta/requirements/web.in`

### Compilation Scripts
- [ ] Create `_meta/_scripts/compile_requirements.sh`
  - Run `pip-compile base.in`
  - Run `pip-compile` for each project .in file
  - Use --upgrade flag when requested
  - Generate .txt lock files
- [ ] Create PowerShell version for Windows
- [ ] Test compilation generates correct constraints

### Environment Setup Scripts
- [ ] Create `_meta/_scripts/setup_layered_envs.sh`
  - Create venv for each project
  - Install from compiled .txt files
  - Verify base deps are same version across all
- [ ] Handle errors and conflicts
- [ ] Report successful creation

### Synchronization Scripts
- [ ] Create `_meta/_scripts/sync_requirements.sh`
  - Use pip-sync to match compiled requirements exactly
  - Remove packages not in requirements
  - Add missing packages
  - Ensure consistent state

### Update Workflow
- [ ] Create `_meta/_scripts/update_base.sh`
  - Edit base.in
  - Recompile base.txt
  - Recompile all project .txt files (they depend on base)
  - Update all venvs
- [ ] Create per-project update scripts

### Testing
- [ ] Verify all projects have same base package versions
- [ ] Run all test suites in their venvs
- [ ] Verify base deps aren't duplicated at different versions
- [ ] Test adding new dependency to base
- [ ] Test adding project-specific dependency

### direnv Integration
- [ ] Create `.envrc` for each project
- [ ] Auto-activate project's venv
- [ ] Load project .env file

### IDE Integration
- [ ] Document VS Code workspace setup
- [ ] Document PyCharm setup
- [ ] Test GitHub Copilot with layered approach

### Documentation
- [ ] Create `_meta/docs/VIRTUAL_ENV_LAYERED.md`
  - pip-tools workflow explanation
  - How to add/update dependencies
  - Compilation process
  - Troubleshooting
  - When to use this approach
- [ ] Create developer quick reference
- [ ] Update main README.md

## Script Examples

### compile_requirements.sh
```bash
#!/bin/bash
# Compile all .in files to .txt lock files using pip-compile

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REQ_DIR="$REPO_ROOT/_meta/requirements"

cd "$REQ_DIR"

echo "📝 Compiling requirements with pip-tools..."

# Install pip-tools if not available
pip install pip-tools

# Compile base first
echo ""
echo "Compiling base.in..."
pip-compile base.in

# Compile project-specific (they reference base.txt)
PROJECTS=("classification" "configload" "model" "scoring" "sources" "web")

for project in "${PROJECTS[@]}"; do
    echo ""
    echo "Compiling ${project}.in..."
    pip-compile "${project}.in"
done

echo ""
echo "✅ All requirements compiled successfully!"
echo ""
echo "Generated files:"
ls -lh *.txt
```

### setup_layered_envs.sh
```bash
#!/bin/bash
# Create layered virtual environments for all projects

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REQ_DIR="$REPO_ROOT/_meta/requirements"

echo "🏗️  Creating layered virtual environments..."

# Project definitions: name, directory, requirements file
declare -A PROJECTS=(
    ["Classification"]="Classification classification.txt"
    ["ConfigLoad"]="ConfigLoad configload.txt"
    ["Model"]="Model model.txt"
    ["Scoring"]="Scoring scoring.txt"
    ["Sources"]="Sources sources.txt"
    ["Web"]="Client/Backend web.txt"
)

for project_name in "${!PROJECTS[@]}"; do
    read -r project_dir req_file <<< "${PROJECTS[$project_name]}"
    
    venv_path="$REPO_ROOT/$project_dir/venv"
    req_path="$REQ_DIR/$req_file"
    
    echo ""
    echo "📦 Setting up $project_name ($project_dir)..."
    
    # Create venv
    python3 -m venv "$venv_path"
    source "$venv_path/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install from compiled requirements
    if [ -f "$req_path" ]; then
        echo "  Installing from $req_file..."
        pip install -r "$req_path"
    else
        echo "  ⚠️  Requirements file not found: $req_path"
    fi
    
    deactivate
    echo "✅ $project_name ready"
done

echo ""
echo "🎉 All layered environments created!"
echo ""
echo "To activate:"
echo "  cd <project-directory>"
echo "  source venv/bin/activate"
```

### sync_requirements.sh
```bash
#!/bin/bash
# Sync all environments to exactly match compiled requirements

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REQ_DIR="$REPO_ROOT/_meta/requirements"

echo "🔄 Syncing all environments with pip-sync..."

# Install pip-tools if not available
pip install pip-tools

declare -A PROJECTS=(
    ["Classification"]="Classification classification.txt"
    ["ConfigLoad"]="ConfigLoad configload.txt"
    ["Model"]="Model model.txt"
    ["Scoring"]="Scoring scoring.txt"
    ["Sources"]="Sources sources.txt"
    ["Web"]="Client/Backend web.txt"
)

for project_name in "${!PROJECTS[@]}"; do
    read -r project_dir req_file <<< "${PROJECTS[$project_name]}"
    
    venv_path="$REPO_ROOT/$project_dir/venv"
    req_path="$REQ_DIR/$req_file"
    
    echo ""
    echo "Syncing $project_name..."
    
    if [ -d "$venv_path" ] && [ -f "$req_path" ]; then
        source "$venv_path/bin/activate"
        pip-sync "$req_path"
        deactivate
        echo "✅ $project_name synced"
    else
        echo "⚠️  Skipping $project_name (venv or requirements not found)"
    fi
done

echo ""
echo "✅ All environments synced!"
```

## Acceptance Criteria

- [ ] pip-tools installed and working
- [ ] All .in files created with proper constraints
- [ ] All .txt lock files compiled successfully
- [ ] Base dependencies same version across all projects
- [ ] Project-specific dependencies installed correctly
- [ ] All test suites pass in their venvs
- [ ] Scripts work on Windows and Linux
- [ ] pip-sync keeps environments consistent
- [ ] Documentation complete with examples
- [ ] Developer workflow clear and documented

## Advantages

1. **Shared Base Versions**: Common tools (pytest, black) at same version
2. **Reduced Conflicts**: Constraints ensure compatibility
3. **Clear Dependencies**: Explicit .in files, locked .txt files
4. **Reproducible**: pip-compile generates deterministic requirements
5. **Flexibility**: Can override or add project-specific packages

## Disadvantages

1. **Complexity**: Learning curve for pip-tools
2. **Maintenance**: Need to recompile when updating base
3. **Still Duplicate Storage**: Each venv has own copy (no physical sharing)
4. **Extra Steps**: Compile before install workflow
5. **Tool Dependency**: Requires pip-tools

## When to Use This Strategy

**Best for**:
- Teams that want strict version control
- Projects with mostly overlapping dependencies
- When you need reproducible environments
- When you want to prevent dependency drift

**Not ideal for**:
- Small teams that prefer simplicity
- Projects with completely different dependencies
- Rapid prototyping (extra compilation steps)

## Success Metrics

- **Disk Space**: Similar to per-project (~2-3GB) but versions aligned
- **Setup Time**: ~10-15 minutes (compilation + installation)
- **Consistency**: 100% version alignment for base packages
- **Maintenance**: Clear workflow for updates

## References

- [pip-tools documentation](https://github.com/jazzband/pip-tools)
- [James Cooke - pip-tools workflow](https://jamescooke.info/)
- [pip-tools constraints guide](https://pip-tools.readthedocs.io/en/latest/#workflow)

---

**Note**: Only implement this issue if #113 recommends Strategy 4 (Layered Hybrid with pip-tools)
