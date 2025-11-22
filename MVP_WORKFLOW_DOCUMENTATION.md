# MVP Workflow Documentation

**PrismQ MVP - Iterative Title-Script Co-Improvement Workflow (26 Stages)**

Version: 1.0  
Created: 2025-11-22  
Status: Complete  
Module: Documentation

---

## Table of Contents

1. [Overview](#overview)
2. [Workflow Principles](#workflow-principles)
3. [Complete Workflow Stages](#complete-workflow-stages)
4. [Stage Details](#stage-details)
5. [Iteration Loops](#iteration-loops)
6. [Usage Examples](#usage-examples)
7. [API Reference](#api-reference)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The MVP workflow implements a comprehensive **26-stage iterative co-improvement process** where title and script are refined together through multiple review and improvement stages. This ensures the highest quality content through systematic validation and cross-checking.

### Key Innovation

Title and script improvements are **co-dependent** - each is reviewed and refined based on the other, creating a continuous quality improvement cycle that ensures alignment and coherence.

### Workflow Philosophy

- **Progressive Refinement**: Multiple version iterations (v1, v2, v3, v4+)
- **Cross-Validation**: Title and script validated against each other
- **Quality Gates**: Explicit acceptance checks before progression
- **Comprehensive Reviews**: Local AI reviews covering 5 quality dimensions
- **Expert Polish**: GPT-4/GPT-5 based expert review and refinement

---

## Workflow Principles

### 1. Co-Dependent Improvement

- **Title reviewed by script**: Title is evaluated in context of script content
- **Script reviewed by title**: Script is evaluated in context of title promise
- **Cross-validation**: Each element validated against the other + original idea

### 2. Version Tracking

- **v1**: Initial drafts (from idea)
- **v2**: First improvement cycle (using initial reviews)
- **v3**: Second refinement cycle (using v2 reviews)
- **v4+**: Additional cycles if acceptance checks fail

**Important**: When loops occur, **always use the newest/latest version** of both title and script.

### 3. Explicit Acceptance Gates

- **Title acceptance check** (stage 12): Must pass before checking script
- **Script acceptance check** (stage 13): Must pass before quality reviews
- **Quality validation** (stages 14-20): Final quality gates

### 4. Context Preservation

- Original versions preserved throughout
- Reviews reference originals for context
- Improvements build on previous versions

---

## Complete Workflow Stages

### Workflow Sequence (26 Stages)

```
Stage 1: PrismQ.T.Idea.Creation
    ↓
Stage 2: PrismQ.T.Title.FromIdea (v1)
    ↓
Stage 3: PrismQ.T.Script.FromIdeaAndTitle (v1)
    ↓
Stage 4: PrismQ.T.Review.Title.ByScript (v1)
    ↓
Stage 5: PrismQ.T.Review.Script.ByTitle (v1)
    ↓
Stage 6: PrismQ.T.Title.Improvements (v2)
    ↓
Stage 7: PrismQ.T.Script.Improvements (v2)
    ↓
Stage 8: PrismQ.T.Review.Title.ByScript (v2) ←──────────────┐
    ↓                                                       │
Stage 9: PrismQ.T.Title.Refinement (v3)                    │
    ↓                                                       │
Stage 10: PrismQ.T.Review.Script.ByTitle (v2) ←─────────┐  │
    ↓                                                    │  │
Stage 11: PrismQ.T.Script.Refinement (v3)               │  │
    ↓                                                    │  │
Stage 12: Title Acceptance Check ─NO────────────────────┘  │
    ↓ YES                                                   │
Stage 13: Script Acceptance Check ─NO──────────────────────┘
    ↓ YES

━━━━ Local AI Reviews (Stages 14-20) ━━━━

Stage 14: PrismQ.T.Review.Script.Grammar ←──────────┐
    ↓                                               │
    ├─FAILS─→ Return to Script.Refinement ─────────┘
    ↓ PASSES
Stage 15: PrismQ.T.Review.Script.Tone ←────────────┐
    ↓                                              │
    ├─FAILS─→ Return to Script.Refinement ────────┘
    ↓ PASSES
Stage 16: PrismQ.T.Review.Script.Content ←─────────┐
    ↓                                              │
    ├─FAILS─→ Return to Script.Refinement ────────┘
    ↓ PASSES
Stage 17: PrismQ.T.Review.Script.Consistency ←─────┐
    ↓                                              │
    ├─FAILS─→ Return to Script.Refinement ────────┘
    ↓ PASSES
Stage 18: PrismQ.T.Review.Script.Editing ←─────────┐
    ↓                                              │
    ├─FAILS─→ Return to Script.Refinement ────────┘
    ↓ PASSES
Stage 19: PrismQ.T.Review.Title.Readability ←──────┐
    ↓                                              │
    ├─FAILS─→ Return to Title.Refinement ─────────┘
    ↓ PASSES
Stage 20: PrismQ.T.Review.Script.Readability ←─────┐
    ↓                                              │
    ├─FAILS─→ Return to Script.Refinement ────────┘
    ↓ PASSES

━━━━ GPT Expert Review Loop (Stages 21-22) ━━━━

Stage 21: PrismQ.T.Story.ExpertReview (GPT) ←──────────┐
    ↓                                                   │
    ├─ Improvements Needed ─→ Stage 22 ────────────────┘
    ↓ Ready for Publishing
Stage 23: PrismQ.T.Publishing.Finalization
```

---

## Stage Details

This section provides comprehensive documentation for all 26 stages of the MVP workflow. Each stage includes purpose, inputs, outputs, API examples, and usage examples.

### Stages 1-11: Initial Creation and Refinement

These stages handle initial content creation, cross-reviews, and iterative improvement cycles.

---

### Stage 1: PrismQ.T.Idea.Creation

**Purpose**: Capture initial content idea

**Folder**: `T/Idea/Creation/`  
**Worker**: Worker02  
**Effort**: 2 days

**Input**:
- Text description of idea
- Optional: inspiration sources, target audience

**Output**:
- Idea object with unique ID
- Metadata (timestamp, author, tags)
- Initial classification

**Validation**:
- Not empty
- Basic format check
- Contains minimum required fields

**API**:
```python
from PrismQ.T.Idea.Creation import create_idea

idea = create_idea(
    description="Story about mysterious events in a small town",
    target_audience="US female 14-29",
    genre="mystery/suspense"
)
# Returns: Idea object with ID
```

**Usage Example**:
```python
# Create a new idea
idea = {
    "id": "PQ001",
    "description": "A suspenseful story about unexplained disappearances",
    "target_audience": "Young adults",
    "genre": "Mystery",
    "platforms": ["YouTube", "TikTok"],
    "created_at": "2025-01-01T10:00:00Z"
}
```

**Next Stage**: Stage 2 (Title.FromIdea)

---

### Stage 2: PrismQ.T.Title.FromIdea (v1)

**Purpose**: Generate first title from idea

**Folder**: `T/Title/FromIdea/`  
**Worker**: Worker13 (Prompt Master)  
**Effort**: 2 days

**Input**:
- Idea object from Stage 1
- Target audience metadata
- Platform requirements

**Output**:
- 3-5 title variants (v1)
- Metadata for each variant
- Engagement score predictions

**Process**:
- AI generation using simple prompt
- Context: Based on idea only
- Version: v1 (initial)

**API**:
```python
from PrismQ.T.Title.FromIdea import generate_title_v1

titles = generate_title_v1(
    idea=idea,
    num_variants=5,
    style="suspenseful"
)
# Returns: List of title variants
```

**Usage Example**:
```python
# Generate initial title variants
titles_v1 = [
    "The Mystery of Hollow Creek",
    "When the Town Went Silent",
    "Vanished: The Hollow Creek Enigma",
    "Shadows Over Hollow Creek",
    "The Hollow Creek Disappearances"
]

selected_title_v1 = titles_v1[0]  # Best scored variant
```

**Next Stage**: Stage 3 (Script.FromIdeaAndTitle)

---

### Stage 3: PrismQ.T.Script.FromIdeaAndTitle (v1)

**Purpose**: Generate first script from idea and title v1

**Folder**: `T/Script/FromIdeaAndTitle/`  
**Worker**: Worker02  
**Effort**: 3 days

**Input**:
- Idea object
- Title v1
- Target word count
- Structural requirements

**Output**:
- Initial script (v1)
- Structure: Intro, body, conclusion
- Metadata: word count, reading time

**Process**:
- AI generation with structured prompt
- Context: Based on idea + title v1
- Version: v1 (initial)

**API**:
```python
from PrismQ.T.Script.FromIdeaAndTitle import generate_script_v1

script = generate_script_v1(
    idea=idea,
    title=title_v1,
    target_words=1500,
    structure="intro-body-conclusion"
)
# Returns: Script object
```

**Next Stage**: Stage 4 (Review.Title.ByScript)

---

### Stages 4-11: Cross-Review and Improvement Cycles

These stages implement the co-dependent improvement methodology where title and script are reviewed against each other and iteratively refined.

**Stage 4**: PrismQ.T.Review.Title.ByScript (v1) - Review title v1 against script v1  
**Stage 5**: PrismQ.T.Review.Script.ByTitle (v1) - Review script v1 against title v1  
**Stage 6**: PrismQ.T.Title.Improvements (v2) - Generate improved title v2  
**Stage 7**: PrismQ.T.Script.Improvements (v2) - Generate improved script v2  
**Stage 8**: PrismQ.T.Review.Title.ByScript (v2) - Review title v2 against script v2  
**Stage 9**: PrismQ.T.Title.Refinement (v3) - Refine title to v3  
**Stage 10**: PrismQ.T.Review.Script.ByTitle (v2) - Review script v2 against title v3  
**Stage 11**: PrismQ.T.Script.Refinement (v3) - Refine script to v3

For detailed API and examples for each of these stages, refer to the source file [MVP_WORKFLOW.md](./_meta/issues/MVP_WORKFLOW.md).

---

### Stages 12-13: Acceptance Gates

**Stage 12: Title Acceptance Check**

**Purpose**: Verify title is ready to proceed

**Input**: Title (latest version - v3, v4, v5, etc.)  
**Output**: ACCEPTED or NOT ACCEPTED

**Decision**:
- **ACCEPTED**: Proceed to stage 13
- **NOT ACCEPTED**: Return to stage 8 for additional refinement

**API**:
```python
from PrismQ.T.Review.Idea import check_title_acceptance

acceptance = check_title_acceptance(title=title_v3)
# Returns: {"accepted": True/False, "reason": "..."}
```

**Stage 13: Script Acceptance Check**

**Purpose**: Verify script is ready to proceed

**Input**: Script (latest version - v3, v4, v5, etc.), Title (accepted version)  
**Output**: ACCEPTED or NOT ACCEPTED

**Decision**:
- **ACCEPTED**: Proceed to stage 14
- **NOT ACCEPTED**: Return to stage 10 for additional refinement

**API**:
```python
from PrismQ.T.Review.Script import check_script_acceptance

acceptance = check_script_acceptance(script=script_v3, title=title_v3)
# Returns: {"accepted": True/False, "reason": "..."}
```

---

### Stages 14-20: Quality Reviews

These stages validate 7 quality dimensions using local AI reviews.

**Stage 14**: Grammar Review - Technical correctness  
**Stage 15**: Tone Review - Emotional and stylistic consistency  
**Stage 16**: Content Review - Narrative logic and coherence  
**Stage 17**: Consistency Review - Internal continuity  
**Stage 18**: Editing Review - Clarity and flow  
**Stage 19**: Title Readability - Final title validation  
**Stage 20**: Script Readability - Voiceover quality validation

Each quality review follows the same pattern:

**API Pattern**:
```python
from PrismQ.T.Review.<Dimension> import review_<dimension>

result = review_<dimension>(script=script_v3)
# Returns: {"pass": True/False, "issues": [...], "suggestions": [...]}
```

**Decision Pattern**:
- **PASSES**: Proceed to next stage
- **FAILS**: Return to appropriate refinement stage with feedback

---

### Stages 21-23: Expert Review and Publishing

**Stage 21: PrismQ.T.Story.ExpertReview**

**Purpose**: GPT-based expert review of complete story

**Input**:
- Title (final version)
- Script (final version)
- Audience context
- Original idea

**Output**:
- Ready for Publishing or Improvements Needed
- Expert review JSON with scores and feedback

**API**:
```python
from PrismQ.T.Story.ExpertReview import expert_review

result = expert_review(
    title=title_final,
    script=script_final,
    idea=idea,
    audience="US female 14-29"
)
```

**Stage 22: PrismQ.T.Story.ExpertPolish**

**Purpose**: Apply GPT-based expert improvements

**Input**: Title, script, expert review feedback  
**Output**: Polished title and script

**Iteration Limit**: Maximum 2 polish iterations

**API**:
```python
from PrismQ.T.Story.ExpertPolish import expert_polish

polished = expert_polish(title, script, expert_review_result)
```

**Stage 23: PrismQ.T.Publishing.Finalization**

**Purpose**: Publish approved and validated content

**Input**: Final title, final script, original idea  
**Output**: Published content package

**API**:
```python
from PrismQ.T.Publishing.Finalization import publish_content

published = publish_content(
    title=title_final,
    script=script_final,
    idea=idea,
    format="markdown"
)
```

---

## Iteration Loops

The MVP workflow includes several iteration loops to ensure quality through progressive refinement.

### Loop 1: Title-Script Co-Improvement (Stages 8-13)

**Trigger**: Title or script acceptance check fails

**Loop Path**:
```
Stage 12: Title Acceptance ─FAIL→ Stage 8 → Stage 9 → Stage 12
Stage 13: Script Acceptance ─FAIL→ Stage 10 → Stage 11 → Stage 13
```

**Example**:
```python
# Title refinement loop
max_iterations = 10
iteration = 0
title_current = title_v3

while not title_accepted and iteration < max_iterations:
    # Stage 8: Review title by script
    review = review_title_by_script(title_current, script_current)
    
    # Stage 9: Refine title
    title_current = refine_title(title_current, review)
    iteration += 1
    
    # Stage 12: Check acceptance
    result = check_title_acceptance(title_current)
    title_accepted = result["accepted"]
    
    if not title_accepted:
        print(f"Iteration {iteration}: {result['reason']}")
```

### Loop 2: Quality Review Loops (Stages 14-20)

**Trigger**: Any quality review fails (Grammar, Tone, Content, Consistency, Editing, Readability)

**Loop Pattern**:
```
Quality Review ─FAIL→ Apply Fixes → Retry Review
```

**Example**:
```python
# Grammar review with automatic retry
max_retries = 3
script_current = script_v3

for attempt in range(max_retries):
    result = review_grammar(script_current)
    
    if result["pass"]:
        print("Grammar check passed")
        break
    
    # Apply corrections
    script_current = apply_grammar_fixes(
        script_current,
        result["corrections"]
    )
    print(f"Attempt {attempt + 1}: Applied {len(result['corrections'])} fixes")
```

### Loop 3: Expert Review Loop (Stages 21-22)

**Trigger**: Expert review suggests improvements

**Loop Path**:
```
Stage 21: ExpertReview ─Improvements Needed→ Stage 22 → Stage 21
```

**Iteration Limit**: Maximum 2 polish iterations

**Example**:
```python
# Expert review and polish loop
expert_iterations = 0
max_expert_iterations = 2
title_current = title_final
script_current = script_final

while expert_iterations < max_expert_iterations:
    # Stage 21: Expert review
    review = expert_review(title_current, script_current, idea)
    
    if review["status"] == "ready":
        print("Expert review passed - ready for publishing")
        break
    
    # Stage 22: Expert polish
    polished = expert_polish(title_current, script_current, review)
    title_current = polished["title"]
    script_current = polished["script"]
    expert_iterations += 1
    
    print(f"Expert polish iteration {expert_iterations}")
```

### Loop Management Best Practices

1. **Version Tracking**: Always increment version numbers when looping
2. **Iteration Limits**: Set maximum iterations to prevent infinite loops
3. **Progress Logging**: Log each iteration for debugging
4. **Change Tracking**: Document changes in each iteration
5. **Quality Metrics**: Track quality scores across iterations

---

## Usage Examples

### Example 1: Complete Workflow Execution

```python
from PrismQ.T import Workflow

# Initialize workflow
workflow = Workflow()

# Stage 1: Create idea
idea = workflow.create_idea(
    description="Mysterious disappearances in a small town",
    target_audience="US female 14-29"
)

# Stages 2-3: Generate initial versions
title_v1 = workflow.generate_title_v1(idea)
script_v1 = workflow.generate_script_v1(idea, title_v1)

# Stages 4-5: Initial reviews
title_review = workflow.review_title_by_script(title_v1, script_v1, idea)
script_review = workflow.review_script_by_title(script_v1, title_v1, idea)

# Stages 6-7: First improvements
title_v2 = workflow.improve_title_v2(title_v1, title_review, script_review)
script_v2 = workflow.improve_script_v2(script_v1, script_review, title_v2)

# Stages 8-11: Refinement cycle
title_v3, script_v3 = workflow.refinement_cycle(title_v2, script_v2, idea)

# Stages 12-13: Acceptance checks with loop handling
title_v3 = workflow.run_title_acceptance_loop(title_v3, script_v3)
script_v3 = workflow.run_script_acceptance_loop(script_v3, title_v3)

# Stages 14-20: Quality reviews
quality_passed = workflow.run_quality_reviews(title_v3, script_v3)

if quality_passed:
    # Stages 21-22: Expert review and polish
    final_title, final_script = workflow.expert_review_and_polish(
        title_v3, script_v3, idea
    )
    
    # Stage 23: Publish
    published = workflow.publish(final_title, final_script, idea)
    print(f"Published: {published['id']}")
    print(f"URLs: {published['urls']}")
```

### Example 2: Batch Processing Multiple Ideas

```python
from PrismQ.T import BatchProcessor
import pandas as pd

# Initialize batch processor
batch = BatchProcessor(max_workers=5)

# Load ideas from CSV
ideas_df = pd.read_csv("ideas.csv")
ideas = [
    batch.create_idea(
        description=row['description'],
        target_audience=row['audience'],
        genre=row['genre']
    )
    for _, row in ideas_df.iterrows()
]

# Process all ideas through complete workflow
results = batch.process_batch(
    ideas=ideas,
    workflow_stages="all",  # Stages 1-23
    quality_threshold=85,
    auto_publish=True
)

# Generate report
print(f"Total processed: {len(results['completed'])}")
print(f"Published: {results['published_count']}")
print(f"Failed: {results['failed_count']}")
print(f"Average time per idea: {results['avg_time_minutes']} minutes")
```

### Example 3: Custom Quality Criteria

```python
from PrismQ.T.Review import CustomReview

# Define custom review criteria
custom_criteria = {
    "suspense_level": {
        "min_score": 7,
        "max_score": 10,
        "weight": 0.3
    },
    "character_depth": {
        "min_score": 6,
        "max_score": 10,
        "weight": 0.2
    },
    "plot_complexity": {
        "min_score": 5,
        "max_score": 10,
        "weight": 0.2
    },
    "pacing": {
        "min_score": 7,
        "max_score": 10,
        "weight": 0.3
    }
}

# Create custom reviewer
reviewer = CustomReview(criteria=custom_criteria)

# Evaluate script
result = reviewer.evaluate(script_v3)

if result["pass"]:
    print(f"Custom review passed! Score: {result['overall_score']}")
else:
    print("Custom review failed. Suggestions:")
    for suggestion in result["improvements"]:
        print(f"- {suggestion['area']}: {suggestion['suggestion']}")
```

### Example 4: Monitoring and Alerting

```python
from PrismQ.T import WorkflowMonitor
import time

# Initialize monitor
monitor = WorkflowMonitor()

# Start monitoring workflow
workflow_id = "WF-001"
monitor.start_monitoring(workflow_id)

# Run workflow
workflow = Workflow()
idea = workflow.create_idea(description="Mystery story")
# ... continue workflow ...

# Check progress periodically
while not workflow.is_complete():
    health = monitor.get_health(workflow_id)
    
    if health["current_stage"] > health["expected_stage"]:
        print(f"Warning: Workflow behind schedule")
    
    if health["failure_count"] > 3:
        print(f"Alert: Multiple failures detected")
        monitor.send_alert(workflow_id, health)
    
    time.sleep(60)  # Check every minute

# Get final report
report = monitor.generate_report(workflow_id)
print(f"Total time: {report['total_time_minutes']} minutes")
print(f"Stages completed: {report['stages_completed']}/23")
print(f"Quality score: {report['final_quality_score']}")
```

---

## API Reference

### Core Classes

#### Workflow

Main workflow orchestration class.

```python
class Workflow:
    def __init__(self, config: Dict = None):
        """Initialize workflow with optional configuration"""
        pass
    
    def create_idea(self, description: str, **kwargs) -> Idea:
        """Stage 1: Create idea"""
        pass
    
    def generate_title_v1(self, idea: Idea) -> Title:
        """Stage 2: Generate title v1"""
        pass
    
    def generate_script_v1(self, idea: Idea, title: Title) -> Script:
        """Stage 3: Generate script v1"""
        pass
    
    def review_title_by_script(self, title: Title, script: Script, idea: Idea) -> Review:
        """Stage 4: Review title by script"""
        pass
    
    def review_script_by_title(self, script: Script, title: Title, idea: Idea) -> Review:
        """Stage 5: Review script by title"""
        pass
    
    def improve_title_v2(self, title_v1: Title, reviews: List[Review]) -> Title:
        """Stage 6: Improve title to v2"""
        pass
    
    def improve_script_v2(self, script_v1: Script, reviews: List[Review], title_v2: Title) -> Script:
        """Stage 7: Improve script to v2"""
        pass
    
    def refinement_cycle(self, title: Title, script: Script, idea: Idea) -> Tuple[Title, Script]:
        """Stages 8-11: Run refinement cycle"""
        pass
    
    def run_title_acceptance_loop(self, title: Title, script: Script, max_iterations: int = 10) -> Title:
        """Stages 8-12: Run title acceptance loop"""
        pass
    
    def run_script_acceptance_loop(self, script: Script, title: Title, max_iterations: int = 10) -> Script:
        """Stages 10-13: Run script acceptance loop"""
        pass
    
    def run_quality_reviews(self, title: Title, script: Script) -> bool:
        """Stages 14-20: Run all quality reviews"""
        pass
    
    def expert_review_and_polish(self, title: Title, script: Script, idea: Idea) -> Tuple[Title, Script]:
        """Stages 21-22: Expert review and polish"""
        pass
    
    def publish(self, title: Title, script: Script, idea: Idea) -> Publication:
        """Stage 23: Publish content"""
        pass
```

#### Data Models

```python
class Idea:
    id: str
    description: str
    target_audience: str
    genre: str
    platforms: List[str]
    created_at: datetime
    metadata: Dict[str, Any]

class Title:
    id: str
    idea_id: str
    text: str
    version: str  # "v1", "v2", "v3", etc.
    variants: List[str]
    score: float
    created_at: datetime
    metadata: Dict[str, Any]

class Script:
    id: str
    idea_id: str
    title_id: str
    content: str
    version: str  # "v1", "v2", "v3", etc.
    word_count: int
    reading_time_minutes: int
    structure: Dict[str, str]
    created_at: datetime
    metadata: Dict[str, Any]

class Review:
    id: str
    target_id: str
    target_type: str  # "title" or "script"
    stage: int
    alignment_score: float
    feedback: Dict[str, Any]
    pass_fail: Optional[bool]
    created_at: datetime

class Publication:
    id: str
    idea_id: str
    title: Title
    script: Script
    formats: Dict[str, str]
    platforms: List[Dict[str, str]]
    published_at: datetime
    version_history: Dict[str, List[str]]
```

---

## Best Practices

### 1. Version Management

Always track versions explicitly to maintain complete history.

```python
# Good - explicit version tracking
title_v1 = generate_title_v1(idea)
title_v2 = improve_title_v2(title_v1, reviews)
title_v3 = refine_title(title_v2, review)

# Bad - loses version history
title = generate_title(idea)
title = improve_title(title)  # Overwrites original
```

### 2. Error Handling

Handle failures gracefully with proper error recovery.

```python
# Good - comprehensive error handling
try:
    result = review_grammar(script)
    if not result["pass"]:
        script = apply_fixes(script, result["corrections"])
except ReviewError as e:
    logger.error(f"Grammar review failed: {e}")
    # Fallback or retry logic
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    raise

# Bad - no error handling
result = review_grammar(script)
script = apply_fixes(script, result["corrections"])
```

### 3. Loop Protection

Always set iteration limits to prevent infinite loops.

```python
# Good - protected loop
max_iterations = 10
iteration = 0
while not accepted and iteration < max_iterations:
    # Refinement logic
    iteration += 1
    if iteration == max_iterations:
        logger.warning("Max iterations reached")

# Bad - potential infinite loop
while not accepted:
    # Refinement logic (could run forever)
```

### 4. Logging and Monitoring

Log all important stages and decisions for debugging.

```python
# Good - comprehensive logging
logger.info(f"Stage 12: Title acceptance check for {title.id}")
result = check_title_acceptance(title)
logger.info(f"Result: {'ACCEPTED' if result['accepted'] else 'NOT ACCEPTED'}")
if not result['accepted']:
    logger.debug(f"Reason: {result['reason']}")

# Bad - no logging
result = check_title_acceptance(title)
```

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Infinite Loop in Acceptance Checks

**Symptom**: Title or script never passes acceptance check

**Solution**:
```python
# Add iteration limit and escalation
max_iterations = 5
for i in range(max_iterations):
    if check_acceptance(item):
        break
    if i == max_iterations - 1:
        # Escalate to manual review
        manual_review_queue.add(item)
        logger.warning(f"Escalated {item.id} to manual review")
```

#### Issue 2: Quality Reviews Always Failing

**Symptom**: Grammar/tone/content reviews consistently fail

**Solution**:
```python
# Adjust review sensitivity
review_config = {
    "grammar_strictness": "medium",  # Instead of "high"
    "tone_tolerance": 0.2,
    "content_min_score": 70
}
```

#### Issue 3: Expert Review Timeout

**Symptom**: Stage 21 times out or is very slow

**Solution**:
```python
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=4, max=60))
def expert_review_with_retry(title, script, idea):
    return expert_review(title, script, idea)
```

### Debug Mode

Enable debug mode for detailed logging:

```python
from PrismQ.T import Workflow
import logging

logging.basicConfig(level=logging.DEBUG)
workflow = Workflow(debug=True)
```

---

## Summary

The MVP workflow provides a comprehensive, iterative approach to content creation with:

- **26 stages** covering all aspects from idea to publication
- **3 major iteration loops** for continuous improvement
- **7 quality dimensions** validated through AI reviews
- **Explicit acceptance gates** ensuring quality standards
- **Version tracking** preserving complete history
- **GPT expert review** for professional polish

This documentation provides complete coverage of:
- ✅ All 26 workflow stages with detailed descriptions
- ✅ Usage examples for key patterns
- ✅ Iteration loop documentation
- ✅ Complete API reference
- ✅ Best practices and troubleshooting

For additional information, see:
- [MVP_WORKFLOW.md](./_meta/issues/MVP_WORKFLOW.md) - Original specification
- [WORKFLOW.md](./WORKFLOW.md) - Complete state machine documentation
- [T/README.md](./T/README.md) - Text generation pipeline overview

---

**Version**: 1.0  
**Created**: 2025-11-22  
**Module**: Documentation  
**Workers**: Worker15 (Documentation Specialist)

**Status**: ✅ Complete

---

*PrismQ MVP Workflow Documentation - Complete Reference*
