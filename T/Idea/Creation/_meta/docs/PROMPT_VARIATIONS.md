# Prompt Variation Research for Idea Refinement

## Overview

This document contains high-quality alternative prompt variations for improving text quality in different, controlled ways. All versions are compatible with Qwen/Ollama and maintain core constraints: conceptual rewrite, no expansion, no descriptiveness, controlled flavor orientation.

Each variation produces different strengths and can be selected based on your workflow needs.

---

## 1. Analytical Structure Model (More Organized Thinking)

### Description
Forces the model to internalize a conceptual pattern before generating. Produces very tight logic, less drift, and more sophisticated ideas.

### Prompt Template

```
You will rewrite the provided text into a stronger core idea. Identify its implicit conceptual intention and reconstruct it using a coherent analytical structure focused on causality, purpose, tension, and transformation. Orient the refined idea toward the thematic flavor specified in [FLAVOR], interpreted conceptually rather than descriptively. Do not introduce new events, scenes, or details. Produce exactly 5 sentences that form a unified conceptual statement, following this internal pattern: premise, mechanism, challenge, shift, conceptual outcome. Do not reference rewriting or source text. Output only the final idea.

SOURCE_IDEA: [INSERT TEXT HERE]
```

### Strengths
- Very tight logic
- Less drift
- More sophisticated ideas
- Strong analytical coherence

### Best For
- Complex ideas requiring logical structure
- Technical or conceptual content
- When clarity and rigor are paramount

---

## 2. Contrast-and-Refine Model (Sharper Thematic Output)

### Description
Primes the model to search for the strongest possible conceptual center. Emphasizes central tension or contrast.

### Prompt Template

```
Rewrite the source idea into a clearer, more focused concept. Infer what the idea is fundamentally trying to explore and restate it with stronger thematic clarity shaped by [FLAVOR]. Emphasize the central tension or contrast embedded in the idea, expressed conceptually rather than descriptively. Output exactly 5 sentences forming a single refined idea. Do not summarize, analyze, or reference the original text; only present the final concept.

SOURCE_IDEA: [INSERT TEXT HERE]
```

### Strengths
- Strong central tension
- More dramatic conceptual direction
- Sharp thematic focus
- Clear contrast identification

### Best For
- Ideas with inherent conflict or tension
- Dramatic content
- When thematic clarity is the priority

---

## 3. Minimalist Precision Model (Cleaner, Denser Ideas)

### Description
Strips the writing of fluff and philosophical drift. Uses tight, economical phrasing.

### Prompt Template

```
Rewrite the text into a precise, distilled core idea shaped conceptually by [FLAVOR]. Use tight, economical phrasing and avoid abstraction not inherent in the idea. Output exactly 5 sentences that present the refined idea directly and clearly without atmospherics, imagery, or narrative framing. Output only the idea as a standalone conceptual statement.

SOURCE_IDEA: [INSERT TEXT HERE]
```

### Strengths
- Very crisp ideas
- Reduced ambiguity
- Great for downstream pipelines
- Maximum density

### Best For
- Pipeline integration
- When conciseness is critical
- Technical documentation
- Database storage

---

## 4. Academic Interpretation Model (More Depth Without Descriptiveness)

### Description
Encourages ideas that sound like conceptual frameworks or research constructs.

### Prompt Template

```
Rewrite the provided source idea with clearer internal logic, thematic cohesion, and interpretive depth aligned with [FLAVOR]. Frame the idea as a conceptual investigation rather than a narrative premise. Output exactly 5 sentences presenting a refined theoretical-style idea without imagery or emotional scene-setting. Output only the final refined idea.

SOURCE_IDEA: [INSERT TEXT HERE]
```

### Strengths
- More intellectual tone
- Strong conceptual rigor
- Theoretical framework approach
- Academic quality

### Best For
- Research contexts
- Intellectual property development
- Conceptual analysis
- Framework building

---

## 5. High-Constraint Logic Model (Most Resistant to Drift)

### Description
For models prone to poetic or descriptive drift. Each sentence has a specific conceptual function.

### Prompt Template

```
Rewrite the source idea into a disciplined conceptual statement shaped by [FLAVOR]. Each sentence must introduce one specific conceptual function: a premise, a mechanism, an adaptive pressure, a thematic transformation, and a concluding implication. Avoid all sensory, metaphorical, emotional, or scenic language. Output exactly 5 sentences as the final idea, without commentary or reference to rewriting.

SOURCE_IDEA: [INSERT TEXT HERE]
```

### Strengths
- Very controlled outputs
- Perfect structure for AI pipelines
- Maximum consistency
- Eliminates drift completely

### Best For
- Automated systems
- Strict quality control
- Pipeline consistency
- Production environments

---

## 6. Interpretive Growth Model (Best for Emotional Themes)

### Description
Optimized for emotional flavors. Focuses on internal change and psychological trajectories.

### Prompt Template

```
Rewrite the source idea as a conceptual exploration of internal change, aligned with the thematic flavor [FLAVOR]. Identify the idea's implicit psychological or developmental trajectory and render it as a structured conceptual statement without describing scenes or emotions. Output exactly 5 sentences. Output only the refined idea.

SOURCE_IDEA: [INSERT TEXT HERE]
```

