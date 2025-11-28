# IMP-003: SEO-Focused Title Suggestion System

**Type**: Improvement - Title Generation  
**Worker**: Worker13 (Prompt Engineering Master)  
**Priority**: High  
**Effort**: 2 days  
**Module**: `PrismQ.T.Title` (all submodules)  
**Category**: Title Generation  
**Status**: 🎯 PLANNED

---

## Description

Implement SEO-focused title suggestion system that generates titles optimized for search engine visibility and ranking. This system analyzes keyword opportunities, search intent, and SEO best practices to create titles that perform well in organic search while maintaining engagement value.

Builds upon POST-001 (SEO Keywords) by focusing specifically on title optimization during the generation phase, rather than post-publishing analysis.

---

## Business Justification

- SEO-optimized titles drive 50-80% more organic traffic
- Improves content discoverability in search engines
- Increases long-term content value (evergreen traffic)
- Reduces dependency on social media promotion
- Better ROI on content production

---

## Acceptance Criteria

- [ ] Implement keyword suggestion engine for title generation
- [ ] Analyze search volume and competition for title keywords
- [ ] Generate SEO-optimized title variants (10+ suggestions)
- [ ] Score titles for SEO value (keyword presence, placement, density)
- [ ] Identify search intent alignment (informational, navigational, transactional)
- [ ] Suggest long-tail keyword opportunities
- [ ] Check title uniqueness against existing content
- [ ] Integrate with title generation prompts
- [ ] Add SEO score to title acceptance gate
- [ ] Provide SEO improvement recommendations

---

## SEO Optimization Factors

### Primary Factors (High Impact)
1. **Keyword Placement**: Primary keyword in first 50 characters
2. **Search Intent Match**: Title aligns with user search intent
3. **Keyword Density**: Optimal balance (not stuffing)
4. **Title Uniqueness**: Distinctive from competitors

### Secondary Factors (Medium Impact)
5. **Long-tail Keywords**: Specific, less competitive phrases
6. **Search Volume**: Keywords with decent search volume
7. **Semantic Keywords**: Related terms and synonyms
8. **Click-Worthiness**: Engaging while SEO-optimized

### Technical Factors
9. **Length Optimization**: 50-60 characters for optimal SERP display
10. **Special Characters**: Proper use of separators (|, -, :)
11. **Capitalization**: Title case for readability
12. **Stop Words**: Strategic use vs. removal

---

## Input/Output

**Input**:
- Idea/concept
- Target keywords (optional)
- Content type
- Target audience
- Geographic focus (optional)

**Output**:
```python
{
    "seo_optimized_titles": [
        {
            "title": "How to Master Python in 30 Days | Complete Guide 2024",
            "seo_score": 92,
            "primary_keyword": "master python",
            "secondary_keywords": ["python guide", "learn python"],
            "search_volume": "high",
            "competition": "medium",
            "search_intent": "informational",
            "keyword_placement": "excellent",
            "uniqueness_score": 85,
            "recommendations": [
                "Primary keyword well-placed",
                "Year adds freshness signal",
                "Length optimal for SERP display"
            ]
        },
        # ... more variants
    ],
    "keyword_opportunities": [
        {"keyword": "python tutorial", "volume": 50000, "difficulty": 65},
        {"keyword": "learn python fast", "volume": 8000, "difficulty": 45}
    ],
    "competitor_analysis": {
        "top_ranking_titles": [...],
        "gaps": ["Few titles focus on 30-day timeframe"],
        "opportunities": ["Beginner-focused angle underserved"]
    }
}
```

---

## Dependencies

- **MVP-002**: T.Title.From.Idea (integration point)
- **POST-001**: SEO Keywords (complementary, shares keyword data)
- **IMP-001**: Platform Optimization (SEO length varies by platform)
- SEO API access (optional): Google Keyword Planner, SEMrush, Ahrefs

---

## Technical Notes

### Implementation Approach

1. **Keyword Research Engine** (`T/Title/seo/keyword_research.py`):
```python
class KeywordResearch:
    def suggest_keywords(self, idea: Idea, limit: int = 20) -> List[KeywordSuggestion]:
        """Suggest relevant keywords for title."""
        
        # Extract core concepts
        concepts = self._extract_concepts(idea)
        
        # Generate keyword variations
        keywords = self._generate_variations(concepts)
        
        # Score by search volume and competition
        scored = self._score_keywords(keywords)
        
        # Filter and rank
        return sorted(scored, key=lambda x: x.seo_value)[:limit]
    
    def _score_keywords(self, keywords: List[str]) -> List[KeywordSuggestion]:
        """Score keywords for SEO value."""
        results = []
        for kw in keywords:
            volume = self._get_search_volume(kw)  # API or estimate
            competition = self._get_competition(kw)
            
            # Calculate SEO value score
            seo_value = self._calculate_seo_value(volume, competition)
            
            results.append(KeywordSuggestion(
                keyword=kw,
                search_volume=volume,
                competition=competition,
                seo_value=seo_value
            ))
        return results
```

