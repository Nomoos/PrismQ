# IMP-012: Historical Performance Data Integration

**Type**: Improvement - Acceptance Gates  
**Worker**: Worker17 (Analytics Specialist)  
**Priority**: High  
**Effort**: 2 days  
**Module**: `PrismQ.T.Review.Title.Acceptance`, `PrismQ.T.Review.Script.Acceptance`  
**Category**: Acceptance Gates  
**Status**: 🎯 PLANNED

---

## Description

Integrate historical performance data from published content into acceptance gates to make data-driven decisions. Track which accepted titles/scripts performed well (engagement, retention, conversions) and use this data to refine acceptance criteria and scoring. Enables continuous improvement based on real-world results.

Current acceptance gates use static criteria. This enhancement adds feedback loop from actual performance, making acceptance smarter over time.

---

## Business Justification

- Data-driven acceptance improves content quality by 40%+
- Learn which patterns actually work vs. theoretical "best practices"
- Continuous improvement without manual updates
- Identifies emerging trends and patterns
- Reduces reliance on subjective judgment

---

## Acceptance Criteria

- [ ] Design performance metrics schema (engagement, retention, clicks, etc.)
- [ ] Implement data collection pipeline from published content
- [ ] Create performance tracking database tables
- [ ] Build performance analysis dashboard
- [ ] Correlate acceptance scores with actual performance
- [ ] Identify high-performing patterns (titles, script structures)
- [ ] Update acceptance criteria based on performance data
- [ ] Implement dynamic threshold adjustment
- [ ] Generate performance-based recommendations
- [ ] Add performance prediction to acceptance results

---

## Performance Metrics to Track

### Title Performance
- **Click-Through Rate (CTR)**: % of impressions that clicked
- **Engagement Rate**: Likes, comments, shares
- **Search Ranking**: Position for target keywords
- **Bounce Rate**: % who left immediately
- **Social Shares**: Viral potential indicator

### Script Performance
- **Completion Rate**: % who watched to end
- **Average Watch Time**: How long viewers stayed
- **Retention Curve**: Where viewers drop off
- **Re-watch Rate**: Indicates quality
- **Conversion Rate**: For CTA effectiveness

### Combined Metrics
- **Overall Quality Score**: Composite metric
- **Audience Satisfaction**: Ratings, feedback
- **ROI**: Revenue per content piece
- **Long-term Value**: Evergreen performance

---

## Input/Output

**Input (Collection)**:
```python
{
    "content_id": "12345",
    "title": "The Secret Nobody Knows",
    "script_id": "67890",
    "published_date": "2024-11-20",
    "platform": "youtube",
    "performance_data": {
        "impressions": 50000,
        "clicks": 4500,  # CTR: 9%
        "avg_watch_time": 48,  # seconds
        "completion_rate": 0.72,
        "engagement_score": 85,
        "shares": 230
    },
    "acceptance_scores": {
        "title_score": 88,
        "script_score": 82
    }
}
```

**Output (Analysis)**:
```python
{
    "analysis_period": "last_90_days",
    "total_content_pieces": 250,
    "correlations": {
        "title_score_vs_ctr": 0.72,  # Strong positive correlation
        "script_score_vs_completion": 0.68,
        "overall_acceptance_vs_performance": 0.75
    },
    "high_performers": {
        "average_title_score": 92,
        "average_script_score": 88,
        "common_patterns": [
            "Question-based titles (CTR +25%)",
            "Under 50-second scripts (completion +30%)",
            "Strong hook scores >90 (retention +40%)"
        ]
    },
    "threshold_recommendations": {
        "title_acceptance_threshold": {
            "current": 75,
            "recommended": 80,
            "reason": "Titles scoring 80+ have 35% better CTR"
        },
        "script_acceptance_threshold": {
            "current": 70,
            "recommended": 78,
            "reason": "Scripts scoring 78+ have 40% better completion"
        }
    },
    "underperformers": {
        "patterns": [
            "Titles with 'ultimate guide' (CTR -15%)",
            "Scripts over 90s on shorts (completion -45%)"
        ],
        "recommendations": [
            "Increase title engagement threshold for 'guide' titles",
            "Stricter timing requirements for short-form"
        ]
    }
}
```

