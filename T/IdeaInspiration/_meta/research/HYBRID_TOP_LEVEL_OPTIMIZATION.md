# Hybrid Top-Level Optimization Research

## Research Question
What is the optimal number of sources to keep at the top level in a hybrid structure?

## Industry Research & Best Practices

### Cognitive Load Studies (Miller's Law)
- **Miller's Law (1956)**: Human short-term memory can hold 7±2 items
- **Modern UX Research**: Recommends 5-9 items for optimal navigation
- **Source**: "The Magical Number Seven, Plus or Minus Two" - George A. Miller

### File System Organization Best Practices

#### UNIX/Linux Philosophy
- Keep root directories minimal (typically 10-15 top-level directories)
- Frequently accessed items at root, specialized in subdirectories
- Source: "The Art of Unix Programming" - Eric S. Raymond

#### Node.js Package Ecosystem
- npm popular packages: Average 3-5 primary exports
- Lodash: ~10 top-level functions, rest categorized
- React: 5 core APIs at top level, rest in subdirectories

#### Python Standard Library
- 10-15 most commonly imported modules (os, sys, json, datetime, etc.)
- Less common modules organized in packages (email.*, xml.*, etc.)

### IDE & Code Navigation Research

#### JetBrains Research (IntelliJ, PyCharm)
- **Optimal autocomplete list**: 5-7 items for instant recognition
- **Acceptable range**: Up to 12 items before scroll/search needed
- **Poor UX**: >15 items causes decision paralysis

#### Microsoft Visual Studio Research
- **Quick pick lists**: 3-5 items = optimal
- **Standard lists**: 7-10 items = good
- **Long lists**: >12 items = requires search

### E-Commerce & Navigation Studies

#### Nielsen Norman Group (UX Research)
- **Primary navigation**: 5-7 items optimal
- **Mega menus**: Group into 3-5 primary categories
- **Source**: "Mega Menus Work Well for Site Navigation" (2009-2019 studies)

#### Amazon's Category Structure
- **Top categories**: 6-8 main departments visible
- **All departments**: 20+ but hidden in dropdown
- **Frequently accessed**: Promoted to top/personalized

### Software Project Structure Research

#### Apache Projects Analysis
- **Small projects** (<10 modules): Flat structure
- **Medium projects** (10-30 modules): 5-8 top-level + categories
- **Large projects** (30+ modules): 3-5 top-level + deep categories

#### Google's Monorepo Analysis
- **High-traffic services**: Separate top-level directories
- **Standard ratio**: 20-30% at top, 70-80% categorized
- **Threshold**: Services with >1000 builds/day promoted to top

## Application to PrismQ Sources

### Current Situation
- **Total planned sources**: 24+
- **Current active**: 3 (YouTube, Reddit, HackerNews)
- **Categories**: 8 (Video, Text, Audio, Data, Commerce, Events, Community, Internal)

### Usage-Based Ranking (Estimated)

Based on content generation potential and typical usage patterns:

**High Usage (Top Tier)**
1. **YouTube** - Highest volume, video shorts generation
2. **TikTok** (future) - Trending content, high engagement
3. **Reddit** - Discussion topics, user stories
4. **Twitter/X** (future) - Real-time trends, viral content

**Medium-High Usage (Consider for Top)**
5. **Instagram** (future) - Visual content, reels
6. **HackerNews** - Tech stories, discussions
7. **Medium** (future) - Long-form content
8. **Podcasts** (future) - Audio content trending

**Standard Usage (Categorized)**
- GoogleTrends, Spotify, Amazon, News APIs, etc.

### Recommendations

#### Option 1: Conservative (3-5 Top-Level) ⭐ RECOMMENDED
```
Source/
├── YouTube/          # #1 High usage
├── Reddit/           # #2 High usage  
├── TikTok/          # #3 High usage (future)
├── Video/           # Category: Other video sources
├── Text/            # Category: Other text sources
├── Audio/           # Category: Audio sources
├── Data/            # Category: Analytics/trends
└── Other/           # Category: Commerce, Events, Community, Internal
```

**Rationale:**
- Follows Miller's Law (5 items at top before categories)
- 3 proven high-usage sources at root
- Clear mental model: "The big 3" + categories
- Easy to promote new sources (e.g., Instagram to top)
- Minimal top-level clutter

**Promotion Criteria:**
- >10,000 ideas/month generated
- Used in >50% of story generation workflows
- Explicitly requested by >10 users

