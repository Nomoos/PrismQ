# T/Review/Title/Acceptance - Title Acceptance Gate

**Namespace**: `PrismQ.T.Review.Title.Acceptance`

**Stage 12 (MVP-012)** in the MVP workflow - Title Acceptance Gate

## Purpose

The Title Acceptance Gate determines whether a title (at any version - v3, v4, v5, etc.) is ready to proceed to script acceptance (MVP-013) or needs further refinement through another review-refinement cycle.

This critical quality gate ensures titles meet minimum standards for:
- **Clarity**: Title is clear and understandable
- **Engagement**: Title is compelling and attention-grabbing
- **Script Alignment**: Title accurately reflects script content

## Workflow Position

```
Title (vN) + Script (vN) → Acceptance Gate (MVP-012) → {
    ACCEPTED: Proceed to Script Acceptance (MVP-013)
    NOT ACCEPTED: Loop back to Title Review (MVP-008) → Title Refinement → v(N+1)
}
```

## Key Features

- **Three-Criterion Evaluation**: Clarity, Engagement, Script Alignment
- **Automatic Threshold Checking**: Configurable thresholds for each criterion
- **Detailed Feedback**: Provides specific recommendations when not accepted
- **Version Tracking**: Works with any version (v3, v4, v5, etc.)
- **JSON-Compatible Output**: Structured results for integration

## API Reference

### Main Function

#### `check_title_acceptance()`

```python
def check_title_acceptance(
    title_text: str,
    title_version: str = "v3",
    script_text: str = "",
    script_version: str = "v3",
    script_summary: str = ""
) -> TitleAcceptanceResult
```

**Parameters:**
- `title_text` (str): The title to evaluate
- `title_version` (str): Version of the title (e.g., "v3", "v4")
- `script_text` (str): The script content to evaluate against
- `script_version` (str): Version of the script
- `script_summary` (str, optional): Brief summary of script content

**Returns:**
- `TitleAcceptanceResult`: Acceptance status and detailed feedback

**Example:**
```python
from T.Review.Title.Acceptance import check_title_acceptance

result = check_title_acceptance(
    title_text="The Echo Mystery: Dark Secrets Revealed",
    title_version="v3",
    script_text="A mysterious echo in an old house reveals dark secrets...",
    script_version="v3"
)

if result.accepted:
    print("Title accepted - proceed to MVP-013")
else:
    print(f"Title not accepted: {result.reason}")
    for rec in result.recommendations:
        print(f"  - {rec}")
```

### Evaluation Functions

#### `evaluate_clarity(title_text: str) -> AcceptanceCriterionResult`

Evaluates title clarity based on:
- Length appropriateness (optimal: 30-75 characters)
- Structure and grammar
- Absence of ambiguity
- Readability factors

#### `evaluate_engagement(title_text: str, script_summary: str) -> AcceptanceCriterionResult`

Evaluates title engagement potential based on:
- Curiosity generation
- Compelling words usage
- Question or intrigue elements
- Emotional resonance

#### `evaluate_script_alignment(title_text: str, script_text: str, script_summary: str) -> AcceptanceCriterionResult`

Evaluates title-script alignment based on:
- Keyword overlap
- Theme matching
- Content representation
- Expectation setting

## Data Models

### TitleAcceptanceResult

```python
@dataclass
class TitleAcceptanceResult:
    title_text: str
    title_version: str
    accepted: bool
    overall_score: int  # 0-100
    reason: str
    criteria_results: List[AcceptanceCriterionResult]
    script_version: str = ""
    script_summary: str = ""
    recommendations: List[str] = None
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = None
```

**Methods:**
- `to_dict()`: Convert to dictionary (JSON-compatible)
- `get_criterion_result(criterion)`: Get result for specific criterion
- `__repr__()`: String representation

### AcceptanceCriterionResult

```python
@dataclass
class AcceptanceCriterionResult:
    criterion: AcceptanceCriteria
    score: int  # 0-100
    passed: bool
    reasoning: str
    threshold: int = 70
```

### AcceptanceCriteria (Enum)

```python
class AcceptanceCriteria(Enum):
    CLARITY = "clarity"
    ENGAGEMENT = "engagement"
    SCRIPT_ALIGNMENT = "script_alignment"
```

## Acceptance Thresholds

```python
CLARITY_THRESHOLD = 70          # Minimum clarity score
ENGAGEMENT_THRESHOLD = 70       # Minimum engagement score
ALIGNMENT_THRESHOLD = 75        # Minimum alignment score
OVERALL_THRESHOLD = 75          # Minimum overall score
```

**Acceptance Logic:**
- All three criteria must pass their thresholds
- Overall score must be >= 75
- If any criterion fails or overall score is too low: NOT ACCEPTED

## Usage Examples

### Example 1: Basic Acceptance Check

