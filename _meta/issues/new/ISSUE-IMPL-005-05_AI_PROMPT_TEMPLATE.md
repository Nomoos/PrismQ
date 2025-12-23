# AI Prompt Template for Title Review

**Module**: `T/Review/Title/From/Content/Idea`  
**Purpose**: Defines the expected behavior and output format for AI-powered title review  
**Date**: 2025-12-23  
**Status**: Specification - To Be Implemented  
**Version**: 2.0 (Updated with Narrative Format)

---

## Overview

This document specifies TWO AI prompt templates for title review functionality:

1. **Narrative Format** (RECOMMENDED) - Natural language review, optimized for local AI models
2. **Structured Format** - Explicit sections with ratings, for programmatic parsing

Both approaches have the same role and analysis rules but differ in output format.

---

## AI Role Definition

**Role**: Senior title editor and viral content strategist

**Task**: WRITE A TEXTUAL REVIEW of a TITLE based on:
- **STORY IDEA** (original intent and promise)
- **CONTENT** (existing or obsolete script / final content)

**Important**: The AI is NOT reviewing the content quality. It is reviewing the TITLE's effectiveness, accuracy, and emotional performance given what the audience is promised (Idea) and what they actually receive (Content).

---

## 🆕 RECOMMENDED: Narrative Format Prompt

### Why This Format?

**Advantages**:
- More natural for local AI models (less constrained output)
- Easier for humans to read and understand
- Flexible - AI can adapt tone and depth naturally
- Better quality from smaller models (less rigid structure)
- Professional, critique-style output

**Best For**:
- Local AI models (Ollama, LM Studio, etc.)
- Human review workflow
- Exploratory analysis
- Non-technical stakeholders

### Prompt Template (Narrative)

```
You are a senior title editor and viral content strategist.

Your task is to WRITE A TEXTUAL REVIEW of a TITLE based on:
- the STORY IDEA (original intent and promise)
- the CONTENT (existing / obsolete script or final content)

You are NOT reviewing the content quality.
You are reviewing the TITLE's effectiveness, accuracy, and emotional performance
given what the audience is promised (Idea) and what they actually receive (Content).

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
- Compare title promise vs idea intent
- Compare title promise vs content delivery
- Detect overpromise, underpromise, or misdirection
- Judge emotional pull in under 1 second
- Consider trust, retention, and replay motivation
- Assume short-form, audio-first, emotion-driven platforms

---

OUTPUT RULES (STRICT):
- Output ONLY a continuous review text (paragraphs allowed)
- Do NOT use headings, lists, or bullet points
- Do NOT quote the prompt or structure
- Do NOT mention scores or labels explicitly
- Do NOT rewrite or summarize the content
- Do NOT suggest content changes
- You MAY suggest title improvements or alternatives naturally within the text
- Tone: professional, precise, critical but constructive

The review should clearly answer:
- Does the title fit the idea?
- Does the title truthfully represent the content?
- Does it create enough emotional tension to earn the click?
- What is the main risk of keeping this title as-is?
```

### Analysis Rules (Internal Logic - Narrative Format)

