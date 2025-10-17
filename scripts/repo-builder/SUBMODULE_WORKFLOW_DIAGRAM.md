# Submodule Workflow Diagrams

## Current repo-builder Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  USER INPUT: PrismQ.IdeaInspiration.NewModule               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Parse & Derive Chain                                        │
│  ['PrismQ', 'PrismQ.IdeaInspiration',                       │
│   'PrismQ.IdeaInspiration.NewModule']                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  For each repo in chain:                                     │
│                                                               │
│  ┌─────────────────────────────────────────┐               │
│  │ 1. Check if exists on GitHub            │               │
│  │    YES: Clone locally if not present    │               │
│  │    NO:  Create from template            │               │
│  └─────────────────────────────────────────┘               │
│                                                               │
│  ┌─────────────────────────────────────────┐               │
│  │ 2. Map to local path:                   │               │
│  │    PrismQ.A.B → WORKSPACE/mod/A/mod/B   │               │
│  └─────────────────────────────────────────┘               │
│                                                               │
│  ❌ NOT DONE: Register as git submodule    │               │
│  ❌ NOT DONE: Add to .gitmodules           │               │
│  ❌ NOT DONE: Commit to parent             │               │
└─────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  RESULT:                                                     │
│  ✅ Repositories created/cloned                             │
│  ✅ Local directory structure correct                       │
│  ❌ NOT git submodules - just directories                   │
│  ❌ Parent repo unaware of children                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Proposed add-repo-with-submodule Workflow (Option 1)

