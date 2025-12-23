#!/usr/bin/env python3
"""
Example script demonstrating best practices for Python startup.

This example shows:
1. No work at import time
2. Explicit composition root (main function)
3. Dependency injection via constructor
4. Clear separation of concerns
5. Testable design
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Add repo to path (only path manipulation, no side effects)
REPO_ROOT = Path(__file__).parent
sys.path.insert(0, str(REPO_ROOT))


# =============================================================================
# Business Logic - Pure, no side effects, dependencies injected
# =============================================================================

class ContentProcessor:
    """Business logic for processing content.
    
    Dependencies are injected via constructor - no global state.
    """
    
    def __init__(self, database_path: str, ai_model: str, ai_api_base: str):
        """Initialize with explicit dependencies.
        
        Args:
            database_path: Path to database
            ai_model: AI model name
            ai_api_base: AI API base URL
        """
        self.database_path = database_path
        self.ai_model = ai_model
        self.ai_api_base = ai_api_base
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process_content(self, content_id: str) -> bool:
        """Process content with injected dependencies.
        
        Args:
            content_id: Content to process
        
        Returns:
            True if successful
        """
        self.logger.info(f"Processing content {content_id}")
        self.logger.info(f"Using database: {self.database_path}")
        self.logger.info(f"Using AI model: {self.ai_model} at {self.ai_api_base}")
        
        # Your business logic here...
        
        return True


# =============================================================================
# Composition Root - Wire everything together
# =============================================================================

def create_app(
    database_path: Optional[str] = None,
    ai_model: Optional[str] = None,
    check_ai: bool = True
) -> ContentProcessor:
    """Composition root - create and wire all dependencies.
    
    This is where all objects are instantiated and connected.
    Nothing happens at import time - only when this function is called.
    
    Args:
        database_path: Override database path
        ai_model: Override AI model
        check_ai: Whether to check Ollama availability
    
    Returns:
        Configured ContentProcessor ready to use
    
    Raises:
        RuntimeError: If AI check fails and check_ai is True
    """
    from src.startup import create_startup_config
    
    # Create startup config (explicit, in composition root)
    config = create_startup_config(
        database_path=database_path,
        ai_model=ai_model,
        interactive=False
    )
    
    # Check AI if requested (fail fast on misconfiguration)
    if check_ai:
        if not config.check_ollama_available():
            raise RuntimeError(
                f"Ollama not available at {config.get_ai_settings().api_base}. "
                f"Please start Ollama with model {config.get_ai_settings().model}"
            )
    
    # Create business logic with injected dependencies
    processor = ContentProcessor(
        database_path=config.get_database_path(),
        ai_model=config.get_ai_settings().model,
        ai_api_base=config.get_ai_settings().api_base
    )
    
    return processor


# =============================================================================
# Main Entry Point - Launch only, no wiring
# =============================================================================

def main() -> int:
    """Main entry point - setup logging and launch.
    
    Returns:
        Exit code (0 = success, non-zero = error)
    """
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        # Composition root - create app with all dependencies
        logger.info("Creating application...")
        app = create_app(check_ai=False)  # Don't check AI in this example
        
        # Use the app
        logger.info("Running application...")
        success = app.process_content("example-001")
        
        if success:
            logger.info("✅ Application completed successfully")
            return 0
        else:
            logger.error("❌ Application failed")
            return 1
    
    except Exception as e:
        logger.error(f"❌ Application error: {e}", exc_info=True)
        return 1


# =============================================================================
# Script Entry Point - Only for launching
# =============================================================================

if __name__ == "__main__":
    # Only launch main, don't do any wiring here
    # This makes the module importable for testing
    exit_code = main()
    sys.exit(exit_code)


# =============================================================================
# Testing Example - How to test with this pattern
# =============================================================================

def test_content_processor():
    """Example test - easy to test with explicit dependencies."""
    # Create processor with test dependencies (no real DB, no real AI)
    processor = ContentProcessor(
        database_path="/tmp/test.db",
        ai_model="test-model",
        ai_api_base="http://test:1234"
    )
    
    # Test business logic
    result = processor.process_content("test-001")
    assert result is True
    print("✓ Test passed")


if __name__ == "__test__":
    # Run tests
    test_content_processor()
