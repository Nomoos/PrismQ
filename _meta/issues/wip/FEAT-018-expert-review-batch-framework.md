# FEAT-018 — Expert Review & Polish: Batch API Framework (Steps 18–21)

**Started**: 2026-03-07 (session)
**Stage**: 18–21 (Story.Review, Story.Polish)
**Status**: WIP — framework complete, bat files + step 21 poll pending

---

## Summary

Replacing the old blocking Ollama-based expert review (steps 18–19) with a
multi-model batch framework that supports:
- **GPT** (OpenAI Batch API, `o3` with `reasoning_effort=medium`)
- **Claude** (Anthropic Batch API, `claude-opus-4-6`)
- **Manual** (user writes response files to `C:/PrismQ/manual/`)

Each model has its own DB state, so all three tracks can run independently.
Steps are split: submit (18, 20) and poll (19, 21).

---

## New State Machine

```
[17] STORY_REVIEW
  → [18.1] STORY_REVIEW_GPT_PENDING     (OpenAI Batch)
  → [18.2] STORY_REVIEW_CLAUDE_PENDING  (Anthropic Batch)
  → [18.3] STORY_REVIEW_MANUAL_PENDING  (file: {story_id}_review_done.txt)

[19] Poll review → STORY_POLISH (PASS ≥75) or ContentRegen09 (FAIL)

[20] STORY_POLISH
  → [20.1] STORY_POLISH_GPT_PENDING
  → [20.2] STORY_POLISH_CLAUDE_PENDING
  → [20.3] STORY_POLISH_MANUAL_PENDING  (file: {story_id}_polish_done.txt)

[21] Poll polish → PUBLISHING
```

---

## Completed ✅

### Model/state.py
New states added to both `StoryState` enum and `StateNames` class:
- `STORY_REVIEW_GPT_PENDING`    = `PrismQ.T.Story.Review.GPT.Pending`
- `STORY_REVIEW_CLAUDE_PENDING` = `PrismQ.T.Story.Review.Claude.Pending`
- `STORY_REVIEW_MANUAL_PENDING` = `PrismQ.T.Story.Review.Manual.Pending`
- `STORY_POLISH_GPT_PENDING`    = `PrismQ.T.Story.Polish.GPT.Pending`
- `STORY_POLISH_CLAUDE_PENDING` = `PrismQ.T.Story.Polish.Claude.Pending`
- `STORY_POLISH_MANUAL_PENDING` = `PrismQ.T.Story.Polish.Manual.Pending`

### T/_shared/ framework (all new)
```
T/_shared/__init__.py
T/_shared/api/__init__.py
T/_shared/api/api_config.py          GPT_MODEL="o3", REASONING_EFFORT="medium"
T/_shared/api/rest_client.py         Generic HTTP client with retry
T/_shared/api/openai_client.py       OpenAI Chat Completions (direct calls)
T/_shared/api/openai_batch_client.py OpenAI Batch API lifecycle
T/_shared/api/claude_batch_client.py Anthropic Batch API lifecycle
T/_shared/db/__init__.py
T/_shared/db/story_batch_db.py       StoryBatch + StoryBatchItem tables
```

**StoryBatch table** (created on first use):
```sql
StoryBatch      (id, openai_batch_id, step, status, story_count, submitted_at, ...)
StoryBatchItem  (id, batch_id, story_id, custom_id, result_json)
```
`step` values: `"review-gpt"`, `"review-claude"`, `"polish-gpt"`, `"polish-claude"`

### Service files (all new)
```
T/Story/Review/src/story_review_batch_submit.py  Step 18 — submit (gpt/claude/manual)
T/Story/Review/src/story_review_batch_poll.py    Step 19 — poll all 3 tracks
T/Story/Polish/src/story_polish_batch_submit.py  Step 20 — submit
T/Story/Polish/src/story_polish_batch_poll.py    Step 21 — poll all 3 tracks
```

### Prompt templates (new)
```
T/Story/Review/_meta/prompts/review_story_gpt.txt  Expert review → {"overall_score", "feedback"}
T/Story/Polish/_meta/prompts/polish_story_gpt.txt  Polish → {"title", "content", "changes"}
```

### Documentation updated
```
_meta/docs/workflow/state-machine.md  — full mermaid graph + model table updated
```

---

## Pending ❌

### 1. story_polish_batch_poll.py — Claude pending handling
File: `T/Story/Polish/src/story_polish_batch_poll.py`
Currently handles GPT + Manual. Need to add `_poll_claude_batch()` method
(same pattern as `story_review_batch_poll.py` → `_poll_claude_batch()`).

