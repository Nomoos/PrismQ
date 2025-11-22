# T/Title/FromIdea - Initial Title Draft from Idea

**Namespace**: `PrismQ.T.Title.FromIdea`

Generate initial title variants directly from the idea concept.

## Purpose

Create the first version (v1) of title options based solely on the original idea, before any script content exists.

## Workflow Position

**Stage 2** in MVP workflow: `PrismQ.T.Title.Draft (v1)`

```
PrismQ.T.Idea.Creation
    ↓
PrismQ.T.Title.FromIdea (v1) ← Initial title creation
    ↓
PrismQ.T.Script.Draft (v1)
```

## Input

- Idea object with:
  - Core concept
  - Target audience
  - Content theme
  - Key message

## Process

1. Analyze idea concept and theme
2. Generate 3-5 title variants
3. Consider SEO and engagement factors
4. Store variants with idea reference

## Output

- Title v1 variants (3-5 options)
- Associated metadata (length, keywords, style)
- Link to source idea

## Next Stage

After title variants are created, they are used in:
- **Stage 3**: Script.FromIdea (uses Title v1 as context)
- **Stage 4**: Review.Title.ByScript (reviews Title v1 against Script v1)

## Module Metadata

**[→ View FromIdea/_meta/docs/](./_meta/docs/)**
**[→ View FromIdea/_meta/examples/](./_meta/examples/)**
**[→ View FromIdea/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Title](../README.md)** | **[→ Title/_meta](../_meta/)**
