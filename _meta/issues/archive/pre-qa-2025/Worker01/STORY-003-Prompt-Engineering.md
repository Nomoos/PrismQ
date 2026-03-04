# STORY-003: Prompt Engineering and Templates

**Phase**: 1 (GPT Integration - MVP)  
**Priority**: Critical  
**Effort**: 2 days  
**Dependencies**: None (blocks STORY-001, STORY-002)  
**Assigned**: Worker13 (Prompt Master)  
**Status**: New  
**Created**: 2025-11-24

---

## Problem Statement

Design and implement high-quality prompt templates for Story ExpertReview and Polish operations. The prompts must guide GPT to provide structured, consistent, and high-quality reviews that match our quality standards.

Key requirements:
- Prompt for expert story review (Stage 21)
- Prompt for story polishing (Stage 22)
- Consistent JSON output format
- Few-shot examples for better quality
- Flexible for different content types and audiences

---

## Current State

**No prompts exist yet**. The current implementation uses simulated logic.

**What's Needed**:
1. Expert Review Prompt Template
2. Polish/Improvement Prompt Template
3. Few-shot examples library
4. Prompt versioning system
5. A/B testing framework for prompts

---

## Acceptance Criteria

### Expert Review Prompt
- [ ] Create system prompt for expert reviewer role
- [ ] Define review dimensions (coherence, audience fit, quality, platform optimization)
- [ ] Specify JSON output schema with all required fields
- [ ] Include scoring guidelines (0-100 scale)
- [ ] Add decision logic (publish vs polish)
- [ ] Include 3+ few-shot examples (good stories, needs work stories)
- [ ] Handle multiple audience types (teens, adults, etc.)
- [ ] Handle multiple platforms (YouTube, TikTok, blog, etc.)

### Polish Prompt
- [ ] Create system prompt for expert editor role
- [ ] Define improvement types (title, script, both)
- [ ] Specify surgical vs. comprehensive changes
- [ ] Preserve story essence while improving
- [ ] Include change tracking in output
- [ ] Add 3+ few-shot examples
- [ ] Handle different priority levels (high, medium, low)

### Prompt Structure
- [ ] Create `T/Story/ExpertReview/prompts/` directory
- [ ] Store prompts as templates (Jinja2 or simple string format)
- [ ] Version prompts (v1, v2, etc.)
- [ ] Document prompt design decisions
- [ ] Create prompt testing framework

### JSON Output Schema
- [ ] Define exact schema for review output
- [ ] Define exact schema for polish output
- [ ] Include all required fields
- [ ] Validate schema with JSON Schema or Pydantic
- [ ] Document schema for developers

### Quality Assurance
- [ ] Test prompts with 10+ real story examples
- [ ] Measure consistency (same input → similar output)
- [ ] Measure quality (expert human validation)
- [ ] Optimize for token efficiency
- [ ] Document prompt performance metrics

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP) ✅
**Analysis**: Prompt templates should be separate from code logic.

**Recommendation**: Store prompts in dedicated files, not hardcoded in Python.

**Structure**:
```
T/Story/ExpertReview/prompts/
├── review_v1.txt
├── review_v2.txt
├── polish_v1.txt
└── examples/
    ├── review_examples.json
    └── polish_examples.json
```

### Open/Closed Principle (OCP) ✅
**Analysis**: Should be easy to add new prompt versions without changing code.

**Recommendation**: Use prompt loader that reads from files:
```python
class PromptLoader:
    def load_review_prompt(self, version: str = "v1") -> str:
        return self._load_file(f"review_{version}.txt")
```

### Liskov Substitution Principle (LSP) ✅
**Analysis**: Different prompt versions should be interchangeable.

**Recommendation**: All versions must produce the same JSON schema, even if content differs.

### Interface Segregation Principle (ISP) ✅
**Analysis**: Prompts should be focused (one per task).

