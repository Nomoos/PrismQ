# Source Grouping Proposal

**Date**: 2025-11-11  
**Status**: Proposal  
**Author**: GitHub Copilot

## Overview

This document proposes a new organizational structure for the `Source/` directory based on analysis of the legacy `Legacy_Reference/` structure. The goal is to maintain the proven categorization system while adapting it to the modern, cleaner architecture.

## Current State

### Source/ (Modern - 3 sources)
```
Source/
├── YouTube/
├── HackerNews/
└── Reddit/
```

### Legacy_Reference/ (Legacy - 27+ sources)
Organized into 7 main categories with clear grouping:
- **Content** (Shorts, Forums, Articles, Podcasts, Streams)
- **Signals** (Trends, Hashtags, News, Memes, Sounds, Challenges, Locations)
- **Creative** (LyricSnippets, ScriptBeats, VisualMoodboard)
- **Events** (CalendarHolidays, SportsHighlights, EntertainmentReleases)
- **Commerce** (AmazonBestsellers, AppStoreTopCharts, EtsyTrending)
- **Community** (QASource, CommentMining, UserFeedback, PromptBox)
- **Internal** (CSVImport, ManualBacklog)

## Proposed Structure

### Option 1: Flat with Category Prefixes (Minimal Change)
Keep the current flat structure but use consistent naming that implies categories:

```
Source/
├── Content_YouTube/
├── Content_HackerNews/
├── Content_Reddit/
├── Content_TikTok/          # Future
├── Content_Instagram/       # Future
├── Signals_GoogleTrends/    # Future
├── Signals_TikTokHashtag/   # Future
└── ...
```

**Pros:**
- Minimal disruption to current structure
- Easy to navigate alphabetically
- Clear category identification

**Cons:**
- Doesn't scale well with many sources (flat namespace)
- Less intuitive directory browsing
- Category benefits not fully realized

### Option 2: Hierarchical Categories (Recommended)
Adopt the proven legacy category structure with modern architecture:

```
Source/
├── Content/                    # Content sources (articles, videos, social)
│   ├── Shorts/                 # Short-form video content
│   │   ├── YouTube/           # ✓ Already exists
│   │   ├── TikTok/            # Future
│   │   └── Instagram/         # Future
│   │
│   ├── Forums/                 # Discussion platforms
│   │   ├── HackerNews/        # ✓ Already exists
│   │   └── Reddit/            # ✓ Already exists
│   │
│   ├── Articles/               # Long-form content
│   │   ├── Medium/            # Future
│   │   └── WebArticles/       # Future
│   │
│   ├── Podcasts/               # Audio content
│   │   ├── Spotify/           # Future
│   │   └── ApplePodcasts/     # Future
│   │
│   └── Streams/                # Live streaming clips
│       ├── TwitchClips/       # Future
│       └── KickClips/         # Future
│
├── Signals/                    # Trend and signal sources
│   ├── Trends/                 # Market and search trends
│   │   ├── GoogleTrends/      # Future
│   │   └── TrendsFile/        # Future
│   │
│   ├── Hashtags/               # Social media hashtags
│   │   ├── TikTokHashtag/     # Future
│   │   └── InstagramHashtag/  # Future
│   │
│   ├── News/                   # News aggregators
│   │   ├── GoogleNews/        # Future
│   │   └── NewsApi/           # Future
│   │
│   ├── Memes/                  # Meme tracking
│   │   ├── MemeTracker/       # Future
│   │   └── KnowYourMeme/      # Future
│   │
│   ├── Sounds/                 # Audio trends
│   │   ├── TikTokSounds/      # Future
│   │   └── InstagramAudio/    # Future
│   │
│   ├── Challenges/             # Social challenges
│   │   └── SocialChallenge/   # Future
│   │
│   └── Locations/              # Geo-based trends
│       └── GeoLocalTrends/    # Future
│
├── Creative/                   # Creative inspiration sources
│   ├── LyricSnippets/         # Future
│   ├── ScriptBeats/           # Future
│   └── VisualMoodboard/       # Future
│
├── Events/                     # Event-based sources
│   ├── CalendarHolidays/      # Future
│   ├── SportsHighlights/      # Future
│   └── EntertainmentReleases/ # Future
│
├── Commerce/                   # E-commerce trends
│   ├── AmazonBestsellers/     # Future
│   ├── AppStoreTopCharts/     # Future
│   └── EtsyTrending/          # Future
│
├── Community/                  # Community-driven sources
│   ├── QASource/              # Future
│   ├── CommentMining/         # Future
│   ├── UserFeedback/          # Future
│   └── PromptBox/             # Future
│
└── Internal/                   # Internal tools and utilities
    ├── CSVImport/             # Future
    └── ManualBacklog/         # Future
```

