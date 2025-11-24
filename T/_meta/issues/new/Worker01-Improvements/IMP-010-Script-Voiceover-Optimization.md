# IMP-010: Voice-Over Readability Optimization

**Type**: Improvement - Script Generation  
**Worker**: Worker12 (Content Specialist)  
**Priority**: High  
**Effort**: 2 days  
**Module**: `PrismQ.T.Script` (all submodules)  
**Category**: Script Generation  
**Status**: 🎯 PLANNED

---

## Description

Implement voice-over readability optimization system to ensure scripts are easy to read aloud, pronounce correctly, and deliver naturally. Identifies tongue-twisters, complex phrases, pronunciation challenges, and provides alternative phrasing. Builds upon existing MVP-020 Readability by adding voice-over-specific analysis.

---

## Business Justification

- Poor voice-over readability causes 40-60% increase in recording time
- Natural-sounding scripts increase perceived professionalism by 50%+
- Reduces re-recording costs (fewer takes needed)
- Improves narrator/voice actor experience
- Enables smoother TTS (text-to-speech) output

---

## Acceptance Criteria

- [ ] Detect tongue-twisters and difficult pronunciation sequences
- [ ] Identify long or complex sentences unsuitable for voice-over
- [ ] Score scripts for voice-over readability (0-100)
- [ ] Suggest simplified alternatives for complex phrases
- [ ] Check breathing point adequacy (natural pause locations)
- [ ] Identify homophone confusion risks
- [ ] Validate proper noun pronunciation guidance
- [ ] Support multiple reading styles (formal, casual, dramatic)
- [ ] Generate pronunciation guides for difficult words
- [ ] Integrate with script generation and quality reviews

---

## Voice-Over Readability Factors

### Critical Issues (High Priority)
1. **Tongue-Twisters**: Repeating similar sounds ("she sells seashells")
2. **Complex Word Clusters**: Multiple long words together
3. **Ambiguous Pronunciation**: Words with multiple pronunciations
4. **Breathing Challenges**: Sentences too long without natural pauses

### Important Factors (Medium Priority)
5. **Homophone Confusion**: Similar-sounding words ("there/their/they're")
6. **Number Reading**: How to read numbers aloud
7. **Acronym Clarity**: How to pronounce abbreviations
8. **Awkward Transitions**: Difficult sound combinations between words

### Nice-to-Have (Low Priority)
9. **Proper Noun Guides**: Pronunciation notes for names/places
10. **Emphasis Suggestions**: Where to add vocal emphasis
11. **Pace Markers**: Where to speed up or slow down
12. **Emotion Cues**: Tone guidance for emotional delivery

---

## Input/Output

**Input**:
- Script text
- Reading style (formal, casual, dramatic, educational)
- Target audience
- Voice type (narrator, character, instructional)

**Output**:
```python
{
    "overall_readability_score": 82,
    "voice_over_score": 76,
    "issues": [
        {
            "type": "tongue_twister",
            "severity": "high",
            "location": "line 15",
            "text": "She sells seashells by the seashore",
            "problem": "Excessive 's' and 'sh' sounds in sequence",
            "alternatives": [
                "She gathers shells along the beach",
                "Seashells line the waterfront",
                "The shore is covered with shells"
            ],
            "recommended": "She gathers shells along the beach"
        },
        {
            "type": "long_sentence",
            "severity": "medium",
            "location": "line 23",
            "text": "The investigation, which had been ongoing for several months and involved multiple agencies from different jurisdictions, finally yielded results.",
            "word_count": 23,
            "breathing_issue": True,
            "alternatives": [
                "The investigation lasted several months. Multiple agencies worked together. Finally, they got results.",
                "After months of investigation across multiple agencies, results finally came.",
                "The long investigation involving many agencies finally paid off."
            ]
        },
        {
            "type": "pronunciation_ambiguity",
            "severity": "low",
            "location": "line 31",
            "word": "read",
            "problem": "Can be pronounced 'reed' (present) or 'red' (past)",
            "context": "She read the book yesterday",
            "correct_pronunciation": "red",
            "suggestion": "Consider 'finished reading' for clarity"
        }
    ],
    "breathing_points": [
        {"location": "line 5", "status": "adequate"},
        {"location": "line 12", "status": "missing", "suggestion": "Add comma after 'However'"},
        {"location": "line 23", "status": "insufficient", "suggestion": "Split sentence"}
    ],
    "pronunciation_guide": [
        {"word": "Nguyen", "pronunciation": "win", "location": "line 7"},
        {"word": "GIF", "pronunciation": "jif or gif", "note": "Either acceptable", "location": "line 19"}
    ],
    "recommendations": [
        "Fix high-severity tongue-twister at line 15",
        "Split long sentence at line 23 for better breathing",
        "Add pronunciation note for 'Nguyen' at line 7",
        "Consider simplifying technical jargon in lines 45-48"
    ]
}
```

