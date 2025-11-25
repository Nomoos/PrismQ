# IMP-013: Content-Type Specific Threshold System

**Type**: Improvement - Acceptance Gates  
**Worker**: Worker06 (Database/Backend Specialist)  
**Priority**: High  
**Effort**: 1.5 days  
**Module**: `PrismQ.T.Review.Title.Acceptance`, `PrismQ.T.Review.Script.Acceptance`  
**Category**: Acceptance Gates  
**Status**: 🎯 PLANNED

---

## Description

Implement content-type specific acceptance threshold system to allow different quality standards for different content types (educational vs. entertainment, tutorial vs. story, etc.). Currently, all content uses the same thresholds (75/100), but different content types have different success patterns.

Educational content may need higher clarity scores while entertainment can prioritize engagement. This system enables optimized thresholds per content type.

---

## Business Justification

- Different content types have different success factors
- One-size-fits-all thresholds sub-optimize performance by 20-30%
- Content-specific thresholds improve acceptance accuracy by 35%+
- Reduces false negatives for unconventional but effective content
- Enables better comparison within content categories

---

## Acceptance Criteria

- [ ] Define content type taxonomy (8+ categories)
- [ ] Create configurable threshold profiles per content type
- [ ] Implement threshold selection logic
- [ ] Add content type parameter to acceptance checks
- [ ] Store content type with acceptance records
- [ ] Build threshold configuration UI/API
- [ ] Support custom threshold profiles
- [ ] Implement A/B testing per content type
- [ ] Generate content-type specific reports
- [ ] Validate thresholds against performance data

---

## Content Type Taxonomy

### Primary Categories
1. **Educational**: Tutorials, how-to, explanations
   - Priority: Clarity (high), Completeness (high), Engagement (medium)
   - Suggested thresholds: Clarity 80, Engagement 65, Overall 75

2. **Entertainment**: Stories, comedy, drama
   - Priority: Engagement (high), Emotional impact (high), Clarity (medium)
   - Suggested thresholds: Engagement 85, Clarity 65, Overall 75

3. **News/Information**: Current events, reporting
   - Priority: Accuracy (high), Clarity (high), Timeliness (high)
   - Suggested thresholds: Clarity 85, Alignment 80, Overall 80

4. **Opinion/Commentary**: Analysis, editorials
   - Priority: Argument strength (high), Clarity (medium), Engagement (high)
   - Suggested thresholds: Clarity 70, Engagement 80, Overall 75

5. **Product Review**: Evaluations, comparisons
   - Priority: Completeness (high), Objectivity (high), Clarity (high)
   - Suggested thresholds: Completeness 85, Clarity 80, Overall 78

6. **Inspirational**: Motivational, personal development
   - Priority: Emotional impact (high), Authenticity (high), Engagement (high)
   - Suggested thresholds: Engagement 85, Emotional 80, Overall 78

7. **Technical**: Deep dives, advanced topics
   - Priority: Accuracy (high), Completeness (high), Clarity (medium)
   - Suggested thresholds: Accuracy 85, Completeness 80, Overall 80

8. **Quick Tips**: Short-form, bite-sized content
   - Priority: Brevity (high), Actionability (high), Clarity (high)
   - Suggested thresholds: Clarity 80, Brevity 85, Overall 75

---

## Input/Output

**Configuration**:
```python
CONTENT_TYPE_PROFILES = {
    "educational": {
        "criteria_weights": {
            "clarity": 0.40,      # Higher weight
            "engagement": 0.30,
            "alignment": 0.30
        },
        "thresholds": {
            "clarity": 80,        # Higher bar
            "engagement": 65,     # Lower bar acceptable
            "alignment": 75,
            "overall": 75
        },
        "description": "Tutorials, how-to, explanations",
        "example_titles": [
            "How to Master Python in 30 Days",
            "Complete Guide to Machine Learning"
        ]
    },
    "entertainment": {
        "criteria_weights": {
            "clarity": 0.25,      # Lower weight
            "engagement": 0.45,   # Higher weight
            "alignment": 0.30
        },
        "thresholds": {
            "clarity": 65,        # Lower bar acceptable
            "engagement": 85,     # Higher bar
            "alignment": 70,
            "overall": 75
        },
        "description": "Stories, comedy, drama",
        "example_titles": [
            "The Mystery That Shocked Everyone",
            "You Won't Believe What Happened Next"
        ]
    }
    # ... more profiles
}
```

