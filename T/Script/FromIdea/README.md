# T/Script/FromIdea - Initial Script Draft from Idea

**Namespace**: `PrismQ.T.Script.FromIdea`

Generate initial script draft directly from the idea and initial title.

## Purpose

Create the first version (v1) of the script based on the original idea and the initial title (v1).

## Workflow Position

**Stage 3** in MVP workflow: `PrismQ.T.Script.Draft (v1)`

```
PrismQ.T.Idea.Creation
    ↓
PrismQ.T.Title.FromIdea (v1)
    ↓
PrismQ.T.Script.FromIdea (v1) ← Initial script creation
    ↓
PrismQ.T.Rewiew.Title.ByScript
```

## Input

- Idea object with:
  - Core concept
  - Target audience
  - Content structure
  - Key message
- Title v1 (from Title.FromIdea)

## Process

1. Analyze idea concept and structure
2. Consider title promises and expectations
3. Generate script with:
   - Introduction/hook
   - Main content/body
   - Conclusion/call-to-action
4. Format for target platform (YouTube short, etc.)
5. Store with idea and title references

## Output

- Script v1 (initial draft)
- Structure metadata (sections, timing)
- Link to source idea and title
- Estimated length/duration

## Next Stage

After script is created, it is used in:
- **Stage 4**: Rewiew.Title.ByScript (reviews Title v1 against Script v1)
- **Stage 5**: Rewiew.Script.ByTitle (reviews Script v1 against Title v1)

## Module Metadata

**[→ View FromIdea/_meta/docs/](./_meta/docs/)**
**[→ View FromIdea/_meta/examples/](./_meta/examples/)**
**[→ View FromIdea/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Script](../README.md)** | **[→ Script/_meta](../_meta/)**
