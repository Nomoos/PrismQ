# AI Integration for Idea Generation - Fix Documentation

## Problem Statement

The idea generation system was producing template-like text instead of AI-generated content:

```
How Core relates to the attention-grabbing opening or central question
How Core relates to the main idea or premise in 1-2 sentences
The emotional heart of the story centered on Core
```

This template text appeared even when Ollama was running, indicating the AI generation was not being utilized.

## Solution

Integrated AI generation into the `idea_variants.py` module to use Ollama for generating rich, narrative content. **AI generation is now required** - the system will raise an error if Ollama is not available.

### Changes Made

1. **AI Generator Integration** (`idea_variants.py`)
   - Added `AIIdeaGenerator` import and integration
   - Modified `IdeaGenerator.__init__()` to initialize AI generator when available
   - **Raises `RuntimeError` if AI is requested but Ollama is not available**
   - Removed template fallback - AI is now required

2. **Custom Field Generation Prompt** (`field_generation.txt`)
   - Created a specialized prompt for generating field-specific content
   - Instructs AI to generate concrete, specific content (not template-like)
   - Avoids phrases like "relates to" or "for this topic"

3. **Updated Generation Methods**
   - `_generate_focused_content()`: Requires AI, raises error if unavailable
   - `_generate_field_content()`: Requires AI, raises error if unavailable
   - `_try_ai_generation()`: Returns content or raises `RuntimeError`
   - Added comprehensive error messages with setup instructions

### Architecture

```
Input Title → IdeaGenerator
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
AI Available?      Error (RuntimeError)
    ↓
AIIdeaGenerator
    ↓
field_generation.txt
    ↓
Rich AI content
```

## Usage

### Normal Usage (Ollama Running)

```python
from idea_variants import create_ideas_from_input

# Requires Ollama to be running
ideas = create_ideas_from_input("Acadia Night Hikers", count=10)

for idea in ideas:
    print(f"Hook: {idea['hook']}")
    # Output: Rich, narrative content like:
    # "Sarah discovers an ancient map hidden in her grandmother's attic, 
    #  leading to a treasure hunt through Acadia's moonlit trails."
```

### Without Ollama (Will Raise Error)

```python
from idea_variants import IdeaGenerator

# This will raise RuntimeError if Ollama is not available
try:
    gen = IdeaGenerator(use_ai=True)  # Default
    idea = gen.generate_from_flavor("My Title", "Emotion-First Hook")
except RuntimeError as e:
    print(f"Error: {e}")
    # Output: "AI generation requested but Ollama is not available. 
    #          Please ensure Ollama is installed and running..."
```

### Disabling AI (For Testing Only)

```python
from idea_variants import IdeaGenerator

# Explicitly disable AI - but generation will fail
gen = IdeaGenerator(use_ai=False)

try:
    idea = gen.generate_from_flavor("My Title", "Emotion-First Hook")
except RuntimeError as e:
    print(f"Error: {e}")
    # Output: "AI generator not available. Cannot generate ideas without AI..."
```

## Setup Instructions

**AI generation is required.** To use this system, you must install and run Ollama:

1. **Install Ollama**
   ```bash
   # Visit https://ollama.com/ for installation instructions
   ```

2. **Pull a Model**
   ```bash
   ollama pull qwen3:32b  # Recommended for RTX 5090
   # or
   ollama pull qwen2.5:72b-q4_K_M  # Alternative for creative writing
   ```

3. **Start Ollama Server**
   ```bash
   ollama serve
   ```

4. **Run Idea Generation**
   ```bash
   python T/Idea/Creation/src/idea_creation_interactive.py
   ```

## Testing

### Run Demonstration Script

```bash
python T/Idea/Creation/_meta/examples/demo_ai_generation.py
```

This will:
- Attempt to generate ideas with current configuration
- Show clear error if Ollama is not detected
- Provide setup instructions

### Run Tests

```bash
# Run test suite (uses mocked AI)
python T/Idea/Creation/_meta/tests/test_ai_integration.py
```

## Expected Behavior

### With Ollama Running
- Each field contains rich, narrative content
- No template phrases like "How X relates to Y"
- Content is specific to the input and flavor
- Logging shows: "AI generated content for..."

### Without Ollama
- **Raises `RuntimeError` immediately**
- Error message includes setup instructions
- No idea generation occurs

## Verification

To verify AI generation is working:

1. Ensure Ollama is running: `curl http://localhost:11434/api/tags`
2. Run idea generation
3. Check that no errors are raised
4. Verify output contains narrative content (not template phrases)

Example of AI-generated content:
```
Hook: "Under the Acadia moonlight, three friends discover a hidden 
       trail that only appears after midnight, leading them to 
       mysteries their small town has kept buried for decades."

Core Concept: "A coming-of-age adventure where nighttime hikes become 
               a gateway to uncovering family secrets and finding courage 
               in the darkness."
```

## Files Modified

- `T/Idea/Creation/src/idea_variants.py` - Core integration, removed fallback
- `T/Idea/Creation/_meta/prompts/field_generation.txt` - New prompt (created)
- `T/Idea/Creation/_meta/tests/test_ai_integration.py` - Updated tests
- `T/Idea/Creation/AI_INTEGRATION_README.md` - Updated documentation

## Error Messages

### When Ollama is not installed/running:
```
RuntimeError: AI generation requested but Ollama is not available. 
Please ensure Ollama is installed and running. 
Install from https://ollama.com/ and start with 'ollama serve'.
```

### When AI is disabled but generation is attempted:
```
RuntimeError: AI generator not available. Cannot generate ideas without AI. 
Please ensure Ollama is installed and running.
```

### When AI generates insufficient content:
```
RuntimeError: AI generated insufficient content for 'hook'. 
Generated: 15 characters, minimum required: 20.
```

## Troubleshooting

### "Ollama is not available" error
- Check if Ollama is running: `curl http://localhost:11434/api/tags`
- Start Ollama: `ollama serve`
- Verify model is installed: `ollama list`
- If no models, install one: `ollama pull qwen3:32b`

### "AI generated insufficient content" error
- The AI model might need a better prompt
- Try a different model (e.g., qwen2.5:72b)
- Check model temperature setting in AIConfig
- Verify the model is functioning: `ollama run qwen3:32b "test"`

### Firewall blocking port 11434
- Check firewall settings
- Ensure localhost connections are allowed
- Try accessing `http://localhost:11434/api/tags` in a browser
