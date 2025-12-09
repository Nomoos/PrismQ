# AI-Powered SEO Metadata Generation (POST-001)

**Worker13: Prompt Engineering Master**

## Overview

This module extends the SEO Keywords functionality with AI-powered metadata generation using GPT/LLM models via Ollama. It implements prompt engineering best practices to generate high-quality, SEO-optimized metadata.

## Features

### 🤖 AI-Powered Generation
- **Meta Descriptions**: Keyword-rich, compelling descriptions (150-160 chars)
- **Title Tags**: Optimized, click-worthy titles (<60 chars)
- **Open Graph Metadata**: Social media-optimized descriptions
- **Related Keywords**: Context-aware keyword suggestions

### 🎯 Prompt Engineering
- Role-based prompts (SEO expert persona)
- Clear constraints and guidelines
- Output formatting instructions
- Best practice integration
- Chain-of-thought reasoning

### 🔄 Graceful Fallback
- Automatic fallback to rule-based generation
- No dependency on AI availability
- Consistent quality guarantees

## Quick Start

### Basic Usage

```python
from T.Publishing.SEO.Keywords import process_content_seo

# AI-powered metadata generation
result = process_content_seo(
    title="Your Content Title",
    script="Your content text...",
    use_ai=True,  # Enable AI generation
    brand_name="YourBrand"
)

print(f"Meta Description: {result['meta_description']}")
print(f"Title Tag: {result['title_tag']}")
print(f"Quality Score: {result['quality_score']}/100")
print(f"AI Generated: {result['ai_generated']}")
```

### Advanced Usage

```python
from T.Publishing.SEO.Keywords import generate_ai_seo_metadata, AIConfig
from T.Publishing.SEO.Keywords import extract_keywords

# Step 1: Extract keywords
extraction = extract_keywords(
    title="How to Learn Python",
    script="Python is a versatile programming language...",
    method="tfidf"
)

# Step 2: Configure AI (using default Qwen 3:30B model)
config = AIConfig(
    model="qwen3:32b",  # Default local AI model
    temperature=0.3,  # Lower for more focused output
    max_tokens=500,
    enable_ai=True
)

# Step 3: Generate AI metadata
metadata = generate_ai_seo_metadata(
    title="How to Learn Python",
    script="Python is a versatile programming language...",
    primary_keywords=extraction.primary_keywords,
    secondary_keywords=extraction.secondary_keywords,
    keyword_density=extraction.keyword_density,
    config=config,
    brand_name="TechEdu"
)

print(metadata.meta_description)
print(metadata.title_tag)
print(metadata.quality_score)
```

## Configuration

### AIConfig Options

```python
from T.Publishing.SEO.Keywords import AIConfig

config = AIConfig(
    model="qwen3:32b",  # Default local AI model (Ollama)
    api_base="http://localhost:11434",  # Ollama API URL
    temperature=0.3,  # 0.0-2.0 (lower = more focused)
    max_tokens=500,  # Maximum tokens to generate
    timeout=30,  # Request timeout in seconds
    enable_ai=True  # Enable/disable AI generation
)
```

### Default Local AI Model

PrismQ uses **Qwen 3:30B** (`qwen3:32b`) as the default local AI model. This model provides an excellent balance of quality and speed for content generation tasks.

**Why Qwen 3:30B?**
- Strong reasoning and instruction-following capabilities
- Well-suited for content generation and SEO tasks
- Good balance between model size and inference speed
- Strong multilingual support
- Works well with Ollama on consumer hardware

**Setup**:
```bash
# Install Ollama
# Visit: https://ollama.com/

# Pull the default model
ollama pull qwen3:32b

# Start the server
ollama serve
```

### Model Recommendations

**Default Model**:
- `qwen3:32b` - Default choice, excellent balance of quality and speed

**Alternative Models for Higher Performance (RTX 5090)**:
- `llama3.1:70b-q4_K_M` - Excellent quality, optimized quantization
- `llama3.1:70b-q8_0` - Highest quality, more VRAM

**Alternative Models for Faster Inference**:
- `qwen3:8b` - Faster, good quality
- `llama3.1:8b` - Faster, good quality
- `mistral:7b` - Fast inference
- `mixtral:8x7b` - High quality

### Temperature Settings

- **0.2-0.3**: Focused, consistent SEO metadata (recommended)
- **0.4-0.6**: Balanced creativity and consistency
- **0.7-0.9**: More creative variations

## Prompt Engineering

