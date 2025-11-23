# POST-006: T.Title.ABTesting - A/B Testing Framework

**Type**: Post-MVP Enhancement  
**Worker**: Worker17 (Analytics)  
**Priority**: Medium  
**Effort**: 2 days  
**Module**: `PrismQ.T.Title.ABTesting`  
**Sprint**: Sprint 4 (Weeks 9-10)  
**Status**: 🎯 PLANNED

---

## Description

Framework for testing multiple title variants to optimize engagement and click-through rates.

This system enables data-driven title optimization by running A/B tests across different title variants, tracking performance metrics, and recommending winning variations based on statistical significance.

---

## Acceptance Criteria

- [ ] Store multiple title variants with test metadata
- [ ] Track variant performance metrics (CTR, views, engagement)
- [ ] Calculate statistical significance (chi-square test, confidence intervals)
- [ ] Recommend winning variant based on data
- [ ] Integration with Analytics module (M) for metric collection
- [ ] A/B test configuration and scheduling interface
- [ ] Support multivariate testing (A/B/C/D...)
- [ ] Export test results and reports

---

## Input/Output

**Input**:
- Multiple title variants (2-5 variants)
- Test configuration:
  - Traffic split percentages
  - Minimum sample size
  - Test duration
  - Success metric (CTR, engagement, views)
- Target audience segments (optional)

**Output**:
- A/B test report:
  - Variant performance comparison
  - Statistical significance results
  - Winning variant recommendation
  - Confidence level
- Performance visualizations
- Test history and trends

---

## Dependencies

- **MVP-002**: T.Title.FromIdea module
- **Future**: M module integration for real-time metrics

---

## Technical Notes

### A/B Test Data Model
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class TitleVariant:
    variant_id: str  # A, B, C, etc.
    title: str
    traffic_percent: float  # 50%, 25%, etc.
    
@dataclass
class ABTest:
    test_id: str
    content_id: str
    variants: List[TitleVariant]
    start_date: datetime
    end_date: datetime
    status: str  # 'active' | 'completed' | 'paused'
    min_sample_size: int  # e.g., 1000 views
    success_metric: str  # 'ctr' | 'engagement' | 'views'
```

### Statistical Significance Calculation
```python
from scipy.stats import chi2_contingency

def calculate_significance(variant_a, variant_b):
    """
    Calculate statistical significance using chi-square test.
    Returns p-value and confidence level.
    """
    # Example: CTR comparison
    data = [
        [variant_a.clicks, variant_a.views - variant_a.clicks],
        [variant_b.clicks, variant_b.views - variant_b.clicks]
    ]
    
    chi2, p_value, dof, expected = chi2_contingency(data)
    
    confidence = (1 - p_value) * 100
    is_significant = p_value < 0.05  # 95% confidence
    
    return {
        'p_value': p_value,
        'confidence': confidence,
        'is_significant': is_significant
    }
```

### Traffic Splitting Strategy
```python
def assign_variant(user_id: str, variants: List[TitleVariant]) -> TitleVariant:
    """
    Assign user to variant based on hash-based distribution.
    Ensures consistent assignment for same user.
    """
    import hashlib
    
    hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
    threshold = hash_val % 100
    
    cumulative = 0
    for variant in variants:
        cumulative += variant.traffic_percent
        if threshold < cumulative:
            return variant
    
    return variants[0]  # fallback
```

### Files to Create
- `T/Title/ABTesting/test_manager.py` (new)
- `T/Title/ABTesting/statistics.py` (new)
- `T/Title/ABTesting/variant_router.py` (new)
- `T/Title/ABTesting/report_generator.py` (new)
- `T/Title/ABTesting/__init__.py` (new)

### Database Schema
```sql
CREATE TABLE ab_tests (
    id INTEGER PRIMARY KEY,
    test_id TEXT UNIQUE,
    content_id TEXT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    status TEXT,
    min_sample_size INTEGER,
    success_metric TEXT,
    config JSON
);

CREATE TABLE title_variants (
    id INTEGER PRIMARY KEY,
    test_id TEXT,
    variant_id TEXT,
    title TEXT,
    traffic_percent REAL,
    FOREIGN KEY (test_id) REFERENCES ab_tests(test_id)
);

CREATE TABLE variant_metrics (
    id INTEGER PRIMARY KEY,
    test_id TEXT,
    variant_id TEXT,
    metric_date DATE,
    views INTEGER,
    clicks INTEGER,
    engagement_score REAL,
    created_at TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES ab_tests(test_id)
);
```

### Testing Requirements
- [ ] Test traffic splitting algorithm (verify distribution)
- [ ] Test statistical significance calculation
- [ ] Test with different sample sizes
- [ ] Test multivariate scenarios (A/B/C/D)
- [ ] Validate winning variant recommendation logic
- [ ] Test report generation
- [ ] Integration test with Title module

---

## A/B Test Configuration

```python
# Example: Create A/B test
test = ABTest(
    test_id="test-2025-11-23-001",
    content_id="content-123",
    variants=[
        TitleVariant(
            variant_id="A",
            title="How AI is Transforming Healthcare in 2025",
            traffic_percent=50
        ),
        TitleVariant(
            variant_id="B", 
            title="AI Healthcare Revolution: 2025 Breakthrough",
            traffic_percent=50
        )
    ],
    min_sample_size=1000,
    success_metric="ctr"
)
```

---

## Test Result Report Example

```json
{
  "test_id": "test-2025-11-23-001",
  "status": "completed",
  "duration_days": 7,
  "total_views": 5240,
  "variants": [
    {
      "variant_id": "A",
      "title": "How AI is Transforming Healthcare in 2025",
      "views": 2618,
      "clicks": 285,
      "ctr": 10.89,
      "engagement_score": 0.72
    },
    {
      "variant_id": "B",
      "title": "AI Healthcare Revolution: 2025 Breakthrough",
      "views": 2622,
      "clicks": 354,
      "ctr": 13.50,
      "engagement_score": 0.81
    }
  ],
  "analysis": {
    "winning_variant": "B",
    "confidence": 97.3,
    "p_value": 0.027,
    "is_significant": true,
    "improvement": "+24.0% CTR"
  },
  "recommendation": "Deploy variant B as primary title"
}
```

---

## Multivariate Testing Support

Support testing 3+ variants simultaneously:
```python
variants = [
    TitleVariant("A", "Title Version 1", 33.3),
    TitleVariant("B", "Title Version 2", 33.3),
    TitleVariant("C", "Title Version 3", 33.4)
]
```

Pairwise statistical comparison:
- A vs B
- A vs C
- B vs C

Recommend overall winner with highest significance.

---

## Integration with Future M Module

Once Metrics (M) module is implemented:
- Real-time metric collection from published content
- Automatic test conclusion when significance reached
- Dashboard visualization of test progress
- Historical test performance tracking

---

## Success Metrics

- Traffic splitting accuracy: ±2% of target
- Statistical calculation accuracy: 100%
- Test completion detection: Real-time
- Report generation time: <3 seconds
- Support for 2-5 variants simultaneously

---

**Created**: 2025-11-23  
**Owner**: Worker17 (Analytics Specialist)
