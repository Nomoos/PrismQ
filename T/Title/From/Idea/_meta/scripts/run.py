#!/usr/bin/env python3
"""CLI script for creating stories with titles from Ideas stored in database.

This tool loads Ideas from the database that don't yet have Stories and creates
10 Story objects with their initial Titles (v0) for each.

Database configuration is loaded from .env file (default: C:/PrismQ/.env).
The .env file defines WORKING_DIRECTORY where db.s3db is located.

Usage:
    python run.py                                   # Use default .env at C:/PrismQ/.env
    python run.py --env /path/to/.env               # Use custom .env file
    python run.py --preview                         # Preview mode (no changes)
    python run.py --limit 5                         # Process max 5 ideas
    python run.py --idea-id 123                     # Process specific idea

Examples:
    # Preview what would be processed (no changes made)
    python run.py --preview
    
    # Process all Ideas without Stories
    python run.py
    
    # Process only first 3 Ideas
    python run.py --limit 3
    
    # Process specific Idea by ID
    python run.py --idea-id 42
    
    # Output as JSON
    python run.py --json
    
    # Use custom .env file
    python run.py --env D:/MyProject/.env
"""

import sys
import os
import argparse
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

# Setup paths for imports
script_dir = Path(__file__).parent.absolute()
project_root = script_dir.parent.parent.parent.parent.parent.parent
src_dir = script_dir.parent.parent / 'src'
idea_model_dir = project_root / 'T' / 'Idea' / 'Model' / 'src'
envload_dir = project_root / 'EnvLoad'

