# Coding Guidelines – Module Design & Responsibilities

## 1. Core principles

- Each module must have **a single, clearly defined responsibility**.
- The codebase is organized into **layers of abstraction**.
- **Generic functionality belongs higher** in the hierarchy.
- **Specialized functionality belongs lower** in the hierarchy.
- A module must **not contain logic that belongs to a different layer**.

---

## 2. Namespace shortcuts (top-level aliases)

### Why shortcuts exist
Top-level namespaces can become too long. To keep names readable, we use **shortcuts only at the top level**.

### Shortcut rule
- Use **short namespaces** like `PrismQ.T`, `PrismQ.A`, etc.
- Do **not** use the long explicit versions in code or module names.

### Meaning of shortcuts
- `PrismQ.T` = **PrismQ.Text**
- `PrismQ.A` = **PrismQ.Audio**
- (Same idea applies to other top-level domains.)

> The shortcuts are the **official public namespaces**.
> The explicit long names must not appear in imports, package names, or documentation.

---

## 3. Naming & structure conventions

### Namespace-to-folder mapping
- Folder paths mirror namespace segments.
- Example:
  - `T/Content/From/Idea/Title` → `PrismQ.T.Content.From.Idea.Title`

### Module layout
Each module follows the same internal structure:

```
module/
├── src/        # Production source code only
├── _meta/      # Tests, issues, scripts, docs, tooling
```

- `src/` must contain **only runtime code**.
- `_meta/` must not be imported by production code.

---

## 4. Layer responsibilities (example shown for Text: `PrismQ.T`)

### `src / PrismQ`
- The **most generic** utilities used across the entire project.
- No domain assumptions (no Text/Audio/Content concepts).
- Examples: Database configuration, environment config

### `PrismQ.T` (Text foundation)
- Shared **foundation for Text modules**.
- Base types, primitives, and utilities used by multiple `PrismQ.T.*` modules.
- Currently: No foundation layer implemented (future extension point)

---

## 5. Domain modules under `PrismQ.T.*`

### Rule of thumb
- `PrismQ.T.<Domain>` contains logic **specific to that domain**, but **generic within the domain**.
- If logic is shared across multiple Text domains, move it **up** to `PrismQ.T` (or to `PrismQ` if fully cross-cutting).

### Examples (non-exhaustive)

- **`PrismQ.T.Idea`** (`T/Idea/`)
  Core Idea model and operations (validation, transformations, workflows).

- **`PrismQ.T.Title`** (`T/Title/`)
  Title concept operations (rules, validation, title utilities).

- **`PrismQ.T.Story`** (`T/Story/`)
  Story concept operations (structure, segmentation, transformations).

- **`PrismQ.T.Publishing`** (`T/Publishing/`)
  Publishing concept operations (scheduling, platform abstractions, publishing rules).

> Additional domains follow the same rules.

---

## 6. Cross-cutting "Content" subtree (`PrismQ.T.Content.*`)

Use `PrismQ.T.Content.*` when logic concerns **content artifacts or pipelines** (processing, conversion, storage),
especially when it spans multiple domains.

- **`PrismQ.T.Content`** (`T/Content/`)
  Generic functionality for working with content artifacts, independent of origin.
  - **AI configuration** (`T/Content/src/ai_config.py`) - for content generation
  - Content processing utilities
  - Generation helpers

- **`PrismQ.T.Content.From`** (`T/Content/From/`)
  Shared functionality for content derived from a source.

- **`PrismQ.T.Content.From.Idea`** (`T/Content/From/Idea/`)
  Shared logic for all content derived from an Idea.

- **`PrismQ.T.Content.From.Idea.Title`** (`T/Content/From/Idea/Title/`)
  Title-specific content logic derived from an Idea.

### Important distinction
- `PrismQ.T.Title` = Title **domain operations** (generic title logic)
- `PrismQ.T.Content.From.Idea.Title` = Title **content pipeline** (generating titles from ideas)

These are **different concepts** and should not be confused!

---

## 7. Placement rules (decision order)

Follow this decision tree to determine where code belongs:

1. **Is it generic across the whole project?**  
   → `PrismQ` (`src/`)
   - Example: Database configuration, environment setup

2. **Is it shared across multiple Text domains?**  
   → `PrismQ.T` (`T/src/`) - *Future foundation layer*

3. **Is it specific to a Text domain (Idea / Title / Story / Publishing)?**  
   → `PrismQ.T.<Domain>` (`T/<Domain>/`)
   - Example: Idea validation → `T/Idea/`

