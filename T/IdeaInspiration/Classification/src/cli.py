"""CLI for PrismQ.IdeaInspiration.Classification module.

This module provides a command-line interface for classifying IdeaInspiration objects.
It accepts a list of IdeaInspiration objects and returns the same list enriched
with category and subcategory classifications.
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add parent directories to path to import required modules
current_dir = Path(__file__).parent
classification_root = current_dir.parent
sys.path.insert(0, str(classification_root.parent.parent))  # For Model
sys.path.insert(0, str(classification_root))  # For src

# Try to import IdeaInspiration from Model
try:
    from Model.idea_inspiration import IdeaInspiration, ContentType
except ImportError:
    # Fallback if Model is not in path
    sys.path.insert(0, str(classification_root.parent / 'Model'))
    from idea_inspiration import IdeaInspiration, ContentType

# Import classification module
from src.classification import TextClassifier, ClassificationEnrichment

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def classify_inspirations(inspirations: List[IdeaInspiration]) -> List[IdeaInspiration]:
    """Classify a list of IdeaInspiration objects.
    
    This function accepts a list of IdeaInspiration objects, classifies them
    into main categories and subcategories, and returns the same list with
    updated category attributes.
    
    Args:
        inspirations: List of IdeaInspiration objects to classify
        
    Returns:
        List of IdeaInspiration objects with updated category and subcategory_relevance
    """
    logger.info(f"Classifying {len(inspirations)} IdeaInspiration objects")
    
    # Initialize classifier
    classifier = TextClassifier()
    
    # Classify each inspiration
    classified_inspirations = []
    for i, inspiration in enumerate(inspirations):
        try:
            # Get classification enrichment
            enrichment = classifier.enrich(inspiration)
            
            # Update the inspiration's category and subcategory attributes
            inspiration.category = enrichment.category.value
            
            # Convert tags to subcategory_relevance scores
            # Use a simple approach: assign confidence score to identified tags
            if enrichment.tags:
                for tag in enrichment.tags:
                    # Convert confidence to percentage (0-100)
                    relevance_score = int(enrichment.category_confidence * 100)
                    inspiration.subcategory_relevance[tag] = relevance_score
            
            classified_inspirations.append(inspiration)
            logger.debug(
                f"Classified inspiration {i+1}/{len(inspirations)}: "
                f"{inspiration.title[:50]}... = {inspiration.category}"
            )
            
        except Exception as e:
            logger.error(f"Error classifying inspiration {i+1}: {str(e)}")
            # Keep the original without classification
            classified_inspirations.append(inspiration)
    
    logger.info(f"Successfully classified {len(classified_inspirations)} IdeaInspiration objects")
    return classified_inspirations


def main():
    """Main entry point for the CLI.
    
    Reads IdeaInspiration objects from stdin (JSON array), classifies them,
    and outputs the classified objects to stdout (JSON array).
    """
    logger.info("PrismQ.IdeaInspiration.Classification CLI - Starting")
    
    try:
        # Read input from stdin
        input_data = sys.stdin.read()
        
        if not input_data.strip():
            logger.warning("No input data received")
            print("[]")
            return
        
        # Parse JSON input
        try:
            data = json.loads(input_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON input: {e}")
            print(json.dumps({"error": "Invalid JSON input"}))
            sys.exit(1)
        
        # Convert to list if single object
        if isinstance(data, dict):
            data = [data]
        
        if not isinstance(data, list):
            logger.error("Input must be a JSON array of IdeaInspiration objects")
            print(json.dumps({"error": "Input must be a JSON array"}))
            sys.exit(1)
        
        # Convert dictionaries to IdeaInspiration objects
        inspirations = []
        for item in data:
            if isinstance(item, dict):
                inspirations.append(IdeaInspiration.from_dict(item))
            else:
                logger.warning(f"Skipping invalid item: {type(item)}")
        
        if not inspirations:
            logger.warning("No valid IdeaInspiration objects found in input")
            print("[]")
            return
        
        # Classify the inspirations
        classified = classify_inspirations(inspirations)
        
        # Convert back to dictionaries for JSON output
        output = [insp.to_dict() for insp in classified]
        
        # Output results
        print(json.dumps(output, indent=2))
        
        logger.info("PrismQ.IdeaInspiration.Classification CLI - Complete")
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
