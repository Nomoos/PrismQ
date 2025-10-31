# Issue #115: Implement Per-Project Virtual Environments

**Type**: Implementation  
**Priority**: Medium  
**Status**: New  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 1-2 weeks  
**Dependencies**: #113 (if this strategy is chosen)  
**Related Issues**: #113, #114, #116, #117

---

## Description

Implement fully isolated virtual environments for each PrismQ.IdeaInspiration project. This issue should be implemented if Strategy 2 (Per-Project Isolation) is chosen in #113.

## Implementation Overview

Create individual `venv/` directory in each project folder, with automation scripts to create, update, and manage all environments.

## Architecture

```
PrismQ.IdeaInspiration/
├── _meta/
│   └── _scripts/
│       ├── setup_all_envs.sh        # Create all project venvs
│       ├── update_all_envs.sh       # Update all venvs
│       ├── activate_env.sh          # Helper: activate specific project
│       └── test_all_envs.sh         # Run tests in each env
├── Classification/
│   ├── venv/                        # Classification environment
│   ├── .envrc                       # direnv auto-activation
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

## Tasks

### Environment Creation Scripts
- [ ] Create `_meta/_scripts/setup_all_envs.sh`
  - Iterate through all project directories
  - Create `venv/` in each project
  - Activate and install requirements
  - Verify installation success
- [ ] Create Windows PowerShell version
- [ ] Handle errors gracefully (skip if venv exists)

### Individual Project Setup
- [ ] Add `venv/` to each project's .gitignore
- [ ] Ensure requirements.txt is up-to-date for each project
- [ ] Create per-project activation helpers if needed

### Update and Maintenance Scripts
- [ ] Create `_meta/_scripts/update_all_envs.sh`
  - Update pip in each environment
  - Upgrade packages with --upgrade flag
  - Report any failures
- [ ] Create `_meta/_scripts/clean_all_envs.sh`
  - Remove all venv directories
  - Useful for fresh start

### Testing Automation
- [ ] Create `_meta/_scripts/test_all_envs.sh`
  - Run each project's tests in its own environment
  - Collect results
  - Generate summary report
- [ ] Verify isolation: test passes in own env, not others

### direnv Integration
- [ ] Create `.envrc` template for projects
- [ ] Create `.envrc` for each project directory
  - Auto-activate project's venv on `cd`
  - Load project-specific .env file
  - Deactivate on `cd` out
- [ ] Document direnv installation
- [ ] Test on Windows (may need workarounds)

### IDE Integration
- [ ] Document VS Code multi-root workspace setup
  - Configure Python interpreter per folder
  - Workspace settings template
- [ ] Document PyCharm multi-module project setup
- [ ] Test GitHub Copilot with folder-specific interpreters

### Documentation
- [ ] Create `_meta/docs/VIRTUAL_ENV_PER_PROJECT.md`
  - Setup instructions
  - How to switch between projects
  - direnv usage guide
  - Adding new projects
  - Troubleshooting
- [ ] Update main README.md
- [ ] Add to .gitignore: `*/venv/`

## Script Examples

### setup_all_envs.sh
```bash
#!/bin/bash
# Create virtual environments for all PrismQ projects

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECTS=("Classification" "ConfigLoad" "Model" "Scoring" "Sources" "Client/Backend")

for project in "${PROJECTS[@]}"; do
    project_dir="$REPO_ROOT/$project"
    
    if [ ! -d "$project_dir" ]; then
        echo "⚠️  Skipping $project (directory not found)"
        continue
    fi
    
    echo "📦 Setting up environment for $project..."
    
    # Create venv
    python3 -m venv "$project_dir/venv"
    
    # Activate
    source "$project_dir/venv/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install requirements if exists
    if [ -f "$project_dir/requirements.txt" ]; then
        pip install -r "$project_dir/requirements.txt"
    fi
    
    # Deactivate
    deactivate
    
    echo "✅ $project environment ready"
