# BUG-004 — Variant diversity too low (repeated vocabulary, "mirror" x4)

**Found**: 2026-03-04 (QA session)
**Stage**: 01 (T.Idea.From.User)
**Severity**: Medium — reduces value of 10-variant generation

## Problem

10 generated variants share the same vocabulary and sentence structure.
The word "mirror" appears in variants 3, 6, 8, and 9.
Variants 6, 8, and 9 are nearly identical in structure.

The purpose of generating 10 variants with different flavors is to produce
*diverse* angles on the same topic. Currently they converge to the same literary style.

## Evidence (QA 2026-03-04)

Variants 6, 8, 9 all start with:
> "A moment of misaligned desire fractures the fragile boundary between..."

That is the same opening sentence pattern in 3 out of 10 variants.

"Mirror" used as metaphor: variants 3, 6, 8, 9 (40% repetition rate).

## Root Cause

- Model temperature may be too low → low diversity
- Flavor prompts don't sufficiently differentiate the narrative voice
- No post-generation deduplication / diversity check

## Fix

1. Increase temperature for idea generation (currently 0.6-0.8, try 0.8-1.0)
2. Add diversity check: reject variant if cosine similarity to existing variants > 0.85
3. Strengthen flavor prompt differentiation (each flavor should enforce unique structural constraints)
