# Implement Internal Category Sources

**Type**: Feature
**Priority**: Low
**Status**: Done
**Category**: Internal
**Target Platform**: Windows, NVIDIA RTX 5090, AMD Ryzen, 64GB RAM
**Completed**: 2025-10-30

## Description

Implement all Internal category sources for managing internally-sourced content including manual backlogs and data imports.

## Sources

### Internal
- **ManualBacklogSource** - Manual idea backlog and notes
- **CSVImportSource** - Import ideas from CSV/Excel files

## Reference Implementation

Based on: `Sources/Content/Shorts/YouTube/`

## Goals

1. Implement all 2 Internal sources following SOLID principles
2. Support manual idea entry and tracking
3. Enable bulk data imports from files
4. Transform data to IdeaInspiration format
5. Store in SQLite databases with deduplication

## Key Features (Common Across All Sources)

### Data Collection
- Manually entered ideas and notes
- Imported data from spreadsheets
- Status tracking (new, in-progress, used, archived)
- Priority and category tags
- Assignment and ownership
- Creation and modification timestamps

### Methods
- Manual entry via CLI or web form
- CSV/Excel file import
- JSON bulk import
- Copy-paste from external sources
- Integration with note-taking apps (future)

### Universal Metrics
- Idea age (days since creation)
- Usage tracking (has it been used?)
- Priority scoring
- Category distribution

## Technical Requirements

### Architecture
```
Internal/
├── ManualBacklog/
│   ├── src/
│   │   ├── cli.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── idea_manager.py
│   │   └── plugins/
│   │       ├── __init__.py
│   │       └── manual_entry.py
└── CSVImport/
    ├── src/
    │   ├── cli.py
    │   ├── core/
    │   │   ├── config.py
    │   │   ├── database.py
    │   │   └── csv_parser.py
    │   └── plugins/
    │       ├── __init__.py
    │       └── csv_import.py
```

### Dependencies
- pandas (CSV/Excel parsing)
- openpyxl (Excel support)
- click or argparse (CLI)
- SQLite, ConfigLoad (all sources)

### Data Model (Internal Idea)
```python
{
    'source': 'manual_backlog|csv_import',
    'source_id': 'generated_id',
    'idea': {
        'title': 'Idea title',
        'description': 'Idea description',
        'notes': 'Additional notes',
        'category': 'category_name',
        'priority': 'high|medium|low'
    },
    'metadata': {
        'status': 'new|in_progress|used|archived',
        'created_by': 'user_name',
        'assigned_to': 'assignee_name',
        'tags': ['tag1', 'tag2']
    },
    'tracking': {
        'created_at': '2025-01-15T10:00:00Z',
        'modified_at': '2025-01-15T15:00:00Z',
        'used_at': None,
        'age_days': 5
    },
    'universal_metrics': {
        'priority_score': 7.5,
        'actionability': 8.0
    }
}
```

## Success Criteria

- [x] Both Internal sources implemented
- [x] Each source follows SOLID principles
- [x] Manual entry via CLI working
- [x] CSV/Excel import functional
- [x] Status tracking implemented
- [x] Priority and categorization working
- [x] Deduplication working
- [x] Data transforms to IdeaInspiration format
- [x] CLI interfaces consistent
- [x] Comprehensive tests (>80% coverage on core logic)
- [x] Documentation complete

## Implementation Summary

### Completed Components

**ManualBacklogSource** (`Sources/Internal/ManualBacklog/`)
- ✅ Full CLI with commands: add, update, mark-used, list-ideas, show, stats
- ✅ SQLite database storage with deduplication
- ✅ Status tracking (new, in_progress, used, archived)
- ✅ Priority management (critical, urgent, high, medium, low)
- ✅ Tag and assignment tracking
- ✅ IdeaInspiration format transformation
- ✅ 43 passing tests with 96% coverage on core logic
- ✅ Comprehensive README documentation

**CSVImportSource** (`Sources/Internal/CSVImport/`)
- ✅ CSV and Excel (.xlsx) file support via pandas/openpyxl
- ✅ Full CLI with commands: import-file, import-directory, validate, list-ideas, stats
- ✅ Intelligent column mapping (recognizes alternative names)
- ✅ Batch import from directories
- ✅ Data validation before import
- ✅ SQLite database storage with deduplication
- ✅ IdeaInspiration format transformation
- ✅ 36 passing tests with 86-90% coverage on core logic
- ✅ Comprehensive README documentation

### Test Results

**ManualBacklog**: 43/43 tests passing (100%)
- Database: 11 tests
- IdeaManager: 20 tests
- Plugin: 12 tests

**CSVImport**: 36/36 tests passing (100%)
- Database: 11 tests
- CSV Parser: 15 tests
- Plugin: 10 tests

### Verification

Smoke tests performed successfully:
- ✅ Manual idea creation via CLI
- ✅ CSV file validation
- ✅ CSV file import
- ✅ Idea listing and display
- ✅ Database operations
- ✅ Deduplication logic

## Implementation Priority

1. **CSVImportSource** - Enables bulk data migration
2. **ManualBacklogSource** - For ongoing manual entry

## Related Issues

- #001 - Unified Pipeline Integration

## CSV Import Format

Expected CSV structure:
```csv
title,description,category,priority,tags,status,notes
"Video idea 1","Description here","content","high","tag1,tag2","new","Additional notes"
"Video idea 2","Another description","marketing","medium","tag3","in_progress","More notes"
```

## Estimated Effort

2-3 weeks total
- CSVImportSource: 1 week
- ManualBacklogSource: 1-2 weeks

## Notes

Internal sources are the lowest priority as they don't automate content discovery, but they're still valuable for:
- Migrating existing idea backlogs
- Capturing one-off ideas that don't fit other sources
- Manual override when automated sources miss something
- Team collaboration on idea management

Consider building a simple web UI for manual entry in the future to improve usability beyond CLI.
