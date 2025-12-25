# IMP-009: Transition Quality Improvement

**Type**: Improvement - Script Generation  
**Worker**: Worker13 (Prompt Engineering Master)  
**Priority**: Medium  
**Effort**: 1.5 days  
**Module**: `PrismQ.T.Content` (all submodules)  
**Category**: Script Generation  
**Status**: 🎯 PLANNED

---

## Description

Implement transition quality analysis and improvement system for scripts. Identifies weak or abrupt transitions between sections, provides transition suggestions, and generates smooth connective phrases. Smooth transitions increase perceived content quality and viewer retention.

---

## Business Justification

- Poor transitions create jarring experience (20-30% drop in perceived quality)
- Smooth transitions improve comprehension by 25%+
- Professional transitions increase credibility
- Automated improvement saves editing time
- Consistent transition quality across all content

---

## Acceptance Criteria

- [ ] Detect transition points in scripts
- [ ] Score transition quality (smoothness, relevance, naturalness)
- [ ] Identify abrupt or missing transitions
- [ ] Suggest improved transition phrases
- [ ] Generate context-aware transition options
- [ ] Support different transition types (chronological, logical, spatial, contrastive)
- [ ] Integrate with script generation and improvement
- [ ] Add transition score to quality reviews
- [ ] Provide transition templates library
- [ ] Track high-performing transition patterns

---

## Transition Types and Patterns

### Chronological Transitions
- "Meanwhile...", "After that...", "Three days later...", "In that moment..."

### Logical Transitions
- "As a result...", "Therefore...", "This means that...", "Because of this..."

### Additive Transitions
- "Moreover...", "In addition...", "What's more...", "On top of that..."

### Contrastive Transitions
- "However...", "On the other hand...", "Despite this...", "Yet..."

### Clarifying Transitions
- "In other words...", "To put it simply...", "What this means is...", "Essentially..."

### Sequential Transitions
- "First...", "Next...", "Finally...", "The last step..."

---

## Input/Output

**Input**:
- Script text
- Content type
- Transition style preference (formal/casual/invisible)

**Output**:
```python
{
    "overall_transition_score": 78,
    "transitions_analyzed": 8,
    "issues_found": 3,
    "analysis": [
        {
            "location": "line 12",
            "current": "The house was abandoned. It had secrets.",
            "score": 45,
            "issue": "abrupt_shift",
            "type_needed": "contrastive",
            "suggestions": [
                "The house was abandoned. But it held secrets that refused to die.",
                "The house was abandoned. Yet within its walls, secrets remained.",
                "Though the house stood empty, its secrets endured."
            ],
            "recommended": "The house was abandoned. Yet within its walls, secrets remained."
        },
        {
            "location": "line 28",
            "current": "We explored the basement. The attic had clues too.",
            "score": 50,
            "issue": "missing_logical_connection",
            "type_needed": "additive",
            "suggestions": [
                "We explored the basement. But the attic revealed even more clues.",
                "After searching the basement, we discovered the attic held crucial clues.",
                "The basement yielded some answers. The attic, however, held the key."
            ]
        }
    ],
    "recommendations": [
        "Add transition at line 12 (abrupt topic shift)",
        "Strengthen connection at line 28",
        "Consider adding summary transition before conclusion"
    ]
}
```

---

## Technical Implementation

```python
TRANSITION_PATTERNS = {
    "chronological": {
        "weak": ["then", "next", "after"],
        "medium": ["moments later", "meanwhile", "shortly after"],
        "strong": ["as the sun set", "three days later", "in that exact moment"]
    },
    "logical": {
        "weak": ["so", "thus"],
        "medium": ["therefore", "as a result"],
        "strong": ["this revelation meant that", "the implications were clear"]
    }
    # ... more patterns
}

class TransitionAnalyzer:
    def analyze_transitions(self, script: str, content_type: str) -> TransitionAnalysis:
        # Split into sentences/sections
        sentences = self._split_sentences(script)
        
        # Identify transitions
        transitions = []
        for i in range(len(sentences) - 1):
            current = sentences[i]
            next_sent = sentences[i + 1]
            
            transition = self._analyze_transition_quality(current, next_sent)
            transitions.append(transition)
        
        # Calculate overall score
        overall_score = sum(t.score for t in transitions) / len(transitions)
        
        # Generate improvement suggestions
        suggestions = self._generate_suggestions(transitions, content_type)
        
        return TransitionAnalysis(
            overall_score=overall_score,
            transitions=transitions,
            suggestions=suggestions
        )
    
    def _analyze_transition_quality(self, current: str, next_sent: str) -> TransitionScore:
        # Check for explicit transition words
        has_transition = self._has_transition_word(next_sent)
        
        # Check semantic continuity
        continuity = self._check_semantic_continuity(current, next_sent)
        
        # Detect abrupt shifts
        is_abrupt = continuity < 0.5 and not has_transition
        
        # Score (0-100)
        score = self._calculate_transition_score(
            has_transition, 
            continuity, 
            is_abrupt
        )
        
        return TransitionScore(
            current=current,
            next=next_sent,
            score=score,
            has_transition=has_transition,
            is_abrupt=is_abrupt
        )
    
    def _suggest_improvements(self, transition: TransitionScore) -> List[str]:
        # Determine needed transition type
        trans_type = self._determine_transition_type(
            transition.current, 
            transition.next
        )
        
        # Generate contextual suggestions
        suggestions = self._generate_contextual_transitions(
            transition.current,
            transition.next,
            trans_type
        )
        
        return suggestions
```

---

## Dependencies

- **MVP-003**: T.Script.FromIdeaAndTitle
- **MVP-007**: T.Script.FromOriginalScriptAndReviewAndTitle
- **IMP-008**: Pacing Analysis (transitions affect pacing)
- NLP library for semantic similarity

---

## Success Metrics

- Transition quality scores correlate with viewer retention (r > 0.5)
- Scripts with good transitions (>80) perceived as 30% more professional
- Transition suggestions accepted by reviewers >75% of the time
- Abrupt transition detection accuracy >90%
- User satisfaction with suggestions >85%

---

**Created**: 2025-11-24  
**Owner**: Worker13 (Prompt Engineering Master)  
**Category**: Script Generation Improvements
