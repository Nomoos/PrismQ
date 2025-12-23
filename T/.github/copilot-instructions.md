# PrismQ.T - Text Generation Pipeline - GitHub Copilot Instructions

> **Note**: For general project guidelines, see the [main repository's copilot instructions](../../.github/copilot-instructions.md).

## Module Context

**Namespace**: `PrismQ.T` (Text)

The Text Generation Pipeline is the **foundation** of the PrismQ content workflow. It transforms initial ideas into high-quality, published text content optimized for blogs, articles, and social media platforms.

### Workflow Position
```
IdeaInspiration → Text Pipeline → PublishedText
    ↓                                  ↓
Analytics Feedback              Audio Pipeline (A)
```

---

## Module Structure

```
T/
├── src/                      # Text foundation layer (shared utilities)
│   └── ai_config.py         # AI configuration for all Text modules
├── Idea/                    # Idea development and structuring
│   ├── Model/              # Core data model
│   ├── Outline/            # Content outline development
│   ├── Review/             # Idea validation
│   └── Inspiration/        # Raw inspiration collection (submodule)
├── Title/                   # Title-specific operations
├── Script/                  # Script drafting and refinement
│   └── From/Idea/Title/    # Script generation from ideas
├── Content/                 # Content artifacts and pipelines
│   └── From/Idea/          # Content derived from ideas
│       ├── Title/          # Title generation
│       ├── Script/         # Script generation
│       └── Description/    # Description generation
├── Publishing/              # Publishing operations
└── Story/                   # Story-specific operations
```

---

## Module Responsibilities

### What Belongs Here
- **Text Foundation** (`T/src/`) - AI configuration, shared Text utilities
- **Domain Logic** - Idea, Title, Script, Story domain operations
- **Content Generation** - Text content creation pipelines
- **Publishing** - Text content publication workflows

### What Doesn't Belong Here
- Generic cross-project utilities → Move to `src/` (root)
- Audio-specific logic → Move to `A/` (Audio module)
- Video-specific logic → Move to `V/` (Video module)

---

## Key Design Patterns

### Hierarchy Levels
1. **T/src/** - Text foundation (AI config used by Content, Publishing, Story)
2. **T/<Domain>/** - Domain-specific operations (Idea, Title, Script)
3. **T/Content/** - Content artifact operations
4. **T/Content/From/<Source>/** - Content generation from specific sources

### Dependency Flow
```
T/Content/From/Idea/Title  (most specialized)
        ↓
T/Content/From/Idea
        ↓
T/Content
        ↓
T/src (Text foundation)
        ↓
src/ (root)             (most generic)
```

### Module Distinctions
- **T/Title/** = Title domain operations (generic title logic)
- **T/Content/From/Idea/Title/** = Title content pipeline (generating titles from ideas)
- These are **different concepts** - don't confuse them!

---

## Common Operations

### Working with AI Configuration
```python
# ✅ Import from T foundation layer
from T.src.ai_config import create_ai_config

# ❌ Don't duplicate AI config in submodules
```

### Adding New Content Type
1. Determine if it's domain logic or content pipeline
2. Place in appropriate layer (domain vs. content)
3. Reuse AI config from `T/src/`
4. Follow dependency direction (specialized → generic)

### Working with Ideas
- **Idea domain** → `T/Idea/`
- **Content from Ideas** → `T/Content/From/Idea/`

---

## Integration Points

### Inputs
- Inspiration data from `T/Idea/Inspiration/`
- Analytics feedback from `M/` (Metrics module)

### Outputs
- **PublishedText** → Consumed by `A/` (Audio Pipeline)
- **Publishing data** → Sent to `P/` (Publishing module)
- **Metrics** → Reported to `M/` (Metrics module)

---

## Project Guidelines Reference

For detailed project-wide guidelines:
- **[Root Copilot Instructions](../../.github/copilot-instructions.md)** - Core principles and hierarchy
- **[Coding Guidelines](../../_meta/docs/guidelines/CODING_GUIDELINES.md)** - Module placement rules
- **[Module Hierarchy](../../_meta/docs/guidelines/MODULE_HIERARCHY_UPDATED.md)** - Dependency diagrams

### Quick Rules
1. **Dependencies**: Specialized → Generic (never reversed)
2. **AI Config**: Import from `T/src/`, don't duplicate
3. **Reusable Logic**: Move up to common parent
4. **Module Structure**: `src/` for production, `_meta/` for tests/docs

---

## Questions to Ask

When working on this module:
- Is this domain logic or content pipeline logic?
- Does this belong in Text foundation (`T/src/`) or a submodule?
- Am I following the dependency direction (specialized → generic)?
- Should I reuse AI config from `T/src/`?
- Is this Text-specific, or should it be in Audio/Video modules?
- Have I avoided duplicating logic across submodules?

---

## Module Documentation

- **[T Module README](../README.md)** - Detailed workflow and module structure
- **[Title & Script Workflow](../_meta/docs/TITLE_SCRIPT_WORKFLOW.md)** - Complete workflow guide
- **[Workflow State Machine](../_meta/docs/WORKFLOW_STATE_MACHINE.md)** - Visual state diagram
