# CORE-002: T.Script.FromIdeaAndTitle - Create Initial Script Draft

**Phase**: Core Pipeline  
**Priority**: High  
**Effort**: 3 days  
**Dependencies**: CORE-001 (T.Title.From.Idea)  
**Stage**: Stage 3 in MVP Workflow

---

## Problem Statement

Implement and enhance the script generation module that creates initial script drafts (v1) from an Idea object and Title variant. This is Stage 3 of the core pipeline workflow, following `T.Title.From.Idea`.

## Current State

**✅ Foundation Implemented**:
- `T/Script/FromIdeaAndTitle/src/script_generator.py` exists with:
  - `ScriptGenerator` class with configuration
  - `ScriptV1` dataclass for structured output
  - `ScriptSection` for intro/body/conclusion breakdown
  - 4 structure types (hook-deliver-cta, three-act, problem-solution, story)
  - Platform targeting (YouTube shorts, TikTok, Instagram Reels)
  - Duration estimation based on words-per-second
  - Tone detection and configuration

**⚠️ Enhancement Opportunities**:
1. No AI/LLM integration for content generation
2. Content is template-based, not creative
3. No database persistence for scripts
4. Limited tone customization
5. No version history tracking
6. No integration with review stages

## Acceptance Criteria

- [ ] Script generation produces structured v1 drafts
- [ ] Scripts respect platform duration constraints (YouTube short < 60s, medium < 180s)
- [ ] Scripts include intro, body, and conclusion sections
- [ ] Content delivers on title promises
- [ ] Duration estimates are accurate (±10%)
- [ ] Module integrates with Title.From.Idea output
- [ ] Unit tests achieve >80% coverage
- [ ] Integration with Stage 4-5 (Review stages) verified

## SOLID Principles Analysis

- **SRP**: `ScriptGenerator` handles only script generation; `ScriptV1` is a data container
- **OCP**: Structure methods (hook-deliver-cta, three-act, etc.) can be extended
- **LSP**: `ScriptV1` can be substituted wherever script data is expected
- **ISP**: Clear interface with `generate_script_v1()` as primary entry point
- **DIP**: Configuration injected via `ScriptGeneratorConfig` dataclass

## Implementation Details

### Location
```
T/Script/FromIdeaAndTitle/
├── src/
│   ├── __init__.py
│   └── script_generator.py   # Main implementation
├── _meta/
│   ├── docs/
│   ├── examples/
│   └── tests/
└── README.md
```

### Key Classes

```python
# ScriptGenerator - Main generator class
class ScriptGenerator:
    def generate_script_v1(
        self,
        idea: Idea,
        title: str,
        script_id: Optional[str] = None,
        **kwargs
    ) -> ScriptV1

# ScriptV1 - Output structure
@dataclass
class ScriptV1:
    script_id: str
    idea_id: str
    title: str
    full_text: str
    sections: List[ScriptSection]
    total_duration_seconds: int
    structure_type: ScriptStructure
    platform_target: PlatformTarget
    metadata: Dict[str, Any]
    version: int = 1
```

### Script Structure Types

1. **HOOK_DELIVER_CTA**: Hook (15%) → Deliver (70%) → CTA (15%)
2. **THREE_ACT**: Setup (25%) → Development (50%) → Resolution (25%)
3. **PROBLEM_SOLUTION**: Problem (30%) → Investigation (50%) → Solution (20%)
4. **STORY**: Beginning → Middle → End

### Platform Targets

| Platform | Max Duration | Default Structure |
|----------|--------------|-------------------|
| YouTube Short | 60s | HOOK_DELIVER_CTA |
| YouTube Medium | 180s | THREE_ACT |
| YouTube Long | >180s | THREE_ACT |
| TikTok | 60s | HOOK_DELIVER_CTA |
| Instagram Reel | 90s | HOOK_DELIVER_CTA |

## Input Components

### From Idea.Creation (Stage 1)
- Core concept
- Target audience
- Content theme
- Keywords
- Themes
- Synopsis
- Hook
- Premise

### From Title.From.Idea (Stage 2)
- Selected title variant (text)
- Title style (direct, question, how-to, etc.)
- Title keywords
- Title promises/expectations

## Testing Strategy

```bash
# Run existing tests
cd /home/runner/work/PrismQ/PrismQ
python -m pytest T/Script/FromIdeaAndTitle/_meta/tests/ -v

# Test integration with Title.From.Idea
python -m pytest tests/test_integration.py -k "script" -v
```

### Test Cases
- Generate script from valid idea + title
- Verify section structure (intro, body, conclusion)
- Test all 4 structure types
- Verify duration calculations
- Test platform-specific constraints
- Test tone detection
- Edge cases: minimal idea, long titles

## Definition of Done

- [ ] All existing functionality preserved
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration with Title.From.Idea verified
- [ ] Integration with Stage 4-5 verified
- [ ] Duration estimates accurate within 10%
- [ ] Documentation updated
- [ ] Code reviewed by Worker10
- [ ] Performance benchmarks documented

## Commands

```bash
# Branch creation
cd /home/runner/work/PrismQ/PrismQ
git checkout -b core-002-script-from-idea-title

# Implementation location
# T/Script/FromIdeaAndTitle/src/script_generator.py

# Tests location
# T/Script/FromIdeaAndTitle/_meta/tests/test_script_generator.py
```

## Workflow Integration

### Input Flow
```
Stage 1: Idea.Creation
    ↓
    Idea Object (concept, themes, keywords, hook, premise, synopsis)
    ↓
Stage 2: Title.From.Idea
    ↓
    TitleVariant (text, style, keywords, score)
    ↓
Stage 3: Script.FromIdeaAndTitle ← THIS MODULE
    ↓
    ScriptV1 (full_text, sections, duration, metadata)
```

### Output Flow
After script v1 is generated, it flows to:
- **Stage 4**: `T.Review.Title.ByScriptIdea` - Reviews Title v1 against Script v1 and Idea
- **Stage 5**: `T.Review.Script.ByTitleIdea` - Reviews Script v1 against Title v1 and Idea

## Example Usage

```python
from T.Idea.Model.src.idea import Idea, ContentGenre
from T.Title.From.Idea.src.title_generator import TitleGenerator
from T.Script.FromIdeaAndTitle.src.script_generator import (
    ScriptGenerator, 
    ScriptGeneratorConfig,
    PlatformTarget,
    ScriptStructure
)

# Create idea
idea = Idea(
    title="The Future of AI",
    concept="Exploring how AI will transform everyday life",
    genre=ContentGenre.EDUCATIONAL
)

# Generate title
title_gen = TitleGenerator()
titles = title_gen.generate_from_idea(idea, num_variants=5)
selected_title = titles[0].text

# Generate script
config = ScriptGeneratorConfig(
    platform_target=PlatformTarget.YOUTUBE_MEDIUM,
    target_duration_seconds=90,
    structure_type=ScriptStructure.HOOK_DELIVER_CTA
)
script_gen = ScriptGenerator(config)
script = script_gen.generate_script_v1(idea, selected_title)

print(f"Generated script: {len(script.full_text)} chars")
print(f"Duration: {script.total_duration_seconds}s")
print(f"Sections: {len(script.sections)}")
```

---

**Created**: 2025-11-30  
**Module Number**: #2 in PARALLEL_RUN_NEXT.md  
**Workflow Position**: Stage 3 of Core Pipeline
