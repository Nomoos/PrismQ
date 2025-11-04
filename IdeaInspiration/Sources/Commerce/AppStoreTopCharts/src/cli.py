"""Command-line interface for PrismQ.IdeaInspiration.Sources.Commerce.AppStoreTopCharts."""

import click
import sys
from pathlib import Path
from .core.config import Config
from .plugins.google_play_plugin import GooglePlayPlugin
from .plugins.apple_app_store_plugin import AppleAppStorePlugin

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[5] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ App Store Top Charts Source - Gather app trends from app stores."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--platform', '-p', type=click.Choice(['google', 'apple', 'both']), 
              default='both', help='Platform to scrape')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, platform, no_interactive):
    """Scrape top apps from app stores.
    
    This command scrapes app data from Google Play Store and/or Apple App Store
    top charts across configured categories.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize central database only (single DB approach)
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        total_scraped = 0
        total_saved_central = 0
        
        # Scrape Google Play
        if platform in ['google', 'both']:
            click.echo("\n=== Google Play Store ===")
            try:
                google_plugin = GooglePlayPlugin(config)
                ideas = google_plugin.scrape()
                total_scraped += len(ideas)
                
                for idea in ideas:
                    central_saved = central_db.insert(idea)
                    if central_saved:
                        total_saved_central += 1
                        click.echo(f"  ✓ Saved: {idea.title[:60]}")
                    else:
                        click.echo(f"  ↻ Updated: {idea.title[:60]}")
                        
            except ValueError as e:
                click.echo(f"Google Play scraping skipped: {e}", err=True)
            except Exception as e:
                click.echo(f"Error scraping Google Play: {e}", err=True)
        
        # Scrape Apple App Store
        if platform in ['apple', 'both']:
            click.echo("\n=== Apple App Store ===")
            try:
                apple_plugin = AppleAppStorePlugin(config)
                ideas = apple_plugin.scrape()
                total_scraped += len(ideas)
                
                for idea in ideas:
                    central_saved = central_db.insert(idea)
                    if central_saved:
                        total_saved_central += 1
                        click.echo(f"  ✓ Saved: {idea.title[:60]}")
                    else:
                        click.echo(f"  ↻ Updated: {idea.title[:60]}")
                        
            except ValueError as e:
                click.echo(f"Apple App Store scraping skipped: {e}", err=True)
            except Exception as e:
                click.echo(f"Error scraping Apple App Store: {e}", err=True)
        
        click.echo(f"\n{'='*50}")
        click.echo(f"Scraping complete!")
        click.echo(f"Total apps found: {total_scraped}")
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
              help='Maximum number of apps to display')
@click.option('--category', '-c', help='Filter by category')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, category, no_interactive):
    """List collected apps."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        if category:
            apps = db.get_products_by_category(category, limit=limit)
        else:
            apps = db.get_all_products(limit=limit)
        
        if not apps:
            click.echo("No apps found.")
            return
        
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Apps ({len(apps)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, app in enumerate(apps, 1):
            click.echo(f"{i}. [{app['category']}] {app['title']}")
            click.echo(f"   App ID: {app['source_id']}")
            if app['brand']:
                click.echo(f"   Developer: {app['brand']}")
            if app['price'] is not None:
                if app['price'] == 0:
                    click.echo(f"   Price: Free")
                else:
                    click.echo(f"   Price: ${app['price']} {app['currency']}")
            if app['score']:
                click.echo(f"   Score: {app['score']:.2f}")
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
    """Show statistics about collected apps."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_path, interactive=not no_interactive)
        
        statistics = db.get_statistics()
        
        if statistics['total'] == 0:
            click.echo("No apps collected yet.")
            return
        
        # Build output as a string first to avoid Click dict iteration bug
        output_lines = []
        output_lines.append("\n" + "=" * 50)
        output_lines.append("App Collection Statistics")
        output_lines.append("=" * 50 + "\n")
        output_lines.append(f"Total Apps: {statistics['total']}\n")
        
        if statistics.get('by_source'):
            output_lines.append("Apps by Source:")
            for source, count in sorted(statistics['by_source'].items()):
                percentage = (count / statistics['total']) * 100
                output_lines.append(f"  {source}: {count} ({percentage:.1f}%)")
            output_lines.append("")
        
        if statistics.get('by_category'):
            output_lines.append("Top Categories:")
            # Convert to list before iterating to avoid Click bug
            cat_list = [(k, v) for k, v in statistics['by_category'].items()]
            for category, count in cat_list[:10]:
                percentage = (count / statistics['total']) * 100
                output_lines.append(f"  {category}: {count} ({percentage:.1f}%)")
            output_lines.append("")
        
        # Output everything at once
        click.echo("\n".join(output_lines))
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.confirmation_option(prompt='Are you sure you want to clear all apps?')
def clear(env_file, no_interactive):
    """Clear all apps from the database."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        
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