for path in [str(project_root), str(src_dir), str(idea_model_dir), str(envload_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from idea import Idea, IdeaStatus, ContentGenre
from idea_db import IdeaDatabase
from story_title_service import (
    StoryTitleService,
    StoryTitleResult,
    create_stories_from_idea,
)
from title_generator import TitleConfig
from EnvLoad import Config

# Default .env file path
DEFAULT_ENV_FILE = "C:/PrismQ/.env"


def get_ideas_without_stories(db_path: str) -> List[Dict[str, Any]]:
    """Get all Ideas from database that don't have Stories yet.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        List of Idea dictionaries without Stories
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get ideas that don't have any Story rows referencing them
    # Check if Story table exists first
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='Story'
    """)
    story_table_exists = cursor.fetchone() is not None
    
    if story_table_exists:
        # Get ideas without stories
        cursor.execute("""
            SELECT i.* FROM ideas i
            LEFT JOIN Story s ON CAST(i.id AS TEXT) = s.idea_id
            WHERE s.id IS NULL
            ORDER BY i.id
        """)
    else:
        # No Story table - all ideas are pending
        cursor.execute("SELECT * FROM ideas ORDER BY id")
    
    ideas = []
    for row in cursor.fetchall():
        idea_dict = dict(row)
        # Parse JSON fields
        for field in ['target_demographics', 'target_platforms', 'target_formats', 
                      'keywords', 'themes', 'potential_scores', 'metadata']:
            if idea_dict.get(field):
                try:
                    idea_dict[field] = json.loads(idea_dict[field])
                except (json.JSONDecodeError, TypeError):
                    pass
        ideas.append(idea_dict)
    
    conn.close()
    return ideas


def get_idea_by_id(db_path: str, idea_id: int) -> Optional[Dict[str, Any]]:
    """Get a specific Idea from database by ID.
    
    Args:
        db_path: Path to SQLite database
        idea_id: ID of the Idea
        
    Returns:
        Idea dictionary or None
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM ideas WHERE id = ?", (idea_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    idea_dict = dict(row)
    # Parse JSON fields
    for field in ['target_demographics', 'target_platforms', 'target_formats', 
                  'keywords', 'themes', 'potential_scores', 'metadata']:
        if idea_dict.get(field):
            try:
                idea_dict[field] = json.loads(idea_dict[field])
            except (json.JSONDecodeError, TypeError):
                pass
    
    conn.close()
    return idea_dict


def dict_to_idea(idea_dict: Dict[str, Any]) -> Idea:
    """Convert database Idea dictionary to Idea object.
    
    Args:
        idea_dict: Dictionary from database
        
    Returns:
        Idea object
    """
    genre = ContentGenre.EDUCATIONAL
    if idea_dict.get('genre'):
        try:
            genre = ContentGenre[idea_dict['genre'].upper()]
        except (KeyError, AttributeError):
            pass
    
    status = IdeaStatus.DRAFT
    if idea_dict.get('status'):
        try:
            status = IdeaStatus[idea_dict['status'].upper()]
        except (KeyError, AttributeError):
            pass
    
    return Idea(
        title=idea_dict.get('title', 'Untitled'),
        concept=idea_dict.get('concept', ''),
        genre=genre,
        status=status,
    )


def print_preview(ideas: List[Dict[str, Any]], as_json: bool = False):
    """Print preview of Ideas that would be processed.
    
    Args:
        ideas: List of Idea dictionaries
        as_json: Output as JSON
    """
    if as_json:
        output = {
            'mode': 'preview',
            'ideas_count': len(ideas),
            'stories_would_create': len(ideas) * 10,
            'ideas': []
        }
        for idea in ideas:
            output['ideas'].append({
                'id': idea.get('id'),
                'title': idea.get('title'),
                'concept': idea.get('concept', '')[:100],
                'genre': idea.get('genre'),
                'status': idea.get('status'),
            })
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return
    
    print()
    print("=" * 70)
    print("  PrismQ.T.Title.From.Idea - PREVIEW MODE")
    print("=" * 70)
    print(f"  Ideas to process: {len(ideas)}")
    print(f"  Stories would create: {len(ideas) * 10}")
    print("=" * 70)
    print()
    
    for idea in ideas:
        concept = idea.get('concept', '')
        concept_preview = concept[:50] + '...' if len(concept) > 50 else concept
        print(f"  Idea #{idea.get('id')}: {idea.get('title')}")
        print(f"    Concept: {concept_preview}")
        print(f"    Genre: {idea.get('genre', 'N/A')}")
        print(f"    Status: {idea.get('status', 'N/A')}")
        print(f"    → Would create 10 stories with titles")
        print()
    
    print("=" * 70)
    print("  Run without --preview to actually create stories")
    print("=" * 70)
    print()


def print_result(idea_dict: Dict[str, Any], result: StoryTitleResult, as_json: bool = False):
    """Print creation result for a single Idea.
    
    Args:
        idea_dict: Source Idea dictionary
        result: StoryTitleResult from creation
        as_json: Output as JSON
    """
    if as_json:
        output = {
            'idea_id': idea_dict.get('id'),
            'idea_title': idea_dict.get('title'),
            'story_count': result.count,
            'stories': []
        }
        for story, title in result.get_story_title_pairs():
            output['stories'].append({
                'story_id': story.id,
                'state': story.state.value,
                'title_id': title.id,
                'title_version': title.version,
                'title_text': title.text,
            })
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return
    
    print(f"\n  Idea #{idea_dict.get('id')}: {idea_dict.get('title')}")
    print(f"  Created {result.count} stories:")
    for i, (story, title) in enumerate(result.get_story_title_pairs(), 1):
        title_preview = title.text[:50] + '...' if len(title.text) > 50 else title.text
        print(f"    {i}. Story #{story.id}: {title_preview}")


def main():
    parser = argparse.ArgumentParser(
        description='Create Stories with Titles from Ideas in database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be processed (no changes made)
  python run.py --preview
  
  # Process all Ideas without Stories
  python run.py
  
  # Process only first 3 Ideas
  python run.py --limit 3
  
  # Process specific Idea by ID
  python run.py --idea-id 42
  
  # Output as JSON
  python run.py --json
  
  # Use custom .env file
  python run.py --env D:/MyProject/.env
        """
    )
    
    parser.add_argument('--env', '-e', default=DEFAULT_ENV_FILE,
                        help=f'Path to .env file (default: {DEFAULT_ENV_FILE})')
    parser.add_argument('--preview', '-p', action='store_true', 
                        help='Preview mode - show what would be done without making changes')
    parser.add_argument('--idea-id', '-i', type=int, help='Process specific Idea by ID')
    parser.add_argument('--limit', '-l', type=int, help='Maximum number of Ideas to process')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Load configuration from .env file
    try:
        config = Config(env_file=args.env, interactive=False)
        db_path = config.database_path
    except Exception as e:
        print(f"Error loading configuration from {args.env}: {e}")
        return 1
    
    # Verify database exists
    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}")
        print(f"  (loaded from .env file: {args.env})")
        return 1
    
    if not args.json:
        print(f"  [INFO] Using .env file: {args.env}")
        print(f"  [INFO] Working directory: {config.working_directory}")
        print(f"  [INFO] Database: {db_path}")
    
    # Get Ideas to process
    if args.idea_id:
        idea_dict = get_idea_by_id(db_path, args.idea_id)
        if not idea_dict:
            print(f"Error: Idea #{args.idea_id} not found in database")
            return 1
        ideas = [idea_dict]
    else:
        ideas = get_ideas_without_stories(db_path)
    
    if args.limit and len(ideas) > args.limit:
        ideas = ideas[:args.limit]
    
    if not ideas:
        if not args.json:
            print()
            print("=" * 70)
            print("  PrismQ.T.Title.From.Idea")
            print("=" * 70)
            print("  No Ideas found that need Stories")
            print("=" * 70)
            print()
        else:
            print(json.dumps({'status': 'no_ideas', 'message': 'No Ideas found that need Stories'}))
        return 0
    
    # Preview mode
    if args.preview:
        print_preview(ideas, as_json=args.json)
        return 0
    
    # Process Ideas
    if not args.json:
        print()
        print("=" * 70)
        print("  PrismQ.T.Title.From.Idea - Processing")
        print("=" * 70)
        print(f"  Ideas to process: {len(ideas)}")
        print(f"  Database: {db_path}")
        print("=" * 70)
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Ensure Story/Title tables exist
    service = StoryTitleService(conn)
    service.ensure_tables_exist()
    
    results = []
    for idea_dict in ideas:
        idea = dict_to_idea(idea_dict)
        idea_id = str(idea_dict.get('id'))
        
        result = create_stories_from_idea(
            idea,
            connection=conn,
            idea_id=idea_id,
            skip_if_exists=True
        )
        
        if result:
            results.append((idea_dict, result))
            if not args.json:
                print_result(idea_dict, result, as_json=False)
        else:
            if not args.json:
                print(f"\n  Idea #{idea_dict.get('id')}: Skipped (already has stories)")
    
    conn.close()
    
    # Summary
    if not args.json:
        print()
        print("=" * 70)
        total_stories = sum(r[1].count for r in results)
        print(f"  Total: {len(results)} Ideas processed, {total_stories} Stories created")
        print("=" * 70)
        print()
    else:
        output = {
            'status': 'completed',
            'ideas_processed': len(results),
            'stories_created': sum(r[1].count for r in results),
            'results': []
        }
        for idea_dict, result in results:
            output['results'].append({
                'idea_id': idea_dict.get('id'),
                'idea_title': idea_dict.get('title'),
                'stories_created': result.count
            })
        print(json.dumps(output, indent=2, ensure_ascii=False))
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
