# BUG-010 — Paralelní .sh setup skripty jsou dead code na Windows

**Found**: 2026-03-04 (QA session)
**Severity**: 🟡 MEDIUM — způsobuje zmatek, Copilot opravuje nesprávné soubory

## Problém

V projektu existují dvě sady setup skriptů:

| Soubor | Kde | Kdo ho volá | Platforma |
|---|---|---|---|
| `_meta/scripts/common/setup_env.bat` | hlavní pipeline | každý `Run.bat` | ✅ Windows (aktivní) |
| `T/Idea/From/User/_meta/scripts/setup_env.sh` | module-level | nikdo na Windows | ❌ mrtvý kód |
| `T/Story/From/Idea/_meta/scripts/setup_env.sh` | module-level | nikdo na Windows | ❌ mrtvý kód |
| `T/Title/From/Idea/_meta/scripts/setup_env.sh` | module-level | nikdo na Windows | ❌ mrtvý kód |

## Konkrétní dopad

PR #368 (Copilot) opravil auto-pull Ollama modelů **do `.sh` souborů** —
ty se ale na Windows nikdy nespustí. Oprava tedy nemá žádný efekt.

Skutečný `setup_env.bat` (`_meta/scripts/common/`) opraven nebyl.

## Root Cause

Projekt vznikal nebo byl navrhován s ohledem na více platforem (Linux CI/CD?),
ale primárním runtime prostředím je Windows. `.sh` skripty zůstaly jako
historický artefakt nebo CI placeholder bez aktivního volání.

## Možnosti řešení

**Možnost A** (doporučeno): Odstranit `.sh` skripty z `T/*/From/*/_meta/scripts/`
- Jsou duplicitní vůči `_meta/scripts/common/setup_env.bat`
- Jejich přítomnost mate Copilota i vývojáře

**Možnost B**: Ponechat `.sh` pouze pro explicitní CI/CD pipeline
- Přejmenovat na `setup_env.ci.sh`
- Přidat komentář: "This script is for CI/CD only, not for local Windows development"
- Zadat Copilotovi opravovat `.bat`, ne `.sh`

## Nutná oprava pro BUG-001

Model auto-pull přidat do `_meta/scripts/common/setup_env.bat`:

```bat
REM ── Ollama model check ─────────────────────────────────────
echo [INFO] Checking Ollama AI models...
for %%M in (qwen3:8b qwen3:14b qwen3:32b) do (
    ollama list 2>nul | findstr /i "%%M" >nul
    if errorlevel 1 (
        echo [INFO] Pulling model: %%M
        ollama pull %%M
    ) else (
        echo [INFO] Model ready: %%M
    )
)
```
