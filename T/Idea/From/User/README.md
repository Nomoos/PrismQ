# T/Idea/From/User - AI-Powered Idea Creation Module

**Namespace**: `PrismQ.T.Idea.From.User`

Generate **10 Ideas by default** from simple text inputs using local AI models (Ollama). Input text flows directly to AI prompts without any parsing, extraction, or validation.

---

## Quick Start

```python
from PrismQ.T.Idea.From.User.src.idea_variants import create_ideas_from_input

# Input text passes directly to AI - no parsing
ideas = create_ideas_from_input("Your text here", count=10)
```

**Prerequisites**: Ollama must be installed and running. See [Setup Guide](./_meta/docs/AI_INTEGRATION_README.md#setup-instructions).

---

## Documentation

### Core Guides
- **[AI Integration Guide](./_meta/docs/AI_INTEGRATION_README.md)** - Setup, usage, and AI configuration
- **[How It Works (CZ)](./_meta/docs/HOW_IT_WORKS.md)** - Detailed technical documentation in Czech
- **[Flavors System](./_meta/docs/FLAVOR_SYSTEM.md)** - Understanding and using content flavors
- **[Custom Prompts](./_meta/docs/CUSTOM_PROMPTS.md)** - Advanced prompt templating

### Implementation Details
- **[Final Implementation Summary](./_meta/docs/FINAL_IMPLEMENTATION_SUMMARY.md)** - Complete implementation overview
- **[SOLID Refactoring](./_meta/docs/SOLID_REFACTORING_SUMMARY.md)** - Architecture and design patterns
- **[Implementation Notes](./_meta/docs/IMPLEMENTATION_NOTES.md)** - Technical details and decisions

### Migration & Changes
- **[Flavors Migration](./_meta/docs/FLAVORS_MIGRATION.md)** - Transitioning to flavor-based system
- **[Prompt Changes](./_meta/docs/PROMPT_CHANGE_SUMMARY.md)** - Prompt evolution and updates
- **[Fallback Removal](./_meta/docs/FALLBACK_REMOVAL_SUMMARY.md)** - AI requirement changes

### Reference
- **[AI Generation Guide](./_meta/docs/AI_GENERATION.md)** - Complete AI setup and models
- **[Prompt Variations](./_meta/docs/PROMPT_VARIATIONS.md)** - Prompt engineering guide
- **[Quick Templates](./_meta/docs/QUICKSTART_TEMPLATES.md)** - Quick reference templates
- **[Model Selection](./_meta/docs/QWEN_MODEL_SELECTION.md)** - Choosing the right AI model

### Code Review & Testing
- **[Review Documents](./_meta/docs/REVIEW.md)** - Code reviews and feedback
- **[Final Report](./_meta/docs/FINAL_REPORT.md)** - Project completion report
- **[Worker10 Review](./_meta/docs/WORKER10_REVIEW.md)** - Detailed technical review
- **[Test Suite](./_meta/tests/)** - Comprehensive test coverage

### Examples
- **[Usage Examples](./_meta/examples/)** - Code examples and demos
- **[Creation Examples](./_meta/examples/creation_examples.md)** - Step-by-step usage patterns

---

## Key Concepts

- **Input Passthrough**: Text flows directly to AI without parsing
- **Flavor-Based**: 39+ curated content flavors for different audiences
- **Weighted Selection**: Automatic flavor selection optimized for target demographics
- **AI Required**: Ollama must be running (no fallback mode)
- **Default 10 Ideas**: Generates 10 variations by default

---

## Navigation

**[← Back to T/Idea](../README.md)** | **[→ Model Module](../Model/)** | **[→ Fusion Module](../Fusion/)**

---

*Part of the PrismQ.T.Idea content development workflow*  
*Implements Path 2: Manual Creation with AI-powered idea generation*
