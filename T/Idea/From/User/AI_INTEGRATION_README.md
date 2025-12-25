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

2. **Idea Improvement Prompt** (`idea_improvement.txt`)
   - Uses the user-specified prompt format with `[FLAVOR]` and `[INPUT]` placeholders
   - Generates exactly 5 sentences that express a refined, improved idea
   - Allows "light atmospheric or descriptive language" for tone/context
   - Remains conceptual while incorporating thematic flavor influence
   - **Output stored as single paragraph (not parsed into fields)**

3. **Updated Generation Methods**
   - `generate_from_flavor()`: Uses `idea_improvement` prompt to generate complete 5-sentence idea
   - **Stores complete paragraph in 'hook' field only** (other fields left empty)
   - **20% chance to add a second flavor** for richer thematic influence
   - Dual flavors shown as "Flavor1 + Flavor2" in variant name
   - Raises `RuntimeError` if AI unavailable or generates insufficient content
   - Added comprehensive error messages with setup instructions

4. **Placeholder Updates** (`ai_generator.py`)
   - Changed from `[INSERT TEXT HERE]` to simpler `[INPUT]`
   - Also supports `[TEXT]` as alternative placeholder
   - Maintains backward compatibility

### Architecture

```
Input Title → IdeaGenerator
              ↓
    ┌─────────┴─────────┐
    ↓                   ↓
AI Available?      Error (RuntimeError)
    ↓
Select Flavor(s) (20% chance for dual flavor)
    ↓
AIIdeaGenerator
    ↓
idea_improvement.txt (with [FLAVOR] and [INPUT])
    ↓
5-sentence refined idea (single paragraph)
    ↓
Store in 'hook' field
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
    print(f"Variant: {idea['variant_name']}")
    # May show dual flavor: "Identity + Empowerment + Teen Girl Drama"
    
    print(f"Idea: {idea['hook']}")
    # Output: Complete 5-sentence paragraph, e.g.:
    # "Three friends discover the Acadia trails transform after midnight 
    #  into pathways of bioluminescent moss and ancient whispers. The night 
    #  hikes become rituals of self-discovery, where darkness provides cover 
    #  for vulnerability and authentic connection. Each participant carries 
    #  a secret fear or doubt that the natural setting gradually brings to 
    #  light. The group dynamic shifts from casual friendship to chosen family 
    #  through shared moments of wonder and honesty. The story speaks to those 
    #  who find themselves more at home in liminal spaces than conventional 
    #  daylight interactions."
```

### Prompt Format

The system uses `idea_improvement.txt` with these placeholders:
- `[FLAVOR]` - Thematic flavor (single or dual: "Flavor1" or "Flavor1 and Flavor2")
- `[INPUT]` - Source idea/title to refine (simplified from `[INSERT TEXT HERE]`)

The prompt generates exactly 5 sentences as a single continuous paragraph:
- **Stored in**: `hook` field only
- **Other fields**: Left empty (not parsed)
- **Dual flavors**: 20% chance to combine two flavors for richer themes

### Second Flavor Feature

```python
from idea_variants import IdeaGenerator

gen = IdeaGenerator(use_ai=True)

# Default: 20% chance of dual flavor
idea1 = gen.generate_from_flavor("My Title", "Mystery/Curiosity Gap")

# Explicit control: 50% chance of dual flavor
idea2 = gen.generate_from_flavor(
    "My Title", 
    "Mystery/Curiosity Gap",
    second_flavor_chance=0.5
)

# No second flavor: 0% chance
idea3 = gen.generate_from_flavor(
    "My Title", 
    "Mystery/Curiosity Gap",
    second_flavor_chance=0.0
)
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
   python T/Idea/From/User/src/idea_creation_interactive.py
   ```

## Testing

### Run Demonstration Script

```bash
python T/Idea/From/User/_meta/examples/demo_ai_generation.py
```

This will:
- Attempt to generate ideas with current configuration
- Show clear error if Ollama is not detected
- Provide setup instructions

### Run Tests

```bash
# Run test suite (uses mocked AI)
python T/Idea/From/User/_meta/tests/test_ai_integration.py
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

- `T/Idea/From/User/src/idea_variants.py` - Core integration, removed fallback
- `T/Idea/From/User/_meta/prompts/field_generation.txt` - New prompt (created)
- `T/Idea/From/User/_meta/tests/test_ai_integration.py` - Updated tests
- `T/Idea/From/User/AI_INTEGRATION_README.md` - Updated documentation

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
