#!/usr/bin/env python3
"""CLI script for creating stories with titles from an Idea.

This tool accepts an Idea (via text input, JSON, or file) and creates 10 Story
objects with their initial Titles (v0).

Usage:
    python create_stories.py "idea title" "concept description"
    python create_stories.py --file idea.json
    python create_stories.py --idea-id "my-idea-123" "AI in Healthcare" "Medical AI trends"
    python create_stories.py --db prismq.db "My Idea Title" "My idea concept"

Examples:
    # From title and concept
    python create_stories.py "The Future of AI" "An exploration of AI trends"
    
    # With explicit idea ID
    python create_stories.py --idea-id "future-ai-2024" "Future of AI" "AI trends exploration"
    
    # From JSON file
    python create_stories.py --file idea.json
    
    # With database persistence
    python create_stories.py --db prismq.db "My Idea" "My concept description"
    
    # Output as JSON
    python create_stories.py "My Idea" "My concept" --json
"""

import sys
import os
import argparse
import json
import sqlite3
from pathlib import Path

# Setup paths for imports
# Script location: T/Title/From/Idea/_meta/scripts/create_stories.py
# Need to add: project_root (parent of T) and various module paths
script_dir = Path(__file__).parent.absolute()

# Navigate to project root (parent of T directory)
# _meta/scripts -> _meta -> Idea -> From -> Title -> T -> project_root
project_root = script_dir.parent.parent.parent.parent.parent.parent
src_dir = script_dir.parent.parent / 'src'
idea_model_dir = project_root / 'T' / 'Idea' / 'Model' / 'src'

# Ensure all required paths are in sys.path
for path in [str(project_root), str(src_dir), str(idea_model_dir)]:
    if path not in sys.path:
        sys.path.insert(0, path)

from idea import Idea, IdeaStatus, ContentGenre
from story_title_service import (
    StoryTitleService,
    StoryTitleResult,
    create_stories_from_idea,
)
from title_generator import TitleConfig


def parse_json_input(json_text: str) -> tuple:
    """Parse JSON input and extract idea fields.
    
    Args:
        json_text: JSON string with idea data
        
    Returns:
        Tuple of (title, concept, idea_id, genre)
    """
    data = json.loads(json_text)
    
    title = (
        data.get('title') or 
        data.get('story_title') or 
        data.get('name') or 
        'Untitled Idea'
    )
    
    concept = (
        data.get('concept') or 
        data.get('description') or 
        data.get('theme') or
        ''
    )
    
    idea_id = data.get('id') or data.get('idea_id')
    
    genre_str = data.get('genre', 'educational')
    try:
        genre = ContentGenre(genre_str.upper())
    except (ValueError, AttributeError):
        genre = ContentGenre.EDUCATIONAL
    
    return title, concept, idea_id, genre


