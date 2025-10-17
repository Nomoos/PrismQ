# How repo-builder Currently Works

## Overview

The `repo-builder` script is a tool that creates GitHub repositories and clones them locally following the PrismQ nested module hierarchy pattern. It does **NOT** register repositories as git submodules.

---

## Core Functionality

### What repo-builder Does

1. **Parses Input**: Accepts dotted module names or GitHub URLs
2. **Derives Chain**: Builds full hierarchy from root to deepest
3. **Creates/Clones**: For each repository in the chain:
   - Checks if repository exists on GitHub
   - Creates from template if it doesn't exist
   - Clones to correct local path if not present
   - Updates existing local clones
4. **Adds Collaborators**: Automatically adds PrismQDev as collaborator

### What repo-builder Does NOT Do

❌ Does NOT register repositories as git submodules  
❌ Does NOT add entries to `.gitmodules`  
❌ Does NOT commit to parent repositories  
❌ Does NOT run `git submodule add`  

---

## Path Mapping Rules

The `get_repository_path()` function maps dotted repository names to local filesystem paths:

### Rule Pattern
```
PrismQ                    → WORKSPACE/
PrismQ.Segment            → WORKSPACE/mod/Segment/
PrismQ.A.B                → WORKSPACE/mod/A/mod/B/
PrismQ.A.B.C              → WORKSPACE/mod/A/mod/B/mod/C/
PrismQ.A.B.C.D            → WORKSPACE/mod/A/mod/B/mod/C/mod/D/
```

### Implementation
```python
def get_repository_path(repo_name: str, workspace: Path) -> Path:
    if repo_name == "PrismQ":
        return workspace
    
    parts = repo_name.split(".")
    path = workspace
    
    # For each segment after "PrismQ", add mod/<Segment>
    for segment in parts[1:]:
        path = path / "mod" / segment
    
    return path
```

---

## Detailed Example: PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource

### Input Processing

**Input**: `PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource`

### Step 1: Derive Module Chain

The `derive_module_chain()` function builds the full hierarchy:

```python
chain = [
    'PrismQ',
    'PrismQ.Idea',
    'PrismQ.Idea.Sources',
    'PrismQ.Idea.Sources.Content',
    'PrismQ.Idea.Sources.Content.Shorts',
    'PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource'
]
```

### Step 2: Path Mapping for Each Repository

Assuming `WORKSPACE = /home/runner/work/PrismQ/PrismQ`:

| Repository Name | GitHub URL | Local Path |
|----------------|------------|------------|
| `PrismQ` | `https://github.com/Nomoos/PrismQ.git` | `/home/runner/work/PrismQ/PrismQ/` |
| `PrismQ.Idea` | `https://github.com/Nomoos/PrismQ.Idea.git` | `/home/runner/work/PrismQ/PrismQ/mod/Idea/` |
| `PrismQ.Idea.Sources` | `https://github.com/Nomoos/PrismQ.Idea.Sources.git` | `/home/runner/work/PrismQ/PrismQ/mod/Idea/mod/Sources/` |
| `PrismQ.Idea.Sources.Content` | `https://github.com/Nomoos/PrismQ.Idea.Sources.Content.git` | `/home/runner/work/PrismQ/PrismQ/mod/Idea/mod/Sources/mod/Content/` |
| `PrismQ.Idea.Sources.Content.Shorts` | `https://github.com/Nomoos/PrismQ.Idea.Sources.Content.Shorts.git` | `/home/runner/work/PrismQ/PrismQ/mod/Idea/mod/Sources/mod/Content/mod/Shorts/` |
| `PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource` | `https://github.com/Nomoos/PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource.git` | `/home/runner/work/PrismQ/PrismQ/mod/Idea/mod/Sources/mod/Content/mod/Shorts/mod/YouTubeShortsSource/` |

### Step 3: Directory Structure Created

```
/home/runner/work/PrismQ/PrismQ/                                   (PrismQ root)
├── .git/
├── mod/
│   └── Idea/                                                      (PrismQ.Idea)
│       ├── .git/                                                  (independent git repo)
│       └── mod/
│           └── Sources/                                           (PrismQ.Idea.Sources)
│               ├── .git/                                          (independent git repo)
│               └── mod/
│                   └── Content/                                   (PrismQ.Idea.Sources.Content)
│                       ├── .git/                                  (independent git repo)
│                       └── mod/
│                           └── Shorts/                            (PrismQ.Idea.Sources.Content.Shorts)
│                               ├── .git/                          (independent git repo)
│                               └── mod/
│                                   └── YouTubeShortsSource/       (final module)
│                                       └── .git/                  (independent git repo)
```

### Step 4: Processing Each Repository

For each repository in the chain, `create_git_chain()` performs:

#### 4.1 Check if Repository Exists on GitHub
```bash
gh repo view Nomoos/PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource
```

