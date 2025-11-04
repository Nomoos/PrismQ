"""Command-line interface for PrismQ.IdeaInspiration.Sources.Commerce.AmazonBestsellers."""

import click
import sys
from pathlib import Path
from .core.config import Config
from .plugins.amazon_bestsellers import AmazonBestsellersPlugin

# Import central IdeaInspiration database from Model module
model_path = Path(__file__).resolve().parents[5] / 'Model'
if str(model_path) not in sys.path:
    sys.path.insert(0, str(model_path))

from idea_inspiration_db import IdeaInspirationDatabase, get_central_database_path


@click.group()
@click.version_option(version='1.0.0')
def main():
    """PrismQ Amazon Bestsellers Source - Gather product trends from Amazon."""
    pass


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def scrape(env_file, no_interactive):
    """Scrape bestselling products from Amazon.
    
    This command scrapes product data from Amazon bestseller lists across
    configured categories. Note that this uses mock data for demonstration.
    
    For production use, you should:
    1. Use Amazon Product Advertising API (requires approval)
    2. Or use an authorized scraping service
    3. Respect Amazon's robots.txt and Terms of Service
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Initialize central database only (single DB approach)
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Initialize Amazon plugin
        try:
            amazon_plugin = AmazonBestsellersPlugin(config)
        except ValueError as e:
            click.echo(f"Error: {e}", err=True)
            sys.exit(1)
        
        # Scrape from Amazon
        total_scraped = 0
        total_saved_central = 0
        
        click.echo("Scraping Amazon bestsellers...")
        click.echo(f"Categories: {', '.join(config.amazon_categories)}")
        click.echo(f"Max products per category: {config.amazon_max_products}")
        click.echo("")
        
        try:
            # Scrape products - returns List[IdeaInspiration]
            ideas = amazon_plugin.scrape()
            total_scraped = len(ideas)
            click.echo(f"Found {len(ideas)} products")
            
            # Save each IdeaInspiration to central database (single DB)
            for idea in ideas:
                central_saved = central_db.insert(idea)
                if central_saved:
                    total_saved_central += 1
                    click.echo(f"  ✓ Saved: {idea.title[:60]}")
                else:
                    click.echo(f"  ↻ Updated: {idea.title[:60]}")
            
        except Exception as e:
            click.echo(f"Error scraping Amazon: {e}", err=True)
            import traceback
            traceback.print_exc()
        
        click.echo(f"\nScraping complete!")
        click.echo(f"Total products found: {total_scraped}")
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
              help='Maximum number of products to display')
@click.option('--category', '-c', help='Filter by category')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
def list(env_file, limit, category, no_interactive):
    """List collected products."""
    try:
        # Load configuration  
        config = Config(env_file, interactive=not no_interactive)
        
        # Open central database
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Get products - filter by source_platform
        ideas = central_db.get_all(
            limit=limit,
            source_platform="amazon_bestsellers",
            category=category
        )
        
        if not ideas:
            click.echo("No products found.")
            return
        
        # Display products
        click.echo(f"\n{'='*80}")
        click.echo(f"Collected Products ({len(ideas)} total)")
        click.echo(f"{'='*80}\n")
        
        for i, idea in enumerate(ideas, 1):
            click.echo(f"{i}. [{idea.metadata.get('category', 'N/A')}] {idea.title}")
            click.echo(f"   ASIN: {idea.source_id}")
            if idea.metadata.get('brand'):
                click.echo(f"   Brand: {idea.metadata.get('brand')}")
            if idea.metadata.get('price'):
                click.echo(f"   Price: ${idea.metadata.get('price')} {idea.metadata.get('currency', 'USD')}")
            if idea.keywords:
                click.echo(f"   Tags: {', '.join(idea.keywords)}")
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
    """Show statistics about collected products."""
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open central database
        central_db_path = get_central_database_path()
        central_db = IdeaInspirationDatabase(central_db_path, interactive=not no_interactive)
        
        # Get all Amazon bestseller ideas
        ideas = central_db.get_all(source_platform="amazon_bestsellers")
        
        if not ideas:
            click.echo("No products collected yet.")
            return
        
        # Calculate statistics
        total = len(ideas)
        by_category = {}
        
        for idea in ideas:
            category = idea.metadata.get('category', 'Unknown')
            by_category[category] = by_category.get(category, 0) + 1
        
        # Display statistics
        click.echo(f"\n{'='*50}")
        click.echo(f"Product Collection Statistics")
        click.echo(f"{'='*50}\n")
        click.echo(f"Total Products: {total}\n")
        
        click.echo(f"Top Categories:")
        for category, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / total) * 100
            click.echo(f"  {category}: {count} ({percentage:.1f}%)")
        click.echo()
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option('--env-file', '-e', type=click.Path(), 
              help='Path to .env file')
@click.option('--no-interactive', is_flag=True, 
              help='Disable interactive prompts for missing configuration')
@click.confirmation_option(prompt='Are you sure you want to clear all Amazon bestseller products?')
def clear(env_file, no_interactive):
    """Clear Amazon bestseller products from the central database.
    
    Note: This only removes products from this source, not the entire database.
    """
    try:
        # Load configuration
        config = Config(env_file, interactive=not no_interactive)
        
        # Open central database
        central_db_path = get_central_database_path()
        
        # Note: IdeaInspirationDatabase doesn't have a delete by platform method yet
        # For now, just inform the user to use the central database tools
        click.echo("To clear Amazon bestseller products, use the central IdeaInspiration database tools.")
        click.echo(f"Central database: {central_db_path}")
        click.echo("This ensures data consistency across all sources.")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
