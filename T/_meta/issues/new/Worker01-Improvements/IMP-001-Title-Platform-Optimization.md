# IMP-001: Platform-Specific Title Length Optimization

**Type**: Improvement - Title Generation  
**Worker**: Worker12 (Content Specialist)  
**Priority**: High  
**Effort**: 1.5 days  
**Module**: `PrismQ.T.Title.FromIdea`, `PrismQ.T.Title.FromOriginalTitleAndReviewAndScript`  
**Category**: Title Generation  
**Status**: 🎯 PLANNED

---

## Description

Implement platform-specific title length optimization to ensure titles meet optimal character counts for different platforms (YouTube, TikTok, Instagram, Twitter/X, LinkedIn, Medium, etc.). Each platform has different title length recommendations for maximum visibility and engagement.

Currently, the title generation process uses generic length guidelines. This enhancement will add platform-aware optimization to generate titles that perform best on each target platform.

---

## Business Justification

- Different platforms truncate titles at different lengths
- Platform-optimized titles have 20-30% higher click-through rates
- Reduces manual title editing for cross-platform publishing
- Improves SEO and discoverability on each platform

---

## Acceptance Criteria

- [ ] Define optimal title length ranges for 8+ major platforms
- [ ] Add platform parameter to title generation functions
- [ ] Implement length validation and warnings
- [ ] Generate platform-specific title variants
- [ ] Add platform metadata to title records in database
- [ ] Create platform-specific title scoring (length factor)
- [ ] Update title improver to respect platform constraints
- [ ] Provide length optimization feedback in reviews
- [ ] Support multi-platform title optimization (generate for all platforms at once)
- [ ] Add configuration for custom platform length rules

---

## Platform Length Specifications

### Video Platforms
- **YouTube**: 60-70 characters (optimal), 100 max
- **TikTok**: 40-50 characters (optimal), 100 max
- **Instagram Reels**: 40-50 characters (optimal), 125 max
- **Facebook**: 40-60 characters (optimal), no hard limit but truncates at ~63

### Social Media
- **Twitter/X**: 50-70 characters (optimal), 280 max but titles truncate at ~70
- **LinkedIn**: 50-70 characters (optimal), 200+ visible

### Blogging Platforms
- **Medium**: 60-80 characters (optimal), no hard limit
- **WordPress**: 50-70 characters (optimal for SEO)

---

## Input/Output

**Input**:
- Idea object
- Title variants
- Target platform(s) (single or list)
- Length preferences (optional)

**Output**:
- Platform-optimized title variants
- Length compliance indicators
- Platform-specific scoring
- Truncation warnings if needed
- Multi-platform compatibility report

---

## Dependencies

- **MVP-002**: T.Title.FromIdea (v1 generation)
- **MVP-006**: T.Title.FromOriginalTitleAndReviewAndScript (improvements)
- Database schema may need update for platform field

---

## Technical Notes

### Implementation Approach

1. **Platform Configuration** (`T/Title/config/platforms.py`):
```python
PLATFORM_CONFIGS = {
    "youtube": {
        "optimal_min": 60,
        "optimal_max": 70,
        "hard_max": 100,
        "weight": 1.0
    },
    "tiktok": {
        "optimal_min": 40,
        "optimal_max": 50,
        "hard_max": 100,
        "weight": 1.0
    },
    # ... more platforms
}
```

2. **Length Validator** (`T/Title/validators/length_validator.py`):
```python
def validate_title_length(title: str, platform: str) -> ValidationResult:
    """Validate title length for specific platform."""
    config = PLATFORM_CONFIGS.get(platform)
    length = len(title)
    
    if length > config["hard_max"]:
        return ValidationResult(
            passed=False,
            score=0,
            message=f"Title exceeds {platform} max length"
        )
    
    # Score based on optimal range
    if config["optimal_min"] <= length <= config["optimal_max"]:
        return ValidationResult(passed=True, score=100, message="Optimal length")
    # ... calculate score for non-optimal
```

3. **Platform-Aware Generation**:
```python
def generate_title_for_platform(
    idea: Idea,
    platform: str,
    style: str = "direct"
) -> str:
    """Generate title optimized for specific platform."""
    config = PLATFORM_CONFIGS[platform]
    target_length = (config["optimal_min"] + config["optimal_max"]) // 2
    
    # Generate with length constraint
    prompt = f"Generate {style} title, target {target_length} chars..."
    # ... generation logic
```

### Files to Create/Modify

**New Files**:
- `T/Title/config/platforms.py` - Platform configurations
- `T/Title/validators/length_validator.py` - Length validation logic
- `T/Title/optimizers/platform_optimizer.py` - Platform-specific optimization

**Modified Files**:
- `T/Title/FromIdea/src/title_generator.py` - Add platform parameter
- `T/Title/FromOriginalTitleAndReviewAndScript/src/title_improver.py` - Add platform awareness
- Database schema - Add `platform` field to titles table

### Database Schema Update

```sql
ALTER TABLE titles ADD COLUMN platform VARCHAR(50);
ALTER TABLE titles ADD COLUMN platform_score INTEGER DEFAULT 100;
ALTER TABLE titles ADD COLUMN length_optimal BOOLEAN DEFAULT TRUE;
```

### Testing Requirements

- [ ] Unit tests for each platform configuration
- [ ] Length validation tests (optimal, under, over)
- [ ] Multi-platform generation tests
- [ ] Platform scoring calculation tests
- [ ] Integration tests with existing title generation
- [ ] Edge cases: empty titles, very long titles, special characters

---

## Success Metrics

- Platform-optimized titles have length compliance rate >95%
- Title length scores improve by 25%+ for all platforms
- Cross-platform title generation time <3 seconds
- Manual title editing for platform publishing reduces by 40%+
- Platform-specific engagement metrics improve by 15%+

---

## Related Issues

- IMP-003: SEO-Focused Title Suggestion (benefits from platform awareness)
- IMP-005: Enhanced Title Generation Strategies (uses platform constraints)
- POST-001: SEO Keywords (can leverage platform metadata)

---

**Created**: 2025-11-24  
**Owner**: Worker12 (Content Specialist)  
**Category**: Title Generation Improvements
