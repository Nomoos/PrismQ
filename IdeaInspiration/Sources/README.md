# PrismQ.IdeaInspiration.Sources

Comprehensive library for collecting content from diverse platforms using a unified database architecture.

## ✨ Highlights

- **24 source integrations** - YouTube, Reddit, Google Trends, TikTok, and more
- **Single database pattern** - All sources save to one central database
- **Plugin architecture** - Modular, extensible source implementations
- **Unified data model** - All sources return standard `IdeaInspiration` objects
- **SOLID principles** - Clean, maintainable, testable code
- **Platform identification** - `source_platform` field for filtering

## 🚀 Quick Start

```bash
# Example: Run Google Trends source
cd Sources/Signals/GoogleTrends
pip install -e .
python -m google_trends_source
```

## 📦 Source Categories

| Category | Sources | Count |
|----------|---------|-------|
| **Signals** | Google Trends, TikTok Hashtag, News API, Memes, etc. | 12 |
| **Creative** | Lyric Snippets, Script Beats, Visual Moodboard | 3 |
| **Events** | Calendar Holidays, Sports, Entertainment Releases | 3 |
| **Commerce** | Amazon Bestsellers, App Store, Etsy Trending | 3 |
| **Community** | QA Source, Comment Mining, User Feedback | 4 |
| **Internal** | CSV Import, Manual Backlog | 2 |

## 📚 Documentation

- **[Source Architecture](./_meta/docs/README.md)** - Architecture and implementation patterns
- **[Contributing](./_meta/docs/CONTRIBUTING.md)** - How to add new sources
- **Individual Source READMEs** - See each source directory for specific usage

## 🔗 Related

- [Main Repository](../) - PrismQ.IdeaInspiration overview
- [Model Module](../Model/) - IdeaInspiration data model used by all sources
- [Classification Module](../Classification/) - Categorize collected content
- [Scoring Module](../Scoring/) - Score collected content

## 📄 License

Proprietary - All Rights Reserved