```
┌─────────────────────────────────────────────────────────────┐
│  USER INPUT: PrismQ.IdeaInspiration.NewModule               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Use repo-builder (import as library)               │
│  ┌─────────────────────────────────────────┐               │
│  │ • Parse & derive chain                  │               │
│  │ • Create/clone repositories             │               │
│  │ • Set up directory structure            │               │
│  └─────────────────────────────────────────┘               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Add submodule registration (NEW)                   │
│                                                               │
│  For each repo in chain (except PrismQ root):               │
│                                                               │
│  ┌─────────────────────────────────────────┐               │
│  │ A. Determine parent repository:         │               │
│  │    PrismQ.A.B → parent is PrismQ.A      │               │
│  └─────────────────────────────────────────┘               │
│                     │                                        │
│                     ▼                                        │
│  ┌─────────────────────────────────────────┐               │
│  │ B. Get repository URL:                  │               │
│  │    https://github.com/Nomoos/           │               │
│  │    PrismQ.A.B.git                       │               │
│  └─────────────────────────────────────────┘               │
│                     │                                        │
│                     ▼                                        │
│  ┌─────────────────────────────────────────┐               │
│  │ C. Add as submodule in parent:          │               │
│  │    cd PARENT_PATH                       │               │
│  │    git submodule add <url> <rel_path>   │               │
│  │    (e.g., mod/B)                        │               │
│  └─────────────────────────────────────────┘               │
│                     │                                        │
│                     ▼                                        │
│  ┌─────────────────────────────────────────┐               │
│  │ D. Commit changes to parent:            │               │
│  │    git add .gitmodules mod/B            │               │
│  │    git commit -m "Add PrismQ.A.B        │               │
│  │                   as submodule"         │               │
│  └─────────────────────────────────────────┘               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Initialize submodules (optional)                   │
│  ┌─────────────────────────────────────────┐               │
│  │ git submodule update --init --recursive │               │
│  └─────────────────────────────────────────┘               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  RESULT:                                                     │
│  ✅ Repositories created/cloned                             │
│  ✅ Local directory structure correct                       │
│  ✅ Registered as git submodules                            │
│  ✅ .gitmodules updated                                     │
│  ✅ Parent repo tracks submodule commits                    │
│  ✅ Changes committed to parent                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Example: Creating PrismQ.IdeaInspiration.NewModule

### Before (repo-builder only):

```
PrismQ/                                    (git repo)
├── .git/
├── mod/
│   ├── IdeaInspiration/                   (just a directory - NOT submodule!)
│   │   ├── .git/                          (independent git repo)
│   │   └── mod/
│   │       └── NewModule/                 (just a directory - NOT submodule!)
│   │           └── .git/                  (independent git repo)
│   └── RepositoryTemplate/
└── .gitmodules                            (doesn't mention IdeaInspiration.NewModule)
```

❌ **Problem**: Parent repos don't know about child repos
❌ `git status` in PrismQ doesn't show changes in submodules
❌ `git clone PrismQ` doesn't get submodules automatically

---

### After (add-repo-with-submodule):

```
PrismQ/                                    (git repo)
├── .git/
├── mod/
│   ├── IdeaInspiration/                   ✅ REGISTERED SUBMODULE
│   │   ├── .git/                          (git repo)
│   │   └── mod/
│   │       └── NewModule/                 ✅ REGISTERED SUBMODULE
│   │           └── .git/                  (git repo)
│   └── RepositoryTemplate/
└── .gitmodules
    [submodule "mod/IdeaInspiration"]
        path = mod/IdeaInspiration
        url = https://github.com/Nomoos/PrismQ.IdeaInspiration.git
        branch = main
    [submodule "mod/RepositoryTemplate"]
        path = mod/RepositoryTemplate
        url = https://github.com/Nomoos/PrismQ.RepositoryTemplate.git
        branch = main
```

```
PrismQ/mod/IdeaInspiration/.gitmodules
    [submodule "mod/NewModule"]                ✅ ADDED
        path = mod/NewModule
        url = https://github.com/Nomoos/PrismQ.IdeaInspiration.NewModule.git
        branch = main
```

✅ **Benefits**:
- Parent repos track exact commit of each submodule
- `git status` shows submodule changes
- `git clone --recurse-submodules PrismQ` gets everything
- Team collaboration: everyone on same submodule versions

---

## Command Comparison

### Using repo-builder (current):
```bash
python -m repo_builder PrismQ.IdeaInspiration.NewModule

# Result: Repos created, NOT as submodules
```

### Using add-repo-with-submodule (proposed):
```bash
python -m add_repo_with_submodule PrismQ.IdeaInspiration.NewModule

# Result: Repos created AND registered as submodules
```

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│  add-repo-with-submodule (NEW SCRIPT)                    │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │  cli.py                                            │  │
│  │  • Parse command line arguments                    │  │
│  │  • Call repo-builder functions                     │  │
│  │  • Call submodule operations                       │  │
│  └────────────────┬───────────────────────────────────┘  │
│                   │                                        │
│                   ├─────────────────┬─────────────────────┤
│                   ▼                 ▼                      │
│  ┌──────────────────────┐  ┌───────────────────────────┐ │
│  │ Import from          │  │ submodule_operations.py   │ │
│  │ repo-builder:        │  │ (NEW)                     │ │
│  │                      │  │                           │ │
│  │ • derive_chain()     │  │ • add_git_submodule()    │ │
│  │ • create_git_chain() │  │ • commit_changes()       │ │
│  │ • parse_url()        │  │ • init_submodule()       │ │
│  └──────────────────────┘  └───────────────────────────┘ │
│                                                            │
│  NO CHANGES TO REPO-BUILDER ✅                            │
└──────────────────────────────────────────────────────────┘
              │
              │ imports functions
              ▼
┌──────────────────────────────────────────────────────────┐
│  repo-builder (UNCHANGED)                                 │
│                                                            │
│  ┌────────────────────────────────────────────────────┐  │
│  │  • exceptions.py                                   │  │
│  │  • validation.py                                   │  │
│  │  • parsing.py                                      │  │
│  │  • display.py                                      │  │
│  │  • repository.py                                   │  │
│  │  • cli.py                                          │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## Implementation Priority (Option 1)

### Phase 1: Core Functionality
```
✅ 1. Create directory structure
✅ 2. Implement add_git_submodule()
✅ 3. Implement commit_submodule_changes()
✅ 4. Import from repo-builder
✅ 5. Wire up CLI
```

### Phase 2: Error Handling
```
✅ 6. Validate parent is git repo
✅ 7. Check if already a submodule
✅ 8. Handle git command failures
✅ 9. Rollback on error
```

### Phase 3: Testing & Documentation
```
✅ 10. Unit tests
✅ 11. Integration tests
✅ 12. README.md
✅ 13. Usage examples
```

### Future Enhancements (Optional)
```
⏭️ 14. Auto-initialize submodules
⏭️ 15. Interactive confirmation mode
⏭️ 16. Dry-run mode
⏭️ 17. Recursive validation
```
