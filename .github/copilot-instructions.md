# GitHub Copilot Instructions for PrismQ

## ⚠️ CRITICAL: Single Shared Database

**PrismQ uses ONE shared database (db.s3db) for ALL modules.**

- **Database File**: `C:/PrismQ/db.s3db` (or working directory)
- **All Tables**: Idea, Story, Title, Content, Publishing, Analytics - ALL in ONE database
- **DO NOT**: Create multiple databases or separate database files
- **DO NOT**: Create new database connections per operation - reuse existing connections
- **Connection Management**: Setup once at initialization, reuse across operations, close on exit

This is documented in:
- `src/__init__.py` (line 12): "Shared database (db.s3db) for all content storage"
- `src/startup.py`: DatabaseConfig for single database path
- Module docstrings: IMPORTANT warnings about single database

When working with database code:
1. Always check if a database connection already exists
2. Reuse existing connections instead of creating new ones
3. Document that the connection is to the shared db.s3db
4. Never create separate databases for different modules

---

## 🎯 Core Principles

### 1. Make Small, Surgical Changes
- Make the smallest possible changes to accomplish the task
- Avoid unnecessary modifications to unrelated code
- Keep changes focused and surgical
- Follow the existing code style and patterns

### 2. Ask When Uncertain About Location
- If you cannot find a module or are unsure where to make changes, ask the user
- Do not guess or make assumptions about file locations
- Use clarification language when asking, for example:
  - "Could you please clarify which module should be modified?"
  - "I'd like to understand better where this change should be made."
  - "To ensure I make the correct changes, could you specify the file path?"

### 3. Always Ask When Uncertain
- When in doubt about any aspect of the task, ask the user for clarification
- Do not make assumptions that could lead to incorrect implementations
- Use clarification language in questions, for example:
  - "Could you please elaborate on the expected behavior?"
  - "I want to make sure I understand correctly - does this mean...?"
  - "To clarify, should the implementation include...?"

---

## 📚 Essential Documentation

**Before making changes, review these core documents:**

### Module Structure & Architecture
- **[Coding Guidelines](../_meta/docs/guidelines/CODING_GUIDELINES.md)** - Module hierarchy, placement rules, dependency direction
- **[Module Hierarchy](../_meta/docs/guidelines/MODULE_HIERARCHY_UPDATED.md)** - Detailed hierarchy and dependency diagrams
- **[PR Review Checklist](../_meta/docs/guidelines/PR_CODE_REVIEW_CHECKLIST.md)** - Required verification before merging

### Quick Reference
- **[README.md](../README.md)** - Project overview and module navigation
- **[Workflow Documentation](../_meta/WORKFLOW.md)** - State machine and workflow processes

---

## 🏗️ Module Structure Convention

Every module follows this layout:
```
module/
├── src/        # Production source code only (runtime code)
├── _meta/      # Tests, docs, examples, scripts, auxiliary files
```

**Critical Rules:**
- `src/` contains **only runtime code** - never tests, scripts, or tooling
- `_meta/` contains everything else - tests, documentation, issue tracking, scripts
- Production code must **never** import from `_meta/`

---

## 📐 Module Hierarchy & Placement

### Decision Tree: Where Does Code Belong?

Follow this order when deciding code placement:

1. **Generic across entire project?** → `src/` (root level)
   - Example: Database configuration, environment setup

2. **Shared across multiple Text domains?** → `T/src/` (Text foundation)
   - Example: AI configuration used by Content, Publishing, Story

3. **Specific to a Text domain?** → `T/<Domain>/`
   - Example: `T/Idea/`, `T/Title/`, `T/Story/`, `T/Publishing/`

4. **About content artifacts?** → `T/Content/`
   - Example: AI for content generation, content processing utilities

5. **Content from a specific source?** → `T/Content/From/<Source>/`
   - Example: Content from Ideas → `T/Content/From/Idea/`

6. **Most specialized behavior?** → Deepest module (leaf)
   - Example: Title generation from Idea → `T/Content/From/Idea/Title/`

### Namespace Shortcuts (IMPORTANT!)
- Use `T` for `Text` (not `PrismQ.Text`)
- Use `A` for `Audio` (not `PrismQ.Audio`)
- Use `V` for `Video` (not `PrismQ.Video`)
- Shortcuts are the **official namespaces** - never use long forms

---

## 🔄 Dependency Rules

**Critical: Dependencies flow specialized → generic (NEVER reversed)**

✅ **Allowed:**
- Specialized modules → Generic modules
- `T/Content/From/Idea/Title/` → `T/Content/`
- `T/Content/` → `T/src/`
- `T/Idea/` → `src/`

❌ **Not Allowed:**
- Generic modules → Specialized modules
- `src/` → `T/Content/`
- `T/Content/` → `T/Content/From/Idea/Title/`

### Reusability Rule
- If functionality is needed in multiple places, **move it up** to the nearest common parent
- Never duplicate reusable logic in specialized modules
- Prefer lifting logic upward over copying it downward

---

## 🎨 Design Principles

### SOLID Principles
- **Single Responsibility**: Each module has exactly one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Subtypes must be substitutable for base types
- **Interface Segregation**: Use focused, minimal interfaces (Python Protocols)
- **Dependency Inversion**: Depend on abstractions, inject dependencies

### Additional Principles
- **DRY**: Don't Repeat Yourself - eliminate duplication
- **KISS**: Keep It Simple - favor simplicity over complexity
- **YAGNI**: You Aren't Gonna Need It - implement only what's needed now
- **Composition Over Inheritance**: Prefer object composition to class inheritance

---

## ⚠️ Common Pitfalls to Avoid

1. **Wrong Abstraction Level**: Placing generic logic in specialized modules
2. **Side Effects at Import**: No I/O, network, or resource initialization during import
3. **Circular Dependencies**: Never allowed - respect dependency direction
4. **Duplicated Logic**: Always move shared code to common parent
5. **Import from _meta/**: Production code must never import from `_meta/`
6. **Using Long Namespaces**: Use shortcuts (`T`, not `PrismQ.Text`)

---

## ✅ Before Committing

Verify your changes meet these requirements:

- [ ] Code is in the **correct abstraction layer** (use placement decision tree)
- [ ] Dependencies follow **specialized → generic** direction
- [ ] No side effects at import time
- [ ] Reusable logic is in the **common parent**, not duplicated
- [ ] Module structure follows `src/` and `_meta/` convention
- [ ] Production code does not import from `_meta/`
- [ ] Tests are in `_meta/` directory
- [ ] Documentation is updated if needed

---

## 🔍 Code Style

### Python Specifics
- Follow PEP 8 style guide
- Use type hints for all function parameters and return values
- Write comprehensive docstrings (Google style)
- Keep functions under 50 lines when possible
- No side effects at import time (use lazy imports if needed)

### Example - Lazy Import Pattern
```python
# ✅ Good: No side effects at import
def check_ollama_available():
    import requests  # Lazy import
    return requests.get("http://localhost:11434/api/tags")

# ❌ Bad: Side effect at import time
import requests
ollama_status = requests.get("http://localhost:11434/api/tags")
```

---

## 📞 Getting Help

- Check module-specific instructions in module's `.github/copilot-instructions.md`
- Review detailed guidelines in `_meta/docs/guidelines/`
- When uncertain, **always ask the user** before making assumptions