---

## Technical Implementation

```python
# Tongue-twister patterns
TONGUE_TWISTER_PATTERNS = {
    "s_sounds": ["s", "sh", "z", "zh"],
    "p_b_sounds": ["p", "b"],
    "t_d_sounds": ["t", "d", "th"],
    "difficult_clusters": ["str", "shr", "thr", "scr"]
}

class VoiceOverAnalyzer:
    def analyze_voice_over_readability(
        self,
        script: str,
        reading_style: str = "casual"
    ) -> VoiceOverAnalysis:
        """Comprehensive voice-over readability analysis."""
        
        # Detect issues
        tongue_twisters = self._detect_tongue_twisters(script)
        long_sentences = self._detect_long_sentences(script)
        pronunciation_issues = self._detect_pronunciation_issues(script)
        breathing_analysis = self._analyze_breathing_points(script)
        
        # Score overall readability
        overall_score = self._calculate_readability_score(
            tongue_twisters,
            long_sentences,
            pronunciation_issues,
            breathing_analysis
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            tongue_twisters,
            long_sentences,
            pronunciation_issues
        )
        
        return VoiceOverAnalysis(
            overall_score=overall_score,
            issues=tongue_twisters + long_sentences + pronunciation_issues,
            breathing_points=breathing_analysis,
            recommendations=recommendations
        )
    
    def _detect_tongue_twisters(self, text: str) -> List[Issue]:
        """Detect sequences of difficult-to-pronounce sounds."""
        issues = []
        words = text.split()
        
        for i in range(len(words) - 3):
            # Check 3-4 word windows for repeated sounds
            window = ' '.join(words[i:i+4])
            
            for sound_group, sounds in TONGUE_TWISTER_PATTERNS.items():
                count = sum(window.lower().count(s) for s in sounds)
                
                if count >= 6:  # Threshold for tongue-twister
                    issues.append(Issue(
                        type="tongue_twister",
                        text=window,
                        severity="high",
                        problem=f"Excessive {sound_group} in sequence"
                    ))
        
        return issues
    
    def _suggest_alternatives(self, problematic_text: str) -> List[str]:
        """Generate easier-to-read alternatives using LLM."""
        
        prompt = f"""
        The following text is difficult to read aloud due to tongue-twister effect:
        "{problematic_text}"
        
        Generate 3 alternative phrasings that:
        1. Convey the same meaning
        2. Are easier to pronounce
        3. Sound natural when spoken
        4. Avoid repetitive sounds
        
        Alternatives:
        """
        
        alternatives = self._call_llm(prompt)
        return alternatives
```

---

## Dependencies

- **MVP-003**: T.Script.FromIdeaAndTitle
- **MVP-007**: T.Script.FromOriginalScriptAndReviewAndTitle
- **MVP-020**: Readability Review (builds upon this)
- Pronunciation library (optional): pronouncing, CMU Pronouncing Dictionary

---

## Success Metrics

- Voice-over recording time reduces by 40%+
- Scripts with high voice-over scores (>85) require 50% fewer takes
- Tongue-twister detection accuracy >90%
- Alternative suggestions accepted >80% of the time
- Narrator satisfaction increases by 60%+
- TTS output quality improves by 35%+

---

## Related Issues

- IMP-006: Platform Timing (voice-over pace affects duration)
- IMP-008: Pacing Analysis (readability affects pacing)
- IMP-009: Transition Quality (transitions must be speakable)
- MVP-020: Readability Review (extends this with voice-over focus)

---

**Created**: 2025-11-24  
**Owner**: Worker12 (Content Specialist)  
**Category**: Script Generation Improvements
