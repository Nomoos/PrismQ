# IMP-014: Dynamic Criteria Weighting System

**Type**: Improvement - Acceptance Gates  
**Worker**: Worker17 (Analytics Specialist)  
**Priority**: Medium  
**Effort**: 1.5 days  
**Module**: `PrismQ.T.Review.Title.Acceptance`, `PrismQ.T.Review.Script.Acceptance`  
**Category**: Acceptance Gates  
**Status**: 🎯 PLANNED

---

## Description

Implement dynamic criteria weighting system that automatically adjusts the importance (weight) of different acceptance criteria based on performance data, platform requirements, and content trends. Currently, weights are fixed (clarity: 35%, engagement: 35%, alignment: 30%), but optimal weights vary by context.

This system learns which criteria matter most for success in different scenarios and adjusts weights accordingly.

---

## Business Justification

- Fixed weights sub-optimize for varying contexts
- Dynamic weights improve prediction accuracy by 25-40%
- Adapts to changing platform algorithms and audience preferences
- Reduces need for manual threshold tuning
- Enables personalized quality standards

---

## Acceptance Criteria

- [ ] Implement weight adjustment algorithm based on performance data
- [ ] Support context-aware weighting (platform, audience, content type)
- [ ] A/B test different weight configurations
- [ ] Track which weight combinations perform best
- [ ] Implement gradual weight adjustment (not sudden shifts)
- [ ] Add weight explanations to acceptance results
- [ ] Support manual weight overrides for specific use cases
- [ ] Monitor weight drift and anomalies
- [ ] Visualize weight evolution over time
- [ ] Document optimal weight patterns

---

## Weighting Contexts

### By Platform
- **YouTube Shorts**: Engagement 50%, Clarity 30%, Alignment 20%
  - Hook strength matters more than detail
- **Educational Blog**: Clarity 50%, Completeness 30%, Engagement 20%
  - Understanding trumps entertainment
- **LinkedIn**: Professionalism 40%, Clarity 35%, Insight 25%
  - Authority and expertise valued

### By Audience
- **14-18 years**: Engagement 45%, Brevity 35%, Clarity 20%
  - Short attention spans, need excitement
- **25-45 years**: Clarity 40%, Completeness 35%, Engagement 25%
  - Value thorough information
- **45+ years**: Clarity 45%, Authority 30%, Completeness 25%
  - Prefer detailed, credible content

### By Content Goal
- **Viral/Growth**: Engagement 50%, Shareability 30%, Clarity 20%
- **Education**: Clarity 45%, Completeness 35%, Accuracy 20%
- **Conversion**: Relevance 40%, CTA Strength 35%, Engagement 25%

---

## Input/Output

**Configuration**:
```python
DYNAMIC_WEIGHT_CONFIGS = {
    "default": {
        "clarity": 0.35,
        "engagement": 0.35,
        "alignment": 0.30
    },
    "youtube_shorts_14_18": {
        "clarity": 0.20,
        "engagement": 0.50,
        "alignment": 0.30,
        "learned_from": "500+ high-performing shorts",
        "performance_improvement": "+35%",
        "confidence": 0.92
    },
    "educational_blog_25_45": {
        "clarity": 0.50,
        "engagement": 0.20,
        "alignment": 0.30,
        "learned_from": "300+ educational posts",
        "performance_improvement": "+28%",
        "confidence": 0.88
    }
}
```

**Usage**:
```python
result = check_title_acceptance(
    title_text="The One Thing Python Developers Never Do",
    platform="youtube_shorts",
    audience_age_range="14-18",
    content_goal="viral",
    use_dynamic_weights=True  # NEW parameter
)

# Result uses dynamically optimized weights
{
    "weights_used": {
        "clarity": 0.20,      # Reduced for shorts
        "engagement": 0.50,   # Increased for viral
        "alignment": 0.30
    },
    "weight_reasoning": "Optimized for YouTube Shorts targeting 14-18 audience with viral goal. Data shows engagement matters 2.5x more than clarity for this context.",
    "scores": {
        "clarity": 75,
        "engagement": 92,     # High score on high-weight criterion
        "alignment": 85
    },
    "weighted_overall": 85,   # (75*0.20 + 92*0.50 + 85*0.30)
    "default_overall": 84,    # Would have been with default weights
    "improvement": +1,
    "accepted": True
}
```

