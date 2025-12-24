# Title Review Prompts for qwen3:32b

This directory contains AI prompts optimized for the **qwen3:32b** model for title review tasks.

## Optimization for qwen3:32b

These prompts are designed to work optimally with qwen3:32b by:

1. **Clear Structure**: Using bullet points and numbered lists that Qwen models handle well
2. **Explicit Requirements**: Stating length, tone, and format requirements upfront
3. **JSON Output**: Requesting structured JSON responses which qwen3:32b excels at
4. **Focused Tasks**: Breaking complex evaluation into clear, manageable criteria
5. **Concise Language**: Using direct, analytical language without unnecessary verbosity
6. **Avoidance Clauses**: Explicitly stating what NOT to do (reduces hallucination)
7. **Context-First**: Providing all context before the task for better comprehension

## Available Prompts

### 1. `title_review_v1.txt`
**Purpose**: Comprehensive v1 title review against content and idea

**Use Case**: Initial title evaluation for v1 titles

**Key Features**:
- 4-criteria evaluation (Content, Idea, Engagement, SEO)
- Weighted scoring system
- Specific improvement recommendations
- JSON structured output

**Variables**:
- `{title_text}` - The title to review
- `{content_text}` - The content/script text
- `{idea_summary}` - Core idea summary
- `{target_audience}` - Target audience description

### 2. `title_review_v2_comparison.txt`
**Purpose**: Compare v2 title against v1 and track improvements

**Use Case**: Evaluating title refinements and iteration progress

**Key Features**:
- Score comparison and delta tracking
- Regression detection
- Progress assessment
- Next steps recommendations

**Variables**:
- `{title_v1}` - Previous title version
- `{v1_score}` - Previous score
- `{title_v2}` - Current title version
- `{v2_score}` - Current score
- `{content_text}` - The content/script
- `{v1_feedback}` - Previous review feedback

### 3. `title_quick_review.txt`
**Purpose**: Rapid title assessment for quick feedback

**Use Case**: Fast iteration cycles, preliminary checks

**Key Features**:
- Under 150 words response
- First impression focus
- Single main issue identification
- One actionable fix

**Variables**:
- `{title_text}` - The title to review
- `{brief_context}` - Brief context (1-2 sentences)

## Usage Example

```python
from T.src.ai_config import create_ai_config
import requests

# Load prompt
with open('T/Review/Title/From/Content/_meta/prompts/title_review_v1.txt', 'r') as f:
    prompt_template = f.read()

# Fill in variables
prompt = prompt_template.format(
    title_text="The Echo - A Haunting Discovery",
    content_text="Sarah investigates mysterious sounds...",
    idea_summary="Horror story about echoes in hospital",
    target_audience="Horror short film enthusiasts"
)

# Configure AI (defaults to qwen3:32b)
ai_settings = create_ai_config()

# Call Ollama API
response = requests.post(
    f"{ai_settings.get_api_base()}/api/generate",
    json={
        "model": ai_settings.get_model(),
        "prompt": prompt,
        "temperature": ai_settings.get_random_temperature(),
        "stream": False
    }
)

# Parse JSON response
import json
result = json.loads(response.json()['response'])
```

## Model Configuration

The default AI configuration in `T/src/ai_config.py` is already set for qwen3:32b:

```python
DEFAULT_AI_MODEL = "qwen3:32b"
DEFAULT_AI_API_BASE = "http://localhost:11434"
AI_TEMPERATURE_MIN = 0.6
AI_TEMPERATURE_MAX = 0.8
```

## Prompt Design Principles

### 1. Structured Instructions
Qwen3 responds best to clearly structured prompts with:
- Numbered or bulleted lists
- Clear section headers
- Explicit requirements stated upfront

### 2. JSON Responses
Request JSON format for:
- Structured data extraction
- Consistent parsing
- Type-safe results

### 3. Length Constraints
Always specify maximum response length:
- Prevents verbose outputs
- Ensures focused responses
- Improves response time

### 4. Negative Instructions
Include "Avoid:" sections to:
- Reduce hallucinations
- Prevent common issues
- Focus model behavior

### 5. Context Before Task
Provide all context first, then the task:
- Improves comprehension
- Reduces confusion
- Better quality outputs

## Testing Prompts

To test these prompts with qwen3:32b:

```bash
# 1. Ensure Ollama is running
ollama serve

# 2. Pull the model if needed
ollama pull qwen3:32b

# 3. Run the test script
python T/Review/Title/From/Content/_meta/examples/test_ai_prompts.py
```

## Performance Notes

- **Average Response Time**: 2-5 seconds for v1 review
- **Token Usage**: ~500-800 tokens for full review
- **JSON Parsing Success Rate**: >95% with these prompts
- **Model Temperature**: 0.6-0.8 for good balance of creativity and consistency

## Maintenance

When updating prompts:
1. Test with multiple examples
2. Verify JSON output parsing
3. Check response length stays within limits
4. Validate against qwen3:32b (not other models)
5. Update this README with any changes

## Related Documentation

- AI Configuration: `T/src/ai_config.py`
- Title Review Implementation: `T/Review/Title/From/Content/Idea/by_content_and_idea.py`
- Model Documentation: https://ollama.com/library/qwen3:32b
