#!/usr/bin/env python3
"""Example of using the configuration manager in PrismQ modules.

This example demonstrates how to:
1. Set up working directory configuration
2. Store and retrieve configuration values
3. Use configuration in your application

Run this example to see the configuration manager in action.
"""

from config_manager import ConfigManager, setup_working_directory
from pathlib import Path


def main():
    """Demonstrate configuration manager usage."""
    print("=" * 60)
    print("PrismQ Configuration Manager Example")
    print("=" * 60)
    print()
    
    # Step 1: Set up working directory configuration
    print("Step 1: Setting up working directory configuration...")
    config = setup_working_directory("PrismQ.Example.App")
    print(f"✓ Working directory configured: {config.working_dir}")
    print()
    
    # Step 2: Store some configuration values
    print("Step 2: Storing configuration values...")
    config.update({
        'DATABASE_PATH': str(config.working_dir / 'db.s3db'),
        'LOG_LEVEL': 'INFO',
        'DEBUG_MODE': 'false',
        'API_ENDPOINT': 'https://api.prismq.com/v1'
    })
    print("✓ Configuration values stored")
    print()
    
    # Step 3: Retrieve configuration values
    print("Step 3: Retrieving configuration values...")
    print(f"  - APP_NAME: {config.get('APP_NAME')}")
    print(f"  - WORKING_DIR: {config.get('WORKING_DIR')}")
    print(f"  - DATABASE_PATH: {config.get('DATABASE_PATH')}")
    print(f"  - LOG_LEVEL: {config.get('LOG_LEVEL')}")
    print(f"  - DEBUG_MODE: {config.get('DEBUG_MODE')}")
    print(f"  - API_ENDPOINT: {config.get('API_ENDPOINT')}")
    print()
    
    # Step 4: Check if configuration exists
    print("Step 4: Checking configuration existence...")
    print(f"  - Has DATABASE_PATH? {config.has('DATABASE_PATH')}")
    print(f"  - Has NONEXISTENT_KEY? {config.has('NONEXISTENT_KEY')}")
    print()
    
    # Step 5: Get with default value
    print("Step 5: Getting values with defaults...")
    cache_dir = config.get('CACHE_DIR', str(config.working_dir / 'cache'))
    print(f"  - CACHE_DIR (with default): {cache_dir}")
    print()
    
    # Step 6: Show .env file location
    print("Step 6: Configuration file location...")
    print(f"  - .env file: {config.env_file}")
    print(f"  - File exists: {config.env_file.exists()}")
    print()
    
    # Step 7: Display .env file contents
    print("Step 7: Current .env file contents:")
    print("-" * 60)
    if config.env_file.exists():
        with open(config.env_file, 'r') as f:
            print(f.read())
    print("-" * 60)
    print()
    
    # Step 8: Demonstrate persistence
    print("Step 8: Demonstrating persistence...")
    print("Creating a new ConfigManager instance...")
    config2 = ConfigManager(config.working_dir)
    print(f"  - APP_NAME from new instance: {config2.get('APP_NAME')}")
    print(f"  - DATABASE_PATH from new instance: {config2.get('DATABASE_PATH')}")
    print("✓ Configuration persisted across instances")
    print()
    
    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
