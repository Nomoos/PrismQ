# Issue #116: Implement Grouped Virtual Environments Strategy

**Type**: Implementation  
**Priority**: Medium  
**Status**: New  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 1-2 weeks  
**Dependencies**: #113 (if this strategy is chosen)  
**Related Issues**: #113, #114, #115, #117

---

## Description

Implement grouped virtual environments for PrismQ.IdeaInspiration based on logical project groupings. This balances isolation and efficiency by sharing environments among related projects.

This issue should be implemented if Strategy 3 (Grouped Environments) is chosen in #113.

## Implementation Overview

Create 3 strategic environment groups based on project characteristics and dependencies:

1. **Core Environment**: Lightweight modules with similar dependencies
2. **ML Environment**: Machine learning processing (future heavy dependencies)
3. **Web Environment**: Web application with FastAPI stack

## Proposed Architecture

```
PrismQ.IdeaInspiration/
├── .venv-core/              # Shared: Classification, Model, ConfigLoad, Sources
├── .venv-ml/                # Isolated: Scoring (when ML deps added)
├── .venv-web/               # Isolated: Client/Backend
├── _meta/
│   └── _scripts/
│       ├── setup_grouped_envs.sh     # Create all group envs
│       ├── update_grouped_envs.sh    # Update all groups
│       ├── activate_core.sh          # Activate core env
│       ├── activate_ml.sh            # Activate ML env
│       ├── activate_web.sh           # Activate web env
│       └── test_all_groups.sh        # Test all groups
├── Classification/
│   ├── .envrc               # Auto-activate .venv-core
│   └── requirements.txt
├── ConfigLoad/
│   ├── .envrc               # Auto-activate .venv-core
│   └── requirements.txt
├── Model/
│   ├── .envrc               # Auto-activate .venv-core
│   └── requirements.txt
├── Sources/
│   ├── .envrc               # Auto-activate .venv-core
│   └── requirements.txt
├── Scoring/
│   ├── .envrc               # Auto-activate .venv-ml
│   └── requirements.txt
└── Client/Backend/
    ├── .envrc               # Auto-activate .venv-web
    └── requirements.txt
```

## Grouping Rationale

### Group 1: Core Environment (.venv-core)
**Projects**: Classification, Model, ConfigLoad, Sources

**Justification**:
- All have zero or minimal runtime dependencies
- Similar development dependency profiles (pytest, black, mypy)
- Often developed and tested together
- No conflicting requirements
- Tight integration in the pipeline

**Dependencies**:
- python-dotenv (ConfigLoad, Sources)
- psutil (ConfigLoad - optional)
- pytest, black, mypy, flake8, ruff (all dev dependencies)

### Group 2: ML Environment (.venv-ml)
**Projects**: Scoring

**Justification**:
- Future heavy ML dependencies (torch, transformers, sentence-transformers)
- GPU-intensive workloads
- May need specific CUDA/PyTorch versions
- Isolated to prevent conflicts with web framework
- Memory-intensive, benefits from dedicated environment

**Current Dependencies**:
- python-dotenv (lightweight now)

**Future Dependencies** (commented in requirements.txt):
- torch>=2.0.0 (GPU acceleration)
- transformers>=4.30.0
- sentence-transformers>=2.2.0
- numpy, pillow

### Group 3: Web Environment (.venv-web)
**Projects**: Client/Backend

**Justification**:
- Heavy web framework dependencies (FastAPI, Uvicorn, Pydantic)
- Completely different domain from data processing
- Independent development cycle
- Frequent iterations and updates
- No overlap with ML or core modules

**Dependencies**:
- fastapi, uvicorn, pydantic, sse-starlette
- aiofiles, httpx
- pytest, pytest-asyncio

## Tasks

### Environment Setup Scripts
- [ ] Create `_meta/_scripts/setup_grouped_envs.sh`
  - Create .venv-core with core dependencies
  - Create .venv-ml with ML dependencies
  - Create .venv-web with web dependencies
  - Report successful creation

### Dependency Management
- [ ] Create `_meta/requirements/core-requirements.txt`
  - Combine Classification, Model, ConfigLoad, Sources deps
  - Deduplicate and resolve versions
- [ ] Create `_meta/requirements/ml-requirements.txt`
  - Scoring dependencies (current + future commented)
- [ ] Create `_meta/requirements/web-requirements.txt`
  - Client/Backend dependencies

### Activation Scripts
- [ ] Create `_meta/_scripts/activate_core.sh`
- [ ] Create `_meta/_scripts/activate_ml.sh`
- [ ] Create `_meta/_scripts/activate_web.sh`
- [ ] Create PowerShell versions for Windows

### direnv Integration
- [ ] Create `.envrc` for each project pointing to correct group env
  - Classification, Model, ConfigLoad, Sources → .venv-core
  - Scoring → .venv-ml
  - Client/Backend → .venv-web

### Testing
- [ ] Run Classification tests with .venv-core
- [ ] Run Model tests with .venv-core
- [ ] Run ConfigLoad tests with .venv-core
- [ ] Run Sources tests with .venv-core
- [ ] Run Scoring tests with .venv-ml
- [ ] Run Client/Backend tests with .venv-web
- [ ] Verify no cross-contamination

### IDE Integration
- [ ] Document multi-folder VS Code workspace setup
  - Configure interpreter per project group
  - Workspace settings template
- [ ] Document PyCharm setup
- [ ] Test GitHub Copilot with grouped interpreters

### Documentation
- [ ] Create `_meta/docs/VIRTUAL_ENV_GROUPED.md`
  - Grouping rationale
  - Setup instructions
  - How to switch between groups
  - Adding new projects to groups
  - When to create new group
- [ ] Update main README.md
- [ ] Add to .gitignore: `.venv-*/`

