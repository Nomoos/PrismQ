"""Command-line interface for InstagramHashtagSource."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .plugins.instagram_hashtag import InstagramHashtagPlugin

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[6] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@click.group()
@click.version_option(version='1.0.0')
def main():
    """Instagram Hashtag Source - Gather signal inspirations from Instagram hashtags - Gather signal inspirations from hashtags."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--hashtags', '-k', multiple=True,
              help='Additional keywords to track (can be specified multiple times)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, keywords, no_interactive):
    """Scrape trending hashtags from Instagram..
    
    This command scrapes current hashtags from Instagram
    and optionally searches for specific keywords.
    
    Examples:
        python -m src.cli scrape
        python -m src.cli scrape --hashtags "AI" --hashtags "technology"
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize central database only (single DB approach)
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Initialize Instagram plugin
        try:
            news_plugin = InstagramHashtagPlugin(config)
        except Exception as e:
            click.echo(f"Error initializing Instagram: {e}", err=True)
            click.echo("\nInstall instagrapi with: pip install instagrapi", err=True)
            sys.exit(1)
        
        # Scrape from Instagram
        total_scraped = 0
        total_saved_central = 0
        
        click.echo("Scraping from Instagram...")
        if keywords:
            click.echo(f"Keywords: {', '.join(keywords)}")
        click.echo()
        
        try:
            # Convert keywords tuple to list
            keyword_list = list(keywords) if keywords else None
            
            # Scrape news - returns List[IdeaInspiration]
            ideas = news_plugin.scrape(query=keyword_list[0] if keyword_list else None)
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} hashtags")
            
            # Save each IdeaInspiration to central database (single DB)
            for idea in ideas:
                central_saved = central_db.insert(idea)
                if central_saved:
                    total_saved_central += 1
                    click.echo(f"  ✓ Saved: {idea.title[:60]}")
                else:
                    click.echo(f"  ↻ Updated: {idea.title[:60]}")
            
        except Exception as e:
            click.echo(f"Error scraping Instagram: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total articles found: {total_scraped}")
        click.echo(f"Saved to central database: {total_saved_central}")
        click.echo(f"Central database: {central_db_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--limit', '-l', type=int, default=20, 
              help='Maximum number of ideas to display')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, no_interactive):
    """List collected news ideas from central database."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open central database
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Get ideas from Instagram source
        ideas = central_db.get_by_source_platform("instagram_hashtag", limit=limit)
        
        if not ideas:
            click.echo("No news ideas found in central database.")
            return
        
        # Display ideas
        click.echo(f"\n{'='*80}")
        click.echo(f"News Ideas from Central Database ({len(ideas)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, idea in enumerate(ideas, 1):
            click.echo(f"{i}. {idea.title}")
            if idea.description:
                click.echo(f"   Description: {idea.description[:100]}...")
            if idea.keywords:
                click.echo(f"   Tags: {', '.join(idea.keywords[:5])}")
            if idea.source_url:
                click.echo(f"   URL: {idea.source_url}")
            click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def stats(env_file, no_interactive):
    """Show statistics about collected news ideas."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open central database
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Get all news ideas
        ideas = central_db.get_by_source_platform("instagram_hashtag")
        
        if not ideas:
            click.echo("No news ideas collected yet.")
            return
        
        # Calculate statistics
        total = len(ideas)
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"News Idea Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total News Ideas: {total}\n")
        click.echo(f"Source Platform: news_api")
        click.echo(f"Central Database: {central_db_path}")
        click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output file path (JSON format)')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def export(env_file, output, no_interactive):
    """Export news ideas to JSON file."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open central database
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Get news ideas
        ideas = central_db.get_by_source_platform("instagram_hashtag")
        
        if not ideas:
            click.echo("No news ideas to export.")
            return
        
        # Export to file
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert IdeaInspiration objects to dictionaries
        ideas_dict = [idea.to_dict() for idea in ideas]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ideas_dict, f, indent=2, ensure_ascii=False)
        
        click.echo(f"Exported {len(ideas)} news ideas to {output}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.confirmation_option(prompt='Are you sure you want to clear all news ideas from central database?')
def clear(env_file, no_interactive):
    """Clear all news ideas from the central database."""
    try:
        # Note: This command is deprecated in single DB approach
        # Central database should not be cleared per-source
        click.echo("Warning: Cannot clear central database from individual source module.")
        click.echo("Use Model/idea_inspiration_db.py tools to manage central database.")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
