# Module Naming Rules

## Overview

This document defines the **canonical naming convention** for all PrismQ modules, states, and paths.

## Core Principle

**State names directly mirror directory paths under the project root.**

```
Directory Path → Module/State Name
```

## Naming Pattern

```
PrismQ.<ContentType>.<What>.<From>.<Source>.<Context>
```

### Components:

1. **PrismQ** - Project name (always present)
2. **ContentType** - Type of content being processed:
   - `T` = Text
   - `A` = Audio  
   - `V` = Video
   - `M` = Metrics
3. **What** - What artifact we create:
   - `Content` - Text/script content
   - `Title` - Titles
   - `Idea` - Ideas
   - `Story` - Stories
   - `Review` - Reviews
4. **From** - Indicates source-based creation (optional)
5. **Source** - What we create from, in creation order:
   - `Idea` → `Title` → `Content` → `Review` → `Story`
6. **Context** - Additional contextual elements in creation order

## Examples

### Basic Examples

| Directory Path | Module/State Name |
|----------------|-------------------|
| `T/Idea/From/User/` | `PrismQ.T.Idea.From.User` |
| `T/Story/From/Idea/` | `PrismQ.T.Story.From.Idea` |
| `T/Title/From/Idea/` | `PrismQ.T.Title.From.Idea` |
| `T/Content/From/Idea/Title/` | `PrismQ.T.Content.From.Idea.Title` |

### Review Examples

| Directory Path | Module/State Name |
|----------------|-------------------|
| `T/Review/Title/From/Content/` | `PrismQ.T.Review.Title.From.Content` |
| `T/Review/Content/From/Title/` | `PrismQ.T.Review.Content.From.Title` |
| `T/Review/Title/From/Content/Idea/` | `PrismQ.T.Review.Title.From.Content.Idea` |
| `T/Review/Content/From/Title/Idea/` | `PrismQ.T.Review.Content.From.Title.Idea` |

### Refinement Examples

| Directory Path | Module/State Name |
|----------------|-------------------|
| `T/Content/From/Title/Content/Review/` | `PrismQ.T.Content.From.Title.Content.Review` |
| `T/Title/From/Title/Title/Review/Content/` | `PrismQ.T.Title.From.Title.Title.Review.Content` |

## Creation Order

When multiple sources are involved, they appear in **creation order**:

```
Idea → Title → Content → Review → Story
```

### Examples of Creation Order:

1. **Content from Idea and Title:**
   - Directory: `T/Content/From/Idea/Title/`
   - State: `PrismQ.T.Content.From.Idea.Title`
   - Meaning: Content created from Idea first, then Title

2. **Title from Title (refinement) with Content review:**
   - Directory: `T/Title/From/Title/Review/Content/`
   - State: `PrismQ.T.Title.From.Title.Review.Content`
   - Meaning: Title refined from previous Title, using Content Review

3. **Review Title using Content and Idea:**
   - Directory: `T/Review/Title/From/Content/Idea/`
   - State: `PrismQ.T.Review.Title.From.Content.Idea`
   - Meaning: Review of Title based on Content (created first) and Idea (original source)

## Conversion Rules

### Directory → State Name

1. Take the full directory path under project root
2. Replace `/` with `.`
3. Prefix with `PrismQ`

**Example:**
```
T/Content/From/Idea/Title/
→ T.Content.From.Idea.Title
→ PrismQ.T.Content.From.Idea.Title
```

### State Name → Directory Path

1. Remove `PrismQ.` prefix
2. Replace `.` with `/`
3. Add trailing `/`

**Example:**
```
PrismQ.T.Content.From.Idea.Title
→ T.Content.From.Idea.Title
→ T/Content/From/Idea/Title/
```

## Important Distinctions

### Domain vs Pipeline

Different modules serve different purposes:

| Type | Example | Purpose |
|------|---------|---------|
| Domain Operations | `PrismQ.T.Title` | Generic title logic and operations |
| Content Pipeline | `PrismQ.T.Content.From.Idea.Title` | Title generation from ideas |

**These are different concepts!**
- `T/Title/` = Title domain (generic title operations)
- `T/Content/From/Idea/Title/` = Title content pipeline (creating titles from ideas)

## Validation Checklist

When documenting states or modules:

- [ ] State name matches directory path exactly
- [ ] All path segments present in state name
- [ ] Components in correct creation order
- [ ] Using correct content type shortcut (T, A, V, M)
- [ ] No abbreviations except official shortcuts
- [ ] Path ends with `/` in documentation
- [ ] State name prefixed with `PrismQ.`

## Common Mistakes

### ❌ Wrong: Using "By" instead of "From"

```
PrismQ.T.Review.Title.ByContent ❌
```

**Correct:**
```
PrismQ.T.Review.Title.From.Content ✓
```

### ❌ Wrong: Wrong creation order

```
PrismQ.T.Content.From.Title.Idea ❌
(implies Title was created before Idea)
```

**Correct:**
```
PrismQ.T.Content.From.Idea.Title ✓
(Idea → Title → Content)
```

### ❌ Wrong: Missing path segments

```
PrismQ.T.Content.Title ❌
(missing From/Idea)
```

**Correct:**
```
PrismQ.T.Content.From.Idea.Title ✓
```

### ❌ Wrong: Using long-form namespace

```
PrismQ.Text.Content ❌
```

**Correct:**
```
PrismQ.T.Content ✓
```

## Cross-References

For detailed information about module hierarchy and dependencies, see:
- [CODING_GUIDELINES.md](./CODING_GUIDELINES.md) - Complete module design principles
- [MODULE_HIERARCHY_UPDATED.md](./MODULE_HIERARCHY_UPDATED.md) - Detailed hierarchy and dependencies

## Summary

**One Rule to Remember:**

> **State name = Directory path with `/` → `.` and `PrismQ.` prefix**

Example: `T/Content/From/Idea/Title/` → `PrismQ.T.Content.From.Idea.Title`

This ensures consistency across the entire codebase and documentation.