4. **Is it about content artifacts rather than the domain itself?**  
   → `PrismQ.T.Content` (`T/Content/`)
   - Example: AI for content generation → `T/Content/src/ai_config.py`

5. **Is it specific to content derived from a particular source?**  
   → `PrismQ.T.Content.From.<Source>` (`T/Content/From/<Source>/`)
   - Example: Content from Ideas → `T/Content/From/Idea/`

6. **Is it the most specialized behavior?**  
   → Deepest module (leaf)
   - Example: Title generation from Idea → `T/Content/From/Idea/Title/`

---

## 8. Dependency rules

- Dependencies must flow **from specialized → generic** (leaf → root).
- Higher-level modules must **not depend on lower-level modules**.
- Lower-level modules **may depend on higher-level modules**.
- Circular dependencies are **not allowed**.

### Dependency diagram (Text domain)

```
PrismQ.T.Content.From.Idea.Title  (most specialized)
            ↓
PrismQ.T.Content.From.Idea
            ↓
PrismQ.T.Content.From
            ↓
PrismQ.T.Content
            ↓
PrismQ.T (Text foundation)
            ↓
PrismQ (src/)                    (most generic)
```

### Examples

**✅ Allowed:**
- `PrismQ.T.Content.From.Idea.Title` → `PrismQ.T.Content`
- `PrismQ.T.Content` → `PrismQ` (`T/Content/` imports from `src/`)
- `PrismQ.T.Idea` → `PrismQ`

**❌ Not Allowed:**
- `PrismQ` → `PrismQ.T` (generic → specialized)
- `PrismQ.T.Content` → `PrismQ.T.Content.From.Idea.Title` (generic → specialized)

---

## 9. Reusability rule

- If functionality is needed in more than one place, **move it up** to the nearest common parent module.
- Do not duplicate reusable logic in specialized modules.
- Prefer lifting logic upward over copying it downward.

### Example
If both `T/Content/From/Idea/Title/` and `T/Content/From/Idea/Script/` need the same AI temperature function:
- ❌ Don't duplicate in both modules
- ✅ Move it up to `T/Content/From/Idea/` or `T/Content/` (depending on scope)

---

## 10. Import & initialization rules

- **No side effects at import time**.
- No I/O, network, or resource initialization during import.
- Initialization and wiring belongs in the **composition root** (main function).
- Use lazy imports when necessary (import inside functions).

### Example

**❌ Bad:**
```python
# module imports trigger network call
import requests
ollama_status = requests.get("http://localhost:11434/api/tags")
```

**✅ Good:**
```python
# No side effects at import
def check_ollama_available():
    import requests  # Lazy import
    return requests.get("http://localhost:11434/api/tags")
```

---

## 11. Current implementation status

### ✅ What's already correct

1. **Namespace shortcuts**: Using `T/` for Text domain
2. **Module structure**: Using `src/` and `_meta/` convention
3. **Dependency direction**: Specialized → generic flow verified
4. **AI configuration placement**: Correctly at `T/Content/src/ai_config.py`
5. **Domain separation**: 
   - `T/Title/` for title domain operations
   - `T/Content/From/Idea/Title/` for title content pipeline
6. **Cross-cutting concerns**: Database config at `src/` level

### 🔄 Future extensions

1. **Foundation layer**: `T/src/` for shared Text utilities (not yet needed)
2. **Other domains**: Audio (`A/`), Video, etc. (when needed)

---

## 12. Code review checklist

Before merging, verify that:

- [ ] Changes work **after merge** (build, run, tests).
- [ ] Code is placed in the **correct abstraction layer**.
- [ ] No generic logic exists in specialized leaf modules.
- [ ] Dependencies follow the allowed direction (specialized → generic).
- [ ] Reusable logic is lifted to the proper parent.
- [ ] No circular dependencies were introduced.
- [ ] No side effects at import time.
- [ ] Module structure follows `src/` and `_meta/` convention.

---

## 13. Guiding principle

> **Write code where it logically belongs — not where it was first needed.**

Each module should have exactly one responsibility and know exactly one thing — nothing more, nothing less.

---

## Related Documentation

- `MODULE_HIERARCHY_UPDATED.md` - Detailed hierarchy and dependency diagrams
- `IMPLEMENTATION_SUMMARY.md` - Implementation details for startup infrastructure
- `VERIFICATION_REPORT.md` - Verification results after merge
