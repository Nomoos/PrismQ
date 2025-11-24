# IMP-007: Hook Effectiveness Evaluation System

**Type**: Improvement - Script Generation  
**Worker**: Worker17 (Analytics Specialist)  
**Priority**: High  
**Effort**: 1.5 days  
**Module**: `PrismQ.T.Script` (all submodules)  
**Category**: Script Generation  
**Status**: 🎯 PLANNED

---

## Description

Implement hook effectiveness evaluation system to score and optimize script openings (first 3-10 seconds) for maximum audience retention. Research shows 50-70% of viewers decide whether to continue watching within the first 5 seconds. This system quantifies hook quality and provides data-driven optimization recommendations.

---

## Business Justification

- First 5 seconds determine 50-70% of viewer retention
- Strong hooks increase video completion rates by 40-60%
- Data-driven hook optimization reduces guesswork
- Enables A/B testing of different hook strategies
- Improves algorithm favorability (watch time metric)

---

## Acceptance Criteria

- [ ] Implement hook detection and extraction (first 10 seconds/30 words)
- [ ] Score hooks on multiple dimensions (curiosity, clarity, relevance, urgency)
- [ ] Identify hook patterns that perform well (question, statement, story, shock value)
- [ ] Calculate predicted retention rate based on hook quality
- [ ] Provide specific improvement recommendations
- [ ] Integrate with script generation (optimize hooks automatically)
- [ ] Support hook A/B testing framework
- [ ] Track historical hook performance correlation
- [ ] Generate hook variants for testing
- [ ] Add hook score to script acceptance criteria

---

## Hook Evaluation Dimensions

### Core Dimensions (weighted)
1. **Curiosity** (30%): Creates desire to know more
2. **Clarity** (25%): Immediately understandable
3. **Relevance** (25%): Matches title promise and audience interest
4. **Urgency** (20%): Creates need to watch now

### Secondary Factors
5. **Pattern Recognition**: Matches proven hook patterns
6. **Emotional Impact**: Triggers emotional response
7. **Specificity**: Concrete vs. vague language
8. **Length**: Optimal word count for platform

---

## Input/Output

**Input**:
- Full script text
- Title
- Platform
- Target audience

**Output**:
```python
{
    "hook_text": "Every night at midnight, she returns to the house...",
    "hook_duration": 4.2,  # seconds
    "overall_score": 88,
    "dimensions": {
        "curiosity": 95,
        "clarity": 85,
        "relevance": 90,
        "urgency": 80
    },
    "pattern": "mystery_opening",
    "predicted_retention": 72,  # % likely to watch past 10s
    "strengths": [
        "Strong curiosity trigger with 'every night at midnight'",
        "Mystery element engages viewer",
        "Specific detail (house) creates imagery"
    ],
    "weaknesses": [
        "Could add more urgency with time constraint",
        "Consider revealing stakes earlier"
    ],
    "recommendations": [
        "Add: 'But tonight is different' for urgency",
        "Consider: 'You won't believe what happens next'",
        "Test variant: Start with the reveal"
    ],
    "alternative_hooks": [
        "What happens at the house at midnight will shock you...",
        "She's been doing this for 10 years. Tonight, we find out why...",
        "The secret of the midnight visitor is finally revealed..."
    ]
}
```

---

## Hook Pattern Library

**High-Performing Patterns:**
- **Question Hook**: "Have you ever wondered why...?"
- **Mystery Hook**: "Nobody knows what really happened..."
- **Shocking Statement**: "Everything you know about X is wrong."
- **Personal Story**: "This is the day my life changed forever."
- **Data Hook**: "87% of people don't know this..."
- **Challenge Hook**: "Can you solve this in 10 seconds?"
- **Contrast Hook**: "While everyone does X, winners do Y..."

---

## Technical Implementation

```python
class HookEvaluator:
    def evaluate_hook(self, script: str, title: str, platform: str) -> HookScore:
        # Extract hook (first 30 words or 10 seconds)
        hook = self._extract_hook(script, platform)
        
        # Score dimensions
        curiosity = self._score_curiosity(hook, title)
        clarity = self._score_clarity(hook)
        relevance = self._score_relevance(hook, title)
        urgency = self._score_urgency(hook)
        
        # Pattern recognition
        pattern = self._identify_pattern(hook)
        
        # Calculate overall score
        overall = (curiosity * 0.30 + clarity * 0.25 + 
                  relevance * 0.25 + urgency * 0.20)
        
        # Predict retention
        predicted_retention = self._predict_retention(overall, pattern, platform)
        
        # Generate recommendations
        recs = self._generate_recommendations(hook, scores, pattern)
        
        return HookScore(
            hook_text=hook,
            overall_score=overall,
            dimensions={...},
            predicted_retention=predicted_retention,
            recommendations=recs
        )
```

---

## Dependencies

- **MVP-003**: T.Script.FromIdeaAndTitle
- **IMP-002**: Emotional Scoring (applies to hooks)
- **IMP-006**: Platform Timing (hook duration varies)

---

## Success Metrics

- Hook scoring accuracy validated against retention data (r > 0.7)
- High-scoring hooks (>85) show 40%+ better retention
- Hook recommendations improve scores by 25%+
- Pattern identification accuracy >90%
- Predicted retention within ±10% of actual

---

**Created**: 2025-11-24  
**Owner**: Worker17 (Analytics Specialist)  
**Category**: Script Generation Improvements
