"""Idea Review Generator for Worker10 quality assurance.

This module generates comprehensive reviews of ideas created using the
Idea.Creation module, analyzing:
- Gaps: Missing or weak content areas
- Pros: Strong points of each variant
- Cons: Areas needing improvement
- Differences across variants: How variants differ from each other
- Similarity/compatibility with original text: How well variants align with input
"""

import sys
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import re

# Add parent directories to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
idea_creation_src = os.path.join(current_dir, '../../Idea/Creation/src')
sys.path.insert(0, idea_creation_src)

from idea_variants import (
    create_ideas_from_input,
    format_idea_as_text,
    VARIANT_TEMPLATES,
    DEFAULT_IDEA_COUNT,
)


@dataclass
class IdeaVariantAnalysis:
    """Analysis of a single idea variant.
    
    Attributes:
        variant_index: Index of the variant (0-based)
        variant_type: Type of variant template used
        variant_name: Human-readable name of the variant
        pros: List of strengths/positive aspects
        cons: List of weaknesses/areas for improvement
        gaps: List of missing or incomplete content areas
        similarity_score: Score (0-100) for similarity to original input
        key_themes: Main themes identified in the variant
        unique_elements: Elements that distinguish this variant from others
    """
    variant_index: int
    variant_type: str
    variant_name: str
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    similarity_score: int = 0
    key_themes: List[str] = field(default_factory=list)
    unique_elements: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "variant_index": self.variant_index,
            "variant_type": self.variant_type,
            "variant_name": self.variant_name,
            "pros": self.pros,
            "cons": self.cons,
            "gaps": self.gaps,
            "similarity_score": self.similarity_score,
            "key_themes": self.key_themes,
            "unique_elements": self.unique_elements,
        }


@dataclass
class IdeaReviewResult:
    """Complete review result for generated ideas.
    
    Attributes:
        original_input: The original text input used for generation
        input_type: Type of input (keyword, phrase, longer text)
        generated_at: Timestamp of generation
        total_variants: Number of variants generated
        variant_analyses: Individual analysis for each variant
        cross_variant_differences: Key differences between variants
        overall_gaps: Gaps common across all variants
        overall_strengths: Strengths common across all variants
        compatibility_summary: Summary of how well variants match original input
        recommendations: Suggestions for improvement or next steps
        average_similarity_score: Average similarity score across all variants
    """
    original_input: str
    input_type: str
    generated_at: datetime = field(default_factory=datetime.now)
    total_variants: int = 0
    variant_analyses: List[IdeaVariantAnalysis] = field(default_factory=list)
    cross_variant_differences: List[str] = field(default_factory=list)
    overall_gaps: List[str] = field(default_factory=list)
    overall_strengths: List[str] = field(default_factory=list)
    compatibility_summary: str = ""
    recommendations: List[str] = field(default_factory=list)
    average_similarity_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "original_input": self.original_input,
            "input_type": self.input_type,
            "generated_at": self.generated_at.isoformat(),
            "total_variants": self.total_variants,
            "variant_analyses": [va.to_dict() for va in self.variant_analyses],
            "cross_variant_differences": self.cross_variant_differences,
            "overall_gaps": self.overall_gaps,
            "overall_strengths": self.overall_strengths,
            "compatibility_summary": self.compatibility_summary,
            "recommendations": self.recommendations,
            "average_similarity_score": self.average_similarity_score,
        }
    
    def format_as_markdown(self) -> str:
        """Format the review as a markdown document."""
        lines = []
        
        # Header
        lines.append("# Idea Review Report")
        lines.append("")
        lines.append(f"**Original Input**: `{self.original_input}`")
        lines.append(f"**Input Type**: {self.input_type}")
        lines.append(f"**Generated At**: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total Variants**: {self.total_variants}")
        lines.append(f"**Average Similarity Score**: {self.average_similarity_score:.1f}%")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"{self.compatibility_summary}")
        lines.append("")
        
        # Overall Analysis
        lines.append("## Overall Analysis")
        lines.append("")
        
        lines.append("### Overall Strengths")
        for strength in self.overall_strengths:
            lines.append(f"- ✅ {strength}")
        lines.append("")
        
        lines.append("### Overall Gaps")
        for gap in self.overall_gaps:
            lines.append(f"- ⚠️ {gap}")
        lines.append("")
        
        # Cross-Variant Differences
        lines.append("## Differences Across Variants")
        lines.append("")
        for diff in self.cross_variant_differences:
            lines.append(f"- {diff}")
        lines.append("")
        
        # Individual Variant Analysis
        lines.append("## Individual Variant Analysis")
        lines.append("")
        
        for analysis in self.variant_analyses:
            lines.append(f"### Variant {analysis.variant_index + 1}: {analysis.variant_name}")
            lines.append(f"**Type**: `{analysis.variant_type}`")
            lines.append(f"**Similarity Score**: {analysis.similarity_score}%")
            lines.append("")
            
            if analysis.key_themes:
                lines.append("**Key Themes**: " + ", ".join(analysis.key_themes))
                lines.append("")
            
            if analysis.pros:
                lines.append("**Pros:**")
                for pro in analysis.pros:
                    lines.append(f"- ✅ {pro}")
                lines.append("")
            
            if analysis.cons:
                lines.append("**Cons:**")
                for con in analysis.cons:
                    lines.append(f"- ❌ {con}")
                lines.append("")
            
            if analysis.gaps:
                lines.append("**Gaps:**")
                for gap in analysis.gaps:
                    lines.append(f"- ⚠️ {gap}")
                lines.append("")
            
            if analysis.unique_elements:
                lines.append("**Unique Elements:**")
                for elem in analysis.unique_elements:
                    lines.append(f"- 🔹 {elem}")
                lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        for rec in self.recommendations:
            lines.append(f"- 💡 {rec}")
        lines.append("")
        
        return "\n".join(lines)