#### 4.2a If Repository EXISTS:
```python
# Check if already cloned locally
if (repo_path / ".git").exists():
    # Pull latest changes
    git -C <repo_path> pull
else:
    # Clone to correct location
    gh repo clone Nomoos/<repo_name> <repo_path>
```

#### 4.2b If Repository DOES NOT EXIST:
```python
# Create from template
gh repo create Nomoos/<repo_name> \
    --template Nomoos/PrismQ.RepositoryTemplate \
    --public \
    --confirm

# Add collaborator
gh api /repos/Nomoos/<repo_name>/collaborators/PrismQDev \
    -X PUT \
    -f permission=push
```

---

## Complete Workflow Example

### Command
```bash
python -m repo_builder PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource
```

### Console Output
```
🚀 PrismQ Nested Repository Builder & Checker
==================================================

🔍 Validating GitHub CLI authentication...
✅ GitHub CLI is authenticated

📂 Working directory: /home/runner/work/PrismQ/PrismQ

🔍 Processing input: PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource

📦 Module Chain (root → deepest):
==================================================
🏠 PrismQ (depth: 1)
  📁 PrismQ.Idea (depth: 2)
    📁 PrismQ.Idea.Sources (depth: 3)
      📁 PrismQ.Idea.Sources.Content (depth: 4)
        📁 PrismQ.Idea.Sources.Content.Shorts (depth: 5)
          🎯 PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource (depth: 6)
==================================================

Repository PrismQ already exists.
Repository PrismQ already cloned locally.
Repository PrismQ updated successfully.

Repository PrismQ.Idea already exists.
Cloning repository PrismQ.Idea...
Repository PrismQ.Idea cloned successfully.

Creating repository PrismQ.Idea.Sources from template...
Repository PrismQ.Idea.Sources created successfully from template.
Adding PrismQDev as collaborator to PrismQ.Idea.Sources...
PrismQDev added as collaborator to PrismQ.Idea.Sources.

Creating repository PrismQ.Idea.Sources.Content from template...
Repository PrismQ.Idea.Sources.Content created successfully from template.
Adding PrismQDev as collaborator to PrismQ.Idea.Sources.Content...
PrismQDev added as collaborator to PrismQ.Idea.Sources.Content.

Creating repository PrismQ.Idea.Sources.Content.Shorts from template...
Repository PrismQ.Idea.Sources.Content.Shorts created successfully from template.
Adding PrismQDev as collaborator to PrismQ.Idea.Sources.Content.Shorts...
PrismQDev added as collaborator to PrismQ.Idea.Sources.Content.Shorts.

Creating repository PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource from template...
Repository PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource created successfully from template.
Adding PrismQDev as collaborator to PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource...
PrismQDev added as collaborator to PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource.

✅ Analysis complete!
```

---

## Path Mapping Algorithm Breakdown

### For: `PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource`

```python
repo_name = "PrismQ.Idea.Sources.Content.Shorts.YouTubeShortsSource"
workspace = Path("/home/runner/work/PrismQ/PrismQ")

# Split into parts
parts = repo_name.split(".")
# Result: ['PrismQ', 'Idea', 'Sources', 'Content', 'Shorts', 'YouTubeShortsSource']

# Start with workspace root
path = workspace
# path = /home/runner/work/PrismQ/PrismQ

# Iterate over parts[1:] (skip 'PrismQ')
for segment in ['Idea', 'Sources', 'Content', 'Shorts', 'YouTubeShortsSource']:
    path = path / "mod" / segment

# Iteration 1: segment = 'Idea'
# path = /home/runner/work/PrismQ/PrismQ/mod/Idea

# Iteration 2: segment = 'Sources'
# path = /home/runner/work/PrismQ/PrismQ/mod/Idea/mod/Sources

# Iteration 3: segment = 'Content'
# path = /home/runner/work/PrismQ/PrismQ/mod/Idea/mod/Sources/mod/Content

# Iteration 4: segment = 'Shorts'
# path = /home/runner/work/PrismQ/PrismQ/mod/Idea/mod/Sources/mod/Content/mod/Shorts

# Iteration 5: segment = 'YouTubeShortsSource'
# path = /home/runner/work/PrismQ/PrismQ/mod/Idea/mod/Sources/mod/Content/mod/Shorts/mod/YouTubeShortsSource

# Final path:
# /home/runner/work/PrismQ/PrismQ/mod/Idea/mod/Sources/mod/Content/mod/Shorts/mod/YouTubeShortsSource
```

---

## Key Characteristics

### ✅ What It Handles Well
- **Hierarchical Structure**: Maintains clean nested directory organization
- **GitHub Integration**: Creates repos from template, adds collaborators
- **Idempotent**: Safe to run multiple times (checks before creating)
- **Smart Cloning**: Only clones if not already present locally

