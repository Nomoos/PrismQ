# Improved One-by-One Title Generation

## Overview

This document describes the improved one-by-one title generation approach that prioritizes **accuracy and quality** over speed.

## Rationale

After initial implementation of single-call generation (10 titles in one API call), we reverted to the one-by-one approach based on user feedback prioritizing:
1. **Accuracy/Exactness** (přesnost/exaktnost)
2. **Quality** over performance
3. **Creative diversity** through randomized temperature

## Key Improvements

### 1. One-by-One Generation with Random Temperature

**Implementation:**
```python
for i in range(n_variants):
    # Random temperature in sweet spot for creative titles
    temp = random.uniform(0.6, 0.8)
    
    # Generate title from AI
    response_text = self.ollama_client.generate(prompt, temperature=temp)
    
    # Parse and score the response
    variant = self._parse_response(response_text, idea)
    if variant:
        variants.append(variant)
```

**Benefits:**
- **Higher quality**: AI focuses on ONE high-quality title per call
- **Creative diversity**: Random temperature (0.6-0.8) ensures varied outputs
- **Less formulaic**: Reduced risk of repetitive or templated titles
- **Better accuracy**: Each generation is independent and thoughtful

### 2. Updated Length Criteria (40-60 Characters)

**Old criteria:** 45-52 characters
**New criteria:** 40-60 characters

**Rationale:**
- Wider range accommodates more creative expression
- Based on user-specified evaluation criteria
- Better readability across different platforms

**Scoring configuration:**
```python
ideal_length_min: int = 40
ideal_length_max: int = 60
good_length_min: int = 35
good_length_max: int = 65
acceptable_length_max: int = 70
```

### 3. Direct Idea Insertion (No Analysis)

**Maintained from previous improvement:**
- Idea text is inserted directly into prompt template
- No preprocessing or content analysis
- Cleaner, more predictable behavior

```python
def _create_prompt(self, idea: Idea) -> str:
    """Create the title generation prompt.
    
    This method directly inserts the Idea text into the prompt template
    without any analysis or preprocessing.
    """
    idea_text = idea.concept or idea.title or "No idea provided"
    template = self.prompt_loader.get_title_generation_prompt()
    return template.format(IDEA=idea_text)
```

### 4. Quality Scoring and Sorting

**New feature:**
- Variants are sorted by quality score (highest first)
- Ensures best titles are prioritized

```python
# Sort by score (highest first) for better quality results
variants.sort(key=lambda v: v.score, reverse=True)
```

### 5. Enhanced Logging

**Improved debugging:**
```python
logger.info(f"Generating {n_variants} title variants (one-by-one for quality)")
logger.debug(f"Generating title {i+1}/{n_variants} with temperature={temp:.2f}")
logger.debug(f"  Generated: '{variant.text}' (score={variant.score:.2f})")
```

## Prompt Template

**Updated to request ONE title:**
```
Your objective: Using the idea below, create one title that is vivid, intriguing, 
and emotionally resonant.

Title requirements:
- Length between 40-60 characters (ideal range for readability and engagement)
- Include one natural primary keyword from the idea
- Prioritize emotional depth, curiosity, intimacy, mystery, or psychological nuance
- ...

Output only the title with no commentary or quotation marks
```

## Performance Trade-offs

### Speed
- **Old (single call):** ~1 API call, ~5-10 seconds total
- **New (one-by-one):** ~10 API calls, ~50-100 seconds total

### Quality
- **Old (single call):** Faster but potentially less diverse, risk of formulaic outputs
- **New (one-by-one):** Slower but higher quality, more creative diversity

## Evaluation Criteria

As specified by the user:

1. **Délka (Length):** Ideal 40-60 characters
   - Scored using `TitleScorer.score_by_length()`
   - Ideal range: 40-60 chars (score: 0.95)
   - Good range: 35-65 chars (score: 0.90)

2. **Čitelnost (Readability):**
   - Ensured through prompt requirements
   - Scored through length optimization
   - Book-style narrative focus

## Testing

All tests updated and passing:
- ✅ `test_initialization` - Generator initializes correctly
- ✅ `test_generate_from_idea` - One-by-one generation with 3 calls
- ✅ `test_prompt_uses_literary_template` - Prompt validation
- ✅ `test_unavailable_raises_error` - Error handling

## Files Modified

1. **`T/Title/From/Idea/_meta/prompts/title_generation.txt`**
   - Request ONE title (not 10)
   - Updated length criteria to 40-60 characters

2. **`T/Title/From/Idea/src/ai_title_generator.py`**
   - Reverted to loop-based generation
   - Added random temperature per call
   - Added quality sorting
   - Enhanced logging
   - Removed multiline parsing method

3. **`T/Title/From/Idea/src/title_scorer.py`**
   - Updated scoring ranges to 40-60 characters
   - Updated documentation

4. **`T/Title/From/Idea/_meta/tests/test_refactored_modules.py`**
   - Updated mock to single response per call
   - Added call count verification

5. **`T/Title/From/Idea/README.md`**
   - Updated process description
   - Reflected new length criteria

## Conclusion

This improved one-by-one approach prioritizes **quality and accuracy** as requested:
- ✅ Higher quality through focused generation
- ✅ Creative diversity through random temperature
- ✅ Updated length criteria (40-60 chars)
- ✅ Direct idea insertion maintained
- ✅ Quality scoring and sorting
- ✅ All tests passing

The trade-off is slower generation (~10x), but this is acceptable given the user's explicit preference for accuracy over performance.