---

## Technical Implementation

```python
class DynamicWeightingSystem:
    def __init__(self):
        self.weight_optimizer = WeightOptimizer()
        self.performance_tracker = PerformanceTracker()
    
    def get_optimal_weights(
        self,
        platform: str,
        audience: dict,
        content_type: str,
        goal: str = "engagement"
    ) -> dict:
        """Get dynamically optimized weights for context."""
        
        # Build context key
        context_key = self._build_context_key(
            platform, audience, content_type, goal
        )
        
        # Check cache
        cached_weights = self._get_cached_weights(context_key)
        if cached_weights and self._is_fresh(cached_weights):
            return cached_weights
        
        # Calculate optimal weights from performance data
        optimal_weights = self.weight_optimizer.optimize(
            context=context_key,
            performance_data=self.performance_tracker.get_data(context_key),
            current_weights=self._get_default_weights()
        )
        
        # Cache and return
        self._cache_weights(context_key, optimal_weights)
        return optimal_weights

class WeightOptimizer:
    def optimize(
        self,
        context: str,
        performance_data: List[dict],
        current_weights: dict
    ) -> dict:
        """Optimize weights based on performance data."""
        
        # Extract features and targets
        X = []  # Scores for each criterion
        y = []  # Actual performance (CTR, completion rate, etc.)
        
        for item in performance_data:
            X.append([
                item['clarity_score'],
                item['engagement_score'],
                item['alignment_score']
            ])
            y.append(item['performance_score'])
        
        # Use linear regression to find optimal weights
        # Weights that maximize correlation with performance
        model = Ridge(alpha=0.1)  # Regularized to prevent overfitting
        model.fit(X, y)
        
        # Extract coefficients as weights (normalized to sum to 1)
        raw_weights = model.coef_
        normalized_weights = self._normalize_weights(raw_weights)
        
        # Gradual adjustment (don't shift too quickly)
        adjusted_weights = self._gradual_adjustment(
            current=current_weights,
            target=normalized_weights,
            step_size=0.1  # 10% shift per iteration
        )
        
        return {
            "clarity": adjusted_weights[0],
            "engagement": adjusted_weights[1],
            "alignment": adjusted_weights[2],
            "learned_from": f"{len(performance_data)} samples",
            "confidence": self._calculate_confidence(model, X, y)
        }
    
    def _gradual_adjustment(
        self,
        current: dict,
        target: dict,
        step_size: float
    ) -> list:
        """Gradually adjust weights to avoid sudden changes."""
        
        adjusted = []
        for key in ["clarity", "engagement", "alignment"]:
            current_val = current[key]
            target_val = target[key]
            
            # Move step_size% towards target
            new_val = current_val + (target_val - current_val) * step_size
            adjusted.append(new_val)
        
        # Ensure they sum to 1
        return self._normalize_weights(adjusted)
```

---

## Dependencies

- **MVP-012**: Title Acceptance Gate (enhancement target)
- **MVP-013**: Script Acceptance Gate (enhancement target)
- **IMP-012**: Historical Data (weight optimization source)
- **IMP-013**: Custom Thresholds (weights work with thresholds)
- ML libraries: scikit-learn for optimization

---

## Success Metrics

- Dynamic weights improve prediction accuracy by 25-40%
- Weight-optimized acceptance correlates better with performance (r > 0.75)
- System identifies optimal weights within 100 samples per context
- Weight drift stays within ±5% per month (stability)
- A/B testing shows dynamic weights improve outcomes by 20%+

---

**Created**: 2025-11-24  
**Owner**: Worker17 (Analytics Specialist)  
**Category**: Acceptance Gates Improvements
