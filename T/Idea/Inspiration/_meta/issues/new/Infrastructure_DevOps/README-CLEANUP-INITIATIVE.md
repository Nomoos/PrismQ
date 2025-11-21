# Repository Cleanup Initiative

## Overview
This directory contains a set of issues focused on cleaning up and standardizing the PrismQ.IdeaInspiration repository. These issues address documentation organization, code structure, and development workflow improvements.

## Issues Created

### Issue #200: Consolidate Redundant Documentation
**Priority**: Medium  
**Effort**: 2-3 hours  
**Status**: New

Archive historical completion summaries, status reports, and reorganization documents. These files served their purpose during development but now clutter the repository.

**Key Actions**:
- Archive 35+ historical documents to `_meta/docs/archive/`
- Preserve important information in active docs
- Create archive index for reference

### Issue #201: Organize Documentation Hierarchy
**Priority**: Medium  
**Effort**: 4-6 hours  
**Status**: New  
**Depends on**: #200

Standardize documentation structure across all modules with consistent naming and organization.

**Key Actions**:
- Standardize `docs/` vs `_meta/docs/` usage
- Create documentation indexes
- Consolidate duplicate content (VENV, database, coverage docs)
- Define clear documentation categories

### Issue #202: Standardize Module Structure and Organization
**Priority**: Medium  
**Effort**: 8-12 hours  
**Status**: New  
**Depends on**: #200, #201

Ensure all modules follow consistent structure with tests, examples, and source code properly organized.

**Key Actions**:
- Define standard module structure
- Move test files to `tests/` directories
- Move example files to `examples/` directories
- Ensure all modules have `.envrc` for direnv
- Create module template

### Issue #203: Improve and Standardize .gitignore Files
**Priority**: Low  
**Effort**: 1-2 hours  
**Status**: New

Enhance `.gitignore` to comprehensively cover Python artifacts, IDE files, and build outputs.

**Key Actions**:
- Add comprehensive Python ignore patterns
- Cover all common IDEs
- Add testing artifacts
- Add documentation build outputs
- Module-specific ignores where needed

### Issue #204: Clean Up and Organize _meta/issues Directory
**Priority**: Medium  
**Effort**: 4-6 hours  
**Status**: New  
**Depends on**: #200

Organize the issue tracking directory with better structure and clearer workflow.

**Key Actions**:
- Move summary files to appropriate archives
- Organize done/ by time period
- Create issue templates
- Document issue workflow
- Create issue index

### Issue #205: Remove Duplicate Test Files and Consolidate Test Structure
**Priority**: Medium  
**Effort**: 3-4 hours  
**Status**: New  
**Depends on**: #202

Standardize test location and structure across all modules.

**Key Actions**:
- Move all tests to `tests/` directories
- Move examples to `examples/` directories
- Add pytest configuration
- Create TESTING.md guide
- Ensure all tests still pass

### Issue #206: Standardize Python Configuration Files
**Priority**: Low  
**Effort**: 4-6 hours  
**Status**: New

Adopt modern Python packaging with `pyproject.toml` and consistent tool configuration.

**Key Actions**:
- Create standard `pyproject.toml` template
- Migrate from `setup.py` where possible
- Centralize tool configurations
- Update installation docs

### Issue #207: Standardize README Files as Navigation Hubs and Deduplicate
**Priority**: Medium  
**Effort**: 4-6 hours  
**Status**: New  
**Depends on**: #200, #201

Ensure README files serve as navigation hubs with highlights only, moving detailed content to docs/ and eliminating duplication.

**Key Actions**:
- Define README template (navigation + highlights only)
- Move detailed content from READMEs to docs/ files
- Deduplicate README vs docs/ content
- Ensure single source of truth for each topic
- Update all module READMEs to follow standard

## Implementation Order

### Phase 1: Documentation Cleanup (Low Risk)
1. **Issue #200** - Archive historical docs (2-3 hours)
2. **Issue #203** - Improve .gitignore (1-2 hours)

### Phase 2: Documentation Organization (Medium Risk)
3. **Issue #201** - Organize documentation hierarchy (4-6 hours)
4. **Issue #207** - Standardize READMEs as navigation hubs (4-6 hours)
5. **Issue #204** - Clean up issues directory (4-6 hours)

### Phase 3: Code Structure (Higher Risk - Needs Testing)
6. **Issue #202** - Standardize module structure (8-12 hours)
7. **Issue #205** - Consolidate test structure (3-4 hours)
8. **Issue #206** - Standardize Python configuration (4-6 hours)

