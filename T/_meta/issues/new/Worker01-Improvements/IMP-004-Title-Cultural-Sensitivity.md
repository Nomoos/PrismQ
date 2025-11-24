# IMP-004: Cultural Sensitivity and Localization Check

**Type**: Improvement - Title Generation  
**Worker**: Worker12 (Content Specialist)  
**Priority**: Medium  
**Effort**: 1.5 days  
**Module**: `PrismQ.T.Title` (all submodules)  
**Category**: Title Generation  
**Status**: 🎯 PLANNED

---

## Description

Implement cultural sensitivity and localization checking system for titles to ensure content is appropriate across different cultures, regions, and demographics. This system will detect potentially offensive language, cultural insensitivity, idioms that don't translate well, and provide localization recommendations.

In a global content marketplace, culturally inappropriate titles can damage brand reputation and limit content reach. This enhancement provides automated cultural screening and localization guidance.

---

## Business Justification

- Prevents cultural missteps that could damage brand reputation
- Enables safer global content distribution
- Identifies localization opportunities for international markets
- Reduces manual cultural review overhead
- Increases content accessibility across diverse audiences

---

## Acceptance Criteria

- [ ] Detect culturally sensitive terms and phrases
- [ ] Identify idioms and expressions that may not translate
- [ ] Flag potentially offensive language by region
- [ ] Check for religious/political sensitivity
- [ ] Validate color/number symbolism appropriateness
- [ ] Suggest culturally appropriate alternatives
- [ ] Support multi-region cultural screening
- [ ] Provide localization difficulty score
- [ ] Integration with title acceptance gate (warning system)
- [ ] Cultural appropriateness documentation

---

## Cultural Sensitivity Categories

### High-Risk Areas
1. **Religious References**: Terms, symbols, sacred concepts
2. **Political Terms**: Controversial topics, regime references
3. **Ethnic/Racial Terms**: Potentially offensive descriptors
4. **Gender Language**: Stereotypes, insensitive phrasing
5. **Body/Appearance**: Sensitivity varies by culture
6. **Historical Events**: Traumatic history references

### Medium-Risk Areas
7. **Idioms/Slang**: Culture-specific expressions
8. **Humor**: Different humor sensibilities
9. **Colors**: Symbolic meanings vary (white = death in some cultures)
10. **Numbers**: Lucky/unlucky meanings (4 in Asia, 13 in West)
11. **Animals**: Different symbolism (pig, cow, etc.)
12. **Food References**: Dietary restrictions, taboos

### Localization Considerations
13. **Name References**: Celebrity names may be unknown
14. **Currency/Units**: USD, metric vs. imperial
15. **Date Formats**: MM/DD vs. DD/MM
16. **Cultural Events**: Holidays, seasons vary

---

## Input/Output

**Input**:
- Title text
- Target regions/cultures (list)
- Content category
- Sensitivity level (strict, moderate, permissive)

**Output**:
```python
{
    "title": "Black Friday: The Ultimate Shopping Guide",
    "overall_sensitivity": "medium-risk",
    "regions_analyzed": ["US", "UK", "EU", "ASIA", "MENA"],
    "flags": [
        {
            "issue": "Color reference 'Black'",
            "category": "cultural_symbolism",
            "severity": "low",
            "regions_affected": ["ASIA"],
            "explanation": "Black associated with mourning in some Asian cultures",
            "recommendation": "Consider 'Big Sale Friday' for Asian markets"
        },
        {
            "issue": "Western holiday reference",
            "category": "localization",
            "severity": "medium",
            "regions_affected": ["ASIA", "MENA"],
            "explanation": "Black Friday not widely celebrated outside Western markets",
            "recommendation": "Use 'End of Year Sale' or regional equivalent"
        }
    ],
    "localization_difficulty": 65,
    "recommendations": {
        "global_safe_alternative": "The Ultimate Shopping Guide",
        "regional_variants": {
            "ASIA": "Big Sale: Complete Shopping Guide",
            "MENA": "Great Deals: Shopping Guide 2024",
            "US": "Black Friday: The Ultimate Shopping Guide"  # original
        }
    },
    "approved_regions": ["US", "UK", "EU"],
    "review_recommended": ["ASIA", "MENA"]
}
```

---

## Dependencies

- **MVP-002**: T.Title.FromIdea
- **MVP-012**: Title Acceptance (integration point)
- Cultural sensitivity database/API
- Translation API (optional, for localization suggestions)

---

## Technical Notes

### Implementation Approach

