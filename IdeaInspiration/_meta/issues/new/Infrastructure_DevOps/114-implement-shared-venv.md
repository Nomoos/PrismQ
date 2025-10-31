# Issue #114: Implement Shared Virtual Environment Strategy

**Type**: Implementation  
**Priority**: Medium  
**Status**: New  
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM  
**Estimated Duration**: 1 week  
**Dependencies**: #113 (if this strategy is chosen)  
**Related Issues**: #113, #115, #116, #117

---

## Description

Implement a single shared virtual environment for all PrismQ.IdeaInspiration projects in the monorepo. This issue should only be implemented if Strategy 1 (One Shared Environment) is chosen in #113.

## Implementation Overview

Create one top-level `.venv` directory containing all dependencies from all projects, with automation scripts to maintain it.

## Architecture

```
PrismQ.IdeaInspiration/
├── .venv/                    # Single shared virtual environment
├── _meta/
│   └── _scripts/
│       ├── create_shared_env.sh      # Create the shared venv
│       ├── update_shared_env.sh      # Update all dependencies
│       └── activate_shared_env.sh    # Helper to activate
├── Classification/
├── ConfigLoad/
├── Model/
├── Scoring/
├── Sources/
└── Client/Backend/
```

## Tasks

### Environment Creation
- [ ] Create `_meta/_scripts/create_shared_env.sh`
  - Create `.venv` at repository root
  - Install Python 3.10+ (verify compatibility)
  - Upgrade pip, setuptools, wheel

### Dependency Management
- [ ] Create consolidated requirements file
  - Option A: Generate `requirements-all.txt` combining all projects
  - Option B: Script that installs from each project's requirements.txt
- [ ] Handle version conflicts
  - Document any conflicting requirements
  - Choose compatible versions or latest
  - Update project requirements if needed
- [ ] Create `_meta/_scripts/update_shared_env.sh`
  - Re-install/upgrade all dependencies
  - Verify no conflicts
  - Run tests after updates

### Activation Scripts
- [ ] Create `_meta/_scripts/activate_shared_env.sh` (Linux/macOS)
- [ ] Create `_meta/_scripts/activate_shared_env.ps1` (Windows PowerShell)
- [ ] Create `_meta/_scripts/activate_shared_env.bat` (Windows CMD)

### IDE Integration
- [ ] Document VS Code setup
  - Set Python interpreter to `.venv/bin/python`
  - Configure workspace settings
- [ ] Document PyCharm setup
- [ ] Test GitHub Copilot integration
  - Verify it sees all project dependencies
  - Test autocompletion across projects

### Testing
- [ ] Run all project test suites with shared env
  - Classification tests
  - ConfigLoad tests
  - Model tests
  - Scoring tests
  - Sources tests
  - Client/Backend tests
- [ ] Verify no import conflicts
- [ ] Verify all dev tools work (pytest, black, mypy, ruff)

### Documentation
- [ ] Create `_meta/docs/VIRTUAL_ENV_SETUP.md`
  - Installation instructions
  - How to activate the environment
  - How to add new dependencies
  - Troubleshooting guide
- [ ] Update main README.md with setup instructions
- [ ] Add to .gitignore: `/.venv/`

## Script Examples

### create_shared_env.sh
```bash
#!/bin/bash
# Create shared virtual environment for PrismQ.IdeaInspiration

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="$REPO_ROOT/.venv"

echo "Creating shared virtual environment at $VENV_DIR"

# Create venv
python3 -m venv "$VENV_DIR"

# Activate
source "$VENV_DIR/bin/activate"

# Upgrade base tools
pip install --upgrade pip setuptools wheel

# Install all project dependencies
echo "Installing Classification dependencies..."
pip install -r "$REPO_ROOT/Classification/requirements.txt"

echo "Installing ConfigLoad dependencies..."
pip install -r "$REPO_ROOT/ConfigLoad/requirements.txt"

# ... repeat for all projects

echo "Shared environment created successfully!"
echo "Activate with: source .venv/bin/activate"
```

### update_shared_env.sh
```bash
#!/bin/bash
# Update shared virtual environment

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "$REPO_ROOT/.venv/bin/activate"

echo "Updating all dependencies..."

# Reinstall with --upgrade flag
for project in Classification ConfigLoad Model Scoring Sources Client/Backend; do
    if [ -f "$REPO_ROOT/$project/requirements.txt" ]; then
        echo "Updating $project dependencies..."
        pip install --upgrade -r "$REPO_ROOT/$project/requirements.txt"
    fi
done

echo "Dependencies updated successfully!"
```

## Acceptance Criteria

- [ ] Single `.venv` directory created at repository root
- [ ] All project dependencies installed without conflicts
- [ ] All project test suites pass using shared environment
- [ ] Scripts created and tested on Windows
- [ ] IDE integration documented and tested
- [ ] GitHub Copilot can access all project dependencies
- [ ] Developer documentation complete
- [ ] No conflicts between web framework and ML dependencies

## Known Challenges

### Version Conflicts
- **Issue**: Different projects may require different versions
- **Solution**: Document conflicts, choose compatible versions, test thoroughly

### Large Environment Size
- **Issue**: Environment contains superset of all dependencies
- **Solution**: Accept the trade-off, monitor disk usage

### Future ML Dependencies
- **Issue**: Scoring module may need specific torch/CUDA versions
- **Solution**: Test compatibility, may need to reconsider strategy later

## Success Metrics

- **Disk Space**: Single `.venv` directory size (~500MB-2GB estimated)
- **Install Time**: One-time setup < 10 minutes
- **Developer Experience**: One activation command for all projects
- **Test Pass Rate**: 100% of all project tests pass

## Rollback Plan

If conflicts are unresolvable:
- Fall back to per-project or grouped environments (#115 or #116)
- Keep scripts for reference
- Document lessons learned

---

**Note**: Only implement this issue if #113 recommends Strategy 1 (Shared Environment)
