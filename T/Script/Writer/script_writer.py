"""Script Writer with AI Feedback Loop for PrismQ.

This module defines the ScriptWriter functionality that integrates with
the AI Script Reviewer to create an iterative optimization feedback loop.

The Writer takes:
- Original text/script
- Review report from AI Script Reviewer
- Target audience specifications

And produces:
- Optimized script reflecting review feedback
- YouTube short optimized content (< 3 minutes, variable length)
- Audience-aligned improvements

Workflow:
    ScriptDraft → AI Reviewer → Review Report → AI Writer → Optimized Script
                       ↓                              ↓
                   (Feedback Loop if score < threshold)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class OptimizationStrategy(Enum):
    """Strategy for script optimization."""
    
    YOUTUBE_SHORT = "youtube_short"  # Optimize for YouTube shorts
    ENGAGEMENT_BOOST = "engagement_boost"  # Focus on engagement
    PACING_IMPROVEMENT = "pacing_improvement"  # Fix pacing issues
    CLARITY_ENHANCEMENT = "clarity_enhancement"  # Improve clarity
    AUDIENCE_ALIGNMENT = "audience_alignment"  # Better audience fit
    COMPREHENSIVE = "comprehensive"  # Address all issues


@dataclass
class OptimizationResult:
    """Result of script optimization."""
    
    original_text: str
    optimized_text: str
    changes_made: List[str]
    optimization_strategy: OptimizationStrategy
    estimated_score_improvement: int  # Expected score increase
    length_before_seconds: Optional[int] = None
    length_after_seconds: Optional[int] = None
    key_improvements: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class FeedbackLoopIteration:
    """Single iteration in the feedback loop."""
    
    iteration_number: int
    review_score: int
    optimization_applied: List[str]
    score_improvement: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ScriptWriter:
    """AI-powered script writer with feedback loop integration.
    
    The ScriptWriter works in conjunction with ScriptReview to implement
    an iterative optimization feedback loop:
    
    1. Receives original script and review report
    2. Analyzes improvement points prioritized by impact
    3. Applies optimizations based on review feedback
    4. Generates optimized script for target audience
    5. Can iterate multiple times until target score reached
    
    Features:
    - YouTube short optimization (< 3 minutes, variable length)
    - Audience-specific content adaptation
    - Iterative improvement based on AI review feedback
    - Score-driven optimization (target: 80%+)
    - Automatic feedback loop management
    
    Attributes:
        writer_id: AI writer identifier
        target_score_threshold: Minimum acceptable score (0-100)
        max_iterations: Maximum feedback loop iterations
        optimization_strategy: Current optimization strategy
        
        Feedback Loop State:
            current_iteration: Current iteration number
            iterations_history: History of all iterations
            original_script: Initial script text
            current_script: Latest optimized version
            cumulative_improvements: All improvements applied
            
        Performance Tracking:
            initial_score: Starting review score
            current_score: Latest review score
            score_progression: Score changes over iterations
            total_score_improvement: Overall improvement achieved
            
        Optimization Context:
            target_audience: Target audience description
            target_length_seconds: Target duration
            youtube_short_mode: Whether optimizing for YouTube shorts
            focus_areas: Priority areas from review
    
    Example:
        >>> from script_review import ScriptReview, ReviewCategory, ImprovementPoint
        >>> 
        >>> # Create writer
        >>> writer = ScriptWriter(
        ...     writer_id="AI-Writer-001",
        ...     target_score_threshold=80,
        ...     max_iterations=3,
        ...     optimization_strategy=OptimizationStrategy.YOUTUBE_SHORT
        ... )
        >>> 
        >>> # Original script
        >>> original_script = "A girl hears a voice... [145 seconds of content]"
        >>> 
        >>> # Apply review feedback
        >>> result = writer.optimize_from_review(
        ...     original_script=original_script,
        ...     review=review_report,
        ...     target_audience="Horror enthusiasts aged 18-35"
        ... )
        >>> 
        >>> print(f"Optimized from {result.length_before_seconds}s to {result.length_after_seconds}s")
        >>> print(f"Applied {len(result.changes_made)} improvements")
        >>> print(f"Expected score improvement: +{result.estimated_score_improvement}")
    """
    
    writer_id: str = "AI-ScriptWriter-001"
    target_score_threshold: int = 80  # Target quality score
    max_iterations: int = 3
    optimization_strategy: OptimizationStrategy = OptimizationStrategy.COMPREHENSIVE
    
    # Feedback Loop State
    current_iteration: int = 0
    iterations_history: List[FeedbackLoopIteration] = field(default_factory=list)
    original_script: str = ""
    current_script: str = ""
    cumulative_improvements: List[str] = field(default_factory=list)
    
    # Performance Tracking
    initial_score: int = 0
    current_score: int = 0
    score_progression: List[int] = field(default_factory=list)
    total_score_improvement: int = 0
    
    # Optimization Context
    target_audience: str = ""
    target_length_seconds: Optional[int] = None
    youtube_short_mode: bool = False
    focus_areas: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""
    metadata: Dict[str, str] = field(default_factory=dict)
    
    def optimize_from_review(
        self,
        original_script: str,
        review: Any,  # ScriptReview instance
        target_audience: Optional[str] = None
    ) -> OptimizationResult:
        """Optimize script based on review feedback.
        
        This is the main method that implements the feedback loop between
        AI Reviewer and AI Writer. It analyzes the review report and applies
        targeted optimizations to improve the script.
        
        Args:
            original_script: Original script text
            review: ScriptReview instance with evaluation and recommendations
            target_audience: Optional target audience override
            
        Returns:
            OptimizationResult with optimized script and details
        """
        # Initialize if first iteration
        if self.current_iteration == 0:
            self.original_script = original_script
            self.initial_score = review.overall_score
            self.score_progression.append(review.overall_score)
        
        self.current_iteration += 1
        self.current_script = original_script
        self.current_score = review.overall_score
        
        # Set optimization context
        if target_audience:
            self.target_audience = target_audience
        elif review.target_audience:
            self.target_audience = review.target_audience
        
        self.youtube_short_mode = review.is_youtube_short
        if review.optimal_length_seconds:
            self.target_length_seconds = review.optimal_length_seconds
        
        # Collect focus areas from review
        self.focus_areas = []
        for imp_point in review.get_high_priority_improvements():
            self.focus_areas.append(imp_point.title)
        
        # Determine optimization strategy based on review
        strategy = self._determine_strategy(review)
        
        # Apply optimizations (placeholder for actual AI implementation)
        changes_made = []
        optimized_text = original_script
        estimated_improvement = 0
        
        # Strategy-specific optimizations
        if strategy == OptimizationStrategy.YOUTUBE_SHORT:
            changes_made.append("Optimized for YouTube short format")
            changes_made.append(f"Reduced length to {self.target_length_seconds}s")
            estimated_improvement += 15
        
        if review.needs_major_revision:
            changes_made.append("Applied major structural revision")
            estimated_improvement += 20
        
        # Apply high-priority improvements
        for imp_point in review.get_high_priority_improvements():
            changes_made.append(f"{imp_point.title}: {imp_point.suggested_fix}")
            estimated_improvement += (imp_point.impact_score // 5)  # Partial impact
            self.cumulative_improvements.append(imp_point.title)
        
        # Quick wins
        for quick_win in review.quick_wins:
            changes_made.append(f"Quick win: {quick_win}")
            estimated_improvement += 5
        
        # Update tracking
        estimated_new_score = min(100, review.overall_score + estimated_improvement)
        self.score_progression.append(estimated_new_score)
        self.total_score_improvement = estimated_new_score - self.initial_score
        
        # Record iteration
        iteration = FeedbackLoopIteration(
            iteration_number=self.current_iteration,
            review_score=review.overall_score,
            optimization_applied=changes_made,
            score_improvement=estimated_improvement
        )
        self.iterations_history.append(iteration)
        
        # Create result
        result = OptimizationResult(
            original_text=original_script,
            optimized_text=optimized_text,
            changes_made=changes_made,
            optimization_strategy=strategy,
            estimated_score_improvement=estimated_improvement,
            length_before_seconds=review.current_length_seconds,
            length_after_seconds=self.target_length_seconds,
            key_improvements=self.focus_areas[:5],
            notes=f"Iteration {self.current_iteration}/{self.max_iterations}"
        )
        
        return result
    
    def should_continue_iteration(self) -> bool:
        """Check if feedback loop should continue.
        
        Returns:
            True if should iterate again, False if done
        """
        if self.current_iteration >= self.max_iterations:
            return False
        
        if self.current_score >= self.target_score_threshold:
            return False
        
        # Check if still making progress
        if len(self.score_progression) >= 2:
            recent_improvement = (
                self.score_progression[-1] - self.score_progression[-2]
            )
            if recent_improvement < 5:  # Diminishing returns
                return False
        
        return True
    
    def get_feedback_loop_summary(self) -> Dict[str, Any]:
        """Get summary of feedback loop progress.
        
        Returns:
            Dictionary with feedback loop metrics and status
        """
        return {
            "writer_id": self.writer_id,
            "current_iteration": self.current_iteration,
            "max_iterations": self.max_iterations,
            "initial_score": self.initial_score,
            "current_score": self.current_score,
            "total_improvement": self.total_score_improvement,
            "score_progression": self.score_progression,
            "target_threshold": self.target_score_threshold,
            "target_reached": self.current_score >= self.target_score_threshold,
            "should_continue": self.should_continue_iteration(),
            "improvements_applied": len(self.cumulative_improvements),
            "focus_areas": self.focus_areas,
            "optimization_strategy": self.optimization_strategy.value,
            "youtube_short_mode": self.youtube_short_mode,
            "target_audience": self.target_audience
        }
    
    def _determine_strategy(self, review: Any) -> OptimizationStrategy:
        """Determine optimization strategy based on review.
        
        Args:
            review: ScriptReview instance
            
        Returns:
            Appropriate optimization strategy
        """
        if review.is_youtube_short and review.current_length_seconds:
            if review.current_length_seconds > (review.optimal_length_seconds or 90):
                return OptimizationStrategy.YOUTUBE_SHORT
        
        # Check for dominant weak category
        if review.category_scores:
            weak_categories = [
                cs for cs in review.category_scores if cs.score < 70
            ]
            if weak_categories:
                weakest = min(weak_categories, key=lambda cs: cs.score)
                category_name = weakest.category.value
                
                if "engagement" in category_name:
                    return OptimizationStrategy.ENGAGEMENT_BOOST
                elif "pacing" in category_name:
                    return OptimizationStrategy.PACING_IMPROVEMENT
                elif "clarity" in category_name:
                    return OptimizationStrategy.CLARITY_ENHANCEMENT
                elif "audience" in category_name:
                    return OptimizationStrategy.AUDIENCE_ALIGNMENT
        
        return OptimizationStrategy.COMPREHENSIVE
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ScriptWriter to dictionary representation.
        
        Returns:
            Dictionary containing all fields
        """
        data = asdict(self)
        data["optimization_strategy"] = self.optimization_strategy.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScriptWriter":
        """Create ScriptWriter from dictionary.
        
        Args:
            data: Dictionary containing ScriptWriter fields
            
        Returns:
            ScriptWriter instance
        """
        # Handle enum conversion
        strategy = data.get("optimization_strategy", "comprehensive")
        if isinstance(strategy, str):
            try:
                strategy = OptimizationStrategy(strategy)
            except ValueError:
                strategy = OptimizationStrategy.COMPREHENSIVE
        
        # Convert iterations history
        iterations = []
        for iter_data in data.get("iterations_history", []):
            iterations.append(FeedbackLoopIteration(
                iteration_number=iter_data["iteration_number"],
                review_score=iter_data["review_score"],
                optimization_applied=iter_data["optimization_applied"],
                score_improvement=iter_data["score_improvement"],
                timestamp=iter_data.get("timestamp", datetime.now().isoformat())
            ))
        
        return cls(
            writer_id=data.get("writer_id", "AI-ScriptWriter-001"),
            target_score_threshold=data.get("target_score_threshold", 80),
            max_iterations=data.get("max_iterations", 3),
            optimization_strategy=strategy,
            current_iteration=data.get("current_iteration", 0),
            iterations_history=iterations,
            original_script=data.get("original_script", ""),
            current_script=data.get("current_script", ""),
            cumulative_improvements=data.get("cumulative_improvements", []),
            initial_score=data.get("initial_score", 0),
            current_score=data.get("current_score", 0),
            score_progression=data.get("score_progression", []),
            total_score_improvement=data.get("total_score_improvement", 0),
            target_audience=data.get("target_audience", ""),
            target_length_seconds=data.get("target_length_seconds"),
            youtube_short_mode=data.get("youtube_short_mode", False),
            focus_areas=data.get("focus_areas", []),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            notes=data.get("notes", ""),
            metadata=data.get("metadata", {})
        )
    
    def __repr__(self) -> str:
        """String representation of ScriptWriter."""
        return (
            f"ScriptWriter(id='{self.writer_id}', "
            f"iteration={self.current_iteration}/{self.max_iterations}, "
            f"score={self.current_score}%, "
            f"improvement=+{self.total_score_improvement})"
        )
