# T.Title.ABTesting - A/B Testing Framework

**Module**: `PrismQ.T.Title.ABTesting`  
**Status**: ✅ Implemented  
**Sprint**: Sprint 4 (Weeks 9-10)  
**Type**: Post-MVP Enhancement

---

## Overview

Framework for testing multiple title variants to optimize engagement and click-through rates. This system enables data-driven title optimization by running A/B tests across different title variants, tracking performance metrics, and recommending winning variations based on statistical significance.

## Features

- **Multiple Variant Testing**: Support for 2-5 variants (A/B/C/D/E testing)
- **Statistical Significance**: Chi-square test with 95% confidence threshold
- **Hash-Based Traffic Splitting**: Consistent user assignment with accurate distribution
- **Performance Metrics**: Track CTR, views, and engagement scores
- **Test Management**: Complete lifecycle management (create, start, pause, complete, cancel)
- **Report Generation**: Comprehensive reports with winning variant recommendations

---

## Installation

The module is part of the PrismQ T (Text) pipeline and requires:

```bash
pip install scipy  # For statistical calculations
```

---

## Quick Start

```python
from T.Title.ABTesting import (
    ABTestManager,
    TitleVariant,
    VariantRouter,
    VariantMetrics,
    generate_report
)
from datetime import datetime, timedelta

# 1. Create test manager
manager = ABTestManager()

# 2. Define variants
variants = [
    TitleVariant("A", "Original Title Style", 50),
    TitleVariant("B", "Alternative Title Style", 50)
]

# 3. Create test
test = manager.create_test(
    test_id="test-001",
    content_id="content-123",
    variants=variants,
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=7),
    min_sample_size=1000,
    success_metric="ctr"
)

# 4. Start test
manager.start_test("test-001")

# 5. Assign users to variants
router = VariantRouter()
for user_id in user_ids:
    variant = router.assign(user_id, test.variants)
    # Show user the variant.title

# 6. After collecting metrics, generate report
metrics_data = {
    "A": VariantMetrics("A", views=2000, clicks=200, engagement_score=0.7),
    "B": VariantMetrics("B", views=2000, clicks=260, engagement_score=0.75)
}

report = generate_report(test, metrics_data)
print(f"Winner: {report.analysis.winning_variant}")
print(f"Confidence: {report.analysis.confidence:.1f}%")
print(f"Recommendation: {report.recommendation}")
```

---

## Module Components

### 1. Test Manager (`test_manager.py`)

Manages A/B test lifecycle and configuration.

**Classes**:
- `TitleVariant`: Represents a single title variant
- `ABTest`: Test configuration and metadata
- `TestStatus`: Test status enum (DRAFT, ACTIVE, PAUSED, COMPLETED, CANCELLED)
- `ABTestManager`: Test lifecycle management

**Key Methods**:
- `create_test()`: Create a new A/B test
- `start_test()`: Start a draft test
- `pause_test()`: Pause an active test
- `complete_test()`: Mark test as completed
- `list_tests()`: List tests with filtering

### 2. Statistics (`statistics.py`)

Statistical significance calculations and metric tracking.

**Classes**:
- `VariantMetrics`: Performance metrics for a variant (views, clicks, CTR, engagement)
- `SignificanceResult`: Statistical test results
- `calculate_significance()`: Chi-square test for significance
- `compare_all_variants()`: Pairwise comparison for multivariate tests
- `find_overall_winner()`: Determine overall winner from multiple variants

**Supported Metrics**:
- `ctr`: Click-through rate (default)
- `engagement`: Engagement score
- `views`: View count

### 3. Variant Router (`variant_router.py`)

Hash-based user assignment ensuring consistent variant delivery.

**Classes**:
- `VariantRouter`: Manages variant assignments

**Key Features**:
- Consistent assignment: Same user always gets same variant
- Accurate distribution: Matches target percentages within ±2% (large samples)
- Hash-based: Uses MD5 hash of user_id for deterministic assignment

### 4. Report Generator (`report_generator.py`)

Generates comprehensive test reports with recommendations.

**Classes**:
- `TestReport`: Complete test report with analysis
- `ReportGenerator`: Report generation logic

**Report Contents**:
- Variant performance comparison
- Statistical significance analysis
- Winning variant identification
- Actionable recommendations
- JSON export capability

---

## Traffic Distribution

The module uses hash-based traffic splitting to ensure:

1. **Consistency**: Same user always sees same variant
2. **Accuracy**: Distribution matches target percentages
3. **Deterministic**: Reproducible results

### Distribution Accuracy

- **Large samples (10,000+)**: ±2% of target
- **Medium samples (1,000+)**: ±4% of target
- **Small samples (100+)**: ±5% of target

