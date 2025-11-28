# IMP-005: Enhanced Title Generation Strategies

**Type**: Improvement - Title Generation  
**Worker**: Worker13 (Prompt Engineering Master)  
**Priority**: High  
**Effort**: 2 days  
**Module**: `PrismQ.T.Title.From.Idea`, `PrismQ.T.Title.From.Title.Review.Script`  
**Category**: Title Generation  
**Status**: 🎯 PLANNED

---

## Description

Expand and enhance the title generation strategy system beyond the current 10 strategies (Direct, Question, How-to, Curiosity, Authoritative, Listicle, Problem-Solution, Comparison, Ultimate-Guide, Benefit). Add 10+ new advanced strategies, improve prompt engineering for each strategy, and implement dynamic strategy selection based on content type and audience.

Current title generation uses fixed prompts for 10 strategies. This enhancement adds more sophisticated strategies and adaptive generation.

---

## Business Justification

- More diverse title options lead to better engagement
- Strategy diversity reduces title fatigue
- Advanced strategies target specific audience segments
- Improved prompts generate higher-quality titles
- Dynamic selection optimizes for content type

---

## Acceptance Criteria

- [ ] Add 10+ new title generation strategies
- [ ] Improve prompt engineering for all strategies (existing + new)
- [ ] Implement dynamic strategy selection algorithm
- [ ] Add few-shot examples for each strategy
- [ ] Support strategy combinations (hybrid strategies)
- [ ] Create strategy effectiveness scoring
- [ ] Integrate with A/B testing framework
- [ ] Add strategy recommendation system
- [ ] Document strategy best practices
- [ ] Support custom user-defined strategies

---

## New Title Generation Strategies

### Advanced Engagement Strategies (6 new)

1. **Controversy/Debate**: Challenges conventional wisdom
   - Example: "Why Everyone Is Wrong About AI Safety"
   - Best for: Opinion pieces, thought leadership
   - Risk: Can alienate some audience segments

2. **Curiosity Gap**: Creates knowledge gap that demands filling
   - Example: "The One Thing Successful People Never Do"
   - Best for: Viral content, social media
   - Risk: Can feel clickbaity if overused

3. **Contrarian**: Takes opposite stance from mainstream
   - Example: "Stop Learning to Code: Here's What to Do Instead"
   - Best for: Thought leadership, niche audiences
   - Risk: May reduce broad appeal

4. **Personal Story**: First-person narrative angle
   - Example: "How I Lost $1 Million and Found Success"
   - Best for: Personal brands, testimonials
   - Risk: Requires authentic personal experience

5. **Data-Driven**: Leads with statistics or research
   - Example: "87% of Startups Fail Because of This Mistake"
   - Best for: Business, education, scientific content
   - Risk: Requires accurate data

6. **Challenge/Quest**: Frames as achievable goal
   - Example: "30-Day Challenge: Transform Your Morning Routine"
   - Best for: Self-improvement, tutorials
   - Risk: Commitment level may deter some

### Psychological Trigger Strategies (4 new)

7. **Fear-of-Missing-Out (FOMO)**: Urgency and exclusivity
   - Example: "Last Chance: Join 10,000 Who Already Know This"
   - Best for: Limited-time content, courses, events
   - Risk: Overuse reduces effectiveness

8. **Social Proof**: Leverages others' success/adoption
   - Example: "Join 1 Million Users Who Switched to This Method"
   - Best for: Product launches, trend adoption
   - Risk: Numbers must be verifiable

9. **Authority Transfer**: Borrows credibility from experts
   - Example: "Harvard Study Reveals Shocking Truth About Sleep"
   - Best for: Educational, health, science content
   - Risk: Requires proper sourcing

10. **Identity/Tribe**: Appeals to specific group membership
    - Example: "For Developers Who Hate Meetings"
    - Best for: Niche audiences, community content
    - Risk: May exclude others

### Format Innovation Strategies (3 new)