**Recommendation**: Separate review and polish prompts. Don't combine.

### Dependency Inversion Principle (DIP) ✅
**Analysis**: Code should depend on prompt interface, not specific prompts.

**Recommendation**: Use `PromptTemplate` abstraction:
```python
class PromptTemplate(ABC):
    @abstractmethod
    def render(self, **context) -> str:
        pass
```

---

## Implementation Details

### 1. Expert Review Prompt Template

**File**: `T/Story/ExpertReview/prompts/review_v1.txt`

```text
You are an expert story reviewer with 20+ years of experience in content creation for digital media. Your task is to provide a comprehensive professional review of a story (title + script) for publication.

## Story Details

**Title**: {{title}}

**Script**: 
{{script}}

**Target Audience**: {{audience_demographic}} ({{audience_age_range}})
**Platform**: {{platform}}
**Content Style**: {{content_style}}
**Duration**: {{duration}}

**Original Idea**: {{original_idea}}

**Local Reviews Summary**: {{local_reviews_summary}}

## Review Framework

Evaluate the story across five dimensions:

### 1. Story Coherence (0-100)
- Does the title accurately represent the script?
- Does the narrative flow logically?
- Are there plot holes or inconsistencies?
- Rate: 90-100 (Excellent), 80-89 (Good), 70-79 (Needs Work), <70 (Major Issues)

### 2. Audience Fit (0-100)
- Is the content appropriate for the target demographic?
- Does the tone match audience expectations?
- Is the complexity level right for the age range?
- Rate: 90-100 (Perfect Match), 80-89 (Good Fit), 70-79 (Acceptable), <70 (Poor Fit)

### 3. Professional Quality (0-100)
- Is the writing polished and professional?
- Are there grammatical or stylistic issues?
- Is the pacing appropriate?
- Rate: 90-100 (Publication Ready), 80-89 (Minor Polish Needed), 70-79 (Moderate Work), <70 (Major Revision)

### 4. Platform Optimization (0-100)
- Is the content optimized for {{platform}}?
- Is the length appropriate for the platform?
- Does it follow platform best practices?
- Rate: 90-100 (Perfect), 80-89 (Well Optimized), 70-79 (Acceptable), <70 (Not Optimized)

### 5. Overall Quality (0-100)
- Holistic assessment combining all dimensions
- Consider commercial viability
- Consider engagement potential
- Rate: 95-100 (Publish Now), 90-94 (Polish & Publish), 80-89 (Needs Polish), <80 (Major Revision)

## Output Format

Provide your review in the following JSON structure:

{
  "overall_assessment": {
    "ready_for_publishing": boolean,
    "quality_score": integer (0-100),
    "confidence": integer (0-100)
  },
  "story_coherence": {
    "score": integer (0-100),
    "feedback": "detailed feedback string",
    "title_script_alignment": "perfect" | "good" | "needs_work"
  },
  "audience_fit": {
    "score": integer (0-100),
    "feedback": "detailed feedback string",
    "demographic_match": "excellent" | "good" | "needs_work"
  },
  "professional_quality": {
    "score": integer (0-100),
    "feedback": "detailed feedback string",
    "production_ready": boolean
  },
  "platform_optimization": {
    "score": integer (0-100),
    "feedback": "detailed feedback string",
    "platform_perfect": boolean
  },
  "improvement_suggestions": [
    {
      "component": "title" | "script" | "both",
      "priority": "high" | "medium" | "low",
      "suggestion": "specific actionable suggestion",
      "impact": "expected improvement description",
      "estimated_effort": "small" | "medium" | "large"
    }
  ],
  "decision": "publish" | "polish"
}

## Decision Logic

- If overall quality_score >= 95: decision = "publish"
- If overall quality_score < 95: decision = "polish" with improvement_suggestions
- ready_for_publishing = true only if quality_score >= 95

## Examples

[Include 3 few-shot examples here - see examples section below]
```