Example:
```python
variants = [
    TitleVariant("A", "Title A", 33.33),
    TitleVariant("B", "Title B", 33.33),
    TitleVariant("C", "Title C", 33.34)
]

router = VariantRouter()
for i in range(10000):
    variant = router.assign(f"user_{i}", variants)

stats = router.get_distribution_stats(variants)
# Expected: Each variant gets ~33.33% (±2%)
```

---

## Statistical Significance

The module uses chi-square test to determine statistical significance:

- **Threshold**: p < 0.05 (95% confidence)
- **Minimum Sample**: 100 views per variant
- **Method**: Chi-square contingency test for CTR comparison

### Interpretation

- `p_value < 0.05`: Statistically significant (95%+ confidence)
- `p_value >= 0.05`: Not significant (continue testing)
- `confidence`: (1 - p_value) × 100

### Example Results

```python
# Variant A: 2000 views, 200 clicks (10% CTR)
# Variant B: 2000 views, 300 clicks (15% CTR)

result = calculate_significance(variant_a, variant_b, "ctr")
# p_value: 0.0001 (highly significant)
# confidence: 99.99%
# winning_variant: "B"
# improvement: 50% (15% vs 10%)
```

---

## Test Workflow

### 1. Planning Phase
- Define success metric (CTR, engagement, views)
- Determine minimum sample size (default: 1000 per variant)
- Set test duration (recommended: 7-14 days)
- Create title variants (2-5 variants)

### 2. Running Phase
- Start test (status: ACTIVE)
- Assign users to variants using hash-based routing
- Track performance metrics
- Monitor for statistical significance

### 3. Analysis Phase
- Complete test when min sample reached
- Calculate statistical significance
- Generate report with recommendations
- Export results for records

### 4. Implementation Phase
- Deploy winning variant as primary title
- Document results and learnings
- Use insights for future tests

---

## Testing

The module includes comprehensive test coverage:

```bash
# Run all ABTesting tests
pytest T/Title/ABTesting/_meta/tests/ -v

# Run specific test file
pytest T/Title/ABTesting/_meta/tests/test_statistics.py -v

# Run with coverage
pytest T/Title/ABTesting/_meta/tests/ --cov=T/Title/ABTesting
```

**Test Coverage**: 70 tests across 4 test files
- `test_test_manager.py`: 23 tests (lifecycle management)
- `test_statistics.py`: 18 tests (significance calculations)
- `test_variant_router.py`: 17 tests (traffic splitting)
- `test_report_generator.py`: 12 tests (report generation)

---

## Examples

See `_meta/examples/usage_example.py` for a complete working example:

```bash
python3 T/Title/ABTesting/_meta/examples/usage_example.py
```

---

## Best Practices

### 1. Sample Size
- **Minimum**: 1000 views per variant
- **Recommended**: 2000+ views per variant
- **Optimal**: 5000+ views per variant for high confidence

### 2. Test Duration
- **Minimum**: 7 days (capture weekly patterns)
- **Recommended**: 14 days (more reliable)
- **Maximum**: 30 days (diminishing returns)

### 3. Variant Design
- Keep variants focused on specific hypotheses
- Test one variable at a time when possible
- Ensure variants are meaningfully different
- Limit to 2-3 variants unless necessary

### 4. Traffic Split
- Use 50/50 for A/B tests
- Use equal splits for multivariate (33/33/34 for A/B/C)
- Can use 80/20 for conservative testing (80% control)

### 5. Success Criteria
- **CTR**: Best for click-based goals
- **Engagement**: Best for time-on-page goals
- **Views**: Best for exposure goals

---

## Limitations

1. **Maximum Variants**: 5 variants (A/B/C/D/E)
2. **Minimum Sample**: 100 views per variant (for significance testing)
3. **Metrics**: Supports CTR, engagement, views (no custom metrics yet)
4. **Storage**: In-memory only (no database persistence in MVP)

---

## Future Enhancements

- [ ] Database persistence for test history
- [ ] Integration with M (Metrics) module for real-time tracking
- [ ] Automatic test conclusion when significance reached
- [ ] Dashboard visualization of test progress
- [ ] Custom metrics support
- [ ] Sequential testing (Bayesian approach)
- [ ] Multi-armed bandit optimization

---

## Dependencies

- Python 3.12+
- scipy 1.16+ (for statistical calculations)
- datetime (standard library)
- dataclasses (standard library)

---

## Related Modules

- **T.Title.FromIdea**: Initial title generation
- **T.Title.FromOriginalTitleAndReviewAndScript**: Title improvement
- **M** (Future): Real-time metrics collection
- **P** (Future): Publishing and distribution

---

## Support & Issues

For questions or issues, see:
- Issue: [POST-006-ABTesting.md](../../_meta/issues/new/POST-MVP-Enhancements/POST-006-ABTesting.md)
- Repository: [PrismQ](https://github.com/Nomoos/PrismQ)

---

**Version**: 1.0.0  
**Author**: PrismQ Team - Worker17  
**Last Updated**: 2025-11-23
