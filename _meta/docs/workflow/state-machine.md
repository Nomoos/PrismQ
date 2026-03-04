# PrismQ.T Content Production — State Machine

**Complete state diagram for Story production pipeline (modules 03–20)**

> 📖 **See also**:
> - [Workflow Documentation Index](./README.md)
> - Module reports in `_meta/reports/`

---

## State Diagram

```mermaid
stateDiagram-v2
    direction TB

    %% ── State aliases (short ID → actual PrismQ.T state string) ──────────
    TitleFromIdea          : [03] PrismQ.T.Title.From.Idea
    ContentFromIdeaTitle   : [04] PrismQ.T.Content.From.Idea.Title
    RevTitleFromContentIdea: [05] PrismQ.T.Review.Title.From.Content.Idea
    RevContentFromTitleIdea: [06] PrismQ.T.Review.Content.From.Title.Idea
    RevTitleFromContent    : [07] PrismQ.T.Review.Title.From.Content
    TitleRegen             : [08] PrismQ.T.Title.From.Title.Review.Content
    ContentRegen09         : [09] PrismQ.T.Content.From.Title.Content.Review
    RevContentFromTitle    : [10] PrismQ.T.Review.Content.From.Title
    Grammar                : [11] PrismQ.T.Review.Content.Grammar
    Tone                   : [12] PrismQ.T.Review.Content.Tone
    Content                : [13] PrismQ.T.Review.Content.Content
    Consistency            : [14] PrismQ.T.Review.Content.Consistency
    Editing                : [15] PrismQ.T.Review.Content.Editing
    TitleReadability       : [16] PrismQ.T.Review.Title.Readability
    ContentReadability     : [17] PrismQ.T.Review.Content.Readability
    StoryReview            : [18] PrismQ.T.Story.Review
    StoryPolish            : [19] PrismQ.T.Story.Polish
    Publishing             : [20] PrismQ.T.Publishing

    %% ── Phase 1–2: Generation ────────────────────────────────────────────
    [*]                    --> TitleFromIdea
    TitleFromIdea          --> ContentFromIdeaTitle

    %% ── Phase 3: Initial Review Cycle (modules 05–07) ───────────────────
    ContentFromIdeaTitle   --> RevTitleFromContentIdea

    RevTitleFromContentIdea --> RevContentFromTitleIdea : PASS
    RevTitleFromContentIdea --> TitleRegen              : FAIL

    RevContentFromTitleIdea --> RevTitleFromContent     : PASS
    RevContentFromTitleIdea --> ContentRegen09          : FAIL

    RevTitleFromContent     --> RevContentFromTitle     : PASS
    RevTitleFromContent     --> TitleRegen              : FAIL

    %% ── Phase 4: Regeneration loops (modules 08–09) ────────────────────
    %% [08] title improvement → [10] quality gate (content checked against new title)
    TitleRegen     --> RevContentFromTitle
    %% [09] content improvement → [10] quality gate
    ContentRegen09 --> RevContentFromTitle

    %% ── Phase 5: Pre-Quality Gate (module 10) ───────────────────────────
    RevContentFromTitle --> Grammar        : PASS
    RevContentFromTitle --> ContentRegen09 : FAIL

    %% ── Phase 6: Quality Review Chain (modules 11–17) ───────────────────
    %% content issues → [09] content regen; title issue → [08] title regen
    Grammar     --> Tone             : PASS ≥85
    Grammar     --> ContentRegen09   : FAIL

    Tone        --> Content          : PASS ≥75
    Tone        --> ContentRegen09   : FAIL

    Content     --> Consistency      : PASS ≥75
    Content     --> ContentRegen09   : FAIL

    Consistency --> Editing          : PASS ≥80
    Consistency --> ContentRegen09   : FAIL

    Editing     --> TitleReadability : PASS ≥75
    Editing     --> ContentRegen09   : FAIL

    TitleReadability --> ContentReadability : PASS ≥75
    TitleReadability --> TitleRegen         : FAIL

    ContentReadability --> StoryReview    : PASS ≥75
    ContentReadability --> ContentRegen09 : FAIL

    %% ── Phase 7: Expert Review (modules 18–19) ──────────────────────────
    StoryReview --> StoryPolish    : PASS ≥70
    StoryReview --> ContentRegen09 : FAIL

    StoryPolish --> Publishing

    Publishing --> [*]
```