### ❌ What It Doesn't Handle
- **Submodule Registration**: Directories are independent git repos, not submodules
- **Parent Tracking**: Parent repos don't know about child repos
- **Version Control**: No tracking of which commit each child should use
- **Atomic Operations**: Can't clone/update entire hierarchy with one git command

---

## Git Status Comparison

### After Using repo-builder

```bash
cd /home/runner/work/PrismQ/PrismQ
git status
```

**Output:**
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

The child repositories (Idea, Sources, etc.) are **NOT** tracked by the parent.

```bash
cd /home/runner/work/PrismQ/PrismQ/mod/Idea/mod/Sources/mod/Content
git status
```

**Output:**
```
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
```

Each directory is an **independent git repository** with no connection to its parent.

### What .gitmodules Looks Like

The `.gitmodules` file **does not** include the newly created repositories:

```
[submodule "mod/IdeaInspiration"]
    path = mod/IdeaInspiration
    url = https://github.com/Nomoos/PrismQ.IdeaInspiration.git
    branch = main
[submodule "mod/RepositoryTemplate"]
    path = mod/RepositoryTemplate
    url = https://github.com/Nomoos/PrismQ.RepositoryTemplate.git
    branch = main
```

**Missing entries** for:
- `mod/Idea`
- `mod/Idea/mod/Sources`
- etc.

---

## Module Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  repo-builder Components                                     │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  cli.py                                               │  │
│  │  • Parse arguments                                    │  │
│  │  • Call workflow functions                            │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                          │
│                   ▼                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  parsing.py                                           │  │
│  │  • parse_github_url()                                │  │
│  │  • derive_module_chain()                             │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                          │
│                   ▼                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  repository.py                                        │  │
│  │  • repository_exists()                               │  │
│  │  • get_repository_path()                             │  │
│  │  • create_git_chain()                                │  │
│  │  • add_repository_collaborator()                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  GitHub CLI Commands Used:                                   │
│  • gh repo view <name>                                       │
│  • gh repo create <name> --template ...                      │
│  • gh repo clone <name> <path>                               │
│  • gh api /repos/<name>/collaborators/<user>                 │
│                                                               │
│  Git Commands Used:                                          │
│  • git -C <path> pull                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Comparison with Other Tools

### repo-builder vs git submodule add

| Feature | repo-builder | git submodule add |
|---------|-------------|-------------------|
| Creates GitHub repo | ✅ Yes | ❌ No |
| Clones locally | ✅ Yes | ✅ Yes |
| Registers in .gitmodules | ❌ No | ✅ Yes |
| Parent tracks child commit | ❌ No | ✅ Yes |
| Creates template-based | ✅ Yes | ❌ No |
| Adds collaborators | ✅ Yes | ❌ No |
| Handles nested hierarchy | ✅ Yes | ❌ Manual |

---

## Usage Examples

### Example 1: Simple Two-Level Module
```bash
python -m repo_builder PrismQ.MyModule
```

**Chain**: `['PrismQ', 'PrismQ.MyModule']`

**Paths**:
- `PrismQ` → `/workspace/`
- `PrismQ.MyModule` → `/workspace/mod/MyModule/`

### Example 2: Three-Level Module
```bash
python -m repo_builder PrismQ.IdeaInspiration.Sources
```

**Chain**: `['PrismQ', 'PrismQ.IdeaInspiration', 'PrismQ.IdeaInspiration.Sources']`

**Paths**:
- `PrismQ` → `/workspace/`
- `PrismQ.IdeaInspiration` → `/workspace/mod/IdeaInspiration/`
- `PrismQ.IdeaInspiration.Sources` → `/workspace/mod/IdeaInspiration/mod/Sources/`

### Example 3: Using GitHub URL
```bash
python -m repo_builder https://github.com/Nomoos/PrismQ.Idea.Sources.Content
```

**Parsed to**: `PrismQ.Idea.Sources.Content`

**Chain**: `['PrismQ', 'PrismQ.Idea', 'PrismQ.Idea.Sources', 'PrismQ.Idea.Sources.Content']`

---

## Summary

### What repo-builder Achieves
1. ✅ Automated GitHub repository creation from template
2. ✅ Systematic local directory structure (mod-based hierarchy)
3. ✅ Automatic collaborator management
4. ✅ Idempotent operations (safe to re-run)

### What's Missing (Reason for add-repo-with-submodule)
1. ❌ Git submodule registration
2. ❌ Parent repository awareness of children
3. ❌ Commit tracking between parent and child
4. ❌ Atomic updates of entire module tree
5. ❌ Automatic initialization with `git clone --recurse-submodules`

### The Gap
After running repo-builder, you have a perfect directory structure with all repos created and cloned, but:
- Parent repos have no knowledge of child repos
- Can't track which commit of a child repo should be used
- Team members can't automatically get all submodules
- CI/CD doesn't know about nested structure

**This is exactly what add-repo-with-submodule will solve** by adding the submodule registration step after repo-builder's work is complete.
