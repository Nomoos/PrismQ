# Shallow Hierarchy by Content Type: 5 Alternative Variants

**Date**: 2025-11-11  
**Status**: Alternative Proposals  
**Author**: GitHub Copilot

## Executive Summary

This document presents 5 alternative shallow hierarchy variants organized by **content type** rather than source category. Based on research of content management systems, digital asset management, and media organization best practices, these variants focus on the **nature and format of the content** being collected.

---

## Research: Content Organization Best Practices

### Industry Standards Reviewed

#### 1. **IPTC Media Topics** (International Press Telecommunications Council)
- Standard for categorizing news and media content
- Categories: Arts/Culture, Crime/Law, Disaster/Accident, Economy, Education, Environment, Health, Lifestyle, Politics, Science, Society, Sport, Technology, Weather

#### 2. **Dublin Core Metadata** (Digital Libraries)
- Type vocabulary: Collection, Dataset, Event, Image, InteractiveResource, MovingImage, PhysicalObject, Service, Software, Sound, StillImage, Text

#### 3. **Schema.org Types** (Structured Data)
- CreativeWork hierarchy: Article, AudioObject, ImageObject, VideoObject, WebPage, SocialMediaPosting, Review, Recipe, Course

#### 4. **YouTube Content Categories**
- Film & Animation, Autos & Vehicles, Music, Pets & Animals, Sports, Travel & Events, Gaming, People & Blogs, Comedy, Entertainment, News & Politics, Howto & Style, Education, Science & Technology

#### 5. **Medium/Substack Content Types**
- Story types: Article, Essay, Fiction, Poetry, Review, Interview, Guide, List, News, Opinion

#### 6. **Content Marketing Institute Framework**
- By format: Blog posts, Videos, Podcasts, Infographics, Case studies, Webinars, E-books, Social media, Research reports

#### 7. **DAM (Digital Asset Management) Systems**
- By media type: Text, Image, Video, Audio, Interactive, Mixed
- By purpose: Editorial, Marketing, Product, User-generated

### Key Principles from Research

1. **Format-First Classification** - Group by media type (video, text, audio)
2. **Duration/Length Matters** - Short-form vs long-form is significant
3. **Interaction Model** - Real-time vs asynchronous, live vs recorded
4. **Publication Frequency** - Episodic vs continuous, scheduled vs ad-hoc
5. **Engagement Pattern** - Passive consumption vs active participation
6. **Content Lifecycle** - Ephemeral vs evergreen, trending vs archival

---

## Variant 1: Media Type Classification

**Philosophy**: Organize by fundamental media format (text, video, audio, data)

```
Source/
├── _meta/
├── src/
│
├── Video/                      # Video content sources
│   ├── YouTube/
│   ├── TikTok/
│   ├── Instagram/
│   ├── TwitchClips/
│   └── Vimeo/
│
├── Text/                       # Text-based content sources
│   ├── Reddit/
│   ├── HackerNews/
│   ├── Medium/
│   ├── Twitter/
│   └── Blogs/
│
├── Audio/                      # Audio content sources
│   ├── Spotify/
│   ├── ApplePodcasts/
│   ├── Clubhouse/
│   └── AudioTrends/
│
├── Data/                       # Data and analytics sources
│   ├── GoogleTrends/
│   ├── TwitterHashtag/
│   ├── MemeTracker/
│   ├── NewsAPI/
│   └── Analytics/
│
├── Commerce/                   # E-commerce sources
│   ├── AmazonBestsellers/
│   ├── EtsyTrending/
│   └── AppStoreTopCharts/
│
├── Events/                     # Event-based sources
│   ├── CalendarHolidays/
│   ├── SportsHighlights/
│   └── EntertainmentReleases/
│
├── Community/                  # Community interaction sources
│   ├── QASource/
│   ├── CommentMining/
│   └── UserFeedback/
│
└── Internal/                   # Internal tools
    ├── CSVImport/
    └── ManualBacklog/
```

### Characteristics
- **Primary criterion**: Media format (what kind of content)
- **8 top-level categories**: Video, Text, Audio, Data, Commerce, Events, Community, Internal
- **Clear boundaries**: No ambiguity about where sources belong
- **Format-agnostic platforms**: Multi-format sources can appear in multiple categories or primary one

