# BUG-002 — Ollama cold start: first 1-2 requests fail with empty response

**Found**: 2026-03-04 (QA session)
**Stage**: 03 (T.Title.From.Idea)
**Severity**: Medium — data loss (stories skipped permanently)

## Problem

When `qwen3:8b` is not yet loaded into memory, the first 1-2 API calls return
an empty `response` field. The pipeline logs `"AI returned empty title"` and
**permanently skips** the story — it is never retried.

## Observed Output

```
Processing Story 1/18646 (ID: 19790)
AI returned empty title
⚠ AI could not generate a title for Story 19790, skipping   ← LOST

Processing Story 2/18646 (ID: 19780)
AI returned empty title
⚠ AI could not generate a title for Story 19780, skipping   ← LOST

Processing Story 3/18646 (ID: 19770)
Generated Title: Fractured Mirror's Echo ✅
```

## Root Cause

Ollama loads models lazily. First request triggers load (~10-30s).
During loading, response may be empty or malformed.
Current code: skip on empty, no retry.

## Affected File

`T/Title/From/Idea/src/ai_title_generator.py:235`

## Fix Options

1. **Warm-up ping** before processing loop: send a dummy prompt, wait for non-empty response
2. **Retry logic**: on empty response, wait 5s and retry up to 3 times before skipping
3. **State reset**: don't permanently skip — leave story in retryable state

Recommended: option 2 (retry with backoff), simplest fix with no architectural change.
