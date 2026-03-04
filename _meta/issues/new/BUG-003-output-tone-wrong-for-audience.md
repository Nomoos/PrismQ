# BUG-003 — AI output tone too literary for YT Short audience (13-17)

**Found**: 2026-03-04 (QA session)
**Stage**: 01 (T.Idea.From.User), 03 (T.Title.From.Idea)
**Severity**: High — core product quality issue

## Problem

Generated ideas and titles read like literary fiction synopses, not YouTube Short hooks.
The target audience is 13-17 year old girls (US/Canada). They expect:

> **"POV: the cute guy from bio just texted my best friend…"**

Instead the pipeline produces:

> **"A moment of misaligned desire fractures the fragile trust between two people bound by loyalty."**
> **"Fractured Mirror's Echo"**
> **"Mirage's Fractured Thread"**

No 13-year-old clicks on "Fractured Mirror's Echo."

## Evidence

From QA run (2026-03-04), 10 generated idea variants — all use:
- Passive, abstract phrasing ("A moment of X fractures Y")
- Literary metaphors ("mirror", "shadow", "echo", "fractures")
- No conversational voice, no teen slang, no POV framing

Title scorer gave 0.80 to generic literary titles — scoring is blind to
audience relevance and YT-specific hook criteria.

## Root Cause

1. Prompts in `T/Idea/From/User/` do not enforce teen-conversational voice
2. Flavor system generates literary/artistic variations, not platform-native hooks
3. Title scorer (`title_scorer.py`) has no YT Short-specific evaluation criteria

## Affected Files

- `T/Idea/From/User/src/` — prompts / flavor definitions
- `T/Title/From/Idea/src/title_scorer.py` — scoring logic
- `T/Idea/From/User/src/flavors.py` — flavor tone definitions

## Fix

- Audit and rewrite prompts to enforce conversational, first-person, present-tense voice
- Add YT Short hook evaluation criteria to title scorer:
  - starts with POV / "I" / question?
  - contains emotional trigger word?
  - length ≤ 60 chars?
  - no literary metaphor?
- Review flavor definitions for audience fit
