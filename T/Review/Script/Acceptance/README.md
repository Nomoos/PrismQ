# PrismQ.T.Review.Script.Acceptance

**Script Acceptance Gate (MVP-013)**

This module implements the acceptance criteria check for scripts before they proceed to quality review stages. It verifies that the script (latest version) meets acceptance criteria for completeness, coherence, and alignment with title.

## Overview

The Script Acceptance Gate is a critical checkpoint in the PrismQ workflow that determines whether a script is ready to proceed to quality reviews (MVP-014+) or needs additional refinement (loop back to MVP-010).

### Workflow Position

```
MVP-012: Title Acceptance (PASSED)
        ↓
MVP-013: Script Acceptance Gate (THIS MODULE)
        ↓
    ACCEPTED?
        ↓
    YES → MVP-014: Quality Reviews (Grammar, Tone, Content, etc.)
    NO  → MVP-010: Script Review → Script Refinement → back to MVP-013
```

## Acceptance Criteria

The script is evaluated on three key dimensions:

1. **Completeness** (35% weight)
   - Script has sufficient length
   - Clear beginning, middle, and end
   - Complete narrative arc

2. **Coherence** (35% weight)
   - Logical flow and transitions
   - Complete sentences and proper structure
   - Consistent narrative

3. **Alignment with Title** (30% weight)
   - Script references key concepts from title
   - Delivers on title's promise
   - Maintains thematic consistency

### Acceptance Threshold

- **Default threshold**: 70/100
- **Customizable** via `acceptance_threshold` parameter
- **Decision**: ACCEPTED if `overall_score >= threshold`

## Installation

No additional dependencies required. This module is part of the PrismQ core.

## Usage

### Basic Usage

```python
from T.Review.Script.Acceptance import check_script_acceptance

# Check script acceptance
result = check_script_acceptance(
    script_text=script_v3,
    title="The Echo Mystery",
    script_version="v3"
)

if result["accepted"]:
    print("Proceed to quality reviews")
else:
    print(f"Loop back to refinement: {result['reason']}")
```

### With Custom Threshold

```python
# Use stricter acceptance criteria
result = check_script_acceptance(
    script_text=script_text,
    title=title,
    acceptance_threshold=80  # More strict
)
```

### Complete Example

```python
from T.Review.Script.Acceptance import check_script_acceptance

script = """
In the old house on Elm Street, mysterious echoes fill every room.
The echoes carry messages from the past, revealing long-hidden secrets.
As we investigate deeper, we discover clues in the walls and floors.
Each sound brings us closer to understanding the mystery.
Finally, we uncover the truth that has been waiting for decades.
"""

title = "The Echo Mystery"

result = check_script_acceptance(
    script_text=script,
    title=title,
    script_version="v3"
)

print(f"Accepted: {result['accepted']}")
print(f"Overall Score: {result['overall_score']}/100")
print(f"Completeness: {result['completeness_score']}/100")
print(f"Coherence: {result['coherence_score']}/100")
print(f"Alignment: {result['alignment_score']}/100")

if not result['accepted']:
    print("\nIssues:")
    for issue in result['issues']:
        print(f"  - {issue}")
    
    print("\nSuggestions:")
    for suggestion in result['suggestions']:
        print(f"  - {suggestion}")
```

## Return Value

The `check_script_acceptance` function returns a dictionary with the following structure:

```python
{
    "accepted": bool,              # True if script passes, False otherwise
    "reason": str,                 # Explanation for the decision
    "completeness_score": int,     # 0-100
    "coherence_score": int,        # 0-100
    "alignment_score": int,        # 0-100
    "overall_score": int,          # 0-100 (weighted average)
    "issues": List[str],           # Issues preventing acceptance (if rejected)
    "suggestions": List[str]       # Suggestions for improvement (if rejected)
}
```

## API Reference

### check_script_acceptance()

```python
def check_script_acceptance(
    script_text: str,
    title: str,
    script_version: Optional[str] = None,
    acceptance_threshold: int = 70
) -> Dict[str, Any]
```

**Parameters:**
- `script_text` (str): The script text to evaluate (latest version)
- `title` (str): The accepted title
- `script_version` (Optional[str]): Version identifier (e.g., "v3", "v4")
- `acceptance_threshold` (int): Minimum score required for acceptance (default: 70)

**Returns:**
- `Dict[str, Any]`: Dictionary containing acceptance result and detailed scores

**Raises:**
- No exceptions raised; validation errors return rejection with explanation

## Decision Logic

### ACCEPTED (score >= threshold)
```
Reason: "Script meets acceptance criteria (score: 75/70). Proceed to quality reviews (MVP-014)."
Next Step: Proceed to MVP-014 (Quality Reviews)
```

### NOT ACCEPTED (score < threshold)
```
Reason: "Script does not meet acceptance criteria (score: 65/70). Loop back to script review and refinement (MVP-010)."
Next Step: Loop back to MVP-010 (Script Review → Script Refinement)
```

## Examples

See `_meta/examples/acceptance_example.py` for complete working examples demonstrating:
- Accepted high-quality scripts
- Rejected incomplete scripts
- Rejected misaligned scripts
- Custom threshold usage

Run the example:
```bash
cd /home/runner/work/PrismQ/PrismQ
python3 T/Review/Script/Acceptance/_meta/examples/acceptance_example.py
```

## Testing

Comprehensive test suite available in `_meta/tests/test_acceptance.py`

Run tests:
```bash
cd /home/runner/work/PrismQ/PrismQ
python3 -m pytest T/Review/Script/Acceptance/_meta/tests/test_acceptance.py -v
```

Test coverage includes:
- Basic acceptance/rejection scenarios
- Completeness evaluation
- Coherence evaluation
- Alignment evaluation
- Custom threshold handling
- Edge cases (empty script, missing title)
- Return value structure validation

## Implementation Details

### Completeness Scoring

Evaluates:
- Word count (more comprehensive = higher score)
- Narrative structure indicators (beginning, middle, end)
- Completeness of story arc

### Coherence Scoring

Evaluates:
- Transition words and connecting phrases
- Sentence structure and punctuation
- Paragraph organization

### Alignment Scoring

Evaluates:
- Keyword presence from title in script
- Phrase matching (bigrams)
- Thematic consistency

### Overall Score Calculation

```python
overall_score = (
    completeness_score * 0.35 +
    coherence_score * 0.35 +
    alignment_score * 0.30
)
```

## Integration

### Import from Parent Module

```python
from T.Review.Script import check_script_acceptance
```

### Import Directly

```python
from T.Review.Script.Acceptance import check_script_acceptance
```

## Dependencies

- **Python**: 3.12+
- **Standard Library**: dataclasses, typing
- **Internal**: None (standalone module)

## Version History

- **v1.0** (2025-11-22): Initial implementation of MVP-013
  - Completeness evaluation
  - Coherence evaluation
  - Alignment evaluation
  - Configurable acceptance threshold
  - Comprehensive test suite

## Contributing

When making changes to this module:
1. Ensure all tests pass
2. Add tests for new functionality
3. Update documentation
4. Follow existing code style

## License

Part of the PrismQ project.

## Related Modules

- **MVP-010**: Script Review by Title
- **MVP-011**: Script Refinement
- **MVP-012**: Title Acceptance (prerequisite)
- **MVP-014+**: Quality Reviews (Grammar, Tone, Content, etc.)

## Support

For questions or issues, refer to the main PrismQ documentation.