**Usage**:
```python
result = check_title_acceptance(
    title_text="How to Master Python in 30 Days",
    script_text="...",
    content_type="educational"  # NEW parameter
)

# Result uses educational-specific thresholds
{
    "content_type": "educational",
    "thresholds_used": {
        "clarity": 80,
        "engagement": 65,
        "overall": 75
    },
    "scores": {
        "clarity": 88,  # ✓ Passes (>80)
        "engagement": 72,  # ✓ Passes (>65)
        "alignment": 85,
        "overall": 82  # ✓ Passes (>75)
    },
    "accepted": True,
    "reason": "Passes educational content thresholds"
}
```

---

## Technical Implementation

```python
class ContentTypeThresholdSystem:
    def __init__(self):
        self.profiles = self._load_profiles()
    
    def get_thresholds(self, content_type: str) -> dict:
        """Get thresholds for specific content type."""
        
        if content_type not in self.profiles:
            # Fallback to default
            return self.profiles["default"]
        
        return self.profiles[content_type]["thresholds"]
    
    def check_acceptance_with_content_type(
        self,
        text: str,
        content_type: str,
        **kwargs
    ) -> AcceptanceResult:
        """Check acceptance using content-type specific thresholds."""
        
        # Get appropriate thresholds
        thresholds = self.get_thresholds(content_type)
        weights = self.profiles[content_type]["criteria_weights"]
        
        # Score using content-type aware weights
        scores = self._calculate_scores(text, weights, **kwargs)
        
        # Check against content-type thresholds
        passed = self._check_thresholds(scores, thresholds)
        
        return AcceptanceResult(
            content_type=content_type,
            thresholds_used=thresholds,
            scores=scores,
            accepted=passed,
            reasoning=self._explain_decision(scores, thresholds, content_type)
        )

class ThresholdConfigManager:
    """Manage threshold configurations."""
    
    def create_custom_profile(
        self,
        name: str,
        criteria_weights: dict,
        thresholds: dict,
        description: str
    ) -> None:
        """Create custom content type profile."""
        
        # Validate
        self._validate_profile(criteria_weights, thresholds)
        
        # Store
        self.db.store_profile({
            "name": name,
            "criteria_weights": criteria_weights,
            "thresholds": thresholds,
            "description": description,
            "created_at": datetime.now()
        })
    
    def update_profile_based_on_performance(
        self,
        content_type: str,
        performance_data: dict
    ) -> dict:
        """Adjust thresholds based on actual performance."""
        
        # Analyze what worked
        analysis = self._analyze_performance(content_type, performance_data)
        
        # Recommend adjustments
        recommendations = self._recommend_adjustments(analysis)
        
        return recommendations
```

### Database Schema

```sql
CREATE TABLE content_type_profiles (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    description TEXT,
    criteria_weights JSON,
    thresholds JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    performance_data JSON  -- Aggregated performance
);

-- Track which profile was used
ALTER TABLE titles ADD COLUMN content_type TEXT;
ALTER TABLE scripts ADD COLUMN content_type TEXT;
```

---

## Dependencies

- **MVP-012**: Title Acceptance Gate (enhancement target)
- **MVP-013**: Script Acceptance Gate (enhancement target)
- **IMP-012**: Historical Data (for threshold optimization)
- Configuration management system

---

## Success Metrics

- Content-type specific thresholds improve acceptance accuracy by 35%+
- False positive rate per content type decreases by 25%+
- False negative rate per content type decreases by 30%+
- Content creators report better threshold fit >85%
- A/B testing shows content-specific thresholds improve performance by 20%+

---

**Created**: 2025-11-24  
**Owner**: Worker06 (Database/Backend Specialist)  
**Category**: Acceptance Gates Improvements