1. **Cultural Database** (`T/Title/culture/cultural_database.py`):
```python
SENSITIVE_TERMS = {
    "religious": {
        "high_risk": ["jihad", "crusade", "holocaust"],
        "medium_risk": ["bible", "quran", "karma"],
        "regions": {
            "MENA": ["specific terms..."],
            "ASIA": ["specific terms..."]
        }
    },
    "political": {
        "high_risk": ["regime", "dictator", "propaganda"],
        "regions": {
            "CHINA": ["specific terms..."],
            "RUSSIA": ["specific terms..."]
        }
    },
    # ... more categories
}

CULTURAL_SYMBOLISM = {
    "colors": {
        "white": {
            "US": "purity, weddings",
            "ASIA": "mourning, death",
            "risk_level": "medium"
        },
        "red": {
            "US": "danger, passion",
            "ASIA": "luck, prosperity",
            "risk_level": "low"
        }
    },
    "numbers": {
        "4": {"ASIA": "death", "risk_level": "high"},
        "13": {"US": "unlucky", "risk_level": "medium"}
    }
}

IDIOMS_DATABASE = {
    "kick the bucket": {
        "meaning": "die",
        "translatable": False,
        "alternatives": ["pass away", "die"]
    },
    "raining cats and dogs": {
        "meaning": "heavy rain",
        "translatable": False,
        "alternatives": ["pouring rain", "heavy rainfall"]
    }
}
```

2. **Cultural Analyzer** (`T/Title/culture/cultural_analyzer.py`):
```python
class CulturalAnalyzer:
    def analyze_cultural_sensitivity(
        self,
        title: str,
        regions: List[str],
        sensitivity_level: str = "moderate"
    ) -> CulturalAnalysisResult:
        """Analyze title for cultural sensitivity."""
        
        flags = []
        
        # Check sensitive terms
        flags.extend(self._check_sensitive_terms(title, regions))
        
        # Check idioms
        flags.extend(self._check_idioms(title))
        
        # Check cultural symbolism
        flags.extend(self._check_symbolism(title, regions))
        
        # Calculate overall risk
        risk_level = self._calculate_risk_level(flags)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            title, flags, regions
        )
        
        return CulturalAnalysisResult(
            title=title,
            risk_level=risk_level,
            flags=flags,
            recommendations=recommendations
        )
```

3. **Localization Suggester** (`T/Title/culture/localization_suggester.py`):
```python
class LocalizationSuggester:
    def suggest_regional_variants(
        self,
        title: str,
        regions: List[str]
    ) -> Dict[str, str]:
        """Suggest culturally appropriate variants."""
        
        variants = {}
        
        for region in regions:
            # Analyze what needs localization
            issues = self._identify_localization_needs(title, region)
            
            if not issues:
                variants[region] = title  # Safe as-is
            else:
                # Generate appropriate variant
                variant = self._generate_regional_variant(title, region, issues)
                variants[region] = variant
        
        return variants
```

### Files to Create

**New Files**:
- `T/Title/culture/cultural_database.py` - Cultural sensitivity data
- `T/Title/culture/cultural_analyzer.py` - Analysis logic
- `T/Title/culture/localization_suggester.py` - Localization suggestions
- `T/_meta/data/cultural_terms.json` - Cultural terms database
- `T/_meta/data/regional_idioms.json` - Idioms database

**Modified Files**:
- `T/Review/Title/Acceptance/acceptance.py` - Add cultural check (warning)
- `T/Title/FromIdea/src/title_generator.py` - Optional cultural filtering

### Testing Requirements

- [ ] Sensitive term detection tests (high coverage)
- [ ] Idiom identification tests
- [ ] Cultural symbolism recognition tests
- [ ] Regional variant generation tests
- [ ] False positive rate tests (<5%)
- [ ] Multi-region analysis tests
- [ ] Edge cases: mixed language titles, slang

---

## Success Metrics

- Cultural sensitivity detection accuracy >90%
- False positive rate <5%
- Localization suggestions approved by human reviewers >80%
- Prevents 100% of high-risk cultural issues from publication
- Regional variant generation time <1 second per region
- User satisfaction with cultural recommendations >85%

---

## Related Issues

- IMP-001: Platform Optimization (cultural norms vary by platform)
- IMP-002: Emotional Scoring (emotional appropriateness varies by culture)
- IMP-005: Title Strategies (cultural strategies for generation)

---

## Notes

- **Privacy**: No personally identifiable information stored
- **Bias Mitigation**: Regular review of flagged terms to avoid over-censorship
- **Human Review**: System provides warnings, not hard blocks
- **Continuous Learning**: Database updated based on feedback

---

**Created**: 2025-11-24  
**Owner**: Worker12 (Content Specialist)  
**Category**: Title Generation Improvements
