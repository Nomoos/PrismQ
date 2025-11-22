"""Title Acceptance Gate module for PrismQ MVP workflow.

This module implements Stage 12 (MVP-012) of the MVP workflow - the title
acceptance gate that determines whether a title is ready to proceed or needs
further refinement.

Public API:
    - check_title_acceptance(): Main acceptance gate function
    - TitleAcceptanceResult: Result data model
    - AcceptanceCriteria: Enum of acceptance criteria
    - AcceptanceCriterionResult: Individual criterion result

Usage:
    from T.Review.Title.Acceptance import check_title_acceptance
    
    result = check_title_acceptance(
        title_text="The Echo Mystery: Dark Secrets Revealed",
        title_version="v3",
        script_text="A mysterious echo reveals dark secrets...",
        script_version="v3"
    )
    
    if result.accepted:
        print("Title accepted - proceed to script acceptance")
    else:
        print(f"Title not accepted: {result.reason}")
        for rec in result.recommendations:
            print(f"  - {rec}")
"""

from .acceptance import (
    check_title_acceptance,
    TitleAcceptanceResult,
    AcceptanceCriteria,
    AcceptanceCriterionResult,
    evaluate_clarity,
    evaluate_engagement,
    evaluate_script_alignment,
    CLARITY_THRESHOLD,
    ENGAGEMENT_THRESHOLD,
    ALIGNMENT_THRESHOLD,
    OVERALL_THRESHOLD
)

__all__ = [
    'check_title_acceptance',
    'TitleAcceptanceResult',
    'AcceptanceCriteria',
    'AcceptanceCriterionResult',
    'evaluate_clarity',
    'evaluate_engagement',
    'evaluate_script_alignment',
    'CLARITY_THRESHOLD',
    'ENGAGEMENT_THRESHOLD',
    'ALIGNMENT_THRESHOLD',
    'OVERALL_THRESHOLD'
]
