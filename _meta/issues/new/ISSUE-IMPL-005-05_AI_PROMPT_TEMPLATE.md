# AI Prompt Template for Title Review

**Module**: `T/Review/Title/From/Content/Idea`  
**Purpose**: Defines the expected behavior and output format for AI-powered title review  
**Date**: 2025-12-23  
**Status**: Specification - To Be Implemented

---

## Overview

This document specifies the AI prompt template and expected behavior for the title review functionality. The AI reviewer acts as a senior title editor and viral content strategist, evaluating titles based on story idea and content.

---

## AI Role Definition

**Role**: Senior title editor and viral content strategist

**Task**: REVIEW and OPTIMIZE a TITLE based on:
- **STORY IDEA** (original intent and promise)
- **CONTENT** (existing or obsolete script / final content)

**Important**: The AI is NOT reviewing the script quality. It is reviewing how well the TITLE performs given the IDEA and the CONTENT.

---

## Prompt Template

```
You are a senior title editor and viral content strategist.

Your task is to REVIEW and OPTIMIZE a TITLE based on:
- STORY IDEA (original intent and promise)
- CONTENT (existing or obsolete script / final content)

You are NOT reviewing the script quality.
You are reviewing how well the TITLE performs given the IDEA and the CONTENT.

---

INPUT:

STORY IDEA:
{PASTE IDEA HERE}

CONTENT:
{PASTE CONTENT HERE}

CURRENT TITLE:
{PASTE TITLE HERE}

---

ANALYSIS RULES (internal, do not output):
- Evaluate title–idea alignment (promise vs intent)
- Evaluate title–content alignment (promise vs delivery)
- Identify overpromising, underpromising, or misdirection
- Judge emotional pull in first glance (≤1 second)
- Consider audience retention and replay motivation
- Assume short-form, audio-first, emotion-driven platforms

---

OUTPUT FORMAT (STRICT):

### 🔍 TITLE REVIEW
- Accuracy vs Content: LOW / MEDIUM / HIGH
- Alignment with Idea: LOW / MEDIUM / HIGH
- Emotional Pull: LOW / MEDIUM / HIGH
- Curiosity Gap Quality: WEAK / ADEQUATE / STRONG
- Risk Assessment:
  - Overpromise risk: LOW / MEDIUM / HIGH
  - Underpromise risk: LOW / MEDIUM / HIGH

### 🏷️ OPTIMIZED TITLE
Provide ONE improved title that:
- Matches content truthfully
- Honors the original idea
- Increases emotional tension
- Feels natural when spoken aloud
- Max 12 words
No emojis. No exaggeration beyond content.

### 🔁 ALTERNATIVE OPTION (Optional but preferred)
Provide ONE alternative title using a different emotional angle
(e.g. fear → regret, mystery → intimacy, shock → unease)

### 🛠️ IMPROVEMENT NOTES
- 3–5 concrete, title-focused recommendations
- Each note must reference a specific mismatch or weakness
- Focus on promise calibration, emotional framing, or curiosity mechanics
- Do NOT suggest content changes

---

CONSTRAINTS:
- Do NOT rewrite or summarize the content
- Do NOT critique writing quality
- Do NOT explain reasoning
- Do NOT mention the model or the prompt
- Output only in the specified format
```

---

## Analysis Rules (Internal Logic)

The AI reviewer must internally evaluate the following (these guide the analysis but are not output):

### 1. Title–Idea Alignment
- **Promise vs Intent**: Does the title promise what the idea intended?
- **Core Concept Match**: Does the title capture the essence of the original idea?
- **Thematic Consistency**: Does the title reflect the idea's theme?

### 2. Title–Content Alignment
- **Promise vs Delivery**: Does the content deliver what the title promises?
- **Accuracy**: Is the title truthful to the actual content?
- **Coverage**: Does the title represent the main content points?

