# Custom Prompt Templates Guide

## Overview

PrismQ's Idea Creation module now supports flexible custom prompt templates for AI-powered idea generation with thematic flavors. This allows you to create and use your own prompts with local AI models (via Ollama), guided by 93 different thematic orientations.

## Features

- **Flexible Placeholder Formats**: Supports `{variable}`, `[FLAVOR]`, and `INSERTTEXTHERE` placeholder formats
- **Thematic Flavors**: 93 flavors derived from all variant templates to guide idea refinement
- **Template Files**: Store reusable prompts in `_meta/prompts/` directory
- **Inline Templates**: Use template strings directly in code
- **Easy Integration**: Works seamlessly with existing AI generation system

## Flavor System

All 93 variant templates have been transformed into thematic flavors that can guide AI-powered idea refinement.

### What are Flavors?

Flavors are thematic orientations derived from variant templates that guide the conceptual refinement of ideas. Examples include:

- **Emotional Drama + Growth** - Focus on emotional depth and character development
- **Mystery + Unease** - Orient toward enigma, discovery, and uncertainty
- **Psychological Tension** - Emphasize internal conflict and mental states
- **Introspective Transformation** - Center on self-discovery and change
- **Existential Conflict** - Explore fundamental questions of identity and meaning
- **Romantic Tension** - Focus on attraction and connection
- **Moral Dilemma** - Emphasize ethical choice and difficult decisions
- ...and 86 more!

### Browsing Flavors

```python
from flavors import list_flavors, list_flavor_categories, search_flavors_by_keyword

# List all flavors (93 total)
all_flavors = list_flavors()
print(f"Total flavors: {len(all_flavors)}")

# Browse by category
categories = list_flavor_categories()
for category, flavors in categories.items():
    print(f"{category}: {len(flavors)} flavors")

# Search by keyword
mystery_flavors = search_flavors_by_keyword("mystery")
emotional_flavors = search_flavors_by_keyword("emotional")
```

### Using Flavors with Templates

The `idea_improvement.txt` template now supports the `[FLAVOR]` placeholder with **weighted random selection**:

```python
from ai_generator import AIIdeaGenerator

generator = AIIdeaGenerator()

# Method 1: Use weighted random flavor (DEFAULT - no flavor parameter needed)
result = generator.generate_with_custom_prompt(
    input_text="Acadia Night Hikers",
    prompt_template_name="idea_improvement"
)
# Automatically selects a weighted random flavor like "Emotional Drama + Growth"
# Higher-weighted flavors (weight 100) are more likely to be selected

# Method 2: Specify a particular flavor
result = generator.generate_with_custom_prompt(
    input_text="Acadia Night Hikers",
    prompt_template_name="idea_improvement",
    flavor="Mystery + Unease"  # Explicit flavor
)

# Method 3: Disable flavor selection
result = generator.generate_with_custom_prompt(
    input_text="Acadia Night Hikers",
    prompt_template_name="idea_improvement",
    use_random_flavor=False  # No flavor applied
)
```

**Flavor Weights**: Each flavor inherits the weight from its variant template. Ultra-primary flavors (weight 100) like "Emotional Drama + Growth", "Identity + Empowerment", and "Body Acceptance Seed" are most likely to be selected, tuned for the primary audience (US girls 13-15).

Different flavors produce different conceptual emphases while maintaining the core idea.

## Quick Start

### 1. Using a Template File

Create a template file in `T/Idea/From/User/_meta/prompts/` (e.g., `my_template.txt`):

```
Analyze this text and provide insights:

{input}

List 3 key themes and explain each.
```

Use it in Python:

```python
from ai_generator import AIIdeaGenerator

generator = AIIdeaGenerator()
result = generator.generate_with_custom_prompt(
    input_text="The Vanishing Tide",
    prompt_template_name="my_template"
)
print(result)
```

### 2. Using an Inline Template

```python
from ai_generator import AIIdeaGenerator

generator = AIIdeaGenerator()

template = """
Task: Improve this story concept.

Original: {input}

Output an improved version:
"""

result = generator.generate_with_custom_prompt(
    input_text="A story about time travel",
    prompt_template=template
)
print(result)
```

### 3. Alternative Placeholder Formats

The system supports multiple placeholder formats:

- `{input}` - Standard Python format string
- `{variable}` - Any named placeholder
- `INSERTTEXTHERE` - Custom format (case-sensitive)
- `INSERT_TEXT_HERE` - Custom format with underscores
- `INSERT TEXT HERE` - Custom format with spaces

Example:

```
Task: Analyze the following text.

Text to analyze:
INSERTTEXTHERE

Provide 3 insights.
```

## Available Functions

### `list_available_prompts()`

Lists all prompt template files in the `_meta/prompts/` directory.

```python
from ai_generator import list_available_prompts

templates = list_available_prompts()
print(templates)  # ['idea_from_title', 'idea_from_description', 'idea_improvement', ...]
```

### `apply_template(template, **kwargs)`

Applies variable substitution to a template string.

```python
from ai_generator import apply_template

template = "Hello {name}, welcome to {place}!"
result = apply_template(template, name="World", place="PrismQ")
print(result)  # "Hello World, welcome to PrismQ!"
```

### `AIIdeaGenerator.generate_with_custom_prompt()`

Generates text using a custom prompt template.

