# PrismQ.IdeaInspiration.Model

Core data model and database setup for content ideas across the PrismQ ecosystem.

## ✨ Highlights

- **Unified data model** - Single `IdeaInspiration` structure for text, video, and audio
- **Factory methods** - Easy creation from different content sources
- **Database automation** - One-command SQLite database setup
- **Blending support** - Combine multiple inspirations (M:N relationship with Idea model)
- **Zero dependencies** - Pure Python implementation
- **Type-safe** - Full type hints support
- **Well tested** - Comprehensive test coverage

## 🚀 Quick Start

```bash
# Setup database (Windows)
.\setup_db.ps1

# Setup database (Linux/macOS)
./setup_db.sh

# Basic usage
python -c "from idea_inspiration import IdeaInspiration; print('OK')"
```

## 📚 Documentation

- **[Setup Guide](./docs/SETUP.md)** - Database setup and installation
- **[User Guide](./docs/USER_GUIDE.md)** - Complete usage examples and features
- **[Contributing](./_meta/docs/CONTRIBUTING.md)** - Development guidelines

## 🔗 Related

- [Main Repository](../) - PrismQ.IdeaInspiration overview
- [Classification Module](../Classification/) - Uses this model for content classification
- [Scoring Module](../Scoring/) - Uses this model for content scoring
- [Sources Module](../Sources/) - Uses this model for source integrations

## 📄 License

Proprietary - All Rights Reserved
