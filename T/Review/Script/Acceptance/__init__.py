"""PrismQ.T.Review.Content.Acceptance - Content Acceptance Gate Module

This module implements MVP-013: Content Acceptance Gate that determines if a
script (latest version) is ready to proceed to quality reviews.

Acceptance Criteria:
- Completeness: Content has clear beginning, middle, and end
- Coherence: Content flows logically and makes sense
- Alignment: Content content aligns with the title promise

Workflow:
- If ACCEPTED: Proceed to MVP-014 (Quality Reviews)
- If NOT ACCEPTED: Loop back to MVP-010 (Content Review → Refinement)

Always uses the newest/latest script version.

Example Usage:
    >>> from PrismQ.T.Review.Content.Acceptance import check_content_acceptance
    >>>
    >>> result = check_content_acceptance(
    ...     content_text="In the old house, mysterious echoes reveal secrets...",
    ...     title="The Echo Mystery",
    ...     script_version="v3"
    ... )
    >>>
    >>> if result["accepted"]:
    ...     print("Proceed to quality reviews")
    ... else:
    ...     print(f"Rejected: {result['reason']}")
    ...     print(f"Issues: {result['issues']}")
"""

from .acceptance import ScriptAcceptanceResult, check_content_acceptance

__all__ = ["check_content_acceptance", "ScriptAcceptanceResult"]
