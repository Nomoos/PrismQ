# T/Script/FromOriginalScriptAndReviewAndTitle - All Script Improvements

**Namespace**: `PrismQ.T.Script.FromOriginalScriptAndReviewAndTitle`

Generate improved script versions (v2, v3, v4, v5...) using review feedback, original script, and title context.

## Purpose

This state handles **ALL** script improvements and refinements after the initial v1. Whether it's the first improvement (v2), iterative refinements (v3+), quality reviews (Grammar, Tone, Content, Consistency, Editing), or readability polish, all review-driven script updates happen here.

## Workflow Positions

This state is used in **multiple stages** throughout the workflow:

### Stage 7: First Improvements (v1 → v2)
**Using reviews from both title and script v1, plus new title v2**
```
Stage 4: Rewiew.Title.ByScript (v1) ← Title review
Stage 5: Rewiew.Script.ByTitle (v1) ← Script review
Stage 6: Title improved to v2
    ↓
Stage 7: Script.FromOriginalScriptAndReviewAndTitle (v1 → v2) ← THIS STATE
```

### Stage 11: Iterative Refinements (v2 → v3, v3 → v4, v4 → v5...)
**Using latest review feedback and current title**
```
Stage 10: Rewiew.Script.ByTitle (vN) ← Review latest
    ↓
Stage 11: Script.FromOriginalScriptAndReviewAndTitle (vN → vN+1) ← THIS STATE
    ↓
Stage 13: Script Acceptance Check
    ↓ if NOT ACCEPTED, loop back to Stage 10 → Stage 11
```

### Stages 14-18: Quality Review Refinements
**Using specific quality dimension feedback**
```
Stage 14: Rewiew.Script.Grammar ← Grammar check
    ↓ if FAILS
Script.FromOriginalScriptAndReviewAndTitle (grammar fix) ← THIS STATE

Stage 15: Rewiew.Script.Tone ← Tone check
    ↓ if FAILS
Script.FromOriginalScriptAndReviewAndTitle (tone fix) ← THIS STATE

Stage 16: Rewiew.Script.Content ← Content check
    ↓ if FAILS
Script.FromOriginalScriptAndReviewAndTitle (content fix) ← THIS STATE

Stage 17: Rewiew.Script.Consistency ← Consistency check
    ↓ if FAILS
Script.FromOriginalScriptAndReviewAndTitle (consistency fix) ← THIS STATE

Stage 18: Rewiew.Script.Editing ← Editing check
    ↓ if FAILS
Script.FromOriginalScriptAndReviewAndTitle (editing fix) ← THIS STATE
```

### Stage 20 Feedback: Readability Polish (final version refinement)
**Using readability review feedback**
```
Stage 20: Rewiew.Script.Readability (Voiceover) ← Final quality check
    ↓ if FAILS
Script.FromOriginalScriptAndReviewAndTitle (voiceover polish) ← THIS STATE
```

## Input Components

### Always Present
- **Original Script Version** (v1, v2, v3... whatever is the starting point)
- **Review Feedback** (always present - from any review type)
- **Current Title Version** (for context and alignment)

### Contextual
- **Original Idea** (for intent preservation)
- **Previous Review History** (for learning from iterations)
- **All Previous Script Versions** (for comparison)

## Review Types Handled

This state processes feedback from:

1. **Script Review by Title** (Stages 5, 10)
   - Script-title alignment
   - Content delivery vs promises
   - Quality and flow

2. **Title Review by Script** (Stages 4, 8)
   - Insights relevant to script
   - Title expectations to meet

3. **Grammar Review** (Stage 14)
   - Grammar corrections
   - Punctuation, spelling, syntax
   - Tense and person consistency

4. **Tone Review** (Stage 15)
   - Emotional intensity
   - Style alignment
   - Voice/POV consistency
   - Audience-specific tone

5. **Content Review** (Stage 16)
   - Logic gaps
   - Plot issues, contradictions
   - Character motivation
   - Pacing, structure

6. **Consistency Review** (Stage 17)
   - Character names
   - Timeline, locations
   - Detail matching
   - Fact alignment

7. **Editing Review** (Stage 18)
   - Sentence rewrites
   - Clarity improvements
   - Redundancy removal
   - Transition polish

8. **Script Readability Review** (Stage 20)
   - Voiceover flow
   - Pronunciation ease
   - Natural speech patterns
   - Dramatic delivery

## Process

### Common Steps (All Iterations)

1. **Analyze review feedback** (always present):
   - Identify review type and focus
   - Extract specific issues
   - Prioritize fixes (critical vs minor)
   - Understand quality/acceptance criteria

2. **Study original script**:
   - Identify what works
   - Understand what needs change
   - Review version history (avoid repeated mistakes)

3. **Ensure title alignment**:
   - Verify script delivers on title promises
   - Check opening hook matches title
   - Maintain consistency with title message

