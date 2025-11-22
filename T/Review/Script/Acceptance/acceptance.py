"""Script Acceptance Gate for PrismQ MVP-013.

This module implements the acceptance criteria check for scripts before they
proceed to quality review stages. It verifies that the script (latest version)
meets acceptance criteria for completeness, coherence, and alignment with title.

Workflow Position:
    Title Accepted (MVP-012) → Script Acceptance Check (MVP-013) → Quality Reviews (MVP-014+)
    
If NOT ACCEPTED: Loop back to MVP-010 (Script Review → Script Refinement)
If ACCEPTED: Proceed to MVP-014 (Quality Reviews)

The acceptance check always uses the newest/latest script version.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


@dataclass
class ScriptAcceptanceResult:
    """Result of script acceptance check.
    
    Attributes:
        accepted: Whether the script is accepted
        reason: Explanation for acceptance or rejection
        completeness_score: Score for script completeness (0-100)
        coherence_score: Score for script coherence (0-100)
        alignment_score: Score for alignment with title (0-100)
        overall_score: Overall acceptance score (0-100)
        issues: List of issues preventing acceptance (if rejected)
        suggestions: Suggestions for improvement (if rejected)
    """
    
    accepted: bool
    reason: str
    completeness_score: int
    coherence_score: int
    alignment_score: int
    overall_score: int
    issues: List[str]
    suggestions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)


def check_script_acceptance(
    script_text: str,
    title: str,
    script_version: Optional[str] = None,
    acceptance_threshold: int = 70
) -> Dict[str, Any]:
    """Check if script meets acceptance criteria.
    
    This function evaluates the latest version of the script to determine
    if it meets the acceptance criteria for completeness, coherence, and
    alignment with the title.
    
    Acceptance Criteria:
    - Completeness: Script has clear beginning, middle, and end
    - Coherence: Script flows logically and makes sense
    - Alignment: Script content aligns with the title promise
    
    Args:
        script_text: The script text to evaluate (latest version)
        title: The accepted title
        script_version: Optional version identifier (e.g., "v3", "v4")
        acceptance_threshold: Minimum score required for acceptance (default: 70)
        
    Returns:
        Dictionary with:
        - accepted: True/False
        - reason: Explanation for the decision
        - completeness_score: Score for completeness (0-100)
        - coherence_score: Score for coherence (0-100)
        - alignment_score: Score for alignment with title (0-100)
        - overall_score: Overall acceptance score (0-100)
        - issues: List of issues (if rejected)
        - suggestions: List of suggestions (if rejected)
        
    Example:
        >>> result = check_script_acceptance(
        ...     script_text="A mysterious echo in an old house...",
        ...     title="The Echo Mystery",
        ...     script_version="v3"
        ... )
        >>> if result["accepted"]:
        ...     print("Proceed to quality reviews")
        ... else:
        ...     print(f"Loop back to refinement: {result['reason']}")
    """
    # Validate inputs
    if not script_text or not script_text.strip():
        return ScriptAcceptanceResult(
            accepted=False,
            reason="Script is empty or contains only whitespace",
            completeness_score=0,
            coherence_score=0,
            alignment_score=0,
            overall_score=0,
            issues=["Script text is empty"],
            suggestions=["Generate script content"]
        ).to_dict()
    
    if not title or not title.strip():
        return ScriptAcceptanceResult(
            accepted=False,
            reason="Title is empty or missing",
            completeness_score=0,
            coherence_score=0,
            alignment_score=0,
            overall_score=0,
            issues=["Title is required for acceptance check"],
            suggestions=["Provide a valid title"]
        ).to_dict()
    
    # Evaluate acceptance criteria
    completeness_score = _evaluate_completeness(script_text)
    coherence_score = _evaluate_coherence(script_text)
    alignment_score = _evaluate_alignment(script_text, title)
    
    # Calculate overall score (weighted average)
    overall_score = int(
        (completeness_score * 0.35) +
        (coherence_score * 0.35) +
        (alignment_score * 0.30)
    )
    
    # Determine acceptance
    accepted = overall_score >= acceptance_threshold
    
    # Collect issues and suggestions if not accepted
    issues = []
    suggestions = []
    
    if not accepted:
        if completeness_score < acceptance_threshold:
            issues.append(f"Completeness score ({completeness_score}) below threshold")
            suggestions.append("Ensure script has clear beginning, middle, and end")
        
        if coherence_score < acceptance_threshold:
            issues.append(f"Coherence score ({coherence_score}) below threshold")
            suggestions.append("Improve logical flow and narrative structure")
        
        if alignment_score < acceptance_threshold:
            issues.append(f"Alignment score ({alignment_score}) below threshold")
            suggestions.append("Better align script content with title promise")
        
        reason = (
            f"Script does not meet acceptance criteria (score: {overall_score}/{acceptance_threshold}). "
            f"Loop back to script review and refinement (MVP-010)."
        )
    else:
        reason = (
            f"Script meets acceptance criteria (score: {overall_score}/{acceptance_threshold}). "
            f"Proceed to quality reviews (MVP-014)."
        )
    
    return ScriptAcceptanceResult(
        accepted=accepted,
        reason=reason,
        completeness_score=completeness_score,
        coherence_score=coherence_score,
        alignment_score=alignment_score,
        overall_score=overall_score,
        issues=issues,
        suggestions=suggestions
    ).to_dict()


def _evaluate_completeness(script_text: str) -> int:
    """Evaluate script completeness.
    
    Checks if script has:
    - Sufficient length (not too short)
    - Clear structure (beginning, middle, end indicators)
    - Complete narrative arc
    
    Args:
        script_text: The script text to evaluate
        
    Returns:
        Completeness score (0-100)
    """
    score = 0
    script_lower = script_text.lower()
    words = script_text.split()
    word_count = len(words)
    
    # Base score from word count
    if word_count < 20:
        score += 20  # Too short
    elif word_count < 50:
        score += 50  # Short but potentially complete
    elif word_count < 100:
        score += 75  # Good length
    else:
        score += 85  # Comprehensive
    
    # Check for narrative structure indicators
    beginning_indicators = ['begin', 'start', 'open', 'first', 'once', 'intro']
    middle_indicators = ['then', 'next', 'suddenly', 'meanwhile', 'however', 'but']
    end_indicators = ['finally', 'end', 'conclude', 'last', 'realize', 'discover']
    
    has_beginning = any(indicator in script_lower for indicator in beginning_indicators)
    has_middle = any(indicator in script_lower for indicator in middle_indicators)
    has_ending = any(indicator in script_lower for indicator in end_indicators)
    
    # Bonus points for structure
    if has_beginning:
        score += 5
    if has_middle:
        score += 5
    if has_ending:
        score += 5
    
    # Cap at 100
    return min(score, 100)


def _evaluate_coherence(script_text: str) -> int:
    """Evaluate script coherence.
    
    Checks if script:
    - Flows logically (has connecting words)
    - Forms complete sentences
    - Maintains consistent narrative
    
    Args:
        script_text: The script text to evaluate
        
    Returns:
        Coherence score (0-100)
    """
    score = 50  # Start with baseline
    script_lower = script_text.lower()
    
    # Check for connecting words (transition indicators)
    connecting_words = [
        'and', 'but', 'however', 'therefore', 'because', 'so', 'then',
        'meanwhile', 'suddenly', 'finally', 'after', 'before', 'while',
        'although', 'since', 'when', 'where', 'as', 'if'
    ]
    
    connection_count = sum(
        1 for word in connecting_words 
        if f' {word} ' in f' {script_lower} '
    )
    
    # More connections suggest better flow
    if connection_count >= 5:
        score += 30
    elif connection_count >= 3:
        score += 20
    elif connection_count >= 1:
        score += 10
    
    # Check for sentence structure (presence of punctuation)
    sentences = [s.strip() for s in script_text.split('.') if s.strip()]
    if len(sentences) >= 2:
        score += 10  # Multiple sentences
    
    # Check for paragraph breaks (suggests organized thought)
    paragraphs = [p.strip() for p in script_text.split('\n') if p.strip()]
    if len(paragraphs) >= 2:
        score += 10  # Multiple paragraphs
    
    # Cap at 100
    return min(score, 100)


def _evaluate_alignment(script_text: str, title: str) -> int:
    """Evaluate script-title alignment.
    
    Checks if script:
    - References key concepts from title
    - Delivers on title's promise
    - Maintains thematic consistency with title
    
    Args:
        script_text: The script text to evaluate
        title: The title to align with
        
    Returns:
        Alignment score (0-100)
    """
    score = 40  # Start with baseline
    
    script_lower = script_text.lower()
    title_lower = title.lower()
    
    # Extract key words from title (excluding common stopwords)
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of'}
    title_words = [
        word.strip('.,!?;:') 
        for word in title_lower.split() 
        if word.strip('.,!?;:') not in stopwords and len(word) > 2
    ]
    
    if not title_words:
        # Title has no meaningful words, give benefit of doubt
        return 75
    
    # Check how many title keywords appear in script
    matches = sum(1 for word in title_words if word in script_lower)
    match_ratio = matches / len(title_words) if title_words else 0
    
    # Score based on keyword presence
    if match_ratio >= 0.8:
        score += 40  # Excellent alignment
    elif match_ratio >= 0.5:
        score += 30  # Good alignment
    elif match_ratio >= 0.3:
        score += 20  # Moderate alignment
    elif match_ratio >= 0.1:
        score += 10  # Weak alignment
    
    # Bonus for exact phrase matches
    if len(title_words) >= 2:
        # Check for bigrams from title
        title_bigrams = [
            f"{title_words[i]} {title_words[i+1]}"
            for i in range(len(title_words) - 1)
        ]
        bigram_matches = sum(1 for bigram in title_bigrams if bigram in script_lower)
        if bigram_matches > 0:
            score += min(bigram_matches * 10, 20)
    
    # Cap at 100
    return min(score, 100)
