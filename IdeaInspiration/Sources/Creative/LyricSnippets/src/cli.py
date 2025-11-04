"""Command-line interface for PrismQ.IdeaInspiration.Sources.Creative.LyricSnippets."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .plugins.genius_plugin import GeniusPlugin
from .plugins.manual_import_plugin import ManualImportPlugin

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[6] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Lyric Snippets Source - Gather creative inspiration from song lyrics."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--query', '-q', help='Search query for lyrics')
@click.option('--max-results', '-n', type=int, help='Maximum number of results')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, query, max_results, no_interactive):
    """Scrape lyric snippets from Genius API.
    
    Examples:
        python -m src.cli scrape --query "love songs"
        python -m src.cli scrape --query "hip hop" --max-results 20
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize central database only (single DB approach)
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Initialize Genius plugin
        try:
            genius_plugin = GeniusPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            click.echo("\nTo use Genius API:", err=True)
            click.echo("1. Get API key from https://genius.com/api-clients", err=True)
            click.echo("2. Set GENIUS_API_KEY in .env file", err=True)
            click.echo("3. Install lyricsgenius: pip install lyricsgenius", err=True)
            sys.exit(1)
        
        # Scrape from Genius
        total_scraped = 0
        total_saved_central = 0
        
        search_query = query or "trending songs"
        click.echo(f"Scraping lyric snippets from Genius...")
        click.echo(f"Search query: {search_query}")
        if max_results:
            click.echo(f"Max results: {max_results}")
        click.echo()
        
        try:
            # Plugin returns List[IdeaInspiration]
            ideas = genius_plugin.scrape(search_query=search_query, max_results=max_results)
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} lyric snippets")
            
            # Save each IdeaInspiration to central database (single DB)
            for idea in ideas:
                central_saved = central_db.insert(idea)
                if central_saved:
                    total_saved_central += 1
                    click.echo(f"✓ Saved: {idea.title[:60]}...")
            
        except Exception as e:
            click.echo(f"Error scraping Genius: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total snippets found: {total_scraped}")
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
@click.option('--title', '-t', required=True, help='Song title')
@click.option('--artist', '-a', help='Artist name')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape_song(env_file, title, artist, no_interactive):
    """Scrape a specific song by title and artist.
    
    Examples:
        python -m src.cli scrape-song --title "Bohemian Rhapsody" --artist "Queen"
        python -m src.cli scrape-song --title "Imagine"
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Genius plugin
        try:
            genius_plugin = GeniusPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        click.echo(f"Searching for: {title}" + (f" by {artist}" if artist else ""))
        click.echo()
        
        try:
            resource = genius_plugin.get_song_by_title(title, artist)
            
            if not resource:
                click.echo(f"Song not found: {title}", err=True)
                sys.exit(1)
            
            # Convert to creative metrics
            creative_metrics = CreativeMetrics.from_genius(resource['metrics'])
            
            # Save to database
            success = db.insert_resource(
                source='genius',
                source_id=resource['source_id'],
                title=resource['title'],
                content=resource['content'],
                tags=resource['tags'],
                score=creative_metrics.inspiration_value or 0.0,
                score_dictionary=creative_metrics.to_dict()
            )
            
            if success:
                click.echo(f"✓ Saved: {resource['title']}")
            else:
                click.echo(f"⟳ Updated: {resource['title']}")
            
            click.echo(f"\nDatabase: {config.database_path}")
            
        except Exception as e:
            click.echo(f"Error: {e}", err=True)
            import traceback
            traceback.print_exc()
            sys.exit(1)
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--file', '-f', required=True, type=click.Path(exists=True),
              help='Path to JSON or CSV file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def import_file(env_file, file, no_interactive):
    """Import lyric snippets from JSON or CSV file.
    
    Examples:
        python -m src.cli import-file --file lyrics.json
        python -m src.cli import-file --file lyrics.csv
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize manual import plugin
        manual_plugin = ManualImportPlugin(config)
        
        file_path = Path(file)
        click.echo(f"Importing from: {file_path}")
        click.echo()
        
        # Import based on file extension
        if file_path.suffix.lower() == '.json':
            resources = manual_plugin.import_from_json(str(file_path))
        elif file_path.suffix.lower() == '.csv':
            resources = manual_plugin.import_from_csv(str(file_path))
        else:
            click.echo(f"Unsupported file format: {file_path.suffix}", err=True)
            click.echo("Supported formats: .json, .csv", err=True)
            sys.exit(1)
        
        if not resources:
            click.echo("No resources found in file.")
            return
        
        total_saved = 0
        
        for resource in resources:
            # Convert to creative metrics
            creative_metrics = CreativeMetrics.from_manual(resource['metrics'])
            
            # Save to database
            success = db.insert_resource(
                source='manual',
                source_id=resource['source_id'],
                title=resource['title'],
                content=resource['content'],
                tags=resource['tags'],
                score=creative_metrics.inspiration_value or 0.0,
                score_dictionary=creative_metrics.to_dict()
            )
            
            if success:
                total_saved += 1
                click.echo(f"✓ Imported: {resource['title'][:60]}...")
        
        click.echo(f"\nImport complete!")
        click.echo(f"Total resources imported: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--limit', '-l', type=int, default=20, 
              help='Maximum number of resources to display')
@click.option('--source', '-s', help='Filter by source')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, source, no_interactive):
    """List collected lyric snippets."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get resources
        resources = db.get_all_resources(limit=limit)
        
        # Filter by source if specified
        if source:
            resources = [r for r in resources if r['source'] == source]
        
        if not resources:
            click.echo("No lyric snippets found.")
            return
        
        # Display resources
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Lyric Snippets ({len(resources)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, resource in enumerate(resources, 1):
            click.echo(f"{i}. [{resource['source'].upper()}] {resource['title']}")
            click.echo(f"   ID: {resource['source_id']}")
            if resource['tags']:
                click.echo(f"   Tags: {resource['tags']}")
            if resource['content']:
                # Show first few lines
                lines = resource['content'].split('\n')[:3]
                preview = '\n   '.join(lines)
                click.echo(f"   Preview:\n   {preview}")
                if len(resource['content'].split('\n')) > 3:
                    click.echo("   ...")
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
    """Show statistics about collected lyric snippets."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get all resources
        resources = db.get_all_resources(limit=10000)  # Get all
        
        if not resources:
            click.echo("No lyric snippets collected yet.")
            return
        
        # Calculate statistics
        total = len(resources)
        by_source = {}
        
        for resource in resources:
            source = resource['source']
            by_source[source] = by_source.get(source, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Lyric Snippet Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Snippets: {total}\n")
        click.echo(f"Snippets by Source:")
        for source, count in sorted(by_source.items()):
            percentage = (count / total) * 100
            click.echo(f"  {source.capitalize()}: {count} ({percentage:.1f}%)")
        click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.confirmation_option(prompt='Are you sure you want to clear all lyric snippets?')
def clear(env_file, no_interactive):
    """Clear all lyric snippets from the database."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Delete database file
        db_path = Path(config.database_path)
        if db_path.exists():
            db_path.unlink()
            click.echo(f"Database cleared: {config.database_path}")
        else:
            click.echo("Database does not exist.")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
