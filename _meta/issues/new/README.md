# Issues — QA Session 2026-03-04

Seřazeno dle severity (nejvyšší → nejnižší).

---

## 🔴 HIGH — Blokuje pipeline nebo kvalitu produktu

| ID | Soubor | Popis |
|---|---|---|
| BUG-007 | [BUG-007](./BUG-007-json-parse-error-false-rejection.md) | JSON parse error (qwen3 thinking mode) → 35% false rejection v kroku 05 |
| BUG-003 | [BUG-003](./BUG-003-output-tone-wrong-for-audience.md) | Výstup příliš literární pro cílové publikum 13–17 let |
| BUG-001 | [BUG-001](./BUG-001-default-model-mismatch.md) | Default model `qwen3:14b` chybí → 404, krok 01 kompletně blokován |

---

## 🟡 MEDIUM — Zhoršuje kvalitu nebo efektivitu, neblokuje kompletně

| ID | Soubor | Popis |
|---|---|---|
| FEAT-009 | [FEAT-009](./BUG-009-regen-loop-no-iteration-limit.md) | Progresivní čekání v regen smyčce (krok 08) dle verze titulu |
| BUG-008 | [BUG-008](./BUG-008-reject-threshold-too-aggressive.md) | Reject threshold 70 příliš agresivní → zbytečné regen smyčky |
| BUG-004 | [BUG-004](./BUG-004-variant-diversity-too-low.md) | Nízká diverzita variant — slovo "mirror" v 40% výstupů |
| BUG-005 | [BUG-005](./BUG-005-flavor-stacking-incoherence.md) | Flavor stacking 6+ → inkoherentní output |
| BUG-002 | [BUG-002](./BUG-002-ollama-cold-start-failures.md) | Ollama cold start → první 1–2 stories trvale ztraceny |

---

## 🟢 LOW — Kosmetické / onboarding / nice-to-have

| ID | Soubor | Popis |
|---|---|---|
| BUG-006 | [BUG-006](./BUG-006-missing-model-setup-docs.md) | Chybí dokumentace požadovaných Ollama modelů |

---

## Doporučené pořadí oprav

1. **BUG-007** — jedna regex řádka, okamžitý dopad na 35% stories
2. **BUG-001** — resolved stažením modelů (již hotovo)
3. **FEAT-009** — progresivní čekání v kroku 08
4. **BUG-008** — zvážit snížení threshold nebo soft-accept zónu
5. **BUG-003** — audit promptů, největší dopad na kvalitu produktu
6. **BUG-002** — retry logika pro cold start
7. **BUG-004 + BUG-005** — ladění flavor systému
8. **BUG-006** — dokumentace
