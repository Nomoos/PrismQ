# Script Generator Documentation

**Module**: `PrismQ.T.Script.FromIdeaAndTitle`  
**Version**: 0.1.0  
**Status**: MVP Implementation

## Overview

The Script Generator module implements **MVP-003** functionality to create initial script drafts (v1) from an Idea object and a title variant (v1). This is Stage 3 in the MVP workflow:

```
Stage 1: Idea.Creation
    ↓
Stage 2: Title.FromIdea (v1)
    ↓
Stage 3: Script.FromIdeaAndTitle (v1) ← THIS MODULE
    ↓
Stage 4: Review.Title.ByScript
```

## Features

### Core Functionality
- Generate structured scripts with introduction, body, and conclusion
- Multiple structure types (hook-deliver-cta, three-act, problem-solution, story)
- Platform optimization (YouTube shorts, TikTok, Instagram Reels)
- Duration targeting with automatic estimation
- Coherence with title promises and idea intent
- Configurable tone and style

### Script Structures

#### 1. Hook-Deliver-CTA (Default)
Best for: Engaging short-form content
- **Hook/Introduction** (15%): Grab attention immediately
- **Delivery/Body** (70%): Deliver on title promise
- **CTA/Conclusion** (15%): Call-to-action and conclusion

#### 2. Three-Act
Best for: Narrative storytelling
- **Act 1** (25%): Setup and establish context
- **Act 2** (50%): Development and build tension
- **Act 3** (25%): Resolution and conclusion

#### 3. Problem-Solution
Best for: Educational and explanatory content
- **Problem** (30%): Establish the problem or question
- **Investigation** (50%): Explore and investigate
- **Solution** (20%): Present solution or conclusion

#### 4. Story
Best for: Narrative content
- **Beginning** (25%): Setup
- **Middle** (50%): Development
- **End** (25%): Resolution

### Platform Targets

- **YOUTUBE_SHORT**: < 60 seconds
- **YOUTUBE_MEDIUM**: 60-180 seconds (default: 90s)
- **YOUTUBE_LONG**: > 180 seconds
- **TIKTOK**: < 60 seconds
- **INSTAGRAM_REEL**: < 90 seconds
- **GENERAL**: No specific constraints

## Usage

### Basic Usage

```python
from PrismQ.T.Script.FromIdeaAndTitle import ScriptGenerator
from PrismQ.T.Idea.Model import Idea

# Create or load an idea
idea = Idea(
    id="mystery-001",
    title="The Abandoned Lighthouse",
    concept="A mysterious lighthouse that still operates despite being abandoned",
    premise="Every night at 9 PM, the lighthouse beam turns on...",
    hook="What if the keeper never really left?",
    synopsis="A deep dive into the coast's most enduring mystery..."
)

# Generate script
generator = ScriptGenerator()
script = generator.generate_script_v1(
    idea=idea,
    title="The Mystery of the Abandoned Lighthouse"
)

print(f"Script Duration: {script.total_duration_seconds} seconds")
print(f"Sections: {len(script.sections)}")
print(script.full_text)
```

### YouTube Short Optimization

```python
from PrismQ.T.Script.FromIdeaAndTitle import (
    ScriptGenerator,
    ScriptGeneratorConfig,
    PlatformTarget,
    ScriptStructure
)

# Configure for YouTube short
config = ScriptGeneratorConfig(
    platform_target=PlatformTarget.YOUTUBE_SHORT,
    target_duration_seconds=60,
    structure_type=ScriptStructure.HOOK_DELIVER_CTA,
    tone="dramatic"
)

generator = ScriptGenerator(config)
script = generator.generate_script_v1(idea, title)
```

### Custom Configuration with Overrides

```python
generator = ScriptGenerator()

script = generator.generate_script_v1(
    idea=idea,
    title=title,
    platform_target=PlatformTarget.YOUTUBE_MEDIUM,
    target_duration_seconds=120,
    structure_type=ScriptStructure.PROBLEM_SOLUTION,
    tone="educational",
    include_cta=True,
    script_id="custom-script-001"
)
```

## API Reference

### ScriptGenerator

Main class for generating scripts.

**Constructor**:
```python
ScriptGenerator(config: Optional[ScriptGeneratorConfig] = None)
```

**Methods**:

#### generate_script_v1()
```python
def generate_script_v1(
    idea: Idea,
    title: str,
    script_id: Optional[str] = None,
    **kwargs
) -> ScriptV1
```

Generates initial script (v1) from idea and title.

**Parameters**:
- `idea` (Idea): Source Idea object
- `title` (str): Title variant (v1) to use
- `script_id` (str, optional): Custom script ID
- `**kwargs`: Configuration overrides

**Returns**: ScriptV1 object

**Raises**: ValueError if inputs are invalid

### ScriptGeneratorConfig

Configuration for script generation.

**Attributes**:
- `platform_target` (PlatformTarget): Target platform
- `target_duration_seconds` (int): Target duration in seconds (default: 90)
- `structure_type` (ScriptStructure): Script structure to use
- `words_per_second` (float): Narration speed (default: 2.5)
- `include_cta` (bool): Include call-to-action (default: True)
- `tone` (str): Script tone - "engaging", "mysterious", "educational", "dramatic", "conversational"

### ScriptV1

Generated script object.

**Attributes**:
- `script_id` (str): Unique identifier
- `idea_id` (str): Reference to source idea
- `title` (str): Title used for generation
- `full_text` (str): Complete script text
- `sections` (List[ScriptSection]): Script sections
- `total_duration_seconds` (int): Estimated total duration
- `structure_type` (ScriptStructure): Structure type used
- `platform_target` (PlatformTarget): Target platform
- `metadata` (Dict): Additional metadata
- `created_at` (str): Creation timestamp
- `version` (str): Version number (always "v1")
- `notes` (str): Additional notes

**Methods**:
- `get_section(section_type: str) -> Optional[ScriptSection]`: Get specific section
- `to_dict() -> Dict[str, Any]`: Convert to dictionary

### ScriptSection

A section of the script.

**Attributes**:
- `section_type` (str): Section type ("introduction", "body", "conclusion")
- `content` (str): Section content
- `estimated_duration_seconds` (int): Estimated duration
- `purpose` (str): Section purpose
- `notes` (str): Additional notes

## Examples

See `_meta/examples/example_usage.py` for complete examples including:
- Basic script generation
- YouTube short optimization
- Educational content creation
- Custom configuration

## Testing

Run tests with pytest:

```bash
cd T/Script/FromIdeaAndTitle/_meta/tests
pytest test_script_generator.py -v
```

Test coverage includes:
- Basic functionality
- Different script structures
- Platform targets
- Configuration overrides
- Content generation
- Edge cases

## Integration

### Input Dependencies

**MVP-002: Title.FromIdea**
- Provides title v1 variants
- Script generator expects a selected title string

**MVP-001: Idea.Creation**
- Provides Idea object with:
  - Core concept
  - Target audience
  - Content theme
  - Key message
  - Premise, hook, synopsis

### Output Usage

**MVP-004: Review.Title.ByScript**
- Reviews title v1 against generated script v1

**MVP-005: Review.Script.ByTitle**
- Reviews script v1 against title v1

## Best Practices

1. **Choose Appropriate Structure**: Match structure to content type
   - Use Hook-Deliver-CTA for short-form engaging content
   - Use Problem-Solution for educational content
   - Use Three-Act for narrative storytelling

2. **Target Duration**: Set realistic duration targets
   - YouTube Short: 45-60 seconds
   - YouTube Medium: 90-120 seconds
   - Full videos: 180+ seconds

3. **Tone Selection**: Match tone to content and audience
   - Dramatic for horror/thriller
   - Educational for how-to/explainer
   - Conversational for lifestyle/vlog

4. **Use Idea Content**: Ensure ideas have rich content
   - Detailed premise and synopsis
   - Clear hook
   - Defined themes and keywords

## Limitations

This MVP implementation includes:
- Template-based content generation
- Simple keyword extraction
- Basic tone detection
- Fixed structure percentages

Future enhancements will include:
- AI-powered content generation
- Dynamic structure adaptation
- Advanced NLP for analysis
- Multiple script variants
- SEO optimization

## Version History

- **v0.1.0** (2024-11-22): Initial MVP implementation
  - Basic script generation
  - Multiple structure types
  - Platform optimization
  - Comprehensive test suite

## See Also

- [Module README](../../README.md)
- [Examples](../examples/example_usage.py)
- [Tests](../tests/test_script_generator.py)
- [T/Script Documentation](../../../README.md)
