"""Command-line interface for QASource."""

import click
import sys
from pathlib import Path
from .core.config import Config
from .plugins.stackexchange_plugin import StackExchangePlugin

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[5] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@click.group()
@click.version_option(version='1.0.0')
def main():
    """QASource - Gather questions from Q&A platforms."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), help='Path to .env file')
@click.option('--sites', '-s', help='StackExchange sites (comma-separated)')
@click.option('--tags', '-t', help='Tags to filter by (comma-separated)')
@click.option('--max-questions', '-m', type=int, help='Maximum questions to fetch')
@click.option('--no-interactive', is_flag=True, help='Disable interactive prompts')
def scrape(env_file, sites, tags, max_questions, no_interactive):
    """Scrape questions from StackExchange sites."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize central database only (single DB approach)
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        plugin = StackExchangePlugin(config)
        
        # Parse parameters
        site_list = [s.strip() for s in sites.split(',')] if sites else None
        tag_list = [t.strip() for t in tags.split(',')] if tags else None
        
        click.echo(f"Scraping from StackExchange sites...")
        click.echo(f"Sites: {site_list or config.stackexchange_sites}")
        click.echo(f"Tags: {tag_list or config.filter_tags}")
        click.echo("")
        
        # Scrape questions - returns List[IdeaInspiration]
        ideas = plugin.scrape(
            sites=site_list,
            tags=tag_list,
            max_questions=max_questions
        )
        
        total_scraped = len(ideas)
        total_saved_central = 0
        
        click.echo(f"\nFound {total_scraped} questions")
        
        # Save each IdeaInspiration to central database (single DB)
        for idea in ideas:
            central_saved = central_db.insert(idea)
            if central_saved:
                total_saved_central += 1
                click.echo(f"  ✓ Saved: {idea.title[:60]}")
            else:
                click.echo(f"  ↻ Updated: {idea.title[:60]}")
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total questions found: {total_scraped}")
        click.echo(f"Saved to central database: {total_saved_central}")
        click.echo(f"Central database: {central_db_path}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), help='Path to .env file')
@click.option('--limit', '-l', type=int, default=20, help='Maximum signals to display')
@click.option('--no-interactive', is_flag=True, help='Disable interactive prompts')
def list(env_file, limit, no_interactive):
    """List collected Q&A signals."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_url, interactive=not no_interactive)
        
        signals = db.get_all_signals(limit=limit)
        
        if not signals:
            click.echo("No signals found.")
            return
        
        click.echo(f"\n{'='*80}")
        click.echo(f"Q&A Signals ({len(signals)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, signal in enumerate(signals, 1):
            content = signal['content']
            analysis = signal['analysis']
            
            click.echo(f"{i}. [{signal['context']['platform'].upper()}] {content['title']}")
            click.echo(f"   Author: {content['author']}")
            click.echo(f"   Topics: {', '.join(analysis.get('topics', []))}")
            click.echo(f"   Scores: {signal['metrics']['upvotes']} upvotes, "
                      f"{signal['metrics']['replies']} answers")
            click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), help='Path to .env file')
@click.option('--no-interactive', is_flag=True, help='Disable interactive prompts')
def stats(env_file, no_interactive):
    """Show statistics about collected signals."""
    try:
        config = Config(env_file, interactive=not no_interactive)
        db = Database(config.database_url, interactive=not no_interactive)
        
        signals = db.get_all_signals(limit=1000)
        
        if not signals:
            click.echo("No signals collected yet.")
            return
        
        total = len(signals)
        by_platform = {}
        
        for signal in signals:
            platform = signal['context']['platform']
            by_platform[platform] = by_platform.get(platform, 0) + 1
        
        click.echo(f"\n{'='*50}")
        click.echo(f"Q&A Signal Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Signals: {total}\n")
        
        click.echo(f"Signals by Platform:")
        for platform, count in sorted(by_platform.items()):
            percentage = (count / total) * 100
            click.echo(f"  {platform}: {count} ({percentage:.1f}%)")
        click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