11. **Meta-Commentary**: Commentary on the content itself
    - Example: "The Article That Made 1,000 CEOs Quit Their Jobs"
    - Best for: Impactful content, case studies
    - Risk: Can seem self-aggrandizing

12. **Paradox**: Presents apparent contradiction
    - Example: "The Lazy Person's Guide to Getting More Done"
    - Best for: Productivity, unconventional methods
    - Risk: Requires resolution in content

13. **Sensory**: Emphasizes sensory experience
    - Example: "The Sound That Changed How We Think About Music"
    - Best for: Arts, entertainment, immersive content
    - Risk: Harder to execute in text format

### Future: AI-Generated Custom Strategies
- Dynamic strategy creation based on content analysis
- Hybrid strategies combining multiple approaches
- Audience-specific custom strategies

---

## Input/Output

**Input**:
- Idea/concept
- Content type
- Target audience
- Platform
- Strategy preference (optional)

**Output**:
```python
{
    "recommended_strategies": [
        {
            "strategy": "curiosity_gap",
            "score": 95,
            "reason": "High engagement for target audience (18-34)",
            "estimated_ctr": 8.5
        },
        {
            "strategy": "data_driven",
            "score": 88,
            "reason": "Content has strong statistics",
            "estimated_ctr": 7.2
        }
    ],
    "generated_titles": [
        {
            "title": "The One Thing Nobody Tells You About Python",
            "strategy": "curiosity_gap",
            "score": 92,
            "emotional_resonance": 85,
            "seo_score": 78
        },
        {
            "title": "73% of Python Developers Wish They Knew This Earlier",
            "strategy": "data_driven",
            "score": 89,
            "emotional_resonance": 80,
            "seo_score": 85
        }
        # ... more titles
    ],
    "strategy_combinations": [
        {
            "strategies": ["curiosity_gap", "listicle"],
            "title": "7 Secrets Nobody Tells You About Python",
            "score": 94
        }
    ]
}
```

---

## Dependencies

- **MVP-002**: T.Title.From.Idea (enhancement target)
- **IMP-002**: Emotional Scoring (strategy selection input)
- **IMP-003**: SEO Enhancement (strategy selection input)
- Advanced prompt engineering techniques

---

## Technical Notes

### Implementation Approach

1. **Strategy Library** (`T/Title/strategies/strategy_library.py`):
```python
TITLE_STRATEGIES = {
    # Existing strategies (enhanced)
    "direct": {
        "description": "Clear, straightforward title",
        "prompt_template": "Generate a direct, clear title...",
        "few_shot_examples": [...],
        "best_for": ["educational", "professional"],
        "engagement_factor": 0.7,
        "seo_factor": 0.9
    },
    
    # New strategies
    "curiosity_gap": {
        "description": "Creates knowledge gap demanding resolution",
        "prompt_template": """Generate a title that creates curiosity...
        Examples:
        - "The One Thing X Never Do"
        - "What Nobody Tells You About X"
        - "The Secret Behind X That Everyone Misses"
        
        Rules:
        - Hint at valuable information without revealing it
        - Use singular forms ("One Thing" not "Things")
        - Imply exclusivity or hidden knowledge
        - Avoid clickbait overuse
        """,
        "few_shot_examples": [
            {"input": "python tips", "output": "The One Python Trick Senior Developers Don't Share"},
            {"input": "weight loss", "output": "What Doctors Won't Tell You About Losing Weight"}
        ],
        "best_for": ["viral", "social_media", "entertainment"],
        "engagement_factor": 0.95,
        "seo_factor": 0.6,
        "risk_level": "medium"  # Can feel clickbaity
    },
    
    "controversy": {
        "description": "Challenges conventional wisdom",
        "prompt_template": """Generate a controversial title...
        Examples:
        - "Why Everyone Is Wrong About X"
        - "The Inconvenient Truth About X"
        - "Stop Doing X: Here's Why"
        
        Rules:
        - Challenge mainstream view
        - Imply conventional wisdom is flawed
        - Must be defensible in content
        - Balance controversy with credibility
        """,
        "few_shot_examples": [...],
        "best_for": ["opinion", "thought_leadership"],
        "engagement_factor": 0.9,
        "seo_factor": 0.7,
        "risk_level": "high"  # Can alienate
    },
    
    # ... more strategies
}
```

