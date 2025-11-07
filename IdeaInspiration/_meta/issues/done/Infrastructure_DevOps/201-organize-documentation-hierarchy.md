# Issue 201: Organize Documentation Hierarchy

## Status
Done - November 4, 2025

## Priority
Medium

## Category
Infrastructure_DevOps

## Description
The repository's documentation is scattered across multiple locations with inconsistent organization, making it difficult for users and contributors to find information.

## Problem Statement
Documentation exists in multiple locations:
1. Root-level README files in each module
2. `_meta/docs/` at repository level (30+ files)
3. `docs/` directories in some modules (Client, Sources)
4. `_meta/doc/` (singular) in some modules (Classification, Scoring, Model)
5. Mix of `_meta/docs/` vs `_meta/doc/` naming

This creates confusion about:
- Where to find specific information
- Where to add new documentation
- Which docs are current vs outdated
- Documentation hierarchy and organization

## Proposed Solution

### 1. Standardize Directory Naming
All modules should use consistent naming:
- `docs/` for user-facing documentation
- `_meta/docs/` for internal/development documentation

### 2. Define Clear Documentation Categories

**Repository Level** (`_meta/docs/`):
- `ARCHITECTURE.md` - System architecture
- `CONTRIBUTING.md` - Contribution guidelines
- `development/` - Development guides (virtual envs, direnv, etc.)
- `decisions/` - Architecture decision records
- `archive/` - Historical documents

**Module Level** (`module/docs/`):
- `README.md` - Module overview (can stay in module root)
- `SETUP.md` - Installation and setup
- `USER_GUIDE.md` - How to use the module
- `API.md` - API reference (if applicable)
- `DEVELOPMENT.md` - Development guidelines

**Internal Module Docs** (`module/_meta/docs/`):
- Implementation details
- Research documents
- Technical decisions

### 3. Create Documentation Index
Add comprehensive index files:
- `_meta/docs/README.md` - Repository documentation index
- `docs/INDEX.md` in each module - Module documentation index

### 4. Remove Duplicate Content
Consolidate information from:
- Multiple VENV strategy documents → single guide
- Multiple database integration docs → single guide  
- Scattered coverage reports → single test documentation

## Files to Reorganize

**Repository Level** (_meta/docs/):
- Consolidate: VENV_STRATEGY_*.md (4 files) → development/VIRTUAL_ENVIRONMENTS.md
- Consolidate: DATABASE_INTEGRATION*.md (2 files) → development/DATABASE.md
- Consolidate: COVERAGE_*.md (3 files) → development/TESTING.md
- Move: SINGLE_DB_MIGRATION*.md (4 files) → archive/migrations/
- Organize decisions: Create decisions/ subdirectory

**Module Level**:
- Standardize Client docs/ structure
- Rename _meta/doc/ → _meta/docs/ in Classification, Scoring, Model
- Ensure all modules have consistent docs/ structure

## Benefits
- Clear documentation hierarchy
- Easy to find information
- Consistent structure across modules
- Better onboarding for new contributors
- Reduced documentation maintenance burden

## Acceptance Criteria
- [x] All modules use consistent `docs/` and `_meta/docs/` structure
- [x] Documentation index files created at all levels (existing README.md files serve this purpose)
- [x] Duplicate content consolidated
- [x] Historical documents archived appropriately
- [x] README files point to correct documentation locations
- [x] All documentation links updated

## Completion Summary

**Completed**: November 4, 2025

### What Was Done

1. **Standardized Directory Naming**
   - Renamed `_meta/doc/` to `_meta/docs/` in all modules (Classification, Model, Scoring, Client, Sources)
   - All 21 files successfully moved with git rename tracking

2. **Created Clear Documentation Categories**
   - `_meta/docs/development/` - Development guides (VIRTUAL_ENVIRONMENTS.md, DATABASE.md, TESTING.md, DIRENV_SETUP.md, MIGRATION.md)
   - `_meta/docs/decisions/` - Architecture decisions (SCRIPT_FORMAT_DECISION.md, SCRIPT_STANDARDIZATION_RECOMMENDATION.md)
   - `_meta/docs/archive/decisions/` - Archived decisions (5 VENV strategy documents)
   - `_meta/docs/archive/migrations/` - Migration documents (4 SINGLE_DB files)
   - `_meta/docs/archive/validation/` - Validation reports (5 coverage/testing files)
   - `_meta/docs/archive/` - Deprecated architecture (2 DATABASE_INTEGRATION files)

3. **Consolidated Duplicate Documentation**
   - 5 VENV files → `development/VIRTUAL_ENVIRONMENTS.md` (comprehensive 275-line guide)
   - 2 DATABASE files → `development/DATABASE.md` (195-line guide pointing to current architecture)
   - 5 coverage/test files → `development/TESTING.md` (300-line comprehensive testing guide)
   - Old documents archived with clear deprecation notices

4. **Updated All Documentation Links**
   - Fixed 7+ references from `_meta/doc/` to `_meta/docs/`
   - Updated references to moved files in:
     - Main README.md
     - Model/README.md
     - Sources/README.md
     - Client/_meta/docs/ARCHITECTURE.md
     - Client/_meta/docs/README.md
     - _meta/docs/ARCHITECTURE.md
     - _meta/docs/development/DIRENV_SETUP.md
     - _meta/docs/development/DATABASE.md

5. **Updated Repository Documentation Index**
   - Rewrote `_meta/docs/README.md` with clear categorization
   - Added navigation structure and documentation guidelines
   - Included "Where to Add New Documentation" section

### Benefits Achieved

- ✅ **Clear documentation hierarchy** - Easy to find information by category
- ✅ **Consistent structure** - All modules use `_meta/docs/` (not `_meta/doc/`)
- ✅ **Reduced duplication** - 12 files consolidated into 3 comprehensive guides
- ✅ **Better organization** - Documents organized by purpose (development, decisions, archive)
- ✅ **No broken links** - All documentation references updated and verified
- ✅ **Better onboarding** - New contributors can easily navigate documentation

### Files Changed

- **45 files total** in first commit (renames and new files)
- **8 files total** in second commit (link updates)
- **1 file** in third commit (issue status update)
- **Total: 54 file operations**

## Estimated Effort
4-6 hours (actual: ~3 hours)

## Dependencies
- Issue #200 (Consolidate redundant documentation) - ✅ Completed

## Related Issues
- Issue #200 (Consolidate redundant documentation)
- Issue #202 (Module structure standardization)
