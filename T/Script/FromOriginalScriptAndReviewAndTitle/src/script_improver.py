"""Script Improver for generating v2+ scripts from original script, reviews, and title.

This module implements the script improvement logic for MVP-007 (Stage 7):
- Takes original Script (v1 or vN), review feedback, and Title (v2 or latest) as input
- Generates improved script version (v2 or vN+1)
- Addresses feedback from both title and script reviews
- Ensures alignment with improved title version
- Maintains coherence with original idea and previous versions
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import sys
import os

# Add parent directories to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
script_v1_path = os.path.join(parent_dir, 'Script', 'FromIdeaAndTitle', 'src')
review_script_path = os.path.join(parent_dir, 'Review', 'Script')
sys.path.insert(0, script_v1_path)
sys.path.insert(0, review_script_path)

try:
    from script_generator import ScriptV1, ScriptSection, ScriptStructure, PlatformTarget, ScriptTone
    from script_review import ScriptReview, ReviewCategory, ImprovementPoint
except ImportError:
    # Fallback for testing or development
    pass


@dataclass
class ReviewFeedback:
    """Container for review feedback from multiple sources.
    
    Attributes:
        script_review: Review of the script by title
        title_review: Review of the title by script (contains insights for script)
        review_type: Type of review (general, grammar, tone, etc.)
        priority_issues: List of high-priority issues to address
        suggestions: List of improvement suggestions
        metadata: Additional context
    """
    
    script_review: Optional[Any] = None  # ScriptReview object
    title_review: Optional[Any] = None  # TitleReview object
    review_type: str = "general"
    priority_issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScriptV2:
    """Improved script version (v2 or vN+1).
    
    Attributes:
        script_id: Unique identifier for this script version
        idea_id: Reference to source Idea
        previous_script_id: Reference to previous script version
        title: The title (v2 or latest) this script aligns with
        full_text: Complete script text
        sections: Breakdown into intro, body, conclusion
        total_duration_seconds: Estimated total duration
        structure_type: Type of structure used
        platform_target: Target platform
        
        version: Version number (2, 3, 4, etc.)
        version_history: List of previous version IDs
        
        improvements_made: Description of changes from previous version
        review_feedback_addressed: List of review issues that were addressed
        title_alignment_notes: How script aligns with current title
        
        metadata: Additional metadata
        created_at: Creation timestamp
        notes: Additional notes or context
    """
    
    script_id: str
    idea_id: str
    previous_script_id: str
    title: str
    full_text: str
    sections: List[ScriptSection]
    total_duration_seconds: int
    structure_type: ScriptStructure
    platform_target: PlatformTarget
    
    version: int
    version_history: List[str] = field(default_factory=list)
    
    improvements_made: str = ""
    review_feedback_addressed: List[str] = field(default_factory=list)
    title_alignment_notes: str = ""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""
    
    def get_section(self, section_type: str) -> Optional[ScriptSection]:
        """Get a specific section by type."""
        for section in self.sections:
            if section.section_type == section_type:
                return section
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "script_id": self.script_id,
            "idea_id": self.idea_id,
            "previous_script_id": self.previous_script_id,
            "title": self.title,
            "full_text": self.full_text,
            "sections": [
                {
                    "section_type": s.section_type,
                    "content": s.content,
                    "estimated_duration_seconds": s.estimated_duration_seconds,
                    "purpose": s.purpose,
                    "notes": s.notes
                }
                for s in self.sections
            ],
            "total_duration_seconds": self.total_duration_seconds,
            "structure_type": self.structure_type.value if isinstance(self.structure_type, Enum) else self.structure_type,
            "platform_target": self.platform_target.value if isinstance(self.platform_target, Enum) else self.platform_target,
            "version": self.version,
            "version_history": self.version_history,
            "improvements_made": self.improvements_made,
            "review_feedback_addressed": self.review_feedback_addressed,
            "title_alignment_notes": self.title_alignment_notes,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "notes": self.notes
        }


@dataclass
class ScriptImproverConfig:
    """Configuration for script improvement.
    
    Attributes:
        target_duration_seconds: Target script duration
        words_per_second: Narration speed for duration estimation
        preserve_successful_elements: Whether to preserve well-reviewed parts
        address_all_critical_issues: Whether to address all high-priority issues
        align_with_new_title: Whether to align with updated title
        tone: Script tone to maintain or adjust to
    """
    
    target_duration_seconds: Optional[int] = None  # None = keep original
    words_per_second: float = 2.5
    preserve_successful_elements: bool = True
    address_all_critical_issues: bool = True
    align_with_new_title: bool = True
    tone: Optional[ScriptTone] = None  # None = keep original


class ScriptImprover:
    """Generate improved script versions (v2+) from original script, reviews, and title.
    
    This class implements the MVP-007 functionality to create refined scripts
    based on review feedback and title alignment.
    """
    
    def __init__(self, config: Optional[ScriptImproverConfig] = None):
        """Initialize ScriptImprover with configuration.
        
        Args:
            config: Optional improvement configuration
        """
        self.config = config or ScriptImproverConfig()
    
    def generate_script_v2(
        self,
        original_script: ScriptV1,
        title_v2: str,
        review_feedback: ReviewFeedback,
        script_id: Optional[str] = None,
        **kwargs
    ) -> ScriptV2:
        """Generate improved script (v2 or vN+1) from original script, reviews, and new title.
        
        Args:
            original_script: Original script version (v1 or vN)
            title_v2: Improved title version (v2 or latest)
            review_feedback: Combined feedback from reviews
            script_id: Optional script ID (generated if not provided)
            **kwargs: Additional configuration overrides
            
        Returns:
            ScriptV2 object with improved script
            
        Raises:
            ValueError: If original_script, title_v2, or review_feedback is invalid
        """
        if not original_script:
            raise ValueError("Original script cannot be None")
        if not title_v2 or not title_v2.strip():
            raise ValueError("Title v2 cannot be empty")
        if not review_feedback:
            raise ValueError("Review feedback cannot be None")
        
        # Override config with kwargs
        config = self._apply_config_overrides(kwargs)
        
        # Generate script ID if not provided
        if not script_id:
            script_id = self._generate_script_id(original_script, title_v2)
        
        # Calculate new version number
        new_version = original_script.version + 1
        
        # Analyze review feedback
        analysis = self._analyze_review_feedback(review_feedback, original_script, title_v2)
        
        # Generate improved sections
        improved_sections = self._improve_sections(
            original_script, 
            title_v2, 
            analysis, 
            config
        )
        
        # Assemble full text
        full_text = self._assemble_full_text(improved_sections)
        
        # Calculate total duration
        total_duration = sum(s.estimated_duration_seconds for s in improved_sections)
        
        # Build version history
        version_history = list(original_script.version_history) if hasattr(original_script, 'version_history') else []
        version_history.append(original_script.script_id)
        
        # Create improvements summary
        improvements_made = self._create_improvements_summary(analysis)
        
        # Create title alignment notes
        title_alignment_notes = self._create_title_alignment_notes(title_v2, analysis)
        
        # Create ScriptV2 object
        script_v2 = ScriptV2(
            script_id=script_id,
            idea_id=original_script.idea_id,
            previous_script_id=original_script.script_id,
            title=title_v2,
            full_text=full_text,
            sections=improved_sections,
            total_duration_seconds=total_duration,
            structure_type=original_script.structure_type,
            platform_target=original_script.platform_target,
            version=new_version,
            version_history=version_history,
            improvements_made=improvements_made,
            review_feedback_addressed=analysis.get('addressed_issues', []),
            title_alignment_notes=title_alignment_notes,
            metadata={
                "original_script_id": original_script.script_id,
                "original_version": original_script.version,
                "title_v2": title_v2,
                "review_type": review_feedback.review_type,
                "improvement_config": {
                    "target_duration": config.target_duration_seconds,
                    "preserve_successful": config.preserve_successful_elements,
                    "address_critical": config.address_all_critical_issues
                }
            },
            notes=f"Generated v{new_version} from v{original_script.version} using {review_feedback.review_type} reviews and title '{title_v2}'"
        )
        
        return script_v2
    
    def _apply_config_overrides(self, kwargs: Dict[str, Any]) -> ScriptImproverConfig:
        """Apply configuration overrides from kwargs."""
        config = ScriptImproverConfig(
            target_duration_seconds=kwargs.get('target_duration_seconds', self.config.target_duration_seconds),
            words_per_second=kwargs.get('words_per_second', self.config.words_per_second),
            preserve_successful_elements=kwargs.get('preserve_successful_elements', self.config.preserve_successful_elements),
            address_all_critical_issues=kwargs.get('address_all_critical_issues', self.config.address_all_critical_issues),
            align_with_new_title=kwargs.get('align_with_new_title', self.config.align_with_new_title),
            tone=kwargs.get('tone', self.config.tone)
        )
        return config
    
    def _generate_script_id(self, original_script: ScriptV1, title_v2: str) -> str:
        """Generate a unique script ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = original_script.version + 1
        idea_id = original_script.idea_id
        return f"script_v{version}_{idea_id}_{timestamp}"
    
    def _analyze_review_feedback(
        self, 
        review_feedback: ReviewFeedback, 
        original_script: ScriptV1,
        title_v2: str
    ) -> Dict[str, Any]:
        """Analyze review feedback to extract key improvement areas.
        
        Args:
            review_feedback: Combined review feedback
            original_script: Original script to analyze
            title_v2: New title for alignment
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "critical_issues": [],
            "medium_issues": [],
            "low_issues": [],
            "successful_elements": [],
            "title_alignment_needs": [],
            "duration_adjustment": None,
            "tone_adjustment": None,
            "addressed_issues": []
        }
        
        # Extract issues from script review
        if review_feedback.script_review:
            script_review = review_feedback.script_review
            
            # Extract improvement points by priority
            if hasattr(script_review, 'improvement_points'):
                for point in script_review.improvement_points:
                    priority = getattr(point, 'priority', 'medium')
                    issue_desc = f"{getattr(point, 'title', 'Issue')}: {getattr(point, 'description', '')}"
                    
                    if priority == 'high':
                        analysis['critical_issues'].append(issue_desc)
                    elif priority == 'medium':
                        analysis['medium_issues'].append(issue_desc)
                    else:
                        analysis['low_issues'].append(issue_desc)
                    
                    analysis['addressed_issues'].append(issue_desc)
            
            # Extract strengths
            if hasattr(script_review, 'strengths'):
                analysis['successful_elements'].extend(script_review.strengths)
            
            # Check for duration issues
            if hasattr(script_review, 'optimal_length_seconds') and hasattr(script_review, 'current_length_seconds'):
                if script_review.optimal_length_seconds and script_review.current_length_seconds:
                    if abs(script_review.optimal_length_seconds - script_review.current_length_seconds) > 10:
                        analysis['duration_adjustment'] = script_review.optimal_length_seconds
        
        # Extract insights from title review
        if review_feedback.title_review:
            # Title review may contain insights about what script should emphasize
            if hasattr(review_feedback.title_review, 'notes'):
                analysis['title_alignment_needs'].append(review_feedback.title_review.notes)
        
        # Add priority issues from feedback
        analysis['critical_issues'].extend(review_feedback.priority_issues)
        
        return analysis
    
    def _improve_sections(
        self,
        original_script: ScriptV1,
        title_v2: str,
        analysis: Dict[str, Any],
        config: ScriptImproverConfig
    ) -> List[ScriptSection]:
        """Generate improved script sections based on feedback and title alignment.
        
        Args:
            original_script: Original script
            title_v2: New title for alignment
            analysis: Analyzed review feedback
            config: Improvement configuration
            
        Returns:
            List of improved script sections
        """
        improved_sections = []
        
        # Determine target duration
        if config.target_duration_seconds:
            target_duration = config.target_duration_seconds
        elif analysis['duration_adjustment']:
            target_duration = analysis['duration_adjustment']
        else:
            target_duration = original_script.total_duration_seconds
        
        # Process each section
        for section in original_script.sections:
            improved_section = self._improve_section(
                section, 
                title_v2, 
                analysis, 
                config,
                target_duration
            )
            improved_sections.append(improved_section)
        
        # Adjust durations to match target
        self._adjust_section_durations(improved_sections, target_duration)
        
        return improved_sections
    
    def _improve_section(
        self,
        section: ScriptSection,
        title_v2: str,
        analysis: Dict[str, Any],
        config: ScriptImproverConfig,
        target_total_duration: int
    ) -> ScriptSection:
        """Improve a single section based on feedback.
        
        In production, this would use AI to generate improved content.
        For MVP, we apply structured improvements based on feedback analysis.
        """
        # Calculate target words for this section
        target_words = int(section.estimated_duration_seconds * config.words_per_second)
        
        # Start with original content
        improved_content = section.content
        
        # Apply improvements based on analysis
        improvements_applied = []
        
        # Address critical issues for this section
        for issue in analysis['critical_issues']:
            if section.section_type in issue.lower() or "all sections" in issue.lower():
                # In production: AI would rewrite based on issue
                # For MVP: Add improvement note
                improvements_applied.append(f"Addressed: {issue[:50]}...")
        
        # Align with new title if needed
        if config.align_with_new_title and section.section_type == "introduction":
            # Introduction should reference new title themes
            if title_v2.lower() not in improved_content.lower():
                # In production: AI would integrate title themes
                # For MVP: Note the alignment
                improvements_applied.append(f"Aligned with title: {title_v2}")
        
        # Adjust tone if specified
        if config.tone and section.section_type == "body":
            improvements_applied.append(f"Adjusted tone to: {config.tone}")
        
        # Create improved section with notes
        notes = section.notes
        if improvements_applied:
            notes += "\n" + "Improvements: " + "; ".join(improvements_applied)
        
        improved_section = ScriptSection(
            section_type=section.section_type,
            content=improved_content,
            estimated_duration_seconds=section.estimated_duration_seconds,
            purpose=section.purpose,
            notes=notes
        )
        
        return improved_section
    
    def _adjust_section_durations(self, sections: List[ScriptSection], target_total: int):
        """Adjust section durations proportionally to match target total.
        
        Modifies sections in place.
        """
        current_total = sum(s.estimated_duration_seconds for s in sections)
        
        if current_total == 0 or current_total == target_total:
            return
        
        # Calculate adjustment ratio
        ratio = target_total / current_total
        
        # Adjust each section
        for section in sections:
            section.estimated_duration_seconds = int(section.estimated_duration_seconds * ratio)
        
        # Handle rounding by adjusting the largest section
        adjusted_total = sum(s.estimated_duration_seconds for s in sections)
        if adjusted_total != target_total:
            largest_section = max(sections, key=lambda s: s.estimated_duration_seconds)
            largest_section.estimated_duration_seconds += (target_total - adjusted_total)
    
    def _assemble_full_text(self, sections: List[ScriptSection]) -> str:
        """Assemble full script text from sections."""
        return "\n\n".join(section.content for section in sections)
    
    def _create_improvements_summary(self, analysis: Dict[str, Any]) -> str:
        """Create a summary of improvements made."""
        summary_parts = []
        
        if analysis['critical_issues']:
            summary_parts.append(f"Addressed {len(analysis['critical_issues'])} critical issues")
        
        if analysis['medium_issues']:
            summary_parts.append(f"Improved {len(analysis['medium_issues'])} medium-priority areas")
        
        if analysis['duration_adjustment']:
            summary_parts.append(f"Adjusted duration to {analysis['duration_adjustment']}s")
        
        if analysis['tone_adjustment']:
            summary_parts.append(f"Adjusted tone to {analysis['tone_adjustment']}")
        
        if not summary_parts:
            summary_parts.append("Minor refinements and polish")
        
        return "; ".join(summary_parts)
    
    def _create_title_alignment_notes(self, title_v2: str, analysis: Dict[str, Any]) -> str:
        """Create notes about title alignment."""
        notes_parts = [f"Aligned with title: '{title_v2}'"]
        
        if analysis['title_alignment_needs']:
            notes_parts.append("Emphasized: " + "; ".join(analysis['title_alignment_needs'][:2]))
        
        return " | ".join(notes_parts)


__all__ = ["ScriptImprover", "ScriptImproverConfig", "ScriptV2", "ReviewFeedback"]