### Advantages
✅ **Intuitive for content creators** - Natural mental model (making videos? check Video/)  
✅ **Technical consistency** - Similar processing pipelines per media type  
✅ **Skill-based teams** - Video team, text team, data team  
✅ **Clear API contracts** - Each media type has standard interfaces  
✅ **Easy to explain** - "Where do video sources go? Video/"  

### Disadvantages
❌ **Multi-format platforms** - Where does Instagram go? (Video + Image + Stories)  
❌ **Ignores content purpose** - News video vs entertainment video both in Video/  
❌ **Missing semantic context** - What's the source about?  
❌ **Trend sources scattered** - Twitter text vs TikTok video both track trends  

### Best For
- Teams organized by media expertise (video editors, writers, data analysts)
- Technical processing pipelines differ by format
- Content production workflow matches format types
- Clear separation of media handling code

---

## Variant 2: Content Duration/Format Classification

**Philosophy**: Organize by content length and consumption pattern (micro, short, long, live, periodic)

```
Source/
├── _meta/
├── src/
│
├── Micro/                      # Micro-content (< 3 min, quick consumption)
│   ├── TikTok/
│   ├── InstagramReels/
│   ├── YouTubeShorts/
│   ├── TwitterPosts/
│   └── TwitchClips/
│
├── Short/                      # Short-form (3-20 min, focused consumption)
│   ├── YouTubeVideos/
│   ├── MediumArticles/
│   ├── RedditPosts/
│   ├── HackerNews/
│   └── BlogPosts/
│
├── Long/                       # Long-form (20+ min, deep engagement)
│   ├── Podcasts/
│   ├── Documentaries/
│   ├── LongArticles/
│   ├── Courses/
│   └── Webinars/
│
├── Live/                       # Live/real-time content
│   ├── TwitchStreams/
│   ├── YouTubeLive/
│   ├── TwitterSpaces/
│   └── LiveEvents/
│
├── Periodic/                   # Scheduled/episodic content
│   ├── PodcastEpisodes/
│   ├── TVShows/
│   ├── Newsletters/
│   └── SeriesContent/
│
├── Trending/                   # Trending and viral content
│   ├── GoogleTrends/
│   ├── TrendingHashtags/
│   ├── ViralMemes/
│   ├── TrendingTopics/
│   └── BreakingNews/
│
├── Evergreen/                  # Timeless, archival content
│   ├── WikiContent/
│   ├── Tutorials/
│   ├── References/
│   └── GuidesHowTos/
│
├── Commerce/                   # Commercial content
│   ├── ProductReviews/
│   ├── Bestsellers/
│   └── Marketplace/
│
├── Community/                  # User-generated Q&A
│   ├── QAForums/
│   ├── UserComments/
│   └── Feedback/
│
└── Internal/                   # Internal tools
    ├── CSVImport/
    └── ManualBacklog/
```

### Characteristics
- **Primary criterion**: Content length and temporal characteristics
- **10 top-level categories**: Micro, Short, Long, Live, Periodic, Trending, Evergreen, Commerce, Community, Internal
- **Consumption-focused**: Organized by how users engage with content
- **Temporal dimension**: Ephemeral vs lasting, scheduled vs spontaneous

### Advantages
✅ **User behavior alignment** - Matches how people consume content  
✅ **Content strategy clarity** - Different strategies for micro vs long-form  
✅ **Production planning** - Different workflows for each duration type  
✅ **Recommendation engine** - Easy to build "more like this" features  
✅ **Trend identification** - Trending sources grouped together  

### Disadvantages
❌ **Platform ambiguity** - YouTube has micro, short, long, and live  
❌ **Subjective boundaries** - What's "short" vs "long"?  
❌ **Evolving definitions** - Attention spans change over time  
❌ **Mixed content** - Single source can have multiple durations  

### Best For
- Content recommendation systems
- Audience attention span optimization
- Production schedules based on content length
- User experience design around consumption patterns

---

## Variant 3: Engagement Type Classification

**Philosophy**: Organize by how users interact with content (passive, active, collaborative, transactional)