### 2. Polish Prompt Template

**File**: `T/Story/ExpertReview/prompts/polish_v1.txt`

```text
You are an expert story editor specializing in surgical improvements to content. Your task is to apply specific, high-impact improvements to a story while preserving its essence and core message.

## Current Story

**Title**: {{title}}

**Script**:
{{script}}

**Original Idea**: {{original_idea}}

## Expert Review Feedback

The story received the following improvement suggestions from expert review:

{{improvement_suggestions_formatted}}

## Your Task

Apply improvements to the title and/or script based on the suggestions above. Follow these principles:

### Improvement Principles

1. **Preserve Essence**: Keep the core story, message, and voice intact
2. **Surgical Changes**: Make targeted, specific improvements (not wholesale rewrites)
3. **High Impact**: Focus on changes with maximum quality improvement
4. **Maintain Length**: Keep similar length (±10%)
5. **Priority-Driven**: Focus on HIGH priority suggestions first

### Change Types

**For Title**:
- Capitalization improvements
- Word choice optimization
- Clarity enhancements
- SEO considerations
- Click-worthiness

**For Script**:
- Opening hook enhancement
- Pacing adjustments
- Relatability additions
- Clarity improvements
- Structural refinements

## Output Format

Provide your polished story in the following JSON structure:

{
  "polished_title": "improved title text",
  "polished_script": "improved script text",
  "change_log": [
    {
      "component": "title" | "script",
      "change_type": "capitalization" | "word_choice" | "opening_enhancement" | "pacing_adjustment" | "relatability_add" | "clarity_improvement" | "structure_refinement",
      "before": "text before change",
      "after": "text after change",
      "rationale": "why this change improves the story",
      "suggestion_reference": "which suggestion this addresses"
    }
  ],
  "improvements_applied": ["suggestion_1_id", "suggestion_2_id"],
  "quality_delta_estimate": integer (estimated score increase, 1-10),
  "notes": "any additional notes about the polish process"
}

## Examples

[Include 3 few-shot examples here]
```

### 3. Few-Shot Examples

**File**: `T/Story/ExpertReview/prompts/examples/review_examples.json`

```json
{
  "examples": [
    {
      "input": {
        "title": "The House That Remembers",
        "script": "Sarah inherits an old Victorian mansion...",
        "audience": "US female 14-29",
        "platform": "YouTube Shorts"
      },
      "output": {
        "overall_assessment": {
          "ready_for_publishing": false,
          "quality_score": 88,
          "confidence": 92
        },
        "improvement_suggestions": [
          {
            "component": "title",
            "priority": "high",
            "suggestion": "Add emotional hook to title",
            "impact": "Increases click-through rate by 15-20%",
            "estimated_effort": "small"
          }
        ],
        "decision": "polish"
      }
    },
    {
      "input": {
        "title": "Why Your Morning Routine is Killing Your Productivity",
        "script": "You wake up. Hit snooze. Check your phone...",
        "audience": "US adults 25-40",
        "platform": "Medium blog"
      },
      "output": {
        "overall_assessment": {
          "ready_for_publishing": true,
          "quality_score": 96,
          "confidence": 95
        },
        "decision": "publish"
      }
    }
  ]
}
```

### 4. Prompt Loader Implementation

**File**: `T/Story/ExpertReview/src/prompt_loader.py`

