"""CLI for PrismQ.IdeaInspiration.Scoring module.

This module provides a command-line interface for scoring IdeaInspiration objects.
It accepts a list of IdeaInspiration objects and returns the same list enriched
with scores.
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add parent directories to path to import required modules
current_dir = Path(__file__).parent
scoring_root = current_dir.parent
sys.path.insert(0, str(scoring_root.parent.parent))  # For Model
sys.path.insert(0, str(scoring_root.parent))  # For ConfigLoad
sys.path.insert(0, str(scoring_root))  # For src

from ConfigLoad import Config, get_module_logger
from src.scoring import ScoringEngine
from src.models import ScoreBreakdown

# Try to import IdeaInspiration from Model
try:
    from Model.idea_inspiration import IdeaInspiration, ContentType
except ImportError:
    # Fallback if Model is not in path
    sys.path.insert(0, str(scoring_root.parent / 'Model'))
    from idea_inspiration import IdeaInspiration, ContentType

# Initialize logger
logger = get_module_logger(
    module_name="PrismQ.IdeaInspiration.Scoring.CLI",
    module_version="1.0.0",
    module_path=str(Path(__file__).parent),
    log_startup=False
)


def score_inspirations(inspirations: List[IdeaInspiration]) -> List[IdeaInspiration]:
    """Score a list of IdeaInspiration objects.
    
    This function accepts a list of IdeaInspiration objects, calculates scores
    for each one, and returns the same list with updated score attributes.
    
    Args:
        inspirations: List of IdeaInspiration objects to score
        
    Returns:
        List of IdeaInspiration objects with updated scores
    """
    logger.info(f"Scoring {len(inspirations)} IdeaInspiration objects")
    
    # Initialize scoring engine
    engine = ScoringEngine()
    
    # Score each inspiration
    scored_inspirations = []
    for i, inspiration in enumerate(inspirations):
        try:
            # Get score breakdown
            score_breakdown = engine.score_idea_inspiration(inspiration)
            
            # Update the inspiration's score attribute
            inspiration.score = int(score_breakdown.overall_score)
            
            scored_inspirations.append(inspiration)
            logger.debug(f"Scored inspiration {i+1}/{len(inspirations)}: {inspiration.title[:50]}... = {inspiration.score}")
            
        except Exception as e:
            logger.error(f"Error scoring inspiration {i+1}: {str(e)}")
            # Keep the original without score
            scored_inspirations.append(inspiration)
    
    logger.info(f"Successfully scored {len(scored_inspirations)} IdeaInspiration objects")
    return scored_inspirations


def main():
    """Main entry point for the CLI.
    
    Reads IdeaInspiration objects from stdin (JSON array), scores them,
    and outputs the scored objects to stdout (JSON array).
    """
    logger.info("PrismQ.IdeaInspiration.Scoring CLI - Starting")
    
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
        
        # Score the inspirations
        scored = score_inspirations(inspirations)
        
        # Convert back to dictionaries for JSON output
        output = [insp.to_dict() for insp in scored]
        
        # Output results
        print(json.dumps(output, indent=2))
        
        logger.info("PrismQ.IdeaInspiration.Scoring CLI - Complete")
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
