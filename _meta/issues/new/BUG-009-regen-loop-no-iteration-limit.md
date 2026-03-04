# FEAT-009 — Soft limit iterací pro regen smyčku (krok 05→08→05)

**Found**: 2026-03-04 (QA session)
**Stage**: 05 + 08 (Review.Title ↔ Title.From.Title.Review.Content)
**Severity**: 🟡 MEDIUM
**Type**: Enhancement / ochrana kvality dat

## Kontext

Regen smyčka 05→08→05 má přirozený soft-depriorizační mechanismus přes
`Title.version` — stories s vyšší verzí klesají na konec fronty. To zabraňuje
deadlocku, ale nestanovuje explicitní hranici kvality.

## Požadavek

Přidat **soft limit přes verzi titulu**: po dosažení `Title.version >= N`
ukončit smyčku řízeně — ne tvrdým zastavením, ale přesunem do definovaného
stavu s nejlepším dostupným výsledkem.

## Navrhované chování

Žádný hard limit ani force-accept. Pouze:
1. **SQL prioritizace** — fronty řazeny `ORDER BY Title.version ASC` → nižší verze = vyšší priorita
2. **Progresivní čekání v kroku 08** — čím vyšší verze, tím delší pauza před zpracováním další story

| Title.version | Čekání po zpracování |
|---|---|
| 1 | 0s (standardní 1ms) |
| 2 | 0s (standardní 1ms) |
| 3 | 5s |
| 4 | 10s |
| 5 | 15s |
| N ≥ 3 | `(N - 2) × 5` sekund |

Toto platí **pouze pro krok 08** (Title.From.Title.Review.Content).

## Implementace — krok 08

```python
REGEN_WAIT_BASE_VERSION = 3      # od které verze začíná čekání
REGEN_WAIT_STEP_SECONDS = 5      # sekund za každou verzi nad base

def get_wait_seconds(title_version: int) -> float:
    if title_version < REGEN_WAIT_BASE_VERSION:
        return 0.001  # standardní 1ms
    return (title_version - REGEN_WAIT_BASE_VERSION + 1) * REGEN_WAIT_STEP_SECONDS

# V processing loop (pouze krok 08):
story = get_next_story_ordered_by_title_version()  # ORDER BY version ASC
process_story(story)
wait = get_wait_seconds(story.title_version)
time.sleep(wait)
```

## SQL — řazení fronty (krok 08)

```sql
-- Výběr další story k regeneraci — nižší verze má přednost
SELECT s.id, MAX(t.version) AS title_version
FROM Story s
JOIN Title t ON t.story_id = s.id
WHERE s.state = 'PrismQ.T.Title.From.Title.Review.Content'
GROUP BY s.id
ORDER BY title_version ASC, s.id ASC
LIMIT 1;
```

## Monitoring

```sql
-- Distribuce verzí titulů — kolik stories je v jaké iteraci
SELECT MAX(t.version) AS version, COUNT(*) AS cnt
FROM Title t
JOIN Story s ON s.id = t.story_id
WHERE s.state = 'PrismQ.T.Title.From.Title.Review.Content'
GROUP BY MAX(t.version)
ORDER BY version;
```

## Konfigurace (env vars)

```
PRISMQ_REGEN_WAIT_BASE_VERSION=3
PRISMQ_REGEN_WAIT_STEP_SECONDS=5
```

## Poznámka k BUG-007

Oprava BUG-007 (JSON parse → false rejection) výrazně sníží počet stories
dosahujících version 2+. Progresivní čekání slouží jako záchranná síť
pro opravdové edge casy, ne jako primární ochrana.
