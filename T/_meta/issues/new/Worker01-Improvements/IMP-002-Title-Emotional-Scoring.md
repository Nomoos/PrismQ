# IMP-002: Emotional Resonance Scoring for Titles

**Type**: Improvement - Title Generation  
**Worker**: Worker17 (Analytics Specialist)  
**Priority**: Medium  
**Effort**: 2 days  
**Module**: `PrismQ.T.Title` (all submodules)  
**Category**: Title Generation  
**Status**: 🎯 PLANNED

---

## Description

Implement emotional resonance scoring system for titles to evaluate their emotional impact and engagement potential. This system will analyze titles for emotional triggers, sentiment, intensity, and audience resonance, providing scores and recommendations for improvement.

Research shows titles with appropriate emotional resonance have 40-60% higher click-through rates. This enhancement quantifies emotional impact and guides title optimization.

---

## Business Justification

- Emotional titles drive 40-60% higher engagement
- Data-driven approach to emotional optimization
- Reduces guesswork in title creation
- Enables A/B testing of emotional strategies
- Helps maintain consistent emotional tone

---

## Acceptance Criteria

- [ ] Implement emotional category detection (joy, fear, surprise, curiosity, anger, sadness, etc.)
- [ ] Calculate emotional intensity score (0-100)
- [ ] Identify emotional triggers and power words
- [ ] Support sentiment analysis (positive, negative, neutral)
- [ ] Generate emotional tone recommendations
- [ ] Score emotional appropriateness for target audience
- [ ] Integrate with title acceptance gate
- [ ] Provide emotional comparison across title variants
- [ ] Add emotional metrics to A/B testing framework
- [ ] Support emotional tone customization per content type

---

## Emotional Categories

### Primary Emotions
- **Curiosity**: Mystery, intrigue, question-raising (optimal for most content)
- **Excitement**: Enthusiasm, anticipation, thrill
- **Fear**: Concern, worry, caution (effective but use carefully)
- **Surprise**: Unexpected, shocking, amazing
- **Joy**: Happiness, delight, satisfaction
- **Anger**: Frustration, injustice, outrage (use sparingly)

### Composite Emotions
- **Urgency**: Time-sensitive, immediate action needed
- **Empathy**: Understanding, connection, relatability
- **Authority**: Confidence, expertise, trustworthiness
- **Humor**: Lighthearted, funny, entertaining

---

## Input/Output

**Input**:
- Title text
- Target audience demographics
- Content type (educational, entertainment, news, etc.)
- Desired emotional tone (optional)

**Output**:
```python
{
    "title": "The Secret Nobody Wants You to Know",
    "emotional_score": 85,
    "primary_emotion": "curiosity",
    "secondary_emotions": ["surprise", "urgency"],
    "intensity": 78,
    "sentiment": "neutral-positive",
    "power_words": ["secret", "nobody", "know"],
    "triggers": {
        "curiosity": 90,
        "urgency": 65,
        "exclusivity": 75
    },
    "audience_resonance": 82,
    "recommendations": [
        "Strong curiosity trigger - good for engagement",
        "Consider softening urgency for broader appeal",
        "Exclusivity angle works well for target demographic"
    ]
}
```

---

## Dependencies

- **MVP-002**: T.Title.FromIdea
- **MVP-012**: Title Acceptance Gate (integration point)
- NLP library for emotion detection (NLTK, TextBlob, or custom)

---

## Technical Notes

### Implementation Approach

1. **Emotional Lexicon** (`T/Title/analysis/emotional_lexicon.py`):
```python
EMOTIONAL_WORDS = {
    "curiosity": {
        "high": ["secret", "mystery", "hidden", "unknown", "revealed"],
        "medium": ["discover", "find", "learn", "explore"],
        "low": ["see", "look", "check"]
    },
    "urgency": {
        "high": ["now", "immediately", "urgent", "critical"],
        "medium": ["soon", "today", "don't wait"],
        "low": ["eventually", "sometime"]
    },
    # ... more categories
}

POWER_WORDS = [
    "secret", "proven", "guaranteed", "ultimate", "essential",
    "shocking", "amazing", "incredible", "revolutionary",
    # ... more power words
]
```

2. **Emotional Analyzer** (`T/Title/analysis/emotional_analyzer.py`):
```python
class EmotionalAnalyzer:
    def analyze_title(self, title: str, audience: dict) -> EmotionalScore:
        """Analyze emotional resonance of title."""
        
        # Detect primary emotion
        emotions = self._detect_emotions(title)
        primary = max(emotions, key=emotions.get)
        
        # Calculate intensity
        intensity = self._calculate_intensity(title, emotions)
        
        # Find power words
        power_words = self._find_power_words(title)
        
        # Score audience fit
        audience_score = self._score_audience_resonance(
            emotions, audience
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            emotions, intensity, audience_score
        )
        
        return EmotionalScore(
            primary_emotion=primary,
            emotions=emotions,
            intensity=intensity,
            power_words=power_words,
            audience_resonance=audience_score,
            recommendations=recommendations
        )
```

3. **Sentiment Analysis Integration**:
```python
from textblob import TextBlob  # or NLTK/spaCy

def analyze_sentiment(title: str) -> SentimentResult:
    """Analyze sentiment polarity and subjectivity."""
    blob = TextBlob(title)
    return SentimentResult(
        polarity=blob.sentiment.polarity,  # -1 to 1
        subjectivity=blob.sentiment.subjectivity,  # 0 to 1
        classification=_classify_sentiment(blob.sentiment)
    )
```

### Files to Create

**New Files**:
- `T/Title/analysis/emotional_lexicon.py` - Emotional word database
- `T/Title/analysis/emotional_analyzer.py` - Core analysis logic
- `T/Title/analysis/sentiment_analyzer.py` - Sentiment analysis
- `T/Title/scoring/emotional_scorer.py` - Scoring algorithms
- `T/_meta/data/emotional_words.json` - Emotional word database (JSON)

**Modified Files**:
- `T/Review/Title/Acceptance/acceptance.py` - Add emotional criteria
- `T/Title/ABTesting/ab_testing.py` - Add emotional metrics

### Testing Requirements

- [ ] Unit tests for each emotional category detection
- [ ] Power word identification accuracy tests
- [ ] Sentiment analysis validation tests
- [ ] Intensity calculation tests
- [ ] Audience resonance scoring tests
- [ ] Integration with acceptance gate tests
- [ ] Edge cases: neutral titles, mixed emotions, sarcasm

---

## Success Metrics

- Emotional scoring accuracy validated against human reviewers (>85% agreement)
- Titles with optimized emotional scores have 20%+ higher CTR
- Emotional recommendations lead to 30%+ improvement in variant quality
- System correctly identifies primary emotion >90% of the time
- Audience resonance scores correlate with engagement metrics (r > 0.7)

---

## Related Issues

- IMP-001: Platform Optimization (emotional intensity varies by platform)
- IMP-005: Title Generation Strategies (uses emotional targeting)
- IMP-007: Hook Effectiveness (similar emotional analysis for scripts)
- POST-006: A/B Testing (emotional metrics for testing)

---

**Created**: 2025-11-24  
**Owner**: Worker17 (Analytics Specialist)  
**Category**: Title Generation Improvements