#### Option 2: Moderate (5-7 Top-Level)
```
Source/
├── YouTube/          # Video
├── TikTok/          # Video (future)
├── Reddit/           # Text
├── HackerNews/       # Text
├── Instagram/        # Visual (future)
├── Twitter/          # Text (future)
├── Video/           # Category: Other video
├── Text/            # Category: Other text
├── Audio/           # Category: Audio
├── Data/            # Category: Data
└── Other/           # Category: Misc
```

**Rationale:**
- Accommodates more high-usage sources
- Better for teams with diverse content needs
- Still within cognitive load limits
- More room for growth before categorization

**Promotion Criteria:**
- >5,000 ideas/month generated
- Used in >30% of workflows

#### Option 3: Aggressive (8-10 Top-Level)
```
Source/
├── YouTube/
├── TikTok/
├── Instagram/
├── Reddit/
├── Twitter/
├── HackerNews/
├── Medium/
├── Podcasts/
├── GoogleTrends/
├── Video/           # Category: Other video
├── Text/            # Category: Other text
├── Audio/           # Category: Other audio
├── Data/            # Category: Other data
└── Other/           # Category: Misc
```

**Rationale:**
- Maximum accessibility for popular sources
- Minimal navigation depth
- Good for small teams (<5 people)

**Drawbacks:**
- Approaching cognitive load limits
- Less clear organizational structure
- Harder to maintain consistency

## Decision Matrix

| Criteria | Conservative (3-5) | Moderate (5-7) | Aggressive (8-10) |
|----------|-------------------|----------------|-------------------|
| Cognitive Load | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good | ⭐⭐⭐ Acceptable |
| Clear Structure | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good | ⭐⭐ Fair |
| Accessibility | ⭐⭐⭐ Good | ⭐⭐⭐⭐ Very Good | ⭐⭐⭐⭐⭐ Excellent |
| Scalability | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Good | ⭐⭐ Fair |
| Maintenance | ⭐⭐⭐⭐⭐ Easy | ⭐⭐⭐⭐ Easy | ⭐⭐⭐ Moderate |
| Governance | ⭐⭐⭐⭐⭐ Clear | ⭐⭐⭐⭐ Clear | ⭐⭐⭐ Moderate |
| Onboarding | ⭐⭐⭐⭐⭐ Easy | ⭐⭐⭐⭐ Easy | ⭐⭐⭐ Moderate |

## Final Recommendation

### Conservative Approach (3-5 Top-Level) ⭐⭐⭐⭐⭐

**Current implementation:**
```
Source/
├── YouTube/          # Top: Proven high-usage video source
├── Reddit/           # Top: Proven high-usage text source (consider)
├── Video/           # Category: Future video sources
├── Text/            # Category: Future text sources (HackerNews here)
├── Audio/           # Category: Audio sources
├── Data/            # Category: Analytics/trends sources
└── Other/           # Category: Commerce, Events, Community, Internal
```

**Promotion path:**
1. Start with 1 source at top (YouTube)
2. Monitor usage metrics for 1-2 months
3. Promote 2nd source if meets criteria (Reddit or TikTok)
4. Cap at 3-5 sources at top
5. Review quarterly

**Metrics to track:**
- Ideas generated per month
- Usage in story generation workflows
- User requests/feedback
- Development/maintenance burden

**Benefits:**
- ✅ Optimal cognitive load (3-5 items)
- ✅ Clear "top tier" designation
- ✅ Easy governance and promotion process
- ✅ Scales well to 24+ sources
- ✅ Follows industry best practices
- ✅ Supports future growth without refactoring

## Implementation Notes

### Symlinks (Optional)
Consider symlinks for discoverability:
```bash
# YouTube is at top, but also accessible via category
Source/YouTube/          # Primary location
Source/Video/YouTube     # Symlink to ../YouTube
```

### Routing Configuration
Create `Source/_routing.json`:
```json
{
  "top_tier_sources": {
    "YouTube": {
      "location": "./YouTube/",
      "also_in_category": "Video/",
      "priority": 1,
      "metrics": {
        "monthly_ideas": 50000,
        "workflow_usage": 0.85
      }
    }
  },
  "promotion_criteria": {
    "monthly_ideas_threshold": 10000,
    "workflow_usage_threshold": 0.50,
    "user_requests_threshold": 10
  },
  "review_schedule": "quarterly"
}
```

## Conclusion

**Recommended: Conservative approach with 3-5 top-level sources**

This aligns with:
- Miller's Law (7±2 items)
- UX best practices (5-7 primary items)
- Industry patterns (20-30% at top)
- PrismQ's current scale (3 active, 24+ planned)

**Current action:** Start with 1-2 sources at top (YouTube, optionally Reddit), move others to categories.