```
Source/
├── _meta/
├── src/
│
├── Consume/                    # Passive consumption
│   ├── StreamingVideo/
│   │   ├── YouTube/
│   │   ├── TikTok/
│   │   └── Vimeo/
│   ├── ReadingContent/
│   │   ├── Medium/
│   │   ├── Blogs/
│   │   └── NewsArticles/
│   └── ListeningContent/
│       ├── Podcasts/
│       └── AudioBooks/
│
├── Discuss/                    # Active discussion/interaction
│   ├── Forums/
│   │   ├── Reddit/
│   │   ├── HackerNews/
│   │   └── StackOverflow/
│   ├── SocialMedia/
│   │   ├── Twitter/
│   │   └── Facebook/
│   └── Comments/
│       └── CommentSections/
│
├── Discover/                   # Discovery and exploration
│   ├── Trending/
│   │   ├── GoogleTrends/
│   │   ├── TrendingTopics/
│   │   └── ViralContent/
│   ├── Explore/
│   │   ├── SearchData/
│   │   └── Recommendations/
│   └── Curated/
│       └── EditorialPicks/
│
├── Create/                     # User-generated creation prompts
│   ├── Inspiration/
│   │   ├── VisualMoodboard/
│   │   ├── LyricSnippets/
│   │   └── ScriptBeats/
│   └── Templates/
│       └── CreativePrompts/
│
├── Shop/                       # Transactional/commercial
│   ├── Marketplace/
│   │   ├── Amazon/
│   │   └── Etsy/
│   └── AppStores/
│       └── AppStoreCharts/
│
├── Schedule/                   # Calendar-based/temporal
│   ├── Events/
│   │   ├── CalendarHolidays/
│   │   └── SportingEvents/
│   └── Releases/
│       └── EntertainmentReleases/
│
├── Learn/                      # Educational content
│   ├── Tutorials/
│   ├── Courses/
│   └── Documentation/
│
├── Feedback/                   # User feedback mechanisms
│   ├── QA/
│   ├── Reviews/
│   └── UserFeedback/
│
└── Internal/                   # Internal tools
    ├── CSVImport/
    └── ManualBacklog/
```

### Characteristics
- **Primary criterion**: User interaction model
- **9 top-level categories**: Consume, Discuss, Discover, Create, Shop, Schedule, Learn, Feedback, Internal
- **Action-oriented**: Verbs describe what users do
- **UX-focused**: Maps to user journeys and workflows

### Advantages
✅ **User journey mapping** - Aligns with how users interact  
✅ **Feature development** - Clear buckets for new features  
✅ **Analytics natural grouping** - Track engagement by type  
✅ **Product thinking** - Matches product management frameworks  
✅ **Cross-functional teams** - Teams own user journeys  

### Disadvantages
❌ **Complex classification** - YouTube users consume AND discuss AND discover  
❌ **Overlapping categories** - Same source fits multiple buckets  
❌ **Implementation complexity** - Need multi-category support  
❌ **Less technical clarity** - Doesn't help with processing logic  

### Best For
- Product-led organizations
- User experience design focus
- Cross-functional team structures
- Customer journey optimization

---

## Variant 4: Content Topic/Domain Classification

**Philosophy**: Organize by subject matter and domain (news, entertainment, education, lifestyle)