class IdeaReviewGenerator:
    """Generator for comprehensive idea reviews.
    
    Worker10's tool for analyzing ideas generated by Idea.Creation,
    producing structured reviews with gaps, pros, cons, and variant analysis.
    """
    
    # Input type thresholds
    KEYWORD_MAX_LENGTH = 30
    PHRASE_MAX_LENGTH = 100
    
    # Evaluation criteria
    CORE_FIELDS = ['hook', 'emotional_core', 'target_audience', 'premise']
    ENGAGEMENT_FIELDS = ['wow_moment', 'engagement_mechanic', 'visual_hook']
    STRUCTURE_FIELDS = ['opening_hook', 'rising_stakes', 'peak_moment', 'conclusion_shape']
    
    def __init__(self, num_ideas: int = DEFAULT_IDEA_COUNT):
        """Initialize the review generator.
        
        Args:
            num_ideas: Number of ideas to generate for review (default: 10)
        """
        self.num_ideas = num_ideas
    
    def generate_review(
        self,
        text_input: str,
        seed: Optional[int] = None,
        allow_duplicate_types: bool = True
    ) -> IdeaReviewResult:
        """Generate a comprehensive review of ideas from the input text.
        
        Args:
            text_input: The text input to generate ideas from
            seed: Optional seed for reproducible generation
            allow_duplicate_types: Whether to allow duplicate variant types
            
        Returns:
            IdeaReviewResult containing the complete review
        """
        if not text_input or not text_input.strip():
            raise ValueError("Input text cannot be empty")
        
        text_input = text_input.strip()
        
        # Determine input type
        input_type = self._classify_input(text_input)
        
        # Generate ideas using template-based generation
        ideas = create_ideas_from_input(
            text_input=text_input,
            count=self.num_ideas,
            seed=seed,
            allow_duplicate_types=allow_duplicate_types
        )
        
        # Analyze each variant
        variant_analyses = []
        for i, idea in enumerate(ideas):
            analysis = self._analyze_variant(idea, text_input, i)
            variant_analyses.append(analysis)
        
        # Calculate cross-variant analysis
        cross_differences = self._analyze_cross_variant_differences(ideas, variant_analyses)
        overall_gaps = self._identify_overall_gaps(variant_analyses)
        overall_strengths = self._identify_overall_strengths(variant_analyses)
        
        # Calculate average similarity score
        avg_similarity = sum(va.similarity_score for va in variant_analyses) / len(variant_analyses) if variant_analyses else 0
        
        # Generate compatibility summary
        compatibility_summary = self._generate_compatibility_summary(
            text_input, input_type, variant_analyses, avg_similarity
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            variant_analyses, overall_gaps, avg_similarity
        )
        
        return IdeaReviewResult(
            original_input=text_input,
            input_type=input_type,
            total_variants=len(ideas),
            variant_analyses=variant_analyses,
            cross_variant_differences=cross_differences,
            overall_gaps=overall_gaps,
            overall_strengths=overall_strengths,
            compatibility_summary=compatibility_summary,
            recommendations=recommendations,
            average_similarity_score=avg_similarity
        )
    
    def _classify_input(self, text: str) -> str:
        """Classify the input text type.
        
        Args:
            text: Input text to classify
            
        Returns:
            Classification string (keyword, phrase, or longer text)
        """
        length = len(text)
        word_count = len(text.split())
        
        if length <= self.KEYWORD_MAX_LENGTH and word_count <= 3:
            return "keyword"
        elif length <= self.PHRASE_MAX_LENGTH and word_count <= 15:
            return "phrase"
        else:
            return "longer text"
    
    def _analyze_variant(
        self,
        variant: Dict[str, Any],
        original_input: str,
        index: int
    ) -> IdeaVariantAnalysis:
        """Analyze a single variant.
        
        Args:
            variant: The variant dictionary to analyze
            original_input: The original input text
            index: Index of this variant
            
        Returns:
            IdeaVariantAnalysis for this variant
        """
        variant_type = variant.get('variant_type', 'unknown')
        variant_name = variant.get('variant_name', 'Unknown Variant')
        
        # Calculate similarity score
        similarity_score = self._calculate_similarity(variant, original_input)
        
        # Identify pros
        pros = self._identify_pros(variant)
        
        # Identify cons
        cons = self._identify_cons(variant)
        
        # Identify gaps
        gaps = self._identify_gaps(variant)
        
        # Extract key themes
        key_themes = self._extract_themes(variant)
        
        # Identify unique elements for this variant type
        unique_elements = self._identify_unique_elements(variant)
        
        return IdeaVariantAnalysis(
            variant_index=index,
            variant_type=variant_type,
            variant_name=variant_name,
            pros=pros,
            cons=cons,
            gaps=gaps,
            similarity_score=similarity_score,
            key_themes=key_themes,
            unique_elements=unique_elements
        )
    
    def _calculate_similarity(self, variant: Dict[str, Any], original_input: str) -> int:
        """Calculate similarity score between variant and original input.
        
        Args:
            variant: The variant to analyze
            original_input: Original input text
            
        Returns:
            Similarity score (0-100)
        """
        original_lower = original_input.lower()
        original_words = set(re.findall(r'\b\w+\b', original_lower))
        
        # Get all text content from variant
        variant_text = self._extract_variant_text(variant).lower()
        variant_words = set(re.findall(r'\b\w+\b', variant_text))
        
        # Calculate word overlap (Jaccard similarity)
        if not original_words:
            return 50  # Default score for empty input
        
        intersection = original_words & variant_words
        union = original_words | variant_words
        
        if not union:
            return 50
        
        word_similarity = len(intersection) / len(original_words) * 100
        
        # Check for exact phrase match (bonus)
        phrase_bonus = 0
        if original_lower in variant_text:
            phrase_bonus = 20
        
        # Check for partial matches
        partial_match = 0
        for word in original_words:
            if word in variant_text and len(word) > 3:
                partial_match += 5
        
        total_score = min(100, int(word_similarity * 0.6 + phrase_bonus + partial_match * 0.2))
        return max(0, min(100, total_score))
    
    def _extract_variant_text(self, variant: Dict[str, Any]) -> str:
        """Extract all text content from a variant.
        
        Args:
            variant: The variant dictionary
            
        Returns:
            Combined text content
        """
        texts = []
        
        # Common text fields to check
        text_fields = [
            'source_title', 'source_description', 'hook', 'hook_line', 'hook_essence',
            'premise', 'concept', 'core_hook', 'central_mystery', 'emotional_hook',
            'opening_hook', 'context_setup', 'rising_stakes', 'peak_moment',
            'wow_moment', 'voice_hook', 'scene_hook', 'emotional_premise',
            'supernatural_element', 'tech_concept', 'challenge_scenario',
            'discovery', 'collision_point', 'digital_trigger'
        ]
        
        for field in text_fields:
            value = variant.get(field)
            if isinstance(value, str):
                texts.append(value)
            elif isinstance(value, dict):
                for sub_value in value.values():
                    if isinstance(sub_value, str):
                        texts.append(sub_value)
        
        return ' '.join(texts)
    
    def _identify_pros(self, variant: Dict[str, Any]) -> List[str]:
        """Identify strengths of a variant.
        
        Args:
            variant: The variant to analyze
            
        Returns:
            List of identified pros
        """
        pros = []
        variant_type = variant.get('variant_type', '')
        
        # Check for core content presence
        if variant.get('core_hook') or variant.get('hook') or variant.get('hook_line'):
            pros.append("Has a clear hook that captures attention")
        
        if variant.get('emotional_hook') or variant.get('emotional_core') or variant.get('main_emotion'):
            pros.append("Strong emotional appeal")
        
        if variant.get('target_audience'):
            pros.append("Well-defined target audience")
        
        if variant.get('visual_hook') or variant.get('first_frame_concept'):
            pros.append("Visual hook present for engagement")
        
        if variant.get('wow_moment') or variant.get('peak_moment') or variant.get('turning_point'):
            pros.append("Clear climax/wow moment defined")
        
        if variant.get('engagement_mechanic'):
            pros.append("Built-in engagement mechanism")
        
        # Type-specific pros
        if variant_type in ['emotional_drama', 'identity_power', 'personal_voice']:
            if variant.get('character_challenge') or variant.get('identity_struggle'):
                pros.append("Strong character-driven narrative")
        
        if variant_type in ['mystery', 'light_mystery', 'realistic_mystery']:
            if variant.get('central_mystery') or variant.get('central_puzzle'):
                pros.append("Engaging mystery element")
        
        if variant_type in ['shortform', 'shortform2']:
            pros.append("Optimized for mobile/short-form platforms")
        
        if variant.get('resolution_direction') or variant.get('payoff'):
            pros.append("Clear resolution/payoff planned")
        
        return pros[:5]  # Limit to top 5 pros
    
    def _identify_cons(self, variant: Dict[str, Any]) -> List[str]:
        """Identify weaknesses of a variant.
        
        Args:
            variant: The variant to analyze
            
        Returns:
            List of identified cons
        """
        cons = []
        variant_type = variant.get('variant_type', '')
        
        # Check for missing critical elements
        if not variant.get('target_audience') and 'target_audience' not in str(variant):
            cons.append("Target audience not explicitly defined")
        
        source_title = variant.get('source_title', '')
        source_desc = variant.get('source_description', '')
        
        # Check hook quality
        hook_fields = ['hook', 'core_hook', 'hook_line', 'hook_essence', 'opening_hook']
        hook_present = any(variant.get(f) for f in hook_fields)
        if not hook_present:
            cons.append("Missing a clear hook")
        
        # Check for overly generic content
        generic_phrases = ['everything changes', 'nobody expected', 'you won\'t believe']
        variant_text = self._extract_variant_text(variant).lower()
        for phrase in generic_phrases:
            if phrase in variant_text:
                cons.append(f"Contains potentially generic phrase: '{phrase}'")
                break
        
        # Type-specific cons
        if variant_type in ['skeleton', 'scene_seed']:
            if not variant.get('context_setup') and not variant.get('scene_hook'):
                cons.append("May need more context/setup")
        
        if variant_type == 'minimal':
            cons.append("Minimal structure may need expansion for production")
        
        if variant_type in ['niche_blend']:
            cons.append("Multiple niche blend may risk confusing the audience")
        
        return cons[:4]  # Limit to top 4 cons
    
    def _identify_gaps(self, variant: Dict[str, Any]) -> List[str]:
        """Identify gaps or missing content in a variant.
        
        Args:
            variant: The variant to analyze
            
        Returns:
            List of identified gaps
        """
        gaps = []
        variant_type = variant.get('variant_type', '')
        
        # Check for empty or missing common fields
        if not variant.get('source_description'):
            gaps.append("No expanded description provided")
        
        # Check engagement elements
        if not variant.get('engagement_mechanic') and not variant.get('engagement_element'):
            gaps.append("No explicit engagement mechanism defined")
        
        # Check for platform-specific content
        if not variant.get('platform') and not variant.get('audience_segment'):
            gaps.append("Platform targeting not specified")
        
        # Check safety/moderation elements
        if not variant.get('safety_checklist') and not variant.get('sensitivities'):
            gaps.append("Content safety guidelines not addressed")
        
        # Type-specific gap analysis
        if variant_type in ['emotional_drama', 'identity_power']:
            if not variant.get('growth_arc') and not variant.get('character_journey'):
                gaps.append("Character growth arc not defined")
        
        if variant_type in ['mystery', 'light_mystery']:
            if not variant.get('resolution_style') and not variant.get('revelation_type'):
                gaps.append("Mystery resolution approach not specified")
        
        if variant_type in ['skeleton', 'scene_seed']:
            if not variant.get('conclusion_shape') and not variant.get('target_script_length'):
                gaps.append("Story conclusion/length not defined")
        
        return gaps[:4]  # Limit to top 4 gaps
    
    def _extract_themes(self, variant: Dict[str, Any]) -> List[str]:
        """Extract key themes from a variant.
        
        Args:
            variant: The variant to analyze
            
        Returns:
            List of key themes
        """
        themes = []
        variant_type = variant.get('variant_type', '')
        
        # Type-based theme identification
        type_themes = {
            'emotion_first': ['emotion', 'feeling'],
            'mystery': ['mystery', 'curiosity', 'suspense'],
            'skeleton': ['narrative', 'story structure'],
            'shortform': ['viral', 'mobile-first'],
            'niche_blend': ['multi-genre', 'creative fusion'],
            'soft_supernatural': ['supernatural', 'friendship', 'wonder'],
            'light_mystery': ['puzzle', 'adventure'],
            'scifi_school': ['technology', 'social dynamics'],
            'safe_survival': ['teamwork', 'resilience'],
            'emotional_drama': ['emotion', 'character growth'],
            'rivals_allies': ['competition', 'collaboration'],
            'identity_power': ['identity', 'empowerment'],
            'ai_companion': ['AI', 'connection'],
            'urban_quest': ['urban', 'adventure', 'community'],
            'magical_aesthetic': ['magic', 'aesthetics', 'wonder'],
            'family_drama': ['family', 'relationships'],
            'social_home': ['social media', 'family dynamics'],
            'realistic_mystery': ['mystery', 'family secrets'],
            'school_family': ['school', 'family'],
            'personal_voice': ['identity', 'personal expression'],
        }
        
        if variant_type in type_themes:
            themes.extend(type_themes[variant_type])
        
        # Extract from content
        if variant.get('main_emotion'):
            themes.append(variant['main_emotion'])
        
        if variant.get('emotional_core'):
            themes.append('emotional depth')
        
        if variant.get('moral_question') or variant.get('ethical_note'):
            themes.append('moral/ethical themes')
        
        return list(set(themes))[:5]
    
    def _identify_unique_elements(self, variant: Dict[str, Any]) -> List[str]:
        """Identify unique elements specific to this variant.
        
        Args:
            variant: The variant to analyze
            
        Returns:
            List of unique elements
        """
        unique = []
        variant_type = variant.get('variant_type', '')
        
        # Type-specific unique elements
        if variant_type == 'soft_supernatural':
            if variant.get('supernatural_element'):
                unique.append(f"Supernatural element: {variant['supernatural_element'][:50]}...")
        
        if variant_type == 'scifi_school':
            if variant.get('tech_concept'):
                unique.append(f"Tech concept: {variant['tech_concept'][:50]}...")
        
        if variant_type == 'mystery' or variant_type == 'light_mystery':
            if variant.get('central_mystery') or variant.get('central_puzzle'):
                mystery = variant.get('central_mystery') or variant.get('central_puzzle')
                unique.append(f"Central mystery: {mystery[:50]}...")
        
        if variant_type in ['emotion_first', 'emotional_drama']:
            if variant.get('main_emotion') or variant.get('emotional_premise'):
                emotion = variant.get('main_emotion') or variant.get('emotional_premise', '')[:30]
                unique.append(f"Emotional driver: {emotion}")
        
        if variant.get('hook_essence'):
            unique.append(f"Hook: {variant['hook_essence'][:40]}...")
        elif variant.get('core_hook'):
            unique.append(f"Hook: {variant['core_hook'][:40]}...")
        elif variant.get('hook_line'):
            unique.append(f"Hook: {variant['hook_line'][:40]}...")
        
        return unique[:3]
    
    def _analyze_cross_variant_differences(
        self,
        variants: List[Dict[str, Any]],
        analyses: List[IdeaVariantAnalysis]
    ) -> List[str]:
        """Analyze key differences across all variants.
        
        Args:
            variants: List of all variants
            analyses: List of variant analyses
            
        Returns:
            List of key differences
        """
        differences = []
        
        # Group by variant type
        type_counts: Dict[str, int] = {}
        for v in variants:
            vtype = v.get('variant_type', 'unknown')
            type_counts[vtype] = type_counts.get(vtype, 0) + 1
        
        # Note variant type distribution
        unique_types = len(type_counts)
        if unique_types == len(variants):
            differences.append(f"All {len(variants)} variants use different template types (maximum diversity)")
        elif unique_types == 1:
            differences.append(f"All variants use the same template type: {list(type_counts.keys())[0]}")
        else:
            most_common = max(type_counts.items(), key=lambda x: x[1])
            differences.append(f"Template distribution: {unique_types} unique types, most common: {most_common[0]} ({most_common[1]}x)")
        
        # Compare similarity scores
        scores = [a.similarity_score for a in analyses]
        if scores:
            min_score, max_score = min(scores), max(scores)
            score_range = max_score - min_score
            if score_range > 30:
                differences.append(f"Large similarity score variance ({min_score}%-{max_score}%): some variants align better with input than others")
            elif score_range < 10:
                differences.append(f"Consistent similarity scores ({min_score}%-{max_score}%): variants equally aligned with input")
        
        # Compare structural approaches
        has_emotion_focus = any(v.get('variant_type', '').startswith('emotion') for v in variants)
        has_mystery_focus = any('mystery' in v.get('variant_type', '') for v in variants)
        has_short_form = any('shortform' in v.get('variant_type', '') for v in variants)
        
        approaches = []
        if has_emotion_focus:
            approaches.append("emotion-driven")
        if has_mystery_focus:
            approaches.append("mystery/puzzle")
        if has_short_form:
            approaches.append("short-form/viral")
        
        if len(approaches) > 1:
            differences.append(f"Multiple narrative approaches present: {', '.join(approaches)}")
        
        # Compare audience targeting
        audiences = set()
        for v in variants:
            if isinstance(v.get('target_audience'), dict):
                audiences.add('segmented audience')
            elif isinstance(v.get('target_audience'), str):
                audiences.add(v['target_audience'])
        
        if len(audiences) > 1:
            differences.append(f"Diverse audience targeting across variants")
        
        return differences[:5]
    
    def _identify_overall_gaps(
        self,
        analyses: List[IdeaVariantAnalysis]
    ) -> List[str]:
        """Identify gaps common across all variants.
        
        Args:
            analyses: List of variant analyses
            
        Returns:
            List of common gaps
        """
        if not analyses:
            return []
        
        # Count gap occurrences
        gap_counts: Dict[str, int] = {}
        for analysis in analyses:
            for gap in analysis.gaps:
                gap_counts[gap] = gap_counts.get(gap, 0) + 1
        
        # Find gaps present in majority of variants
        threshold = len(analyses) // 2
        common_gaps = [
            gap for gap, count in gap_counts.items()
            if count >= threshold
        ]
        
        return common_gaps[:4]
    
    def _identify_overall_strengths(
        self,
        analyses: List[IdeaVariantAnalysis]
    ) -> List[str]:
        """Identify strengths common across all variants.
        
        Args:
            analyses: List of variant analyses
            
        Returns:
            List of common strengths
        """
        if not analyses:
            return []
        
        # Count pro occurrences
        pro_counts: Dict[str, int] = {}
        for analysis in analyses:
            for pro in analysis.pros:
                pro_counts[pro] = pro_counts.get(pro, 0) + 1
        
        # Find pros present in majority of variants
        threshold = len(analyses) // 2
        common_pros = [
            pro for pro, count in pro_counts.items()
            if count >= threshold
        ]
        
        return common_pros[:4]
    
    def _generate_compatibility_summary(
        self,
        original_input: str,
        input_type: str,
        analyses: List[IdeaVariantAnalysis],
        avg_similarity: float
    ) -> str:
        """Generate a summary of how well variants match the original input.
        
        Args:
            original_input: The original input text
            input_type: Type of input (keyword, phrase, longer text)
            analyses: List of variant analyses
            avg_similarity: Average similarity score
            
        Returns:
            Summary text
        """
        parts = []
        
        # Input type assessment
        if input_type == "keyword":
            parts.append(f"The input '{original_input}' was treated as a keyword seed.")
        elif input_type == "phrase":
            parts.append(f"The input was interpreted as a phrase with multiple concept elements.")
        else:
            parts.append(f"The input was processed as longer text, preserving more context and nuance.")
        
        # Similarity assessment
        if avg_similarity >= 80:
            parts.append(f"Variants show excellent alignment with the original input (avg {avg_similarity:.0f}% similarity).")
        elif avg_similarity >= 60:
            parts.append(f"Variants show good alignment with creative interpretation (avg {avg_similarity:.0f}% similarity).")
        elif avg_similarity >= 40:
            parts.append(f"Variants take significant creative liberty from the input (avg {avg_similarity:.0f}% similarity).")
        else:
            parts.append(f"Variants have diverged significantly from the original input (avg {avg_similarity:.0f}% similarity).")
        
        # Best performing variant
        if analyses:
            best_variant = max(analyses, key=lambda a: a.similarity_score)
            parts.append(f"Best aligned variant: {best_variant.variant_name} ({best_variant.similarity_score}% similarity).")
        
        return " ".join(parts)
    
    def _generate_recommendations(
        self,
        analyses: List[IdeaVariantAnalysis],
        overall_gaps: List[str],
        avg_similarity: float
    ) -> List[str]:
        """Generate recommendations based on the review.
        
        Args:
            analyses: List of variant analyses
            overall_gaps: Common gaps identified
            avg_similarity: Average similarity score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Similarity-based recommendations
        if avg_similarity < 50:
            recommendations.append("Consider providing more specific input or keywords to improve variant alignment")
        
        # Gap-based recommendations
        if "No explicit engagement mechanism defined" in overall_gaps:
            recommendations.append("Add engagement hooks (questions, calls-to-action) to variants before production")
        
        if "Content safety guidelines not addressed" in overall_gaps:
            recommendations.append("Review variants for content safety before publishing")
        
        # Type diversity recommendations
        variant_types = [a.variant_type for a in analyses]
        emotion_count = sum(1 for t in variant_types if 'emotion' in t or 'drama' in t)
        mystery_count = sum(1 for t in variant_types if 'mystery' in t)
        
        if emotion_count == 0 and mystery_count == 0:
            recommendations.append("Consider adding emotion-focused or mystery variants for audience engagement")
        
        # Best variant recommendation
        if analyses:
            best_by_pros = max(analyses, key=lambda a: len(a.pros))
            recommendations.append(f"Strongest variant by features: {best_by_pros.variant_name} - consider prioritizing for development")
        
        # General recommendations
        recommendations.append("Test top variants with target audience before full production")
        
        return recommendations[:5]


def generate_idea_review(
    text_input: str,
    num_ideas: int = DEFAULT_IDEA_COUNT,
    seed: Optional[int] = None
) -> IdeaReviewResult:
    """Convenience function to generate an idea review.
    
    Args:
        text_input: Text input to generate ideas from
        num_ideas: Number of ideas to generate
        seed: Optional seed for reproducibility
        
    Returns:
        IdeaReviewResult with complete review
    """
    generator = IdeaReviewGenerator(num_ideas=num_ideas)
    return generator.generate_review(text_input, seed=seed)


__all__ = [
    "IdeaReviewGenerator",
    "IdeaReviewResult",
    "IdeaVariantAnalysis",
    "generate_idea_review",
]