2. **Strategy Selector** (`T/Title/strategies/strategy_selector.py`):
```python
class StrategySelector:
    def recommend_strategies(
        self,
        idea: Idea,
        content_type: str,
        audience: dict,
        platform: str,
        count: int = 3
    ) -> List[StrategyRecommendation]:
        """Recommend best strategies for this content."""
        
        # Analyze content characteristics
        content_analysis = self._analyze_content(idea, content_type)
        
        # Score each strategy
        strategy_scores = {}
        for strategy_name, strategy in TITLE_STRATEGIES.items():
            score = self._score_strategy_fit(
                strategy,
                content_analysis,
                audience,
                platform
            )
            strategy_scores[strategy_name] = score
        
        # Return top N
        top_strategies = sorted(
            strategy_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:count]
        
        return [
            StrategyRecommendation(
                strategy=name,
                score=score,
                reason=self._explain_recommendation(name, score, content_analysis)
            )
            for name, score in top_strategies
        ]
```

3. **Enhanced Title Generator** (`T/Title/strategies/enhanced_generator.py`):
```python
class EnhancedTitleGenerator:
    def generate_with_strategy(
        self,
        idea: Idea,
        strategy: str,
        **kwargs
    ) -> List[str]:
        """Generate titles using specific strategy."""
        
        strategy_config = TITLE_STRATEGIES[strategy]
        
        # Build enhanced prompt with few-shot examples
        prompt = self._build_enhanced_prompt(
            idea,
            strategy_config,
            **kwargs
        )
        
        # Generate titles
        titles = self._call_llm(prompt, count=kwargs.get('count', 3))
        
        # Post-process and validate
        validated_titles = self._validate_strategy_compliance(
            titles,
            strategy_config
        )
        
        return validated_titles
```

### Files to Create

**New Files**:
- `T/Title/strategies/strategy_library.py` - All strategies with prompts
- `T/Title/strategies/strategy_selector.py` - Strategy recommendation
- `T/Title/strategies/enhanced_generator.py` - Enhanced generation
- `T/Title/strategies/hybrid_strategies.py` - Strategy combinations
- `T/_meta/data/strategy_examples.json` - Few-shot examples

**Modified Files**:
- `T/Title/From/Idea/src/title_generator.py` - Use enhanced strategies
- `T/Title/ABTesting/ab_testing.py` - Add strategy A/B testing

### Testing Requirements

- [ ] Each strategy generates appropriate titles (90%+ success rate)
- [ ] Strategy selector recommends relevant strategies (>80% accuracy)
- [ ] Few-shot examples improve generation quality (measurable)
- [ ] Hybrid strategies produce coherent titles
- [ ] Performance tests (generation time <3 seconds for 10 strategies)
- [ ] A/B tests validate strategy effectiveness
- [ ] Edge cases: ambiguous content, niche topics

---

## Success Metrics

- Title variant quality scores improve by 20%+
- Strategy recommendation accuracy >80% (validated by human review)
- Generation diversity increases (measured by title uniqueness)
- Engagement rates improve by 15%+ for new strategies
- Strategy-audience fit correlation >0.7
- User satisfaction with strategy options >85%

---

## Related Issues

- IMP-001: Platform Optimization (strategies vary by platform)
- IMP-002: Emotional Scoring (strategies have emotional profiles)
- IMP-003: SEO Enhancement (strategies have SEO implications)
- POST-006: A/B Testing (test strategy effectiveness)

---

**Created**: 2025-11-24  
**Owner**: Worker13 (Prompt Engineering Master)  
**Category**: Title Generation Improvements
