"""Command-line interface for PrismQ.IdeaInspiration.Sources.Internal.CSVImport."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .plugins.csv_import_plugin import CSVImportPlugin

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[5] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ CSV Import Source - Import idea inspirations from CSV/Excel files."""
    pass


@main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.option('--batch-id', '-b', type=str,
              help='Optional batch identifier for this import')
def import_file(file_path, env_file, no_interactive, batch_id):
    """Import ideas from a CSV or Excel file.
    
    FILE_PATH: Path to the CSV or Excel file to import
    
    Example:
        csv-import import-file data/ideas.csv
        csv-import import-file data/ideas.xlsx --batch-id migration_2025
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize central database only (single DB approach)
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Initialize plugin
        plugin = CSVImportPlugin(config)
        
        # Import ideas
        click.echo(f"\nImporting ideas from: {file_path}")
        ideas = plugin.scrape(file_path, batch_id)
        
        if not ideas:
            click.echo("No ideas to import.", err=True)
            sys.exit(1)
        
        # Save to central database
        click.echo(f"\nSaving {len(ideas)} ideas to database...")
        saved_count = 0
        for idea in ideas:
            if central_db.insert(idea):
                saved_count += 1
        
        click.echo(f"\n✓ Successfully imported {saved_count} ideas!")
        click.echo(f"Central database: {central_db_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.option('--pattern', '-p', type=str, default='*.csv',
              help='File pattern to match (default: *.csv)')
@click.option('--directory', '-d', type=click.Path(exists=True), required=True,
              help='Directory containing CSV/Excel files')
def import_directory(env_file, no_interactive, pattern, directory):
    """Import ideas from all CSV/Excel files in a directory.
    
    Example:
        csv-import import-directory -d data/imports/
        csv-import import-directory -d data/ -p "*.xlsx"
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Initialize plugin
        plugin = CSVImportPlugin(config)
        
        # Find all matching files
        dir_path = Path(directory)
        file_paths = list(dir_path.glob(pattern))
        
        if not file_paths:
            click.echo(f"No files matching pattern '{pattern}' found in {directory}", err=True)
            sys.exit(1)
        
        click.echo(f"Found {len(file_paths)} file(s) to import:")
        for fp in file_paths:
            click.echo(f"  - {fp}")
        
        # Import all files
        results = plugin.import_multiple_files([str(fp) for fp in file_paths])
        
        # Save all ideas
        total_saved = 0
        for file_result in results['file_results']:
            if file_result['success']:
                click.echo(f"\nProcessing: {file_result['file_path']}")
                ideas = plugin.scrape(file_result['file_path'])
                saved = db.save_ideas(ideas)
                total_saved += saved
                click.echo(f"  ✓ Saved {saved} ideas")
        
        # Show summary
        click.echo(f"\n{'='*60}")
        click.echo("Import Summary:")
        click.echo(f"  Total files processed: {results['total_files']}")
        click.echo(f"  Successful: {results['successful_files']}")
        click.echo(f"  Failed: {results['failed_files']}")
        click.echo(f"  Total ideas imported: {total_saved}")
        click.echo(f"{'='*60}")
        
        # Show statistics
        stats = db.get_stats()
        click.echo("\nDatabase Statistics:")
        click.echo(f"  Total ideas: {stats['total']}")
        click.echo(f"  By status: {stats['by_status']}")
        click.echo(f"  By category: {stats['by_category']}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument('file_path', type=click.Path(exists=True))
def validate(file_path):
    """Validate CSV/Excel file structure without importing.
    
    FILE_PATH: Path to the CSV or Excel file to validate
    
    Example:
        csv-import validate data/ideas.csv
    """
    try:
        from .core.csv_parser import CSVParser
        
        parser = CSVParser()
        validation = parser.validate_csv_structure(file_path)
        
        click.echo(f"\nValidation Results for: {file_path}")
        click.echo(f"{'='*60}")
        
        if validation['valid']:
            click.echo("✓ File structure is valid")
        else:
            click.echo("✗ File structure is invalid", err=True)
            if 'error' in validation:
                click.echo(f"  Error: {validation['error']}")
            if 'suggestions' in validation:
                click.echo("  Suggestions:")
                for suggestion in validation['suggestions']:
                    click.echo(f"    - {suggestion}")
            sys.exit(1)
        
        click.echo(f"\nFile Details:")
        click.echo(f"  Total rows: {validation.get('total_rows', 'N/A')}")
        click.echo(f"  Columns: {', '.join(validation.get('columns', []))}")
        
        click.echo(f"\nColumn Mapping:")
        click.echo(f"  ✓ Title column: {validation.get('has_title', False)}")
        click.echo(f"  {'✓' if validation.get('has_description') else '✗'} Description column: {validation.get('has_description', False)}")
        click.echo(f"  {'✓' if validation.get('has_category') else '✗'} Category column: {validation.get('has_category', False)}")
        click.echo(f"  {'✓' if validation.get('has_priority') else '✗'} Priority column: {validation.get('has_priority', False)}")
        click.echo(f"  {'✓' if validation.get('has_tags') else '✗'} Tags column: {validation.get('has_tags', False)}")
        click.echo(f"  {'✓' if validation.get('has_status') else '✗'} Status column: {validation.get('has_status', False)}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.option('--status', '-s', type=str,
              help='Filter by status')
@click.option('--category', '-c', type=str,
              help='Filter by category')
@click.option('--limit', '-l', type=int,
              help='Limit number of results')
@click.option('--format', '-f', type=click.Choice(['table', 'json']), default='table',
              help='Output format (default: table)')
def list_ideas(env_file, no_interactive, status, category, limit, format):
    """List imported ideas from the database.
    
    Example:
        csv-import list --status new
        csv-import list --category content --limit 10
        csv-import list --format json
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get ideas
        ideas = db.get_ideas(status=status, category=category, limit=limit)
        
        if not ideas:
            click.echo("No ideas found.")
            return
        
        if format == 'json':
            click.echo(json.dumps(ideas, indent=2))
        else:
            # Table format
            click.echo(f"\nFound {len(ideas)} idea(s):\n")
            click.echo(f"{'ID':<20} {'Title':<40} {'Status':<12} {'Category':<15} {'Priority':<10}")
            click.echo("="*100)
            
            for idea in ideas:
                source_id = idea['source_id'][:18]
                title = idea['idea']['title'][:38]
                status_val = idea['metadata']['status'][:10]
                category_val = idea['idea']['category'][:13]
                priority_val = idea['idea']['priority'][:8]
                
                click.echo(f"{source_id:<20} {title:<40} {status_val:<12} {category_val:<15} {priority_val:<10}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def stats(env_file, no_interactive):
    """Show database statistics.
    
    Example:
        csv-import stats
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get statistics
        stats = db.get_stats()
        
        click.echo("\nDatabase Statistics:")
        click.echo(f"{'='*60}")
        click.echo(f"Total ideas: {stats['total']}")
        
        if stats['by_status']:
            click.echo(f"\nBy Status:")
            for status, count in stats['by_status'].items():
                click.echo(f"  {status}: {count}")
        
        if stats['by_category']:
            click.echo(f"\nBy Category:")
            for category, count in stats['by_category'].items():
                click.echo(f"  {category}: {count}")
        
        if stats['by_priority']:
            click.echo(f"\nBy Priority:")
            for priority, count in stats['by_priority'].items():
                click.echo(f"  {priority}: {count}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