### Strengths
- Clear emotional arc
- No narrative drift
- Strong character development focus
- Psychological depth

### Best For
- Character-driven content
- Emotional themes
- Personal growth narratives
- Relationship dynamics

---

## Comparison Matrix

| Model | Logic Strength | Drift Resistance | Emotional Depth | Technical Clarity | Use Case |
|-------|---------------|------------------|-----------------|-------------------|----------|
| Analytical Structure | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★★ | Complex analysis |
| Contrast-and-Refine | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | Dramatic content |
| Minimalist Precision | ★★★★☆ | ★★★★★ | ★★☆☆☆ | ★★★★★ | Pipelines |
| Academic Interpretation | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★★★ | Research |
| High-Constraint Logic | ★★★★★ | ★★★★★ | ★★☆☆☆ | ★★★★★ | Production |
| Interpretive Growth | ★★★☆☆ | ★★★☆☆ | ★★★★★ | ★★★☆☆ | Emotional themes |

---

## Choosing the Right Model

### By Content Type

**Conceptual/Abstract Ideas** → Analytical Structure or Academic Interpretation

**Dramatic/Conflict-Driven** → Contrast-and-Refine

**Technical/Precise** → Minimalist Precision or High-Constraint Logic

**Character/Emotional** → Interpretive Growth

**Pipeline/Automated** → High-Constraint Logic or Minimalist Precision

### By Output Requirements

**Need consistency?** → High-Constraint Logic

**Need depth?** → Academic Interpretation or Analytical Structure

**Need brevity?** → Minimalist Precision

**Need drama?** → Contrast-and-Refine

**Need emotional arc?** → Interpretive Growth

---

## Implementation Guide

### Creating Template Files

Each variation can be saved as a separate template file:

```
_meta/prompts/
├── idea_improvement.txt                    # Current default
├── idea_improvement_analytical.txt         # Variation 1
├── idea_improvement_contrast.txt           # Variation 2
├── idea_improvement_minimalist.txt         # Variation 3
├── idea_improvement_academic.txt           # Variation 4
├── idea_improvement_high_constraint.txt    # Variation 5
└── idea_improvement_growth.txt             # Variation 6
```

### Usage Example

```python
from ai_generator import AIIdeaGenerator

generator = AIIdeaGenerator()

# Use different variations
result_analytical = generator.generate_with_custom_prompt(
    input_text="Acadia Night Hikers",
    prompt_template_name="idea_improvement_analytical",
    flavor="Mystery + Unease"
)

result_minimalist = generator.generate_with_custom_prompt(
    input_text="Acadia Night Hikers",
    prompt_template_name="idea_improvement_minimalist",
    flavor="Mystery + Unease"
)

# Compare outputs
print("Analytical:", result_analytical)
print("Minimalist:", result_minimalist)
```

### A/B Testing

```python
variations = [
    "idea_improvement_analytical",
    "idea_improvement_contrast",
    "idea_improvement_minimalist",
]

results = {}
for variation in variations:
    results[variation] = generator.generate_with_custom_prompt(
        input_text="Your idea",
        prompt_template_name=variation,
        flavor="Your flavor"
    )

# Evaluate which produces best results for your use case
```

---

## Qwen/Ollama Optimization Notes

All variations are optimized for Qwen models with:

1. **Clear Instructions**: Explicit task definition
2. **Structural Guidance**: Internal patterns specified
3. **Reinforcement**: Constraints repeated at end
4. **No Ambiguity**: Direct, unambiguous language
5. **Output Specification**: Exact format requirements

### Model-Specific Tips

**For Qwen 3.30b:**
- Responds well to structured patterns
- Benefits from explicit conceptual functions
- Minimalist and High-Constraint work best

**For Qwen 2.5 72b:**
- Can handle more complex instructions
- Academic Interpretation produces excellent results
- Better at maintaining emotional depth

**For Llama 3.1 70b:**
- Analytical Structure performs well
- Good balance across all variations
- Less prone to drift with any version

---

## Future Enhancements

### Potential Additional Variations

1. **Genre-Specific Models**: Optimized for sci-fi, fantasy, contemporary, etc.
2. **Audience-Adapted Models**: Tailored for different age groups or demographics
3. **Medium-Specific Models**: For video scripts, prose, social media, etc.
4. **Hybrid Models**: Combining strengths of multiple variations

### Customization

Each variation can be further customized:

```python
# Start with a base variation
base = _load_prompt("idea_improvement_analytical.txt")

# Add custom constraints
custom = base + "\n\nAdditional constraint: Focus on visual storytelling."

# Use with AI
result = generator.generate_with_custom_prompt(
    input_text="Your idea",
    prompt_template=custom,
    flavor="Your flavor"
)
```

---

## Research Source

This research is derived from analysis of high-quality prompting practices for:
- Qwen model family
- Ollama local deployment
- Conceptual refinement tasks
- Production AI pipelines

Validated through:
- Comparative testing across models
- Output quality analysis
- Consistency measurements
- Drift resistance evaluation

---

## See Also

- `FLAVOR_SYSTEM.md` - Complete flavor documentation
- `CUSTOM_PROMPTS.md` - General templating guide
- `flavors.py` - Flavor implementation
- `idea_improvement.txt` - Current default template