### 2. Bat files in `_meta/scripts/`
Need to create:
```
_meta/scripts/18_PrismQ.T.Story.Review.Submit/Run.bat      (step 18 — PRISMQ_REVIEW_MODE=gpt)
_meta/scripts/19_PrismQ.T.Story.Review.Poll/Run.bat         (step 19)
_meta/scripts/20_PrismQ.T.Story.Polish.Submit/Run.bat       (step 20 — PRISMQ_REVIEW_MODE=gpt)
_meta/scripts/21_PrismQ.T.Story.Polish.Poll/Run.bat         (step 21)
```

Optionally also per-model bat files:
```
_meta/scripts/18.1_PrismQ.T.Story.Review.GPT/Run.bat       (PRISMQ_REVIEW_MODE=gpt)
_meta/scripts/18.2_PrismQ.T.Story.Review.Claude/Run.bat    (PRISMQ_REVIEW_MODE=claude)
_meta/scripts/18.3_PrismQ.T.Story.Review.Manual/Run.bat    (PRISMQ_REVIEW_MODE=manual)
_meta/scripts/20.1_PrismQ.T.Story.Polish.GPT/Run.bat
...etc
```

### 3. Workflow runner scripts
Need thin `workflow.py` wrapper for each of steps 18–21 (like existing steps)
that connects to DB, calls `run()`, prints result, loops.

Pattern to follow: `T/Review/Content/From/Title/Idea/src/review_content_from_title_idea_workflow.py`

### 4. requirements.txt updates
Add `requests>=2.28.0` (already a dep) to:
- `T/Story/Review/requirements.txt`
- `T/Story/Polish/requirements.txt`
(currently only have pytest)

### 5. update run_all_14b.bat
Add steps 18–21 (or 18–19 at least):
```batch
call "%SCRIPTS%\18_PrismQ.T.Story.Review.Submit\Run.bat"
call "%SCRIPTS%\19_PrismQ.T.Story.Review.Poll\Run.bat"
call "%SCRIPTS%\20_PrismQ.T.Story.Polish.Submit\Run.bat"
call "%SCRIPTS%\21_PrismQ.T.Story.Polish.Poll\Run.bat"
```

### 6. Steps 10–17 AI review rewrite (original plan — still pending)
See original plan file (from plan mode) for full details.
Steps 10–17 still use old rule-based/algorithmic checkers.
All must be rewritten to use local Ollama qwen3:14b reviews.
Fail destination for all: `StateNames.CONTENT_FROM_CONTENT_REVIEW_TITLE`
Service pattern: copy from `T/Review/Content/From/Title/Idea/src/review_content_from_title_idea_service.py`

---

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `PRISMQ_REVIEW_MODE` | `gpt` | `gpt` / `claude` / `manual` |
| `PRISMQ_GPT_MODEL` | `gpt-5.2` | OpenAI model ID (Lechmazur rank #3, 8.511 score) |
| `PRISMQ_GPT_REASONING_EFFORT` | `medium` | OpenAI reasoning effort |
| `PRISMQ_CLAUDE_MODEL` | `claude-opus-4-6` | Anthropic model ID |
| `PRISMQ_MANUAL_DIR` | `C:/PrismQ/manual` | Dir for manual review/polish files |
| `PRISMQ_REVIEW_PASS_THRESHOLD` | `75` | Min score to pass review (step 19) |
| `OPENAI_API_KEY` | — | Required for GPT mode |
| `ANTHROPIC_API_KEY` | — | Required for Claude mode |

---

## Lechmazur Writing Benchmark — Top Models (2026-03-07)

| Rank | Model | Score | API ID | Notes |
|------|-------|-------|--------|-------|
| 1 | Claude Opus 4.6 Thinking 16K | 8.561 | `claude-opus-4-6` + `budget_tokens=16000` | Best overall |
| 2 | Claude Opus 4.6 (no reasoning) | 8.533 | `claude-opus-4-6` | |
| 3 | GPT-5.2 medium reasoning | 8.511 | `gpt-5.2` + `reasoning_effort=medium` | **Current GPT default** |
| 4 | GPT-5 Pro | 8.474 | `gpt-5-pro` | Higher cost |
| 5 | GPT-5.1 medium reasoning | 8.438 | `gpt-5.1` + `reasoning_effort=medium` | |

Source: https://github.com/lechmazur/writing

NOTE: `o3` is the OLD reasoning series (April 2025), NOT the same as GPT-5.x.
GPT-5.2 is a unified model (May 2025 family), `o3` is deprecated in ChatGPT UI.

---

## Manual Mode File Format

**Review done file** (`{MANUAL_DIR}/{story_id}_review_done.txt`):
```
SCORE: 85
FEEDBACK: Strong hook and natural flow, but ending feels rushed.
```

**Polish done file** (`{MANUAL_DIR}/{story_id}_polish_done.txt`):
```
TITLE: The Night Everything Changed
CONTENT:
It was 3 AM when Marcus heard the knock...
[full polished content]
```