## Total Estimated Effort
30-45 hours

## Parallelization Strategy

### 🔀 Issues That Can Be Done in Parallel

Based on dependencies, here's how work can be parallelized:

**Wave 1 (Can start immediately, work in parallel):**
- ✅ **Issue #200** - Archive historical docs (no dependencies)
- ✅ **Issue #203** - Improve .gitignore (no dependencies)

**Wave 2 (After #200 is complete, these can be done in parallel):**
- ✅ **Issue #201** - Organize documentation hierarchy (depends on #200)
- ✅ **Issue #204** - Clean up issues directory (depends on #200)

**Wave 3 (After #200 and #201 are complete, can be done in parallel):**
- ✅ **Issue #207** - Standardize READMEs as navigation hubs (depends on #200, #201)
- ✅ **Issue #202** - Standardize module structure (depends on #200, #201)
- ⚠️ **Issue #206** - Standardize Python configuration (no dependencies, but coordinate with #202)

**Wave 4 (After #202 is complete):**
- ✅ **Issue #205** - Consolidate test structure (depends on #202)

### Optimal Parallel Execution Plan

**For maximum efficiency with 2-3 people:**

**Week 1:**
- Person A: Issue #200 (2-3 hours)
- Person B: Issue #203 (1-2 hours) → then start preparing for #201
- Total: 3-5 hours

**Week 2:**
- Person A: Issue #201 (4-6 hours)
- Person B: Issue #204 (4-6 hours)
- Total: 8-12 hours (parallel)

**Week 3:**
- Person A: Issue #207 (4-6 hours)
- Person B: Issue #202 (8-12 hours)
- Person C (optional): Issue #206 (4-6 hours)
- Total: 8-12 hours with 2 people, faster with 3

**Week 4:**
- Person A or B: Issue #205 (3-4 hours)
- If Person C worked on #206, it's already done
- Otherwise: Issue #206 (4-6 hours)
- Total: 3-8 hours

**Total Time with Parallelization:**
- With 1 person: 30-45 hours
- With 2 people: ~16-25 hours
- With 3 people: ~12-18 hours

### Dependency Graph

```
#200 (Archive docs)          #203 (.gitignore)
    │                            │
    ├──────────┬─────────────────┘
    │          │
    ▼          ▼
  #201       #204
   │
   ├──────────┬──────────┐
   │          │          │
   ▼          ▼          ▼
 #207      #202        #206*
           │
           ▼
         #205

* #206 has no dependencies but should coordinate with #202
```

### Key Parallelization Notes

1. **#200 is the critical path** - Blocks #201, #204, #207, and #202
2. **#203 is independent** - Can be done anytime, good for quick win
3. **#201 and #204 are independent** after #200 - Perfect for parallel work
4. **#202 and #207 can overlap** - Different parts of the repository
5. **#206 is flexible** - No dependencies, but easier after #202 is complete
6. **#205 must wait for #202** - Directly depends on module structure being standardized

### Recommendations

- **Quick Win First**: Start with #203 while planning #200
- **Foundation Second**: #200 is critical path, prioritize it
- **Parallel Documentation Work**: #201, #204, #207 can all be done by different people
- **Careful with Code Changes**: #202, #205, #206 need testing - don't rush
- **Coordinate #202 and #206**: Both touch module configuration, communicate if done in parallel

## Benefits

### Immediate Benefits
- Cleaner repository structure
- Easier navigation
- Better onboarding for new contributors
- Reduced confusion

### Long-term Benefits
- Consistent development experience
- Better maintainability
- Easier CI/CD configuration
- Professional presentation
- Scalable structure for growth

## Success Metrics

- [ ] Repository size reduced (fewer redundant docs)
- [ ] Consistent structure across all modules
- [ ] Clear documentation hierarchy
- [ ] All tests passing
- [ ] No tracked files that should be ignored
- [ ] Standard templates for modules and issues
- [ ] Improved developer experience

## Notes

- These issues can mostly be done independently
- Issues #200 and #203 are good starting points (low risk)
- Structure changes (#202, #205, #206) need careful testing
- Consider doing one module at a time for structure changes
- All changes should be reviewed before finalizing

## Getting Started

**Recommended First Steps**:
1. Start with Issue #203 (gitignore) - quick win, low risk
2. Then Issue #200 (archive docs) - cleanup with immediate benefit
3. Then proceed to other issues in order

**For Each Issue**:
1. Read the full issue description
2. Review files affected
3. Create a branch
4. Make changes incrementally
5. Test thoroughly
6. Create PR for review
