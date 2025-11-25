# IMP-015: Automated Actionable Feedback Generation

**Type**: Improvement - Acceptance Gates  
**Worker**: Worker13 (Prompt Engineering Master)  
**Priority**: High  
**Effort**: 2 days  
**Module**: `PrismQ.T.Review.Title.Acceptance`, `PrismQ.T.Review.Script.Acceptance`  
**Category**: Acceptance Gates  
**Status**: 🎯 PLANNED

---

## Description

Implement automated actionable feedback generation system that provides specific, concrete recommendations when content doesn't pass acceptance gates. Currently, feedback is generic ("score too low"). This system analyzes exactly why content failed and provides step-by-step improvement guidance with examples.

Transforms rejection from frustration into learning opportunity with clear path to acceptance.

---

## Business Justification

- Generic feedback leads to repeated failures (60% re-rejection rate)
- Specific feedback reduces re-work time by 50%+
- Actionable guidance improves content quality faster
- Reduces need for manual review and consultation
- Increases user satisfaction and confidence

---

## Acceptance Criteria

- [ ] Generate specific issue identification (not just "low score")
- [ ] Provide concrete improvement suggestions (not vague advice)
- [ ] Include before/after examples
- [ ] Prioritize recommendations by impact
- [ ] Estimate improvement potential per suggestion
- [ ] Support multiple feedback formats (bullet points, step-by-step, examples)
- [ ] Context-aware feedback (varies by content type, platform, audience)
- [ ] Track feedback effectiveness (which suggestions help most)
- [ ] Generate positive reinforcement for passing elements
- [ ] Integrate with revision workflow

---

## Feedback Quality Levels

### Level 1: Generic (Current State - Avoid)
- "Title score too low (68/75)"
- "Improve engagement"
- "Not accepted, needs work"

### Level 2: Specific (Minimum Target)
- "Engagement score: 65/70 (too low)"
- "Title lacks curiosity trigger"
- "Consider adding question or intrigue element"

### Level 3: Actionable (Target)
- "Engagement score: 65/70. Specific issues:"
  - "No emotional trigger words detected"
  - "Title is purely descriptive without hook"
  - "Missing curiosity gap or question format"
- "Recommended changes:"
  - "Add curiosity element: 'The One Thing About...'"
  - "Or use question format: 'Why Do...?'"
  - "Or add emotional word: 'Amazing', 'Shocking', 'Secret'"

### Level 4: Exemplified (Ideal)
- "Engagement score: 65/70. Here's how to improve:"
  - **Current**: "How to Learn Python"
  - **Issue**: Lacks engagement trigger
  - **Fix 1**: "The One Thing Nobody Tells You About Learning Python" (+20 engagement)
  - **Fix 2**: "Why Most People Fail at Python (And How You Won't)" (+18 engagement)
  - **Fix 3**: "Python Learning Secret That Changed Everything" (+15 engagement)
- "Choose one approach and resubmit for acceptance"

---

## Input/Output

**Input**:
- Acceptance result (failed)
- Content text (title/script)
- Scores breakdown
- Context (platform, audience, content type)

**Output**:
```python
{
    "accepted": False,
    "overall_score": 68,
    "threshold": 75,
    "gap": -7,
    
    "detailed_feedback": {
        "summary": "Title is clear but lacks engagement. Needs stronger hook to pass acceptance.",
        
        "issues": [
            {
                "criterion": "engagement",
                "score": 62,
                "threshold": 70,
                "gap": -8,
                "severity": "high",
                "specific_problems": [
                    "No emotional trigger words detected",
                    "Purely descriptive without intrigue",
                    "Missing curiosity gap or question",
                    "Weak call to attention"
                ]
            },
            {
                "criterion": "clarity",
                "score": 78,
                "threshold": 70,
                "gap": +8,
                "severity": "none",
                "feedback": "✓ Clarity is good - no changes needed"
            }
        ],
        
        "prioritized_recommendations": [
            {
                "priority": 1,
                "focus_area": "Add curiosity trigger",
                "potential_improvement": "+15 to +25 points",
                "suggestions": [
                    {
                        "current": "How to Learn Python",
                        "suggested": "The One Thing Nobody Tells You About Learning Python",
                        "reasoning": "Adds curiosity gap + exclusivity",
                        "estimated_engagement": 85,
                        "estimated_overall": 79
                    },
                    {
                        "current": "How to Learn Python",
                        "suggested": "Why Most Python Tutorials Fail (And This One Won't)",
                        "reasoning": "Contrarian + promise of success",
                        "estimated_engagement": 82,
                        "estimated_overall": 77
                    }
                ]
            },
            {
                "priority": 2,
                "focus_area": "Add emotional language",
                "potential_improvement": "+10 to +15 points",
                "suggestions": [
                    "Add power words: Amazing, Proven, Secret, Ultimate",
                    "Example: 'The Amazing Python Learning Method That Actually Works'"
                ]
            }
        ],
        
        "what_worked": [
            "Clear and concise (78/70)",
            "Good keyword placement",
            "Appropriate length for platform"
        ],
        
        "estimated_effort": "5-10 minutes to revise",
        "confidence": "High - clear issues with proven solutions"
    },
    
    "quick_win": {
        "suggestion": "The One Thing Nobody Tells You About Learning Python",
        "reasoning": "Highest impact change with minimal effort",
        "estimated_acceptance_probability": 0.92
    }
}
```