def print_result(result: StoryTitleResult, as_json: bool = False):
    """Pretty print the creation result."""
    if as_json:
        output = {
            'idea_id': result.idea_id,
            'story_count': result.count,
            'stories': [],
        }
        for story, title in result.get_story_title_pairs():
            output['stories'].append({
                'story_id': story.id,
                'idea_id': story.idea_id,
                'state': story.state.value,
                'title_id': title.id,
                'title_version': title.version,
                'title_text': title.text,
            })
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return
    
    print()
    print("=" * 70)
    print("  PrismQ - Stories Created from Idea")
    print("=" * 70)
    print(f"  Idea ID: {result.idea_id}")
    print(f"  Stories Created: {result.count}")
    print("=" * 70)
    print()
    
    for i, (story, title) in enumerate(result.get_story_title_pairs(), 1):
        print(f"  Story {i}:")
        print(f"    ID: {story.id}")
        print(f"    State: {story.state.value}")
        print(f"    Title (v{title.version}): {title.text}")
        print()
    
    print("=" * 70)
    print(f"  Total: {result.count} stories with titles created")
    print("=" * 70)
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Create Stories with Titles from an Idea',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From title and concept
  python create_stories.py "The Future of AI" "An exploration of AI trends"
  
  # With explicit idea ID  
  python create_stories.py --idea-id "future-ai-2024" "Future of AI" "AI trends"
  
  # From JSON file
  python create_stories.py --file idea.json
  
  # With database persistence
  python create_stories.py --db prismq.db "My Idea" "My concept"
  
  # Allow duplicate stories for same idea
  python create_stories.py --allow-duplicates "My Idea" "My concept"
  
  # Output as JSON
  python create_stories.py "My Idea" "My concept" --json
        """
    )
    
    parser.add_argument('title', nargs='?', help='Idea title')
    parser.add_argument('concept', nargs='?', help='Idea concept/description')
    parser.add_argument('--file', '-f', help='Read idea from JSON file')
    parser.add_argument('--idea-id', '-i', help='Explicit idea identifier')
    parser.add_argument('--db', '-d', help='SQLite database path for persistence')
    parser.add_argument('--allow-duplicates', '-a', action='store_true', 
                        help='Allow creating stories even if idea already has stories')
    parser.add_argument('--json', '-j', action='store_true', help='Output as JSON')
    parser.add_argument('--genre', '-g', default='educational',
                        choices=['educational', 'entertainment', 'news', 'documentary', 'narrative'],
                        help='Content genre (default: educational)')
    
    args = parser.parse_args()
    
    # Get idea data
    title = None
    concept = None
    idea_id = args.idea_id
    genre = ContentGenre.EDUCATIONAL
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try to parse as JSON
            if content.strip().startswith('{'):
                title, concept, file_idea_id, genre = parse_json_input(content)
                if not idea_id:
                    idea_id = file_idea_id
            else:
                # Plain text - first line is title, rest is concept
                lines = content.strip().split('\n')
                title = lines[0] if lines else 'Untitled'
                concept = '\n'.join(lines[1:]) if len(lines) > 1 else ''
                
        except FileNotFoundError:
            print(f"Error: File not found: {args.file}")
            return 1
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return 1
        except Exception as e:
            print(f"Error reading file: {e}")
            return 1
    elif args.title:
        title = args.title
        concept = args.concept or ''
        try:
            genre = ContentGenre[args.genre.upper()]
        except KeyError:
            genre = ContentGenre.EDUCATIONAL
    else:
        parser.print_help()
        return 1
    
    if not title:
        print("Error: Idea title is required")
        return 1
    
    # Create Idea object
    idea = Idea(
        title=title,
        concept=concept,
        genre=genre,
        status=IdeaStatus.DRAFT
    )
    
    if not args.json:
        print()
        print("=" * 70)
        print("  PrismQ - Story Creator from Idea")
        print("=" * 70)
        print(f"  Title: {title}")
        if concept:
            concept_preview = concept[:60] + '...' if len(concept) > 60 else concept
            print(f"  Concept: {concept_preview}")
        if idea_id:
            print(f"  Idea ID: {idea_id}")
        print(f"  Genre: {genre.value if hasattr(genre, 'value') else genre}")
        if args.db:
            print(f"  Database: {args.db}")
        print()
    
    # Create database connection if specified
    connection = None
    if args.db:
        try:
            connection = sqlite3.connect(args.db)
            connection.row_factory = sqlite3.Row
            
            # Ensure tables exist
            service = StoryTitleService(connection)
            service.ensure_tables_exist()
            
            if not args.json:
                print(f"  [INFO] Database connected: {args.db}")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return 1
    
    # Create stories
    try:
        skip_if_exists = not args.allow_duplicates
        result = create_stories_from_idea(
            idea,
            connection=connection,
            idea_id=idea_id,
            skip_if_exists=skip_if_exists
        )
        
        if result is None:
            if not args.json:
                print("  [INFO] Idea already has stories - skipped")
                print("  Use --allow-duplicates to create stories anyway")
                print()
            else:
                print(json.dumps({'status': 'skipped', 'reason': 'idea_already_has_stories'}))
            return 0
        
        print_result(result, as_json=args.json)
        
    except Exception as e:
        print(f"Error creating stories: {e}")
        return 1
    finally:
        if connection:
            connection.close()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