---

## Technical Implementation

```python
class PerformanceTracker:
    def track_content_performance(
        self,
        content_id: str,
        performance_data: dict
    ) -> None:
        """Store performance data for analysis."""
        
        # Store in database
        self.db.insert_performance_record({
            "content_id": content_id,
            "timestamp": datetime.now(),
            "metrics": performance_data
        })
        
        # Update aggregated statistics
        self._update_statistics(content_id, performance_data)
    
    def analyze_acceptance_performance_correlation(
        self,
        days: int = 90
    ) -> CorrelationAnalysis:
        """Analyze correlation between acceptance scores and performance."""
        
        # Get content from last N days
        data = self.db.query_content_with_performance(days)
        
        # Calculate correlations
        title_corr = self._calculate_correlation(
            [d.title_score for d in data],
            [d.ctr for d in data]
        )
        
        script_corr = self._calculate_correlation(
            [d.script_score for d in data],
            [d.completion_rate for d in data]
        )
        
        # Identify patterns
        high_performers = self._identify_high_performers(data, top_percentile=0.20)
        low_performers = self._identify_low_performers(data, bottom_percentile=0.20)
        
        patterns = self._extract_patterns(high_performers, low_performers)
        
        return CorrelationAnalysis(
            title_score_vs_ctr=title_corr,
            script_score_vs_completion=script_corr,
            patterns=patterns
        )

class DynamicThresholdAdjuster:
    def adjust_thresholds_based_on_performance(
        self,
        analysis: CorrelationAnalysis
    ) -> ThresholdRecommendations:
        """Recommend threshold adjustments based on performance data."""
        
        # Analyze current threshold effectiveness
        current_title_threshold = 75
        current_script_threshold = 70
        
        # Find optimal thresholds
        optimal_title = self._find_optimal_threshold(
            scores=[d.title_score for d in analysis.data],
            performance=[d.ctr for d in analysis.data],
            current=current_title_threshold
        )
        
        optimal_script = self._find_optimal_threshold(
            scores=[d.script_score for d in analysis.data],
            performance=[d.completion_rate for d in analysis.data],
            current=current_script_threshold
        )
        
        return ThresholdRecommendations(
            title_threshold=optimal_title,
            script_threshold=optimal_script,
            reasoning={...}
        )
```

### Database Schema

```sql
CREATE TABLE content_performance (
    id INTEGER PRIMARY KEY,
    content_id TEXT,
    title TEXT,
    script_id TEXT,
    platform TEXT,
    published_date TIMESTAMP,
    
    -- Acceptance scores
    title_acceptance_score INTEGER,
    script_acceptance_score INTEGER,
    
    -- Performance metrics
    impressions INTEGER,
    clicks INTEGER,
    ctr FLOAT,
    avg_watch_time FLOAT,
    completion_rate FLOAT,
    engagement_score INTEGER,
    shares INTEGER,
    
    -- Timestamps
    tracked_date TIMESTAMP,
    last_updated TIMESTAMP
);

CREATE INDEX idx_performance_date ON content_performance(published_date);
CREATE INDEX idx_performance_scores ON content_performance(title_acceptance_score, script_acceptance_score);
```

---

## Dependencies

- **MVP-012**: Title Acceptance Gate (enhancement target)
- **MVP-013**: Script Acceptance Gate (enhancement target)
- **MVP-024**: Publishing (performance data source)
- **M Module**: Metrics module (future integration)
- Database for performance tracking

---

## Success Metrics

- Performance tracking covers >95% of published content
- Correlation analysis runs daily automatically
- Data-driven threshold adjustments improve performance by 20%+
- High-performer pattern identification accuracy >85%
- System identifies emerging trends within 2 weeks
- Dashboard provides actionable insights >90% of time

---

**Created**: 2025-11-24  
**Owner**: Worker17 (Analytics Specialist)  
**Category**: Acceptance Gates Improvements