4. **Apply improvements**:
   - Make targeted changes based on review type
   - Preserve successful elements
   - Address review concerns
   - Maintain idea intent
   - Optimize length/timing if needed

5. **Generate next version**:
   - Create improved script (vN+1 or polished version)
   - Document changes and rationale
   - Prepare for next review cycle or publish

### Variation by Review Type

**Stage 7 (v1 → v2)**: Major improvements using both reviews + new title
**Stage 11 (v2 → v3+)**: Iterative refinements until accepted
**Stages 14-18**: Targeted quality dimension fixes
**Stage 20 Feedback**: Voiceover readability polish only

## Output

- **Script vN+1** (next version or polished version)
- **Change Rationale** (why changes were made)
- **Title Alignment Notes** (how it matches current title)
- **Review Response** (how feedback was addressed)
- **Review Type** (which review triggered this improvement)
- **Version Metadata** (version number, timestamp, iteration count)
- **Updated Structure** (sections, timing, format)

## Key Principles

1. **Review Always Present**: Every script improvement is driven by review feedback
2. **Original Script Referenced**: Always builds on previous version
3. **Title Alignment**: Always considers current title version
4. **Version Progression**: Clear v1 → v2 → v3 → v4... progression
5. **Multi-dimensional Quality**: Handles all review types in one state
6. **Iterative**: Can be called multiple times for different review types

## Example Progression

### Stage 7: First Improvement (v1 → v2)
**Inputs:**
- Original Script v1: 145-second narrative, weak middle
- Current Title v2: "The House That Remembers" (newly improved)
- Script Review: "Too long (145s), middle drags, needs paranormal angle"
- Title Review: "Title emphasizes memory/time-loop - script should too"

**Process:**
- Align with new title's memory theme
- Cut 30s from middle
- Strengthen paranormal/time-loop elements
- Improve pacing

**Output:**
- Script v2: 115-second narrative focused on time-loop

### Stage 11: Refinement (v2 → v3)
**Inputs:**
- Original Script v2: 115-second script
- Current Title v3: "The House That Remembers—And Hunts"
- Script Review: "Good length, needs stronger climax"

**Process:**
- Enhance climax sequence at 85-90s mark
- Add threat/danger imagery (matching title's "hunts")
- Maintain good pacing

**Output:**
- Script v3: 115s with enhanced climax and danger

### Stage 14: Grammar Fix
**Inputs:**
- Original Script v3: (accepted version)
- Grammar Review: "Line 15: 'its' should be 'it's' (it is)"

**Process:**
- Fix grammar error only
- No other changes

**Output:**
- Script v3 (grammar corrected)

### Stage 15: Tone Fix
**Inputs:**
- Original Script v3: (grammar passed)
- Tone Review: "Middle section (45-70s) too lighthearted for horror"

**Process:**
- Darken tone in middle section
- Add ominous undertones
- Maintain horror consistency

**Output:**
- Script v3 (tone corrected)

### Stage 16: Content Fix
**Inputs:**
- Original Script v3: (tone passed)
- Content Review: "Why does protagonist enter house? Missing setup"

**Process:**
- Add brief motivation in intro
- Clarify character logic

**Output:**
- Script v3 (content improved)

### Stage 17: Consistency Fix
**Inputs:**
- Original Script v3: (content passed)
- Consistency Review: "Lines 20 and 45: 'mansion' vs 'cottage' - inconsistent"

**Process:**
- Make terminology consistent: "the house"
- Check all references

**Output:**
- Script v3 (consistency fixed)

### Stage 18: Editing Fix
**Inputs:**
- Original Script v3: (consistency passed)
- Editing Review: "Line 78: Long run-on sentence reduces impact"

**Process:**
- Split sentence for better flow
- Improve climax impact

**Output:**
- Script v3 (editing polished)

### Stage 20: Readability Polish
**Inputs:**
- Original Script v3: (all quality reviews passed)
- Readability Review: "Line 34: 'perpetrator's methodology predicated' is tongue-twister"

**Process:**
- Rewrite for natural speech
- Simplify complex phrases
- Test voiceover flow

**Output:**
- Script v3 (readability polished): "whoever did this understood time itself"
- **READABILITY PASSED** ✓ → Ready for Publishing!

## State Naming Logic

`FromOriginalScriptAndReviewAndTitle` captures:
- **From Original Script**: Builds on previous version
- **And Review**: Always includes review feedback (any type)
- **And Title**: Always considers title context

This single state handles all the complexity of script evolution through multiple review types!

## Module Metadata

**[→ View FromOriginalScriptAndReviewAndTitle/_meta/docs/](./_meta/docs/)**
**[→ View FromOriginalScriptAndReviewAndTitle/_meta/examples/](./_meta/examples/)**
**[→ View FromOriginalScriptAndReviewAndTitle/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Script](../README.md)** | **[→ Script/_meta](../_meta/)**
