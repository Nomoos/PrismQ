"""Command-line interface for PrismQ.IdeaInspiration.Sources.Creative.VisualMoodboardSource."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .plugins.unsplash_plugin import UnsplashPlugin
from .plugins.manual_import_plugin import ManualImportPlugin

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[5] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path



@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Visual Moodboard Source - Gather creative inspiration from visual aesthetics."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--query', '-q', help='Search query for visuals')
@click.option('--max-results', '-n', type=int, help='Maximum number of results')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, query, max_results, no_interactive):
    """Scrape visual resources from Unsplash API.
    
    Examples:
        python -m src.cli scrape --query "nature landscapes"
        python -m src.cli scrape --query "minimalist design" --max-results 20
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Unsplash plugin
        try:
            unsplash_plugin = UnsplashPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            click.echo("\nTo use Unsplash API:", err=True)
            click.echo("1. Create account at https://unsplash.com/developers", err=True)
            click.echo("2. Create application and get Access Key", err=True)
            click.echo("3. Set UNSPLASH_ACCESS_KEY in .env file", err=True)
            click.echo("4. Install python-unsplash: pip install python-unsplash", err=True)
            sys.exit(1)
        
        # Scrape from Unsplash
        total_scraped = 0
        total_saved = 0
        
        search_query = query or None  # None gets curated photos
        click.echo(f"Scraping visual resources from Unsplash...")
        if search_query:
            click.echo(f"Search query: {search_query}")
        else:
            click.echo("Getting curated photos...")
        if max_results:
            click.echo(f"Max results: {max_results}")
        click.echo()
        
        try:
            resources = unsplash_plugin.scrape(query=search_query, max_results=max_results)
            total_scraped = len(resources)
            click.echo(f"Found {len(resources)} visual resources")
            
            # Process and save each resource
            for resource in resources:
                # Convert platform metrics to creative metrics
                creative_metrics = CreativeMetrics.from_unsplash(resource['metrics'])
                
                # Save to database
                success = db.insert_resource(
                    source='unsplash',
                    source_id=resource['source_id'],
                    title=resource['title'],
                    content=resource.get('url', ''),  # Store URL as content
                    tags=resource['tags'],
                    score=creative_metrics.inspiration_value or 0.0,
                    score_dictionary=creative_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
                    click.echo(f"✓ Saved: {resource['title'][:60]}...")
            
        except Exception as e:
            click.echo(f"Error scraping Unsplash: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total visual resources found: {total_scraped}")
        click.echo(f"Total visual resources saved: {total_saved}")
        click.echo(f"Database: {config.database_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--count', '-c', type=int, default=10, help='Number of random photos')
@click.option('--query', '-q', help='Optional filter query')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def random(env_file, count, query, no_interactive):
    """Get random visual inspiration from Unsplash.
    
    Examples:
        python -m src.cli random --count 15
        python -m src.cli random --query "architecture" --count 20
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize Unsplash plugin
        try:
            unsplash_plugin = UnsplashPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        click.echo(f"Getting {count} random photos from Unsplash...")
        if query:
            click.echo(f"Filter: {query}")
        click.echo()
        
        try:
            resources = unsplash_plugin.get_random_photos(count=count, query=query)
            total_scraped = len(resources)
            total_saved = 0
            
            for resource in resources:
                creative_metrics = CreativeMetrics.from_unsplash(resource['metrics'])
                
                success = db.insert_resource(
                    source='unsplash',
                    source_id=resource['source_id'],
                    title=resource['title'],
                    content=resource.get('url', ''),
                    tags=resource['tags'],
                    score=creative_metrics.inspiration_value or 0.0,
                    score_dictionary=creative_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
                    click.echo(f"✓ Saved: {resource['title'][:60]}...")
        
            click.echo(f"\nRandom fetch complete!")
            click.echo(f"Total photos found: {total_scraped}")
            click.echo(f"Total photos saved: {total_saved}")
            click.echo(f"Database: {config.database_path}")
            
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
    """Import visual resources from JSON or CSV file.
    
    Examples:
        python -m src.cli import-file --file visuals.json
        python -m src.cli import-file --file visuals.csv
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
                content=resource.get('content', ''),
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
    """List collected visual resources."""
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
            click.echo("No visual resources found.")
            return
        
        # Display resources
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Visual Resources ({len(resources)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, resource in enumerate(resources, 1):
            click.echo(f"{i}. [{resource['source'].upper()}] {resource['title']}")
            click.echo(f"   ID: {resource['source_id']}")
            if resource['tags']:
                click.echo(f"   Tags: {resource['tags']}")
            if resource['content']:
                # Show URL for visual content
                click.echo(f"   URL: {resource['content'][:80]}")
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
    """Show statistics about collected visual resources."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get all resources
        resources = db.get_all_resources(limit=10000)  # Get all
        
        if not resources:
            click.echo("No visual resources collected yet.")
            return
        
        # Calculate statistics
        total = len(resources)
        by_source = {}
        
        for resource in resources:
            source = resource['source']
            by_source[source] = by_source.get(source, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Visual Resource Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Resources: {total}\n")
        click.echo(f"Resources by Source:")
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
@click.confirmation_option(prompt='Are you sure you want to clear all visual resources?')
def clear(env_file, no_interactive):
    """Clear all visual resources from the database."""
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
