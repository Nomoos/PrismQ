"""Taxonomy configuration for tag and category management.

This module provides configuration management for the taxonomy system,
including predefined categories, tag rules, and custom taxonomy definitions.
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class TaxonomyConfig:
    """Configuration for taxonomy generation.
    
    Attributes:
        categories: Hierarchical category structure (parent -> children)
        min_relevance: Minimum relevance score for tags (0.0-1.0)
        max_tags: Maximum number of tags to generate
        max_categories: Maximum number of categories to assign
        tag_similarity_threshold: Threshold for deduplication (0.0-1.0)
        enable_hierarchical: Whether to support hierarchical categories
        min_category_score: Minimum score for category assignment (0.0-1.0)
        min_subcategory_score: Minimum score for subcategory assignment (0.0-1.0)
        custom_rules: Additional custom rules
    """
    
    categories: Dict[str, List[str]] = field(default_factory=dict)
    min_relevance: float = 0.7
    max_tags: int = 10
    max_categories: int = 3
    tag_similarity_threshold: float = 0.85
    enable_hierarchical: bool = True
    min_category_score: float = 0.5
    min_subcategory_score: float = 0.55
    custom_rules: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return asdict(self)
    
    def to_json(self, filepath: Optional[Path] = None) -> str:
        """Convert to JSON string or save to file.
        
        Args:
            filepath: Optional file path to save JSON config
        
        Returns:
            JSON string representation
        """
        json_str = json.dumps(self.to_dict(), indent=2)
        
        if filepath:
            Path(filepath).write_text(json_str)
        
        return json_str
    
    def get_all_categories(self) -> List[str]:
        """Get flattened list of all categories.
        
        Returns:
            List of all category paths
        """
        categories = []
        for parent, children in self.categories.items():
            # Add parent category
            categories.append(parent)
            # Add child categories with full path
            for child in children:
                categories.append(f"{parent}/{child}")
        return categories
    
    def validate(self) -> bool:
        """Validate configuration parameters.
        
        Returns:
            True if configuration is valid
        
        Raises:
            ValueError: If configuration is invalid
        """
        if not 0 <= self.min_relevance <= 1:
            raise ValueError(f"min_relevance must be between 0 and 1, got {self.min_relevance}")
        
        if self.max_tags < 1:
            raise ValueError(f"max_tags must be at least 1, got {self.max_tags}")
        
        if self.max_categories < 1:
            raise ValueError(f"max_categories must be at least 1, got {self.max_categories}")
        
        if not 0 <= self.tag_similarity_threshold <= 1:
            raise ValueError(f"tag_similarity_threshold must be between 0 and 1, got {self.tag_similarity_threshold}")
        
        if not self.categories:
            raise ValueError("categories cannot be empty")
        
        return True


def load_taxonomy_config(filepath: Path) -> TaxonomyConfig:
    """Load taxonomy configuration from JSON file.
    
    Args:
        filepath: Path to JSON configuration file
    
    Returns:
        TaxonomyConfig instance
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is invalid
    
    Example:
        >>> config = load_taxonomy_config(Path("taxonomy.json"))
        >>> print(config.categories)
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Configuration file not found: {filepath}")
    
    try:
        data = json.loads(filepath.read_text())
        config = TaxonomyConfig(**data)
        config.validate()
        return config
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in configuration file: {e}")
    except TypeError as e:
        raise ValueError(f"Invalid configuration structure: {e}")


# Default taxonomy configuration
DEFAULT_TAXONOMY = TaxonomyConfig(
    categories={
        "Technology": [
            "AI", "Web Development", "Mobile", "Cloud", "DevOps",
            "Cybersecurity", "Data Science", "Blockchain", "IoT", "Gaming"
        ],
        "Business": [
            "Marketing", "Finance", "Entrepreneurship", "Leadership",
            "Sales", "Strategy", "Productivity", "E-commerce", "Startups"
        ],
        "Lifestyle": [
            "Health", "Fitness", "Travel", "Food", "Fashion",
            "Home", "Relationships", "Personal Development", "Wellness"
        ],
        "Education": [
            "Programming", "Languages", "Science", "Math", "History",
            "Literature", "Online Learning", "Career Development", "Skills"
        ],
        "Creative": [
            "Design", "Writing", "Photography", "Music", "Art",
            "Video Production", "Content Creation", "Storytelling"
        ],
        "Entertainment": [
            "Movies", "TV Shows", "Books", "Podcasts", "Gaming",
            "Social Media", "Streaming", "Pop Culture"
        ],
        "Science": [
            "Physics", "Biology", "Chemistry", "Space", "Environment",
            "Medicine", "Research", "Innovation", "Climate"
        ],
        "Sports": [
            "Football", "Basketball", "Tennis", "Fitness Training",
            "Extreme Sports", "Olympics", "Sports Analytics"
        ],
        "News": [
            "Politics", "World Events", "Economy", "Technology News",
            "Local News", "Breaking News", "Analysis"
        ],
        "Personal Finance": [
            "Investing", "Saving", "Retirement", "Taxes",
            "Budgeting", "Real Estate", "Cryptocurrency"
        ]
    },
    min_relevance=0.7,
    max_tags=10,
    max_categories=3,
    tag_similarity_threshold=0.85,
    enable_hierarchical=True,
    custom_rules={
        "description": "Default PrismQ taxonomy configuration",
        "version": "1.0",
        "last_updated": "2025-11-23"
    }
)


