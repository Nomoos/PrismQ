# Prompt Optimization for Qwen3:32b Model

**Date**: 2025-12-23  
**Module**: `PrismQ.T.Content.From.Idea.Title`  
**Model**: Qwen3:32b via Ollama

---

## Overview

Optimized the AI content generation prompt specifically for the Qwen3:32b model to leverage its strengths and improve output quality.

---

## Changes Made

### Before: Generic Prompt Structure

```
SYSTEM INSTRUCTION:
You are a professional video content writer.
Follow instructions exactly. Do not add extra sections or explanations.

TASK:
Generate a video content.

INPUTS:
TITLE: {title}
IDEA: {idea_text}
INSPIRATION SEED: {seed} (Single word used only as creative inspiration)

TARGET AUDIENCE:
- Age: {age_range}
- Gender: {gender}
- Country: {country}

REQUIREMENTS:
1. Hook must strongly capture attention within the first 5 seconds.
2. Deliver the main idea clearly and coherently.
3. End with a clear and natural call-to-action.
4. Maintain consistent engaging tone throughout.
5. Use the inspiration seed subtly (symbolic or thematic, not literal repetition).
6. Target length: approximately {target_words} words (for {target_duration} seconds).
7. Maximum length: {max_words} words ({max_duration} seconds).

OUTPUT RULES:
- Output ONLY the content text.
- No headings, no labels, no explanations.
- Do not mention the word "hook", "CTA", or any structure explicitly.
- Do not mention that this is a script.

The first sentence must create immediate curiosity or tension.
```

**Issues**:
- Bullet/numbered format harder for model to parse
- Separated system and instructions (less cohesive)
- Technical language ("SYSTEM INSTRUCTION", "OUTPUT RULES")
- Multiple negative constraints

### After: Qwen3:32b Optimized Prompt

```
You are an expert video content writer specializing in engaging short-form content for {gender} audiences aged {age_range} in {country}.

# Your Task
Write compelling video narration for: "{title}"

# Context
{idea_text}

# Creative Direction
Draw subtle inspiration from: {seed}
(Use this thematically or symbolically—do not mention it directly)

# Requirements
**Structure**: Begin with an attention-grabbing hook, deliver the core message clearly, end with a natural call-to-action.

**Length**: {target_words} words (target) | {max_words} words (maximum)

**Style Guidelines**:
- First sentence must create immediate curiosity or tension
- Use conversational, engaging language throughout
- Maintain consistent energy and pacing
- Make every word count—no filler
- End with a clear action for viewers

**Critical Constraints**:
- Write ONLY the narration text—no labels, headings, or meta-commentary
- Never mention "hook", "CTA", "script", or structural elements
- Never explain what you're doing—just deliver the content
- Stay within word limit

# Output Format
Write the complete narration as a single, flowing text. Start immediately with the hook.
```

**Improvements**:
- Markdown format for better structure recognition
- Clear role definition with specific expertise
- Integrated audience context into role
- Positive framing of requirements
- Concise, actionable style guidelines
- Natural language throughout

---

## Optimization Rationale

### Qwen3:32b Model Characteristics

1. **Strong Instruction Following**: Excels with clear, structured prompts
2. **Markdown Support**: Better parsing of markdown-formatted instructions
3. **Role-Play Capability**: Responds well to expert persona definitions
4. **Creative Writing**: Strong at generating engaging, natural content
5. **Constraint Handling**: Good at following specific word count and style limits

### Optimization Techniques Applied

#### 1. Structured Markdown Format
- **Why**: Qwen3 parses markdown sections more effectively than plain text
- **How**: Used `#` headers and `**bold**` for hierarchy
- **Benefit**: Clearer separation of role, task, and constraints

#### 2. Integrated Role Definition
- **Why**: Models perform better when the role includes context
- **How**: Combined "expert writer" + "specific audience" in opening line
- **Benefit**: Sets appropriate tone and style from the start

#### 3. Positive Framing
- **Why**: Positive instructions ("Do X") work better than negative ("Don't do Y")
- **How**: Converted most "do not" statements to "write" or "use" statements
- **Benefit**: Model focuses on desired output, not avoidance

#### 4. Concise Style Guidelines
- **Why**: Long lists of rules can confuse priority
- **How**: Grouped related requirements, used bullet points sparingly
- **Benefit**: Clearer hierarchy of importance

#### 5. Natural Language
- **Why**: Qwen3 responds well to conversational prompts
- **How**: Avoided technical jargon like "SYSTEM INSTRUCTION", "OUTPUT RULES"
- **Benefit**: More natural, engaging output

#### 6. Clear Output Format
- **Why**: Explicit format specification prevents meta-commentary
- **How**: Final section clearly states "Start immediately with the hook"
- **Benefit**: Reduces need for post-processing

---

## Expected Results

### Quality Improvements
- **More Engaging Hooks**: Clear emphasis on first sentence impact
- **Better Pacing**: "Consistent energy" and "no filler" guidelines
- **Natural Tone**: Conversational language emphasis
- **Length Compliance**: Clear target/maximum word counts

### Output Consistency
- **Fewer Meta-References**: Stronger constraints against explaining structure
- **Format Compliance**: Clearer "single flowing text" requirement
- **Style Adherence**: Better maintained tone throughout

### Model Performance
- **Faster Generation**: Clearer instructions reduce ambiguity
- **Higher Quality**: Better aligned with model's strengths
- **More Predictable**: Structured format improves consistency

---

## Testing

### Validation
- ✅ Prompt generation method works correctly
- ✅ All seed variation tests pass
- ✅ Configuration tests pass
- ✅ Prompt length appropriate (~1163 chars)

### Manual Testing (if Ollama available)
```python
from T.Content.From.Idea.Title.src import generate_content

# Test with Qwen3:32b
content = generate_content(
    title="The Haunted Lighthouse",
    idea_text="A lighthouse keeper discovers time anomalies",
    target_duration_seconds=90,
    seed="midnight"
)

# Check quality:
# - Hook in first sentence?
# - Natural, engaging language?
# - Stays within word limit?
# - No meta-commentary?
```

---

## Impact

### Files Modified
1. **`ai_content_generator.py`**:
   - Updated `_create_content_prompt()` method
   - Added optimization documentation in docstring
   - Updated module docstring

2. **`README.md`**:
   - Added "Model: Qwen3:32b (Optimized)" section
   - Documented prompt optimization rationale
   - Explained model choice benefits

3. **This Document**: New documentation of optimization approach

### Backward Compatibility
- ✅ API unchanged (same parameters, same return values)
- ✅ All existing tests pass
- ✅ Output format identical
- ✅ Only internal prompt structure modified

---

## Future Enhancements

### Potential Improvements
1. **Few-Shot Examples**: Add 1-2 example outputs in prompt
2. **Temperature Tuning**: Adjust for specific content types
3. **Tone Variants**: Create prompt templates for different tones
4. **A/B Testing**: Compare old vs new prompt quality

### Monitoring
- Track average generation time
- Monitor word count compliance
- Collect user feedback on quality
- Measure hook effectiveness

---

## References

- [Qwen3 Model Card](https://ollama.com/library/qwen3:32b)
- [Prompt Engineering Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- Original Issue: ISSUE-IMPL-004-04

---

**Optimized By**: GitHub Copilot  
**Commit**: (pending)  
**Status**: ✅ Complete & Tested
