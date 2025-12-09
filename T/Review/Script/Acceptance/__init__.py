"""PrismQ.T.Review.Script.Acceptance - Script Acceptance Gate Module

This module implements MVP-013: Script Acceptance Gate that determines if a
script (latest version) is ready to proceed to quality reviews.

Acceptance Criteria:
- Completeness: Script has clear beginning, middle, and end
- Coherence: Script flows logically and makes sense
- Alignment: Script content aligns with the title promise

Workflow:
- If ACCEPTED: Proceed to MVP-014 (Quality Reviews)
- If NOT ACCEPTED: Loop back to MVP-010 (Script Review → Refinement)

Always uses the newest/latest script version.

Example Usage:
    >>> from PrismQ.T.Review.Script.Acceptance import check_script_acceptance
    >>>
    >>> result = check_script_acceptance(
    ...     script_text="In the old house, mysterious echoes reveal secrets...",
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

from .acceptance import ScriptAcceptanceResult, check_script_acceptance

__all__ = ["check_script_acceptance", "ScriptAcceptanceResult"]