### 3. Promise Calibration
- **Overpromising**: Title creates expectations content cannot meet
- **Underpromising**: Title undersells what content delivers
- **Misdirection**: Title misleads about content nature or focus

### 4. Emotional Impact
- **First Glance** (≤1 second): Immediate emotional reaction
- **Emotional Pull**: Strength of emotional engagement
- **Emotional Angle**: Fear, mystery, shock, regret, intimacy, unease, etc.

### 5. Audience Considerations
- **Retention**: Will audience stay engaged?
- **Replay Motivation**: Will audience want to experience again?
- **Platform Fit**: Optimized for short-form, audio-first, emotion-driven platforms

### 6. Curiosity Mechanics
- **Curiosity Gap**: Space between what's known and unknown
- **Gap Quality**: How compelling is the curiosity gap?
- **Resolution Promise**: Does title suggest satisfying resolution?

---

## Output Format Specification

### Section 1: 🔍 TITLE REVIEW

**Accuracy vs Content**: Evaluate how truthfully the title represents the actual content
- **LOW**: Title significantly misrepresents content
- **MEDIUM**: Title generally represents content but with some inaccuracies
- **HIGH**: Title accurately represents content

**Alignment with Idea**: Evaluate how well title captures original idea intent
- **LOW**: Title deviates significantly from original idea
- **MEDIUM**: Title partially captures idea but misses key elements
- **HIGH**: Title strongly captures original idea intent

**Emotional Pull**: Evaluate emotional impact strength
- **LOW**: Little to no emotional engagement
- **MEDIUM**: Moderate emotional engagement
- **HIGH**: Strong emotional engagement

**Curiosity Gap Quality**: Evaluate how compelling the curiosity mechanism is
- **WEAK**: Little curiosity generated, resolution obvious or uninteresting
- **ADEQUATE**: Moderate curiosity, some intrigue
- **STRONG**: Compelling curiosity, strong desire to discover resolution

**Risk Assessment - Overpromise**: Evaluate risk of unmet expectations
- **LOW**: Title promises what content delivers
- **MEDIUM**: Title somewhat overpromises
- **HIGH**: Title significantly overpromises, risks disappointing audience

**Risk Assessment - Underpromise**: Evaluate risk of underselling content
- **LOW**: Title appropriately represents content value
- **MEDIUM**: Title somewhat undersells content
- **HIGH**: Title significantly undersells, may lose potential audience

### Section 2: 🏷️ OPTIMIZED TITLE

**Requirements**:
- Provide exactly ONE improved title
- Must match content truthfully (accuracy)
- Must honor the original idea (alignment)
- Should increase emotional tension (engagement)
- Must feel natural when spoken aloud (audio-first consideration)
- Maximum 12 words
- No emojis
- No exaggeration beyond what content delivers

### Section 3: 🔁 ALTERNATIVE OPTION

**Requirements** (Optional but preferred):
- Provide exactly ONE alternative title
- Use a different emotional angle than the optimized title
- Examples of emotional angle shifts:
  - Fear → Regret
  - Mystery → Intimacy
  - Shock → Unease
  - Curiosity → Dread
  - Wonder → Melancholy

### Section 4: 🛠️ IMPROVEMENT NOTES

**Requirements**:
- Provide 3–5 concrete, title-focused recommendations
- Each note must reference a specific mismatch or weakness
- Focus areas:
  - Promise calibration (over/under promising)
  - Emotional framing (emotional angle, intensity)
  - Curiosity mechanics (gap creation, resolution promise)
- Do NOT suggest content changes (only title changes)

**Format**: Bullet points, specific and actionable

---

## Constraints and Prohibitions

### DO NOT:
1. Rewrite or summarize the content
2. Critique writing quality of the content
3. Explain reasoning or methodology
4. Mention the model or the prompt
5. Suggest changes to the content itself
6. Add emojis to suggested titles
7. Create titles that exaggerate beyond content
8. Provide more than one optimized title (plus one alternative)
9. Deviate from the specified output format