---

## Technical Implementation

```python
class ActionableFeedbackGenerator:
    def generate_feedback(
        self,
        acceptance_result: AcceptanceResult,
        content: str,
        context: dict
    ) -> ActionableFeedback:
        """Generate specific, actionable feedback."""
        
        if acceptance_result.accepted:
            return self._generate_positive_feedback(acceptance_result)
        
        # Identify specific issues
        issues = self._identify_specific_issues(
            acceptance_result.criteria_results,
            content
        )
        
        # Generate targeted recommendations
        recommendations = self._generate_recommendations(
            issues,
            content,
            context
        )
        
        # Create examples
        examples = self._generate_examples(
            content,
            recommendations,
            context
        )
        
        # Prioritize by impact
        prioritized = self._prioritize_recommendations(
            recommendations,
            issues
        )
        
        # Find quick win
        quick_win = self._find_quick_win(prioritized, examples)
        
        return ActionableFeedback(
            summary=self._generate_summary(issues, recommendations),
            issues=issues,
            recommendations=prioritized,
            examples=examples,
            quick_win=quick_win,
            what_worked=self._identify_strengths(acceptance_result)
        )
    
    def _identify_specific_issues(
        self,
        criteria_results: List[CriterionResult],
        content: str
    ) -> List[SpecificIssue]:
        """Dig deeper than just low score."""
        
        issues = []
        
        for criterion in criteria_results:
            if not criterion.passed:
                # Analyze WHY it failed
                specific_problems = self._analyze_criterion_failure(
                    criterion,
                    content
                )
                
                issues.append(SpecificIssue(
                    criterion=criterion.name,
                    score=criterion.score,
                    threshold=criterion.threshold,
                    problems=specific_problems
                ))
        
        return issues
    
    def _generate_examples(
        self,
        current_content: str,
        recommendations: List[Recommendation],
        context: dict
    ) -> List[Example]:
        """Generate before/after examples using LLM."""
        
        examples = []
        
        for rec in recommendations[:3]:  # Top 3
            prompt = f"""
            Current title: "{current_content}"
            Issue: {rec.issue}
            Goal: {rec.goal}
            Context: {context}
            
            Generate 3 improved versions that address the issue.
            Each should:
            1. Fix the specific problem
            2. Maintain the core message
            3. Sound natural and engaging
            4. Meet quality standards
            
            Format: [Improved Title] - [Why it's better]
            """
            
            improved_versions = self._call_llm(prompt)
            
            examples.append(Example(
                recommendation=rec,
                current=current_content,
                improved_versions=improved_versions
            ))
        
        return examples
```

---

## Dependencies

- **MVP-012**: Title Acceptance Gate (enhancement target)
- **MVP-013**: Script Acceptance Gate (enhancement target)
- **IMP-002**: Emotional Scoring (for engagement feedback)
- **IMP-003**: SEO Enhancement (for SEO feedback)
- **IMP-005**: Title Strategies (for strategy-based suggestions)
- LLM for example generation

---

## Success Metrics

- Re-submission acceptance rate improves from 40% to 75%+
- Average revision time reduces from 30min to 10min
- User satisfaction with feedback >90%
- Feedback actionability rating (can user understand and apply) >95%
- Suggested changes lead to passing scores >85% of time
- Users report reduced frustration (survey score improves by 60%+)

---

**Created**: 2025-11-24  
**Owner**: Worker13 (Prompt Engineering Master)  
**Category**: Acceptance Gates Improvements