```
Source/
├── _meta/
├── src/
│
├── News/                       # News and current events
│   ├── BreakingNews/
│   │   ├── NewsAPI/
│   │   └── GoogleNews/
│   ├── SocialDiscussion/
│   │   ├── Reddit/
│   │   ├── HackerNews/
│   │   └── Twitter/
│   └── TrendAnalysis/
│       ├── GoogleTrends/
│       └── TrendingTopics/
│
├── Entertainment/              # Entertainment content
│   ├── VideoContent/
│   │   ├── YouTube/
│   │   ├── TikTok/
│   │   └── TwitchClips/
│   ├── Music/
│   │   ├── Spotify/
│   │   └── SoundTrends/
│   └── Events/
│       ├── SportsHighlights/
│       └── EntertainmentReleases/
│
├── Education/                  # Educational content
│   ├── Tutorials/
│   │   └── YouTubeTutorials/
│   ├── Articles/
│   │   └── MediumEducation/
│   ├── Courses/
│   │   └── OnlineCourses/
│   └── Documentation/
│       └── TechnicalDocs/
│
├── Lifestyle/                  # Lifestyle and culture
│   ├── Fashion/
│   │   └── InstagramFashion/
│   ├── Food/
│   │   └── RecipeContent/
│   ├── Travel/
│   │   └── TravelContent/
│   └── Wellness/
│       └── HealthContent/
│
├── Business/                   # Business and commerce
│   ├── Commerce/
│   │   ├── AmazonBestsellers/
│   │   ├── EtsyTrending/
│   │   └── AppStoreTopCharts/
│   ├── Finance/
│   │   └── FinancialNews/
│   └── Marketing/
│       └── AdTrends/
│
├── Technology/                 # Tech and innovation
│   ├── TechNews/
│   │   └── HackerNews/
│   ├── ProductLaunches/
│   │   └── ProductHunt/
│   └── Development/
│       └── GitHubTrending/
│
├── Culture/                    # Pop culture and trends
│   ├── Memes/
│   │   └── MemeTracker/
│   ├── Viral/
│   │   └── ViralContent/
│   └── Challenges/
│       └── SocialChallenges/
│
├── Community/                  # Community engagement
│   ├── QA/
│   │   └── QASource/
│   ├── Feedback/
│   │   └── UserFeedback/
│   └── Comments/
│       └── CommentMining/
│
├── Seasonal/                   # Time-based content
│   ├── Holidays/
│   │   └── CalendarHolidays/
│   └── Events/
│       └── SeasonalEvents/
│
└── Internal/                   # Internal tools
    ├── CSVImport/
    └── ManualBacklog/
```

### Characteristics
- **Primary criterion**: Subject matter and topic domain
- **10 top-level categories**: News, Entertainment, Education, Lifestyle, Business, Technology, Culture, Community, Seasonal, Internal
- **Editorial focus**: How content publishers categorize
- **Topic-driven**: What is the content about?

### Advantages
✅ **Editorial clarity** - Matches how media orgs think  
✅ **Content strategy** - Different strategies per topic  
✅ **SEO-friendly** - Topics map to search keywords  
✅ **Audience segmentation** - Clear user personas per topic  
✅ **Partnerships** - Easy to explain to content partners  

### Disadvantages
❌ **Subjective classification** - What's "lifestyle" vs "entertainment"?  
❌ **Multi-topic sources** - YouTube has all topics  
❌ **Overlap issues** - Tech entertainment vs business tech  
❌ **Requires editorial judgment** - Not purely technical  

### Best For
- Media and publishing organizations
- Content marketing teams
- Editorial workflows
- Audience-specific content strategies

---

## Variant 5: Source Velocity/Freshness Classification

**Philosophy**: Organize by content update frequency and time-sensitivity (real-time, daily, periodic, static)

```
Source/
├── _meta/
├── src/
│
├── RealTime/                   # Real-time streaming (< 1 hour updates)
│   ├── LiveStreams/
│   │   ├── TwitchLive/
│   │   └── YouTubeLive/
│   ├── SocialFeeds/
│   │   ├── TwitterFeed/
│   │   └── InstagramStories/
│   ├── LiveTrends/
│   │   ├── GoogleTrendsLive/
│   │   └── TrendingNow/
│   └── BreakingNews/
│       └── NewsAPILive/
│
├── Hourly/                     # High-frequency updates (1-6 hours)
│   ├── SocialPosts/
│   │   ├── Reddit/
│   │   ├── HackerNews/
│   │   └── TwitterPosts/
│   ├── ShortVideo/
│   │   ├── TikTok/
│   │   ├── YouTubeShorts/
│   │   └── InstagramReels/
│   └── NewsUpdates/
│       └── NewsFeed/
│
├── Daily/                      # Daily content (6-24 hours)
│   ├── DailyVideo/
│   │   └── YouTubeDaily/
│   ├── DailyArticles/
│   │   └── MediumDaily/
│   ├── DailyPodcasts/
│   │   └── SpotifyNew/
│   ├── DailyTrends/
│   │   └── TrendingDaily/
│   └── DailyMemes/
│       └── MemeTrackerDaily/
│
├── Weekly/                     # Weekly content (1-7 days)
│   ├── WeeklyReports/
│   │   └── TrendReports/
│   ├── WeeklyCharts/
│   │   ├── MusicCharts/
│   │   └── AppStoreWeekly/
│   ├── WeeklySeries/
│   │   └── PodcastEpisodes/
│   └── WeeklyRoundup/
│       └── WeeklyHighlights/
│
├── Monthly/                    # Monthly content
│   ├── MonthlyReports/
│   ├── MonthlyBestsellers/
│   │   ├── AmazonMonthly/
│   │   └── EtsyMonthly/
│   └── MonthlyAnalytics/
│
├── Seasonal/                   # Seasonal/scheduled content
│   ├── Holidays/
│   │   └── CalendarHolidays/
│   ├── Sports/
│   │   └── SportingEvents/
│   ├── Entertainment/
│   │   └── EntertainmentReleases/
│   └── SeasonalTrends/
│
├── Evergreen/                  # Static/rarely updated
│   ├── Tutorials/
│   ├── Documentation/
│   ├── Guides/
│   └── Reference/
│
├── UserGenerated/              # User-submitted (variable)
│   ├── QA/
│   │   └── QASource/
│   ├── Feedback/
│   │   └── UserFeedback/
│   └── Comments/
│       └── CommentMining/
│
└── Internal/                   # Internal tools
    ├── CSVImport/
    └── ManualBacklog/
```

