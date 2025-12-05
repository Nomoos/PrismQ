# T/Story/Review - GPT-Based Expert Story Review

**Namespace**: `PrismQ.T.Story.Review`

Final expert-level review of the complete story using GPT (GPT-4/GPT-5).

## Purpose

Provide a holistic, expert-level review of the complete story package (title + script + audience context) after all local AI reviews have passed. This is the final quality gate before publishing.

## Workflow Position

**Stage 21** in MVP workflow: After local AI reviews, before expert polish

```
Stage 20: Script Readability (Local AI) ✓ PASSES
    ↓
Stage 21: Story.Review (GPT-based) ← THIS STAGE
    ↓
    ├─ If improvements needed → Stage 22: Story.Polish
    ↓ If ready for publishing
Stage 23: Publishing.Finalization
```

## Input Components

### Primary Inputs
- **Title** (final version from all local reviews)
- **Script** (final version from all local reviews)
- **Audience Context** (target demographic, platform, style)
- **Original Idea** (for intent verification)

### Review Context
- All local review results (Grammar, Tone, Content, Consistency, Editing, Readability)
- Version history
- Improvement iterations count

## Review Focus

### Holistic Assessment
Unlike local AI reviews that focus on specific dimensions, expert review assesses:

1. **Story Coherence**
   - Does title accurately represent script?
   - Is the story compelling from start to finish?
   - Does it deliver on the promise?

2. **Audience Fit**
   - Perfect for target audience (e.g., US female 14-29)?
   - Appropriate tone and complexity?
   - Engaging and relatable?

3. **Professional Quality**
   - Production-ready?
   - Competitive with professional content?
   - Any subtle improvements possible?

4. **Platform Optimization**
   - Perfect for target platform (YouTube short)?
   - Ideal length and pacing?
   - Thumbnail-worthy title?

5. **Final Polish Opportunities**
   - Small tweaks for major impact?
   - Word choice optimizations?
   - Structural micro-improvements?

## GPT Configuration

### Model Selection
- **GPT-4**: High-quality, cost-effective
- **GPT-5**: Highest quality, premium option

### Expert Roles
- **Expert Reviewer**: Specialized in story assessment
- **Target Audience Expert**: Understands demographic preferences
- **Platform Expert**: Knows platform-specific best practices

### Review Output Format

```json
{
  "overall_assessment": {
    "ready_for_publishing": true/false,
    "quality_score": 0-100,
    "confidence": 0-100
  },
  "story_coherence": {
    "score": 0-100,
    "feedback": "detailed assessment",
    "title_script_alignment": "perfect/good/needs_work"
  },
  "audience_fit": {
    "score": 0-100,
    "feedback": "detailed assessment",
    "demographic_match": "excellent/good/needs_work"
  },
  "professional_quality": {
    "score": 0-100,
    "feedback": "detailed assessment",
    "production_ready": true/false
  },
  "platform_optimization": {
    "score": 0-100,
    "feedback": "detailed assessment",
    "platform_perfect": true/false
  },
  "improvement_suggestions": [
    {
      "component": "title/script",
      "priority": "high/medium/low",
      "suggestion": "specific improvement",
      "impact": "expected improvement description",
      "estimated_effort": "small/medium/large"
    }
  ],
  "decision": "publish/polish"
}
```

## Process

1. **Prepare Review Package**:
   - Compile title, script, audience context
   - Include all local review results
   - Add version history and iteration count

2. **Execute GPT Review**:
   - Send to GPT with expert reviewer prompt
   - Request holistic assessment
   - Get structured feedback (JSON format)

3. **Analyze Results**:
   - Parse GPT response
   - Extract improvement suggestions
   - Prioritize by impact and effort

4. **Make Decision**:
   - **If ready_for_publishing = true**: Proceed to Publishing
   - **If ready_for_publishing = false**: Send to Polish with suggestions

## Output

- **Expert Review JSON**: Complete assessment with scores and suggestions
- **Decision**: Publish or Polish
- **Improvement Plan**: Prioritized list of suggested improvements (if polish needed)
- **Quality Report**: Comprehensive quality assessment for records