The AI reviewer must internally evaluate these aspects (guide analysis, don't output explicitly):

1. **Title–Idea Alignment**: Compare title promise vs idea intent
2. **Title–Content Alignment**: Compare title promise vs content delivery  
3. **Promise Calibration**: Detect overpromise, underpromise, or misdirection
4. **Emotional Impact**: Judge emotional pull in under 1 second
5. **Audience Trust**: Consider trust, retention, and replay motivation
6. **Platform Fit**: Assume short-form, audio-first, emotion-driven platforms

### Output Requirements (Narrative Format)

**Must Do**:
- Write continuous prose (paragraphs allowed)
- Professional, precise, critical but constructive tone
- Answer the four key questions naturally:
  1. Does the title fit the idea?
  2. Does the title truthfully represent the content?
  3. Does it create enough emotional tension to earn the click?
  4. What is the main risk of keeping this title as-is?
- May suggest title improvements/alternatives naturally within the text

**Must NOT Do**:
- Use headings, lists, or bullet points
- Quote the prompt or reveal structure
- Mention scores or labels explicitly (e.g., "HIGH", "MEDIUM", "LOW")
- Rewrite or summarize the content
- Suggest content changes
- Explain methodology or reasoning process

### Example Output (Narrative Format)

**Input**:
- Idea: "A horror story about mysterious echoes in an abandoned house that reveal dark secrets from the past"
- Content: "In an old, forgotten house at the edge of town, every sound echoes..."
- Title: "The House at the Edge of Town"

**Expected Review**:

```
The title undersells the core supernatural element that drives this story. While "The House at the Edge of Town" is descriptive and establishes setting, it reads as generic rural Gothic rather than capturing the haunting, revelatory nature of the echoes that form the story's central mystery. The original idea promises audiences a specific paranormal phenomenon—sounds that expose hidden truths—but the title could describe any abandoned house story.

In terms of content alignment, the title is technically accurate but fails to deliver on the emotional intensity present in the narrative. The content establishes the echoes as sentient, almost malevolent entities that "whisper secrets" and "pull you deeper," yet the title offers no hint of this psychological tension. For audio-first platforms where the title needs to work when spoken aloud, the current phrasing lacks the rhythmic punch or unsettling quality that would make listeners pause.

The main risk here is underpromising. Audiences seeking horror content will scroll past what appears to be a standard haunted house setup, missing the more compelling hook about secrets revealed through sound. A stronger approach might center the echoes themselves—something like "The Echoes That Remember Everything" or "What the Walls Whisper Back"—which honors both the supernatural premise and the revelation theme while creating immediate intrigue about what these echoes might reveal.

The emotional pull is currently minimal. In the critical first second of audience decision-making, "The House at the Edge of Town" triggers familiarity rather than curiosity. For short-form content competing for attention, the title needs to promise something audiences haven't heard before, and the echo phenomenon provides that uniqueness if brought forward.
```

---

## ALTERNATIVE: Structured Format Prompt

### Why This Format?

**Advantages**:
- Explicit ratings for programmatic parsing
- Structured data integration with TitleReview model
- Consistent format across reviews
- Easier to extract metrics

**Best For**:
- API-based AI services (OpenAI, Anthropic, etc.)
- Automated workflows
- Data analytics and tracking
- A/B testing title variants

### Prompt Template (Structured)

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

## Comparison: Narrative vs Structured

| Aspect | Narrative Format | Structured Format |
|--------|------------------|-------------------|
| **Output Style** | Continuous prose | Explicit sections |
| **Readability** | Natural, essay-like | Clear, scannable |
| **AI Model Fit** | Better for local/smaller models | Better for API services |
| **Parsing** | Requires NLP | Simple string matching |
| **Flexibility** | AI can adjust depth/tone | Fixed structure |
| **Human Review** | Easier to read | Requires interpretation |
| **Metrics** | Implicit (need extraction) | Explicit ratings |
| **Title Suggestions** | Embedded naturally | Dedicated sections |
| **Best Use** | Editorial review workflow | Automated pipelines |

### Recommendation

**For This Project**: Use **Narrative Format** as primary approach because:
1. Local AI models produce better quality narrative reviews
2. More natural for human stakeholders to read
3. Less likely to produce parsing errors
4. Better adaptation to edge cases
5. Professional critique style matches editorial workflow

**Keep Structured Format** as optional for:
- Automated batch processing
- Analytics dashboards
- A/B testing frameworks
- Integration with external tools

---

## Shared Analysis Rules (Both Formats)

Both prompt formats use the same internal analysis logic:

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

### For Narrative Format (RECOMMENDED)

When implementing the narrative format:

1. **Input Preparation**:
   - Extract `{PASTE IDEA HERE}` from idea_summary parameter
   - Extract `{PASTE CONTENT HERE}` from content_text parameter
   - Extract `{PASTE TITLE HERE}` from title_text parameter

2. **Prompt Construction**:
   - Use exact template with placeholders replaced
   - Maintain all analysis rules and constraints
   - Set AI temperature to 0.7-0.8 for natural prose

3. **Response Parsing (NLP Required)**:
   - Store complete review text as primary output
   - Use NLP to extract implicit assessments:
     - Sentiment analysis for overall evaluation
     - Pattern matching for risk identification (e.g., "underpromising", "overpromising")
     - Entity extraction for suggested titles (quoted phrases)
   - Look for key phrases:
     - "The title undersells..." → underpromise risk
     - "fails to deliver..." → low accuracy
     - "lacks emotional impact..." → low emotional pull
     - "perfectly captures..." → high alignment

4. **Integration with TitleReview Model**:
   - Store narrative text in `notes` field
   - Extract sentiment-based scores for category_scores
   - Parse suggested titles from quoted text
   - Create TitleImprovementPoint from identified weaknesses

5. **Quality Assurance**:
   - Verify output is continuous prose (no lists/headings)
   - Check that four key questions are answered
   - Validate professional tone
   - Ensure no methodology explanations

### For Structured Format (ALTERNATIVE)

When implementing structured format:

1. **Input Preparation**: (same as narrative)

2. **Prompt Construction**:
   - Use exact template with placeholders replaced
   - Maintain all analysis rules and constraints
   - Set AI temperature to 0.3-0.5 for consistency
   - Enforce strict format compliance

3. **Response Parsing (Simple String Matching)**:
   - Parse structured sections (TITLE REVIEW, OPTIMIZED TITLE, etc.)
   - Extract ratings (LOW/MEDIUM/HIGH, WEAK/ADEQUATE/STRONG)
   - Extract suggested titles and improvement notes
   - Validate format compliance

4. **Integration with TitleReview Model**:
   - Map ratings to numerical scores (0-100)
   - Populate TitleCategoryScore objects
   - Create TitleImprovementPoint objects from improvement notes
   - Store optimized titles as suggestions

### Scoring Conversion (Structured Format Only)

**Suggested Mapping**:
- LOW / WEAK → 0-40
- MEDIUM / ADEQUATE → 41-70
- HIGH / STRONG → 71-100

### Scoring Estimation (Narrative Format)

Since narrative format doesn't provide explicit scores, use NLP-based estimation:

**Sentiment Ranges**:
- Very negative language → 0-40 (e.g., "fails completely", "misses entirely")
- Mixed/cautious language → 41-70 (e.g., "partially captures", "somewhat effective")
- Positive language → 71-100 (e.g., "perfectly captures", "strongly aligns")

**Pattern Keywords for Categories**:
- **Accuracy**: "truthfully", "accurately", "misrepresents", "misleading"
- **Alignment**: "honors", "captures", "deviates", "matches intent"
- **Emotional Pull**: "compelling", "flat", "engaging", "generic"
- **Risk Assessment**: "underpromising", "overpromising", "misdirection"

---

## Optimizing for Local AI Models

### Recommended Models

**For Narrative Format**:
- **Llama 3 8B/70B**: Excellent prose quality, good at critique
- **Mistral 7B**: Fast, concise, works well with constrained output
- **Mixtral 8x7B**: Best quality for local deployment
- **GPT4All models**: Lightweight, good for basic reviews

**For Structured Format**:
- **Llama 3 70B**: Better at following strict format
- **Yi 34B**: Good at structured output
- **Mixtral 8x7B**: Reliable format compliance

### Model Parameters

**For Narrative Format**:
```json
{
  "temperature": 0.7,
  "top_p": 0.9,
  "max_tokens": 800,
  "repeat_penalty": 1.1,
  "stop": ["INPUT:", "ANALYSIS RULES", "---"]
}
```

**For Structured Format**:
```json
{
  "temperature": 0.4,
  "top_p": 0.85,
  "max_tokens": 600,
  "repeat_penalty": 1.15,
  "stop": ["INPUT:", "CONSTRAINTS:"]
}
```

### Prompt Engineering Tips for Local Models

1. **Keep Instructions Clear**: Local models benefit from explicit, simple instructions
2. **Use Examples**: Add 1-2 example reviews in system prompt for better consistency
3. **Avoid Over-Constraining**: Narrative format works better with looser constraints
4. **Test Extensively**: Local models vary significantly - test with your specific model
5. **Adjust Temperature**: Start at 0.7, lower if output too creative, raise if too rigid

### Quality Checks for Local Models

**Narrative Format**:
- [ ] Output is continuous prose (no lists/bullets)
- [ ] Professional, critical tone maintained
- [ ] Four key questions answered
- [ ] At least one title suggestion provided
- [ ] Specific examples from content cited
- [ ] No methodology explanations present

**Structured Format**:
- [ ] All sections present (TITLE REVIEW, OPTIMIZED TITLE, etc.)
- [ ] Ratings use correct format (LOW/MEDIUM/HIGH)
- [ ] Optimized title ≤ 12 words
- [ ] 3-5 improvement notes provided
- [ ] No extraneous sections added

### Fallback Strategy

If local model produces poor output:
1. **Retry** with temperature 0.3 (more conservative)
2. **Simplify** prompt (remove some constraints)
3. **Switch format** (try structured if narrative fails)
4. **Use smaller inputs** (truncate very long content)
5. **Flag for human review** if still failing

---

## Error Handling
## Error Handling

**For Narrative Format**:
- If output contains lists/bullets, regenerate with stronger emphasis on prose
- If output is too short (<200 words), regenerate with higher temperature
- If output is too long (>1000 words), truncate or regenerate with max_tokens limit
- If no title suggestions found, flag for manual title creation
- Log all quality violations for prompt tuning

**For Structured Format**:
- If AI output doesn't match format, attempt regex extraction
- If ratings are missing, use conservative defaults (MEDIUM/ADEQUATE)
- If no optimized title provided, mark as incomplete
- If wrong format used, regenerate with explicit format reminder
- Log all format violations for prompt improvement

---

## Summary & Decision Matrix

### Choose Narrative Format If:
- ✅ Using local AI models (Ollama, LM Studio, etc.)
- ✅ Primary audience is human reviewers/editors
- ✅ Quality of critique matters more than structured data
- ✅ Workflow includes editorial judgment
- ✅ Want natural, professional-sounding reviews

### Choose Structured Format If:
- ✅ Using API-based AI (OpenAI, Anthropic, Google)
- ✅ Need programmatic parsing and data extraction
- ✅ Building automated pipelines
- ✅ Running A/B tests or analytics
- ✅ Integrating with dashboards/metrics

### Hybrid Approach:
Generate both formats:
1. **Primary**: Narrative for human stakeholders
2. **Secondary**: Structured for metrics/tracking
3. Store both in TitleReview.metadata

---

## Implementation Priority

### Phase 1: MVP (Choose One Format)
- Implement **Narrative Format** for local AI integration
- Focus on quality reviews for human workflow
- Manual extraction of key insights

### Phase 2: Enhanced (Add Structure)
- Add NLP-based scoring extraction from narrative
- Populate TitleReview model fields
- Create improvement points from review text

### Phase 3: Advanced (Dual Format)
- Support both formats based on use case
- Automated format selection based on model type
- Advanced analytics and tracking

---

## Related Documentation

- **PRODUCTION_READINESS_CHANGES.md**: Technical implementation requirements
- **FUNCTIONALITY_STEPS.md**: Step-by-step implementation breakdown  
- **CHANGES_SUMMARY.md**: Quick reference for developers
- **CHECKLIST.md**: Implementation task tracker

---

## Changelog

**Version 2.0** (2025-12-23):
- Added Narrative Format as RECOMMENDED approach
- Moved original format to "Structured Format Alternative"
- Added comparison matrix
- Added local AI model optimization guidance
- Added quality checks and fallback strategies
- Added implementation phases and decision matrix

**Version 1.0** (2025-12-23):
- Initial specification with structured format only

---

**Document Version**: 2.0  
**Created**: 2025-12-23  
**Updated**: 2025-12-23  
**Purpose**: Specification for AI title review with dual format support  
**Status**: Ready for Implementation - Narrative Format Recommended
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
