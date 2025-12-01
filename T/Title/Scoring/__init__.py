"""PrismQ.T.Title.ABTesting - A/B Testing Framework

This module provides A/B testing capabilities for title optimization,
enabling data-driven decisions through statistical analysis of variant performance.

Key Features:
- Multiple title variant testing (A/B/C/D...)
- Statistical significance calculation (chi-square test)
- Hash-based traffic splitting for consistent user assignment
- Performance metrics tracking (CTR, views, engagement)
- Test reports with winning variant recommendations

Workflow Position: Post-MVP Enhancement (Sprint 4)
"""

from .test_manager import (
    ABTest,
    TitleVariant,
    ABTestManager,
    TestStatus
)

from .statistics import (
    calculate_significance,
    VariantMetrics,
    SignificanceResult
)

from .variant_router import (
    assign_variant,
    VariantRouter
)

from .report_generator import (
    generate_report,
    TestReport,
    ReportGenerator
)

__all__ = [
    # Test Management
    'ABTest',
    'TitleVariant',
    'ABTestManager',
    'TestStatus',
    
    # Statistics
    'calculate_significance',
    'VariantMetrics',
    'SignificanceResult',
    
    # Variant Routing
    'assign_variant',
    'VariantRouter',
    
    # Reporting
    'generate_report',
    'TestReport',
    'ReportGenerator',
]

__version__ = '1.0.0'
__author__ = 'PrismQ Team - Worker17'
