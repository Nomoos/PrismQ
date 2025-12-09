# Quick Start: Custom Prompt Templates

## What's New

The PrismQ.T.Idea.Creation module now supports **flexible custom prompt templates** for AI-powered idea generation. You can now use prompts like the one in your issue with `INSERTTEXTHERE` placeholders!

## How to Use with Your Example

The example prompt from your issue is now available as a template:

```python
from T.Idea.Creation.src.ai_generator import AIIdeaGenerator

# Initialize the generator
generator = AIIdeaGenerator()

# Use the idea_improvement template (your example!)
result = generator.generate_with_custom_prompt(
    input_text="The Vanishing Tide",
    prompt_template_name="idea_improvement"
)

print(result)
```

## The Template File

Located at: `T/Idea/Creation/_meta/prompts/idea_improvement.txt`

```
Task:
Analyze the following text and identify its core weaknesses in concept, logic, 
worldbuilding, clarity, or thematic intention. Use these weaknesses to redesign 
the idea into a stronger, clearer, more compelling version.

Rules:

Do not summarize the text.
Do not review pacing or structure.
Do not describe the audience.
Do not explain your reasoning.
Do not output critique.
Do not output lists, sections, or commentary.

Output only the final improved idea as a short, self-contained concept.

Now analyze this text and produce the improved idea:

{input}
```

## Creating Your Own Templates

### Option 1: Create a Template File

1. Create a new `.txt` file in `T/Idea/Creation/_meta/prompts/`
2. Use `{input}` or `INSERTTEXTHERE` as placeholders
3. Use it by name:

```python
result = generator.generate_with_custom_prompt(
    input_text="Your text",
    prompt_template_name="your_template_name"
)
```

### Option 2: Use Inline Templates

```python
my_template = """
Task: Analyze this text and provide insights.

Text: INSERTTEXTHERE

Provide 3 key insights.
"""

result = generator.generate_with_custom_prompt(
    input_text="The Vanishing Tide",
    prompt_template=my_template
)
```

## Supported Placeholder Formats

All of these work:

- `{input}` - Standard Python format
- `INSERTTEXTHERE` - Your requested format
- `INSERT_TEXT_HERE` - With underscores
- `INSERT TEXT HERE` - With spaces

## Example Output

When you run with "The Vanishing Tide":

```
Input: The Vanishing Tide

Processing with idea_improvement template...

Result:
[AI will analyze and output an improved version of the idea]
```

## Running the Examples

```bash
cd T/Idea/Creation/_meta/examples
python custom_prompt_example.py
```

This will show you all the different ways to use the templating system.

## Documentation

- **[CUSTOM_PROMPTS.md](../CUSTOM_PROMPTS.md)** - Complete guide
- **[README.md](../README.md)** - Updated with examples
- **[custom_prompt_example.py](../_meta/examples/custom_prompt_example.py)** - Working code

## Requirements

- Ollama must be running (`ollama serve`)
- A model must be installed (e.g., `ollama pull llama3.1:70b-q4_K_M`)

## Testing

Run the test suite:

```bash
cd T/Idea/Creation/_meta/tests
python test_custom_prompts.py
```

All 22 tests should pass ✅

---

**That's it!** The templating system is ready to use with your custom prompts.
