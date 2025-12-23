# PR / Code Review Checklist

## 1. Merge & Stability

- [ ] The code builds successfully **after merging** into the target branch.
- [ ] The application runs correctly in the integrated state (not only on the feature branch).
- [ ] Tests pass after the merge (unit, integration, or smoke tests as applicable).

---

## 2. Module Responsibility & Layering

- [ ] Each module contains **only functionality appropriate to its level**.
- [ ] Lower-level modules do **not** contain generic or reusable logic.
- [ ] Shared logic is placed in the **highest reasonable module**.
- [ ] No duplicated generic functionality across modules.
- [ ] Dependency direction is respected (lower → higher only).

---

## 3. Namespace & Structure Consistency

> The following is **an example for a single module hierarchy**.  
> The same principles must be applied consistently across **all modules**, not only this one.

- [ ] Namespace and folder structure reflect the **exact responsibility level** of the module.
- [ ] Higher-level namespaces contain **broader, reusable functionality**.
- [ ] Lower-level namespaces contain **only specialized logic**.
- [ ] No generic logic exists in deeply nested namespaces.
- [ ] If logic applies to more than one sibling module, it is **moved up** one level.

### Example hierarchy (illustrative only):

```
PrismQ (src/)
├─ Cross-cutting functionality (database, config)
└─ Used by all domains

PrismQ.T (T/src/)
├─ Text foundation (AI config, shared utilities)
└─ Used by all Text domains

PrismQ.T.Content (T/Content/)
├─ Generic content handling
└─ Re-exports from T/src where appropriate

PrismQ.T.Content.From (T/Content/From/)
├─ Shared source-derived logic
└─ Independent of specific sources

PrismQ.T.Content.From.Idea (T/Content/From/Idea/)
├─ Logic common to all Idea-derived content
└─ Used by Title, Script, Description, etc.

PrismQ.T.Content.From.Idea.Title (T/Content/From/Idea/Title/)
└─ Title-specific functionality only
```

**Verification for this PR:**
- `src/startup.py` → Database config (cross-cutting) ✓
- `T/src/ai_config.py` → AI config (Text foundation, used by Content/Publishing/Story) ✓
- `T/Content/src/ai_config.py` → Re-exports from T/src (no duplication) ✓
- `T/Content/From/Idea/Title/` → Uses T/src (correct dependency direction) ✓

---

## 4. Module Layout

- [ ] Each module has a `src/` directory containing **only production code**.
- [ ] Each module has a `_meta/` directory for:
  - Tests
  - Issue tracking artifacts
  - Maintenance scripts
  - Documentation and auxiliary artifacts
- [ ] No test or tooling code leaks into `src/`.

---

## 5. Design & Maintainability

- [ ] Responsibilities are clear and easy to explain.
- [ ] New functionality is easy to extend without modifying unrelated modules.
- [ ] Public APIs are minimal and intentional.
- [ ] Naming clearly reflects responsibility and abstraction level.

---

## 6. Configuration & Side Effects

- [ ] No side effects at import time (I/O, network, DB connections).
- [ ] Configuration is injected, not hard-coded.
- [ ] Startup logic is separated from business logic.

**Verification for this PR:**
- Database config: Lazy loading, no side effects at import ✓
- AI config: Lazy loading (requests imported only when check_ollama_available called) ✓
- Composition root pattern: create_database_config, create_ai_config ✓

---

## 7. Testability

- [ ] Code can be tested in isolation.
- [ ] Dependencies are explicit and replaceable.
- [ ] New behavior is covered by tests (where appropriate).

**Tests for this PR:**
- `test_startup_infrastructure.py` - Infrastructure tests ✓
- `test_ai_hierarchy.py` - Module hierarchy verification ✓
- `example_best_practices.py` - Usage examples ✓

---

## Final Gate

- [ ] This PR **does not introduce functionality at the wrong abstraction level**.
- [ ] This PR **moves shared logic upward** instead of copying it downward.
- [ ] This PR keeps the architecture **cleaner than before**.

**Verification for this PR:**
- AI config moved from `T/Content/` → `T/src/` (upward, not downward) ✓
- Single source of truth at T foundation level ✓
- No duplication across Text domains (Content, Publishing, Story) ✓
- Architecture improvement: eliminated future duplication ✓

---

## Status for This PR

### ✅ All Checklist Items Verified

1. **Merge & Stability**: Builds, runs, tests pass ✓
2. **Module Responsibility**: Correct layering (src → T/src → T/Content → Title) ✓
3. **Namespace Structure**: Matches responsibility level exactly ✓
4. **Module Layout**: src/ and _meta/ convention followed ✓
5. **Design**: Clear responsibilities, maintainable ✓
6. **Configuration**: No side effects, lazy loading ✓
7. **Testability**: Comprehensive tests, explicit dependencies ✓
8. **Final Gate**: Correct abstraction levels, logic moved upward ✓

### Test Results

```
✅ AI config at T/src (foundation level)
✅ T/Content re-exports from T/src
✅ Title module uses T/src
✅ Single source of truth confirmed
```

### Key Achievement

AI configuration correctly placed at **T foundation level** (T/src/ai_config.py) where it belongs for cross-domain usage, rather than at T/Content level. This eliminates duplication across Text domains (Content, Publishing, Story) and establishes proper abstraction hierarchy.

**Ready for merge.**
