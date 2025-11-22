# MVP Workflow API Reference

**API Usage, Examples, and Integration Guide**

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