## Key Principles

1. **Holistic Review**: Assesses complete story, not individual components
2. **GPT-Powered**: Uses advanced AI for expert-level judgment
3. **Final Gate**: Last quality check before publishing
4. **Actionable Feedback**: Provides specific, implementable suggestions
5. **Cost-Conscious**: Only runs once after all local reviews pass

## Example Review Scenario

**Input:**
- Title: "The House That Remembers: and Hunts"
- Script: 115-second horror short
- Audience: US female 14-29
- Platform: YouTube short
- Local Reviews: All passed

**GPT Expert Review:**
```json
{
  "overall_assessment": {
    "ready_for_publishing": false,
    "quality_score": 92,
    "confidence": 95
  },
  "story_coherence": {
    "score": 95,
    "feedback": "Excellent title-script alignment. Time-loop element is clear and compelling."
  },
  "audience_fit": {
    "score": 88,
    "feedback": "Strong fit for target demographic. Slight opportunity to enhance relatability."
  },
  "improvement_suggestions": [
    {
      "component": "script",
      "priority": "high",
      "suggestion": "Add brief relatable context in opening (e.g., 'We've all driven past abandoned houses...')",
      "impact": "Increases immediate audience connection",
      "estimated_effort": "small"
    },
    {
      "component": "title",
      "priority": "medium",
      "suggestion": "Consider removing lowercase 'and' - capitalize for stronger visual impact",
      "impact": "Improves thumbnail readability",
      "estimated_effort": "small"
    }
  ],
  "decision": "polish"
}
```

**Decision**: Send to Polish for small improvements (92% → 95%+ target)

## Critical Story Review Prompt

The module includes a specialized prompt template for local AI critical story reviews. This prompt focuses exclusively on identifying flaws and providing actionable feedback.

### Prompt Storage

The prompt is stored as a separate text file for easier maintenance and editing:
- **Location**: `_meta/prompts/critical_story_review.txt`
- **Loaded at module import** and exposed as `CRITICAL_STORY_REVIEW_PROMPT`

### Using the Critical Review Prompt

```python
from T.Story.Review import (
    get_critical_review_prompt,
    is_ready_for_final_polish,
    get_readiness_statement,
    CRITICAL_STORY_REVIEW_PROMPT
)

# Get the prompt with your story inserted
story_text = "Your complete story text here..."
prompt = get_critical_review_prompt(story_text)

# Use with your local AI model
# response = local_ai.generate(prompt)

# Check if story is ready for final polish based on score
score = 80  # Score from AI review
if is_ready_for_final_polish(score):
    print(get_readiness_statement(score))  # "This story is ready for final polish."
else:
    print(get_readiness_statement(score))  # "This story is not yet ready for final polish."
```

### Review Focus Areas

The critical review prompt focuses on:
- **Pacing and narrative flow issues**
- **Worldbuilding inconsistencies or contradictions**
- **Logical gaps in story rules or mechanics**
- **Underdeveloped or unclear character motivations**
- **Thematic weaknesses or missed opportunities**
- **Structural problems that reduce emotional impact**

### Review Output Structure

The prompt generates reviews with:
1. **Introduction**: Brief statement of what the story attempts to accomplish
2. **Major Flaws**: Bullet points or subsections with evidence
3. **Suggestions for Improvement**: Clear and practical
4. **Conclusion**: Short summary of why the weaknesses matter
5. **Final Score**: Numerical score 0-100%
6. **Readiness Statement**: Whether the story is ready for final polish (75%+ threshold)

### Readiness Threshold

- **Score >= 75%**: "This story is ready for final polish."
- **Score < 75%**: "This story is not yet ready for final polish."

## Module Metadata

**[→ View Review/_meta/docs/](./_meta/docs/)**
**[→ View Review/_meta/examples/](./_meta/examples/)**
**[→ View Review/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Story](../README.md)** | **[→ Story/_meta](../_meta/)**
