#!/usr/bin/env python3
"""
Generate scaffolding for remaining Signal sources based on GoogleTrends template.

This script creates complete directory structures and stub implementations for all
remaining signal sources, making it easy for developers to complete them.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List

# Source definitions
SOURCES = {
    "TikTokHashtag": {
        "category": "Hashtags",
        "signal_type": "hashtag",
        "description": "Trending hashtags on TikTok",
        "library": "TikTokApi",
        "requires_api_key": False,
        "priority": "high",
    },
    "InstagramHashtag": {
        "category": "Hashtags",
        "signal_type": "hashtag",
        "description": "Trending hashtags on Instagram",
        "library": "instaloader",
        "requires_api_key": False,
        "priority": "medium",
    },
    "GoogleNews": {
        "category": "News",
        "signal_type": "news",
        "description": "News articles from Google News",
        "library": "gnews",
        "requires_api_key": False,
        "priority": "high",
    },
    "NewsApi": {
        "category": "News",
        "signal_type": "news",
        "description": "News articles from NewsAPI",
        "library": "newsapi-python",
        "requires_api_key": True,
        "priority": "medium",
    },
    "TikTokSounds": {
        "category": "Sounds",
        "signal_type": "sound",
        "description": "Trending audio on TikTok",
        "library": "TikTokApi",
        "requires_api_key": False,
        "priority": "high",
    },
    "InstagramAudioTrends": {
        "category": "Sounds",
        "signal_type": "sound",
        "description": "Audio trends on Instagram",
        "library": "instaloader",
        "requires_api_key": False,
        "priority": "lower",
    },
    "MemeTracker": {
        "category": "Memes",
        "signal_type": "meme",
        "description": "Track meme propagation across platforms",
        "library": "requests, BeautifulSoup4",
        "requires_api_key": False,
        "priority": "lower",
    },
    "KnowYourMeme": {
        "category": "Memes",
        "signal_type": "meme",
        "description": "Meme database and documentation from KnowYourMeme",
        "library": "requests, BeautifulSoup4",
        "requires_api_key": False,
        "priority": "lower",
    },
    "SocialChallenge": {
        "category": "Challenges",
        "signal_type": "challenge",
        "description": "Viral social media challenges",
        "library": "requests",
        "requires_api_key": False,
        "priority": "lower",
    },
    "GeoLocalTrends": {
        "category": "Locations",
        "signal_type": "location",
        "description": "Location-based trending content",
        "library": "pytrends",
        "requires_api_key": False,
        "priority": "lower",
    },
    "TrendsFile": {
        "category": "Trends",
        "signal_type": "trend",
        "description": "Import trends from CSV/JSON files",
        "library": "pandas",
        "requires_api_key": False,
        "priority": "lower",
    },
}


def to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case."""
    import re

    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def generate_source(source_name: str, source_info: Dict, template_path: Path, output_base: Path):
    """Generate a complete source implementation from template."""

    category = source_info["category"]
    signal_type = source_info["signal_type"]
    description = source_info["description"]
    library = source_info["library"]
    requires_api_key = source_info["requires_api_key"]
    snake_name = to_snake_case(source_name)

    # Create output directory
    output_dir = output_base / category / source_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy template structure
    for item in template_path.iterdir():
        if item.name in [".git", "__pycache__", ".pytest_cache"]:
            continue
        if item.name.endswith(".pyc"):
            continue

        dest = output_dir / item.name
        if item.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(
                item, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")
            )
        else:
            shutil.copy2(item, dest)

    # Generate .env.example
    env_content = f"""# {source_name}Source Configuration

# Database
DATABASE_PATH=signals_{snake_name}.db

# Regions (comma-separated list)
REGIONS=US,GB,CA,AU

# Language
LANGUAGE=en

# Number of results to fetch
MAX_RESULTS=25

# Retry settings
MAX_RETRIES=3
RETRY_DELAY_SECONDS=2

# Time range for trends (in days)
TIMEFRAME_DAYS=7
"""

    if requires_api_key:
        env_content += f"\n# API Key (required)\n{snake_name.upper()}_API_KEY=your_api_key_here\n"

    (output_dir / ".env.example").write_text(env_content)

    # Generate .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv
*.egg-info/
dist/
build/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Database
*.db
*.sqlite
*.sqlite3

# Environment
.env
.env.local

# Logs
*.log
"""
    (output_dir / ".gitignore").write_text(gitignore_content)

    # Update pyproject.toml
    pyproject = (output_dir / "pyproject.toml").read_text()
    pyproject = pyproject.replace("google-trends-source", f'{snake_name.replace("_", "-")}-source')
    pyproject = pyproject.replace("google_trends_source", f"{snake_name}_source")
    pyproject = pyproject.replace("GoogleTrendsSource", f"{source_name}Source")
    pyproject = pyproject.replace("Google Trends signal source", description)
    (output_dir / "pyproject.toml").write_text(pyproject)

    # Update requirements.txt
    requirements = (output_dir / "requirements.txt").read_text()
    lines = requirements.split("\n")
    new_lines = []
    for line in lines:
        if line.startswith("pytrends"):
            for lib in library.split(", "):
                new_lines.append(lib.strip())
        else:
            new_lines.append(line)
    (output_dir / "requirements.txt").write_text("\n".join(new_lines))

    # Generate simplified README
    readme_content = f"""# {source_name}Source