**Pros:**
- ✅ Proven structure from legacy sources
- ✅ Scales well (24+ sources organized cleanly)
- ✅ Clear semantic grouping
- ✅ Easy to find related sources
- ✅ Supports future expansion
- ✅ Aligns with documented taxonomy

**Cons:**
- Requires moving existing sources (YouTube, HackerNews, Reddit)
- More directory depth
- Initial migration effort

### Option 3: Hybrid Approach
Keep high-traffic sources at root, categorize new ones:

```
Source/
├── YouTube/              # Popular sources stay flat
├── Reddit/
├── HackerNews/
└── categories/           # New sources go in categories
    ├── Content/
    ├── Signals/
    └── ...
```

**Pros:**
- No migration of existing sources
- Allows gradual adoption

**Cons:**
- Inconsistent structure
- Confusing for contributors
- Defeats purpose of categorization

## Recommendation: Option 2 (Hierarchical Categories)

### Rationale

1. **Proven Success**: The legacy sources used this structure successfully for 24+ sources
2. **Scalability**: Already planning to support 24+ source types according to documentation
3. **Discovery**: Users can browse by category to find similar sources
4. **Maintenance**: Easier to maintain related sources together
5. **Documentation**: Categories provide natural documentation boundaries
6. **Standards**: Aligns with industry best practices for large codebases

### Migration Plan

#### Phase 1: Create Category Structure (No Breaking Changes)
1. Create category directories: `Content/`, `Signals/`, etc.
2. Add category-level `README.md` files explaining each category
3. Add category-level `_meta/` directories for shared documentation

#### Phase 2: Move Existing Sources
1. Move `YouTube/` → `Content/Shorts/YouTube/`
2. Move `HackerNews/` → `Content/Forums/HackerNews/`
3. Move `Reddit/` → `Content/Forums/Reddit/`
4. Update all imports and references
5. Add symlinks at root for backward compatibility (optional)

#### Phase 3: Document and Test
1. Update main `Source/README.md` with new structure
2. Update documentation references
3. Test all imports and functionality
4. Update CI/CD pipelines if needed

#### Phase 4: Add New Sources to Categories
All future sources follow the category structure from day one.

## Category Descriptions

### Content
**Purpose**: Sources that provide consumable content (videos, articles, posts)  
**Examples**: YouTube, TikTok, Reddit, Medium, Podcasts  
**Use Case**: Direct content ideas for video production

### Signals
**Purpose**: Sources that track trends, movements, and signals in the market  
**Examples**: Google Trends, hashtags, news, memes, viral sounds  
**Use Case**: Identify trending topics before they peak

### Creative
**Purpose**: Sources providing creative inspiration and building blocks  
**Examples**: Lyric snippets, script beats, visual moodboards  
**Use Case**: Overcome creative blocks with pre-generated elements

### Events
**Purpose**: Sources tied to calendar events and schedules  
**Examples**: Holidays, sports events, movie releases  
**Use Case**: Plan content around scheduled events

### Commerce
**Purpose**: Sources tracking e-commerce and marketplace trends  
**Examples**: Amazon bestsellers, app store charts, Etsy trends  
**Use Case**: Identify product-based content opportunities

### Community
**Purpose**: Sources gathering community feedback and questions  
**Examples**: Q&A platforms, comment mining, user feedback  
**Use Case**: Address audience questions and concerns

### Internal
**Purpose**: Internal tools and manual input systems  
**Examples**: CSV import, manual backlog entry  
**Use Case**: Support custom data entry and migration

## Implementation Considerations

### Backward Compatibility
- Consider adding symlinks at root level during transition period
- Update all documentation with both old and new paths
- Add deprecation notices to old paths

### Import Paths
Python imports would change from:
```python
from Source.YouTube import YouTubeSource
```

To:
```python
from Source.Content.Shorts.YouTube import YouTubeSource
```

Or with proper `__init__.py` configuration:
```python
from Source.Content.Shorts import YouTubeSource
```

### Documentation Structure
Each category should have:
- `Category/README.md` - Overview of category and its sources
- `Category/_meta/docs/` - Category-specific architecture docs
- `Category/_meta/examples/` - Cross-source examples within category

## Next Steps

1. **Review**: Get stakeholder feedback on this proposal
2. **Decision**: Choose Option 1, 2, or 3
3. **Plan**: Create detailed migration plan if Option 2 is chosen
4. **Execute**: Implement in phases to minimize disruption
5. **Document**: Update all documentation to reflect new structure

## Questions for Discussion

1. Is the categorization granular enough? (e.g., separate Shorts from other Content?)
2. Should we have a transition period with both structures?
3. Are there additional categories we should plan for?
4. How do we handle sources that could fit multiple categories?
5. Should we prioritize certain categories for migration first?

## References

- Legacy structure: `/Legacy_Reference/`
- Current structure: `/Source/`
- Documentation: `/Legacy_Reference/README.md`
- Architecture: `/_meta/docs/ARCHITECTURE.md`
