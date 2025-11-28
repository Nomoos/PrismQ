# T/Title/From/Idea - Initial Title Draft from Idea

**Namespace**: `PrismQ.T.Title.From.Idea`

Generate initial title variants directly from the idea concept.

## Purpose

Create the first version (v1) of title options based solely on the original idea, before any script content exists.

## Workflow Position

**Stage 2** in MVP workflow: `PrismQ.T.Title.Draft (v1)`

```
PrismQ.T.Idea.Creation
    ↓
PrismQ.T.Title.From.Idea (v1) ← Initial title creation
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
2. Generate 10 title variants using diverse strategies
3. Consider SEO and engagement factors
4. Store variants with idea reference

## Output

- Title v1 variants (10 options by default, 3-10 configurable)
- 10 distinct title styles:
  - **Direct**: Straightforward, clear title
  - **Question**: Poses a question to engage readers
  - **How-to**: Action-oriented, instructional
  - **Curiosity**: Intriguing, creates interest
  - **Authoritative**: Expert perspective, comprehensive
  - **Listicle**: Number-based, digestible format
  - **Problem-Solution**: Addresses challenges and solutions
  - **Comparison**: Contrasts different approaches
  - **Ultimate-Guide**: Comprehensive resource positioning
  - **Benefit**: Value proposition, reader-focused
- Associated metadata (length, keywords, style, score)
- Link to source idea

## Next Stage

After title variants are created, they are used in:
- **Stage 3**: Script.FromIdea (uses Title v1 as context)
- **Stage 4**: Review.Title.ByScript (reviews Title v1 against Script v1)

## Module Metadata

**[→ View From/Idea/_meta/docs/](./_meta/docs/)**
**[→ View From/Idea/_meta/examples/](./_meta/examples/)**
**[→ View From/Idea/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Title](../../README.md)** | **[→ Title/_meta](../../_meta/)**
