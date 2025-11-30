# CORE-001: T.Title.From.Idea - Generate Initial Title Variants from Idea

**Phase**: Core Pipeline  
**Priority**: High  
**Effort**: 2 days  
**Dependencies**: Idea.Creation ✅ (Complete)  
**Stage**: Stage 2 in MVP Workflow

---

## Problem Statement

Implement and enhance the title generation module that creates initial title variants (v1) from an Idea object. This is Stage 2 of the core pipeline workflow, immediately following `PrismQ.T.Idea.Creation`.

## Current State

**✅ Foundation Implemented**:
- `T/Title/From/Idea/src/title_generator.py` exists with:
  - `TitleGenerator` class with configuration
  - `TitleVariant` dataclass for structured output
  - 10 generation strategies (direct, question, how-to, curiosity, authoritative, listicle, problem-solution, comparison, ultimate-guide, benefit)
  - Basic keyword extraction from ideas
  - Length constraints and validation

**⚠️ Enhancement Opportunities**:
1. No AI/LLM integration for improved title quality
2. Basic keyword extraction (no NLP)
3. No A/B testing or scoring optimization
4. No database persistence for generated titles
5. Limited title scoring algorithm
6. No SEO optimization integration

## Acceptance Criteria

- [ ] Title generation produces 3-10 high-quality variants per idea
- [ ] Each variant uses a distinct generation strategy
- [ ] Generated titles meet length constraints (20-100 chars)
- [ ] Titles include relevant keywords from source idea
- [ ] Quality scores accurately reflect title engagement potential
- [ ] Module integrates with Idea.Creation output format
- [ ] Unit tests achieve >80% coverage
- [ ] Integration with Stage 3 (Script.FromIdeaAndTitle) verified

## SOLID Principles Analysis

- **SRP**: `TitleGenerator` handles only title generation; `TitleVariant` is a data container
- **OCP**: Strategy methods allow extension without modifying core generation logic
- **LSP**: `TitleVariant` can be substituted wherever title data is expected
- **ISP**: Clear interface with `generate_from_idea()` as primary entry point
- **DIP**: Configuration injected via `TitleConfig` dataclass

## Implementation Details

### Location
```
T/Title/From/Idea/
├── src/
│   ├── __init__.py
│   └── title_generator.py   # Main implementation
├── _meta/
│   ├── docs/
│   ├── examples/
│   └── tests/
└── README.md
```

### Key Classes

```python
# TitleGenerator - Main generator class
class TitleGenerator:
    def generate_from_idea(self, idea: Idea, num_variants: int = 10) -> List[TitleVariant]

# TitleVariant - Output structure
@dataclass
class TitleVariant:
    text: str
    style: str
    length: int
    keywords: List[str]
    score: float
```

### 10 Generation Strategies

1. **Direct**: Clean, straightforward title
2. **Question**: Poses engaging question
3. **How-to**: Action-oriented, instructional
4. **Curiosity**: Creates intrigue
5. **Authoritative**: Expert perspective
6. **Listicle**: Number-based format
7. **Problem-Solution**: Addresses challenges
8. **Comparison**: Contrasts approaches
9. **Ultimate-Guide**: Comprehensive resource
10. **Benefit**: Value proposition focus

## Testing Strategy

```bash
# Run existing tests
cd /home/runner/work/PrismQ/PrismQ
python -m pytest T/Title/From/Idea/_meta/tests/ -v

# Test integration with Idea.Creation
python -m pytest tests/test_integration.py -k "title" -v
```

### Test Cases
- Generate 10 variants from valid idea
- Handle ideas with minimal data (title only, concept only)
- Validate length constraints
- Verify all 10 strategies produce unique outputs
- Test keyword extraction accuracy
- Edge cases: empty idea, invalid num_variants

## Definition of Done

- [ ] All existing functionality preserved
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration with Idea.Creation verified
- [ ] Integration with Stage 3 verified
- [ ] Documentation updated
- [ ] Code reviewed by Worker10
- [ ] Performance benchmarks documented

## Commands

```bash
# Branch creation
cd /home/runner/work/PrismQ/PrismQ
git checkout -b core-001-title-from-idea

# Implementation location
# T/Title/From/Idea/src/title_generator.py

# Tests location
# T/Title/From/Idea/_meta/tests/test_title_generator.py
```

## Next Stage

After title variants are generated, they flow to:
- **Stage 3**: `T.Script.FromIdeaAndTitle` (CORE-002) - Uses Title v1 as context for script generation

---

**Created**: 2025-11-30  
**Module Number**: #1 in PARALLEL_RUN_NEXT.md  
**Workflow Position**: Stage 2 of Core Pipeline