2. **SEO Title Generator** (`T/Title/seo/seo_title_generator.py`):
```python
class SEOTitleGenerator:
    def generate_seo_titles(
        self,
        idea: Idea,
        keywords: List[str],
        count: int = 10
    ) -> List[SEOTitle]:
        """Generate SEO-optimized title variants."""
        
        titles = []
        
        # Strategy 1: Keyword-first titles
        titles.extend(self._generate_keyword_first(keywords))
        
        # Strategy 2: Natural integration
        titles.extend(self._generate_natural_integration(idea, keywords))
        
        # Strategy 3: Long-tail focused
        titles.extend(self._generate_long_tail(keywords))
        
        # Strategy 4: Question-based (high intent)
        titles.extend(self._generate_question_based(keywords))
        
        # Score each title
        scored_titles = [self._score_seo_title(t) for t in titles]
        
        # Return top N
        return sorted(scored_titles, key=lambda x: x.seo_score, reverse=True)[:count]
    
    def _score_seo_title(self, title: str) -> SEOTitle:
        """Comprehensive SEO scoring."""
        score = 0
        
        # Keyword placement (0-30 points)
        score += self._score_keyword_placement(title)
        
        # Keyword density (0-20 points)
        score += self._score_keyword_density(title)
        
        # Length optimization (0-15 points)
        score += self._score_length(title)
        
        # Search intent match (0-20 points)
        score += self._score_search_intent(title)
        
        # Uniqueness (0-15 points)
        score += self._score_uniqueness(title)
        
        return SEOTitle(title=title, seo_score=score, ...)
```

3. **Search Intent Classifier** (`T/Title/seo/intent_classifier.py`):
```python
INTENT_PATTERNS = {
    "informational": ["how to", "what is", "guide", "tutorial", "tips"],
    "navigational": ["official", "login", "website", "portal"],
    "transactional": ["buy", "price", "deal", "discount", "review"],
    "commercial": ["best", "top", "vs", "compare", "alternative"]
}

def classify_search_intent(title: str) -> str:
    """Classify search intent based on title patterns."""
    title_lower = title.lower()
    
    scores = {intent: 0 for intent in INTENT_PATTERNS}
    
    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if pattern in title_lower:
                scores[intent] += 1
    
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "unknown"
```

### Files to Create

**New Files**:
- `T/Title/seo/keyword_research.py` - Keyword suggestion engine
- `T/Title/seo/seo_title_generator.py` - SEO-optimized generation
- `T/Title/seo/intent_classifier.py` - Search intent analysis
- `T/Title/seo/seo_scorer.py` - SEO scoring algorithms
- `T/_meta/data/seo_patterns.json` - SEO pattern database

**Modified Files**:
- `T/Title/From/Idea/src/title_generator.py` - Add SEO mode
- `T/Review/Title/Acceptance/acceptance.py` - Add SEO criteria

### Testing Requirements

- [ ] Keyword suggestion accuracy tests
- [ ] SEO scoring algorithm validation
- [ ] Search intent classification tests (>90% accuracy)
- [ ] Title uniqueness verification tests
- [ ] Integration with title generation tests
- [ ] Performance tests (generation time <2 seconds)
- [ ] A/B testing setup for SEO vs. non-SEO titles

---

## Success Metrics

- SEO-optimized titles rank 30%+ higher in search results
- Organic traffic from titled content increases 50%+
- Keyword placement accuracy >95%
- Search intent classification accuracy >90%
- Title uniqueness score >80% on average
- SEO score correlates with actual ranking (r > 0.6)

---

## Related Issues

- POST-001: SEO Keywords (complementary post-publishing analysis)
- IMP-001: Platform Optimization (SEO varies by platform)
- IMP-002: Emotional Scoring (balance SEO with engagement)
- IMP-005: Title Strategies (SEO as a generation strategy)

---

**Created**: 2025-11-24  
**Owner**: Worker13 (Prompt Engineering Master)  
**Category**: Title Generation Improvements
