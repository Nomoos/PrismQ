# T/Story/ExpertPolish - GPT-Based Expert Story Polishing

**Namespace**: `PrismQ.T.Story.ExpertPolish`

Apply expert-level improvements to title and script based on GPT review feedback.

## Purpose

Implement the expert-level improvements suggested by GPT ExpertReview to achieve professional publishing quality. This is the final polishing stage before publishing.

## Workflow Position

**Stage 22** in MVP workflow: After expert review, before publishing

```
Stage 21: Story.ExpertReview (GPT-based)
    ↓ Improvements needed
Stage 22: Story.ExpertPolish (GPT-based) ← THIS STAGE
    ↓
Return to Stage 21: Story.ExpertReview for verification
    ↓ If ready
Stage 23: Publishing.Finalization
```

## Input Components

### Primary Inputs
- **Current Title** (from local AI reviews)
- **Current Script** (from local AI reviews)
- **Expert Review JSON** (from Stage 21: ExpertReview)
  - Improvement suggestions with priorities
  - Target quality score
  - Specific feedback per component

### Context
- **Audience Context** (target demographic, platform)
- **Original Idea** (for intent preservation)
- **Version History** (to avoid regression)

## GPT Configuration

### Model Selection
- **GPT-4**: High-quality polishing
- **GPT-5**: Highest quality, premium option

### Expert Roles
- **Expert Writer**: Specialized in content improvement
- **Story Polish Expert**: Knows how to enhance without changing essence
- **Audience Optimization Expert**: Perfects for target demographic

## Process

1. **Analyze Expert Feedback**:
   - Extract improvement suggestions from review JSON
   - Prioritize by impact and priority level
   - Group by component (title vs script)

2. **Apply Title Improvements**:
   - Implement high-priority title suggestions
   - Maintain title essence and recognition
   - Optimize for platform (e.g., thumbnail impact)
   - Preserve SEO value

3. **Apply Script Improvements**:
   - Implement high-priority script suggestions
   - Enhance without changing core narrative
   - Maintain voiceover flow and pacing
   - Preserve length constraints

4. **Validate Changes**:
   - Ensure improvements align with suggestions
   - Verify no unintended changes
   - Check length/timing still within limits
   - Confirm audience fit maintained

5. **Generate Polished Version**:
   - Create title (polished)
   - Create script (polished)
   - Document changes made
   - Prepare for re-review

## Output

- **Title (Polished)**: Expertly improved title
- **Script (Polished)**: Expertly improved script
- **Change Log**: Detailed list of improvements applied
- **Quality Delta**: Expected quality increase
- **Ready for Re-Review**: Package for Stage 21 verification

## Key Principles

1. **Surgical Improvements**: Small, high-impact changes
2. **Preserve Essence**: Don't change the core story
3. **GPT-Powered**: Uses advanced AI for expert-level writing
4. **Iterative**: Can loop back to ExpertReview if needed
5. **Final Touch**: Last improvements before publishing

## Improvement Types

### Title Polish
- **Word Choice**: Optimize for impact and clarity
- **Capitalization**: Enhance visual appeal
- **Length**: Perfect for platform constraints
- **Hook**: Maximize intrigue and clicks
- **SEO**: Maintain search value

### Script Polish
- **Opening Hook**: Strengthen immediate engagement
- **Relatability**: Add audience connection points
- **Pacing**: Fine-tune dramatic timing
- **Word Choice**: Optimize for voiceover flow
- **Clarity**: Ensure perfect comprehension
- **Impact**: Strengthen emotional resonance

## Example Polishing

**Input from ExpertReview:**
```json
{
  "improvement_suggestions": [
    {
      "component": "script",
      "priority": "high",
      "suggestion": "Add brief relatable context in opening",
      "impact": "Increases immediate audience connection"
    },
    {
      "component": "title",
      "priority": "medium",
      "suggestion": "Capitalize 'and' for stronger visual impact",
      "impact": "Improves thumbnail readability"
    }
  ]
}
```

**Before Polish:**
- Title: "The House That Remembers: and Hunts"
- Script Opening: "Every night at midnight, she returns..."

**GPT Expert Polish Process:**

1. **Title Improvement**:
   - Change: "and" → "And"
   - Rationale: Stronger visual impact in thumbnail
   - Result: "The House That Remembers: And Hunts"

2. **Script Opening Enhancement**:
   - Original: "Every night at midnight, she returns..."
   - Added: "We've all driven past abandoned houses. But this one? "
   - Enhanced: "We've all driven past abandoned houses. But this one? Every night at midnight, she returns..."
   - Rationale: Creates immediate relatability before mystery

**After Polish:**
- Title: "The House That Remembers: And Hunts"
- Script Opening: "We've all driven past abandoned houses. But this one? Every night at midnight, she returns..."
- Quality Score: 92% → 96% (projected)
- Change Log: 2 improvements applied (1 title, 1 script)

**Next Step**: Return to Stage 21 (ExpertReview) for verification

## Iteration Limits

To prevent endless polishing:
- **Maximum Expert Iterations**: 2
  - First polish: Apply high-priority suggestions
  - Second polish (if needed): Apply medium-priority suggestions
  - After 2 iterations: Publish regardless (diminishing returns)

## Cost Considerations

- **GPT-4 Cost**: ~$0.02-0.10 per polish
- **GPT-5 Cost**: ~$0.10-0.50 per polish (premium)
- **Iterations**: Max 2, typically 1
- **Total Cost**: Minimal compared to content value

## Success Metrics

- **Quality Improvement**: Target +3-5% score increase
- **Iteration Count**: 1-2 iterations typical
- **Publishing Rate**: >95% publish after 1-2 polish cycles
- **Time Impact**: +5-10 minutes total workflow time

## Module Metadata

**[→ View ExpertPolish/_meta/docs/](./_meta/docs/)**
**[→ View ExpertPolish/_meta/examples/](./_meta/examples/)**
**[→ View ExpertPolish/_meta/tests/](./_meta/tests/)**

## Navigation

**[← Back to Story](../README.md)** | **[→ Story/_meta](../_meta/)**