### Meta Description Prompt

The meta description prompt is engineered to:
- Define clear role (SEO expert)
- Specify exact character limits (150-160)
- Require keyword integration
- Emphasize call-to-action
- Match search intent
- Avoid keyword stuffing

**Key Elements**:
```
- Role definition: "You are an expert SEO specialist"
- Clear constraints: "EXACTLY between 150-160 characters"
- Keyword requirements: "Naturally incorporates at least ONE primary keyword"
- Best practices: "Uses active voice and includes a call-to-action"
- Output format: "Return ONLY the meta description text"
```

### Title Tag Prompt

The title tag prompt is optimized for:
- Search engine visibility
- Click-through rate
- Keyword placement
- Brand integration
- Character limits

**Key Elements**:
```
- SEO optimization focus
- Maximum character limit (60 chars before brand)
- Keyword incorporation
- Front-loading important keywords
- Compelling, click-worthy phrasing
```

### Related Keywords Prompt

The related keywords prompt uses:
- Semantic analysis
- Search intent understanding
- Topical relevance
- JSON output formatting

**Key Elements**:
```
- Context understanding from content
- Semantic relationship to primary keywords
- User search intent consideration
- Commonly searched terms
- Structured JSON output
```

### Open Graph Prompt

The OG description prompt focuses on:
- Social media engagement
- Emotional hooks
- Conversational tone
- Platform optimization

**Key Elements**:
```
- Social media optimization
- Engaging and conversational
- Emotional hooks and curiosity gaps
- 200 character limit
- More descriptive than meta description
```

## API Reference

### AIMetadataGenerator

Main class for AI-powered metadata generation.

```python
from T.Publishing.SEO.Keywords import AIMetadataGenerator, AIConfig

config = AIConfig(enable_ai=True)
generator = AIMetadataGenerator(
    config=config,
    brand_name="YourBrand",
    include_brand=True
)

# Generate meta description
description = generator.generate_meta_description(
    title="Content Title",
    script="Content text...",
    primary_keywords=["keyword1", "keyword2"],
    target_length=155
)

# Generate title tag
title_tag = generator.generate_title_tag(
    title="Content Title",
    primary_keywords=["keyword1", "keyword2"]
)

# Generate related keywords
related = generator.suggest_related_keywords(
    title="Content Title",
    script="Content text...",
    primary_keywords=["keyword1", "keyword2"],
    max_suggestions=10
)

# Generate OG description
og_desc = generator.generate_og_description(
    title="Content Title",
    script="Content text...",
    meta_description="Meta description text",
    primary_keywords=["keyword1", "keyword2"]
)
```

### Methods

#### `generate_meta_description()`
Generate SEO-optimized meta description using AI.

**Parameters**:
- `title` (str): Content title
- `script` (str): Content script/body
- `primary_keywords` (List[str]): Primary keywords
- `target_length` (int): Target character count (default: 155)

**Returns**: str (150-160 characters)

#### `generate_title_tag()`
Generate SEO-optimized title tag using AI.

**Parameters**:
- `title` (str): Original title
- `primary_keywords` (List[str]): Primary keywords

**Returns**: str (<60 characters with brand)

#### `suggest_related_keywords()`
Generate related keyword suggestions using AI.

**Parameters**:
- `title` (str): Content title
- `script` (str): Content script
- `primary_keywords` (List[str]): Existing primary keywords
- `max_suggestions` (int): Maximum number of suggestions

**Returns**: List[str] (up to max_suggestions keywords)

#### `generate_og_description()`
Generate Open Graph description for social media.

**Parameters**:
- `title` (str): Content title
- `script` (str): Content script
- `meta_description` (str): Already generated meta description
- `primary_keywords` (List[str]): Primary keywords

**Returns**: str (up to 200 characters)

## Fallback Behavior

When AI is unavailable (Ollama not running or disabled), the system automatically falls back to rule-based generation:

```python
from T.Publishing.SEO.Keywords import process_content_seo, AIConfig

# Configure AI as disabled
config = AIConfig(enable_ai=False)

# This will use rule-based fallback
result = process_content_seo(
    title="Content Title",
    script="Content text...",
    use_ai=True,  # Requested AI
    ai_config=config
)

# Check if AI was actually used
print(f"AI Generated: {result['ai_generated']}")  # False
```

**Fallback Features**:
- Rule-based meta description from first sentences
- Title tag optimization with brand
- Character limit enforcement
- Keyword presence validation

## Best Practices

