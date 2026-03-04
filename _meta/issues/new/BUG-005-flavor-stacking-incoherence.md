# BUG-005 — Flavor stacking (6+ flavors combined) produces incoherent output

**Found**: 2026-03-04 (QA session)
**Stage**: 01 (T.Idea.From.User)
**Severity**: Medium

## Problem

Variant 4 from QA session had 6+ flavors combined:

> "Chosen Family Seed + Identity + Empowerment + The Routine Morning That Felt Different in Toronto
>  + Comfort Aesthetic → Psychological Twist (Boston) + The One Detail Nobody Noticed in Toronto"

The output is scattered and tries to serve too many narrative directions at once,
resulting in a paragraph that has no clear angle or hook.

## Root Cause

The flavor selector allows combining multiple flavors without a cap.
When 6+ flavors are stacked, the prompt becomes contradictory.

## Fix

- Cap flavor combinations at 2-3 per variant
- Or: use only 1 primary flavor per variant (simplest, most coherent)
- Add test: if combined flavor string > N tokens, reject and re-select