done

echo ""
echo "🎉 All environments created successfully!"
echo ""
echo "To activate an environment:"
echo "  cd <project-directory>"
echo "  source venv/bin/activate"
echo ""
echo "Or install direnv for automatic activation:"
echo "  https://direnv.net/"
```

### activate_env.sh (helper script)
```bash
#!/bin/bash
# Helper to activate a specific project environment

if [ -z "$1" ]; then
    echo "Usage: source _meta/_scripts/activate_env.sh <project-name>"
    echo "Projects: Classification, ConfigLoad, Model, Scoring, Sources, Client/Backend"
    return 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECT="$1"
VENV_PATH="$REPO_ROOT/$PROJECT/venv/bin/activate"

if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
    echo "✅ Activated $PROJECT environment"
else
    echo "❌ Environment not found: $VENV_PATH"
    echo "Run: _meta/_scripts/setup_all_envs.sh"
    return 1
fi
```

### .envrc template
```bash
# Auto-activate virtual environment when entering this directory
# Requires direnv: https://direnv.net/

# Activate the local venv
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    dotenv
fi

# Set project-specific environment variables
export PROJECT_NAME="Classification"  # Change per project
```

### test_all_envs.sh
```bash
#!/bin/bash
# Run tests for all projects in their respective environments

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PROJECTS=("Classification" "ConfigLoad" "Model" "Scoring" "Sources" "Client/Backend")

echo "🧪 Running tests for all projects..."
echo ""

failed_projects=()

for project in "${PROJECTS[@]}"; do
    project_dir="$REPO_ROOT/$project"
    
    if [ ! -d "$project_dir/venv" ]; then
        echo "⚠️  Skipping $project (venv not found)"
        continue
    fi
    
    echo "Testing $project..."
    
    cd "$project_dir"
    source venv/bin/activate
    
    if pytest; then
        echo "✅ $project tests passed"
    else
        echo "❌ $project tests failed"
        failed_projects+=("$project")
    fi
    
    deactivate
    echo ""
done

if [ ${#failed_projects[@]} -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "❌ Tests failed for: ${failed_projects[*]}"
    exit 1
fi
```

## Acceptance Criteria

- [ ] Each project has its own `venv/` directory
- [ ] All project dependencies installed correctly
- [ ] All project test suites pass in their own environments
- [ ] Scripts work on Windows and Linux
- [ ] direnv configuration working for each project
- [ ] IDE multi-folder setup documented and tested
- [ ] Developer documentation complete
- [ ] No cross-contamination between environments

## Advantages

1. **Full Isolation**: Projects can use different package versions
2. **Clean Dependencies**: Each env only has what that project needs
3. **Independent Updates**: Upgrade one project without affecting others
4. **Conflict-Free**: No version conflicts between projects
5. **Flexibility**: Easy to add projects with unique requirements

## Disadvantages

1. **Disk Space**: ~200-500MB per environment (6 envs = 1.2-3GB)
2. **Setup Time**: 5-10 minutes to create all environments
3. **Maintenance**: Need to update 6 environments separately
4. **Switching**: Must remember to activate correct environment
5. **Duplication**: Common packages installed multiple times

## Mitigation Strategies

### For Disk Space
- Use pip's wheel cache (automatically reuses downloads)
- Clean old environments periodically
- Accept trade-off for isolation benefits

### For Switching
- Use direnv for automatic activation
- Document workflow clearly
- Provide helper scripts

### For Maintenance
- Use `update_all_envs.sh` script
- Consider shared base requirements in future (hybrid approach)

## Success Metrics

- **Total Disk Space**: < 3GB for all 6 environments
- **Setup Time**: < 10 minutes for all environments
- **Test Success**: 100% pass rate in each environment
- **Developer Satisfaction**: Easy to work with after initial setup

---

**Note**: Only implement this issue if #113 recommends Strategy 2 (Per-Project Isolation)