### Characteristics
- **Primary criterion**: Update frequency and time-sensitivity
- **9 top-level categories**: RealTime, Hourly, Daily, Weekly, Monthly, Seasonal, Evergreen, UserGenerated, Internal
- **Temporal focus**: When content changes
- **Processing implications**: Different polling/webhook strategies

### Advantages
✅ **Processing optimization** - Different refresh rates per category  
✅ **Resource allocation** - More resources to real-time sources  
✅ **SLA clarity** - Clear expectations for freshness  
✅ **Caching strategy** - Easy to determine cache TTLs  
✅ **Infrastructure planning** - Scale by velocity needs  

### Disadvantages
❌ **Velocity changes** - Source update frequency can change  
❌ **Mixed frequencies** - Single source may have multiple update patterns  
❌ **Not semantic** - Doesn't describe what content is  
❌ **Implementation-focused** - More about tech than content  

### Best For
- Infrastructure and DevOps teams
- Performance optimization focus
- Resource-constrained environments
- SLA-driven organizations

---

## Comparison Matrix: 5 Variants

| Criteria | V1: Media Type | V2: Duration | V3: Engagement | V4: Topic | V5: Velocity |
|----------|----------------|--------------|----------------|-----------|--------------|
| **Intuitive** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Clear Boundaries** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Scalable** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Technical Clarity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Editorial Use** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **User-Centric** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **Multi-Category** | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Migration Effort** | ⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐ |

---

## Top 3 Recommendations

### 🥇 Recommendation #1: Variant 1 (Media Type)

**Why This is Best for Content-First Organization:**

1. **Clearest boundaries** - No ambiguity about video vs text vs audio
2. **Technical consistency** - Processing pipelines align with categories
3. **Team structure** - Natural division of responsibilities
4. **Simple mental model** - Everyone understands media types
5. **Future-proof** - New platforms fit easily (new video app → Video/)

**Recommended Structure:**
```
Source/
├── Video/          # YouTube, TikTok, Instagram, Twitch (8-12 sources)
├── Text/           # Reddit, HackerNews, Medium, Twitter (6-10 sources)
├── Audio/          # Podcasts, Spotify, Audio trends (3-5 sources)
├── Data/           # Trends, analytics, signals (6-8 sources)
├── Commerce/       # Marketplaces (3-4 sources)
├── Events/         # Calendar-based (2-3 sources)
├── Community/      # Q&A, feedback (2-3 sources)
└── Internal/       # Tools (2-3 sources)
```

**Best For**: Teams organized by media expertise, technical processing focus

---

### 🥈 Recommendation #2: Variant 4 (Topic/Domain)

**Why This Works for Editorial Focus:**

1. **Content strategy clarity** - Different strategies per topic domain
2. **Audience alignment** - Clear user personas per category
3. **SEO benefits** - Topics match search intent
4. **Partnership friendly** - Easy to explain to content partners
5. **Media org alignment** - How publishers think about content

