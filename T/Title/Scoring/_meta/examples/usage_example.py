"""Example usage of the ABTesting module.

This example demonstrates how to:
1. Create an A/B test
2. Assign users to variants
3. Collect metrics
4. Analyze results
5. Generate a report with recommendations
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from test_manager import ABTestManager, TitleVariant
from variant_router import VariantRouter
from statistics import VariantMetrics
from report_generator import generate_report


def main():
    """Demonstrate A/B testing workflow."""
    
    print("=" * 70)
    print("PrismQ A/B Testing Framework - Example Usage")
    print("=" * 70)
    print()
    
    # Step 1: Create an A/B test
    print("Step 1: Creating A/B Test")
    print("-" * 70)
    
    manager = ABTestManager()
    
    # Define variants to test
    variants = [
        TitleVariant(
            variant_id="A",
            title="How AI is Transforming Healthcare in 2025",
            traffic_percent=50
        ),
        TitleVariant(
            variant_id="B",
            title="AI Healthcare Revolution: 2025 Breakthrough",
            traffic_percent=50
        )
    ]
    
    # Create the test
    start_date = datetime.now()
    end_date = start_date + timedelta(days=7)
    
    test = manager.create_test(
        test_id="test-2025-11-23-001",
        content_id="content-healthcare-ai",
        variants=variants,
        start_date=start_date,
        end_date=end_date,
        min_sample_size=1000,
        success_metric="ctr"
    )
    
    print(f"Test ID: {test.test_id}")
    print(f"Content ID: {test.content_id}")
    print(f"Status: {test.status.value}")
    print(f"Variants:")
    for v in test.variants:
        print(f"  - {v.variant_id}: {v.title} ({v.traffic_percent}%)")
    print()
    
    # Step 2: Start the test
    print("Step 2: Starting Test")
    print("-" * 70)
    
    manager.start_test(test.test_id)
    print(f"Test status: {test.status.value}")
    print()
    
    # Step 3: Assign users to variants
    print("Step 3: Assigning Users to Variants")
    print("-" * 70)
    
    router = VariantRouter()
    
    # Simulate 100 users
    print("Simulating 100 user assignments...")
    for i in range(100):
        user_id = f"user_{i:04d}"
        variant = router.assign(user_id, test.variants)
        if i < 5:  # Show first 5
            print(f"  {user_id} -> Variant {variant.variant_id}")
    
    # Check distribution
    stats = router.get_distribution_stats(test.variants)
    print(f"\nTraffic distribution:")
    for variant_id, percent in stats.items():
        print(f"  Variant {variant_id}: {percent:.1f}%")
    print()
    
    # Step 4: Collect metrics (simulated)
    print("Step 4: Collecting Performance Metrics")
    print("-" * 70)
    print("After 7 days of running the test...")
    print()
    
    # Simulated metrics showing Variant B performing better
    metrics_data = {
        "A": VariantMetrics(
            variant_id="A",
            views=2618,
            clicks=285,
            engagement_score=0.72
        ),
        "B": VariantMetrics(
            variant_id="B",
            views=2622,
            clicks=354,
            engagement_score=0.81
        )
    }
    
    print("Variant A Performance:")
    print(f"  Views: {metrics_data['A'].views}")
    print(f"  Clicks: {metrics_data['A'].clicks}")
    print(f"  CTR: {metrics_data['A'].ctr:.2f}%")
    print(f"  Engagement: {metrics_data['A'].engagement_score:.2f}")
    print()
    
    print("Variant B Performance:")
    print(f"  Views: {metrics_data['B'].views}")
    print(f"  Clicks: {metrics_data['B'].clicks}")
    print(f"  CTR: {metrics_data['B'].ctr:.2f}%")
    print(f"  Engagement: {metrics_data['B'].engagement_score:.2f}")
    print()
    
    # Step 5: Generate report
    print("Step 5: Generating Test Report")
    print("-" * 70)
    
    # Complete the test
    manager.complete_test(test.test_id)
    
    # Generate report
    report = generate_report(test, metrics_data)
    
    print(f"Test Report for: {report.test_id}")
    print(f"Status: {report.status}")
    print(f"Duration: {report.duration_days} days")
    print(f"Total Views: {report.total_views:,}")
    print()
    
    print("Variant Performance Comparison:")
    print(f"{'Variant':<10} {'Title':<45} {'Views':<8} {'Clicks':<8} {'CTR':<8}")
    print("-" * 85)
    for v in report.variants:
        title_short = v.title[:42] + "..." if len(v.title) > 45 else v.title
        print(f"{v.variant_id:<10} {title_short:<45} {v.views:<8} {v.clicks:<8} {v.ctr:.2f}%")
    print()
    
    print("Statistical Analysis:")
    print(f"  Winning Variant: {report.analysis.winning_variant}")
    print(f"  Confidence Level: {report.analysis.confidence:.1f}%")
    print(f"  P-Value: {report.analysis.p_value:.4f}")
    print(f"  Statistically Significant: {'Yes' if report.analysis.is_significant else 'No'}")
    if report.analysis.improvement:
        print(f"  Improvement: +{report.analysis.improvement:.1f}%")
    print()
    
    print("Recommendation:")
    print(f"  {report.recommendation}")
    print()
    
    # Export to dict (for JSON)
    print("Step 6: Export Report")
    print("-" * 70)
    
    report_dict = report.to_dict()
    print("Report can be exported as JSON:")
    print(f"  - test_id: {report_dict['test_id']}")
    print(f"  - winning_variant: {report_dict['analysis']['winning_variant']}")
    print(f"  - improvement: {report_dict['analysis']['improvement']}")
    print()
    
    print("=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
