# PrismQ.T.Idea.Inspiration - GitHub Copilot Instructions

> **Note**: This is a submodule within the PrismQ project. For general project guidelines, see the [main repository's copilot instructions](../../../.github/copilot-instructions.md).

## Module Context

This is the **Inspiration submodule** of PrismQ.T.Idea - the entry point for all content creation in the PrismQ workflow. It collects, classifies, and scores raw inspiration from diverse sources before they're developed into structured Ideas.

**Module Namespace**: `PrismQ.T.Idea.Inspiration`

Part of the PrismQ ecosystem:
- **Workflow Position**: [*] → Idea.Inspiration → Idea (Model/Outline/Review) → Script...
- **Purpose**: Transform raw inspiration into structured, scored concepts
- **Integration**: Connects with 24+ sources (Reddit, Twitter, RSS feeds, analytics, etc.)

---

## Module-Specific Guidelines

### Module Structure
```
T/Idea/Inspiration/
├── Source/                    # Production source code (runtime)
├── Research_Layers/          # Research and experimental code
├── _meta/                    # Tests, docs, issues, scripts
│   ├── docs/                 # Module documentation
│   ├── issues/               # Issue tracking
│   ├── research/             # Research artifacts
│   └── scripts/              # Utility scripts
├── .github/                  # GitHub configuration & copilot instructions
└── README.md                 # Module overview
```

### This Module's Responsibility
- **Collect** inspiration from 24+ sources (social media, news, analytics)
- **Classify** inspiration into categories (technology, product, lifestyle, etc.)
- **Score** inspiration based on potential and performance data
- **Transform** raw inspiration into structured concepts for Idea development

### Key Design Patterns
- **Source Adapters**: Each source has its own adapter (Reddit, Twitter, RSS, etc.)
- **Classification Pipeline**: Automated categorization using ML/AI
- **Scoring System**: Multi-factor scoring based on engagement, trends, and analytics
- **Feedback Loop**: Performance data from published content informs future scoring

---

## Project-Wide Guidelines

For detailed project-wide guidelines, refer to the [main repository documentation](../../../):
- **[Root Copilot Instructions](../../../.github/copilot-instructions.md)** - Core principles and module hierarchy
- **[Coding Guidelines](../../../_meta/docs/guidelines/CODING_GUIDELINES.md)** - Module placement and dependency rules
- **[Module Hierarchy](../../../_meta/docs/guidelines/MODULE_HIERARCHY_UPDATED.md)** - Detailed hierarchy diagrams
- **[PR Review Checklist](../../../_meta/docs/guidelines/PR_CODE_REVIEW_CHECKLIST.md)** - Pre-merge verification

### Quick Reference: Key Project Rules
1. **Module Structure**: Standard is `src/` for production code, `_meta/` for everything else
   - **Note**: This submodule uses `Source/` instead of `src/` (historical naming)
2. **Dependency Direction**: Specialized → Generic (never reversed)
3. **Namespace Shortcuts**: Use `T` (not `PrismQ.Text`)
4. **No Side Effects**: No I/O at import time
5. **SOLID Principles**: Single responsibility, dependency injection, abstraction

---


## Target Platform Optimization

All code should be optimized for:
- **Operating System**: Windows
- **GPU**: NVIDIA RTX 5090 (Ada Lovelace architecture, 32GB VRAM)
- **CPU**: AMD Ryzen processor
- **RAM**: 64GB DDR5

### AI/ML Considerations for This Module
- Use mixed precision (FP16/BF16) for RTX 5090
- Implement proper batch sizing for 32GB VRAM
- Profile GPU memory usage for classification models
- Consider model quantization for efficiency

---

## Development Workflow

### Code Style (Python)
- Follow PEP 8 for Python code
- Use type hints for all function parameters and return values
- Write comprehensive docstrings using Google style
- Keep functions focused and under 50 lines when possible

### Testing
- Write unit tests for all new functionality in `_meta/tests/`
- Aim for >80% code coverage
- Include performance benchmarks for AI/ML operations
- Test source adapters with mock data

### Adding New Inspiration Sources
1. Create adapter in `Source/adapters/<source_name>/`
2. Implement source-specific collection logic
3. Add classifier integration
4. Add scoring logic
5. Write tests in `_meta/tests/`
6. Update documentation
7. Test with real data (if available)

---

## Integration Points

### Upstream Dependencies
- None (entry point to workflow)

### Downstream Consumers
- **PrismQ.T.Idea** - Receives structured, scored inspirations
- **Analytics Feedback Loop** - Performance data from published content

### External Systems
- Social media APIs (Reddit, Twitter, Instagram, TikTok)
- RSS feed aggregators
- News APIs
- Analytics platforms

---

## Questions to Ask Before Implementation

When working on this module, consider:
- Does this follow the module placement rules? (Check root copilot instructions)
- Is this a new inspiration source? (Follow source adapter pattern)
- Does this affect classification or scoring? (Consider ML model updates)
- Is this compatible with the analytics feedback loop?
- Have I tested with real-world data sources?
- Does this respect API rate limits and terms of service?
- Is error handling robust for external API failures?

---

## Additional Resources

- **[Module README](../README.md)** - Detailed module documentation
- **[Development Plan](../DEVELOPMENT_PLAN.md)** - Development roadmap and architecture
- **[Main Project README](../../../README.md)** - Overall project context