**{description}**

## Status

🚧 **Scaffolding Generated** - Implementation in progress

## Overview

{source_name}Source collects {signal_type} signals for the PrismQ.IdeaInspiration ecosystem.

## TODO

- [ ] Implement `{snake_name}_plugin.py` scraping logic
- [ ] Add API client initialization  
- [ ] Implement signal creation from source data
- [ ] Add error handling and rate limiting
- [ ] Write comprehensive tests
- [ ] Add usage examples to README

## Quick Start

```bash
# Install dependencies
pip install -e .

# Configure
cp .env.example .env
# Edit .env with your settings

# Run (once implemented)
python -m src.cli scrape
python -m src.cli list
```

## Implementation Guide

See `Sources/Signals/IMPLEMENTATION_GUIDE.md` for detailed instructions.

Reference implementation: `Sources/Signals/Trends/GoogleTrends/`

## License

Proprietary - Part of PrismQ.IdeaInspiration ecosystem
"""
    (output_dir / "README.md").write_text(readme_content)

    # Update plugin file
    plugin_path = output_dir / "src" / "plugins" / "google_trends_plugin.py"
    plugin_content = f'''"""{source_name} plugin for scraping {signal_type} signals."""

from typing import List, Dict, Any
from datetime import datetime, timezone
from . import SignalPlugin


class {source_name}Plugin(SignalPlugin):
    """Plugin for scraping {signal_type} signals from {source_name}."""
    
    def __init__(self, config):
        """Initialize {source_name} plugin."""
        super().__init__(config)
        # TODO: Initialize {source_name} API/library
        self.api = None
    
    def get_source_name(self) -> str:
        """Get the name of this source."""
        return "{snake_name}"
    
    def scrape(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Scrape {signal_type} signals from {source_name}.
        
        Returns:
            List of signal dictionaries
        """
        signals = []
        
        try:
            # TODO: Implement scraping logic
            print(f"TODO: Implement {source_name} scraping")
            
        except Exception as e:
            print(f"Error scraping {source_name}: {{e}}")
        
        return signals
'''
    plugin_path.write_text(plugin_content)

    # Rename plugin file
    new_plugin = output_dir / "src" / "plugins" / f"{snake_name}_plugin.py"
    plugin_path.rename(new_plugin)

    # Rename test file
    old_test = output_dir / "tests" / "test_google_trends_plugin.py"
    new_test = output_dir / "tests" / f"test_{snake_name}_plugin.py"
    if old_test.exists():
        test_content = old_test.read_text()
        test_content = test_content.replace("GoogleTrends", source_name)
        test_content = test_content.replace("google_trends", snake_name)
        new_test.write_text(test_content)
        old_test.unlink()

    # Update CLI
    cli = (output_dir / "src" / "cli.py").read_text()
    cli = cli.replace("GoogleTrends", source_name)
    cli = cli.replace("google_trends", snake_name)
    (output_dir / "src" / "cli.py").write_text(cli)

    # Update config
    config = (output_dir / "src" / "core" / "config.py").read_text()
    config = config.replace("GoogleTrendsConfig", f"{source_name}Config")
    config = config.replace("google_trends", snake_name)
    if requires_api_key:
        lines = config.split("\n")
        new_lines = []
        for line in lines:
            new_lines.append(line)
            if "self.language =" in line:
                new_lines.append(
                    f'        self.api_key = self._get_or_default("{snake_name.upper()}_API_KEY", "")'
                )
        config = "\n".join(new_lines)
    (output_dir / "src" / "core" / "config.py").write_text(config)

    # Update metrics
    metrics = (output_dir / "src" / "core" / "metrics.py").read_text()
    metrics = metrics.replace("from_google_trends", f"from_{snake_name}")
    metrics = metrics.replace("google_trends", snake_name)
    (output_dir / "src" / "core" / "metrics.py").write_text(metrics)

    print(f"✅ Generated {source_name} in Sources/Signals/{category}/{source_name}")


def main():
    """Generate all remaining signal sources."""
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    template_path = repo_root / "Sources" / "Signals" / "Trends" / "GoogleTrends"
    output_base = repo_root / "Sources" / "Signals"

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return

    print("🚀 Generating Signal Sources Scaffolding...")
    print(f"Template: {template_path}")
    print(f"Output: {output_base}")
    print()

    generated = []
    for source_name, source_info in SOURCES.items():
        try:
            generate_source(source_name, source_info, template_path, output_base)
            generated.append((source_name, source_info["priority"]))
        except Exception as e:
            print(f"❌ Failed to generate {source_name}: {e}")
            import traceback

            traceback.print_exc()

    print()
    print(f"✅ Generated {len(generated)}/{len(SOURCES)} signal sources")
    print()
    print("Summary by priority:")
    for priority in ["high", "medium", "lower"]:
        sources = [name for name, p in generated if p == priority]
        if sources:
            print(f"  {priority.upper()}: {', '.join(sources)}")
    print()
    print("Next steps:")
    print("1. Review generated sources in Sources/Signals/")
    print("2. Implement TODO items in each *_plugin.py file")
    print("3. Add source-specific scraping logic")
    print("4. Run tests for each source")
    print("5. Update documentation with real examples")


if __name__ == "__main__":
    main()
