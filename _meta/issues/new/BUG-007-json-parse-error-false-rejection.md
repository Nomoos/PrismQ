# BUG-007 — JSON parse error způsobuje false rejection titulů (~35% runů)

**Found**: 2026-03-04 (QA session, krok 05)
**Stage**: 05 (T.Review.Title.From.Content.Idea)
**Severity**: 🔴 HIGH — blokuje ~35% stories, posílá je zbytečně do regen smyčky (krok 08)

## Problém

Model `qwen3:14b` vrací nevalidní JSON v ~35% případů. Pipeline to zachytí,
nastaví fallback score (~36–53) a story je **falešně odmítnuta** a přesměrována
na regeneraci titulu (krok 08). Nejde o špatný titul — jde o parse chybu.

## Pozorovaná četnost (17 runů z logu)

| Výsledek | Počet | % |
|---|---|---|
| ACCEPTED (score ≥ 70) | 8 | 47% |
| REJECTED — JSON error | 6 | 35% ← **falešné rejection** |
| REJECTED — legitimní | 3 | 18% |

## Chybové hlášky

```
Failed to parse AI JSON response: Expecting ',' delimiter: line 24 column 6 (char 1621)
Failed to parse AI JSON response: Expecting ',' delimiter: line 30 column 6 (char 1959)
Failed to parse AI JSON response: Expecting ',' delimiter: line 30 column 6 (char 1975)
Failed to parse AI JSON response: Expecting ',' delimiter: line 30 column 6 (char 1552)
Failed to parse AI JSON response: Expecting ',' delimiter: line 29 column 6 (char 1828)
Failed to parse AI JSON response: Expecting ',' delimiter: line 37 column 6 (char 2418)
```

Chyba vždy `Expecting ',' delimiter` — typický příznak qwen3 **thinking mode**:
model vloží `<think>...</think>` blok dovnitř JSON výstupu, čímž ho znevalidní.

## Root Cause

Qwen3 modely mají chain-of-thought thinking zapnutý defaultně. Výstup vypadá:

```json
{
  "score": 72,
  <think>
  Let me evaluate this carefully...
  </think>
  "reasoning": "..."
}
```

Parser selže na `<think>` tagu uprostřed JSON struktury.

## Dopad

- 35% stories jde zbytečně do krok 08 (regen title) → zbytečný AI call
- Regen title pošle story zpět na krok 05 → další šance na JSON chybu → smyčka
- Reálný accept rate je pravděpodobně ~65–70%, ne 47%

## Fix

**Možnost A** (doporučeno): Stripovat `<think>...</think>` bloky před JSON parsováním:
```python
import re
def strip_thinking(text: str) -> str:
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
```

**Možnost B**: Přidat `"think": false` do Ollama API requestu (pokud model podporuje):
```json
{"model": "qwen3:14b", "options": {"think": false}}
```

**Možnost C**: Použít JSON repair knihovnu (`json-repair` pip package).

## Affected Files

- `T/Review/Title/From/Idea/Content/src/review_title_from_idea_content_interactive.py`
- Jakýkoli soubor s `json.loads()` na AI response v review stages
