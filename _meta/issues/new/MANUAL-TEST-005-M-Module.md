# MANUAL-TEST-005: M (Metrics & Analytics Module) Manual Testing

**Module**: PrismQ.M  
**Type**: Manual Testing  
**Priority**: Medium  
**Status**: 🧪 READY FOR TESTING

---

## Overview

Manual testing issue for the M (Metrics & Analytics Module). The user will run the analytics workflow in a preview environment and provide logs for analysis.

---

## Module Description

The **M (Metrics & Analytics Module)** is a meta-module that monitors performance metrics of published content across all formats (text, audio, video). It collects metrics from published content, tracks KPIs, and provides insights that feed back into the ideation process.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         PrismQ Platform                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  T (Text)  →  A (Audio)  →  V (Video)  →  P (Publish)  →  M (Metrics)  │
│                                                                          │
│                                                 ↓                        │
│                                   T.IdeaInspiration (Feedback Loop)     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Sources

This module collects metrics from published content only:
```
PrismQ.T.PublishedText → PrismQ.M.Analytics (published text metrics)
PrismQ.A.PublishedAudio → PrismQ.M.Analytics (published audio metrics)
PrismQ.V.PublishedVideo → PrismQ.M.Analytics (published video metrics)
PrismQ.P.Published → PrismQ.M.Analytics (cross-platform metrics)
```

---

## Testing Checklist

### 1. Performance Tracking Tests
- [ ] **Engagement Metrics**: Collect views, plays, reads
- [ ] **Retention Metrics**: Collect completion rate, drop-off points
- [ ] **Growth Metrics**: Collect subscribers, followers, audience growth
- [ ] **Revenue Metrics**: Collect monetization, sponsorships (if applicable)

### 2. Analytics Integration Tests

#### Text Analytics
- [ ] **Medium Stats**: Test Medium stats collection
- [ ] **Blog Analytics**: Test blog analytics integration
- [ ] **Social Insights**: Test social media insights

#### Audio Analytics
- [ ] **Spotify for Podcasters**: Test Spotify analytics
- [ ] **Apple Podcasts Connect**: Test Apple Podcasts analytics

#### Video Analytics
- [ ] **YouTube Analytics**: Test YouTube Analytics API
- [ ] **TikTok Analytics**: Test TikTok Analytics

### 3. A/B Testing Tests
- [ ] **Title Testing**: Test clickthrough rate tracking
- [ ] **Thumbnail Testing**: Test video CTR tracking
- [ ] **Format Testing**: Test text vs audio vs video comparison
- [ ] **Platform Testing**: Test platform performance comparison

### 4. Insights & Reporting Tests
- [ ] **Performance Dashboards**: Generate dashboard data
- [ ] **Trend Identification**: Identify performance trends
- [ ] **Audience Analysis**: Analyze audience behavior
- [ ] **Content Recommendations**: Generate recommendations

### 5. Feedback Loop Tests
- [ ] **High-Performing Topics**: Identify top topics and formats
- [ ] **Audience Preferences**: Extract audience preferences
- [ ] **Publishing Optimization**: Determine optimal publishing times
- [ ] **Content Gap Analysis**: Identify content gaps and opportunities

---

## Test Commands

```bash
# Navigate to repository
cd /home/runner/work/PrismQ/PrismQ

# Run M module tests
python -m pytest M/ -v

# Test integration
python -m pytest tests/test_integration.py -k "metric" -v
```

---

## Expected Logs to Capture

When running the preview, please capture:

1. **Data Collection Logs**: Metrics collection from platforms
2. **Analytics Processing Logs**: Data processing and aggregation
3. **Insights Generation Logs**: Insight and recommendation generation
4. **Feedback Loop Logs**: Insights fed back to ideation
5. **Error Logs**: Any errors or warnings
6. **Dashboard Output**: Dashboard data generation

---

## Metric Categories to Test

### Text Metrics
| Metric | Type | Description |
|--------|------|-------------|
| Views | Engagement | Total page views |
| Reads | Engagement | Completed reads |
| Read Time | Engagement | Average time spent |
| Scroll Depth | Engagement | How far users scrolled |
| Likes | Interaction | User likes |
| Comments | Interaction | User comments |
| Shares | Interaction | Content shares |
| Search Ranking | SEO | Position in search results |

### Audio Metrics
| Metric | Type | Description |
|--------|------|-------------|
| Plays | Engagement | Total plays |
| Downloads | Engagement | Episode downloads |
| Completion Rate | Retention | % who finish |
| Subscribers | Growth | Podcast subscribers |
| Listen Time | Retention | Average listen duration |

### Video Metrics
| Metric | Type | Description |
|--------|------|-------------|
| Views | Performance | Total video views |
| Watch Time | Performance | Total watch time |
| Avg View Duration | Performance | Average view length |
| CTR | Discovery | Click-through rate |
| Likes | Engagement | User likes |
| Comments | Engagement | User comments |
| Retention Curve | Retention | Audience retention over time |

---

## Log Submission Format

Please provide logs in the following format:

```
### Environment
- Date: YYYY-MM-DD
- Python Version: X.X.X
- OS: [Windows/Linux/macOS]

### Test Executed
[Description of what was tested]

### Logs
[Paste logs here]

### Metrics Collected
- Text Metrics: [summary]
- Audio Metrics: [summary]
- Video Metrics: [summary]

### Insights Generated
[List any insights or recommendations generated]

### Observations
[Any observations or issues noted]

### Status
- [ ] All tests passed
- [ ] Some tests failed (list which)
- [ ] Errors encountered (describe)
```

---

## Implementation Status

🔄 **Planning Phase**: Architecture and design in progress  
📋 **Components**: To be implemented  
🎯 **Priority**: Medium (after core T, A, V workflows operational)

---

## Related Documentation

- [M Module README](../../M/README.md)

---

**Created**: 2025-12-04  
**Assigned To**: Human Tester  
**Status**: 🧪 READY FOR TESTING
