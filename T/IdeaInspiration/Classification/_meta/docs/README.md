# Documentation

This directory contains comprehensive documentation for PrismQ.IdeaInspiration.Classification.

## Available Documentation

### Getting Started
- [Main README](../README.md) - Overview, installation, and quick start guide
- [TAXONOMY.md](../TAXONOMY.md) - Detailed category taxonomy and usage

### API Documentation
- [CategoryClassifier](../README.md#category-classification) - Primary category classification
- [StoryDetector](../README.md#story-detection) - Binary story detection
- [PrimaryCategory](../README.md#primarycategory-enum) - Category enumeration
- [CategoryResult](../README.md#categoryresult-namedtuple) - Classification result structure

### Examples
- [example.py](../examples/example.py) - Working demonstration of both classifiers

### Development
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [Testing Guide](../README.md#testing) - How to run tests

## Package Structure

The package follows standard Python packaging conventions:

```
prismq/idea/classification/
├── __init__.py              # Package exports
├── categories.py            # Category enums and models
├── category_classifier.py   # Primary category classifier
└── story_detector.py        # Story detection classifier
```

## Additional Resources

- **Repository**: https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification
- **Issues**: https://github.com/PrismQDev/PrismQ.IdeaInspiration.Classification/issues
- **License**: See [LICENSE](../LICENSE) file

## Support

For questions, issues, or feature requests:
1. Check the [README](../README.md) for usage information
2. Review the [TAXONOMY](../TAXONOMY.md) for category details
3. Run the [example.py](../examples/example.py) to see it in action
4. Open an issue if you need help
