"""Command-line interface for InstagramAudioTrendsSource."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .plugins.instagram_audio_trends_plugin import InstagramAudioTrendsPlugin

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[6] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@click.group()
@click.version_option(version='1.0.0')
def main():
    """Instagram Audio Trends Source - Gather signal inspirations from trending Instagram Reels audio."""
    pass


@click.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--limit', '-l', type=int,
              help='Maximum number of results')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, limit, no_interactive):
    """Scrape trending audio from Instagram Reels.
    
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
        
        # Initialize Instagram Audio Trends plugin
        try:
            audio_plugin = InstagramAudioTrendsPlugin(config)
        except Exception as e:
            click.echo(f"Error initializing Instagram Audio Trends plugin: {e}", err=True)
            sys.exit(1)
        
        # Scrape from Instagram
        total_scraped = 0
        total_saved_central = 0
        
        click.echo("Scraping trending audio from Instagram Reels...")
        click.echo()
        
        try:
            # Scrape audio - returns List[IdeaInspiration]
            ideas = audio_plugin.scrape(limit=limit) if limit else audio_plugin.scrape()
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} trending audio clips")
            
            # Save each IdeaInspiration to central database (single DB)
            for idea in ideas:
                central_saved = central_db.insert(idea)
                if central_saved:
                    total_saved_central += 1
                    click.echo(f"  ✓ Saved: {idea.title[:60]}")
                else:
                    click.echo(f"  ↻ Updated: {idea.title[:60]}")
            
        except Exception as e:
            click.echo(f"Error scraping Instagram audio: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total audio clips found: {total_scraped}")
        click.echo(f"Saved to central database: {total_saved_central}")
        click.echo(f"Central database: {central_db_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


main.add_command(scrape)

if __name__ == '__main__':
    main()
