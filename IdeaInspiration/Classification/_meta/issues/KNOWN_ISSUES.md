# Known Issues

This document tracks known issues and limitations in PrismQ.IdeaInspiration.Classification.

## Current Known Issues

### None at this time

As of version 2.0.0, there are no known critical issues.

## Limitations

### 1. Keyword-Based Classification

**Issue**: Classification relies on weighted keyword matching, which may not capture semantic nuances.

**Impact**: Content with ambiguous or misleading titles/descriptions may be misclassified.

**Workaround**: Use confidence scores to filter low-confidence classifications.

**Status**: Working as designed. Future versions may add semantic analysis.

### 2. Language Support

**Issue**: Currently optimized for English content only.

**Impact**: Non-English content may not classify accurately.

**Workaround**: Ensure content metadata is in English or translate before classification.

**Status**: Planned for future enhancement.

### 3. Multi-Category Content

**Issue**: Content is assigned a single primary category, even if it spans multiple categories.

**Impact**: Some nuanced content may not be fully represented by a single category.

**Workaround**: Check `secondary_matches` in CategoryResult for other relevant categories.

**Status**: Working as designed. Secondary matches provide additional context.

## Reporting New Issues

If you encounter an issue:

1. Check this list to see if it's already known
2. Review the [README](../README.md) for usage guidelines
3. Open an issue on GitHub: https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification/issues

## Issue Resolution Process

1. Issue reported and confirmed
2. Added to this document with status
3. Prioritized on roadmap
4. Fixed in upcoming release
5. Moved to resolved section

## Resolved Issues

### Version 2.0.0

- Initial release - no prior issues to resolve
