# BUG-008 — Reject threshold 70 příliš agresivní, způsobuje zbytečné regen smyčky

**Found**: 2026-03-04 (QA session, krok 05)
**Stage**: 05 (T.Review.Title.From.Content.Idea)
**Severity**: 🟡 MEDIUM — zvyšuje počet iterací a AI callů, nezastavuje pipeline

## Problém

Threshold pro přijetí titulu je 70 bodů. Ze sledovaných runů:
- Story 7890: score **65** → REJECTED (5 bodů pod hranicí)
- Story 7980: score **68** → REJECTED (2 body pod hranicí)

Tituly s score 65–69 jsou pravděpodobně použitelné, ale pipeline je posílá
na celou regen smyčku (krok 08 → krok 05 znovu) místo přijetí s varováním.

## Dopad

- Každý false-reject = 2 extra AI cally (krok 08 + krok 05 znovu)
- Při 651 stories ve frontě a ~18% legitimate reject rate = ~120 extra stories v smyčce
- Kombinace s BUG-007 (JSON parse) může způsobit nekonečné smyčky pro některé stories

## Návrh

**Možnost A**: Snížit threshold na 65 (přijmout borderline tituly)
**Možnost B**: Přidat "soft reject" zónu (65–69 = accept s tagem `needs_review`)
**Možnost C**: Limit na max 2 iterace regen smyčky, pak force-accept nebo skip

Doporučeno: Možnost C jako ochrana + Možnost B pro lepší data quality tracking.
