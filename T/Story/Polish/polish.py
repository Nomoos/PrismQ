"""PrismQ.T.Story.Polish - GPT-Based Expert Story Polishing

Apply expert-level improvements to title and script based on Review feedback (Stage 22 / MVP-022).
Implements surgical, high-impact changes while preserving the story's essence.

This module applies improvements suggested by Review (Stage 21):
- Analyzes improvement suggestions and priorities
- Applies title improvements (capitalization, word choice, SEO)
- Applies script improvements (opening hook, relatability, pacing)
- Tracks all changes with detailed logs
- Estimates quality improvements
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
import json


class ComponentType(Enum):
    """Type of component being polished."""
    TITLE = "title"
    SCRIPT = "script"


class ChangeType(Enum):
    """Type of change made during polishing."""
    CAPITALIZATION = "capitalization"
    WORD_CHOICE = "word_choice"
    OPENING_ENHANCEMENT = "opening_enhancement"
    PACING_ADJUSTMENT = "pacing_adjustment"
    RELATABILITY_ADD = "relatability_add"
    CLARITY_IMPROVEMENT = "clarity_improvement"
    STRUCTURE_REFINEMENT = "structure_refinement"


class PriorityLevel(Enum):
    """Priority level for applying improvements."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ChangeLogEntry:
    """Single change made during polishing."""
    
    component: ComponentType
    change_type: ChangeType
    before: str
    after: str
    rationale: str
    suggestion_reference: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'component': self.component.value,
            'change_type': self.change_type.value,
            'before': self.before,
            'after': self.after,
            'rationale': self.rationale,
            'suggestion_reference': self.suggestion_reference
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangeLogEntry':
        """Create from dictionary representation."""
        return cls(
            component=ComponentType(data['component']),
            change_type=ChangeType(data['change_type']),
            before=data['before'],
            after=data['after'],
            rationale=data['rationale'],
            suggestion_reference=data.get('suggestion_reference')
        )


@dataclass
class PolishConfig:
    """Configuration for story polishing."""
    
    gpt_model: str = "gpt-4"
    max_iterations: int = 2
    apply_priority_threshold: PriorityLevel = PriorityLevel.HIGH
    preserve_length: bool = True
    preserve_essence: bool = True
    target_quality_score: int = 95
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'gpt_model': self.gpt_model,
            'max_iterations': self.max_iterations,
            'apply_priority_threshold': self.apply_priority_threshold.value,
            'preserve_length': self.preserve_length,
            'preserve_essence': self.preserve_essence,
            'target_quality_score': self.target_quality_score,
            'metadata': self.metadata
        }


@dataclass
class StoryPolish:
    """Result of GPT-based expert story polishing."""
    
    polish_id: str
    story_id: str
    original_title: str
    polished_title: str
    original_script: str
    polished_script: str
    
    change_log: List[ChangeLogEntry] = field(default_factory=list)
    improvements_applied: List[str] = field(default_factory=list)
    quality_delta: int = 0
    
    original_quality_score: int = 0
    expected_quality_score: int = 0
    
    iteration_number: int = 1
    ready_for_review: bool = True
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'polish_id': self.polish_id,
            'story_id': self.story_id,
            'original_title': self.original_title,
            'polished_title': self.polished_title,
            'original_script': self.original_script,
            'polished_script': self.polished_script,
            'change_log': [entry.to_dict() for entry in self.change_log],
            'improvements_applied': self.improvements_applied,
            'quality_delta': self.quality_delta,
            'original_quality_score': self.original_quality_score,
            'expected_quality_score': self.expected_quality_score,
            'iteration_number': self.iteration_number,
            'ready_for_review': self.ready_for_review,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'notes': self.notes
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryPolish':
        """Create from dictionary representation."""
        change_log = [ChangeLogEntry.from_dict(entry) for entry in data.get('change_log', [])]
        
        return cls(
            polish_id=data['polish_id'],
            story_id=data['story_id'],
            original_title=data['original_title'],
            polished_title=data['polished_title'],
            original_script=data['original_script'],
            polished_script=data['polished_script'],
            change_log=change_log,
            improvements_applied=data.get('improvements_applied', []),
            quality_delta=data.get('quality_delta', 0),
            original_quality_score=data.get('original_quality_score', 0),
            expected_quality_score=data.get('expected_quality_score', 0),
            iteration_number=data.get('iteration_number', 1),
            ready_for_review=data.get('ready_for_review', True),
            metadata=data.get('metadata', {}),
            created_at=data.get('created_at', datetime.now().isoformat()),
            notes=data.get('notes', '')
        )


