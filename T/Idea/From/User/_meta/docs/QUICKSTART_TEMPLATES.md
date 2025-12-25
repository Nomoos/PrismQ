# Quick Start: Custom Prompt Templates

## What's New

The PrismQ.T.Idea.From.User module now supports **flexible custom prompt templates** for AI-powered idea generation. You can now use prompts like the one in your issue with `INSERTTEXTHERE` placeholders!

## How to Use with Your Example

The example prompt from your issue is now available as a template:

```python
from T.Idea.From.User.src.ai_generator import AIIdeaGenerator

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

Located at: `T/Idea/From/User/_meta/prompts/idea_improvement.txt`

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

## Example Usage

**Input:** `"Acadia Night Hikers"`

**Output (from AI):** The template will generate exactly 5 sentences that refine this minimal input into a stronger conceptual idea, inferring the underlying intention and expressing it with clearer thematic focus.

## Creating Your Own Templates

### Option 1: Create a Template File

1. Create a new `.txt` file in `T/Idea/From/User/_meta/prompts/`
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
cd T/Idea/From/User/_meta/examples
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
cd T/Idea/From/User/_meta/tests
python test_custom_prompts.py
```

All 22 tests should pass ✅

---

**That's it!** The templating system is ready to use with your custom prompts.
