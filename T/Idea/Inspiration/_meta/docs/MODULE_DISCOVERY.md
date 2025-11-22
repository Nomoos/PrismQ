# Module Discovery Library

## Overview

The `discover_modules.py` script provides a **single source of truth** for discovering modules in the PrismQ.T.Idea.Inspiration repository. This shared discovery core ensures consistency across different tools that need to know about repository modules.

## Purpose

This library centralizes module discovery logic to:
- ✅ Eliminate duplication across scripts
- ✅ Prevent inconsistencies between different discovery mechanisms
- ✅ Provide a flexible API for different use cases
- ✅ Scale to additional consumers (CI/CD, documentation generators, etc.)

## Usage

### Command Line

```bash
# Discover modules for environment setup (default)
python3 _meta/scripts/discover_modules.py

# Discover all modules (including nested ones)
python3 _meta/scripts/discover_modules.py --filter all

# Discover modules suitable for Client registration
python3 _meta/scripts/discover_modules.py --filter client

# Output as names only (for scripting)
python3 _meta/scripts/discover_modules.py --format names

# Output as JSON
python3 _meta/scripts/discover_modules.py --format json
```

### Python API

```python
from _meta.scripts.discover_modules import ModuleDiscovery

# Initialize discovery
discovery = ModuleDiscovery()

# Get modules for environment setup (top-level only)
env_modules = discovery.discover_for_env_setup()
for module in env_modules:
    print(f"{module.name}: {module.path}")

# Get all modules (including nested)
all_modules = discovery.discover_all()

# Get modules for Client registration
client_modules = discovery.discover_for_client()
```

## Filters

### `env-setup` (Default)

Returns top-level modules needed for environment setup:
- Classification
- EnvLoad
- Model
- Scoring
- Sources

**Filtering logic:**
- Finds all `requirements.txt` files
- Excludes system directories (_meta, .git, venv, etc.)
- Filters out nested modules (if both parent and child have requirements.txt, keeps only parent)

### `all`

Returns all modules found in the repository, including nested ones:
- All modules from `env-setup`
- Plus: Sources/Commerce/AmazonBestsellers, Sources/Creative/LyricSnippets, etc.

**Use case:** Documentation generation, analysis tools

### `client`

Returns modules suitable for Client UI registration:
- Classification
- Scoring
- Sources (and its submodules)
- Excludes: EnvLoad, Model, Client itself (infrastructure)

**Use case:** Client module registration, UI module lists

## Module Information

Each discovered module provides:

```python
@dataclass
class ModuleInfo:
    name: str                    # e.g., "Classification", "Scoring"
    path: Path                   # Absolute path to module directory
    has_requirements: bool       # Has requirements.txt
    has_setup_py: bool          # Has setup.py
    has_pyproject_toml: bool    # Has pyproject.toml
    is_python_project: bool     # Is a Python project
    depth: int                   # Depth from repository root
```

## Integration

### Environment Scripts

All environment management scripts now use the shared discovery:

```bash
# In setup_all_envs.sh
DISCOVERY_SCRIPT="$REPO_ROOT/_meta/scripts/discover_modules.py"
while IFS= read -r project_name; do
    PROJECTS+=("$project_name")
done < <(python3 "$DISCOVERY_SCRIPT" --filter env-setup --format names)
```

### Future Integration Points

The shared discovery can be used by:
- **CI/CD pipelines**: Discover which modules to test/build
- **Documentation generators**: List all available modules
- **Client module loader**: Validate or supplement modules.json
- **Dependency analyzers**: Map module relationships
- **Migration tools**: Find modules needing updates

## Benefits

### Before (Duplicated Logic)

Each script had its own discovery logic:
- ❌ 8 scripts with duplicated find/filter code
- ❌ Inconsistencies between bash and PowerShell
- ❌ Hard to maintain and update
- ❌ Risk of divergence over time

### After (Shared Core)

One discovery implementation:
- ✅ Single source of truth
- ✅ Consistent results across all tools
- ✅ Easy to update in one place
- ✅ Can add new filters/features centrally
- ✅ Testable in isolation

## Examples

### Example 1: List all modules with setup.py

```bash
python3 _meta/scripts/discover_modules.py --filter all --format json | \
  jq '.[] | select(.has_setup_py == true) | .name'
```

### Example 2: Get module count

```bash
python3 _meta/scripts/discover_modules.py --format names | wc -l
```

### Example 3: Check if module exists

```bash
if python3 _meta/scripts/discover_modules.py --format names | grep -q "^Analytics$"; then
    echo "Analytics module found"
fi
```

## Adding Custom Filters

To add a new filter, extend the `ModuleDiscovery` class:

```python
def discover_for_documentation(self, max_depth: int = 3) -> List[ModuleInfo]:
    """Discover modules that should appear in documentation."""
    all_modules = self.discover_all(max_depth)
    
    # Custom filtering logic
    doc_modules = [
        m for m in all_modules
        if (m.path / 'README.md').exists()
    ]
    
    return sorted(doc_modules, key=lambda m: m.name)
```

Then add the filter to the CLI in `main()`:

```python
parser.add_argument(
    '--filter',
    choices=['all', 'env-setup', 'client', 'documentation'],
    default='env-setup',
    help='Filter modules by purpose'
)
```

## Maintenance

### Updating Exclusions

To exclude additional directories, update `EXCLUDED_DIRS`:

```python
class ModuleDiscovery:
    EXCLUDED_DIRS = {
        '_meta', '.git', '.idea', 'venv', 'node_modules',
        # Add new exclusions here
        '.vscode', 'coverage', 'htmlcov'
    }
```

### Changing Search Depth

The default search depth is 3 levels. To change:

```bash
python3 _meta/scripts/discover_modules.py --max-depth 4
```

Or in Python:

```python
modules = discovery.discover_all(max_depth=4)
```
