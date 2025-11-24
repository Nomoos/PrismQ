# IMP-008: Pacing and Flow Analysis Tool

**Type**: Improvement - Script Generation  
**Worker**: Worker12 (Content Specialist)  
**Priority**: Medium  
**Effort**: 2 days  
**Module**: `PrismQ.T.Script` (all submodules)  
**Category**: Script Generation  
**Status**: 🎯 PLANNED

---

## Description

Implement pacing and flow analysis tool to evaluate script rhythm, information density, and narrative progression. Identifies sections that drag or rush, detects pacing inconsistencies, and provides recommendations for optimal flow. Good pacing keeps viewers engaged throughout the content.

---

## Business Justification

- Poor pacing causes 30-40% viewer drop-off
- Optimal pacing increases completion rates by 35%+
- Identifies specific problem sections for targeted improvement
- Reduces subjective pacing decisions with data
- Improves content quality consistently

---

## Acceptance Criteria

- [ ] Implement section-by-section pacing analysis
- [ ] Calculate information density score per section
- [ ] Detect pacing inconsistencies (too fast/too slow)
- [ ] Identify sections likely to cause viewer drop-off
- [ ] Provide pacing optimization recommendations
- [ ] Visualize pacing flow (chart/graph)
- [ ] Support different content types (tutorial, story, educational)
- [ ] Integrate with script generation and improvement
- [ ] Add pacing score to script reviews
- [ ] Track pacing patterns that perform well

---

## Pacing Analysis Dimensions

### Primary Metrics
1. **Information Density**: Concepts/facts per section
2. **Sentence Complexity**: Average words per sentence
3. **Transition Quality**: Smoothness between sections
4. **Variation**: Changes in pace to maintain interest

### Secondary Metrics
5. **Paragraph Length**: Visual/audio chunking
6. **Action/Description Ratio**: Show vs. tell balance
7. **Emotional Beats**: Highs and lows throughout
8. **Breathing Room**: Natural pauses and reflection points

---

## Input/Output

**Input**:
- Script text
- Content type (tutorial, story, educational, etc.)
- Target duration
- Platform

**Output**:
```python
{
    "overall_pacing_score": 82,
    "sections": [
        {
            "section": "introduction",
            "duration": "0-10s",
            "words": 30,
            "pacing_score": 95,
            "information_density": "high",
            "assessment": "excellent",
            "issues": []
        },
        {
            "section": "middle",
            "duration": "30-60s",
            "words": 95,
            "pacing_score": 65,
            "information_density": "very_high",
            "assessment": "too_dense",
            "issues": [
                "Information overload (5 concepts in 30s)",
                "Long sentences (avg 22 words)",
                "No breathing room"
            ],
            "recommendations": [
                "Break into 2 sections",
                "Add transition pause",
                "Simplify sentences"
            ]
        }
    ],
    "flow_issues": [
        "Abrupt transition at 30s mark",
        "Middle section drags (40-50s)",
        "Conclusion feels rushed"
    ],
    "pacing_visualization": {
        "timeline": [...],  # For graphing
        "hot_spots": [40, 45, 48]  # Problem areas
    },
    "recommendations": [
        "Redistribute middle content into two beats",
        "Add breathing pause at 35s",
        "Slow down conclusion (currently 180 WPM)"
    ]
}
```

---

## Technical Implementation

```python
class PacingAnalyzer:
    def analyze_pacing(self, script: str, content_type: str) -> PacingAnalysis:
        # Split into sections
        sections = self._split_into_sections(script)
        
        # Analyze each section
        section_analyses = []
        for section in sections:
            analysis = self._analyze_section(section, content_type)
            section_analyses.append(analysis)
        
        # Detect flow issues
        flow_issues = self._detect_flow_issues(section_analyses)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            section_analyses, 
            flow_issues
        )
        
        # Calculate overall score
        overall_score = self._calculate_overall_pacing_score(section_analyses)
        
        return PacingAnalysis(
            overall_score=overall_score,
            sections=section_analyses,
            flow_issues=flow_issues,
            recommendations=recommendations
        )
    
    def _analyze_section(self, section: str, content_type: str) -> SectionAnalysis:
        # Information density
        density = self._calculate_info_density(section)
        
        # Sentence complexity
        avg_sentence_length = self._avg_sentence_length(section)
        
        # Pacing score based on content type expectations
        expected = CONTENT_TYPE_PACING[content_type]
        score = self._score_against_expectations(
            density, 
            avg_sentence_length, 
            expected
        )
        
        return SectionAnalysis(
            text=section,
            density=density,
            complexity=avg_sentence_length,
            score=score
        )
```

---

## Dependencies

- **MVP-003**: T.Script.FromIdeaAndTitle
- **MVP-007**: T.Script.FromOriginalScriptAndReviewAndScript
- **IMP-006**: Platform Timing (pacing varies by duration)

---

## Success Metrics

- Pacing analysis correlates with retention (r > 0.6)
- Scripts with optimal pacing (>80) have 30%+ better completion rates
- Problem section identification accuracy >85%
- Recommendations improve pacing scores by 25%+
- User satisfaction with pacing analysis >85%

---

**Created**: 2025-11-24  
**Owner**: Worker12 (Content Specialist)  
**Category**: Script Generation Improvements
