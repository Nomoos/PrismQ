# BUG-006 — No setup documentation for required Ollama models

**Found**: 2026-03-04 (QA session)
**Severity**: Medium — blocks new developer onboarding

## Problem

There is no single document listing which Ollama models must be installed
before running the pipeline. A new developer runs `Run.bat` and gets cryptic
404 errors with no guidance.

## Required Models (as of 2026-03-04)

| Model | Stage | Env var |
|---|---|---|
| `qwen3:8b` | 03-04 (Title, Content) | `PRISMQ_AI_MODEL_STAGE_03_04` |
| `qwen3:14b` | 01, 05-06 (Idea, Reviews) | `PRISMQ_AI_MODEL_STAGE_01`, `PRISMQ_AI_MODEL_STAGE_05_06` |
| `qwen3:32b` | 07+ (Quality, default) | `DEFAULT_AI_MODEL` |

## Fix

Add `_meta/docs/setup/OLLAMA_MODELS.md` with:
- List of required models per stage
- `ollama pull` commands
- GPU/RAM requirements per model
- Verification command (`ollama list`)

Also add model check to `common/start_ollama.bat`.