## Script Examples

### setup_grouped_envs.sh
```bash
#!/bin/bash
# Create grouped virtual environments for PrismQ.IdeaInspiration

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "🏗️  Creating grouped virtual environments..."

# Group 1: Core Environment
echo ""
echo "📦 Creating .venv-core (Classification, Model, ConfigLoad, Sources)..."
python3 -m venv "$REPO_ROOT/.venv-core"
source "$REPO_ROOT/.venv-core/bin/activate"
pip install --upgrade pip setuptools wheel

# Install core dependencies
for project in Classification Model ConfigLoad Sources; do
    if [ -f "$REPO_ROOT/$project/requirements.txt" ]; then
        echo "  Installing $project dependencies..."
        pip install -r "$REPO_ROOT/$project/requirements.txt"
    fi
done

deactivate
echo "✅ .venv-core ready"

# Group 2: ML Environment
echo ""
echo "📦 Creating .venv-ml (Scoring)..."
python3 -m venv "$REPO_ROOT/.venv-ml"
source "$REPO_ROOT/.venv-ml/bin/activate"
pip install --upgrade pip setuptools wheel

if [ -f "$REPO_ROOT/Scoring/requirements.txt" ]; then
    echo "  Installing Scoring dependencies..."
    pip install -r "$REPO_ROOT/Scoring/requirements.txt"
fi

deactivate
echo "✅ .venv-ml ready"

# Group 3: Web Environment
echo ""
echo "📦 Creating .venv-web (Client/Backend)..."
python3 -m venv "$REPO_ROOT/.venv-web"
source "$REPO_ROOT/.venv-web/bin/activate"
pip install --upgrade pip setuptools wheel

if [ -f "$REPO_ROOT/Client/Backend/requirements.txt" ]; then
    echo "  Installing Client/Backend dependencies..."
    pip install -r "$REPO_ROOT/Client/Backend/requirements.txt"
fi

deactivate
echo "✅ .venv-web ready"

echo ""
echo "🎉 All grouped environments created successfully!"
echo ""
echo "Activation commands:"
echo "  Core:   source _meta/_scripts/activate_core.sh"
echo "  ML:     source _meta/_scripts/activate_ml.sh"
echo "  Web:    source _meta/_scripts/activate_web.sh"
```

### activate_core.sh
```bash
#!/bin/bash
# Activate core environment (Classification, Model, ConfigLoad, Sources)

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$REPO_ROOT/.venv-core/bin/activate"
echo "✅ Activated core environment (Classification, Model, ConfigLoad, Sources)"
```

### .envrc for core projects (e.g., Classification/.envrc)
```bash
# Auto-activate core environment
# Requires direnv: https://direnv.net/

REPO_ROOT="$(git rev-parse --show-toplevel)"

if [ -f "$REPO_ROOT/.venv-core/bin/activate" ]; then
    source "$REPO_ROOT/.venv-core/bin/activate"
fi

# Load project .env if exists
if [ -f ".env" ]; then
    dotenv
fi

export PROJECT_GROUP="core"
export PROJECT_NAME="Classification"
```

### .envrc for ML project (Scoring/.envrc)
```bash
# Auto-activate ML environment
# Requires direnv: https://direnv.net/

REPO_ROOT="$(git rev-parse --show-toplevel)"

if [ -f "$REPO_ROOT/.venv-ml/bin/activate" ]; then
    source "$REPO_ROOT/.venv-ml/bin/activate"
fi

# Load project .env if exists
if [ -f ".env" ]; then
    dotenv
fi

export PROJECT_GROUP="ml"
export PROJECT_NAME="Scoring"
```

## Acceptance Criteria

- [ ] Three group environments created (.venv-core, .venv-ml, .venv-web)
- [ ] All dependencies installed correctly in each group
- [ ] All project tests pass in their group environment
- [ ] direnv auto-activates correct environment per project
- [ ] Scripts work on Windows and Linux
- [ ] IDE integration documented and tested
- [ ] Developer documentation complete
- [ ] No conflicts within or between groups

## Advantages Over Other Strategies

**vs. Single Shared Environment**:
- ✅ Isolation between ML, web, and core modules
- ✅ No conflicts between FastAPI and future PyTorch
- ✅ Smaller individual environments

**vs. Per-Project Isolation**:
- ✅ Reduced duplication for core modules (4 projects share 1 env)
- ✅ Fewer environments to manage (3 instead of 6)
- ✅ Less disk space (no duplication within groups)

## Trade-offs

**Pros**:
- Balanced approach: isolation where needed, sharing where safe
- Logical groupings based on dependency profiles
- Manageable number of environments (3)
- Reduced disk space vs. full isolation

**Cons**:
- More complex than single environment
- Requires understanding of which project belongs to which group
- Adding new projects requires grouping decision
- Need group-aware direnv setup

## Success Metrics

- **Disk Space**: ~1.5-2.5GB total (vs. 3GB+ for per-project)
  - .venv-core: ~300-500MB
  - .venv-ml: ~500-1000MB (with ML deps)
  - .venv-web: ~300-500MB
- **Setup Time**: < 8 minutes for all 3 environments
- **Test Success**: 100% pass rate for all projects
- **Developer Experience**: Clear grouping, easy switching

## Future Considerations

### When to Add New Group
Create a new group environment when:
- New project has unique, conflicting dependencies
- New project has very heavy dependencies (e.g., new ML model types)
- New domain with different framework (e.g., data visualization with Dash)

### When to Add Project to Existing Group
Add to existing group when:
- Dependencies are compatible with group
- Project logically fits the group's purpose
- No version conflicts introduced

---

**Note**: Only implement this issue if #113 recommends Strategy 3 (Grouped Environments)
