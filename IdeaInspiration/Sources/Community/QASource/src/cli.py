"""Command-line interface for QASource."""

import click
import sys
from .core.config import Config
from .core.database import Database
from .core.sentiment_analyzer import SentimentAnalyzer
from .core.community_processor import CommunityProcessor
from .plugins.stackexchange_plugin import StackExchangePlugin


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
        db = Database(config.database_url, interactive=not no_interactive)
        sentiment_analyzer = SentimentAnalyzer()
        processor = CommunityProcessor(sentiment_analyzer)
        
        plugin = StackExchangePlugin(config)
        
        # Parse parameters
        site_list = [s.strip() for s in sites.split(',')] if sites else None
        tag_list = [t.strip() for t in tags.split(',')] if tags else None
        
        click.echo(f"Scraping from StackExchange sites...")
        click.echo(f"Sites: {site_list or config.stackexchange_sites}")
        click.echo(f"Tags: {tag_list or config.filter_tags}")
        click.echo("")
        
        raw_questions = plugin.scrape(
            sites=site_list,
            tags=tag_list,
            max_questions=max_questions
        )
        
        total_scraped = len(raw_questions)
        total_saved = 0
        
        click.echo(f"\nFound {total_scraped} questions")
        
        for question_data in raw_questions:
            signal = processor.process_question(
                text=question_data['text'],
                title=question_data['title'],
                author=question_data['author'],
                source=question_data['source'],
                source_id=question_data['source_id'],
                platform=question_data['platform'],
                upvotes=question_data['upvotes'],
                answers=question_data['answers'],
                views=question_data['views'],
                timestamp=question_data['timestamp'],
                tags=question_data['tags'],
                category=question_data.get('category')
            )
            
            if db.insert_signal(signal):
                total_saved += 1
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total questions found: {total_scraped}")
        click.echo(f"Total questions saved: {total_saved}")
        click.echo(f"Database: {config.database_url}")
        
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