**Recommended Structure:**
```
Source/
├── News/           # News, discussions, trends (6-8 sources)
├── Entertainment/  # Video, music, events (8-10 sources)
├── Education/      # Tutorials, courses (3-4 sources)
├── Lifestyle/      # Fashion, food, wellness (4-6 sources)
├── Business/       # Commerce, finance (4-6 sources)
├── Technology/     # Tech news, products (3-4 sources)
├── Culture/        # Memes, viral, challenges (3-4 sources)
├── Community/      # Q&A, feedback (2-3 sources)
└── Seasonal/       # Holidays, events (2-3 sources)
```

**Best For**: Media organizations, editorial teams, content marketing

---

### 🥉 Recommendation #3: Variant 2 (Duration/Format)

**Why This is Interesting for UX Focus:**

1. **User behavior match** - How people consume content
2. **Recommendation engine** - Easy similarity matching
3. **Production planning** - Different workflows per duration
4. **Trend identification** - Trending sources grouped
5. **Attention optimization** - Design for consumption patterns

**Recommended Structure:**
```
Source/
├── Micro/          # < 3 min: TikTok, Shorts, Tweets (6-8 sources)
├── Short/          # 3-20 min: YouTube, Reddit, Articles (8-10 sources)
├── Long/           # 20+ min: Podcasts, documentaries (4-5 sources)
├── Live/           # Real-time: Streams, live events (3-4 sources)
├── Trending/       # Trending content (4-6 sources)
├── Commerce/       # Commercial (3-4 sources)
├── Community/      # Q&A (2-3 sources)
└── Internal/       # Tools (2-3 sources)
```

**Best For**: User experience focus, recommendation systems, product teams

---

## Implementation Recommendation for PrismQ

**Recommended: Variant 1 (Media Type)** ⭐

**Rationale:**
1. ✅ **Clearest classification** - No ambiguity about where sources go
2. ✅ **Technical alignment** - Processing logic matches media types
3. ✅ **Team structure** - Can assign video team, text team, data team
4. ✅ **Scalability** - New video platforms go in Video/, simple
5. ✅ **Current sources fit naturally**:
   - YouTube, TikTok, Instagram → Video/
   - Reddit, HackerNews, Medium → Text/
   - Podcasts, Spotify → Audio/
   - GoogleTrends, hashtags → Data/

**Alternative: Variant 4 (Topic/Domain)** - If editorial/content strategy is primary focus

**Migration Example for Variant 1:**
```bash
# Create structure
mkdir -p Source/{Video,Text,Audio,Data,Commerce,Events,Community,Internal}

# Move existing sources
git mv Source/YouTube Source/Video/
git mv Source/Reddit Source/Text/
git mv Source/HackerNews Source/Text/

# Future sources
# TikTok → Source/Video/TikTok/
# GoogleTrends → Source/Data/GoogleTrends/
# Spotify → Source/Audio/Spotify/
```

---

## Conclusion

All 5 variants are valid approaches with different strengths:

- **Variant 1 (Media Type)**: Best for technical teams, clearest boundaries ⭐
- **Variant 2 (Duration)**: Best for UX/product teams, consumption focus
- **Variant 3 (Engagement)**: Best for product-led orgs, user journey focus
- **Variant 4 (Topic)**: Best for editorial teams, content strategy focus ⭐
- **Variant 5 (Velocity)**: Best for infrastructure teams, performance focus

**For PrismQ**, **Variant 1 (Media Type)** is recommended as the best balance of clarity, technical alignment, and scalability for a content generation platform.

---

## Next Steps

1. **Review** all 5 variants with stakeholders
2. **Consider** primary use case: technical processing vs editorial vs UX
3. **Decide** which variant best fits team structure and goals
4. **Prototype** with a few sources to validate
5. **Document** chosen structure and rationale
6. **Migrate** existing sources
7. **Establish** guidelines for future source placement

## References

- IPTC Media Topics Standard
- Dublin Core Metadata Initiative
- Schema.org Structured Data Types
- Content Marketing Institute Framework
- Digital Asset Management Best Practices
- UX Content Organization Patterns
- YouTube/Medium/Substack Category Systems