```python
generator = AIIdeaGenerator()

# Using template file
result = generator.generate_with_custom_prompt(
    input_text="Your text",
    prompt_template_name="template_name"
)

# Using inline template
result = generator.generate_with_custom_prompt(
    input_text="Your text",
    prompt_template="Your template with {input} placeholder"
)

# With additional variables
result = generator.generate_with_custom_prompt(
    input_text="Your text",
    prompt_template="Process {input} for {audience}",
    audience="young adults"
)
```

## Example Templates

### Idea Improvement Template

File: `_meta/prompts/idea_improvement.txt`

```
You will rewrite the provided text into a stronger core idea. Your task is to restate 
the underlying conceptual intention with sharper logic, clearer thematic focus, and 
more coherent framing. You must stay within the scope of the original text, but when 
the text is minimal, fragmentary, or ambiguous, you must infer a plausible conceptual 
intention and refine it. You must never state that the text is insufficient; always 
produce a refined idea based on whatever is given. You may use light atmospheric or 
descriptive language, but only in service of clarifying tone or emotional context, 
not to add new content.

Output exactly 5 sentences that express the improved idea. The output may include 
subtle mood or texture, but must remain grounded in the conceptual structure of the 
idea. Do not add new events, scenes, world elements, characters, lore, or emotional 
beats that are not in the source. Keep the language controlled, purposeful, and 
focused on articulating the central thought.

Do not analyze, critique, summarize, or reference the original text. Do not mention 
that you are rewriting. Do not explain your reasoning. Produce only the final refined 
idea as a standalone conceptual statement.

Reinforcement:
Always generate a refined idea, even from minimal input.
The output may include light atmosphere but must remain conceptual.
The output must refine, not expand.
The output must not summarize or comment on the source.
The output must present only the improved idea.
The output must contain exactly 5 sentences.

SOURCE_IDEA: {input}
```

**Example Usage:**

Input: `"Acadia Night Hikers"`

The template will generate exactly 5 sentences that refine this minimal input into a stronger conceptual idea, inferring the underlying intention and expressing it with clearer thematic focus.

### Story Expansion Template

```
Task: Take this concept and expand it into a full story premise.

Concept: {input}

Create a premise that includes:
1. A compelling protagonist with clear motivation
2. A central conflict that escalates
3. Emotional stakes that matter
4. A unique hook that sets it apart

Write the premise in 2-3 engaging paragraphs.
```

### Theme Analysis Template

```
Analyze the following text for themes:

INSERTTEXTHERE

Identify:
- Main themes (2-3)
- Emotional undercurrents
- Potential symbolic elements
- Target audience appeal

Format as a brief analysis.
```

## Integration with Interactive Mode

The custom prompt templates can be integrated into the interactive idea creation workflow:

```python
# In your code
from ai_generator import AIIdeaGenerator

generator = AIIdeaGenerator()

# Set a custom template for the session
custom_prompt = """
Improve this idea: {input}
Focus on clarity and emotional impact.
"""
generator.set_prompt_template(custom_prompt)

# Now all generations will use this template
# (Or use generate_with_custom_prompt for one-off generations)
```

## Best Practices

1. **Clear Instructions**: Be specific about what you want the AI to do
2. **Output Format**: Specify the desired output format explicitly
3. **Constraints**: Include "do not" rules to prevent unwanted behavior
4. **Examples**: Consider including examples in your template when needed
5. **Test Iteratively**: Try your templates with various inputs to refine them

## Troubleshooting

### Ollama Not Available

If you get "Ollama not available" error:

1. Make sure Ollama is installed and running
2. Check that it's accessible at `http://localhost:11434`
3. Verify you have a model downloaded (e.g., `llama3.1:70b-q4_K_M`)

### Template Not Found

If template file is not found:

1. Check the file exists in `T/Idea/From/User/_meta/prompts/`
2. Ensure filename ends with `.txt`
3. Use template name without the `.txt` extension in code

### Placeholder Not Substituted

If placeholders aren't being replaced:

1. Check placeholder format matches supported formats
2. Ensure you're passing the variable with the correct name
3. Use `apply_template()` directly to debug substitution

## Examples

See `_meta/examples/custom_prompt_example.py` for complete working examples.

Run the examples:

```bash
cd T/Idea/From/User/_meta/examples
python custom_prompt_example.py
```

## Advanced Usage

### Multiple Placeholders

```python
template = """
Analyze {input} for a {demographic} audience.
Focus on {theme} themes.
Output format: {format}
"""

result = generator.generate_with_custom_prompt(
    input_text="My Story",
    prompt_template=template,
    demographic="young adults",
    theme="coming-of-age",
    format="bullet points"
)
```

### Chaining Templates

```python
# First pass - improve the idea
improved = generator.generate_with_custom_prompt(
    input_text=original_text,
    prompt_template_name="idea_improvement"
)

# Second pass - expand to full premise
premise = generator.generate_with_custom_prompt(
    input_text=improved,
    prompt_template_name="story_expansion"
)
```

## Contributing Templates

To contribute a new prompt template:

1. Create a `.txt` file in `_meta/prompts/`
2. Use clear, descriptive filename (e.g., `character_development.txt`)
3. Include clear instructions for the AI
4. Test with various inputs
5. Document expected behavior

Example contribution template structure:

```
# Template Name: [Your Template Name]
# Purpose: [What this template does]
# Best for: [What kinds of inputs work best]

[Your actual prompt template here with {input} placeholder]
```
