# MVP Workflow Best Practices

**Best Practices, Troubleshooting, and Guidelines**

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