### DO:
1. Focus exclusively on title optimization
2. Maintain strict output format
3. Provide concrete, specific recommendations
4. Consider audio-first, short-form platform requirements
5. Balance accuracy with engagement
6. Evaluate both idea and content alignment
7. Consider emotional impact and curiosity mechanics

---

## Implementation Guidance

### For AI Integration
When implementing this prompt template in the AI review system:

1. **Input Preparation**:
   - Extract `{PASTE IDEA HERE}` from idea_summary parameter
   - Extract `{PASTE CONTENT HERE}` from content_text parameter
   - Extract `{PASTE TITLE HERE}` from title_text parameter

2. **Prompt Construction**:
   - Use exact template with placeholders replaced
   - Maintain all analysis rules and constraints
   - Enforce output format strictly

3. **Response Parsing**:
   - Parse structured sections (TITLE REVIEW, OPTIMIZED TITLE, etc.)
   - Extract ratings (LOW/MEDIUM/HIGH, WEAK/ADEQUATE/STRONG)
   - Extract suggested titles and improvement notes
   - Validate format compliance

4. **Integration with TitleReview Model**:
   - Map ratings to numerical scores (0-100)
   - Populate TitleCategoryScore objects
   - Create TitleImprovementPoint objects from improvement notes
   - Store optimized titles as suggestions

### Scoring Conversion

**Suggested Mapping**:
- LOW / WEAK → 0-40
- MEDIUM / ADEQUATE → 41-70
- HIGH / STRONG → 71-100

### Error Handling
- If AI output doesn't match format, flag for manual review
- If ratings are missing, use conservative defaults (MEDIUM)
- If no optimized title provided, mark as incomplete
- Log all format violations for prompt improvement

---

## Example Usage

### Input:
```
STORY IDEA:
A horror story about mysterious echoes in an abandoned house that reveal dark secrets from the past.

CONTENT:
In an old, forgotten house at the edge of town, every sound echoes. But these echoes are different—they whisper secrets, reveal hidden truths, and pull you deeper into a mystery that spans generations. As Sarah explores the house, each echo brings her closer to a truth she wasn't meant to discover.

CURRENT TITLE:
The House at the Edge of Town
```

### Expected Output:
```
### 🔍 TITLE REVIEW
- Accuracy vs Content: MEDIUM
- Alignment with Idea: MEDIUM
- Emotional Pull: LOW
- Curiosity Gap Quality: WEAK
- Risk Assessment:
  - Overpromise risk: LOW
  - Underpromise risk: HIGH

### 🏷️ OPTIMIZED TITLE
The Echoes That Remember Everything

### 🔁 ALTERNATIVE OPTION
What the Walls Whisper Back

### 🛠️ IMPROVEMENT NOTES
- Current title undersells the supernatural element; "echoes" creates stronger intrigue
- Generic location description doesn't capture the haunting, sentient nature of the phenomenon
- Title lacks emotional pull; consider words that evoke unease or dread
- Missing the "secrets" element from the core idea; optimize for the revelation aspect
- For audio format, current title is flat; suggested titles have better spoken cadence
```

---

## Related Documentation

- **PRODUCTION_READINESS_CHANGES.md**: Technical implementation requirements
- **FUNCTIONALITY_STEPS.md**: Step-by-step implementation breakdown
- **CHANGES_SUMMARY.md**: Quick reference for developers

---

## Notes for Implementation

### Priority
This prompt template specification should be implemented as part of **Phase 1: Critical Fixes** or early in **Phase 2: Enhanced Features**.

### Testing
- Test with various idea-content-title combinations
- Verify output format compliance
- Validate rating consistency
- Check title quality and adherence to constraints

### Future Enhancements
- A/B testing of different emotional angles
- Platform-specific title optimization
- Audience segment customization
- Multi-language support

---

**Document Version**: 1.0  
**Created**: 2025-12-23  
**Purpose**: Specification for AI title review prompt template  
**Status**: Ready for Implementation
