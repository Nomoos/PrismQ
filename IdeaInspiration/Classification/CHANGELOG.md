# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2025-11-13

### Added

#### Worker Architecture for Distributed Processing
- **Worker Infrastructure**: Complete worker implementation for TaskManager API integration
  - `ClassificationWorker`: Main worker class for processing classification tasks
  - `WorkerFactory`: Factory pattern for creating worker instances (Open/Closed Principle)
  - Worker protocols and data types (`Task`, `TaskResult`, `TaskStatus`)
  - Support for single and batch classification tasks

#### TaskManager API Integration
- Task type registration for classification operations
  - `PrismQ.Classification.ContentEnrich`: Single content classification
  - `PrismQ.Classification.BatchEnrich`: Batch classification
- Configurable claiming policies (FIFO, LIFO, PRIORITY)
- Exponential backoff for empty queues
- Graceful shutdown and statistics tracking

#### Scripts and Tools
- `scripts/run_worker.py`: Worker launcher with comprehensive CLI options
- `scripts/register_task_types.py`: Task type registration utility
- Support for custom worker IDs, polling intervals, and backoff strategies

#### Documentation
- Comprehensive Worker README with architecture diagrams
- Example worker usage (`_meta/examples/example_worker.py`)
- Updated main README with worker information

#### Tests
- Worker functionality tests (all passing)
- Factory pattern tests
- Integration tests with IdeaInspiration database

### Changed
- Fixed Model import paths to use correct directory structure
- Updated dependencies to include `click` and `python-dotenv`
- Added worker optional dependencies to `pyproject.toml`

### Fixed
- Database integration to use `get_by_id` and insert-only model
- Path resolution for worker imports
- Import handling for optional TaskManager dependency

## [2.1.0] - 2025-10-13

### Added

#### Generalized Text Classification System
- **IdeaInspiration Model**: Unified data structure for representing content across text, video, and audio sources
  - Support for title, description, content (body/subtitles/transcription), keywords, metadata
  - Source type detection (text, video, audio)
  - Conversion to/from dictionaries for serialization
  - Combined text access via `all_text` property

#### Extract Pattern (IdeaInspirationExtractor)
- `extract_from_text()`: Extract from text content with body text
- `extract_from_video()`: Extract from video with subtitle text
- `extract_from_audio()`: Extract from audio with transcription
- `extract_from_metadata()`: Auto-detect content type from metadata dictionary
- Basic keyword extraction from tags (with hashtag cleaning)
- Simple keyword extraction from text using word frequency and stop words

#### Builder Pattern (IdeaInspirationBuilder)
- Fluent API for step-by-step construction of IdeaInspiration objects
- Chainable methods: `set_title()`, `set_description()`, `set_content()`, etc.
- Keyword management: `add_keyword()`, `add_keywords()`, `set_keywords()`
- Automatic keyword extraction from content with `extract_keywords_from_content()`
- Population from metadata dictionaries with `from_metadata_dict()`
- Validation before building
- Reusable builder with `reset()` method

#### TextClassifier
- Unified classification interface for IdeaInspiration objects
- Integrates CategoryClassifier and StoryDetector
- Field-level scoring for title, description, content, and keywords
- Combined confidence score calculation
- Batch classification support with `classify_batch()`
- Direct field classification with `classify_text_fields()`
- TextClassificationResult with detailed scoring information

#### Documentation
- New comprehensive guide: `_meta/doc/GENERALIZED_CLASSIFICATION.md`
  - Architecture overview
  - Usage examples for all patterns
  - Use cases (YouTube Shorts, podcasts, batch processing)
  - Migration guide from v2.0
  - Best practices and performance considerations
- New example script: `example_generalized.py` with 8 working examples
- Updated README with new features and usage examples

#### Testing
- 48 new tests added across 4 test files:
  - `test_idea_inspiration.py`: 10 tests for data model
  - `test_extract.py`: 11 tests for extraction patterns
  - `test_builder.py`: 17 tests for builder pattern
  - `test_text_classifier.py`: 10 tests for unified classifier
- Total: 96 tests with 97% code coverage
- All tests passing

### Changed
- Updated package version to 2.1.0
- Updated package description to reflect generalized text analysis
- Updated `__init__.py` exports to include new modules
- Enhanced README with new feature sections

### Maintained
- **100% Backward Compatibility**: All existing CategoryClassifier and StoryDetector APIs work exactly as before
- **Zero External Dependencies**: All new functionality uses Python standard library only
- **Local Processing**: No external API calls, maintains local-first approach
- All existing 48 tests still passing

## [2.0.0] - 2025-10-13 (Previous Release)

### Added
- CategoryClassifier with 8 primary categories
- StoryDetector for binary story classification
- Comprehensive test suite (48 tests)
- Complete documentation and examples
- Platform-agnostic design for all PrismQ content sources

## Future Enhancements

Potential additions being researched:
- Integration with local AI models (Hugging Face Transformers, spaCy)
- Transformer-based keyword extraction
- Semantic similarity for better classification
- Local embedding models for content understanding
- Multi-language support
- Advanced NLP features using local models

---

For more details, see the [documentation](_meta/doc/GENERALIZED_CLASSIFICATION.md) or run `python example_generalized.py`.
