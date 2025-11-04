"""Command-line interface for TikTokSoundsSource."""

import click
import sys
import json
from pathlib import Path
from .core.config import Config
from .plugins.tik_tok_sounds_plugin import TikTokSoundsPlugin

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[6] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@click.group()
@click.version_option(version='1.0.0')
def main():
    """TikTok Sounds Source - Gather signal inspirations from trending TikTok sounds."""
    pass


@click.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--limit', '-l', type=int,
              help='Maximum number of results')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, limit, no_interactive):
    """Scrape trending sounds from TikTok.
    
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
        
        # Initialize TikTok Sounds plugin
        try:
            sounds_plugin = TikTokSoundsPlugin(config)
        except Exception as e:
            click.echo(f"Error initializing TikTok Sounds plugin: {e}", err=True)
            sys.exit(1)
        
        # Scrape from TikTok
        total_scraped = 0
        total_saved_central = 0
        
        click.echo("Scraping trending sounds from TikTok...")
        click.echo()
        
        try:
            # Scrape sounds - returns List[IdeaInspiration]
            ideas = sounds_plugin.scrape(limit=limit) if limit else sounds_plugin.scrape()
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} trending sounds")
            
            # Save each IdeaInspiration to central database (single DB)
            for idea in ideas:
                central_saved = central_db.insert(idea)
                if central_saved:
                    total_saved_central += 1
                    click.echo(f"  ✓ Saved: {idea.title[:60]}")
                else:
                    click.echo(f"  ↻ Updated: {idea.title[:60]}")
            
        except Exception as e:
            click.echo(f"Error scraping TikTok sounds: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total sounds found: {total_scraped}")
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
        
        # Scrape from Google Trends
        total_scraped = 0
        total_saved = 0
        
        click.echo("Scraping from Google Trends...")
        click.echo(f"Region: {config.tik_tok_sounds_region}")
        click.echo(f"Timeframe: {config.tik_tok_sounds_timeframe}")
        if keywords:
            click.echo(f"Keywords: {', '.join(keywords)}")
        click.echo()
        
        try:
            # Convert keywords tuple to list
            keyword_list = list(keywords) if keywords else None
            
            # Scrape signals
            signals = trends_plugin.scrape(keywords=keyword_list)
            total_scraped = len(signals)
            click.echo(f"Found {len(signals)} signals from Google Trends")
            
            # Process and save each signal
            for signal in signals:
                # Convert platform metrics to universal metrics
                universal_metrics = UniversalMetrics.from_tik_tok_sounds(signal['metrics'])
                
                # Save to database with universal metrics
                success = db.insert_signal(
                    source='tik_tok_sounds',
                    source_id=signal['source_id'],
                    signal_type=signal['signal_type'],
                    name=signal['name'],
                    description=signal['description'],
                    tags=','.join(signal['tags']),
                    metrics=signal['metrics'],
                    temporal=signal['temporal'],
                    universal_metrics=universal_metrics.to_dict()
                )
                
                if success:
                    total_saved += 1
            
        except Exception as e:
            click.echo(f"Error scraping Google Trends: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total signals found: {total_scraped}")
        click.echo(f"Total signals saved: {total_saved}")
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
              help='Maximum number of signals to display')
@click.option('--type', '-t', help='Filter by signal type')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, type, no_interactive):
    """List collected signals."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get signals
        if type:
            signals = db.get_signals_by_type(type, limit=limit)
        else:
            signals = db.get_all_signals(limit=limit)
        
        if not signals:
            click.echo("No signals found.")
            return
        
        # Display signals
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Signals ({len(signals)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, signal in enumerate(signals, 1):
            click.echo(f"{i}. [{signal['signal_type'].upper()}] {signal['name']}")
            click.echo(f"   Source: {signal['source']} | ID: {signal['source_id']}")
            if signal.get('tags'):
                click.echo(f"   Tags: {signal['tags']}")
            if signal.get('description'):
                click.echo(f"   Description: {signal['description']}")
            if signal.get('universal_metrics'):
                um = signal['universal_metrics']
                click.echo(f"   Metrics: Strength={um.get('trend_strength', 0):.1f} | Virality={um.get('virality_score', 0):.1f}")
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
    """Show statistics about collected signals."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get all signals
        signals = db.get_all_signals()
        
        if not signals:
            click.echo("No signals collected yet.")
            return
        
        # Calculate statistics
        total = len(signals)
        by_type = {}
        by_source = {}
        
        for signal in signals:
            signal_type = signal['signal_type']
            source = signal['source']
            
            by_type[signal_type] = by_type.get(signal_type, 0) + 1
            by_source[source] = by_source.get(source, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Signal Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Signals: {total}\n")
        
        click.echo(f"Signals by Type:")
        for signal_type, count in sorted(by_type.items()):
            percentage = (count / total) * 100
            click.echo(f"  {signal_type.capitalize()}: {count} ({percentage:.1f}%)")
        
        click.echo(f"\nSignals by Source:")
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
@click.option('--output', '-o', type=click.Path(), required=True,
              help='Output file path (JSON format)')
@click.option('--type', '-t', help='Filter by signal type')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def export(env_file, output, type, no_interactive):
    """Export signals to JSON file."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open database
        db = Database(config.database_path, interactive=not no_interactive)
        
        # Get signals
        if type:
            signals = db.get_signals_by_type(type)
        else:
            signals = db.get_all_signals()
        
        if not signals:
            click.echo("No signals to export.")
            return
        
        # Export to file
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(signals, f, indent=2, ensure_ascii=False)
        
        click.echo(f"Exported {len(signals)} signals to {output}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.confirmation_option(prompt='Are you sure you want to clear all signals?')
def clear(env_file, no_interactive):
    """Clear all signals from the database."""
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
