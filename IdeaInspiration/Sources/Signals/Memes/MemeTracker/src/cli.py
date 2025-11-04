"""Command-line interface for MemeTrackerSource."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .plugins.meme_tracker_plugin import MemeTrackerPlugin

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[6] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@click.group()
@click.version_option(version='1.0.0')
def main():
    """Meme Tracker Source - Gather signal inspirations from viral memes."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--limit', '-l', type=int,
              help='Maximum number of results')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, limit, no_interactive):
    """Scrape memes.
    
    Examples:
        python -m src.cli scrape
        python -m src.cli scrape --limit 20
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize central database only (single DB approach)
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Initialize plugin
        try:
            plugin = MemeTrackerPlugin(config)
        except Exception as e:
            click.echo(f"Error initializing plugin: {e}", err=True)
            sys.exit(1)
        
        # Scrape
        total_scraped = 0
        total_saved_central = 0
        
        click.echo("Scraping...")
        click.echo()
        
        try:
            # Scrape - returns List[IdeaInspiration]
            ideas = plugin.scrape(limit=limit) if limit else plugin.scrape()
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} memes")
            
            # Save each IdeaInspiration to central database (single DB)
            for idea in ideas:
                central_saved = central_db.insert(idea)
                if central_saved:
                    total_saved_central += 1
                    click.echo(f"  ✓ Saved: {idea.title[:60]}")
                else:
                    click.echo(f"  ↻ Updated: {idea.title[:60]}")
            
        except Exception as e:
            click.echo(f"Error scraping: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total found: {total_scraped}")
        click.echo(f"Saved to central database: {total_saved_central}")
        click.echo(f"Central database: {central_db_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