---

## State Reference Table

| Module | State (PrismQ.T string) | Description |
|--------|------------------------|-------------|
| 03 | `PrismQ.T.Title.From.Idea` | AI title generation from Idea |
| 04 | `PrismQ.T.Content.From.Idea.Title` | AI content generation from Idea + Title |
| 05 | `PrismQ.T.Review.Title.From.Content.Idea` | AI review: title vs. content + idea |
| 06 | `PrismQ.T.Review.Content.From.Title.Idea` | AI review: content vs. title + idea |
| 07 | `PrismQ.T.Review.Title.From.Content` | AI review: title vs. content (final pre-chain) |
| 08 | `PrismQ.T.Title.From.Title.Review.Content` | Title regeneration from review feedback |
| 09 | `PrismQ.T.Content.From.Title.Content.Review` | Content regeneration from early review feedback |
| 10 | `PrismQ.T.Review.Content.From.Title` | **Quality gate**: final review before grammar chain |
| 11 | `PrismQ.T.Review.Content.Grammar` | Grammar, punctuation, syntax (threshold ≥ 85) |
| 12 | `PrismQ.T.Review.Content.Tone` | Tone, voice, emotional register (threshold ≥ 75) |
| 13 | `PrismQ.T.Review.Content.Content` | Factual accuracy, coherence (threshold ≥ 75) |
| 14 | `PrismQ.T.Review.Content.Consistency` | Character/timeline/detail consistency (threshold ≥ 80) |
| 15 | `PrismQ.T.Review.Content.Editing` | Clarity, flow, wordiness, pacing (threshold ≥ 75) |
| 16 | `PrismQ.T.Review.Title.Readability` | Title clarity, catchiness, length (threshold ≥ 75) |
| 17 | `PrismQ.T.Review.Content.Readability` | Voice-over suitability, spoken flow (threshold ≥ 75) |
| 18 | `PrismQ.T.Story.Review` | Expert holistic review: title+content (threshold ≥ 70) |
| 19 | `PrismQ.T.Story.Polish` | Final polish + SEO optimisation |
| 20 | `PrismQ.T.Publishing` | Terminal state — ready for publication |

### Improvement States (FAIL destinations)

| Module | State | Triggered by | Next state |
|--------|-------|--------------|------------|
| 08 | `PrismQ.T.Title.From.Title.Review.Content` | Mod 05 FAIL, Mod 07 FAIL, Mod 16 FAIL | Module 10 (content checked against new title) |
| 09 | `PrismQ.T.Content.From.Title.Content.Review` | Mod 06 FAIL, Mod 10 FAIL, Mods 11–15 FAIL, Mod 17 FAIL, Mod 18 FAIL | Module 10 (basic content review, no idea) |

---

## AI Model Assignment

| Phase | Modules | Model | Notes |
|-------|---------|-------|-------|
| Generation | 03–04 | `qwen3:14b` | Via `PRISMQ_AI_MODEL` env var |
| Initial reviews | 05–07 | `qwen3:14b` | Via `PRISMQ_AI_MODEL_REVIEW` env var |
| Regeneration | 08–09 | `qwen3:32b` | Via `PRISMQ_AI_MODEL_CONTENT_IMPROVE` env var |
| Quality gate | 10 | `qwen3:14b` | |
| Quality reviews | 11–17 | `qwen3:14b` (local Ollama) | Via `PRISMQ_AI_MODEL_REVIEW` |
| Expert review | 18 | External (GPT / Claude) | Not Ollama — top expert model |
| Polish | 19 | External (GPT / Claude) | Not Ollama — top expert model |