# Example custom configurations for different niches

TECH_FOCUSED_TAXONOMY = TaxonomyConfig(
    categories={
        "Programming": [
            "Python", "JavaScript", "Java", "C++", "Go", "Rust",
            "Web Development", "Mobile Development", "Backend", "Frontend"
        ],
        "AI & Machine Learning": [
            "Deep Learning", "NLP", "Computer Vision", "Reinforcement Learning",
            "Data Science", "MLOps", "AI Ethics"
        ],
        "Infrastructure": [
            "Cloud Computing", "DevOps", "Kubernetes", "Docker",
            "CI/CD", "Monitoring", "Networking"
        ],
        "Security": [
            "Application Security", "Network Security", "Ethical Hacking",
            "Cryptography", "Privacy", "Compliance"
        ],
        "Databases": [
            "SQL", "NoSQL", "Database Design", "Performance",
            "Data Warehousing", "Big Data"
        ]
    },
    min_relevance=0.75,  # Higher threshold for tech content
    max_tags=12,
    max_categories=2,
    tag_similarity_threshold=0.80,
    enable_hierarchical=True
)


LIFESTYLE_FOCUSED_TAXONOMY = TaxonomyConfig(
    categories={
        "Health & Wellness": [
            "Nutrition", "Mental Health", "Sleep", "Exercise",
            "Meditation", "Yoga", "Stress Management"
        ],
        "Home & Living": [
            "Interior Design", "Organization", "Cleaning", "DIY",
            "Gardening", "Smart Home", "Sustainability"
        ],
        "Relationships": [
            "Dating", "Marriage", "Family", "Parenting",
            "Friendship", "Communication", "Conflict Resolution"
        ],
        "Personal Growth": [
            "Self-Improvement", "Habits", "Goal Setting", "Motivation",
            "Time Management", "Mindfulness", "Confidence"
        ],
        "Fashion & Beauty": [
            "Style", "Makeup", "Skincare", "Haircare",
            "Sustainable Fashion", "Trends", "Shopping"
        ]
    },
    min_relevance=0.65,  # Lower threshold for lifestyle content
    max_tags=8,
    max_categories=3,
    tag_similarity_threshold=0.85,
    enable_hierarchical=True
)


def create_custom_taxonomy(
    categories: Dict[str, List[str]],
    min_relevance: float = 0.7,
    max_tags: int = 10,
    max_categories: int = 3
) -> TaxonomyConfig:
    """Create a custom taxonomy configuration.
    
    Args:
        categories: Hierarchical category structure
        min_relevance: Minimum relevance score for tags
        max_tags: Maximum number of tags
        max_categories: Maximum number of categories
    
    Returns:
        TaxonomyConfig instance
    
    Example:
        >>> config = create_custom_taxonomy(
        ...     categories={
        ...         "Cooking": ["Baking", "Grilling", "Healthy Recipes"],
        ...         "Travel": ["Europe", "Asia", "Budget Travel"]
        ...     },
        ...     min_relevance=0.65,
        ...     max_tags=8
        ... )
    """
    config = TaxonomyConfig(
        categories=categories,
        min_relevance=min_relevance,
        max_tags=max_tags,
        max_categories=max_categories
    )
    config.validate()
    return config


__all__ = [
    'TaxonomyConfig',
    'load_taxonomy_config',
    'create_custom_taxonomy',
    'DEFAULT_TAXONOMY',
    'TECH_FOCUSED_TAXONOMY',
    'LIFESTYLE_FOCUSED_TAXONOMY',
]