```python
from T.Review.Title.Acceptance import check_title_acceptance

result = check_title_acceptance(
    title_text="The Haunting Echo: Secrets Revealed",
    title_version="v3",
    script_text="A haunting echo reveals dark secrets in the old house...",
    script_version="v3"
)

print(f"Status: {'ACCEPTED' if result.accepted else 'NOT ACCEPTED'}")
print(f"Score: {result.overall_score}/100")
print(f"Reason: {result.reason}")
```

### Example 2: Iterative Refinement

```python
from T.Review.Title.Acceptance import check_title_acceptance

# Initial version
result_v3 = check_title_acceptance(
    title_text="The House",
    title_version="v3",
    script_text="A mystery unfolds in an old house...",
    script_version="v3"
)

if not result_v3.accepted:
    print("v3 not accepted, refining...")
    # ... refine title based on recommendations ...
    
    # After refinement
    result_v4 = check_title_acceptance(
        title_text="The Mystery of the Old House",
        title_version="v4",
        script_text="A mystery unfolds in an old house...",
        script_version="v4"
    )
    
    if result_v4.accepted:
        print("v4 accepted - proceed to script acceptance!")
```

### Example 3: Detailed Criterion Analysis

```python
from T.Review.Title.Acceptance import check_title_acceptance, AcceptanceCriteria

result = check_title_acceptance(
    title_text="The Echo Mystery",
    title_version="v3",
    script_text="A mysterious echo reveals secrets...",
    script_version="v3"
)

# Examine each criterion
for cr in result.criteria_results:
    status = "✓" if cr.passed else "✗"
    print(f"{status} {cr.criterion.value}: {cr.score}/100")
    print(f"  {cr.reasoning}")

# Get specific criterion
clarity = result.get_criterion_result(AcceptanceCriteria.CLARITY)
print(f"\nClarity: {clarity.score}/100 ({'passed' if clarity.passed else 'failed'})")
```

### Example 4: JSON Export

```python
from T.Review.Title.Acceptance import check_title_acceptance
import json

result = check_title_acceptance(
    title_text="The Echo Mystery",
    title_version="v3",
    script_text="A mystery about echoes...",
    script_version="v3"
)

# Convert to JSON
result_json = json.dumps(result.to_dict(), indent=2)
print(result_json)

# Save to file
with open("acceptance_result.json", "w") as f:
    json.dump(result.to_dict(), f, indent=2)
```

## Integration with MVP Workflow

### Stage Flow

1. **Input**: Title (latest version) + Script (latest version)
2. **Evaluate**: Check three criteria (clarity, engagement, alignment)
3. **Decision**:
   - **ACCEPTED**: Move to Stage 13 (Script Acceptance Gate)
   - **NOT ACCEPTED**: Loop to Stage 8 (Title Review by Script v2) → Stage 9 (Title Refinement)

### Workflow Integration Example

```python
from T.Review.Title.Acceptance import check_title_acceptance

def process_title_acceptance_gate(title, script, max_iterations=10):
    """Process title through acceptance gate with iteration limit."""
    
    iteration = 0
    current_version = title.version
    
    while iteration < max_iterations:
        # Stage 12: Check acceptance
        result = check_title_acceptance(
            title_text=title.text,
            title_version=current_version,
            script_text=script.text,
            script_version=script.version
        )
        
        if result.accepted:
            print(f"Title accepted at {current_version}")
            return title, True  # Proceed to MVP-013
        else:
            print(f"Title not accepted at {current_version}: {result.reason}")
            # Loop to MVP-008: Review and refine
            # ... review and refine title ...
            iteration += 1
            current_version = f"v{int(current_version[1:]) + 1}"
    
    print(f"Max iterations reached at {current_version}")
    return title, False
```

## Testing

Run tests:
```bash
cd /home/runner/work/PrismQ/PrismQ
python3 -m pytest T/Review/Title/Acceptance/_meta/tests/test_acceptance.py -v
```

Test coverage:
- Acceptance criteria validation (6 tests)
- Clarity evaluation (6 tests)
- Engagement evaluation (6 tests)
- Script alignment evaluation (4 tests)
- Data model functionality (4 tests)
- Integration scenarios (3 tests)

## Dependencies

**Module**: `PrismQ.T.Review.Title.Acceptance`

**Depends on**:
- MVP-011: Script Refinement v3 (provides latest title version)
- Standard library only (no external dependencies)

**Used by**:
- MVP-013: Script Acceptance Gate
- MVP workflow orchestration

## Navigation

**[← Back to Title Review](../README.md)** | **[→ View Tests](./_meta/tests/)**

---

**Module**: PrismQ.T.Review.Title.Acceptance  
**Stage**: MVP-012 (Stage 12)  
**Worker**: Worker10  
**Status**: ✅ Complete