```python
from pathlib import Path
from typing import Dict, Any
import json

class PromptLoader:
    """Load and manage prompt templates."""
    
    def __init__(self, prompts_dir: Path):
        self.prompts_dir = prompts_dir
        self.examples_dir = prompts_dir / "examples"
    
    def load_review_prompt(self, version: str = "v1") -> str:
        """Load expert review prompt template."""
        path = self.prompts_dir / f"review_{version}.txt"
        return path.read_text(encoding="utf-8")
    
    def load_polish_prompt(self, version: str = "v1") -> str:
        """Load polish prompt template."""
        path = self.prompts_dir / f"polish_{version}.txt"
        return path.read_text(encoding="utf-8")
    
    def load_examples(self, example_type: str = "review") -> Dict[str, Any]:
        """Load few-shot examples."""
        path = self.examples_dir / f"{example_type}_examples.json"
        return json.loads(path.read_text(encoding="utf-8"))
    
    def render_prompt(self, template: str, **context) -> str:
        """Render prompt with context variables."""
        # Simple string formatting (can upgrade to Jinja2 if needed)
        return template.format(**context)
```

---

## Testing Strategy

### Prompt Quality Tests

1. **Consistency Test**: Same input → similar output (run 5 times, measure variance)
2. **Completeness Test**: All required JSON fields present
3. **Schema Validation**: Output matches defined schema
4. **Example Coverage**: Test with 10+ diverse stories
5. **Edge Cases**: Empty script, very long script, special characters

### Test Script

**File**: `T/Story/ExpertReview/_meta/tests/test_prompts.py`

```python
import pytest
from T.Story.ExpertReview.src.prompt_loader import PromptLoader
from pathlib import Path

class TestPrompts:
    @pytest.fixture
    def loader(self):
        prompts_dir = Path(__file__).parent.parent / "prompts"
        return PromptLoader(prompts_dir)
    
    def test_review_prompt_loads(self, loader):
        """Test review prompt loads successfully."""
        prompt = loader.load_review_prompt("v1")
        assert len(prompt) > 100
        assert "{{title}}" in prompt
        assert "{{script}}" in prompt
    
    def test_polish_prompt_loads(self, loader):
        """Test polish prompt loads successfully."""
        prompt = loader.load_polish_prompt("v1")
        assert len(prompt) > 100
        assert "{{title}}" in prompt
    
    def test_prompt_rendering(self, loader):
        """Test prompt renders with context."""
        template = loader.load_review_prompt("v1")
        rendered = loader.render_prompt(
            template,
            title="Test Title",
            script="Test script...",
            audience_demographic="US teens",
            platform="YouTube"
        )
        assert "Test Title" in rendered
        assert "Test script" in rendered
        assert "{{" not in rendered  # No unrendered variables
```

---

## Definition of Done

### Prompts Created
- [ ] Expert Review prompt v1 complete
- [ ] Polish prompt v1 complete
- [ ] 3+ few-shot examples for review
- [ ] 3+ few-shot examples for polish
- [ ] Prompt variables documented

### Code Complete
- [ ] PromptLoader class implemented
- [ ] Prompt rendering working
- [ ] Examples loading working
- [ ] Unit tests passing

### Quality Validated
- [ ] Tested with 10+ real stories
- [ ] Output consistency measured (>80%)
- [ ] Schema compliance verified (100%)
- [ ] Token efficiency optimized
- [ ] Expert human validation completed

### Documentation
- [ ] Prompt design rationale documented
- [ ] Variable reference guide created
- [ ] Few-shot examples explained
- [ ] Version changelog started
- [ ] Usage guide for developers

### Integration Ready
- [ ] Compatible with STORY-001 (GPT Review API)
- [ ] Compatible with STORY-002 (GPT Polish API)
- [ ] Ready for prompt A/B testing (STORY-018)

---

## Related Issues

- **STORY-001**: GPT Review API Integration (uses these prompts)
- **STORY-002**: GPT Polish API Integration (uses these prompts)
- **STORY-018**: Prompt Optimization (will improve these prompts)

---

## Resources

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Few-Shot Learning](https://platform.openai.com/docs/guides/prompt-engineering/strategy-provide-examples)
- [JSON Mode](https://platform.openai.com/docs/guides/text-generation/json-mode)

---

**Status**: Ready for Worker13  
**Created**: 2025-11-24  
**Owner**: Worker01  
**Reviewer**: Worker10