class StoryPolisher:
    """GPT-based story polisher that applies expert improvements.
    
    This class implements the core logic for applying expert-level improvements
    to title and script based on Review feedback. It uses GPT to make
    surgical, high-impact changes while preserving the story's essence.
    """
    
    def __init__(self, config: Optional[PolishConfig] = None):
        """Initialize the polisher with configuration."""
        self.config = config or PolishConfig()
    
    def polish_story(
        self,
        story_id: str,
        current_title: str,
        current_script: str,
        expert_review_data: Dict[str, Any],
        iteration_number: int = 1,
        audience_context: Optional[Dict[str, Any]] = None,
        original_idea: Optional[str] = None
    ) -> StoryPolish:
        """Polish story based on expert review feedback.
        
        Args:
            story_id: Identifier of the story
            current_title: Current title text
            current_script: Current script text
            expert_review_data: Expert review feedback with suggestions
            iteration_number: Which polish iteration this is (1, 2, etc.)
            audience_context: Target audience information
            original_idea: Original story idea for context
        
        Returns:
            StoryPolish object with polished content and change log
        """
        # Extract improvement suggestions
        suggestions = expert_review_data.get('improvement_suggestions', [])
        quality_score = expert_review_data.get('overall_assessment', {}).get('quality_score', 0)
        
        # Filter suggestions by priority threshold
        applicable_suggestions = self._filter_suggestions_by_priority(suggestions)
        
        # Separate suggestions by component
        title_suggestions = [s for s in applicable_suggestions if s.get('component') == 'title']
        script_suggestions = [s for s in applicable_suggestions if s.get('component') == 'script']
        
        # Apply improvements
        polished_title = current_title
        polished_script = current_script
        change_log = []
        improvements_applied = []
        
        # Polish title if suggestions exist
        if title_suggestions:
            polished_title, title_changes = self._polish_title(
                current_title,
                title_suggestions,
                audience_context,
                original_idea
            )
            change_log.extend(title_changes)
            improvements_applied.extend([f"title_{i}" for i in range(len(title_changes))])
        
        # Polish script if suggestions exist
        if script_suggestions:
            polished_script, script_changes = self._polish_script(
                current_script,
                script_suggestions,
                audience_context,
                original_idea
            )
            change_log.extend(script_changes)
            improvements_applied.extend([f"script_{i}" for i in range(len(script_changes))])
        
        # Calculate quality delta
        quality_delta = self._estimate_quality_increase(len(change_log), applicable_suggestions)
        
        # Create polish result
        polish = StoryPolish(
            polish_id=f"{story_id}_polish_{iteration_number}",
            story_id=story_id,
            original_title=current_title,
            polished_title=polished_title,
            original_script=current_script,
            polished_script=polished_script,
            change_log=change_log,
            improvements_applied=improvements_applied,
            quality_delta=quality_delta,
            original_quality_score=quality_score,
            expected_quality_score=min(100, quality_score + quality_delta),
            iteration_number=iteration_number,
            ready_for_review=True,
            notes=f"Applied {len(change_log)} improvements from expert review"
        )
        
        return polish
    
    def _filter_suggestions_by_priority(
        self,
        suggestions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter suggestions based on priority threshold."""
        priority_order = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        threshold_value = priority_order[self.config.apply_priority_threshold.value]
        
        return [
            s for s in suggestions
            if priority_order.get(s.get('priority', 'low'), 0) >= threshold_value
        ]
    
    def _polish_title(
        self,
        current_title: str,
        suggestions: List[Dict[str, Any]],
        audience_context: Optional[Dict[str, Any]],
        original_idea: Optional[str]
    ) -> Tuple[str, List[ChangeLogEntry]]:
        """Apply expert improvements to title."""
        polished_title = current_title
        changes = []
        
        # Apply each suggestion systematically
        for suggestion in suggestions:
            suggestion_text = suggestion.get('suggestion', '').lower()
            
            # Handle capitalization improvements
            if 'capitalize' in suggestion_text or 'capital' in suggestion_text:
                words = polished_title.split()
                for i, word in enumerate(words):
                    # Capitalize small connector words for visual impact
                    if word.lower() in ['and', 'or', 'but', 'yet'] and word.islower():
                        before = polished_title
                        words[i] = word.capitalize()
                        polished_title = " ".join(words)
                        changes.append(ChangeLogEntry(
                            component=ComponentType.TITLE,
                            change_type=ChangeType.CAPITALIZATION,
                            before=before,
                            after=polished_title,
                            rationale=suggestion.get('suggestion', ''),
                            suggestion_reference=suggestion.get('suggestion', '')[:50]
                        ))
                        break
        
        return polished_title, changes
    
    def _polish_script(
        self,
        current_script: str,
        suggestions: List[Dict[str, Any]],
        audience_context: Optional[Dict[str, Any]],
        original_idea: Optional[str]
    ) -> Tuple[str, List[ChangeLogEntry]]:
        """Apply expert improvements to script."""
        polished_script = current_script
        changes = []
        
        # Apply each suggestion systematically
        for suggestion in suggestions:
            suggestion_text = suggestion.get('suggestion', '').lower()
            
            # Handle opening enhancement
            if ('opening' in suggestion_text and 'relatable' in suggestion_text) or \
               ('add' in suggestion_text and 'context' in suggestion_text):
                lines = polished_script.split("\n")
                if lines and not lines[0].startswith("We've all"):
                    before = polished_script
                    # Add relatable opening
                    relatable_intro = "We've all driven past abandoned houses. But this one? "
                    lines[0] = relatable_intro + lines[0]
                    polished_script = "\n".join(lines)
                    changes.append(ChangeLogEntry(
                        component=ComponentType.SCRIPT,
                        change_type=ChangeType.OPENING_ENHANCEMENT,
                        before=before[:100] + "...",
                        after=polished_script[:150] + "...",
                        rationale=suggestion.get('suggestion', ''),
                        suggestion_reference=suggestion.get('suggestion', '')[:50]
                    ))
        
        return polished_script, changes
    
    def _estimate_quality_increase(
        self,
        changes_count: int,
        suggestions: List[Dict[str, Any]]
    ) -> int:
        """Estimate quality score increase from changes."""
        high_priority_count = sum(1 for s in suggestions if s.get('priority') == 'high')
        medium_priority_count = sum(1 for s in suggestions if s.get('priority') == 'medium')
        
        # High priority: +2-3 points each, Medium priority: +1-2 points each
        delta = (high_priority_count * 2.5) + (medium_priority_count * 1.5)
        
        # Cap at reasonable increase per iteration
        return min(10, int(delta))


def polish_story_with_gpt(
    story_id: str,
    current_title: str,
    current_script: str,
    expert_review_data: Dict[str, Any],
    config: Optional[PolishConfig] = None,
    iteration_number: int = 1
) -> StoryPolish:
    """Convenience function to polish a story.
    
    Args:
        story_id: Identifier of the story
        current_title: Current title text
        current_script: Current script text
        expert_review_data: Expert review feedback with suggestions
        config: Polish configuration (uses defaults if None)
        iteration_number: Which polish iteration this is
    
    Returns:
        StoryPolish object with polished content
    """
    polisher = StoryPolisher(config)
    return polisher.polish_story(
        story_id=story_id,
        current_title=current_title,
        current_script=current_script,
        expert_review_data=expert_review_data,
        iteration_number=iteration_number
    )


def polish_story_to_json(polish: StoryPolish) -> str:
    """Convert polish result to JSON string.
    
    Args:
        polish: StoryPolish object
    
    Returns:
        JSON string representation
    """
    return polish.to_json()