### 1. Use Hybrid Keyword Extraction
```python
result = process_content_seo(
    title=title,
    script=script,
    extraction_method="hybrid",  # Best of TF-IDF and frequency
    use_ai=True
)
```

### 2. Set Appropriate Temperature
- Use 0.2-0.3 for consistent, focused SEO metadata
- Avoid high temperatures (>0.7) for SEO tasks

### 3. Include Brand Name
```python
result = process_content_seo(
    title=title,
    script=script,
    use_ai=True,
    brand_name="YourBrand"  # Improves brand visibility
)
```

### 4. Validate Quality Score
```python
if result['quality_score'] < 80:
    print("Review recommendations:")
    for rec in result['recommendations']:
        print(f"  - {rec}")
```

### 5. Handle AI Unavailability
```python
try:
    result = process_content_seo(
        title=title,
        script=script,
        use_ai=True
    )
except Exception as e:
    print(f"AI generation failed, using fallback: {e}")
```

## Performance

### AI Generation Times
- Meta Description: ~2-5 seconds
- Title Tag: ~1-3 seconds
- Related Keywords: ~3-6 seconds
- OG Description: ~2-4 seconds

**Total**: ~10-18 seconds for complete AI metadata generation

### Optimization Tips
- Use lower temperature for faster generation
- Reduce max_tokens to 400-500
- Consider caching results
- Use batch processing for multiple articles

## Testing

Run tests with:

```bash
# All SEO tests
pytest T/Publishing/SEO/Keywords/_meta/tests/ -v

# AI-specific tests
pytest T/Publishing/SEO/Keywords/_meta/tests/test_ai_metadata_generator.py -v

# Integration tests
pytest T/Publishing/SEO/Keywords/_meta/tests/test_integration.py -v
```

## Examples

See detailed examples in:
- `_meta/examples/ai_usage_example.py` - Comprehensive AI usage examples
- `_meta/examples/usage_example.py` - General SEO usage examples

Run examples:
```bash
cd /home/runner/work/PrismQ/PrismQ
python -m T.Publishing.SEO.Keywords._meta.examples.ai_usage_example
```

## Troubleshooting

### Ollama Not Available

**Symptom**: "Ollama not available" warning

**Solutions**:
1. Install Ollama: https://ollama.com/
2. Pull the default model: `ollama pull qwen3:32b`
3. Start server: `ollama serve`
4. Check connection: `curl http://localhost:11434/api/tags`

### AI Generation Fails

**Symptom**: RuntimeError or timeout

**Solutions**:
1. Check Ollama is running: `ollama list`
2. Increase timeout in AIConfig
3. Try smaller model (qwen3:8b or llama3.1:8b)
4. Check system resources (GPU/RAM)

### Low Quality Scores

**Symptom**: Quality score <70

**Solutions**:
1. Review recommendations in result
2. Adjust temperature (try 0.2-0.3)
3. Use hybrid keyword extraction
4. Ensure sufficient content length (>300 words)

### Inconsistent AI Output

**Symptom**: Varying metadata quality

**Solutions**:
1. Lower temperature to 0.2
2. Use more specific prompts
3. Validate output length programmatically
4. Implement retry logic

## Architecture

```
T/Publishing/SEO/Keywords/
├── __init__.py                    # Main module entry point
├── keyword_extractor.py           # NLP-based keyword extraction
├── metadata_generator.py          # Rule-based metadata generation
├── ai_metadata_generator.py       # AI-powered metadata generation ⭐
└── _meta/
    ├── tests/
    │   ├── test_keyword_extractor.py
    │   ├── test_metadata_generator.py
    │   ├── test_ai_metadata_generator.py  # AI tests ⭐
    │   └── test_integration.py
    ├── examples/
    │   ├── usage_example.py
    │   └── ai_usage_example.py            # AI examples ⭐
    └── docs/
        └── AI_METADATA.md                 # This file ⭐
```

## Related Documentation

- [POST-001 Specification](../../../_meta/issues/new/POST-MVP-Enhancements/POST-001-SEO-Keywords.md)
- [Module README](../README.MD)
- [Full API Documentation](./README.md)
- [Worker13 Profile](../../../../../_meta/issues/new/Worker13/README.md)

## Credits

**Implementation**: POST-001  
**Worker**: Worker13 (Prompt Engineering Master)  
**Status**: Production Ready  
**Created**: 2025-11-23

---

For questions or issues, see the main [PrismQ documentation](../../../../../README.md).
