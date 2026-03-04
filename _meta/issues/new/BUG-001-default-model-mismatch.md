# BUG-001 — Default model mismatch (Stage 01 → 404 errors)

**Found**: 2026-03-04 (QA session)
**Stage**: 01 (T.Idea.From.User)
**Severity**: High — blocks stage 01 completely without env override

## Problem

`ai_generator.py` defaults to `qwen3:14b` via `PRISMQ_AI_MODEL_STAGE_01` env var,
but the codebase design model is `qwen3:32b` and `qwen3:14b` is not pre-installed.

Result: every call to `/api/generate` returns HTTP 404.

## Root Cause

```python
# T/Idea/From/User/src/ai_generator.py:178
model: str = os.getenv("PRISMQ_AI_MODEL_STAGE_01", "qwen3:14b")
```

`qwen3:14b` is not listed in installed models → Ollama returns 404.

## Affected Files

- `T/Idea/From/User/src/ai_generator.py:178`
- `T/Idea/From/User/src/idea_create_cli.py:70`
- `T/src/ai_config.py:58`

## Fix

Either:
1. Add `PRISMQ_AI_MODEL_STAGE_01=qwen3:14b` to `C:/PrismQ/.env` and ensure model is pulled
2. Or change default in `ai_config.py` to match an always-installed model

**Chosen fix**: Pull `qwen3:14b` + `qwen3:8b` and document required models in setup guide.

## Status

**Částečně vyřešeno — PR #368** (Copilot, merged):
> "Add automatic Ollama model pull to setup scripts"

PR přidává auto-pull `qwen3:8b` a `qwen3:14b` do `setup_env.sh` pro stage 01–03.

### ⚠️ Zbývající mezery

1. **Pouze `.sh` soubory** — oprava je v `_meta/scripts/setup_env.sh`,
   ale Windows spouští `_meta/scripts/common/setup_env.bat`.
   `.bat` soubor **nemá** ekvivalentní model check → BUG-001 přetrvává na Windows.

2. **Pouze stage 01–03** — `setup_env.sh` pro stage 04+ opraven nebyl.

### Nutné doplnit

Přidat ekvivalentní logiku do `_meta/scripts/common/setup_env.bat`:

```bat
REM Check and pull required Ollama models
set MODELS=qwen3:8b qwen3:14b
for %%M in (%MODELS%) do (
    ollama list | findstr /i "%%M" >nul 2>&1
    if errorlevel 1 (
        echo [INFO] Pulling model: %%M
        ollama pull %%M
    ) else (
        echo [INFO] Model already available: %%M
    )
)
```

Modely manuálně staženy v této session:
```
ollama pull qwen3:14b  ✅
ollama pull qwen3:8b   ✅
```
