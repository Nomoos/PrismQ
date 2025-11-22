# T/Script/FromQualityReviewAndPreviousScript - Script Quality Refinement

**Namespace**: `PrismQ.T.Script.FromQualityReviewAndPreviousScript`

Refine script based on quality review feedback (Grammar, Tone, Content, Consistency, Editing).

## Purpose

Polish script based on specialized quality review feedback after acceptance gates have been passed. This handles refinements from multiple quality review types.

## Workflow Position

**Stages 14-18 Feedback Loops** in MVP workflow: Return from quality reviews

```
Stage 13: Script Acceptance Check ✓ PASSED
    ↓
Stage 14: PrismQ.T.Rewiew.Script.Grammar ←───────────────┐
    ↓                                                     │
    ├─FAILS─→ FromQualityReviewAndPreviousScript ────────┘ ← THIS STATE
    ↓ PASSES                                              ↑
Stage 15: PrismQ.T.Rewiew.Script.Tone ←──────────────────┤
    ↓                                                     │
    ├─FAILS─→ FromQualityReviewAndPreviousScript ────────┘
    ↓ PASSES                                              ↑
Stage 16: PrismQ.T.Rewiew.Script.Content ←───────────────┤
    ↓                                                     │
    ├─FAILS─→ FromQualityReviewAndPreviousScript ────────┘
    ↓ PASSES                                              ↑
Stage 17: PrismQ.T.Rewiew.Script.Consistency ←───────────┤
    ↓                                                     │
    ├─FAILS─→ FromQualityReviewAndPreviousScript ────────┘
    ↓ PASSES                                              ↑
Stage 18: PrismQ.T.Rewiew.Script.Editing ←───────────────┤
    ↓                                                     │
    ├─FAILS─→ FromQualityReviewAndPreviousScript ────────┘
    ↓ PASSES
Stage 19: Title Readability Review
```

## Input Components

### Primary Inputs
- **Previous Script Version** (the accepted version that failed a quality review)
- **Current Title Version** (accepted and may have passed readability)

### Review Feedback (Always Present - from one of the quality reviews)

#### Grammar Review (Stage 14)
- Grammar corrections needed
- Punctuation adjustments
- Spelling fixes
- Syntax improvements
- Tense/person consistency

#### Tone Review (Stage 15)
- Emotional intensity adjustments
- Style alignment issues (dark, suspense, dramatic)
- Voice and POV consistency
- Audience-specific tone tuning
- Tonal mismatches to fix

#### Content Review (Stage 16)
- Logic gaps or missing elements
- Plot issues or contradictions
- Character motivation fixes
- Pacing problems
- Structural feedback
- Scene ordering issues

#### Consistency Review (Stage 17)
- Character name consistency
- Timeline alignment problems
- Location/scene continuity issues
- Repeated details mismatches
- Lore or fact inconsistencies
- Contradictions after edits

#### Editing Review (Stage 18)
- Sentence rewrites needed
- Structural paragraph fixes
- Confusing lines to clarify
- Redundancy to remove
- Transition improvements
- Clarity enhancements

### Context
- **Original Idea** (for intent preservation)
- **All Previous Versions** (for context)
- **Title Content** (for alignment)

## Process

1. **Identify review type**:
   - Determine which quality review triggered refinement
   - Understand review-specific requirements
   - Focus on that dimension of quality

2. **Analyze review feedback** (always present):
   - Extract specific issues
   - Prioritize fixes (critical vs minor)
   - Understand impact on overall quality

3. **Apply targeted improvements**:
   - **Grammar**: Fix technical correctness issues
   - **Tone**: Adjust emotional and stylistic elements
   - **Content**: Resolve narrative/structural problems
   - **Consistency**: Fix continuity and logic gaps
   - **Editing**: Improve clarity and flow

4. **Preserve other qualities**:
   - Don't break what's already passed
   - Maintain script-title alignment
   - Keep idea intent intact
   - Preserve length/timing

5. **Minimal targeted changes**:
   - Only fix what the specific review identified
   - Don't over-edit or change unnecessarily
   - Focus on the specific quality dimension

## Output

- **Script (refined)** (polished version)
- **Quality Improvements** (specific fixes made)
- **Review Type** (which quality review was addressed)
- **Validation Notes** (ready for re-review)

## Key Principle

**Review always present**: Quality refinement is always driven by specific review feedback. **Targeted fixes**: Only address the specific quality dimension that failed, preserving all other aspects.

## Return Paths

After refinement:
1. Returns to the specific quality review stage that failed (14-18)
2. **If PASSES**: Continue to next quality review
3. **If FAILS again**: Back here for another refinement (rare)

Each quality review is sequential:
- Must pass Grammar before Tone
- Must pass Tone before Content
- Must pass Content before Consistency
- Must pass Consistency before Editing
- Must pass Editing before Readability

## Example Refinements by Type

### Grammar Refinement (Stage 14)
**Input:** Script with "its" instead of "it's"
**Grammar Review:** "Line 15: 'its' should be 'it's' (it is)"
**Refinement:** Fix grammar error
**Output:** Script with corrected grammar

### Tone Refinement (Stage 15)
**Input:** Horror script with inconsistent dark tone
**Tone Review:** "Middle section (45-70s) feels too lighthearted for horror"
**Refinement:** Darken tone in middle section
**Output:** Script with consistent dark tone

### Content Refinement (Stage 16)
**Input:** Script with unexplained character motivation
**Content Review:** "Why does protagonist enter the house? Missing setup."
**Refinement:** Add brief motivation explanation in intro
**Output:** Script with clear character logic

### Consistency Refinement (Stage 17)
**Input:** Script calls location "the mansion" then "the cottage"
**Consistency Review:** "Lines 20 and 45: mansion vs cottage - pick one"
**Refinement:** Make it consistently "the house"
**Output:** Script with consistent terminology

### Editing Refinement (Stage 18)
**Input:** Script with run-on sentence at climax
**Editing Review:** "Line 78: Long sentence reduces impact, split into two"
**Refinement:** Break sentence for better flow
**Output:** Script with improved clarity and impact

## Difference from Earlier States

| State | Focus | Timing | Acceptance |
|-------|-------|--------|------------|
| FromReviewAndPreviousScriptAndTitle | Major refinements | Before acceptance | Not yet accepted |
| **This State** | **Quality polish** | **After acceptance** | **Already accepted** |

## Module Metadata

**[→ View FromQualityReviewAndPreviousScript/_meta/docs/](./_meta/docs/)**
**[→ View FromQualityReviewAndPreviousScript/_meta/examples/](./_meta/examples/)**
**[→ View FromQualityReviewAndPreviousScript/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Script](../README.md)** | **[→ Script/_meta](../_meta/)**
