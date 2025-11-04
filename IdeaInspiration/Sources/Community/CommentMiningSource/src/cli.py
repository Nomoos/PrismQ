"""Command-line interface for CommentMiningSource."""

import click
import sys
from pathlib import Path
from .core.config import Config
from .plugins.multiplatform_plugin import MultiPlatformCommentPlugin

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[5] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@click.group()
@click.version_option(version='1.0.0')
def main():
    """Comment Mining Source - Extract ideas from platform comments."""
    pass


@click.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, no_interactive):
    """Scrape comments from multiple platforms.
    
    NOTE: Placeholder implementation.
    Full implementation would scrape YouTube, Instagram, TikTok comments.
    
    Examples:
        python -m src.cli scrape
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize central database only (single DB approach)
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Initialize plugin
        plugin = MultiPlatformCommentPlugin(config)
        
        click.echo("Scraping comments from platforms...")
        click.echo()
        
        # Scrape - returns List[IdeaInspiration]
        ideas = plugin.scrape()
        
        if ideas:
            # Save each IdeaInspiration to central database (single DB)
            total_saved = 0
            for idea in ideas:
                central_saved = central_db.insert(idea)
                if central_saved:
                    total_saved += 1
                    click.echo(f"  ✓ Saved: {idea.title[:60]}")
            
            click.echo(f"\nTotal saved: {total_saved}")
            click.echo(f"Central database: {central_db_path}")
        else:
            click.echo("No comments found (placeholder mode)")
            click.echo("\nFull implementation would scrape from:")
            click.echo("  - YouTube comments")
            click.echo("  - Instagram comments")
            click.echo("  - TikTok comments")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


main.add_command(scrape)

if __name__ == '__main__':
    main()
